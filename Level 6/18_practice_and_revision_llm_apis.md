# Chapter 18: Practice and Revision

## Learning Objectives

By the end of this chapter, you should be able to:

-   Send a request to an LLM provider and inspect the returned response
    and usage metadata.
-   Implement structured output, streaming, and one controlled tool
    call.
-   Apply request deadlines, bounded retries, authentication,
    input/output validation, and safe logging.
-   Exercise batch processing using a supported provider API or
    reproducible fixtures.
-   Compare provider capabilities and measure application behavior.
-   Demonstrate useful output and predictable failure handling in a
    small service project.

> **Scope:** This chapter integrates the patterns from Level 6. It is a
> practical capstone, not a replacement for the detailed explanations in
> the preceding chapters. Provider SDKs and APIs evolve, so verify
> current method names, model identifiers, structured-output support,
> streaming events, batch limits, and retry behavior against the
> provider documentation for the version you install.

<br/>

## 1. Capstone: Build a Reliable LLM Service

Build a small **Support Ticket Assistant**. It accepts a support ticket,
returns a validated classification and summary, can stream a user-facing
summary, and can optionally call one explicitly allowlisted read-only
tool.

<br/>

### Requirements

| Area              | Required Behavior                                                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Provider request  | Make a real provider request in an explicitly enabled integration test; inspect the response and available usage metadata.         |
| Structured output | Return a validated category, priority, summary, and evidence list.                                                                 |
| Streaming         | Stream summary text as it arrives, or use a documented fixture to test event handling without a live API.                          |
| Tool calling      | Support one read-only tool, such as looking up an approved help article. Validate its arguments and authorize it before execution. |
| Reliability       | Set timeouts/deadlines and use bounded retries only for appropriate transient failures.                                            |
| Security          | Authenticate callers, validate input, keep provider keys server-side, and redact sensitive values from logs.                       |
| Batch             | Use a provider's documented batch API where available, or test the batch workflow with deterministic fixtures.                     |
| Observability     | Record request ID, outcome, latency, retry count, and usage metadata when supplied.                                                |
| Testing           | Test success paths and predictable failure paths without depending on a live provider.                                             |


<br/>

### Suggested architecture

``` mermaid
flowchart TD
    C[Client] --> A[FastAPI endpoint]
    A --> AU[Authentication and authorization]
    AU --> V[Request validation]
    V --> S[Application service]
    S --> P[Provider adapter]
    P --> M[LLM API]
    M --> P
    P --> O[Response validation]
    O --> L[Redacted structured logs]
    O --> R[Validated API response]
    S --> T[Allowlisted read-only tool]
    S --> B[Batch adapter or fixture]
```

Keep responsibilities separate. The API endpoint handles HTTP concerns,
the service coordinates the workflow, the provider adapter isolates
SDK-specific behavior, and validators enforce the application's
contract.


<br/>


## 2. Prepare a Reproducible Environment

Create a virtual environment and install only the dependencies needed by
your implementation.

``` bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install openai fastapi uvicorn pydantic httpx pytest
```

Pin tested dependency versions in your project's dependency file after
confirming compatibility. Do not assume that examples written for one
SDK version will work unchanged with another.

Store secrets in environment variables or a secret manager. For example,
a local `.env` file may be used during development if it is excluded
from version control; load it with an explicitly installed configuration
library if desired.

``` bash
# macOS/Linux
export OPENAI_API_KEY="your-key"

# Windows PowerShell
$env:OPENAI_API_KEY = "your-key"
```

Never place a real key in source code, notebooks committed to Git, test
fixtures, logs, or screenshots.


<br/>


## 3. Make and Inspect a Provider Request

A small direct request helps verify credentials, model access, SDK
setup, and response handling. The following example uses the OpenAI
Python SDK's Responses API; confirm the currently supported model name
and API details in the official documentation before running it.

``` python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    timeout=20.0,
    max_retries=0,  # Keep retries explicit in this teaching example.
)

response = client.responses.create(
    model=os.environ["OPENAI_MODEL"],
    input="Classify this ticket in one sentence: I cannot reset my password.",
)

print("Response ID:", response.id)
print("Output text:", response.output_text)
print("Usage:", response.usage)
```

### Inspect the result deliberately

Check these items rather than printing the entire raw response
indiscriminately:

-   **Request/response identifier:** useful for correlating application
    logs with provider-side diagnostics.
-   **Output text:** confirm that the returned content is present and
    useful.
-   **Usage metadata:** inspect input and output token counts if the
    provider returns them.
-   **Finish/status information:** inspect available fields when
    diagnosing incomplete or refused output.
-   **Errors:** distinguish invalid credentials, unsupported model
    identifiers, rate limits, timeouts, and server-side failures.

Usage fields and response shapes differ across providers. A missing
usage value is **unknown**, not zero. Avoid logging raw prompts or
responses if they can contain personal, confidential, or
security-sensitive information.


<br/>


## 4. Implement Structured Output

A structured result gives downstream code a predictable contract. Use a
schema supported by the chosen provider API when possible, then validate
the result locally as well.

``` python
from typing import Literal
from pydantic import BaseModel, Field

class TicketResult(BaseModel):
    category: Literal["account", "billing", "technical", "other"]
    priority: Literal["low", "normal", "high", "urgent"]
    summary: str = Field(min_length=1, max_length=500)
    evidence: list[str] = Field(max_length=5)
```

An example using the OpenAI SDK's parsing helper:

``` python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.parse(
    model="YOUR_SUPPORTED_MODEL",
    messages=[
        {
            "role": "system",
            "content": (
                "Classify support tickets conservatively. "
                "Use only the allowed categories and priorities. "
                "Do not invent evidence."
            ),
        },
        {
            "role": "user",
            "content": "I was charged twice for my monthly subscription.",
        },
    ],
    response_format=TicketResult,
)

result = completion.choices[0].message.parsed
if result is None:
    raise ValueError("The provider did not return a parsed result")

print(result.model_dump())
```

This is an SDK-specific example; verify that the installed SDK and
selected model support this parsing method. If not, use the provider's
documented structured-output mechanism and validate the decoded data
with `TicketResult.model_validate(...)`.

**Important distinction:** schema validity does not guarantee factual
correctness. Check business rules too---for example, whether a claimed
policy or help article actually exists in an approved source.


<br/>


## 5. Stream a Summary

Streaming can improve perceived responsiveness, but it changes the
response contract: clients receive a sequence of events rather than one
complete JSON object.

A simplified SDK-level streaming example:

``` python
from openai import OpenAI

client = OpenAI(timeout=20.0, max_retries=0)

with client.responses.stream(
    model="YOUR_SUPPORTED_MODEL",
    input="Summarize this ticket in two sentences: I cannot sign in after changing phones.",
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

    final_response = stream.get_final_response()

print("\nUsage:", final_response.usage)
```

Confirm the exact streaming interface and event names for the installed
SDK version. If the provider does not expose usage in the final streamed
response, represent usage as unavailable rather than fabricating a
value.

### Streaming checklist

-   Handle completion, failure, and cancellation events.
-   Apply an overall deadline, not just an unbounded wait for the next
    event.
-   Avoid sending internal reasoning, tool arguments, or unvalidated
    structured fields to the client.
-   Define how partial output is represented when a stream fails.
-   Do not retry transparently after text has already been sent unless
    the API contract explicitly supports safe resumption; a retry can
    duplicate content.

For a FastAPI endpoint, choose and document an event contract such as
`event: delta`, `event: completed`, and `event: error`. Do not mix a
partial text stream with a promise that the same HTTP response will also
become a single JSON object.


<br/>


## 6. Execute One Controlled Tool Call

A tool call is a request from the model to your application; it is not
permission to execute arbitrary operations. The application must
validate the name and arguments, apply authorization, execute only
approved behavior, and return a bounded result.

The following example demonstrates the control boundary without relying
on a live model-generated tool call.

``` python
from pydantic import BaseModel, Field

class HelpArticleArgs(BaseModel):
    topic: str = Field(min_length=1, max_length=80)

APPROVED_ARTICLES = {
    "password reset": "Open Account Settings, select Security, then choose Reset Password.",
    "billing receipt": "Open Billing, select the invoice, and choose Download Receipt.",
}

def lookup_help_article(raw_args: dict) -> dict:
    args = HelpArticleArgs.model_validate(raw_args)
    topic = args.topic.strip().casefold()

    # Allowlist: do not use arbitrary model text as a URL, SQL, shell command,
    # file path, or unrestricted search instruction.
    article = APPROVED_ARTICLES.get(topic)
    if article is None:
        return {"found": False, "article": None}

    return {"found": True, "article": article}
```

