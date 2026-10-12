# Chapter 11: Token Usage and Usage Metadata

## Learning objectives

By the end of this chapter, you should be able to:

-   Inspect provider-reported input, output, cached-input, and
    reasoning-token usage when documented.
-   Distinguish observed provider usage from local tokenizer estimates.
-   Represent missing usage metadata honestly rather than treating it as
    zero.
-   Record latency, model identifiers, completion status, and request
    identifiers.
-   Estimate request cost using verified pricing and explicit accounting
    assumptions.
-   Build a usage summary from complete and incomplete metadata
    fixtures.

<br/>

## 1 Why usage metadata matters

An LLM response is not just text. For operational monitoring and cost
control, an application may also need to record:

-   **Usage:** token counts reported by the provider.
-   **Latency:** how long the request took.
-   **Model identity:** the requested model and, when available, the
    model reported by the provider.
-   **Completion status:** whether the request completed normally, was
    refused, or was incomplete.
-   **Request identity:** provider request ID or application-generated
    correlation ID.
-   **Cost estimate:** a calculation based on observed usage and a
    verified price schedule.

These fields support budget tracking, capacity planning, latency
analysis, debugging, and comparisons between model configurations.

``` mermaid
flowchart TD
    A[LLM request] --> B[Provider response or stream]
    B --> C[Extract available usage metadata]
    C --> D[Record latency, model, status, request IDs]
    D --> E{Usage complete?}
    E -->|Yes| F[Calculate cost from verified prices]
    E -->|No| G[Mark observed usage as partial or unavailable]
    F --> H[Usage record and monitoring]
    G --> H
```

**Core rule:** record what was observed, label what was estimated, and
never disguise missing information as a measured value.

<br/>

## 2 Understanding token-usage fields

Providers do not all expose the same schema or accounting categories.
Use the provider's documentation and SDK types for the exact model and
endpoint.

Common fields include:


| Field                 | Typical Meaning                                                     | Important Qualification                                                                                                              |
| --------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `input_tokens`        | Tokens attributed to the request input                              | May include system instructions, conversation history, tool definitions, and other request content, not only the latest user message |
| `output_tokens`       | Tokens attributed to generated output                               | May include more than visible prose, depending on the API's accounting rules                                                         |
| `cached_input_tokens` | Input tokens served through a provider's cache mechanism            | Availability and pricing treatment vary by provider/model                                                                            |
| `reasoning_tokens`    | Tokens attributed to internal reasoning for models that report them | Not every model or endpoint exposes this field; accounting treatment varies                                                          |
| `total_tokens`        | Provider-reported aggregate usage                                   | Do not assume it equals a locally calculated sum unless the provider defines it that way                                             |


A provider may nest details under a usage object, for example
`input_tokens_details.cached_tokens` or
`output_tokens_details.reasoning_tokens`. These names are examples of
possible schema fields, not a universal cross-provider standard.

<br/>

### Do not assume every category is independently billable

A usage category can be informational, included in another count, priced
separately, or not exposed at all. Before calculating cost, confirm:

1.  The exact provider and API endpoint.
2.  The exact model/version or model identifier.
3.  The applicable price schedule and its effective date.
4.  Whether cached input or reasoning tokens are included in aggregate
    counts.
5.  Whether the price is per token, per thousand tokens, or per million
    tokens.
6.  Whether additional charges apply, such as tools, images, audio, or
    other modalities.

<br/>

## 3 Provider-reported usage versus local estimates

These are different kinds of evidence and should be stored separately.

### Provider-reported usage --- observed

The provider's response or final stream event explicitly reports a
count. Preserve the original fields and identify the source as
provider-reported.

<br/>

### Local tokenizer estimate --- estimated

A tokenizer estimates the number of tokens in text or a request
representation. It can be useful before sending a request, but it may
differ from billed usage because of:

-   Different tokenizers or model-specific encodings.
-   Hidden message formatting and protocol overhead.
-   System/developer instructions, tool schemas, and conversation
    history.
-   Multimodal payloads such as images or audio.
-   Provider-specific caching, reasoning, or accounting rules.
-   Truncation, retries, or other request behavior.

A local estimate should never silently overwrite a provider-reported
count.

| Situation                                       | Recommended Representation                                             |
| ----------------------------------------------- | ---------------------------------------------------------------------- |
| Provider reports input and output usage         | Store as observed usage                                                |
| Local tokenizer counts a prompt before the call | Store as an estimate, with method and timestamp                        |
| Stream has no usage event                       | Mark usage as unavailable unless another documented source provides it |
| Only input usage is present                     | Record input as observed and output as missing                         |
| Request times out before a final response       | Record incomplete request status; usage may be unknown or partial      |
| Usage object exists but a field is absent       | Mark that field as missing, not zero                                   |


