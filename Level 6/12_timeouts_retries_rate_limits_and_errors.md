# Chapter 12: Timeouts, Retries, Rate Limits, and Errors

## Learning objectives

By the end of this chapter, you should be able to:

-   Configure connection and read timeouts, plus an overall deadline
    where supported.
-   Distinguish transient failures from authentication, permission, and
    invalid-request errors.
-   Implement bounded exponential backoff with jitter and respect
    supported retry hints.
-   Inspect SDK retry defaults and prevent retries from multiplying
    across layers.
-   Differentiate request-rate limits, token-throughput limits, and
    application concurrency limits.
-   Reason about duplicate requests, duplicate cost, and documented
    idempotency support.
-   Translate provider failures into safe, useful application errors.
-   Test timeout, throttling, and invalid-credential behavior with
    deterministic simulations.

<br/>

## 1 Why failure handling is part of application design

LLM API calls can fail because of network conditions, provider overload,
rate limits, invalid credentials, malformed requests, timeouts, or
interrupted streams. A production application needs a policy for each
category rather than treating every exception as a reason to retry.

``` mermaid
flowchart TD
    A[LLM API attempt] --> B{Outcome}
    B -->|Success| C[Return result and record telemetry]
    B -->|Transient failure| D{Retry budget remains?}
    D -->|Yes| E[Wait with backoff and jitter]
    E --> A
    D -->|No| F[Return safe temporary-failure error]
    B -->|Authentication or invalid request| G[Do not retry unchanged request]
    G --> H[Return safe client/configuration error]
    B -->|Partial stream| I[Mark incomplete and apply stream-specific recovery]
```

**Principle:** retry only when the failure is plausibly temporary, the
retry budget allows it, and repeating the operation is safe enough for
the application.

<br/>

## 2 Timeouts and deadlines

A timeout limits how long an operation may wait. A deadline limits the
total time budget for an operation, potentially including connection
setup, provider processing, retries, and backoff delays.

### Connection timeout

Limits the time spent establishing a connection. It helps prevent an
application from hanging while a network connection is being negotiated.

<br/>

### Read timeout

Limits how long the client waits for response data during an established
connection. For streaming, SDKs may interpret read timeouts as an
inactivity period between bytes or events; verify the specific client
behavior.

<br/>

### Total request deadline

A total deadline is an application-level budget for the complete
operation. Not every SDK exposes a single deadline option that
automatically includes all retry delays. When it does not, enforce a
deadline at the application layer and pass the remaining budget into
each attempt where possible.

``` mermaid
flowchart LR
    A[Request begins] --> B[Connection timeout]
    B --> C[Provider processing and response]
    C --> D[Read timeout between data]
    D --> E{Retry needed?}
    E -->|Yes, budget remains| F[Backoff delay]
    F --> B
    E -->|No or deadline reached| G[Return or stop]
```

A request can have a per-attempt timeout and still exceed the user's
overall latency budget if retries and backoff are unbounded. Set both
deliberately.

<br/>

### Example: configure a timeout in the OpenAI Python SDK

The exact configuration API may vary by SDK version. In current OpenAI
Python SDK patterns, a client can be initialized with a timeout and a
retry count:

``` python
from openai import OpenAI

client = OpenAI(
    timeout=20.0,
    max_retries=2,
)
```

This is an SDK-level timeout, not necessarily a strict end-to-end
deadline for your entire application workflow. Check the installed SDK
documentation for the precise timeout semantics and default retry
behavior.

For lower-level control, some HTTP clients support separate connect,
read, write, and pool timeouts. Use the options supported by the actual
client in use rather than assuming every SDK exposes all four.

<br/>

## 3 Categorizing failures

The right response depends on the failure category. Provider-specific
status codes and exception classes differ, so build a small adapter for
the SDK and provider used by your application.

