# 03. API Keys and Secret Management

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Load provider credentials from environment variables or a suitable
    secret store.
-   Keep local secret files out of version control and provide safe
    placeholder examples.
-   Validate missing configuration without printing credential values.
-   Keep provider credentials on the backend rather than exposing them
    to browser clients.
-   Apply credential rotation, least privilege, and separate
    development/production settings.
-   Distinguish provider authentication from authentication for users of
    your application.

<br/>

## 2. What Is a Secret?

A **secret** is sensitive information that grants access to a system or
resource. In a GenAI application, examples include:

-   A provider API key used by the backend to call a hosted model.
-   A database password.
-   A signing key used to verify application sessions or tokens.
-   A service credential used to access another backend.

Secrets must be protected from unauthorized access, accidental
disclosure, and unnecessary copying. An API key is not ordinary
configuration: a value such as a model name can often be shared, while a
credential can grant billable access to a provider account.

<br/>

### Configuration versus secrets

 | Item                        | Example                                 | Typical Handling                                                                              |
| --------------------------- | --------------------------------------- | --------------------------------------------------------------------------------------------- |
| Non-secret configuration    | Model ID, request timeout, output limit | Environment variables or configuration files                                                  |
| Secret configuration        | Provider API key, database password     | Environment variables for simple deployments; secret manager for stronger centralized control |
| User credential or token    | Application session token               | Application authentication system; validate and protect according to its design               |
| Public client configuration | Public API base URL                     | May be exposed if it is genuinely non-sensitive                                               |


Do not assume a value is safe merely because it is stored in an
environment variable. The variable's value remains sensitive if it
contains a secret.

<br/>

## 3. Two Different Authentication Relationships

A model-backed application commonly has at least two separate
authentication relationships.

1.  **Application-to-provider authentication:** The backend proves to
    the model provider that it is authorized to use the provider's API.
    A provider API key or another provider-supported credential may be
    used.
2.  **User-to-application authentication:** A person or client proves
    its identity to your application, for example with a session cookie
    or access token.

These credentials serve different purposes and should not be substituted
for each other.

``` mermaid
flowchart TD
    U[User or browser client] -->|Application session or access token| A[Your backend API]
    A -->|Validate identity and authorize request| B[Application logic]
    B -->|Provider API key or provider-supported credential| P[Model provider]
    P --> M[Model response]
    M --> B
    B --> U
```

The browser's application token identifies or authorizes the caller to
use your application. The provider credential authorizes the backend to
call the model service. The backend must independently decide which
users may use which application features.

**Important:** A provider API key is not a substitute for authenticating
users. If your backend accepts unauthenticated requests, someone may be
able to consume your provider quota through your service even though the
provider key itself remains hidden.

<br/>

## 4. Load a Credential from an Environment Variable

Environment variables are a simple way to inject secrets into a local
development process or deployed service without embedding them in source
code.

The OpenAI Python SDK, used in the previous chapter, reads
`OPENAI_API_KEY` by default when constructing `OpenAI()`.

<br/>

### 4.1 Set the variable

**Windows PowerShell --- current terminal session**

``` powershell
$env:OPENAI_API_KEY = "your-key-here"
```

**macOS/Linux --- current shell session**

``` bash
export OPENAI_API_KEY="your-key-here"
```

Use a real credential only in your local environment or approved
secret-injection mechanism. The placeholder above is not a working key.

<br/>

### 4.2 Validate configuration safely

``` python
import os


def require_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(f"Required configuration is missing: {name}")

    return value


api_key = require_env("OPENAI_API_KEY")
```

This checks whether the variable is present and non-empty. It does not
print the credential. Avoid logging `api_key`, printing all environment
variables, or including secrets in exception messages.

A small helper can validate other required settings as well:

``` python
import os


def get_required_setting(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(f"Missing required setting: {name}")

    return value


MODEL_NAME = get_required_setting("OPENAI_MODEL")
API_KEY = get_required_setting("OPENAI_API_KEY")
```

Whether a model identifier should be secret is a separate question:
model IDs are usually non-secret configuration, but the application
should still validate that a configured model is allowed.

<br/>

## 5. Use a Local `.env` File Safely

