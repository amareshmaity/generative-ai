# Chapter 15: Request and Response Validation

## Learning objectives

By the end of this chapter, you should be able to:

-   Bound request length, output budgets, and supported task parameters.
-   Allow only configured models and generation options.
-   Apply business rules that go beyond basic field-type validation.
-   Return consistent success and error contracts.
-   Validate generated output before storing it or passing it
    downstream.
-   Distinguish ordinary JSON responses from streaming event contracts.
-   Test invalid inputs, unsupported options, oversized requests, and
    invalid model output.

<br/>

## 1 Validation is a boundary, not a single check

LLM applications accept untrusted input and produce output that may be
incomplete, malformed, or semantically wrong. Validation should
therefore happen at multiple boundaries.

``` mermaid
flowchart TD
    A[HTTP request] --> B[Validate shape and size]
    B --> C[Validate model and allowed options]
    C --> D[Apply business rules and authorization]
    D --> E[Provider call]
    E --> F[Validate completion and output structure]
    F --> G[Apply semantic and business checks]
    G --> H[Store, return, or pass downstream]
    B -->|Invalid| X[Consistent client error]
    C -->|Unsupported| X
    D -->|Rejected| X
    F -->|Invalid output| Y[Safe upstream/output error]
    G -->|Business rule failed| Y
```

**Pre-call validation** prevents invalid, oversized, unauthorized, or
unsupported work from reaching the provider. **Post-call validation**
determines whether the provider's result is safe and fit for the next
step.

A successful HTTP response from the provider does not prove that the
generated content satisfies your application's schema or business rules.

<br/>

## 2 Bound request size and input length

Unbounded input can increase cost and latency, exceed model context
limits, and create denial-of-service risks. Set explicit limits for each
task.

Example with Pydantic:

``` python
from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
```

This enforces character length, not token count. Character limits are
useful as a first boundary, but they are not a precise substitute for
token budgeting. Tokenization varies by model and may include message
formatting, instructions, tool schemas, and multimodal content.

A production request path may use both:

1.  A character or byte limit before expensive processing.
2.  A model-aware token estimate where useful.
3.  A conservative context budget that reserves room for instructions
    and generated output.
4.  A final provider-side context-limit check, with clear handling for
    rejection.

Do not trust a client-supplied token count as authoritative. Estimate or
calculate it on the server using the appropriate tokenizer or
provider-supported method.

<br/>

### Bound output budgets too

Do not let callers request unlimited generation. Define a server-owned
maximum output budget and enforce task-specific limits.

``` python
from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30_000)
    max_output_tokens: int = Field(default=300, ge=1, le=800)
```

This schema demonstrates a numeric range, but a public API should
usually choose a safe default and maximum based on the selected task and
allowed model. Do not let arbitrary client values override
deployment-level limits.

<br/>

## 3 Allow only configured models and options

A public endpoint should not accept an arbitrary model name, provider
URL, SDK configuration object, or unrestricted list of generation
parameters. Doing so can bypass cost controls, expose unintended
backends, or request features your service does not support.

Use an allowlist:

``` python
from typing import Literal
from pydantic import BaseModel, Field


AllowedModel = Literal["fast-model", "quality-model"]


class GenerationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12_000)
    model: AllowedModel = "fast-model"
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=300, ge=1, le=800)
```

The model names above are illustrative application aliases, not real
provider model identifiers. Resolve aliases through server-side
configuration:

``` python
MODEL_CONFIG = {
    "fast-model": {"provider": "provider_a", "model_id": "configured-fast-id"},
    "quality-model": {"provider": "provider_a", "model_id": "configured-quality-id"},
}
```

Never trust the request body to select arbitrary provider credentials,
endpoints, or internal configuration. The server should own the mapping.

<br/>

### Validate cross-field constraints

Field validation checks one value at a time. Some constraints depend on
multiple fields or the selected task.

For example:

-   A summarization task may have a smaller maximum output budget than
    extraction.
-   A particular model may not support a requested generation parameter.
-   A request requiring schema-constrained output must select a model
    and adapter that support that contract.
-   Streaming and ordinary JSON output may require different response
    modes.

Implement these rules in a service or configuration-validation layer,
not only as prompt instructions.

<br/>

## 4 Apply business rules beyond field types

A value can have the correct type and still be invalid for the
application. A string may be too vague, a category may be unknown, or a
numeric amount may violate a domain rule.

For structured extraction, use constrained types where possible and add
semantic checks:

``` python
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class TicketExtraction(BaseModel):
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def check_summary(self):
        if not self.summary.strip():
            raise ValueError("Summary must contain non-whitespace text")
        return self
```

The model validator checks a business-relevant property that a basic
string type would not enforce. For more complex applications, keep
domain rules in explicit functions or domain services so they can be
tested independently.

Examples of business rules:

