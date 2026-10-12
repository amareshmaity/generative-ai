# 04. Model Initialization and Configuration

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Configure model clients, model identifiers, endpoints, and default
    request settings.
-   Distinguish initializing a remote API client from loading model
    weights into local memory.
-   Set supported output limits, generation controls, and timeouts
    explicitly.
-   Reuse clients appropriately and close resources when the application
    shuts down.
-   Record model and prompt versions alongside configuration.
-   Detect unsupported settings rather than assuming they are honored.
-   Build a typed configuration object and validate it at startup.

<br/>

## 2. Three Configuration Layers

A maintainable GenAI application separates configuration into three
layers.

 | Layer                         | What Belongs Here                                                                         | Examples                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Application configuration** | Values that define how the application is deployed and which approved model setup it uses | Environment name, default model ID, prompt version, timeout policy    |
| **Client configuration**      | Settings for the SDK client and its network behavior                                      | API credential, base URL, connection/read timeout, connection pooling |
| **Per-request parameters**    | Settings that can vary for an individual model call                                       | Input, instructions, output-token limit, supported sampling controls  |


These layers overlap in some systems, but separating them conceptually
helps prevent configuration from being scattered throughout route
handlers.

For example, a provider API key should not be passed around as a
per-request user parameter. Likewise, a user should not be allowed to
send an arbitrary base URL or model ID unless the application explicitly
supports and validates that choice.

<br/>

## 3. Initializing an API Client Is Not Loading a Model Locally

### Hosted API client

When you initialize a hosted API client, you create a software object
that knows how to communicate with a remote service. The model weights
remain on the provider's infrastructure.

``` python
from openai import OpenAI

client = OpenAI()
```

This initializes an SDK client. It does **not** download or load the
model's weights into your computer's RAM or GPU memory. A network
request is made when you invoke an API operation.

<br/>

### Local model loading

With local inference, your application loads model weights and
supporting components into local memory, often using a framework such as
Transformers and a runtime such as PyTorch.

``` python
# Illustrative local inference pattern, not needed for a hosted API.
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "a-model-published-for-local-use"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
```

The local example requires an actual compatible model identifier,
sufficient memory, the relevant libraries, and any required model
access. It is included to show the distinction, not as a drop-in model
choice.


| Concern                      | Hosted API Client                                   | Local Model                                       |
| ---------------------------- | --------------------------------------------------- | ------------------------------------------------- |
| Where model weights run      | Provider infrastructure                             | Your machine or serving infrastructure            |
| Client initialization        | Creates a client for remote requests                | Loads tokenizer/model and runtime resources       |
| Main resource considerations | Network, rate limits, request cost, latency         | RAM/VRAM, compute, loading time, serving capacity |
| Model updates                | Provider controls model availability and versioning | You control downloaded weights and deployment     |
| Credential needs             | Usually provider credentials                        | Depends on model source and deployment            |
| Cleanup                      | Close SDK resources when appropriate                | Release model/runtime resources as appropriate    |

<br/>

## 4. Configure a Hosted Client

A client may need credentials, a base URL, timeout settings, and other
transport options. Use the official SDK documentation for the exact
constructor parameters and defaults.

Example using the OpenAI Python SDK:

``` python
import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing.")

client = OpenAI(
    api_key=api_key,
    timeout=30.0,
    max_retries=2,
)
```

This demonstrates explicit client configuration. Verify the installed
SDK's supported arguments and retry defaults before relying on them.
Avoid configuring retries independently at several layers without
understanding how the attempts multiply; reliability policies are
discussed in Chapter 12.

A `base_url` or custom endpoint should be set only when your deployment
intentionally uses a compatible endpoint, such as a provider-supported
alternative or gateway. Validate endpoint configuration at startup. Do
not let arbitrary public request input select the backend URL, as that
can create security and routing risks.

<br/>

## 5. Typed Application Configuration

