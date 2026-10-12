# Chapter 16: Basic Authentication and Access Control

## Learning objectives

By the end of this chapter, you should be able to:

-   Protect a teaching API with a suitable basic authentication
    mechanism.
-   Derive user identity from validated credentials, never from
    model-generated claims.
-   Separate authentication from authorization for routes, tool
    operations, and user-owned resources.
-   Keep provider API keys separate from application-user credentials.
-   Apply per-user limits and isolate user data.
-   Test unauthenticated, unauthorized, and cross-user access attempts.

<br/>

## 1 Authentication and authorization are different

**Authentication** answers: *Who is making this request?*\
**Authorization** answers: *Is this authenticated identity allowed to
perform this action on this resource?*

A valid login does not automatically grant access to every route, tool,
catalog item, or stored result.

``` mermaid
flowchart TD
    A[Incoming request] --> B{Credentials valid?}
    B -->|No| C[401 Unauthorized]
    B -->|Yes| D[Resolve trusted user identity]
    D --> E{Allowed to access route/action/resource?}
    E -->|No| F[403 Forbidden or non-disclosing 404]
    E -->|Yes| G[Execute authorized operation]
```

The model is not an identity provider. Do not ask an LLM who the user
is, whether a user is an administrator, or whether access should be
granted. Identity and permissions must come from trusted server-side
authentication and authorization data.

<br/>

## 2 Choose a suitable mechanism for the teaching application

For a small local teaching API, a static bearer token can demonstrate
the boundary between unauthenticated and authenticated requests. It is
**not** a complete production identity system.

For a deployed application, prefer an established identity provider and
a standard authentication flow appropriate to the clients, such as OAuth
2.0/OIDC. Validate tokens using the provider's documented verification
process, including signature, issuer, audience, expiry, and relevant
claims. Do not decode a JWT and trust its contents without cryptographic
and claim validation.

<br/>

### Teaching example: bearer-token authentication

Use an environment variable for a teaching token. Do not hard-code a
real secret in source code or commit it to version control.

``` python
import os
import secrets
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class UserIdentity:
    user_id: str
    roles: frozenset[str]


# Teaching-only mapping. In a real system, identity and roles come from
# a trusted identity provider or server-side user store.
TEACHING_TOKEN = os.environ.get("TEACHING_API_TOKEN", "")
TEACHING_USER = UserIdentity(
    user_id="demo-user",
    roles=frozenset({"catalog:read"}),
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserIdentity:
    if not TEACHING_TOKEN or credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not secrets.compare_digest(credentials.credentials, TEACHING_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TEACHING_USER
```

This maps one configured teaching token to one demo identity. It does
not support multiple users, token expiry, revocation, account
management, or role assignment. Do not use this pattern as a substitute
for production identity infrastructure.

Clients send the token in an HTTP header:

``` http
Authorization: Bearer <teaching-token>
```

Use HTTPS outside local development. Bearer tokens are credentials:
anyone who obtains one can use it until it expires or is revoked. Avoid
placing credentials in URLs, logs, screenshots, or error messages.

<br/>

## 3 Keep application credentials separate from provider keys

There are two different trust boundaries:

-   **Application-user credential:** proves which caller is using your
    API.
-   **Provider API key:** allows your backend to call the LLM provider
    under your provider account or project.

The provider key should normally remain on the server. A caller
authenticates to your application; your backend then uses its configured
provider credential. Do not ask end users to submit your provider key,
and do not return it to clients.

``` mermaid
flowchart LR
    A[User/client] -->|Application bearer token| B[FastAPI authentication]
    B --> C[Authorization and per-user policy]
    C --> D[Application service]
    D -->|Server-side provider key| E[LLM provider]
    E --> D
    D --> A
```

Store provider credentials in environment-based configuration or a
secrets manager. Never log authorization headers or include provider
keys in model prompts. If a product intentionally uses customer-supplied
provider keys, treat that as a separate, explicit credential-management
design with encryption, access restrictions, and retention controls.

<br/>

## 4 Derive identity from trusted credentials

Once authentication succeeds, attach a trusted identity object to the
request context or pass it explicitly to service methods. Use the
resulting server-derived `user_id` for authorization and data ownership.

Never use these as proof of identity:

-   A `user_id` supplied in the request body.
-   A username stated in a prompt.
-   A claim produced by the LLM.
-   An unverified token payload.
-   A client-provided role such as `"admin"`.