-   A priority must be one of the application's supported values.
-   A date range must have an end date after the start date.
-   An extracted identifier must match a known format.
-   A referenced account or product must exist and be accessible to the
    caller.
-   An amount must be within permitted business bounds.
-   A summary must not be empty or exceed the storage limit.

Validation is not authorization: even a syntactically valid account ID
must be checked against the authenticated caller's permissions.

<br/>

## 5 Validate generated output before using it

Model output is untrusted input from the application's perspective.
Validate it before storing it, returning it as a typed object,
triggering a workflow, or passing it to another service.

A robust post-call sequence is:

1.  Confirm the provider response completed successfully.
2.  Detect refusal, truncation, or incomplete output where the API
    exposes those states.
3.  Parse the output using the expected schema or structured-output
    mechanism.
4.  Validate field constraints and domain rules.
5.  Verify references against trusted application data when required.
6.  Only then persist the result or perform downstream actions.

``` python
import json
from pydantic import ValidationError


def validate_extraction_json(raw_text: str) -> TicketExtraction:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("Model output was not valid JSON") from exc

    try:
        return TicketExtraction.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Model output did not satisfy the schema") from exc
```

This example assumes `raw_text` is expected to contain a JSON object. If
the provider offers schema-constrained output, use that capability where
appropriate---but still apply local validation and business rules. Do
not parse arbitrary prose by stripping text until it happens to resemble
JSON.

<br/>

### Validation failure is not a success

If generated output fails validation:

-   Do not store it as a valid domain record.
-   Do not pass it to a downstream action as if it were trusted.
-   Record a safe failure category and request ID.
-   Decide whether a bounded repair/retry is allowed by the task's
    policy.
-   Avoid repeatedly asking the model to repair output without a retry
    budget.
-   Keep the original raw output only when justified by privacy,
    security, and retention policy.

<br/>

## 6 Consistent success and error contracts

A public API should define a stable success shape and a stable error
shape. Clients should not need to parse provider-specific exception text
to decide what to do.

Example success schema:

``` python
from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    request_id: str
    result: TicketExtraction
```

Example application error schema:

``` python
from typing import Literal
from pydantic import BaseModel


class APIErrorDetail(BaseModel):
    code: Literal[
        "invalid_request",
        "unsupported_model",
        "unsupported_option",
        "provider_timeout",
        "invalid_model_output",
        "provider_unavailable",
    ]
    message: str
    request_id: str


class APIError(BaseModel):
    error: APIErrorDetail
```

<br/>

The exact HTTP status codes are part of the API contract. A reasonable
mapping might be:

| Condition                                       | Typical HTTP Status                 | Reason                                           |
| ----------------------------------------------- | ----------------------------------- | ------------------------------------------------ |
| Malformed or field-invalid request              | `422`                               | Client input does not satisfy the request schema |
| Unsupported model or option                     | `422`                               | The requested configuration is not allowed       |
| Authentication required for your application    | `401`                               | Caller is not authenticated                      |
| Authenticated caller lacks permission           | `403`                               | Caller is not authorized                         |
| Provider timeout                                | `504`                               | Upstream operation exceeded its time budget      |
| Provider unavailable or invalid provider output | `502` or `503`, depending on policy | Upstream could not provide a usable result       |
| Unexpected internal error                       | `500`                               | Unhandled application failure                    |


Use one consistent error envelope and avoid exposing raw provider
messages, API keys, headers, stack traces, or internal hostnames.
Include a request ID for support and diagnostics.

<br/>

## 7 Validate model and task parameters at the service boundary

Request-schema validation is the first gate, but the service should
still validate assumptions that depend on configuration or
authorization.

``` python
class UnsupportedOptionError(Exception):
    pass


def validate_generation_options(
    *,
    model_alias: str,
    temperature: float,
    max_output_tokens: int,
    model_config: dict,
):
    if model_alias not in model_config:
        raise UnsupportedOptionError("Unsupported model")

    config = model_config[model_alias]

    if max_output_tokens > config["max_output_tokens"]:
        raise UnsupportedOptionError("Output budget exceeds model policy")

    if temperature not in config["allowed_temperature_values"]:
        # Example of an overly strict policy: real applications will
        # usually validate a supported range or configured set.
        raise UnsupportedOptionError("Temperature is not allowed")
```

This is a policy example, not a universal temperature-validation design.
A production implementation should model supported parameter ranges and
capabilities accurately for each configured model. The request schema
and service policy should agree; do not rely on either layer alone for
every cross-field rule.

<br/>

## 8 Regular JSON responses versus streaming event contracts

A JSON endpoint typically returns one complete response body that can be
validated against a Pydantic response model.

A streaming endpoint sends multiple events over time. It needs a
separate event contract, including event types, payload shape, and a
terminal completion or error event. It cannot simply reuse the same JSON
response model for the entire stream.