| Category                   | Examples                                                 | Typical Policy                                                                |
| -------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Connection/network failure | DNS issue, connection reset                              | Retry within a bounded budget when the operation is safe                      |
| Timeout                    | Connection or response takes too long                    | Consider bounded retry if deadline remains and request repetition is safe     |
| Rate limiting              | Request-per-time or token-throughput limit exceeded      | Respect retry hints such as `Retry-After` when documented; otherwise back off |
| Temporary server failure   | Overload or provider 5xx response                        | Often retryable, subject to SDK behavior and operation safety                 |
| Authentication failure     | Missing, invalid, or expired API key                     | Do not retry unchanged credentials                                            |
| Permission failure         | Key lacks required access                                | Do not retry unchanged permissions                                            |
| Invalid request            | Invalid schema, unsupported parameter, malformed payload | Correct the request; repeating it unchanged is unlikely to help               |
| Quota/billing restriction  | Project has exhausted quota or billing is unavailable    | Usually requires account/configuration action, not immediate retry            |
| Content or policy refusal  | Provider declines the request                            | Do not treat as a transient infrastructure error                              |
| Stream interruption        | Connection closes after partial output                   | Mark the result incomplete; recovery requires special care                    |


Do not rely on status code alone if the provider documents a more
specific error type or retry instruction. For example, a rate-limit
response and a quota-exhaustion response may require different handling
even if both appear related to limits.

<br/>

## 4 Bounded exponential backoff and jitter

Exponential backoff increases the delay between attempts. Jitter adds
randomness so many clients do not retry simultaneously after a shared
outage.

A common capped schedule is:

$$ d_n = \min(d_{\max}, d_0 \times 2^n) + J_n $$

where:

* $d_0$ is the initial delay.
* $d_{\max}$ is the maximum backoff component.
* $J_n$ is a bounded random jitter term.
* $n$ is the retry index, beginning at zero.


This is one possible policy, not a universal standard. Full-jitter
strategies instead sample a delay uniformly between zero and a capped
exponential bound. Choose one policy and document it.

<br/>

### Retry hints

If the provider supplies a documented retry hint such as `Retry-After`,
honor it within your overall deadline and retry budget. Validate the
hint and avoid sleeping longer than the remaining request deadline. If a
hint is absent or invalid, use the application's backoff policy.

<br/>

### Example: a bounded retry loop for a classified operation

The following is a generic teaching example. A production adapter should
classify actual SDK exceptions and HTTP responses. It should not
classify every exception as transient.

``` python
import random
import time


class TransientFailure(Exception):
    pass


class PermanentFailure(Exception):
    pass


def call_with_bounded_retries(
    operation,
    *,
    max_attempts=3,
    base_delay=0.5,
    max_delay=4.0,
    deadline_seconds=10.0,
):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    started = time.monotonic()

    for attempt in range(max_attempts):
        try:
            return operation()
        except PermanentFailure:
            # Authentication, permissions, or invalid requests should
            # normally be corrected rather than retried unchanged.
            raise
        except TransientFailure:
            last_attempt = attempt == max_attempts - 1
            elapsed = time.monotonic() - started
            remaining = deadline_seconds - elapsed

            if last_attempt or remaining <= 0:
                raise

            exponential_cap = min(max_delay, base_delay * (2 ** attempt))
            delay = random.uniform(0, exponential_cap)  # full jitter

            if delay >= remaining:
                raise TimeoutError("Overall retry deadline would be exceeded")

            time.sleep(delay)

    raise RuntimeError("Unreachable")
```

Important details:

-   `max_attempts` includes the initial attempt.
-   A permanent failure exits immediately.
-   Backoff is capped, and the overall deadline is checked before
    sleeping.
-   The example's deadline check is a teaching approximation: a real
    implementation must also constrain the duration of each operation
    itself. If an operation can block beyond the remaining deadline,
    pass a remaining timeout into the client or use an appropriate
    cancellation mechanism.
-   A production implementation should preserve the final failure
    category and record attempt count, delay, and request identifiers.