A `.env` file is convenient for local development when a tool such as
`python-dotenv` loads values into the process environment. It is not, by
itself, a secure vault. Protect the file and keep it out of source
control.

### 5.1 Install the optional loader

``` bash
python -m pip install python-dotenv
```

<br/>

### 5.2 Create `.env.example`

Commit a placeholder template such as:

``` dotenv
# Copy to .env locally and replace placeholders outside source control.
OPENAI_API_KEY=replace-with-your-local-key
OPENAI_MODEL=replace-with-an-approved-model-id
MODEL_TIMEOUT_SECONDS=30
```

This file must contain **no real credentials**. The model ID and timeout
are examples of ordinary configuration; the API key line is a
placeholder.

<br/>

### 5.3 Create a local `.env`

Copy `.env.example` to `.env`, then put the real local key into `.env`
on your machine. Do not paste a live key into a shared document or
commit it.

<br/>

### 5.4 Add secret files to `.gitignore`

``` gitignore
# Local secrets and environment files
.env
.env.*
!.env.example

# Python artifacts
__pycache__/
*.py[cod]
.venv/
```

The exception `!.env.example` allows the placeholder template to be
committed while ignoring other `.env` files. Review your repository's
existing ignore rules before adopting this pattern.

<br/>

### 5.5 Load the local file

``` python
import os
from dotenv import load_dotenv

load_dotenv()  # Reads local .env values into the process environment.

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Configure the local environment.")
```

For a backend service, prefer a clear startup failure over silently
proceeding with missing credentials. Do not print the key to diagnose
configuration.

<br/>

## 6. Centralize and Validate Application Settings

Scattered calls to `os.getenv()` can make configuration inconsistent. A
settings object gives the application one place to validate required
values and apply defaults.

The following is a compact example using Pydantic Settings. Install the
optional dependency first:

``` bash
python -m pip install pydantic-settings
```

``` python
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: SecretStr
    openai_model: str
    model_timeout_seconds: float = Field(default=30.0, gt=0, le=180)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

Environment variable names are typically derived from field names, so
this configuration maps `openai_api_key` to `OPENAI_API_KEY`,
`openai_model` to `OPENAI_MODEL`, and `model_timeout_seconds` to
`MODEL_TIMEOUT_SECONDS`.

`SecretStr` helps reduce accidental disclosure in representations: its
normal display is masked. It does not encrypt the value in memory or
make it safe to send to logs, external services, or clients.

When constructing a provider client, pass the secret only to the trusted
server-side SDK initialization path. The exact accessor and client
options should follow the selected SDK's documentation.

``` python
# Illustrative server-side initialization.
# Keep this code on the backend, not in browser-delivered JavaScript.
from openai import OpenAI

client = OpenAI(
    api_key=settings.openai_api_key.get_secret_value(),
    timeout=settings.model_timeout_seconds,
)
```

Do not return `settings` or the secret field from an API endpoint. Also
avoid serializing the unmasked secret into logs or debugging output.

<br/>

## 7. Keep Provider Credentials on the Backend

Never embed a long-lived provider API key in browser JavaScript, a
mobile app bundle, a public repository, or client-side configuration
that users can inspect. Client-side code is delivered to a device
controlled by the user, so any included secret can be extracted.

A safer design is:

1.  The browser sends an application request to your backend.
2.  The backend authenticates and authorizes the user.
3.  The backend validates the request and enforces usage limits.
4.  The backend calls the provider using its server-side credential.
5.  The backend returns only the application result required by the
    client.

``` mermaid
sequenceDiagram
    participant Browser
    participant Backend
    participant Provider as Model Provider

    Browser->>Backend: Request + application session/token
    Backend->>Backend: Authenticate, authorize, validate
    Backend->>Provider: Model request + provider credential
    Provider-->>Backend: Model response
    Backend->>Backend: Validate and filter result
    Backend-->>Browser: Application response
