# Chapter 11: Secrets Management

## Learning Objectives

By the end of this chapter, you should be able to:

- Load credentials through environment configuration or a dedicated secret manager.
- Keep credentials out of source control, prompts, client-side bundles, logs, and error messages.
- Apply least privilege and separate credentials across development, testing, staging, and production.
- Explain credential rotation, revocation, and response to suspected exposure.
- Use placeholders and synthetic tokens in examples and automated tests.
- Trace a credential from its source to its use and identify where it must not flow.

<br/>

## 1. Why Secrets Management Matters in GenAI

A **secret** is sensitive authentication or signing material that should only be available to authorized components. Examples include:

- API keys for hosted model providers.
- Database usernames and passwords.
- Cloud access keys and service-account credentials.
- Vector database and search-service tokens.
- OAuth client secrets, refresh tokens, and session-signing keys.
- Webhook secrets, private keys, and encryption keys.

A GenAI application often integrates several services: an application server, model provider, retrieval system, object store, observability platform, and tools that can perform actions. A single exposed credential can therefore affect more than the model itself. For example, a leaked retrieval token may expose documents, while an overprivileged cloud credential may allow an attacker to access unrelated resources.

Secrets management is a **system design responsibility**, not merely a coding convention. The goal is to ensure that a credential is:

1. Created and stored through an approved mechanism.
2. Delivered only to the component that needs it.
3. Used for a narrow, authorized purpose.
4. Excluded from untrusted or unnecessary destinations.
5. Rotated or revoked when required.
6. Auditable without logging the secret itself.

<br/>

### Important distinction

A secret is not the same as a public identifier. A project name, model name, or endpoint URL may be non-secret in one system, although metadata can still be sensitive in context. An API key, bearer token, private key, or password must be treated as secret unless its issuing system explicitly defines otherwise.

<br/>

## 2. Threat Model: How Secrets Escape

Common exposure paths include:

- Hard-coded credentials committed to a repository.
- `.env` files accidentally committed or packaged into an artifact.
- Credentials embedded in frontend JavaScript, mobile applications, or browser requests.
- Secrets copied into prompts, retrieved context, model outputs, or conversation history.
- Request headers, environment dumps, stack traces, debug logs, and telemetry containing credentials.
- Screenshots, notebooks, sample configuration files, or issue reports containing real values.
- Excessive permissions that turn a limited leak into a broad compromise.
- Long-lived credentials that remain usable after a developer, service, or environment no longer needs them.

```mermaid
flowchart TD
    A[Credential issued] --> B[Approved secret store or runtime configuration]
    B --> C[Authorized server-side component]
    C --> D[Authenticated service request]
    D --> E[Response without credential]
    C -. forbidden flow .-> F[Prompt or retrieved context]
    C -. forbidden flow .-> G[Client-side bundle]
    C -. forbidden flow .-> H[Logs or exception text]
    C -. forbidden flow .-> I[Source repository]
```

The diagram illustrates the intended flow. Credentials should reach only the component that needs them and should not travel with ordinary application data.

<br/>

## 3. Loading Credentials Safely

### 3.1 Environment variables

Environment variables are a common way to inject configuration into a server-side process at runtime. They help separate code from deployment-specific values.

```python
import os

api_key = os.environ.get("MODEL_PROVIDER_API_KEY")
if not api_key:
    raise RuntimeError("Required model-provider credential is not configured")

# Pass the value only to the trusted server-side SDK/client that needs it.
# Do not print api_key or include it in prompts, logs, or exceptions.
```

Key practices:

- Read the value at runtime rather than hard-coding it.
- Fail safely when required configuration is missing.
- Avoid printing all environment variables during debugging.
- Restrict who can set or inspect the process environment.
- Keep production secrets out of local developer environments where possible.
- Remember that environment variables are a delivery mechanism, not automatically a secure secret vault. Access by privileged processes, crash dumps, diagnostic tools, and deployment configuration still needs control.

<br/>

### 3.2 Dedicated secret stores

For production workloads, use the organization’s approved secret manager or platform-managed identity mechanism when available. Secret stores can support centralized access control, audit trails, versioning, rotation, and revocation.