A typed configuration object centralizes settings, documents expected
types, and catches missing or invalid values early. The example below
uses Pydantic Settings.

Install the dependencies:

``` bash
python -m pip install pydantic-settings openai
```

Example `.env.example`:

``` dotenv
OPENAI_API_KEY=replace-with-a-local-key
OPENAI_MODEL=replace-with-an-approved-model-id
APP_ENV=development
MODEL_TIMEOUT_SECONDS=30
MODEL_MAX_OUTPUT_TOKENS=500
PROMPT_VERSION=summarize-v1
```

Use placeholders only in `.env.example`. Keep a real `.env` out of
version control.

<br/>

### `config.py`

``` python
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"

    openai_api_key: SecretStr
    openai_model: str = Field(min_length=1)
    model_timeout_seconds: float = Field(default=30.0, gt=0, le=180)
    model_max_output_tokens: int = Field(default=500, ge=1, le=20_000)
    prompt_version: str = Field(default="summarize-v1", min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_settings() -> Settings:
    return Settings()
```

This validates required fields and basic bounds. The example's numeric
limits are application policy, not universal provider limits. Set them
according to your use case and the selected model's documented
capabilities.

The model ID is non-secret configuration in most cases, but it should
still be controlled. In a production application, consider an allowlist
of model identifiers so clients cannot request arbitrary models or
unexpectedly expensive configurations.

<br/>

### Validate at startup

``` python
from config import load_settings

settings = load_settings()

print("Configuration validated.")
print("Environment:", settings.app_env)
print("Model configured:", bool(settings.openai_model.strip()))
# Never print settings.openai_api_key or dump the full settings object.
```

If a required variable is absent or a value violates the declared
constraints, constructing `Settings()` raises a validation error. Handle
startup errors so the service fails clearly without exposing secret
values.

<br/>

## 6. Client Options Versus Per-Request Parameters

Client options govern the SDK client or its network behavior.
Per-request parameters govern an individual generation request.

``` python
from openai import OpenAI

client = OpenAI(
    timeout=30.0,   # Client/network behavior
    max_retries=2,  # SDK retry policy, if supported by this version
)

response = client.responses.create(
    model="gpt-5.5",  # Per-request model selection
    instructions="Summarize the text accurately.",  # Per-request instructions
    input="Synthetic example: the team completed testing and fixed two defects.",
    max_output_tokens=200,  # Per-request generation limit
)
```

Check the installed SDK and the selected model's documentation for
supported parameter names. A parameter can be valid in the SDK but
unsupported for a particular model or API mode.

A practical separation:

-   **Application configuration:** approved default model, environment,
    prompt version, policy limits.
-   **Client options:** credential, endpoint, timeout, connection
    settings, retry policy.
-   **Per-request parameters:** input, instructions, output limit, and
    model controls supported for that request.

Avoid allowing external users to override internal controls such as
credentials, endpoint, retry policy, or unrestricted model selection.

<br/>

## 7. Output Limits and Generation Controls

Generation settings affect the behavior, length, and sometimes the cost
of model responses. Their exact names and semantics are
provider-specific.

### Output limits

An output-token limit bounds how much the model may generate. It is not
the same as a word limit: tokens may be shorter or longer than words,
depending on the text and tokenizer.

Choose a limit that allows the expected answer to finish. A limit that
is too small may cause truncation; a very large limit may increase
worst-case latency and cost.

<br/>

### Sampling and other controls

Some models and APIs support controls such as temperature or
top-p. Others may omit, restrict, or interpret them differently.
Reasoning-oriented models may have different parameter support from
other model families.

Do not assume that every parameter is available for every model. Before
enabling a control:

1.  Check the current API reference for the endpoint.
2.  Check the selected model's capability notes.
3.  Validate the setting in application configuration.
4.  Test the behavior with representative inputs.
5.  Record the effective configuration for reproducibility.