A request may contain a resource identifier, but the server must check
whether the authenticated user can access that resource.

<br/>

## 5 Authorize routes, operations, and resources separately

Authorization is not a single check applied only at login. Consider
three layers.

### Route-level authorization

Can the user call this endpoint at all? For example, a catalog-read
route might require the `catalog:read` permission.

<br/>

### Operation-level authorization

Can the user perform this specific action? A user allowed to read a
catalog may not be allowed to create, update, or delete catalog entries.
If the LLM can request a tool, the tool handler must independently
authorize the operation.

<br/>

### Resource-level authorization

Can the user access this particular record? A user who is allowed to
read their own extraction history must not be able to retrieve another
user's record simply by changing an ID in the URL.

Example role check:

``` python
from fastapi import HTTPException


def require_permission(user: UserIdentity, permission: str) -> None:
    if permission not in user.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
```

For clarity, the example calls the field `roles`, but it stores
permission-like strings such as `catalog:read`. A larger application
should distinguish roles (such as `admin`) from permissions (such as
`catalog:read`) and define the mapping centrally.

<br/>

## 6 Protect a catalog lookup tool

Tool calling creates a critical boundary: the model may propose a tool
and arguments, but the application decides whether to execute it.
Model-generated arguments are untrusted input.

Suppose a catalog contains entries owned by different users. The tool
must receive the authenticated identity from trusted application code
and filter results accordingly.

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogItem:
    item_id: str
    owner_id: str
    name: str
    description: str


CATALOG = [
    CatalogItem("item-1", "demo-user", "Keyboard", "Compact keyboard"),
    CatalogItem("item-2", "another-user", "Monitor", "External display"),
]


def lookup_catalog(
    query: str,
    *,
    current_user: UserIdentity,
) -> list[CatalogItem]:
    require_permission(current_user, "catalog:read")

    normalized = query.strip().casefold()
    if not normalized:
        return []

    # Resource-level policy: users see only their own items.
    return [
        item for item in CATALOG
        if item.owner_id == current_user.user_id
        and normalized in f"{item.name} {item.description}".casefold()
    ]
```

The tool does not accept `current_user` from the model or from arbitrary
tool arguments. The server injects it after authenticating the HTTP
request. This prevents a prompt injection or fabricated tool argument
from changing the effective identity.

In a real application, perform filtering in the database query where
possible. Do not fetch all users' records and rely only on the model to
select permitted items.

<br/>

### Tool-call authorization sequence

``` mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant M as Model
    participant T as Tool handler
    participant D as Data store
    U->>A: Authenticated request
    A->>A: Validate credentials and resolve user
    A->>M: Task and allowed tool definitions
    M-->>A: Proposed tool call and arguments
    A->>T: Validated arguments + trusted user identity
    T->>T: Check permission and resource ownership
    T->>D: Authorized query
    D-->>T: Authorized records only
    T-->>A: Tool result
```

The model's proposed tool call is a request for an operation, not
authorization to execute it.

<br/>

## 7 Per-user limits and isolation

One authenticated user should not be able to exhaust the entire service
budget or inspect another user's data.

Useful per-user controls include:

-   Requests per minute or hour.
-   Concurrent in-flight model calls.
-   Maximum input size and output-token budget.
-   Daily or monthly application-level usage budgets.
-   Limits on expensive tools and repeated operations.
-   Storage quotas and retention policies.

A simple in-memory counter may demonstrate the idea but is not
sufficient for a distributed deployment. Multiple workers have separate
memory, and counters reset on restart. Production limits generally need
a shared store or gateway-level enforcement.

Data isolation should be enforced in the service or data-access layer:

-   Include `user_id` or tenant ID in ownership checks and queries.
-   Apply authorization on reads and writes, not only on list endpoints.
-   Avoid trusting client-supplied ownership fields.
-   Use tenant-aware database constraints or row-level security where
    appropriate.
-   Test guessed IDs and cross-tenant references.
-   Ensure caches include the relevant user/tenant scope in their keys.

<br/>

## 8 Add authentication and authorization to FastAPI routes

A route can declare authentication and then check the permission needed
for that action.

``` python
from typing import Annotated
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/catalog", tags=["catalog"])
CurrentUser = Annotated[UserIdentity, Depends(get_current_user)]