A robust pattern is:

1. The workload authenticates using a platform identity or another approved bootstrap mechanism.
2. The secret manager verifies that identity and its permissions.
3. The workload retrieves only the secret it is authorized to access.
4. The secret is held in memory only as long as operationally necessary.
5. Access and rotation events are logged without recording the secret value.

The bootstrap identity must also be protected. A secret manager does not help if every workload can retrieve every secret.

<br/>

### 3.3 Avoid fallback-to-default credentials

Do not silently fall back to a placeholder, an administrator key, or a production credential when configuration is missing.

```python
import os

def require_secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required configuration: {name}")
    return value

provider_key = require_secret("MODEL_PROVIDER_API_KEY")
```

The error names the missing configuration key, not its value. In production, the error should not reveal secret-store paths or other sensitive deployment details to untrusted callers.

<br/>

## 4. Keep Secrets Out of Repositories

### 4.1 Configuration templates

Commit a template showing the required variable names, but never the actual credentials.

```dotenv
# .env.example — safe placeholders only
MODEL_PROVIDER_API_KEY=replace-with-a-local-test-value
VECTOR_STORE_TOKEN=replace-with-a-local-test-value
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
```

The template documents configuration shape. It is not a working production configuration, and the example values must not be valid credentials.

<br/>

### 4.2 Ignore local secret files

For example, a `.gitignore` file can include:

```gitignore
.env
.env.*
!.env.example
secrets/
*.pem
*.key
```

Adapt these patterns to the repository’s actual needs. Do not ignore every file with a broad pattern if that would hide legitimate, non-secret configuration or test fixtures. `.gitignore` only prevents ordinary untracked files from being added; it does not remove a secret that was already committed or guarantee that a file cannot be force-added.

<br/>

### 4.3 If a secret is committed

Deleting the line in a later commit is not sufficient. The value may remain in repository history, forks, pull-request diffs, caches, or clones.

Treat the credential as exposed:

1. Revoke or rotate it promptly.
2. Review access logs and usage for suspicious activity.
3. Remove it from current files and, where appropriate, clean repository history.
4. Coordinate history rewriting with collaborators because it changes commit references.
5. Check build artifacts, package registries, issue trackers, CI logs, and other copies.
6. Add or improve secret scanning and preventive checks.

**Revocation comes first.** History cleanup does not make a credential safe to reuse.

<br/>

## 5. Keep Secrets Out of Prompts and Model Context

A model prompt is not a secret store. Anything included in a prompt or retrieved context may be exposed through model output, tracing, debugging, provider-side processing, or downstream systems depending on the architecture and policies.

Do not place these in prompts or retrieved documents unless a specifically reviewed design requires it:

- API keys and bearer tokens.
- Passwords and database connection strings.
- Private signing keys.
- Session cookies and refresh tokens.
- Raw environment dumps or secret-manager responses.

Prefer **capability separation**: the model can request an approved operation, while trusted application code authenticates to the relevant service. The model should not need to see the credential.

For example, the model may produce a structured request such as:

```json
{
  "tool": "search_internal_documents",
  "arguments": {
    "query": "deployment rollback procedure"
  }
}
```

The server validates the request, checks the caller’s authorization, and uses its own narrowly scoped credential to query the retrieval service. It does not append the retrieval token to the prompt.

Treat prompt-injection attempts that request secrets as untrusted input. Prompt instructions alone are not a sufficient security boundary; the architecture should make secret access unavailable to the model.

<br/>

## 6. Keep Secrets Out of Client-Side Bundles

Anything shipped to a browser or distributed client should be assumed visible to the user. Build-time environment variables can be substituted directly into frontend JavaScript, so naming a variable `SECRET_KEY` does not make it secret.

Unsafe pattern:

```javascript
// Never put a privileged provider key in frontend code.
const apiKey = "REAL_PROVIDER_KEY";
```

Safer architecture:

```text
Browser or mobile client
        |
        | user-authenticated request
        v
Application backend
        |
        | server-side credential, limited scope
        v
Model provider or internal service
```

The backend should authenticate the user, enforce quotas and authorization, and call the provider using a server-side credential. The client should receive only the response and data it is permitted to see.

