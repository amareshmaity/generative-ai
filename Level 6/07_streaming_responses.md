# 07. Streaming Responses

## Learning objectives

By the end of this chapter, you should be able to:

-   Distinguish provider stream events from your application's transport
    format.
-   Accumulate text or structured deltas and detect stream completion.
-   Introduce Server-Sent Events (SSE) or another documented streaming
    contract.
-   Handle disconnects, cancellation, partial failures, and backpressure
    conceptually.
-   Explain why completed structured output must be validated before
    consequential use.
-   Measure time to first content and total completion time.

> **Scope:** The provider example uses the OpenAI Python SDK's streaming
> Responses API. The application example uses FastAPI and SSE. Provider
> event names, payloads, and transport details are version-dependent;
> verify them against the SDK and framework versions pinned by your
> project.

<br/>

## 1. What streaming changes

In a non-streaming request, the application usually waits for the
complete response before receiving the result. In a streaming request,
the provider emits a sequence of events as generation progresses. The
application can process those events incrementally.

Streaming can improve perceived responsiveness because the user may see
early content before generation finishes. It does not necessarily reduce
the time required to generate the complete answer.

``` mermaid
flowchart TD
    A[Application sends request] --> B[Provider begins generation]
    B --> C[Provider emits stream events]
    C --> D[Application consumes events]
    D --> E[Map provider events to app events]
    E --> F[Transport sends events to client]
    C -->|Completion event| G[Mark generation complete]
    G --> H[Validate final result if required]
```

<br/>

### Non-streaming versus streaming

| Aspect                 | Non-streaming                                      | Streaming                                                                              |
| ---------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------- |
| First visible content  | Usually after the response completes               | Can arrive while generation continues                                                  |
| Application complexity | Lower                                              | Higher: events, cancellation, partial results, and completion state                    |
| Failure behavior       | Often handled before returning the result          | A failure can happen after some content has already been delivered                     |
| Validation             | Validate the completed result before returning it  | Partial content is provisional; validate the completed result before consequential use |
| Best fit               | Simple API calls and structured backend operations | Interactive user interfaces and long responses where early content is useful           |



<br/>


## 2. Provider events are not the application's transport protocol

A provider stream is an SDK/API-level event sequence. Your application
transport is the protocol used between your backend and its client. They
are separate layers.

For example:

-   **Provider layer:** events such as text deltas, output-item events,
    and response-completion events.
-   **Application layer:** a small set of events your frontend
    understands, such as `delta`, `completed`, and `error`.
-   **Transport layer:** SSE, WebSocket, or another documented
    mechanism.

Do not blindly forward every provider event to the browser. Provider
event schemas may change, may expose metadata the client does not need,
and may include details that should remain server-side. Instead,
translate provider events into an application-owned contract.

A simple SSE contract might use:

``` text
event: delta
data: {"text":"Streaming "}

event: delta
data: {"text":"makes output incremental."}

event: completed
data: {"request_id":"app_req_123"}
```

These are application-defined events, not a claim that the provider
emits this exact format.

<br/>

### Example contract

| Application Event | Meaning                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `delta`           | A piece of displayable text is available. It is provisional.                               |
| `completed`       | The provider stream completed and the application finished its required checks.            |
| `error`           | The application could not complete the operation. Some content may already have been sent. |


If structured output or tool calls are involved, define separate typed
events rather than forcing all content into a text `delta`.


<br/>


## 3. Consume provider text deltas

With the OpenAI Responses API, the SDK supports streaming events. A
common pattern is to process text-delta events as they arrive and
observe the terminal event or stream completion.

``` python
from openai import OpenAI

client = OpenAI()

with client.responses.stream(
    model="YOUR_SUPPORTED_MODEL",
    input="Explain streaming responses in three short sentences.",
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

    final_response = stream.get_final_response()

print()
print("Final status:", final_response.status)
```

Use the streaming API documented for your installed SDK version. Some
SDK versions also support `responses.create(..., stream=True)`; do not
mix examples from different SDK versions without checking their current
interface.