<br/>

## 4 A normalized usage record

Provider-specific response objects differ. A small normalized record
makes monitoring easier while preserving the original provider metadata
for later debugging.

The following example uses Python's standard library and Pydantic. It
intentionally represents unknown counts as `None`, not `0`.

``` python
from typing import Literal
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cached_input_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class LLMUsageRecord(BaseModel):
    application_request_id: str
    provider_request_id: str | None = None
    requested_model: str
    reported_model: str | None = None
    status: Literal["completed", "incomplete", "failed", "refused", "unknown"]
    latency_ms: float | None = Field(default=None, ge=0)
    usage_source: Literal["provider", "local_estimate", "partial", "unavailable"]
    usage: TokenUsage
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    cost_status: Literal["calculated", "partial", "unavailable"] = "unavailable"
```

Design notes:

-   `application_request_id` is generated by your application and helps
    correlate logs across services.
-   `provider_request_id` should be captured only when the provider
    exposes it.
-   `requested_model` records what the application asked for;
    `reported_model` records what the response identifies, when
    available.
-   `usage_source` tells downstream systems whether counts are
    provider-reported, estimated, partial, or unavailable.
-   `estimated_cost_usd` is deliberately optional. It should remain
    absent when the data or pricing assumptions are insufficient.

In production, you may add timestamps, endpoint names, deployment
versions, tenant IDs, region, retry count, and a privacy-reviewed trace
identifier.

<br/>

## 5 Extracting usage from a response

Use the response schema documented by the provider SDK version you have
installed. Avoid assuming every response has a usage object.

The following adapter illustrates the defensive pattern for an SDK
response whose `usage` object exposes `input_tokens` and
`output_tokens`. Adapt it to the actual SDK schema.

``` python
def optional_int(value):
    """Return a non-negative integer, or None if the value is unavailable."""
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def extract_basic_usage(response):
    usage = getattr(response, "usage", None)

    if usage is None:
        return {
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "usage_source": "unavailable",
        }

    input_tokens = optional_int(getattr(usage, "input_tokens", None))
    output_tokens = optional_int(getattr(usage, "output_tokens", None))
    total_tokens = optional_int(getattr(usage, "total_tokens", None))

    has_any = any(
        value is not None
        for value in (input_tokens, output_tokens, total_tokens)
    )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "usage_source": "provider" if has_any else "unavailable",
    }
```

This is a deliberately small example. A real provider adapter should
also map documented cached-token and reasoning-token fields, preserve
the raw usage payload, and distinguish a genuinely partial record from a
complete record. Do not infer completeness merely because a usage object
exists.

<br/>

### Preserve provider-specific details

A useful architecture is:

1.  **Provider adapter:** extracts documented fields from the SDK
    response.
2.  **Normalized record:** maps common fields into your application's
    schema.
3.  **Raw metadata storage:** retains a privacy-reviewed copy of
    provider usage metadata.
4.  **Reporting layer:** calculates summaries and costs from normalized
    values.

Avoid logging full prompts or responses just to preserve usage
information. They can contain sensitive user data.

<br/>

## 6 Usage metadata in streaming and incomplete requests

Streaming complicates accounting because the final usage summary may
arrive separately from the text deltas---or may not arrive at all.

A robust stream handler should:

-   Track time to first content and total elapsed time separately.
-   Accumulate content deltas without assuming each event contains
    usage.
-   Inspect documented final events for usage metadata.
-   Mark usage as unavailable or partial if the stream ends without a
    usage summary.
-   Distinguish a completed stream from a cancelled, timed-out,
    disconnected, or incomplete stream.
-   Avoid interpreting a missing final event as zero tokens.
-   Record whether the request was retried; each attempt may have
    different usage and cost implications.

``` mermaid
sequenceDiagram
    participant App as Application
    participant API as Provider API
    App->>API: Start generation
    API-->>App: Content delta
    API-->>App: Content delta
    API-->>App: Final event (usage may be present)
    App->>App: Record status, latency and available usage
    Note over App: If final usage is absent, mark it unavailable or partial
```

A stream can deliver useful text and still fail before a final usage
event. The correct record may therefore contain partial output, an
incomplete status, and unknown usage.

<br/>

## 7 Recording latency, models, status, and request IDs