``` mermaid
flowchart LR
    A[Validated request] --> B[Service and provider]
    B --> C{Response mode}
    C -->|JSON| D[Validate complete result]
    D --> E[Return one response object]
    C -->|Stream| F[Validate/map each event]
    F --> G[Emit delta events]
    G --> H[Emit completed or error event]
```

An example event schema:

``` python
from typing import Literal
from pydantic import BaseModel


class StreamEvent(BaseModel):
    type: Literal["delta", "completed", "error"]
    request_id: str
    text: str | None = None
    code: str | None = None
```

For a streaming contract, define rules such as:

-   `delta` requires text.
-   `completed` is emitted only after normal completion.
-   `error` contains an application-defined safe code.
-   Every event includes the same request ID.
-   No further deltas follow a terminal event.

Pydantic's type annotations alone do not enforce every cross-field rule;
add a model validator if needed. Also note that validating each event
does not make a stream atomic: clients may already have received earlier
events when a later failure occurs.

<br/>

## 9 Practice: invalid input and output

Use the models and validation functions in this chapter to test the
following cases:

1.  Empty text and text longer than the configured character limit.
2.  Unknown model alias.
3.  Negative temperature, temperature outside the permitted range, or an
    unsupported generation parameter.
4.  Output-token budget larger than the configured model/task maximum.
5.  A structured result with an unknown category.
6.  A structured result with an empty summary.
7.  Malformed JSON from the model.
8.  A provider response marked incomplete or refused.
9.  A stream event missing its required text or containing an unknown
    event type.
10. A valid-looking identifier that the authenticated caller is not
    authorized to access.

Example unit tests:

``` python
import pytest
from pydantic import ValidationError


def test_empty_input_is_rejected():
    with pytest.raises(ValidationError):
        ExtractionRequest(text="")


def test_unknown_category_is_rejected():
    with pytest.raises(ValidationError):
        TicketExtraction(
            category="shipping",
            priority="medium",
            summary="Order delivery question.",
        )


def test_unknown_model_is_rejected():
    with pytest.raises(UnsupportedOptionError):
        validate_generation_options(
            model_alias="unconfigured-model",
            temperature=0.2,
            max_output_tokens=100,
            model_config={},
        )
```

Run the tests without calling a real provider. Use fake provider
responses for malformed JSON, incomplete output, refusal, and provider
errors. Add a small integration test for the real adapter separately.

<br/>

### Practice deliverable

Create a test report with columns:

-   Test case
-   Validation stage (pre-call, post-call, or stream-event)
-   Expected result
-   Actual result
-   HTTP status or internal error code
-   Whether the provider was called

The final column helps prove that invalid requests are rejected before
consuming provider resources.

<br/>

## 10 Common mistakes

-   Using character length as if it were an exact token count.
-   Accepting arbitrary model names or provider configuration from
    public requests.
-   Assuming type validation covers authorization or domain rules.
-   Trusting generated JSON without parsing and validating it.
-   Treating a refusal or incomplete response as a normal successful
    result.
-   Returning raw provider errors to the caller.
-   Allowing callers to choose unlimited output budgets.
-   Using one response model for both complete JSON responses and
    streams.
-   Emitting a `completed` stream event after an upstream failure.
-   Retrying invalid model output indefinitely without a bounded policy.

<br/>

## 11 Practice and revision

-   Define Pydantic request models with explicit length and numeric
    bounds.
-   Implement an allowlist for model aliases and supported generation
    options.
-   Add domain-level validation for a structured extraction result.
-   Define a stable success schema and error envelope.
-   Validate generated output before persistence or downstream use.
-   Define separate contracts for JSON responses and stream events.
-   Test invalid input, unsupported options, excessive sizes, and
    invalid model output.
-   Confirm invalid pre-call cases do not invoke the provider.

<br/>

### Checkpoint answer

**Before the provider call**, validate request shape and field
constraints, input length or size, allowed model aliases, supported
generation options, output-token budgets, authentication/authorization,
and task-specific business rules that can be checked from trusted
application data. These checks avoid unnecessary cost and reject invalid
or unauthorized work early.

**After the provider call**, inspect completion/refusal status, parse
and validate generated output, enforce schema and business rules, verify
references against trusted data, and only then store or pass the result
downstream. Streaming requires event-level contracts and explicit
terminal states because some output may already have been delivered
before a later failure.

<br/>

## References

-   [FastAPI request body and Pydantic
    models](https://fastapi.tiangolo.com/tutorial/body/)
-   [FastAPI response
    models](https://fastapi.tiangolo.com/tutorial/response-model/)
-   [Pydantic field
    constraints](https://docs.pydantic.dev/latest/concepts/fields/)
-   [Pydantic
    validators](https://docs.pydantic.dev/latest/concepts/validators/)
-   [OpenAI API documentation](https://platform.openai.com/docs)

Validation guarantees depend on the specific API contract and model
capability. Verify provider response status, structured-output behavior,
and SDK fields against current documentation.
