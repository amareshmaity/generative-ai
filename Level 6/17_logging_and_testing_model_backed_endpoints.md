# Chapter 17: Logging and Testing Model-Backed Endpoints

## Learning objectives

By the end of this chapter, you should be able to:

-   Log request identifiers, status, latency, retries, and usage without
    exposing secrets or sensitive content.
-   Make raw prompt/response capture optional, controlled, and redacted
    when justified.
-   Use fake clients and fixtures for deterministic endpoint and
    error-path tests.
-   Test streaming completion, cancellation, tool arguments,
    authorization, and retry limits.
-   Separate offline tests from optional live integration checks.
-   Evaluate probabilistic task quality using a fixed dataset rather
    than exact-string endpoint assertions.
-   Explain the difference between backend correctness and model-quality
    evaluation.

<br/>

## 1 Two different questions: does the system work, and is the output good?

A model-backed endpoint has at least two testing concerns.

**Backend correctness** asks whether the application behaves according
to its contract: input validation, authorization, retry limits, error
mapping, streaming lifecycle, request IDs, and resource cleanup.

**Model-quality evaluation** asks whether the generated output is useful
and correct for the intended task: extraction accuracy, groundedness,
classification quality, summary coverage, or another task-specific
measure.

These concerns interact, but they are not interchangeable. A perfectly
implemented endpoint can return a low-quality model answer. A good
answer from one test run does not prove the endpoint is secure or
reliable.

``` mermaid
flowchart TD
    A[Model-backed application] --> B[Backend correctness tests]
    A --> C[Model-quality evaluation]
    B --> D[Contracts, security, failures, lifecycle]
    C --> E[Fixed dataset, task metrics, human review]
    D --> F[Release decision]
    E --> F
```

Use deterministic tests for application behavior and a separate
evaluation process for probabilistic model behavior.

<br/>

## 2 What to log

Structured logs are easier to filter and aggregate than unstructured
text. For each request, consider recording:

-   Application request/correlation ID.
-   Provider request ID, if available.
-   Endpoint or operation name.
-   Requested model and reported model, if available.
-   Completion status: completed, refused, incomplete, failed, or
    cancelled.
-   End-to-end latency and, where useful, time to first streamed
    content.
-   Retry attempt count and retry reason category.
-   Provider-reported token usage, with missing fields left unknown.
-   Usage source: provider-reported, local estimate, partial, or
    unavailable.
-   Safe application error code.
-   Deployment/version information and timestamp.

Avoid treating a missing usage count as zero. Keep provider-reported
usage separate from local tokenizer estimates, and record the source of
any cost calculation.

<br/>

### Example: structured logging

``` python
import logging
import json

logger = logging.getLogger("app.llm")


def log_llm_request(
    *,
    request_id: str,
    operation: str,
    model: str,
    status: str,
    latency_ms: float,
    retry_count: int,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    provider_request_id: str | None = None,
    error_code: str | None = None,
):
    record = {
        "event": "llm_request",
        "request_id": request_id,
        "provider_request_id": provider_request_id,
        "operation": operation,
        "model": model,
        "status": status,
        "latency_ms": latency_ms,
        "retry_count": retry_count,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "error_code": error_code,
    }

    logger.info(json.dumps(record))
```

This example demonstrates the fields, not a complete logging
configuration. In production, prefer your logging platform's structured
JSON support, use consistent field names, and validate values before
logging.

<br/>

### Logging rules

-   Never log API keys, authorization headers, bearer tokens, or secret
    configuration.
-   Avoid logging raw prompts and completions by default.
-   Do not put sensitive user content in exception messages or metric
    labels.
-   Sanitize externally supplied request IDs before including them in
    logs.
-   Restrict access to operational logs and define retention periods.
-   Avoid high-cardinality metric labels such as raw request IDs; use
    them in logs/traces instead.
-   Keep logs useful enough to investigate failures without collecting
    unnecessary user data.

<br/>

## 3 Optional raw prompt and response capture

Raw prompt/response capture can help debug prompt construction,
unexpected model output, and provider differences. It can also collect
personal data, confidential business information, credentials
accidentally included in input, or other sensitive content.

Make capture an explicit policy rather than an automatic side effect of
debugging.

Before enabling it, define:

1.  The purpose and authorization for capture.
2.  Which environments can enable it.
3.  Whether users or administrators must opt in.
4.  Redaction rules for known secrets and sensitive fields.
5.  Storage location, encryption, access controls, and retention period.
6.  Whether captured data can be used for evaluation or training.
7.  How to disable capture quickly and delete records when required.

A simple interface can make the decision explicit:

``` python
def record_debug_payload(
    *,
    enabled: bool,
    request_id: str,
    prompt: str,
    response: str | None,
    redactor,
    secure_sink,
):
    if not enabled:
        return

    safe_prompt = redactor(prompt)
    safe_response = redactor(response) if response is not None else None

    secure_sink.write({
        "request_id": request_id,
        "prompt": safe_prompt,
        "response": safe_response,
    })
```

The `redactor` and `secure_sink` must be implemented and tested for your
data policy. Redaction is not guaranteed to detect every secret or
sensitive value. If raw capture is not necessary, do not collect it.

<br/>

## 4 Use fake clients for deterministic tests

Unit tests should not need live API access. A fake client can return a
known result, raise a specific exception, emit a sequence of stream
chunks, or simulate missing metadata.

``` python
class FakeModelClient:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    async def extract(self, text: str):
        self.calls.append({"operation": "extract", "text": text})

        if self.error is not None:
            raise self.error

        return self.result
```

Inject the fake through the same dependency or interface used by the
real provider adapter. This allows tests to verify endpoint contracts
without depending on network conditions or model variability.

Use fixtures for common cases:

-   Valid structured output.
-   Invalid JSON or schema mismatch.
-   Provider timeout.
-   Rate limit and retry exhaustion.
-   Refusal or incomplete response.
-   Missing usage metadata.
-   Stream completion and stream interruption.
-   Unauthorized caller and cross-user resource access.

Avoid asserting exact model prose in a backend unit test. Assert the
behavior that the endpoint owns: status code, response schema, safe
error mapping, number of calls, retry count, and whether the provider
was called at all.

<br/>

## 5 Test request validation and provider-call boundaries

A good test proves that invalid requests are rejected before any model
call is made.

``` python
def test_invalid_input_does_not_call_model(client, fake_model):
    response = client.post("/llm/extract", json={"text": ""})

    assert response.status_code == 422
    assert fake_model.call_count == 0
```

This example assumes the test fixture exposes `client` and `fake_model`,
and that the endpoint validates empty text. Adapt the route path and
fixture names to your application.

Also test:

-   Oversized input.
-   Unsupported model alias or generation option.
-   Excessive output-token budget.
-   Missing or invalid authentication.
-   Caller lacking the required permission.
-   A user attempting to access another user's record.

For access-control tests, assert that the unauthorized operation does
not reach the model or data layer when the policy requires rejection
before that point.

<br/>

## 6 Test error mapping and bounded retries

Use controlled exceptions to exercise failure paths. The test should
verify not only the final response but also the number of attempts and
the error category.

``` python
class SyntheticRateLimit(Exception):
    pass


class AlwaysRateLimited:
    def __init__(self):
        self.calls = 0

    async def generate(self):
        self.calls += 1
        raise SyntheticRateLimit()


async def test_retry_budget_is_bounded():
    client = AlwaysRateLimited()

    try:
        await generate_with_retry_policy(client, max_attempts=3)
    except SyntheticRateLimit:
        pass
    else:
        raise AssertionError("Expected rate-limit failure")

    assert client.calls == 3
```

`generate_with_retry_policy` represents the retry wrapper implemented in
the application. The example's purpose is the invariant: if the
configured limit is three total attempts, the provider adapter should
not be called more than three times.

A complete retry test suite should also verify:

-   Authentication and invalid-request failures are not retried
    unchanged.
-   Retryable failures stop when the attempt limit or deadline is
    reached.
-   Documented retry hints are handled correctly.
-   Backoff and jitter can be controlled in tests using injected clock,
    sleep, and randomness functions.
-   A retry does not bypass request-level authorization or budget
    enforcement.
-   SDK retries are included in the effective attempt count.

<br/>

## 7 Test streaming completion, cancellation, and interruption

Streaming has a lifecycle: content deltas, a terminal completion event,
or an error/cancellation path. Tests should verify the lifecycle rather
than only checking that some text appeared.

Important cases:

-   Normal stream emits deltas and exactly one terminal completion
    event.
-   Upstream failure emits a documented terminal error event.
-   No deltas appear after a terminal event.
-   Cancellation stops consuming upstream data where supported.
-   Partial output is not mislabeled as a complete answer.
-   Missing final usage metadata remains unavailable or partial, not
    zero.
-   Provider resources are closed when the client disconnects or
    cancels.

A simple fake async generator:

``` python
async def fake_stream():
    yield "Part one "
    yield "part two"


async def collect_stream(stream):
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    return chunks


# In an async test:
# assert await collect_stream(fake_stream()) == ["Part one ", "part two"]
```

For cancellation, use an async generator or fake provider that records
when it is closed, then cancel the consumer task and assert cleanup
occurred. Exact cancellation behavior depends on the ASGI server, SDK,
and transport, so add a small integration test using the actual stack.

<br/>

## 8 Test tool arguments and authorization independently

Model-generated tool calls are untrusted requests for operations. Test
the argument validator and tool handler directly, in addition to testing
the model interaction.

Verify that:

-   Unknown tool names are rejected.
-   Extra or malformed arguments are rejected.
-   Arguments satisfy the declared schema.
-   The authenticated user identity is injected by server code, not
    supplied by the model.
-   Permission and resource-ownership checks run before data access.
-   A tool cannot access another user's records by changing an
    identifier.
-   Tool results are correlated with the correct tool-call ID when the
    provider protocol requires it.
-   Tool failures are converted to safe application errors.

A fake model should be able to return adversarial or invalid arguments
so that these paths are repeatable. Do not depend on a real model to
produce the exact invalid call needed for a security test.

<br/>

## 9 Separate offline tests from live integration checks

### Offline tests

Run frequently in local development and CI. They use fakes, fixtures,
and deterministic inputs. They should cover:

-   Schema and business validation.
-   Service-layer logic.
-   Authorization boundaries.
-   Error mapping and retry limits.
-   Stream lifecycle logic.
-   Usage-metadata handling.
-   Request IDs, logging fields, and cleanup.

<br/>

### Live integration checks

Use a real provider to verify that the adapter still matches the
provider's current API and SDK behavior. These tests may be slower,
require credentials, incur cost, and produce nondeterministic output.

Keep live tests small and explicitly configured. They should verify
integration properties such as:

-   Credentials and endpoint configuration work.
-   The selected model accepts the intended request format.
-   Expected response metadata is available or handled as optional.
-   Streaming events are mapped correctly.
-   Structured-output support behaves as expected for the chosen model.

Do not make every pull request depend on a large suite of costly live
calls unless the project explicitly requires it. Use a separate CI job
or scheduled run, protect credentials, and enforce a budget.

<br/>

## 10 Evaluate model quality with a fixed dataset

Probabilistic model output can vary between runs. Exact-string
assertions are usually brittle for tasks such as summarization,
extraction, and open-ended question answering.

Instead, create a fixed evaluation dataset with representative inputs
and expected criteria. For each test case, record:

-   Input and task version.
-   Expected output fields, reference answer, or evaluation rubric.
-   Model and prompt version.
-   Actual output.
-   Metric or rubric score.
-   Evaluation method and timestamp.

Choose metrics based on the task:

| Task                                  | Possible Quality Checks                                                     |
| ------------------------------------- | --------------------------------------------------------------------------- |
| Classification                        | Accuracy, precision, recall, F1, confusion matrix                           |
| Structured extraction                 | Field-level exact match, precision/recall, schema validity, semantic checks |
| Retrieval-grounded question answering | Evidence coverage, correctness, citation validity, abstention quality       |
| Summarization                         | Coverage, factual consistency, rubric-based human or model grading          |
| Tool selection                        | Correct tool, argument validity, authorization behavior, task completion    |


No single metric captures every dimension of quality. For subjective
tasks, use a defined rubric and calibrate automated or LLM-based graders
against human judgments where feasible. Keep quality evaluation separate
from endpoint contract tests.

``` mermaid
flowchart TD
    A[Versioned evaluation dataset] --> B[Run selected model and prompt]
    B --> C[Collect outputs]
    C --> D[Compute task metrics and rubric scores]
    D --> E[Compare with baseline and acceptance thresholds]
    E --> F{Quality acceptable?}
    F -->|Yes| G[Record evaluation and consider release]
    F -->|No| H[Inspect failures and revise]
    H --> B
```