If a provider explicitly supports restricted public client tokens, use them only within the provider’s documented constraints. Do not assume that a key is safe for client exposure simply because it is labeled as an API key.

<br/>

## 7. Logging, Errors, and Observability

Logs should support diagnosis and auditing without becoming a second secret repository.

### 7.1 Dangerous logging patterns

Avoid:

```python
# Unsafe examples — do not use in production
print(os.environ)
logger.debug("Authorization header: %s", authorization_header)
logger.exception("Request failed; request payload=%r", request_payload)
```

Request payloads may contain credentials, personal data, or retrieved private content. Exceptions may include URLs with embedded credentials, headers, connection strings, or SDK configuration.

Prefer structured, redacted events:

```python
logger.warning(
    "model_request_failed",
    extra={
        "provider": "example-provider",
        "request_id": request_id,
        "error_category": "authentication_error",
    },
)
```

Only include fields supported by the logging framework and schema. Do not add tokens, full authorization headers, raw prompts, or unfiltered provider responses.

<br/>

### 7.2 Error-handling principles

- Return generic, actionable messages to end users.
- Preserve a safe correlation or request ID for troubleshooting.
- Store detailed diagnostic information only in an access-controlled system, after redaction.
- Do not include secrets in exception messages.
- Sanitize untrusted text to prevent log injection and misleading log entries.
- Test that redaction applies to nested objects, headers, URLs, and multiline exceptions—not only obvious fields.

Redaction is a defense-in-depth measure. Avoid collecting secrets in the first place, because a redaction rule may miss an unexpected representation.

<br/>

## 8. Least Privilege and Environment Separation

Each credential should have only the permissions necessary for its specific job.

Examples:

- A summarization service may need permission to invoke one model endpoint, but not administer the provider account.
- A retrieval service may need read-only access to a particular index, not permission to delete all indexes.
- A CI job that runs unit tests may use synthetic credentials and should not need production database access.
- A document-ingestion worker may write to an ingestion namespace without being able to read every tenant’s documents.

Use separate identities and credentials for development, testing, staging, and production. This limits accidental cross-environment access and makes revocation more precise.

| Control | Weak practice | Stronger practice |
|---|---|---|
| Scope | One administrator key for every service | Dedicated identity with minimum permissions |
| Environments | Same credential everywhere | Separate credentials and access policies |
| Lifetime | Long-lived key with no review | Short-lived or rotated credentials where supported |
| Access | Broad team-wide secret access | Role-based, need-to-know access |
| Testing | Real production keys in test fixtures | Synthetic tokens or isolated test credentials |
| Audit | Shared key with unclear ownership | Identifiable workload identity and access records |

Least privilege does not mean merely choosing a read-only key. Scope it to the correct resource, tenant, environment, operation, and time window where the platform supports those controls.

<br/>

## 9. Rotation, Revocation, and Suspected Exposure

**Rotation** replaces a credential with a new one. **Revocation** makes an existing credential unusable. They are related but not identical: a new key may be issued while the old key remains valid until it is explicitly disabled.

A controlled rotation workflow is:

1. Identify all workloads that use the credential.
2. Issue a replacement credential with the intended scope.
3. Update the secret store or runtime configuration.
4. Deploy or reload consumers safely.
5. Verify successful authentication and expected behavior.
6. Revoke the old credential.
7. Monitor for failures or unexpected use of the old credential.
8. Record completion and update ownership or runbooks.

For suspected exposure, prioritize containment:

1. Revoke or disable the exposed credential as quickly as practical.
2. Issue a replacement through the approved process.
3. Identify the possible exposure window and affected resources.
4. Inspect audit logs, provider usage, data access, and unusual actions.
5. Rotate related credentials if the incident suggests they may also be compromised.
6. Remove exposed copies from repositories, logs, artifacts, tickets, and shared documents where feasible.
7. Document the incident and close the control gap that enabled it.

Do not paste a suspected secret into a chat or ticket to ask whether it is valid. Refer to the secret by a non-sensitive identifier, such as a vault entry name or key ID.

<br/>