### Tool-call workflow

1.  Receive a proposed tool name and arguments from the provider.
2.  Confirm the tool name is on a server-side allowlist.
3.  Validate arguments against a strict schema.
4.  Authorize the current user for the requested operation and resource.
5.  Execute the minimal permitted operation.
6.  Bound the returned data and remove sensitive fields.
7.  Return the result using the provider's documented tool-result format
    and the matching tool-call ID.
8.  Validate the final user-facing response.

Never let model-generated arguments bypass authorization. For this
capstone, keep the tool read-only and do not build a general-purpose
shell, SQL, filesystem, or arbitrary-URL tool.


<br/>


## 7. Add Deadlines and Bounded Retries

A reliable service has a finite amount of time and a finite retry budget
for each request. Retry only errors likely to be transient, such as
selected rate-limit or server failures, and respect a provider-supplied
retry hint when available.

``` python
import random
import time

def retry_delay(attempt: int, base: float = 0.5, cap: float = 4.0) -> float:
    # Full jitter helps avoid synchronized retry bursts.
    upper = min(cap, base * (2 ** attempt))
    return random.uniform(0, upper)

def run_with_bounded_retries(operation, is_retryable, max_attempts=3):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as exc:
            final_attempt = attempt == max_attempts - 1
            if final_attempt or not is_retryable(exc):
                raise
            time.sleep(retry_delay(attempt))
```

This is a **teaching pattern**, not a complete production retry policy.
Production code should classify concrete SDK exceptions, use a monotonic
overall deadline, honor `Retry-After` when appropriate, cap total
elapsed time, and avoid retrying permanent failures such as invalid
requests or credentials.

Also check the SDK's built-in retry behavior. If the SDK already
retries, adding another retry layer can multiply attempts unexpectedly.
Do not blindly retry non-idempotent tool actions or requests after a
partial stream has been delivered.

<br/>

### Failure-handling matrix

| Failure                           | Typical Handling                                                                                    |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| Invalid request or schema         | Return a safe client error; do not retry unchanged input.                                           |
| Authentication failure            | Reject or report a configuration issue; do not retry repeatedly.                                    |
| Rate limit                        | Respect retry guidance; retry only within the request deadline and budget.                          |
| Provider server error             | Bounded retry may be appropriate.                                                                   |
| Timeout                           | Stop at the deadline; retry only if the operation is safe and budget remains.                       |
| Invalid model output              | Validate, optionally perform one explicitly bounded repair attempt, or return a controlled failure. |
| Tool authorization denied         | Do not execute; return a safe denial.                                                               |
| Stream fails after partial output | Signal an incomplete result; avoid silently replaying duplicate text.                               |


Do not return stack traces, API keys, provider internals, or raw
exception details to public clients.


<br/>


## 8. Add Authentication, Validation, and Safe Logging

At the HTTP boundary, authenticate the caller and validate the request
before invoking the model. Keep provider credentials separate from
client credentials.

``` python
from pydantic import BaseModel, Field

class TicketRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=5000)
    stream: bool = False
```

A production API should use an established identity provider or a
well-maintained authentication library. A static bearer token may be
useful for a local exercise, but it is not a complete production
identity system. Enforce authorization for each protected action, and
apply per-user quotas or rate limits where needed.

<br/>

### Safe structured log example

``` python
import logging
import time
import uuid

logger = logging.getLogger("support_service")

def log_request_outcome(
    *,
    request_id: str,
    outcome: str,
    elapsed_ms: int,
    retry_count: int,
    input_tokens: int | None,
    output_tokens: int | None,
) -> None:
    logger.info(
        "llm_request_finished",
        extra={
            "request_id": request_id,
            "outcome": outcome,
            "elapsed_ms": elapsed_ms,
            "retry_count": retry_count,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    )
```

Generate a request ID at the application boundary and propagate it
through the service and provider adapter. In production, configure a
formatter that emits the fields as structured JSON. Avoid logging raw
tickets, access tokens, API keys, full prompts, full model outputs, or
unredacted tool arguments by default.

Use `None` for unavailable token counts. Record provider request IDs,
status codes, and model identifiers only when available and appropriate
under your privacy policy.