A fixed dataset supports repeatable comparisons, but it does not
guarantee that the dataset represents every production input. Refresh it
with reviewed failure cases while preserving a stable benchmark subset
for trend comparisons.

<br/>

## 11 Example evaluation fixture

For a small classification task, store expected labels and compare them
with model outputs independently from API endpoint tests.

``` python
evaluation_cases = [
    {"text": "I was charged twice.", "expected": "billing"},
    {"text": "I cannot reset my password.", "expected": "account"},
    {"text": "The application crashes at startup.", "expected": "technical"},
]


def classification_accuracy(cases, predict):
    if not cases:
        raise ValueError("Evaluation dataset must not be empty")

    correct = 0
    results = []

    for case in cases:
        predicted = predict(case["text"])
        passed = predicted == case["expected"]
        correct += int(passed)
        results.append({
            "text": case["text"],
            "expected": case["expected"],
            "predicted": predicted,
            "passed": passed,
        })

    return {
        "accuracy": correct / len(cases),
        "results": results,
    }
```

This is a minimal example. In a real evaluation, call the model through
a controlled runner, record model/prompt versions and errors, and
include more representative and edge-case examples. A tiny dataset
demonstrates the mechanics but is not enough to establish production
quality.

<br/>

## 12 Common mistakes

-   Logging secrets, raw credentials, or sensitive prompts by default.
-   Treating missing token usage as zero.
-   Testing only successful requests.
-   Depending on live provider calls for every unit test.
-   Asserting exact generated prose in backend correctness tests.
-   Forgetting cancellation, stream interruption, or resource cleanup.
-   Testing tool schemas but not authorization and resource ownership.
-   Assuming a configured retry count equals the effective number of
    attempts across all layers.
-   Reporting a single accuracy score without examining failure cases or
    class imbalance.
-   Changing the evaluation dataset without recording its version,
    making comparisons misleading.

<br/>

## 13 Practice and revision

### Part A --- Backend correctness

1.  Add structured logs for request ID, model, status, latency, retry
    count, error code, and available usage.
2.  Verify that logs never include provider keys or authorization
    headers.
3.  Make raw prompt/response capture disabled by default and route it
    through explicit redaction and retention controls if enabled.
4.  Use fake clients to test valid output, invalid output, timeout,
    throttling, and missing usage.
5.  Test unauthorized requests and cross-user resource access.
6.  Test tool argument validation and prove that the tool receives
    server-derived identity.
7.  Verify retry limits, stream terminal events, cancellation cleanup,
    and client lifecycle.
8.  Run the offline suite without provider credentials.

<br/>

### Part B --- Model-quality evaluation

1.  Create a small, versioned dataset with expected labels or a scoring
    rubric.
2.  Run one selected model/prompt configuration on every case.
3.  Record outputs, errors, model version, prompt version, and scores.
4.  Compute a task-appropriate metric and inspect failures individually.
5.  Compare a changed prompt or model against the same dataset.
6.  Run a small live integration check separately to verify provider
    connectivity and response mapping.

<br/>

### Checkpoint answer

**Backend correctness tests** verify deterministic application
properties: validation, authorization, response schemas, safe errors,
retry bounds, logging fields, stream lifecycle, cancellation, and
resource cleanup. They should use fakes and fixtures wherever possible
so failures are reproducible and tests do not require a live model.

**Model-quality measurements** evaluate whether outputs satisfy
task-specific expectations. Because generation is probabilistic, use a
fixed, versioned dataset, suitable metrics or rubrics, and failure
analysis rather than relying on exact-string assertions in endpoint
tests. Live integration checks verify the real provider adapter and
should be separate from routine offline tests.

<br/>

## References

-   [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
-   [pytest documentation](https://docs.pytest.org/)
-   [Python logging
    documentation](https://docs.python.org/3/library/logging.html)
-   [OpenAI Python SDK](https://github.com/openai/openai-python)
-   [OpenAI API documentation](https://platform.openai.com/docs)
-   [Pydantic documentation](https://docs.pydantic.dev/)

Adapt fixtures, error types, stream assertions, and live integration
checks to the actual framework, SDK version, provider contract, and
data-protection requirements used by your application.