<br/>

## 5 Inspect SDK retry defaults

SDKs may retry selected network failures, rate-limit responses, or
server errors automatically. If your application also retries, the total
number of attempts can multiply.

Suppose:

-   The SDK makes up to 3 attempts per call.
-   An application wrapper makes up to 4 attempts.

The worst-case provider attempts can be (3 `\times 4`{=tex} = 12),
depending on how each layer defines and implements its retry count.

Before implementing retries:

1.  Read the installed SDK's retry documentation.
2.  Determine whether its setting counts retries or total attempts.
3.  Learn which errors it retries automatically.
4.  Decide which layer owns retry policy.
5.  Set a global attempt/deadline budget and instrument actual attempts.
6.  Test the effective behavior rather than inferring it from
    configuration names.

A good default is to assign one layer clear ownership of retries. If the
SDK already retries, the application layer may focus on an overall
deadline and final error mapping instead of adding another independent
loop.

<br/>

## 6 Request limits, token limits, and concurrency limits

These constraints are related but not interchangeable.


| Limit                         | What It Constrains                                             | Typical Response                                                     |
| ----------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------- |
| Request rate                  | Number of requests within a time window                        | Reduce request frequency; queue or retry after the appropriate delay |
| Token throughput              | Input/output tokens processed within a time window             | Reduce token volume, smooth traffic, or wait for capacity            |
| Application concurrency       | Number of simultaneous in-flight calls your own service allows | Use a semaphore or worker pool; queue excess work                    |
| Daily/monthly quota or budget | Aggregate allowance over a longer period                       | Alert, enforce a budget policy, or request a quota/billing change    |


A semaphore can protect your own service from creating too many
concurrent calls, but it does not by itself guarantee compliance with
provider request-rate or token-throughput limits.

``` python
import asyncio


async def run_with_concurrency_limit(items, async_call, max_concurrency=5):
    semaphore = asyncio.Semaphore(max_concurrency)

    async def bounded(item):
        async with semaphore:
            return await async_call(item)

    return await asyncio.gather(*(bounded(item) for item in items))
```

This limits simultaneous tasks in one process. A multi-worker or
multi-instance deployment may need a distributed limiter or centralized
queue to enforce a shared application-wide cap.

<br/>

## 7 Duplicate requests, cost, and idempotency

A timeout does not always mean the provider failed to process the
request. The provider may have completed generation while the response
was lost before reaching your application.

If the application retries, it may create another generation and incur
additional usage or cost.

Key distinctions:

-   **Transport retry:** the client repeats a request because it did not
    receive a usable response.
-   **Application retry:** business logic starts another attempt after
    classifying the first attempt as failed or incomplete.
-   **Idempotency:** repeating a request with the same documented
    idempotency key has a defined duplicate-handling behavior for an
    operation, if the provider supports it.

Do not assume an idempotency key is supported by every endpoint or that
it guarantees exactly-once execution. Check the provider's current
documentation for supported endpoints, key scope, retention window, and
behavior. If support is absent or unclear, treat the retry as
potentially creating duplicate work and cost.

Practical safeguards:

-   Generate a stable application operation ID.
-   Record each attempt separately under that operation ID.
-   Use provider-supported idempotency only where explicitly documented.
-   Avoid automatically replaying side-effecting tool actions without an
    application-level deduplication strategy.
-   Make the user-facing response clear when the final outcome is
    uncertain.

<br/>

## 8 Partial streams need special handling

A non-streaming request often yields a response object or an exception.
A streaming request may yield several content chunks before the
connection fails. In that case, the application has already exposed part
of the output.

Blindly restarting the request and appending the new output can
duplicate text, contradict the partial answer, or repeat tool
instructions.

Recommended handling:

1.  Track whether any content was already delivered to the client.
2.  Mark the stream as complete only after the documented completion
    event.
3.  If the stream fails before completion, record an incomplete status
    and the available partial output state.