## 10. Synthetic Credentials for Tests and Examples

Use unmistakably fake values in tutorials, unit tests, notebooks, screenshots, and bug reports.

```python
TEST_TOKEN = "test-token-not-valid-000000"
```

A test token should be nonfunctional outside the isolated test environment. Avoid examples that resemble real provider credentials closely enough to be mistaken for usable values, and never copy a real token into a test before masking it.

Useful testing strategies:

- Inject a synthetic token through test configuration.
- Mock the SDK or HTTP client when testing credential use.
- Assert that the expected authorization mechanism is used without printing the value.
- Capture logs and verify that the token does not appear.
- Test missing, malformed, expired, and revoked credentials.
- Ensure integration tests use isolated test accounts and cannot reach production resources accidentally.

Example log-leak regression test:

```python
import logging

def test_token_is_not_logged(caplog):
    fake_token = "test-token-not-valid-000000"

    # Replace this call with the application's function that handles
    # an authenticated request. The test should use a mocked client.
    with caplog.at_level(logging.DEBUG):
        handle_request_for_test(token=fake_token)

    assert fake_token not in caplog.text
```

This is a pattern, not a complete test suite: `handle_request_for_test` must be implemented in the application or replaced with the actual function under test. Also test exceptions and structured log fields, not just ordinary messages.

<br/>

## 11. Credential Flow Review

For each credential, document its lifecycle.

| Stage | Questions to answer |
|---|---|
| Creation | Who or what issues it? Is its scope limited? |
| Storage | Where is the authoritative copy held? Who can read it? |
| Delivery | How does the workload obtain it? Is the channel controlled? |
| Use | Which component receives it, and for what exact operation? |
| Boundaries | Can it reach prompts, retrieved content, clients, logs, traces, or error messages? |
| Renewal | How is it rotated? Can old and new values overlap safely? |
| Revocation | Who can disable it, and how quickly? |
| Verification | What tests and audit records demonstrate the controls? |

A useful review should follow data flow, not merely search for strings named `API_KEY`. Credentials can be copied into nested configuration, headers, exception objects, command-line arguments, or telemetry fields.

<br/>

## 12. Practical Configuration Review

Use this checklist during code review and deployment review.

- [ ] No real credentials are hard-coded in source files, notebooks, tests, or examples.
- [ ] Secret files and generated artifacts are excluded from version control and packaging.
- [ ] Required credentials are loaded at runtime through an approved mechanism.
- [ ] Missing configuration fails safely without printing secret values.
- [ ] Production secrets are not exposed to frontend bundles or mobile clients.
- [ ] Prompts and retrieved context contain no credentials.
- [ ] Logs, traces, metrics, exception messages, and support diagnostics are redacted.
- [ ] Service identities are scoped to the correct resources and operations.
- [ ] Development, test, staging, and production credentials are separated.
- [ ] Rotation and revocation steps have been documented and tested.
- [ ] Secret scanning runs in appropriate repository and CI workflows.
- [ ] Tests use synthetic or isolated test credentials.
- [ ] Credential access is auditable without recording the credential itself.
- [ ] Suspected exposure has a clear owner and incident-response path.

<br/>

## 13. Practice: Review Configuration and Error Messages

### Scenario

An application calls a hosted LLM and an internal vector database. A developer adds the following debugging code:

```python
logger.debug("Environment: %r", os.environ)
logger.debug("Provider client: %r", provider_client)
logger.error("Request failed: %s", exception)
```

The project also includes a local `.env` file and a frontend build configuration.

### Tasks

1. Identify every possible route by which a credential could be exposed.
2. Replace broad environment logging with a small allowlist of non-sensitive diagnostic fields.
3. Inspect whether the provider client’s representation includes headers or configuration.
4. Ensure error responses do not expose connection strings, authorization headers, or secret-store details.
5. Verify that the frontend bundle contains no privileged credentials.
6. Add a synthetic-token test that fails if the token appears in captured logs.
7. Write a rotation and revocation runbook for an accidentally exposed provider key.

<br/>

### Expected review observations