If a required setting is unsupported, fail clearly or choose an
explicitly documented alternative. Do not silently ignore the setting
and claim the request used it.

<br/>

## 8. Timeouts, Reuse, and Resource Cleanup

### Timeouts

A timeout bounds how long the client waits for an operation at the
relevant network or request stage. Set a deliberate timeout appropriate
to the endpoint's latency requirements. A client timeout and an
application's overall request deadline may be different limits.

A timeout does not prove the provider never processed the request. This
matters when considering retries and possible duplicate cost.

<br/>

### Reuse clients

For a long-running API server, create a client at an appropriate
application lifecycle boundary and reuse it rather than constructing a
new client for every request. Reuse can preserve connection pooling and
reduce overhead.

<br/>

### Cleanup

Close clients when the application shuts down, using the lifecycle and
close method documented by the SDK. The exact method can differ between
synchronous and asynchronous clients and across SDKs.

Illustrative synchronous pattern:

``` python
from openai import OpenAI

client = OpenAI(timeout=30.0)

try:
    response = client.responses.create(
        model="gpt-5.5",
        input="Return one short greeting.",
    )
    print(response.output_text)
finally:
    client.close()
```

This is useful for a short script. In a server, closing a shared client
after each request would be incorrect; close it when the application
itself shuts down.

An asynchronous client has an asynchronous lifecycle and must be
awaited/closed according to the installed SDK's documentation. Do not
mix synchronous calls into an async request handler if they block the
event loop.

<br/>

## 9. Record Model and Prompt Versions

Model-backed outputs can change when the model, prompt, request
settings, SDK, or provider behavior changes. Record the configuration
needed to interpret results.

Useful fields include:

-   Provider name and endpoint type.
-   Model identifier and, where available, an immutable model version or
    snapshot.
-   SDK package version.
-   Prompt template identifier or version.
-   Effective per-request settings that affect generation.
-   Request ID, completion status, latency, and usage metadata when
    available.

Do not record secrets or unnecessary sensitive user content. If a
provider exposes only a moving model alias rather than a fixed snapshot,
document that limitation.

A simple application metadata record might look like this:

``` python
run_metadata = {
    "provider": "openai",
    "model": settings.openai_model,
    "prompt_version": settings.prompt_version,
    "timeout_seconds": settings.model_timeout_seconds,
    "max_output_tokens": settings.model_max_output_tokens,
}
```

This is application metadata, not a guarantee that the provider honored
every value. Record only settings actually used in the request and
distinguish configured defaults from effective request parameters.

<br/>

## 10. Detect Unsupported Settings Explicitly

A common configuration failure is silently accepting a setting that has
no effect. For example, an application may expose a temperature field
even when its chosen model or endpoint does not support it.

A safer pattern is to define capabilities for the supported model/API
combination and validate requested settings before sending a request.

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCapabilities:
    supports_temperature: bool
    supports_streaming: bool
    supports_structured_output: bool


def validate_temperature(
    temperature: float | None,
    capabilities: ModelCapabilities,
) -> None:
    if temperature is not None and not capabilities.supports_temperature:
        raise ValueError(
            "Temperature was configured, but this model configuration "
            "does not support it."
        )
```

The capability values must come from verified provider documentation or
a controlled, tested application configuration. Do not guess them from a
model name.

This example demonstrates the validation pattern only. It does not
provide a universal capability registry.

<br/>

## 11. Practice: Build and Validate Typed Configuration

Create a small project:

``` text
model-config-demo/
├── config.py
├── app.py
├── .env.example
├── .gitignore
└── requirements.txt
```

Use the `Settings` class from Section 5.

<br/>

### `requirements.txt`

``` text
pydantic-settings
openai
```

For reproducible work, pin the package versions you test or use a
dependency lock file.

<br/>

### `.env.example`

``` dotenv
OPENAI_API_KEY=replace-with-a-local-key
OPENAI_MODEL=replace-with-an-approved-model-id
APP_ENV=development
MODEL_TIMEOUT_SECONDS=30
MODEL_MAX_OUTPUT_TOKENS=500
PROMPT_VERSION=summarize-v1
```

<br/>


### `app.py`

``` python
from config import load_settings