4.  Do not append a restarted generation to the old partial output
    unless the application has an explicit reconciliation strategy.
5.  Decide whether to restart from scratch, return a clearly marked
    partial response, or ask the client to retry.
6.  Inspect documented final usage metadata if available; otherwise
    record usage as partial or unavailable, not zero.
7.  Ensure cancellation stops unnecessary upstream work where the SDK
    and transport support it.

``` mermaid
flowchart TD
    A[Stream emits chunks] --> B{Completion event received?}
    B -->|Yes| C[Mark completed]
    B -->|No, stream fails| D[Mark incomplete]
    D --> E{Was partial content delivered?}
    E -->|No| F[Retry only if safe and budget remains]
    E -->|Yes| G[Apply explicit recovery policy]
    G --> H[Do not blindly append a new generation]
```

<br/>

## 9 Safe application error mapping

Provider exceptions can contain internal details, request payload
fragments, headers, or diagnostic information that should not be shown
directly to end users.

Map internal failure categories to stable application-level errors. Log
only the diagnostic fields needed for troubleshooting, with secrets and
sensitive content removed.

  -------------------------------------------------------------------------------------------------
  Internal category              Example safe application response          Operational action
  ------------------------------ ------------------------------------------ -----------------------
  Authentication/configuration   `LLM provider configuration error`         Alert operator; do not
                                                                            expose credentials or
                                                                            raw provider payload

  Invalid request                `The request could not be processed`       Validate inputs and
                                                                            inspect redacted
                                                                            diagnostics

  Rate limit                     `Service is busy; retry shortly`           Respect provider retry
                                                                            hints and enforce
                                                                            backoff

  Temporary provider failure     `The service is temporarily unavailable`   Retry within the
                                                                            budget, then fail
                                                                            safely

  Deadline exceeded              `The request took too long`                Stop work where
                                                                            possible and record
                                                                            elapsed time

  Incomplete stream              `The response was interrupted`             Do not claim the answer
                                                                            completed

  Unknown failure                `An unexpected service error occurred`     Record a correlation ID
                                                                            and investigate
  -------------------------------------------------------------------------------------------------

Return a correlation ID to the caller so support teams can find the
corresponding internal record. Do not return API keys, authorization
headers, raw stack traces, internal hostnames, or unredacted provider
responses.

A simple mapping pattern:

``` python
def to_public_error(category: str, request_id: str) -> dict:
    public_messages = {
        "authentication": "LLM provider configuration error",
        "invalid_request": "The request could not be processed",
        "rate_limit": "Service is busy; retry shortly",
        "temporary": "The service is temporarily unavailable",
        "timeout": "The request took too long",
        "incomplete_stream": "The response was interrupted",
    }

    return {
        "error": {
            "code": category,
            "message": public_messages.get(
                category,
                "An unexpected service error occurred",
            ),
            "request_id": request_id,
        }
    }
```

Validate `category` against a controlled set in production. The public
`code` should be an application-defined value, not an arbitrary string
copied from a provider exception.

<br/>

## 10 Practice: simulate timeout, throttling, and invalid credentials

The following exercise uses synthetic exception classes. It does not
call a real provider and does not require API credentials.

``` python
class RateLimited(TransientFailure):
    def __init__(self, retry_after=None):
        super().__init__("synthetic rate limit")
        self.retry_after = retry_after


class InvalidCredentials(PermanentFailure):
    pass


def simulate_case(case):
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1

        if case == "timeout":
            if attempts["count"] < 3:
                raise TransientFailure("synthetic timeout")
            return "success after transient failures"

        if case == "throttling":
            if attempts["count"] < 2:
                raise RateLimited(retry_after=0.1)
            return "success after throttling"

        if case == "invalid_credentials":
            raise InvalidCredentials("synthetic invalid key")

        return "success"

    return operation, attempts
```

Use the simulation to verify the policy:

-   For the timeout case, the retry wrapper may retry up to the
    configured attempt limit.