The event loop above prints text deltas for a command-line
demonstration. A production application should also:

-   Record whether the stream completed normally.
-   Handle exceptions and cancellation.
-   Capture a provider response ID when available.
-   Distinguish text events from other event types.
-   Avoid treating the text already printed as a validated final result.

<br/>

### Text deltas are fragments

A delta is not guaranteed to be a word, sentence, or complete JSON
value. It may contain a few characters or a partial token rendering.
Concatenate deltas in order when reconstructing text:

``` python
parts: list[str] = []

# Inside the stream loop:
if event.type == "response.output_text.delta":
    parts.append(event.delta)

# After normal completion:
complete_text = "".join(parts)
```

Do not independently parse each text delta as though it were a complete
document.


<br/>


## 4. Detect completion and partial failure

Receiving one or more deltas does not mean the stream completed. The
stream can end normally, report an incomplete or failed response, or
raise an exception after some content has been delivered.

Use explicit state:

``` python
received_any_text = False
completed_normally = False
parts: list[str] = []

try:
    with client.responses.stream(
        model="YOUR_SUPPORTED_MODEL",
        input="Describe a validation pipeline.",
    ) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                received_any_text = True
                parts.append(event.delta)
            elif event.type == "response.completed":
                completed_normally = True

        final_response = stream.get_final_response()
        completed_normally = final_response.status == "completed"

except Exception:
    # Record a sanitized failure; do not expose credentials or internals.
    raise

if not completed_normally:
    raise RuntimeError("The response stream did not complete successfully.")

complete_text = "".join(parts)
if not complete_text.strip():
    raise RuntimeError("The completed stream contained no usable text.")
```

The exact terminal event and stream-helper behavior depend on SDK
version. Follow the documented event protocol and test it against the
version you deploy.

**Important:** if an exception occurs after partial content has been
sent to the client, the application generally cannot retract that
content. Send an explicit error event if the transport remains
available, and make the client UI mark the answer as interrupted rather
than completed.


<br/>


## 5. Structured output requires final validation

Text streaming is useful for display, but structured output---such as
JSON used for a database write, a financial action, or a workflow
decision---needs stronger guarantees.

A stream may expose an incomplete object such as:

``` json
{"customer_id":"C-104","approved":
```

That fragment is not valid JSON and must not be acted upon. Even
syntactically valid JSON may fail schema validation or business rules.

A safe high-level sequence is:

1.  Accumulate the relevant deltas.
2.  Confirm that the provider reports successful completion.
3.  Parse the complete payload.
4.  Validate it against a schema.
5.  Apply independent business rules and authorization checks.
6.  Only then use the result for a consequential operation.

``` python
import json
from pydantic import BaseModel, Field

class ReviewResult(BaseModel):
    category: str
    confidence: float = Field(ge=0.0, le=1.0)

def validate_completed_json(text: str) -> ReviewResult:
    payload = json.loads(text)
    return ReviewResult.model_validate(payload)
```

This example validates a completed string; it does not show
provider-side constrained output configuration. Schema validation is not
a substitute for authorization, policy checks, or domain-specific
business rules.

If the UI displays structured content while it is streaming, label it as
provisional and prevent consequential actions until final validation
succeeds.


<br/>


## 6. Expose a documented SSE endpoint

Server-Sent Events (SSE) provide a simple server-to-client stream over
HTTP. The server sends UTF-8 text frames separated by blank lines. SSE
is typically one-way---from server to client---so the client uses a
separate request to initiate work and receives the stream as the
response.

A typical frame is:

``` text
event: delta
data: {"text":"Hello"}
```

The blank line ends the event. A `data:` field can contain JSON text.
The event names and JSON schema should be defined by your application.

<br/>

### FastAPI SSE example

The following example uses a fake async source to focus on transport
framing. It does not call a model provider.