def main() -> None:
    settings = load_settings()

    print("Configuration loaded successfully.")
    print("Environment:", settings.app_env)
    print("Model:", settings.openai_model)
    print("Prompt version:", settings.prompt_version)
    print("Timeout:", settings.model_timeout_seconds)
    print("Output token limit:", settings.model_max_output_tokens)
    print("Provider key configured:", bool(
        settings.openai_api_key.get_secret_value().strip()
    ))


if __name__ == "__main__":
    main()
```

<br/>

### Exercise steps

1.  Create a local `.env` from `.env.example`; never put a real key in
    the example file.
2.  Run the program and confirm valid configuration loads.
3.  Remove `OPENAI_API_KEY` and confirm startup validation fails.
4.  Set `MODEL_TIMEOUT_SECONDS=0` and confirm the validation constraint
    rejects it.
5.  Change `APP_ENV` to an unsupported value and inspect the validation
    error.
6.  Add a prompt version and record it with a sample run.
7.  Confirm no code prints or logs the API key.

This exercise validates configuration; it does not require making a paid
model request.

<br/>

## 12. Checkpoint Questions

1.  What is the difference between initializing a hosted API client and
    loading a local model?
2.  Which values belong in application configuration?
3.  Which settings belong to the SDK client?
4.  Which parameters belong to an individual request?
5.  Why should output limits and timeouts be explicit?
6.  Why should a shared API client normally be reused in a long-running
    service?
7.  When should the client be closed?
8.  Why should unsupported generation settings be rejected rather than
    silently ignored?
9.  Why record model and prompt versions?
10. Why is a configured model ID not proof that the model is available
    or that every parameter is supported?

<br/>

### Suggested answers

1.  A hosted client prepares software to communicate with a remote API;
    local loading places model weights and supporting components into
    local memory.
2.  Environment-specific settings, approved default model, prompt
    version, and application policy limits.
3.  Credentials, base URL where intentionally used, timeout, connection
    behavior, and SDK retry configuration.
4.  Input, instructions, model selection when permitted, output limits,
    and supported generation controls.
5.  They bound resource use and clarify expected behavior; overly small
    limits can truncate output while excessive limits can increase
    latency and cost.
6.  Reuse can preserve connections and reduce repeated setup overhead.
7.  At the end of the owning script or application lifecycle, using the
    SDK's documented cleanup method.
8.  Silent ignoring creates a mismatch between intended and actual
    behavior and makes debugging and reproducibility harder.
9.  They help explain and reproduce behavior changes across runs.
10. Availability depends on provider access and current capabilities;
    configuration must be checked against current documentation and
    tested.

<br/>

## 13. Key Takeaways

1.  Separate application settings, client options, and per-request
    parameters.
2.  Hosted API client initialization does not load model weights
    locally.
3.  Use typed settings and validate configuration during startup.
4.  Configure timeouts and output limits deliberately, within supported
    bounds.
5.  Reuse clients appropriately and close them at the correct lifecycle
    boundary.
6.  Record the model, SDK, prompt version, and effective settings needed
    for reproducibility.
7.  Verify model-specific capabilities instead of assuming all settings
    work everywhere.
8.  Keep secrets out of logs and client-visible responses.

<br/>

## References

-   [OpenAI Python SDK](https://github.com/openai/openai-python)
-   [OpenAI API documentation](https://platform.openai.com/docs/)
-   [Pydantic
    Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
-   [Hugging Face Transformers
    documentation](https://huggingface.co/docs/transformers/index)

<br/>

SDK constructor arguments, model identifiers, supported generation
parameters, and cleanup methods can change by version. Confirm them
against the installed SDK and current official provider documentation
before deployment.