-   For throttling, a production implementation should use `retry_after`
    when the provider documents that hint; the generic wrapper above
    does not yet consume this custom field.
-   For invalid credentials, the permanent exception should escape on
    the first attempt.
-   Assert that the attempt count never exceeds `max_attempts`.
-   Keep delays short in tests by injecting a fake sleep function and
    deterministic jitter source rather than waiting in real time.

Example assertion for the permanent failure:

``` python
operation, attempts = simulate_case("invalid_credentials")

try:
    call_with_bounded_retries(
        operation,
        max_attempts=3,
        deadline_seconds=2,
    )
except InvalidCredentials:
    pass

assert attempts["count"] == 1
```

To make the full test suite deterministic, refactor the retry helper to
accept injectable `sleep`, `clock`, and random-delay functions. Then
test retry count, deadline enforcement, retry-hint handling, and safe
error mapping independently.

<br/>

## 11 Common mistakes

-   Retrying authentication and invalid-request failures unchanged.
-   Treating every provider error as transient.
-   Using unbounded retries or backoff that exceeds the user-facing
    deadline.
-   Ignoring `Retry-After` or other documented retry hints.
-   Adding application retries without inspecting SDK retry defaults.
-   Confusing provider rate limits with local concurrency limits.
-   Assuming a timeout proves that the provider did not process the
    request.
-   Assuming idempotency support without verifying the endpoint's
    contract.
-   Restarting a failed stream and blindly appending its new output.
-   Returning raw provider exceptions or stack traces to end users.

<br/>

## 12 Practice and revision

1.  Classify a synthetic timeout, rate-limit response, invalid
    credential, and malformed request.
2.  Configure a maximum of three total attempts and prove that the retry
    loop never exceeds it.
3.  Add bounded jitter and a deadline; test that the helper does not
    sleep past the remaining budget.
4.  Add support for a documented retry hint such as `Retry-After`,
    validating the value and capping it to the remaining deadline.
5.  Inspect the SDK's installed retry defaults and document which layer
    owns retry policy.
6.  Demonstrate how SDK retries and application retries could multiply
    total provider attempts.
7.  Explain how request-rate limits differ from token-throughput and
    concurrency limits.
8.  Simulate a stream that emits two chunks and then fails; decide what
    the client should see and what status and usage metadata should be
    recorded.
9.  Map internal exceptions to safe public errors with a correlation ID.
10. Explain how duplicate requests can create duplicate usage or side
    effects, and state the conditions under which provider idempotency
    support can be relied upon.

<br/>

### Checkpoint answer

Not every failure should be retried because some failures are permanent
until the request or configuration changes: invalid credentials,
insufficient permissions, malformed requests, and many quota/billing
restrictions. Repeating them unchanged wastes time and may create noise
or additional cost. Transient network, throttling, and selected server
failures may be retryable, but only within a bounded attempt count and
deadline, with appropriate backoff and provider retry hints.

Partial streams need special handling because some output may already
have been delivered and the provider may have processed the request. A
blind retry can duplicate or contradict content and may incur additional
cost. Track completion explicitly, preserve partial-state information,
apply a defined recovery policy, and do not assume missing final usage
metadata means zero consumption.

<br/>

## References

Verify behavior against the exact SDK and endpoint version used in your
application:

-   [OpenAI Python SDK: retries and
    timeouts](https://github.com/openai/openai-python)
-   [OpenAI API error
    codes](https://platform.openai.com/docs/guides/error-codes)
-   [OpenAI API documentation](https://platform.openai.com/docs)
-   [Python `time` module](https://docs.python.org/3/library/time.html)
-   [Python `asyncio` synchronization
    primitives](https://docs.python.org/3/library/asyncio-sync.html)

Retry policies, error types, timeout semantics, rate limits, and
idempotency support are provider- and endpoint-specific. Confirm the
current documentation before deploying a production policy.