Use a monotonic clock for elapsed duration, because wall-clock time can
change. Record wall-clock timestamps separately if needed for audit and
correlation.

``` python
from time import perf_counter


def measure_call(call):
    started = perf_counter()
    try:
        response = call()
        elapsed_ms = (perf_counter() - started) * 1000

        return {
            "response": response,
            "latency_ms": round(elapsed_ms, 2),
            "status": "completed",
        }
    except TimeoutError:
        elapsed_ms = (perf_counter() - started) * 1000
        return {
            "response": None,
            "latency_ms": round(elapsed_ms, 2),
            "status": "incomplete",
        }
    except Exception:
        elapsed_ms = (perf_counter() - started) * 1000
        return {
            "response": None,
            "latency_ms": round(elapsed_ms, 2),
            "status": "failed",
        }
```

This example demonstrates measurement only. Production code should use
provider-specific exception handling, preserve the error category, apply
an explicit timeout, and avoid swallowing diagnostic information.

Record at least:

-   An application-generated request/correlation ID.
-   Provider request ID, if returned.
-   Requested model and reported model, if returned.
-   Start time or timestamp, elapsed latency, and completion status.
-   Attempt number and retry information where applicable.
-   Available usage metadata and its source.

Do not place API keys, authorization headers, raw sensitive prompts, or
unredacted personal data in routine logs.

<br/>

## 8 Estimating cost with explicit assumptions

Cost should be calculated only from a verified price schedule for the
model and date in question. Prices change, and provider pricing may
distinguish uncached input, cached input, output, reasoning, modalities,
or tool usage.

For a simple hypothetical model with per-million-token rates:

$$ \text{Cost} = \frac{I \times P_i + O \times P_o}{1{,}000{,}000} $$

where:

* $I$ = billable input tokens under the stated accounting rule.
* $O$ = billable output tokens under the stated accounting rule.
* $P_i$ = input price per million tokens.
* $P_o$ = output price per million tokens.


This formula is valid only when the chosen counts and rates match the
provider's billing definitions. If cached input has a separate rate,
split it into the appropriate categories. Do not double-count cached
tokens if the provider defines them as a subset of input tokens.

<br/>

### Example using illustrative---not real---prices

Assume the provider reports 2,000 input tokens and 500 output tokens.
For illustration only, suppose input costs \$2.00 per million tokens and
output costs \$8.00 per million tokens.

\[ `\text{Cost}`{=tex} =
`\frac{2{,}000 \times 2.00 + 500 \times 8.00}{1{,}000{,}000}`{=tex} =
\$0.008 \]

This is an arithmetic demonstration, **not a current provider quote**.
Real estimates must cite or record the verified price source, model
identifier, effective date, and assumptions.

``` python
def estimate_simple_cost_usd(
    input_tokens: int | None,
    output_tokens: int | None,
    input_price_per_million: float,
    output_price_per_million: float,
):
    """Estimate cost only when both required observed counts are available."""
    if input_tokens is None or output_tokens is None:
        return None

    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts cannot be negative.")

    if input_price_per_million < 0 or output_price_per_million < 0:
        raise ValueError("Prices cannot be negative.")

    return (
        input_tokens * input_price_per_million
        + output_tokens * output_price_per_million
    ) / 1_000_000


cost = estimate_simple_cost_usd(
    input_tokens=2_000,
    output_tokens=500,
    input_price_per_million=2.00,   # illustrative only
    output_price_per_million=8.00,  # illustrative only
)

print(f"${cost:.6f}")  # $0.008000
```

<br/>

### When usage is missing

Do not substitute zero for missing input or output counts. For example:

-   Input observed, output missing: the full request cost is unknown; an
    input-only partial estimate may be possible if clearly labeled.
-   Both counts missing: cost is unavailable from token usage alone.
-   Counts estimated locally: cost is an estimate based on estimated
    counts, not provider-reported usage.
-   Usage present but price schedule unverified: usage can be reported,
    but cost should remain unavailable.

Keep these concepts separate in dashboards and exports:

-   **Observed usage:** provider-reported counts.
-   **Estimated usage:** tokenizer or application-derived estimates.
-   **Calculated cost:** arithmetic applied to identified counts and a
    verified price schedule.
-   **Partial estimate:** cost for known billable categories only, with
    omitted categories disclosed.

<br/>

## 9 Building a usage summary from fixtures

This practice uses synthetic fixtures so that missing-data behavior can
be tested without API credentials.