``` python
import asyncio
import json
from collections.abc import AsyncIterator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def fake_text_events() -> AsyncIterator[str]:
    for fragment in ["Streaming ", "sends ", "incremental ", "content."]:
        await asyncio.sleep(0.2)
        yield fragment

def sse_frame(event: str, data: dict) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )

@app.get("/stream")
async def stream():
    async def generate():
        try:
            async for fragment in fake_text_events():
                yield sse_frame("delta", {"text": fragment})
            yield sse_frame("completed", {"request_id": "example-request"})
        except asyncio.CancelledError:
            # Run any required cleanup, then propagate cancellation.
            raise
        except Exception:
            yield sse_frame("error", {"message": "Generation interrupted"})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
```

Production considerations:

-   Use authentication and authorization appropriate for the endpoint.
-   Ensure reverse proxies and hosting infrastructure do not buffer the
    stream unexpectedly.
-   Set request and generation deadlines.
-   Send sanitized errors; do not expose stack traces or provider
    secrets.
-   Consider heartbeat comments if supported and useful for long-lived
    streams.
-   Define how the client distinguishes normal completion from a broken
    connection.
-   Use a documented transport alternative, such as WebSockets, only
    when its bidirectional behavior is needed.

The `X-Accel-Buffering` header is relevant to some proxy configurations;
it is not a universal guarantee that all infrastructure will stream
immediately.


<br/>


## 7. Disconnects, cancellation, and backpressure

Streaming connects several components: the provider, backend, network,
and client UI. Any part may become slower or disconnect.

### Disconnect and cancellation

If the client disconnects, continuing to generate an answer may waste
resources. Where supported, the server should detect cancellation, stop
consuming upstream events, close the provider stream, and release
resources. Actual cancellation propagation depends on the web framework,
ASGI server, HTTP client, provider API, and proxy setup, so test it in
the deployed environment.

Do not promise that cancelling the local coroutine always cancels remote
inference. The provider may already have processed some or all of the
request.

<br/>

### Backpressure

Backpressure occurs when a downstream consumer cannot process data as
quickly as it arrives. For example, the provider may emit text faster
than a slow client can receive it.

Conceptual safeguards include:

-   Avoid unbounded in-memory queues.
-   Use bounded buffers and define what happens when they fill.
-   Apply timeouts to slow consumers.
-   Cancel work when continuing no longer provides value.
-   Avoid creating one task per delta without limits.
-   Measure queue depth and time spent waiting to send.

``` mermaid
flowchart LR
    A[Provider stream] --> B[Backend event mapper]
    B --> C[Bounded buffer]
    C --> D[HTTP SSE transport]
    D --> E[Client UI]
    E -->|Consumes slowly| C
    C -->|Buffer full| F[Wait, drop only if contract allows, or cancel]
```

For text generation, silently dropping arbitrary deltas usually corrupts
the visible answer. Prefer bounded waiting or a clearly signalled
cancellation/error policy over silent loss.


<br/>


## 8. Measure time to first content and completion time

Streaming performance has at least two important timing measures:

-   **Time to first content (TTFC):** elapsed time from starting the
    request until the first meaningful content delta is received.
-   **Total completion time:** elapsed time from starting the request
    until the stream completes or fails.

Also consider recording total duration, number of deltas, output length,
provider response ID, completion status, and cancellation/failure
reason. Do not record sensitive content merely to calculate these
metrics.

``` python
import time

started_at = time.perf_counter()
first_content_at = None
parts: list[str] = []

# Inside the provider stream loop:
# if event.type == "response.output_text.delta" and event.delta:
#     if first_content_at is None:
#         first_content_at = time.perf_counter()
#     parts.append(event.delta)

# After the stream finishes or fails:
finished_at = time.perf_counter()

ttfc_seconds = (
    first_content_at - started_at
    if first_content_at is not None
    else None
)
total_seconds = finished_at - started_at

print("Time to first content:", ttfc_seconds)
print("Total duration:", total_seconds)
```

Use a monotonic timer such as `time.perf_counter()` for durations. If no
content arrives, TTFC should be recorded as missing rather than zero.
Compare percentiles such as p50 and p95 across representative requests;
averages alone can hide slow outliers.


<br/>


## 9. Practice: fake stream, mid-stream failure, and cancellation

