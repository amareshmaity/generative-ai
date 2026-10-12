# Chapter 13: Provider Abstraction and Model Portability

## Learning objectives

By the end of this chapter, you should be able to:

-   Define a small model-client interface around the capabilities an
    application actually uses.
-   Normalize text results, structured data, errors, and usage without
    losing important distinctions.
-   Implement provider-specific adapters and explicit capability checks.
-   Compare differences in roles, structured-output schemas, tool
    calling, streaming, and generation controls.
-   Test behavior when switching models or providers.
-   Reject unsupported features explicitly rather than silently
    downgrading them.
-   Build a fake adapter and a real provider adapter, then document a
    second provider in a comparison matrix.

<br/>

## 1 What provider abstraction solves---and what it does not

Applications often begin with one provider's SDK. As the application
grows, provider-specific types can spread through business logic, route
handlers, tests, and monitoring. This makes changing providers or
testing the application more difficult.

A **provider abstraction** places a small application-owned interface
between business logic and the vendor SDK. Each provider adapter
translates between that interface and the provider's native API.

``` mermaid
flowchart TD
    A[Application logic] --> B[Application-owned model interface]
    B --> C[Fake adapter for tests]
    B --> D[Provider A adapter]
    B --> E[Provider B adapter]
    C --> F[Normalized application result]
    D --> F
    E --> F
```

The goal is not to make all providers identical. It is to isolate
vendor-specific details while keeping meaningful differences visible.

A shared method such as `generate_text()` can standardize how the
application asks for text. It cannot guarantee identical reasoning,
instruction following, safety behavior, latency, output quality, or
token accounting across models.

<br/>

## 2 Design the smallest useful interface

Start from application requirements, not from the complete feature set
of a provider SDK. If the application only needs text generation, a
large universal interface for every provider feature adds unnecessary
complexity.

For a simple text-generation service, the interface might require:

-   A prompt or a list of normalized messages.
-   A model identifier resolved by configuration.
-   A small set of supported generation options.
-   A normalized text result.
-   Usage and request metadata when available.
-   A normalized application error category.

Features such as structured output, tool calling, multimodal input, and
streaming should be added only when the application needs them. They may
require distinct methods or typed request objects.

<br/>

### A normalized contract

``` python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Usage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    source: str = "unavailable"


@dataclass
class GenerationResult:
    text: str
    requested_model: str
    reported_model: str | None = None
    provider_request_id: str | None = None
    finish_status: str = "unknown"
    usage: Usage | None = None


class TextModel(Protocol):
    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> GenerationResult:
        ...
```

This contract is deliberately small. The `messages` list uses a
normalized role/content representation, but a production application
should validate roles and content before invoking an adapter.

The result distinguishes the model requested by the application from the
model reported by the provider. It also allows usage metadata to be
unavailable. Missing usage must not be represented as zero.

<br/>

### Avoid over-normalization

Do not flatten every provider response into a single string if the
application needs to distinguish:

-   A refusal from a normal answer.
-   An incomplete response from a completed one.
-   Tool calls from user-facing text.
-   Structured output from free-form text.
-   Partial streaming output from a complete stream.
-   Observed usage from estimated or missing usage.

If those distinctions matter, represent them explicitly in the shared
contract. Keep the original provider response or selected raw metadata
available in a privacy-reviewed diagnostic path when needed.

<br/>

## 3 Implement a fake adapter first

A fake adapter makes tests fast, deterministic, and independent of API
credentials or network availability. It is useful for testing business
logic, request validation, failure handling, and response processing.

``` python
class FakeTextModel:
    def __init__(self, response_text="Test response"):
        self.response_text = response_text
        self.calls = []

    def generate(
        self,
        messages,
        *,
        temperature=None,
        max_output_tokens=None,
    ):
        self.calls.append({
            "messages": messages,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        })

        return GenerationResult(
            text=self.response_text,
            requested_model="fake-model",
            reported_model="fake-model",
            provider_request_id="fake-request-001",
            finish_status="completed",
            usage=Usage(
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                source="unavailable",
            ),
        )
```

Example test:

``` python
def test_service_uses_model():
    model = FakeTextModel("A test summary.")
    result = model.generate(
        [{"role": "user", "content": "Summarize this."}],
        max_output_tokens=100,
    )

    assert result.text == "A test summary."
    assert result.finish_status == "completed"
    assert model.calls[0]["max_output_tokens"] == 100
```

The fake should behave like the application contract, not pretend to
reproduce a real model's intelligence. It can simulate errors and
missing metadata, too.

<br/>

## 4 Implement a real provider adapter

The adapter below uses the OpenAI Python SDK's Responses API as one
concrete example. SDK methods and response fields can change, so check
the installed SDK version and current documentation.

``` python
from openai import OpenAI


class OpenAITextModel:
    def __init__(self, model: str, client: OpenAI | None = None):
        self.model = model
        self.client = client or OpenAI()

    def generate(
        self,
        messages,
        *,
        temperature=None,
        max_output_tokens=None,
    ):
        request = {
            "model": self.model,
            "input": messages,
        }

        if temperature is not None:
            request["temperature"] = temperature
        if max_output_tokens is not None:
            request["max_output_tokens"] = max_output_tokens

        response = self.client.responses.create(**request)
        provider_usage = getattr(response, "usage", None)

        usage = None
        if provider_usage is not None:
            usage = Usage(
                input_tokens=getattr(provider_usage, "input_tokens", None),
                output_tokens=getattr(provider_usage, "output_tokens", None),
                total_tokens=getattr(provider_usage, "total_tokens", None),
                source="provider",
            )

        return GenerationResult(
            text=getattr(response, "output_text", "") or "",
            requested_model=self.model,
            reported_model=getattr(response, "model", None),
            provider_request_id=getattr(response, "id", None),
            finish_status="completed",
            usage=usage,
        )
```

This adapter is a teaching baseline, not a complete production
integration. A production adapter should also:

-   Validate message roles and content types.
-   Map refusal, incomplete, and failed responses explicitly.
-   Map provider exceptions into application-defined error categories.
-   Avoid passing unsupported generation parameters.
-   Capture the actual provider request ID from the documented
    response/header field.
-   Handle structured output, tool calls, streaming, and multimodal
    content only if required.
-   Add tests against the installed SDK and a small integration test
    against the real API.

**Important:** this minimal example marks a returned response as
completed. For production use, derive `finish_status` from the
documented response status and handle non-completed responses
explicitly.

<br/>

## 5 Provider capabilities should be explicit

Different providers, endpoints, and models may support different subsets
of features. Support can also vary by model version, API endpoint, SDK
version, and account configuration.

A capability declaration can make those differences visible:

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCapabilities:
    text_generation: bool
    structured_output: bool
    tool_calling: bool
    streaming: bool
    async_calls: bool
    cached_input_usage: bool
    reasoning_usage: bool
```

A configured adapter can expose its capabilities:

``` python
class ModelCapabilityError(RuntimeError):
    pass


def require_capability(capabilities, feature: str):
    if not hasattr(capabilities, feature):
        raise ValueError(f"Unknown capability: {feature}")

    if not getattr(capabilities, feature):
        raise ModelCapabilityError(
            f"Configured model does not support required feature: {feature}"
        )
```

Example:

``` python
capabilities = ModelCapabilities(
    text_generation=True,
    structured_output=True,
    tool_calling=True,
    streaming=True,
    async_calls=True,
    cached_input_usage=False,
    reasoning_usage=False,
)