``` python
fixtures = [
    {
        "request_id": "req-001",
        "model": "example-model",
        "status": "completed",
        "latency_ms": 420,
        "usage": {
            "input_tokens": 1200,
            "output_tokens": 300,
            "cached_input_tokens": 200,
            "reasoning_tokens": 40,
            "total_tokens": 1500,
        },
        "usage_source": "provider",
    },
    {
        "request_id": "req-002",
        "model": "example-model",
        "status": "completed",
        "latency_ms": 610,
        "usage": {
            "input_tokens": 800,
            "output_tokens": None,
            "cached_input_tokens": None,
            "reasoning_tokens": None,
            "total_tokens": None,
        },
        "usage_source": "partial",
    },
    {
        "request_id": "req-003",
        "model": "example-model",
        "status": "incomplete",
        "latency_ms": 3000,
        "usage": None,
        "usage_source": "unavailable",
    },
]


def summarize_usage(fixtures):
    rows = []

    for item in fixtures:
        usage = item["usage"] or {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")

        rows.append({
            "request_id": item["request_id"],
            "model": item["model"],
            "status": item["status"],
            "latency_ms": item["latency_ms"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": usage.get("total_tokens"),
            "usage_source": item["usage_source"],
            "cost_status": (
                "needs_pricing_and_complete_usage"
                if input_tokens is not None and output_tokens is not None
                else "unavailable_or_partial"
            ),
        })

    return rows


for row in summarize_usage(fixtures):
    print(row)
```

Expected interpretation:

| Request   | Observed Metadata                                              | Correct Interpretation                                                                                             |
| --------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `req-001` | Input, output, cached, reasoning, and total counts are present | Provider-reported usage is available; cost still requires the applicable verified price schedule and billing rules |
| `req-002` | Input is present, but output and several categories are absent | Usage is partial; do not treat missing output as zero                                                              |
| `req-003` | No usage object and request is incomplete                      | Usage is unavailable from this fixture; do not claim zero consumption                                              |


The fixture uses synthetic counts. They are not measured provider usage
and should not be used for billing or production cost reporting.

<br/>

## 10 Common mistakes

-   **Treating missing usage as zero:** this understates consumption and
    creates misleading reports.
-   **Confusing a tokenizer estimate with billed usage:** record source
    and method.
-   **Assuming every provider has identical field names:** write
    provider-specific adapters.
-   **Assuming cached and reasoning tokens are additional to total
    tokens:** follow documented accounting definitions to avoid
    double-counting.
-   **Calculating cost from stale or guessed prices:** record a verified
    source and effective date.
-   **Ignoring retries:** each attempt may consume resources and may be
    billable.
-   **Logging sensitive payloads unnecessarily:** preserve useful
    metadata while applying data minimization.
-   **Reporting a single average latency without status breakdowns:**
    compare completed, failed, timed-out, and incomplete requests
    separately.

<br/>

## 11 Practice and revision

Complete the following tasks using the fixtures in Section 9.

1.  Produce a table with request ID, model, status, latency, input
    tokens, output tokens, total tokens, usage source, and cost status.
2.  Count how many requests have complete, partial, and unavailable
    usage.
3.  Explain why `req-002` must not be reported as having zero output
    tokens.
4.  Explain why `req-003` cannot be assigned a token-based cost of \$0.
5.  Add an optional `provider_request_id` field and preserve `None` when
    it is absent.
6.  Add a local tokenizer estimate to a separate field; do not overwrite
    provider-reported usage.
7.  Use a clearly labeled hypothetical price schedule to calculate the
    cost of `req-001`, then state the assumptions.
8.  Describe what the application should record if a stream yields
    content but disconnects before the final usage event.

<br/>

### Checkpoint answer

A strong answer distinguishes three separate layers:

-   **Observed usage:** counts explicitly reported by the provider, with
    missing fields left unknown.
-   **Estimated usage:** counts inferred locally, labeled with the
    tokenizer or estimation method.
-   **Calculated cost:** a calculation using identified usage counts,
    verified prices, and documented billing assumptions.

Missing metadata is not evidence of zero consumption. If the available
counts are incomplete, report cost as unavailable or as a clearly
labeled partial estimate rather than presenting a misleading total.

<br/>

## References

Consult the documentation for the provider and model actually used by
your application:

-   [OpenAI API documentation](https://platform.openai.com/docs)
-   [OpenAI API pricing](https://openai.com/api/pricing/)
-   [OpenAI Python SDK](https://github.com/openai/openai-python)
-   [Pydantic documentation](https://docs.pydantic.dev/)

Provider schemas, usage fields, SDK methods, and prices can change.
Verify them against the current documentation before implementing a
production adapter or cost report.