<br/>


## 9. Exercise Batch Processing

Batch APIs are useful for offline workloads such as classifying a
backlog of tickets, evaluating prompt variants, or generating
embeddings. They are not necessarily suitable for interactive,
low-latency requests.

Provider batch features vary in input format, limits, processing time,
supported models, output ordering, and error reporting. Use the chosen
provider's current documentation for the actual batch API.

When a live batch API is unavailable or too expensive for a repeatable
exercise, test the application workflow with deterministic fixtures:

``` python
tickets = [
    {"id": "T-001", "text": "I forgot my password."},
    {"id": "T-002", "text": "My invoice appears twice."},
    {"id": "T-003", "text": "The application crashes at startup."},
]

# Deterministic fixture stands in for provider output in unit tests.
fixture_results = {
    "T-001": {"category": "account", "priority": "normal"},
    "T-002": {"category": "billing", "priority": "high"},
    "T-003": {"category": "technical", "priority": "high"},
}

results = []
for ticket in tickets:
    result = fixture_results[ticket["id"]]
    results.append({"id": ticket["id"], **result})

assert len(results) == len(tickets)
assert {item["id"] for item in results} == {item["id"] for item in tickets}
print(results)
```

A robust batch workflow should track each input ID, distinguish
submitted/running/completed/failed items, validate each result
independently, support safe resumption, and report partial failure. Do
not assume that output order always matches input order; correlate
records using stable IDs or provider-supported custom identifiers.


<br/>


## 10. Compare Provider Capabilities and Measure Behavior

Create a capability matrix before selecting or switching providers. Mark
capabilities as **supported**, **unsupported**, or **not yet verified**;
do not infer support from a provider's marketing description alone.

| Capability           | Provider A | Provider B | Evidence to Collect                        |
| -------------------- | ---------- | ---------- | ------------------------------------------ |
| Structured output    | Verify     | Verify     | Schema support and invalid-output behavior |
| Streaming            | Verify     | Verify     | Event format, completion, cancellation     |
| Tool calling         | Verify     | Verify     | Tool schema and result round trip          |
| Batch processing     | Verify     | Verify     | Limits, latency, partial failures          |
| Usage metadata       | Verify     | Verify     | Which token/cost fields are returned       |
| Timeouts and retries | Verify     | Verify     | SDK defaults and error classes             |
| Model availability   | Verify     | Verify     | Supported model IDs and lifecycle          |
| Data handling        | Verify     | Verify     | Retention, privacy, regional requirements  |


<br/>

### Minimal measurement plan

Run the same fixed set of representative tickets through each candidate
configuration. Record:

-   **Task quality:** category accuracy, priority accuracy, and
    human-reviewed summary quality.
-   **Schema compliance:** percentage of responses accepted by the local
    validator.
-   **Latency:** median and p95 end-to-end latency, measured across
    enough repeated requests to be meaningful.
-   **Reliability:** success rate, timeout rate, retry rate, and
    partial-stream failure rate.
-   **Cost:** calculate only from observed usage and verified current
    prices; report missing usage separately.
-   **Operational behavior:** cancellation handling, rate-limit
    behavior, and failure clarity.

Keep model version, prompt version, decoding configuration, test data,
and application code fixed during comparisons. Otherwise, the results
may not be attributable to the provider change.

<br/>

## 11. Build a Reproducible Test Suite

Use fakes and fixtures for ordinary unit tests. Reserve live provider
calls for opt-in integration tests because they can be slower, costly,
rate-limited, and nondeterministic.

Suggested test cases:

``` python
def test_ticket_input_rejects_too_short_text():
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        TicketRequest(ticket="bad")


def test_help_tool_rejects_unexpected_argument():
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        HelpArticleArgs.model_validate({
            "topic": "password reset",
            "command": "run something",
        })


def test_help_tool_returns_only_approved_article():
    result = lookup_help_article({"topic": "password reset"})
    assert result["found"] is True
    assert "Reset Password" in result["article"]


def test_unknown_help_topic_is_not_executed():
    result = lookup_help_article({"topic": "arbitrary external URL"})
    assert result == {"found": False, "article": None}
```

The tests above assume the request and tool schemas/functions from
earlier sections are in the same module. Add tests for authentication,
authorization, retryable versus permanent errors, deadlines, missing
usage metadata, malformed structured output, provider failure, stream
cancellation, duplicate batch submissions, and redaction.