This exercise requires no API key. It simulates a stream that can emit
fragments, fail partway through, or be cancelled by its caller.

``` python
import asyncio
import time
from collections.abc import AsyncIterator

async def fake_event_source(
    *,
    fail_after: int | None = None,
) -> AsyncIterator[dict]:
    fragments = ["Streaming ", "is ", "incremental ", "output."]
    for index, fragment in enumerate(fragments):
        if fail_after is not None and index == fail_after:
            raise RuntimeError("Simulated upstream failure")
        await asyncio.sleep(0.1)
        yield {"type": "delta", "text": fragment}
    yield {"type": "completed"}

async def consume_stream(*, fail_after: int | None = None) -> dict:
    started = time.perf_counter()
    first_content_at = None
    parts = []
    completed = False
    error = None

    try:
        async for event in fake_event_source(fail_after=fail_after):
            if event["type"] == "delta":
                if first_content_at is None:
                    first_content_at = time.perf_counter()
                parts.append(event["text"])
            elif event["type"] == "completed":
                completed = True
    except asyncio.CancelledError:
        # Preserve cancellation semantics.
        raise
    except Exception as exc:
        error = type(exc).__name__

    finished = time.perf_counter()
    return {
        "text": "".join(parts),
        "completed": completed,
        "error": error,
        "time_to_first_content": (
            first_content_at - started
            if first_content_at is not None else None
        ),
        "total_duration": finished - started,
    }

async def main():
    success = await consume_stream()
    print("Success:", success)

    failure = await consume_stream(fail_after=2)
    print("Mid-stream failure:", failure)

    task = asyncio.create_task(consume_stream())
    await asyncio.sleep(0.15)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Caller cancelled the stream consumer.")

asyncio.run(main())
```

<br/>

### Expected observations

-   The successful run contains all fragments and `completed=True`.
-   The failure run may contain partial text, but `completed=False` and
    `error` is set.
-   The cancellation run raises `CancelledError` to the caller; the
    consumer must not mark it as completed.
-   Time to first content is measured from request start to the first
    non-empty delta, not to stream creation alone.

<br/>

### Practice extensions

1.  Map fake events to SSE `delta`, `completed`, and `error` frames.
2.  Add a maximum stream duration.
3.  Add a bounded queue between the event source and transport consumer.
4.  Add a test asserting that partial output is never labelled
    `completed`.
5.  Add a completed-output validation step before marking a structured
    result usable.


<br/>


## 10. Checkpoint: partial content versus a completed, validated response

**Partial content** is provisional. It may be truncated, followed by an
error, or fail schema/business-rule validation. Receiving a text delta
only proves that some content arrived.

A **completed, validated response** requires the provider stream to
reach its documented successful terminal state, the application to
reconstruct the final output, and any required parsing, schema
validation, policy checks, and business-rule checks to pass.

For a plain text chat UI, partial deltas can be displayed as they arrive
with a clear interrupted/error state if the stream fails. For structured
output or consequential actions, do not act on partial content; wait for
successful completion and validation.

<br/>

## 11. Key takeaways

-   Provider stream events and application transport events are separate
    contracts.
-   Accumulate deltas in order and track terminal status explicitly.
-   A stream that emitted text can still fail before completion.
-   SSE is a one-way HTTP streaming option; define and document your
    event schema.
-   Handle disconnects, cancellation, timeouts, and slow consumers
    deliberately.
-   Validate completed structured output before consequential use.
-   Measure time to first content separately from total completion time.

<br/>

## References

-   OpenAI Python SDK --- streaming Responses API:
    https://github.com/openai/openai-python
-   OpenAI API documentation --- Responses API:
    https://platform.openai.com/docs/api-reference/responses
-   FastAPI --- StreamingResponse:
    https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
-   MDN --- Server-Sent Events:
    https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
-   Python `asyncio` tasks and cancellation:
    https://docs.python.org/3/library/asyncio-task.html

Verify current provider event names and SDK streaming methods against
your pinned versions before using them in production.