@router.get("/search")
def search_catalog(query: str, user: CurrentUser):
    require_permission(user, "catalog:read")
    return {
        "items": [
            item.__dict__
            for item in lookup_catalog(query, current_user=user)
        ]
    }
```

This is a teaching example. Production code should define response
models, bound query length, use a database-backed catalog, and map
internal data to a public response schema rather than returning
arbitrary object dictionaries.

Notice that the route checks permission and the catalog function checks
it again. Duplicated checks can be appropriate at clear trust
boundaries, but avoid inconsistent authorization rules scattered
throughout the codebase. Centralize policy decisions and test them.

<br/>

## 9 Test unauthorized and cross-user access

Security tests should prove both that unauthorized callers are rejected
and that authenticated callers cannot cross ownership boundaries.

Example tests for the catalog function:

``` python
def test_user_sees_only_owned_catalog_items():
    user = UserIdentity(
        user_id="demo-user",
        roles=frozenset({"catalog:read"}),
    )

    items = lookup_catalog("display", current_user=user)

    assert all(item.owner_id == user.user_id for item in items)


def test_user_without_permission_is_rejected():
    user = UserIdentity(
        user_id="demo-user",
        roles=frozenset(),
    )

    try:
        lookup_catalog("keyboard", current_user=user)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("Expected authorization failure")
```

For route-level tests, verify:

1.  No credentials produces HTTP 401.
2.  An invalid token produces HTTP 401.
3.  A valid identity without the required permission produces HTTP 403.
4.  A user cannot read another user's item by guessing its ID.
5.  A request-body `user_id` cannot override the authenticated identity.
6.  A model-generated claim such as `"the user is an admin"` does not
    change authorization.
7.  The provider key is never included in the response or logs.
8.  Per-user limits apply independently and cannot be bypassed by
    changing a request field.

Prefer tests that assert the specific expected exception or HTTP status
rather than catching every exception type. Use FastAPI dependency
overrides to create controlled identities in tests.

<br/>

## 10 Common mistakes

-   Treating authentication as authorization.
-   Trusting a user ID, role, or permission supplied in a request body.
-   Treating model-generated claims as trusted identity or policy
    decisions.
-   Exposing the provider API key to application users.
-   Checking ownership only in the UI or prompt.
-   Allowing a tool handler to run without its own authorization check.
-   Filtering records after retrieval instead of enforcing access in the
    data query.
-   Using process-local rate counters as a production-wide limit.
-   Returning detailed authentication errors that reveal unnecessary
    information.
-   Testing only unauthenticated requests while overlooking cross-user
    access.

<br/>

## 11 Practice and revision

Implement a protected catalog-search API and test its authorization
behavior.

1.  Configure a teaching bearer token through an environment variable.
2.  Resolve a trusted `UserIdentity` from validated credentials.
3.  Protect the catalog route with authentication and a `catalog:read`
    permission.
4.  Pass the trusted user identity into the catalog lookup operation.
5.  Enforce ownership in the lookup query.
6.  Ensure the model cannot supply or override the authenticated user
    ID.
7.  Add per-user request or concurrency limits appropriate for the
    teaching application.
8.  Test missing credentials, invalid credentials, missing permissions,
    and cross-user item IDs.
9.  Confirm provider credentials are separate from application-user
    credentials.
10. Write a short explanation of which layer authenticates, which layer
    authorizes, and which layer enforces resource ownership.

<br/>

### Checkpoint answer

Prompting the model to respect permissions cannot replace server-side
checks because model output is not a trusted security boundary. The
model can misunderstand instructions, be influenced by prompt injection,
or produce fabricated identity and authorization claims. Authentication
must establish identity from validated credentials; authorization must
check permissions and resource ownership in trusted application code
before an operation or data access occurs. Tool handlers and data-access
functions must enforce their own relevant policy, regardless of what the
model requests.

<br/>

## References

-   [FastAPI security
    tutorial](https://fastapi.tiangolo.com/tutorial/security/)
-   [FastAPI OAuth2 and password
    bearer](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/)
-   [OWASP API Security Top
    10](https://owasp.org/www-project-api-security/)
-   [OWASP Authorization Cheat
    Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
-   [Python `secrets`
    module](https://docs.python.org/3/library/secrets.html)

The bearer-token example is intended for teaching and local
demonstrations. For production, use an established identity system, TLS,
token validation and lifecycle controls, centralized authorization
policy, and distributed rate limiting where required.