```

Some providers offer explicitly designed client-side or ephemeral-token
flows for particular products. Use those only as documented, narrowly
scoped mechanisms; do not expose a general-purpose long-lived server API
key.

<br/>

## 8. Credential Rotation and Least Privilege

### 8.1 Credential rotation

Rotation means replacing a credential periodically or after a suspected
exposure, then disabling the old credential when it is no longer needed.

A safe rotation process generally includes:

1.  Create a replacement credential using the provider's supported
    process.
2.  Update the secret store or deployment configuration.
3.  Deploy or restart the service in a controlled way so it uses the new
    credential.
4.  Verify successful requests without logging the credential.
5.  Revoke the old credential.
6.  Review access logs and investigate if the rotation was triggered by
    a suspected leak.

Avoid placing keys in deployment commands or logs where they may be
retained. Follow provider-specific guidance about whether old and new
credentials can overlap during the transition.

<br/>

### 8.2 Least privilege

Least privilege means giving each credential only the permissions needed
for its job.

Where the provider supports it:

-   Restrict a key to the necessary project, service, or permissions.
-   Separate development credentials from production credentials.
-   Avoid sharing one unrestricted credential across unrelated
    applications.
-   Limit who can create, read, rotate, or revoke secrets.
-   Monitor usage and set appropriate budget or rate controls.

If a provider does not support a particular restriction, do not assume
it exists. Compensate with backend access controls, project separation,
monitoring, and credential-handling procedures.

<br/>

## 9. Separate Development, Testing, and Production

Use distinct configuration for each environment.

| Environment          | Credential Approach                                             | Important Safeguards                                                                   |
| -------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Local development    | Local `.env` ignored by Git, or injected environment variable   | Synthetic data; restricted development key                                             |
| Automated tests      | Fake provider client; no credential needed for unit tests       | Deterministic tests; optional live tests separated                                     |
| CI integration tests | Secret injected by CI secret facility only when required        | Restricted permissions; masked logs; avoid exposing secrets to untrusted pull requests |
| Production           | Platform secret manager or approved deployment secret injection | Least privilege, access audit, rotation, monitoring                                    |

<br/>

Do not copy production keys into a developer's `.env` file simply
because it is convenient. Prefer fake clients for ordinary tests and
reserve live provider calls for explicit integration tests.

Configuration should also be validated for each environment. For
example, production should fail startup if a required credential is
missing rather than falling back to an insecure default.

<br/>

## 10. Provider Authentication Is Not User Authentication

Consider a backend endpoint `POST /summarize`.

-   The **provider key** allows the backend to submit requests to the
    model provider under the configured account or project.
-   The **application user's session or access token** lets the backend
    identify the caller.
-   **Authorization logic** decides whether that caller may use the
    endpoint, access a document, or consume a particular quota.

The server should authenticate the caller, authorize the requested
operation, validate input, and only then make the provider request. A
valid provider key does not mean every incoming user is allowed to use
your service.

Do not ask the model to decide whether a user's credentials are valid.
Identity and permission checks must be enforced by application code and
trusted identity systems.

<br/>

## 11. Common Secret-Handling Mistakes

| Mistake                                        | Why It Is Risky                                                            | Better Practice                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------- |
| Hard-coding an API key                         | The secret can enter source history and artifacts                          | Inject it through a secret mechanism                    |
| Committing `.env`                              | Repository readers may gain access to the credential                       | Ignore local secret files and commit only placeholders  |
| Printing environment variables                 | Logs or screenshots can expose multiple secrets                            | Check presence and log safe configuration names only    |
| Sending provider keys to browser code          | Users can inspect and extract them                                         | Keep general-purpose keys server-side                   |
| Reusing production keys in tests               | Test output and environments have broader exposure risk                    | Use fake clients or restricted test credentials         |
| Sharing one key across unrelated services      | A leak affects more systems and attribution is harder                      | Separate credentials by environment and purpose         |
| Never rotating a leaked key                    | Unauthorized use can continue                                              | Revoke and replace it promptly                          |
| Treating a provider key as user authentication | Anyone reaching the backend may consume the service if access is unchecked | Authenticate and authorize application users separately |

<br/>

If a key is exposed, deleting it from the latest source file is not
sufficient. Revoke or rotate it through the provider's supported
controls, inspect relevant usage, and remove it from accessible history
and artifacts where practical.

<br/>

## 12. Practice: Safe Configuration Loading

Create a small project with these files:

``` text
secret-config-demo/
├── app.py
├── config.py
├── .env.example
├── .gitignore
└── requirements.txt
```

<br/>

### `requirements.txt`

``` text
pydantic-settings
python-dotenv
openai
```

For a reproducible project, pin tested package versions or use a lock
file rather than relying indefinitely on unpinned dependencies.

<br/>

### `.env.example`

``` dotenv
OPENAI_API_KEY=replace-with-a-local-key
OPENAI_MODEL=replace-with-an-approved-model-id
MODEL_TIMEOUT_SECONDS=30
```

Use placeholders only in this file.

<br/>

### `.gitignore`

``` gitignore
.env
.env.*
!.env.example
.venv/
__pycache__/
*.py[cod]
```

<br/>

### `config.py`

``` python
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: SecretStr
    openai_model: str
    model_timeout_seconds: float = Field(default=30.0, gt=0, le=180)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_settings() -> Settings:
    return Settings()