require_capability(capabilities, "structured_output")
```

Treat capability declarations as configuration backed by verified
documentation and tests, not as assumptions based only on a provider
name. When support varies across models, store capabilities with the
selected model configuration.

<br/>

### Fail explicitly instead of silently downgrading

Suppose a workflow requires schema-constrained output. If the selected
provider/model cannot provide that feature, do not quietly replace it
with "ask the model to return JSON" unless the application explicitly
permits that fallback and validates the result. A prompt requesting JSON
is not equivalent to an API-enforced schema.

Use a clear error or an explicitly configured fallback strategy with
validation and observability.

<br/>

## 6 Normalize text results, structured data, errors, and usage

A portability layer should normalize only the concepts the application
actually uses.

### Text results

Normalize the extracted text, requested/reported model, request
identifier, completion status, and usage. Do not assume that all
providers expose text in the same response field or that all output
items are plain text.

<br/>

### Structured output

Providers may offer different structured-output mechanisms:

-   Schema-constrained generation.
-   JSON mode without full schema enforcement.
-   Tool/function calling used to return structured arguments.
-   Prompt-only JSON instructions.

These approaches have different guarantees. If your application requires
schema adherence, make the guarantee part of the contract and validate
the parsed result locally. Do not map all four mechanisms to a
capability called `structured_output=True` without defining what that
capability promises.

<br/>

### Errors

Map vendor-specific exceptions into stable application categories, such
as:

-   `authentication`
-   `permission`
-   `invalid_request`
-   `rate_limit`
-   `timeout`
-   `temporary_provider_failure`
-   `incomplete_response`
-   `unknown`

Preserve diagnostic information internally after redaction, but return
safe application errors to callers. Do not expose API keys, raw headers,
stack traces, or unredacted provider payloads.

<br/>

### Usage

Use `None` for unknown counts. Record whether usage was
provider-reported, locally estimated, partial, or unavailable. Do not
assume provider token counts use identical accounting rules.

<br/>

## 7 Portability differences to document

Before selecting a second provider, fill out a comparison matrix using
current documentation and tests. The table below is a template, not a
claim that any particular provider supports every feature.

| Capability or Behavior                | Provider A                                             | Provider B | Application Decision                                                           |
| ------------------------------------- | ------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------ |
| Message roles and role restrictions   | Verify                                                 | Verify     | Normalize supported roles; reject unsupported roles or define a tested mapping |
| System/developer instruction handling | Verify                                                 | Verify     | Test instruction priority and behavior                                         |
| Structured output                     | Schema API, JSON mode, tool-based, or prompt-only?     | Verify     | Require the exact guarantee the workflow needs                                 |
| Tool/function calling                 | Argument schema, parallel calls, call/result format    | Verify     | Normalize tool-call lifecycle and validate arguments                           |
| Streaming                             | Event format, completion marker, usage event           | Verify     | Convert to application-owned events and handle interrupted streams             |
| Async support                         | Native async client or wrapper                         | Verify     | Define cancellation and timeout behavior                                       |
| Generation controls                   | Temperature, token limits, stop sequences, top-p, etc. | Verify     | Pass only supported options; do not silently ignore unsupported options        |
| Usage metadata                        | Input/output/cached/reasoning fields                   | Verify     | Preserve unknown fields and accounting differences                             |
| Errors and retry hints                | Status codes, exception types, `Retry-After`           | Verify     | Map into shared error categories and retry policy                              |
| Model identifiers and versioning      | Naming/version semantics                               | Verify     | Keep model configuration explicit and traceable                                |
| Context and output limits             | Model-specific limits                                  | Verify     | Validate or budget requests per selected model                                 |
| Safety/refusal behavior               | Provider/model-specific                                | Verify     | Evaluate using application test cases                                          |


"Verify" is intentional: capabilities change and can differ by endpoint
or model. Populate the matrix from the exact candidate model
documentation, SDK, and test results before making a production switch.

<br/>

## 8 Switching providers is a behavioral change

A common mistake is to treat provider portability as a
configuration-only change. Even if both adapters implement the same
method signature, model behavior can differ in ways that affect
application correctness.

Test at least:

-   Instruction following and response format.
-   Structured-output validity and semantic correctness.
-   Tool selection, argument correctness, and tool-call ordering.
-   Refusal and safety behavior.
-   Streaming event order and final completion detection.
-   Token usage and cost accounting.
-   Latency and timeout behavior.
-   Long-context performance and truncation behavior.
-   Multilingual, domain-specific, and edge-case performance relevant to
    the product.

Use a fixed evaluation set, run both implementations, and compare
results against acceptance criteria. For stochastic outputs, use
task-appropriate scoring and repeated runs where necessary. Do not
require byte-for-byte equality when the real requirement is semantic or
task-level equivalence.

``` mermaid
flowchart TD
    A[Choose candidate provider/model] --> B[Verify documented capabilities]
    B --> C[Run adapter contract tests]
    C --> D[Run fixed task evaluation set]
    D --> E[Compare quality, failures, latency, and cost]
    E --> F{Acceptance criteria met?}
    F -->|Yes| G[Controlled rollout]
    F -->|No| H[Adjust adapter, configuration, or model choice]
    H --> C