A live integration test should be explicitly enabled---for example, by
an environment variable---and should never be required for the default
unit-test suite.


<br/>


## 12. Suggested Project Structure

``` text
support-ticket-assistant/
├── app/
│   ├── main.py                 # FastAPI routes and app lifecycle
│   ├── schemas.py              # Request and response models
│   ├── service.py              # Application workflow
│   ├── auth.py                 # Authentication/authorization
│   ├── tools.py                # Allowlisted tool functions
│   ├── logging_config.py       # Redaction and structured logging
│   └── providers/
│       ├── base.py             # Provider interface
│       └── openai_adapter.py   # SDK-specific implementation
├── tests/
│   ├── test_schemas.py
│   ├── test_tools.py
│   ├── test_service.py
│   ├── test_api.py
│   ├── fixtures/
│   └── test_live_provider.py   # Opt-in integration tests
├── .env.example                # Names only; no real secrets
├── .gitignore
├── pyproject.toml
└── README.md
```

Keep provider-specific response parsing inside the adapter. The service
should consume a small normalized result type so it can be tested with a
fake provider.


<br/>


## 13. Definition of Done

The capstone is complete when all applicable criteria below are
satisfied.

-   [ ] A documented provider request succeeds when valid credentials
    and a supported model are configured.
-   [ ] The application inspects output, status, identifiers, and usage
    metadata without assuming every field exists.
-   [ ] Structured output is validated by a schema and relevant business
    rules.
-   [ ] Streaming has a documented event contract and a defined
    partial-failure behavior.
-   [ ] The controlled tool validates arguments, checks authorization,
    and executes only allowlisted read-only behavior.
-   [ ] Deadlines and bounded retries prevent unbounded work.
-   [ ] Invalid input and unauthorized actions fail safely.
-   [ ] Logs include useful operational fields without exposing secrets
    or sensitive content.
-   [ ] Batch processing is tested against a documented API or
    deterministic fixture, including partial failures.
-   [ ] Provider capabilities are recorded as verified, unsupported, or
    unknown.
-   [ ] Unit tests run without live API credentials; live tests are
    separately opt-in.
-   [ ] The README documents setup, environment variables, tests,
    limitations, and how to run the service.


<br/>


## 14. Practice and Revision Checklist

1.  Make a provider request and inspect the returned output, response
    ID, status, and available usage fields.
2.  Implement structured output and test both valid and invalid results.
3.  Stream a summary and simulate a failure after partial output.
4.  Execute one controlled read-only tool call; reject an unknown tool
    name or invalid arguments.
5.  Test bounded retries with a transient error followed by success, and
    a permanent error that must not be retried.
6.  Add authentication, input limits, authorization checks, and redacted
    structured logs.
7.  Run a batch fixture with one failed item and confirm that successful
    results remain identifiable.
8.  Compare two model/provider configurations using fixed examples and
    record quality, latency, reliability, and cost where measurable.
9.  Run the unit suite without credentials, then run opt-in integration
    tests with valid credentials.
10. Document failure modes and the decisions made to keep behavior
    predictable.

<br/>

### Checkpoint

**Demonstrate useful output and predictable failure handling using
reproducible examples.**

A strong demonstration should include:

-   one successful provider request or a deterministic provider fixture;
-   one schema-valid structured result and one rejected invalid result;
-   one successful stream and one simulated stream failure;
-   one approved tool call and one denied or invalid tool call;
-   tests proving that transient errors are retried within a bounded
    budget while permanent errors are not;
-   a batch report that identifies successful and failed items;
-   logs showing request ID, outcome, latency, retry count, and
    available usage without sensitive payloads;
-   a short provider comparison based on a fixed evaluation set.

<br/>

**Self-assessment questions**

1.  Why should schema validation be followed by business-rule
    validation?
2.  Why is a missing token-usage field different from a value of zero?
3.  Why can retrying after a partial stream duplicate user-visible
    content?
4.  What prevents model-generated tool arguments from becoming
    unauthorized application actions?
5.  Which measurements are needed to compare providers fairly?
6.  Which tests must pass without network access or API credentials?

You are ready to move on when you can explain the design choices,
reproduce the tests, and show how the service behaves under both success
and failure conditions.