```

<br/>

### `app.py`

``` python
from config import load_settings


def main() -> None:
    settings = load_settings()

    # Report safe metadata only. Never print the secret itself.
    print("Configuration loaded.")
    print("Model configured:", bool(settings.openai_model.strip()))
    print("Provider credential configured:", bool(
        settings.openai_api_key.get_secret_value().strip()
    ))
    print("Timeout seconds:", settings.model_timeout_seconds)


if __name__ == "__main__":
    main()
```

Run the exercise:

1.  Create `.env` from `.env.example`.
2.  Set a valid local credential in `.env` if you want to test real
    configuration.
3.  Run `python app.py`.
4.  Temporarily remove or blank the key and run it again. Confirm that
    startup fails with a validation error and does not print the key.
5.  Check `git status` and verify that `.env` is not staged or tracked.
    Do not use a real credential in a public repository.

The example reports only whether the key is configured; it does not make
a model request.

<br/>

## 13. Checkpoint Questions

1.  What is the difference between a provider API key and a user's
    application access token?
2.  Why should a provider API key not be placed in browser JavaScript?
3.  What belongs in `.env.example`?
4.  How can an application detect a missing secret without exposing its
    value?
5.  What is the purpose of credential rotation?
6.  What does least privilege mean for provider credentials?
7.  Why should development and production use separate credentials?
8.  Why is a `.env` file not the same as a secret manager?

<br/>

### Suggested answers

1.  A provider API key authorizes backend access to the provider. A user
    token identifies or authorizes a user to access your application.
2.  Browser-delivered code is inspectable, so a bundled key can be
    extracted and abused.
3.  Placeholder values and the names of expected settings---never live
    secrets.
4.  Check whether the environment variable exists and is non-empty, then
    raise a safe configuration error without printing its value.
5.  Rotation replaces a credential to reduce the impact of exposure and
    support credential lifecycle management.
6.  Give the credential only the permissions and scope required for its
    intended task, where the provider supports those controls.
7.  It limits cross-environment exposure and makes access, monitoring,
    and revocation easier to manage.
8.  A `.env` file is a local configuration convenience that must be
    protected manually. A secret manager typically provides centralized
    access control, auditing, and lifecycle features, depending on the
    service.

<br/>

## 14. Key Takeaways

1.  Keep provider credentials out of source code, browser bundles,
    public repositories, and logs.
2.  Load secrets from environment variables or an appropriate
    secret-management service.
3.  Validate required configuration at startup without revealing secret
    values.
4.  Commit placeholder templates, not local `.env` files containing
    credentials.
5.  Keep provider authentication separate from application-user
    authentication and authorization.
6.  Use separate credentials for development and production, and
    restrict their permissions where possible.
7.  Rotate exposed credentials promptly and review usage after suspected
    compromise.
8.  Use fake clients for routine tests so most tests do not require live
    secrets.

<br/>

## References

-   [OpenAI API
    quickstart](https://developers.openai.com/api/docs/quickstart)
-   [OpenAI Python SDK](https://github.com/openai/openai-python)
-   [Pydantic Settings
    documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
-   [Python `os.environ`
    documentation](https://docs.python.org/3/library/os.html#os.environ)
-   [python-dotenv
    documentation](https://github.com/theskumar/python-dotenv)

Provider-specific credential scopes, rotation behavior, and
secret-management options vary. Verify the selected provider's current
official documentation before deploying.