```

<br/>

## 9 Example: provider-neutral service with dependency injection

Business logic should depend on the interface rather than constructing a
vendor SDK client inside every function.

``` python
class SummaryService:
    def __init__(self, model: TextModel):
        self.model = model

    def summarize(self, text: str) -> str:
        if not text.strip():
            raise ValueError("Text must not be empty")

        result = self.model.generate(
            [{"role": "user", "content": f"Summarize this text:\n\n{text}"}],
            max_output_tokens=200,
        )

        if result.finish_status != "completed":
            raise RuntimeError("Model response was not completed")

        return result.text
```

Use dependency injection to choose the adapter at application startup:

``` python
# Tests
service = SummaryService(FakeTextModel("A concise summary."))

# Production configuration: create a real adapter with the selected model.
# service = SummaryService(OpenAITextModel(model="configured-model"))
```

In production, map `RuntimeError` and other internal failures to the
application error contract described earlier. The example keeps the
service compact to show the dependency boundary.

<br/>

## 10 Practice: fake adapter, real adapter, and second-provider matrix

Complete these tasks:

1.  Define a small `TextModel` protocol and a normalized result object.
2.  Implement `FakeTextModel` with deterministic output and captured
    call arguments.
3.  Write a contract test that can be run against any adapter.
4.  Implement one real provider adapter using the current SDK
    documentation; verify its response and error mappings.
5.  Ensure missing usage remains `None` and the source is recorded.
6.  Add explicit capability declarations for structured output and
    streaming.
7.  Make the application reject a required feature when the selected
    model does not support it.
8.  Fill in the provider comparison matrix for one candidate second
    provider using current official documentation.
9.  Create a small fixed evaluation set and compare outputs,
    structured-output validity, latency, and estimated cost.
10. Document any feature that cannot be mapped without loss and decide
    whether to expose it as a provider-specific extension.

<br/>

### Suggested adapter contract tests

``` python
def assert_text_model_contract(model: TextModel):
    result = model.generate(
        [{"role": "user", "content": "Reply with one short sentence."}],
        max_output_tokens=50,
    )

    assert isinstance(result, GenerationResult)
    assert isinstance(result.text, str)
    assert result.requested_model
    assert result.finish_status in {
        "completed", "incomplete", "refused", "failed", "unknown"
    }

    if result.usage is not None:
        for count in (
            result.usage.input_tokens,
            result.usage.output_tokens,
            result.usage.total_tokens,
        ):
            assert count is None or count >= 0
```

A live adapter contract test may incur cost and be nondeterministic.
Separate pure unit tests with the fake adapter from a small, controlled
integration test suite for the real provider.

<br/>

### Checkpoint answer

A shared interface standardizes how the application calls a model and
consumes selected metadata. It does not make models behaviorally
equivalent. Providers differ in role semantics, schema guarantees,
tool-call protocols, streaming events, generation controls, token
accounting, context limits, error handling, and safety behavior. Models
can also produce different answers under the same nominal settings.

Portability therefore requires explicit capability checks,
provider-specific adapters, clear error and usage normalization, and
evaluation tests before switching. Unsupported features should fail
clearly or use a deliberately configured and validated fallback---not be
silently ignored.

<br/>

## References

-   [OpenAI API documentation](https://platform.openai.com/docs)
-   [OpenAI Python SDK](https://github.com/openai/openai-python)
-   [Anthropic API documentation](https://docs.anthropic.com/)
-   [Google Gemini API
    documentation](https://ai.google.dev/gemini-api/docs)
-   [Python typing:
    Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
-   [Pydantic documentation](https://docs.pydantic.dev/)

Provider APIs, SDK methods, model capabilities, and limits change.
Verify the exact model and endpoint behavior before declaring a
capability portable.
