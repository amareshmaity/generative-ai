# 02. Direct Provider SDKs and a First Request

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Select a provider and consult its official SDK documentation.
-   Install and pin a compatible SDK version for reproducibility.
-   Make a minimal model request and inspect the response.
-   Distinguish an SDK, API endpoint, model identifier, and hosted
    service.
-   Identify request parameters, returned content, and available
    metadata.
-   Recognize that provider APIs and capabilities are not
    interchangeable.
-   Practice with synthetic input or a response fixture when live API
    access is unavailable.

<br/>

## 2. Provider Chosen for This Chapter

This chapter uses the **OpenAI API with the official OpenAI Python SDK**
as one concrete example. The purpose is to learn the general integration
pattern, not to imply that OpenAI is the only suitable provider.

Official references:

-   [Official OpenAI Python SDK repository and
    README](https://github.com/openai/openai-python)
-   [OpenAI API
    quickstart](https://developers.openai.com/api/docs/quickstart)
-   [OpenAI API documentation](https://platform.openai.com/docs/)

The SDK README identifies the Responses API as the primary API for
interacting with OpenAI models. The examples below therefore use
`client.responses.create(...)`. Confirm the current documentation before
copying examples into a production application, because SDK releases,
model availability, and API capabilities can change.

<br/>

## 3. Four Terms You Must Distinguish

These terms are related, but they describe different parts of an
integration.

| Term                 | Meaning                                                                                         | Example in This Chapter                          |
| -------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Hosted service**   | The provider-operated service that runs models and exposes capabilities over a network          | OpenAI API                                       |
| **API endpoint**     | A network interface that accepts a defined request and returns a response                       | Responses API endpoint, commonly `/v1/responses` |
| **SDK**              | A client library that helps application code construct requests, send them, and parse responses | Python package `openai`                          |
| **Model identifier** | The name or ID selecting a model available to the account and endpoint                          | `gpt-5.5` in the current official SDK example    |


The exact model identifier is not a Python class, a package name, or an
endpoint. It is a request parameter interpreted by the provider.

<br/>

### Request path

``` mermaid
flowchart LR
    A[Your Python application] --> B[OpenAI Python SDK]
    B --> C[Responses API endpoint]
    C --> D[Hosted OpenAI service]
    D --> E[Selected model]
    E --> D
    D --> C
    C --> B
    B --> F[Typed response object]
    F --> A
```

The SDK hides much of the low-level HTTP work, but the application still
needs to supply valid parameters, protect credentials, handle failures,
and inspect the returned result.

<br/>

## 4. Install and Pin the SDK

### 4.1 Create an isolated environment

Using a virtual environment helps keep project dependencies separate
from other Python projects.

``` bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**

``` powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

``` bash
source .venv/bin/activate
```

<br/>

### 4.2 Install a specific version

The official SDK repository lists the package as `openai` and documents
installation with `pip install openai`. For reproducibility, this
chapter pins the example to **`openai==3.26.0`**, the latest release
visible in the official repository at the time these notes were prepared
(12 October 2026).

``` bash
python -m pip install "openai==3.26.0"
```

Verify the installed version:

``` bash
python -c "import openai; print(openai.__version__)"
```

Expected version:

``` text
3.26.0
```

This is a version pin for the example, not a claim that this version
will remain the newest forever. When updating the SDK, read its release
notes, run your tests, and update the project's dependency lock or
pinned requirements deliberately.

Example `requirements.txt` entry:

``` text
openai==3.26.0
```

The official Python SDK currently documents Python 3.10+ as its
supported baseline. Use a supported Python version and verify
compatibility with the SDK version selected for your project.

<br/>

## 5. Configure an API Key Safely

A live request requires an API key with access to the selected service
and model. Create/manage credentials using the provider's official
platform. Do not paste a real key into source code, notebooks committed
to Git, screenshots, or logs.

Set an environment variable.

**Windows PowerShell --- current terminal session**

``` powershell
$env:OPENAI_API_KEY = "your-key-here"
```

**macOS/Linux --- current shell session**

``` bash
export OPENAI_API_KEY="your-key-here"
```

The SDK reads `OPENAI_API_KEY` by default when constructing `OpenAI()`.

For local development, a `.env` file can be used with a suitable
configuration loader such as `python-dotenv`, but the file must be
excluded from version control. Commit a `.env.example` with placeholder
values instead. For deployed services, use the platform's
secret-management facility where available.

**Never print the API key to check whether configuration worked.** Check
only whether the variable exists.

``` python
import os

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not configured.")
```

<br/>

## 6. Make the First Request

The official SDK demonstrates text generation with the Responses API.
This example sends synthetic, non-sensitive text.

``` python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    instructions="You are a concise technical assistant.",
    input="In two sentences, explain what an API is.",
)

print(response.output_text)
```

<br/>

### What each part means

-   `OpenAI()` constructs the synchronous SDK client. It reads the API
    key from the standard environment variable unless configured
    otherwise.
-   `client.responses.create(...)` sends a request through the Responses
    API.
-   `model` selects a model identifier supported for your account and
    endpoint.
-   `instructions` supplies high-level instructions for the model's
    response.
-   `input` supplies the task or content to process.
-   `response` is the SDK's response object.
-   `response.output_text` is a convenient SDK property for accessing
    the textual output when text is present.

Model availability and parameters can vary by account, model, and API.
If the example's model identifier is unavailable to your account, select
a currently supported model from the provider's official model
documentation and update the configuration. Do not assume a model name
works merely because it appears in an old tutorial.

<br/>

## 7. Inspect the Response Object

Do not treat the response as only a string. The SDK returns a structured
object that may contain output items, completion status, identifiers,
and usage information.

``` python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    instructions="Answer briefly and clearly.",
    input="What is the purpose of a Python virtual environment?",
)

print("Response ID:", response.id)
print("Status:", response.status)
print("Output text:", response.output_text)

if response.usage is not None:
    print("Usage:", response.usage)
else:
    print("Usage metadata is unavailable.")
```

Useful fields include:

-   **`response.id`** --- identifies the response in the provider's
    system.
-   **`response.status`** --- reports the response status exposed by the
    API.
-   **`response.output_text`** --- convenience access to textual output.
-   **`response.usage`** --- usage details when returned for that
    request.

Exact fields and their meanings depend on the API and SDK version.
Consult the response reference rather than assuming all providers use
the same object shape.

<br/>

### Do not confuse response status with answer quality

A request can succeed at the transport/API level while still producing
an answer that is unsuitable for the application. For example, the
answer may be irrelevant, factually wrong, empty for the task, or
incomplete. Later chapters cover response validation, usage accounting,
error handling, and evaluation in more depth.

<br/>

### Inspect a serialized response for debugging

For local exploration, SDK response models may support serialization
helpers such as `model_dump()`:

``` python
payload = response.model_dump()
print(payload)
```

Treat this as a debugging technique, not a production logging default.
Full responses may contain user content or other sensitive data. In
production, log selected safe fields and redact sensitive information.

<br/>

## 8. Request Parameters: What Are You Sending?

The first request uses these parameters:

| Parameter      | Purpose                                 | Example                            |
| -------------- | --------------------------------------- | ---------------------------------- |
| `model`        | Selects the model                       | `"gpt-5.5"`                        |
| `instructions` | Provides high-level behavioral guidance | `"Answer briefly and clearly."`    |
| `input`        | Provides the task or content            | `"Explain a virtual environment."` |


Other parameters may be supported, such as output limits,
structured-output configuration, streaming options, or tools. Their
names, supported values, defaults, and semantics vary by API and model.
Add them only after checking the current official reference.

A useful rule: **document every parameter that affects behavior**,
especially model ID, prompt/instructions version, output limits, and any
generation settings your application controls.

<br/>

## 9. SDK Versus Direct HTTP Requests

You can interact with an API through a provider's SDK or by sending HTTP
requests directly.

### Using an SDK

Advantages:

-   Convenient client methods.
-   Typed request parameters and response objects.
-   Less manual serialization and HTTP handling.
-   Provider-specific helpers and documented error classes.

Trade-offs:

-   Your code depends on the SDK's package and version.
-   New API capabilities may require a newer SDK release.
-   The SDK's abstractions may not match another provider's SDK.

<br/>

### Using direct HTTP

Advantages:

-   Makes the HTTP contract explicit.
-   Can be useful for debugging or in environments without an SDK.
-   Avoids relying on a provider-specific wrapper for the basic request.

Trade-offs:

-   You must manage headers, authentication, JSON encoding, response
    parsing, timeouts, and errors yourself.
-   You must keep the HTTP contract aligned with the provider's current
    API documentation.

For most Python applications, start with the official SDK unless there
is a concrete reason to use raw HTTP. This chapter focuses on the SDK
approach.

<br/>

## 10. Provider Capabilities Are Not Identical

Do not assume that one provider's request structure, model names, or
response fields can be copied directly to another provider.

Differences can include:

-   Message roles and instruction handling.
-   API endpoint paths and method names.
-   Model identifiers and availability.
-   Structured-output support and schema restrictions.
-   Streaming event formats.
-   Tool/function-call schemas and result correlation.
-   Usage metadata and token accounting.
-   Rate limits, retry hints, and error types.
-   Image, audio, video, and other modality support.

Even when two providers support the same broad capability, the request
format and behavior may differ. A provider adapter can normalize the
subset your application needs, but it cannot guarantee identical model
quality or identical feature support.

<br/>

### Capability-check workflow

``` mermaid
flowchart TD
    A[Choose a use case] --> B[Read official provider docs]
    B --> C[Confirm model access]
    C --> D[Confirm required API capabilities]
    D --> E{Requirements supported?}
    E -- No --> F[Choose another model/provider or revise requirements]
    E -- Yes --> G[Pin SDK and model configuration]
    G --> H[Run a small representative test]
    H --> I[Record output, status, latency, and usage]
```

<br/>

## 11. Offline Practice: Inspect a Response Fixture

If you do not have an API key, cannot access a model service, or want to
test parsing without making a paid request, use a fixture that resembles
a simplified response your application has normalized.

The following example is **an application-defined fixture**, not a
literal OpenAI SDK response. Its shape is intentionally simple and
provider-neutral.

``` python
fixture = {
    "response_id": "resp_example_001",
    "status": "completed",
    "text": "A virtual environment isolates project dependencies.",
    "usage": {
        "input_tokens": 18,
        "output_tokens": 9,
    },
}

response_id = fixture["response_id"]
status = fixture["status"]
text = fixture["text"]
usage = fixture.get("usage")

print("Response ID:", response_id)
print("Status:", status)
print("Text:", text)
print("Usage:", usage if usage is not None else "Unavailable")
```

This offline exercise tests your code's handling of known fields. It
does not verify live authentication, network connectivity, model
availability, provider response parsing, or model quality.

<br/>

## 12. Common First-Request Failures

| Symptom                                  | Possible Cause                                             | What to Check                                                                               |
| ---------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Missing API key / authentication failure | Environment variable is absent, invalid, or not authorized | Check configuration presence without printing the secret                                    |
| Model not found or unavailable           | Typo, account access, or model availability changed        | Verify the model identifier and account access in official documentation                    |
| Invalid request                          | Unsupported parameter or malformed input                   | Compare the request with the current API reference                                          |
| Rate limit / throttling                  | Request or token limit reached                             | Inspect provider guidance and account limits; reliability handling is covered in Chapter 12 |
| Network timeout                          | Connectivity issue or slow service                         | Add an appropriate timeout and safe error handling in application code                      |
| Empty or unexpected text                 | Output shape or completion state differs from assumptions  | Inspect status and output items; do not assume every response is a normal text answer       |


Do not respond to every error by retrying immediately. Authentication
and invalid-request errors usually require correction. Retry behavior,
backoff, rate limits, and deadlines are covered in Chapter 12.

<br/>

## 13. Practice: Make One Small Request

### Live exercise

1.  Create and activate a virtual environment.
2.  Install the pinned SDK version or deliberately choose a newer
    verified release.
3.  Configure the API key as an environment variable.
4.  Send a short request using synthetic text.
5.  Print the response ID, status, textual output, and usage metadata if
    available.
6.  Record the installed SDK version and model identifier used.
7.  Record any failure and how you diagnosed it. Do not include the API
    key in your notes.

<br/>

### Offline exercise

If you cannot make a live request, run the fixture example in Section 11
and explain which real-world behaviors it does and does not test.

<br/>

## 14. Checkpoint: Identify the Request and Response

For the example below:

``` python
response = client.responses.create(
    model="gpt-5.5",
    instructions="Answer in one sentence.",
    input="What does an API do?",
)
```

Answer these questions:

1.  Which parameter selects the model?
2.  Which parameter contains the task?
3.  Which parameter provides the instruction?
4.  What is the difference between the SDK and the API endpoint?
5.  Which property is used to access text conveniently?
6.  Why should usage metadata be checked for availability?
7.  Why is the same request not guaranteed to work unchanged with
    another provider?

<br/>

### Suggested answers

1.  `model`.
2.  `input`.
3.  `instructions`.
4.  The SDK is a client library used by application code; the endpoint
    is the network interface that receives the API request.
5.  `response.output_text`, when textual output is present.
6.  Some responses or API modes may not include usage metadata; missing
    usage should not be interpreted as zero.
7.  Providers differ in endpoint paths, request schemas, model IDs,
    supported parameters, response formats, and capability semantics.

<br/>

## 15. Key Takeaways

1.  Use official provider documentation as the authority for SDK
    installation, request formats, and supported capabilities.
2.  Pin SDK versions for reproducibility and update them through tested
    changes.
3.  Distinguish the hosted service, API endpoint, SDK, and model
    identifier.
4.  Start with one minimal request and inspect the structured
    response---not just the generated text.
5.  Treat model availability and API capabilities as provider- and
    account-dependent.
6.  Use synthetic input for live experiments and fixtures for offline
    tests.
7.  Never hard-code or log provider credentials.
8.  A successful request does not guarantee that the generated answer is
    correct or suitable.

<br/>

## References

-   [Official OpenAI Python SDK
    README](https://github.com/openai/openai-python)
-   [OpenAI API
    quickstart](https://developers.openai.com/api/docs/quickstart)
-   [OpenAI API documentation](https://platform.openai.com/docs/)
-   [OpenAI Python SDK
    releases](https://github.com/openai/openai-python/releases)

<br/>

**Version note:** These notes pin `openai==3.26.0` based on the official
repository release visible on 12 October 2026. Recheck the release page
and SDK compatibility policy before using this pin in a new project.