- Logging all environment variables is unsafe because credentials may be present.
- Object representations and exception strings are not guaranteed to be secret-free.
- A local `.env` file needs exclusion from source control and protection on the developer machine.
- Frontend build-time substitution can expose values even when they originate from environment variables.
- Removing a secret from the latest code does not invalidate a previously exposed credential.

<br/>

## 14. Practice: Credential-Flow Trace

Choose one credential used by your application, such as a model-provider key or vector-store token. Complete the following record.

| Field | Your finding |
|---|---|
| Credential purpose | |
| Issuer and owner | |
| Authoritative storage location | |
| Runtime loading mechanism | |
| Component that uses it | |
| Permissions and resource scope | |
| Components explicitly denied access | |
| Possible logging or prompt paths | |
| Rotation procedure | |
| Revocation procedure | |
| Regression test | |

Draw the flow from secret storage to the authorized consumer. Mark every boundary where the value must not pass: browser, prompt, retrieved documents, user-visible output, logs, tracing, and source control.

<br/>

## 15. Checkpoint

**Checkpoint:** Trace where a credential is loaded, used, and prevented from reaching untrusted components.

Your submission should demonstrate:

1. **Source:** The credential comes from an approved runtime configuration or secret store.
2. **Consumer:** Only the intended server-side component receives it.
3. **Scope:** Its permissions are limited to the required service, resource, and operation.
4. **Non-propagation:** It is not sent to the model, browser, retrieved context, logs, traces, or errors.
5. **Lifecycle:** Rotation and revocation steps are documented.
6. **Evidence:** Automated tests or inspection verify that accidental disclosure is detected.

A strong answer traces the credential through the real application path and cites concrete tests or configuration controls. Merely stating that “the key is stored in an environment variable” is not sufficient.

<br/>

## 16. Review Questions

1. Why is an environment variable not automatically equivalent to a dedicated secret manager?
2. Why does removing a committed secret not resolve the exposure?
3. Why should privileged model-provider credentials remain server-side?
4. What is the difference between credential rotation and revocation?
5. How does least privilege reduce the impact of a leaked key?
6. Why should raw prompts and provider client objects be excluded from ordinary logs?
7. What makes a test credential genuinely synthetic?
8. How would you prove that a secret cannot appear in a prompt or user-visible error?
9. Why are separate development and production credentials important?
10. What should happen first when a production credential is suspected to be exposed?

<br/>

### Suggested answers

1. Environment variables are a delivery mechanism; process access, deployment configuration, and diagnostic output still need protection.
2. Copies may persist in history, forks, logs, artifacts, and clones, and the credential may still be valid. Revoke or rotate it.
3. Client-side assets are visible to users, and prompts are data sent to a model system; neither is an appropriate place for privileged credentials.
4. Rotation replaces a credential; revocation disables an existing one.
5. A stolen credential can only perform the limited actions allowed by its permissions.
6. They may contain credentials, personal data, private content, or sensitive configuration.
7. It is deliberately nonfunctional outside an isolated test environment and does not grant real access.
8. Trace the data flow, use mocked clients, and assert that synthetic values do not appear in prompts, logs, traces, exceptions, or outputs.
9. Separation limits cross-environment impact and enables independent access policies and revocation.
10. Contain the exposure by revoking or disabling the credential, then replace it and investigate possible misuse.

<br/>

## Key Takeaways

- Keep secrets outside source code and model context.
- Use an approved secret store or carefully controlled runtime configuration.
- Never ship privileged credentials to browsers or other untrusted clients.
- Scope credentials narrowly and separate them by environment and workload.
- Treat logs, traces, errors, notebooks, and artifacts as potential disclosure channels.
- Rotate and revoke exposed credentials; repository cleanup alone is insufficient.
- Use synthetic values and automated regression tests to prove non-disclosure.
- Review the full credential lifecycle, not only where the value is initially stored.

<br/>

## Further Reading

- OWASP Cheat Sheet Series: Secrets Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- OWASP Cheat Sheet Series: Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Top 10 for LLM Applications — https://genai.owasp.org/
- NIST Cybersecurity Framework — https://www.nist.gov/cyberframework
- Your cloud provider's official documentation for secret management, workload identity, key rotation, and audit logging.
