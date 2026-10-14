# Chapter 14: Abuse Prevention, Rate Limiting, and Resource Exhaustion

## Learning Objectives

By the end of this chapter, you should be able to:

- Bound request size, uploaded file size, media duration, output tokens, and expensive operations.
- Apply per-user and per-tenant quotas, concurrency limits, and total request deadlines.
- Bound retries, batch sizes, queue depth, and tool execution.
- Track consumption and enforce budgets at application-controlled boundaries.
- Handle unauthenticated abuse, repeated failures, and capacity rejection gracefully.
- Test resource controls with fake clients and small local workloads without creating large bills or traffic.

<br/>

## 1. Why Abuse Prevention Matters in GenAI

GenAI workloads can consume multiple resources in a single request: input tokens, output tokens, embedding operations, retrieval queries, reranking, image or audio processing, external tool calls, storage, and network bandwidth. Some requests are expensive because they are large; others are expensive because they trigger many downstream operations or repeated retries.

**Resource exhaustion** occurs when a workload consumes enough capacity, time, memory, concurrency, or budget to degrade or prevent service. It can be caused by malicious abuse, accidental client loops, oversized uploads, inefficient prompts, retry storms, or legitimate demand that exceeds capacity.

Abuse prevention is therefore both a security control and a reliability practice. It should constrain each request and also protect the service as a whole.

<br/>

### Core principle

A limit is effective only when it is enforced at the boundary that controls the resource. A prompt instruction such as “keep the answer short” does not reliably bound token usage, file processing, tool calls, or total cost.

<br/>

## 2. Map the Resource-Cost Surface

Before setting limits, list the resources consumed along the request path.

| Resource | Example source of consumption | Possible control |
|---|---|---|
| Network bandwidth | Large requests or repeated uploads | Request-body and upload limits |
| Memory | Large files, decoded media, large batches | Size limits, streaming, bounded buffers |
| CPU | Parsing, conversion, chunking, validation | Work limits, deadlines, worker quotas |
| GPU / accelerator time | Image, audio, video, or model workloads | Duration/resolution caps, concurrency limits |
| Model input tokens | Long prompts, history, retrieved context | Input-token budget and context selection |
| Model output tokens | Long generations | Maximum output tokens and stop conditions |
| External API usage | Model, search, embedding, or reranking calls | Per-operation quotas and spending budgets |
| Tool execution | Agent loops or expensive tool calls | Tool allowlists, call budgets, execution timeouts |
| Storage | Uploads, intermediate artifacts, cached results | Storage quotas, retention, cleanup |
| Queue capacity | Bursts or slow downstream dependencies | Queue-depth limits and backpressure |
| Human-review capacity | Excessive escalations or abusive submissions | Review quotas, prioritization, and triage |

A request's cost may be multiplicative. For example, a large document can trigger parsing, chunking, embedding, retrieval, reranking, and several model calls. Limiting only the final answer length leaves most of those costs uncontrolled.

<br/>

## 3. Bound Inputs Before Expensive Processing

Validate input constraints as early as possible—before buffering large bodies, decoding media, calling a model, or starting expensive downstream work.

### 3.1 Request and payload size

Define maximums for:

- HTTP request-body bytes.
- Number and size of fields.
- Text length or estimated input tokens.
- Number of conversation messages and total history size.
- Number of documents, images, audio clips, or other attachments.
- Batch size and number of items in a batch.

Enforce request-body limits at the edge proxy or API gateway and again in application code where appropriate. Do not assume that a client-provided `Content-Length` is always present or trustworthy. For streaming uploads, count bytes as they arrive and stop reading once the configured maximum is exceeded.

<br/>

### 3.2 Files and media

For uploaded files, consider more than the compressed byte size. Define limits for:

- File bytes.
- Page count or document length.
- Image dimensions and total pixel count.
- Audio duration, sample rate, and channels.
- Video duration, frame rate, resolution, and extracted frame count.
- Archive expansion size and number of contained files.
- Parsing time, OCR time, and extracted-text size.

A small compressed file may expand into a large workload. Apply archive expansion limits and defend against decompression bombs. Validate file type from content and parser behavior, not only a filename extension or user-supplied MIME type. Use sandboxed parsers and resource-limited workers for untrusted files.

<br/>

### 3.3 Reject early and explain safely

Return a clear client error when an input exceeds a documented limit. State the relevant limit and how the user can reduce or split the input, without exposing internal infrastructure details.

Do not start a model call and only then discover that the request exceeded an input limit. Early rejection reduces cost and avoids occupying downstream capacity unnecessarily.

<br/>

## 4. Bound Model Input and Output

### 4.1 Input-token budgets

A model's context window is not a practical application budget. A request that fits the model may still be too expensive or slow.

Set an application-level input budget that accounts for:

- System and developer instructions.
- Conversation history.
- Retrieved documents and tool results.
- User input.
- Formatting or schema instructions.
- A reserve for model-specific overhead and output.

When input exceeds the budget, apply a defined policy: reject, ask the user to narrow the request, summarize older history, or select fewer relevant retrieved passages. Do not silently remove critical evidence or security instructions.

<br/>

### 4.2 Output-token caps

Set a maximum output-token count appropriate to the task. A concise classification may need only a small response, while a report-generation task may need more. Use different limits for different operations rather than one large global maximum.

Output caps help bound generation length, but they do not bound all costs. Input processing, image/audio/video processing, embeddings, retrieval, reranking, tool calls, retries, and waiting workers can consume substantial resources before or outside the final generation.

<br/>

### 4.3 Bound agent loops

For agentic applications, define explicit limits for:

- Total tool calls per request.
- Calls to each individual tool.
- Number of agent iterations.
- Maximum parallel tool calls.
- Tool input size and output size.
- Per-tool execution timeout.
- Total wall-clock deadline.
- Maximum model invocations per task.

The model should not be able to bypass these controls by repeatedly requesting a tool or by spawning nested operations. Enforce counters and deadlines in trusted orchestration code, not solely in the prompt.

<br/>

## 5. Per-User and Per-Tenant Limits

A shared global quota can be unfair: one user or tenant may consume the available capacity and degrade service for everyone else. Apply limits at several scopes where relevant:

- Per request.
- Per user or authenticated principal.
- Per tenant or organization.
- Per API key or service identity.
- Per IP address or network range for unauthenticated traffic.
- Per feature, model, or expensive operation.
- Global service capacity and spending budget.

Use multiple windows when appropriate—for example, a short burst limit and a longer sustained-usage limit. A token bucket or leaky bucket can allow reasonable bursts while enforcing an average rate.

<br/>

### Example: token-bucket intuition

A bucket has a maximum capacity and refills at a configured rate. Each request consumes tokens from the bucket. When insufficient tokens remain, the system delays or rejects the request according to policy.

A token bucket is a rate-limiting algorithm; the tokens in the bucket are not LLM tokens. They are abstract quota units representing requests, weighted cost, or another chosen measure.

<br/>

### Avoid quota bypasses

- Identify users and tenants using trusted server-side identity, not client-supplied tenant names alone.
- Ensure anonymous clients cannot create unlimited free identities to bypass limits.
- Apply global limits in addition to per-user limits.
- Make quota updates atomic when requests can arrive concurrently.
- Ensure alternate endpoints and tools share the intended quota accounting.
- Treat forwarded IP headers as trustworthy only when set by a trusted proxy.

Rate limits should protect service capacity without unnecessarily penalizing legitimate users sharing a network. IP-only throttling can affect schools, offices, or households with shared public addresses.

<br/>

## 6. Concurrency, Deadlines, and Backpressure

### 6.1 Concurrency limits

Rate limits control how frequently requests arrive; concurrency limits control how many operations are active simultaneously. Both are necessary because requests can have very different durations.

Set concurrency bounds for:

- Requests per user or tenant.
- Expensive model calls.
- File-processing workers.
- Tool executions.
- Batch jobs.
- External-provider connections.

Use bounded semaphores or worker pools rather than creating an unbounded task for every incoming request. If a limit is reached, queue only a bounded amount of work or reject promptly.

<br/>

### 6.2 Total deadlines

A timeout on one model call is not the same as a deadline for the entire request. A workflow may perform retrieval, reranking, multiple model calls, and tools; each stage can consume time.

Set an end-to-end deadline and propagate the remaining time to downstream calls. Avoid giving each retry a fresh full timeout, which can make the total request duration unbounded.

When a deadline expires:

- Cancel work where cancellation is supported.
- Stop scheduling new downstream operations.
- Release concurrency slots and temporary resources.
- Prevent late results from triggering actions after the request is no longer valid.
- Return a controlled timeout response.

Cancellation must be handled carefully: some downstream work may continue even after the client disconnects. Track or terminate it where supported.

<br/>

### 6.3 Backpressure and queue depth

A queue can smooth short bursts but cannot solve sustained overload. Define maximum queue depth, maximum wait time, and a policy for expired work. When full, reject or shed lower-priority work instead of accepting an unlimited backlog.

Useful overload responses may include a retry-after hint, a clear temporary-capacity message, or a job identifier when the system genuinely supports asynchronous processing. Do not promise a completion time the system cannot support.

<br/>

## 7. Bound Retries, Batches, and Fan-Out

Retries can multiply traffic during a provider outage. If many clients retry simultaneously, they can create a retry storm and make recovery harder.

Use:

- A small, explicit retry budget.
- Exponential backoff with jitter where retries are appropriate.
- Retry rules based on error type.
- A total deadline covering the original attempt and retries.
- Idempotency keys for operations that may have side effects.
- Circuit breakers or load shedding for persistently failing dependencies.

Do not retry every failure. Invalid requests, authorization failures, and policy blocks generally should not be retried automatically. Retrying a non-idempotent tool action may duplicate a payment, message, or update.

Bound batch size and fan-out. One user request should not be able to trigger an unbounded number of embeddings, searches, reranking calls, or parallel tools. Enforce limits in the server-side orchestrator and account for nested operations.

<br/>

## 8. Application-Controlled Budgets

Usage tracking should occur where the application can enforce a decision before more work is performed.

Track, as appropriate:

- Request count and accepted bytes.
- Estimated and actual input/output tokens.
- Model and provider invocations.
- Embedding and reranking operations.
- Tool calls and execution time.
- Media-processing duration and extracted content size.
- Queue wait time and worker occupancy.
- Cost estimates by user, tenant, feature, and model.
- Rejections, timeouts, retries, and provider failures.

Use both **usage quotas** and **spending budgets**. A request-count limit does not account for varying request costs; a spending limit alone may not protect memory, concurrency, or latency.

<br/>

### Budget enforcement pattern

1. Authenticate the caller and resolve the tenant from trusted identity.
2. Validate input and estimate the expected work.
3. Check per-request, per-user, per-tenant, and global budgets.
4. Reserve budget or capacity before expensive work where possible.
5. Execute only within the allowed operation and time budgets.
6. Reconcile estimates with actual usage.
7. Release unused reservations and record safe metrics.
8. Reject or defer additional work when a limit is reached.

Budget reservation must be concurrency-safe. If several requests check a balance simultaneously without atomic reservation, they may all proceed and collectively exceed the limit.

Do not log secret-bearing provider headers or raw private content just to measure usage. Prefer counters, normalized error codes, request identifiers, and provider-reported usage metadata.

<br/>

## 9. Unauthenticated Abuse and Repeated Failures

Public endpoints may receive requests before the caller has an authenticated identity. Apply controls at the network and application edges, such as:

- Maximum request-body size.
- Per-IP or per-network burst controls, with trusted-proxy handling.
- Global concurrency limits.
- Short deadlines for inexpensive validation.
- Abuse detection for repeated malformed requests.
- Challenge or authentication requirements where appropriate.
- Quotas before costly operations.
- Safe rejection without revealing detailed internal defenses.

Unauthenticated rate limiting should not rely exclusively on an IP address. Distributed clients can rotate addresses, and legitimate users can share one address. Combine several signals carefully, comply with privacy requirements, and avoid collecting unnecessary identifying data.

Repeated failures can indicate misconfiguration, a buggy client, abuse, or a downstream outage. Track error categories and patterns, but do not automatically assume malicious intent. Apply graduated controls where justified: reject invalid requests, slow abusive patterns, require reauthentication, or temporarily limit a principal according to documented policy.

<br/>

## 10. Graceful Capacity Rejection

A robust service should fail predictably under overload rather than exhausting memory or crashing.

A capacity-rejection response should:

- Clearly indicate that the request was not accepted or completed.
- Avoid implying that a rejected action succeeded.
- Include retry guidance only when retrying is reasonable.
- Avoid encouraging immediate, synchronized retries.
- Preserve idempotency for any request whose status is uncertain.
- Avoid exposing internal hostnames, provider credentials, stack traces, or infrastructure details.

For asynchronous workloads, distinguish between **accepted**, **queued**, **running**, **completed**, and **failed**. An HTTP response that acknowledges queueing should not be described as successful task completion.

Use graceful degradation when a safe, useful fallback exists. For example, a system might disable an optional reranking stage or offer a smaller batch size during overload. Do not remove essential authorization, validation, or policy checks merely to improve throughput.

<br/>

## 11. Example: A Bounded Local Request Handler

The following Python pattern illustrates input checks, an operation budget, and a deadline. It is intentionally small and does not replace gateway limits, distributed quotas, provider-side controls, or production-grade cancellation.

```python
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class Limits:
    max_text_chars: int = 8_000
    max_output_tokens: int = 500
    max_tool_calls: int = 3
    total_deadline_seconds: float = 10.0


class LimitExceeded(Exception):
    pass


def validate_text(text: str, limits: Limits) -> None:
    if len(text) > limits.max_text_chars:
        raise LimitExceeded("Input exceeds the allowed size")


def run_bounded_task(text, client, limits=Limits()):
    validate_text(text, limits)
    deadline = time.monotonic() + limits.total_deadline_seconds

    # Illustrative only: the client must enforce its own network timeout.
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Request deadline exceeded")

    response = client.generate(
        text,
        max_output_tokens=limits.max_output_tokens,
        timeout=remaining,
    )
    if time.monotonic() > deadline:
        raise TimeoutError("Request deadline exceeded")

    return response
```

Notes:

- `max_text_chars` is a character limit, not a reliable token count. Production systems should also enforce a token budget using the relevant tokenizer or provider usage information.
- The example assumes `client.generate` supports a timeout argument. Use the actual client API and verify its timeout semantics.
- Checking the clock after a blocking call detects a late response but does not itself cancel work. Use client cancellation or task-level deadlines where supported.
- A complete agent orchestrator must also count tool calls, bound tool arguments/results, and prevent new work after the deadline.
- A local limit does not replace distributed per-tenant quotas or edge-level request-size controls.

<br/>

## 12. Practice: Verify Limits with Fake Clients

Use fake clients and small local workloads. Do not generate large provider bills, high traffic, or intentionally overload a shared service.

### Synthetic test plan

| Test | Setup | Expected result |
|---|---|---|
| R1 | Text is below the configured maximum | Input validation passes |
| R2 | Text exceeds the maximum by one character | Rejected before client invocation |
| R3 | Fake client records requested output-token cap | Cap is passed to the client |
| R4 | Fake client simulates a timeout | Request fails within the configured deadline budget |
| R5 | Fake client returns a retryable error repeatedly | Retry count remains within the configured budget |
| R6 | Tool loop attempts more than the maximum calls | Additional tool calls are denied |
| R7 | Per-tenant quota is exhausted | New expensive work is rejected or deferred |
| R8 | Concurrency slots are full | Request is queued within a bounded queue or rejected |
| R9 | Batch exceeds maximum item count | Batch is rejected or safely split under policy |
| R10 | Moderation or authorization check fails | Required safety control is not bypassed during degradation |
| R11 | Unauthenticated client repeatedly sends malformed input | Edge/application controls limit the repeated work |
| R12 | Duplicate request arrives after a timeout | Idempotency or status reconciliation prevents duplicate side effects |

<br/>

### Example fake client

```python
class FakeModelClient:
    def __init__(self):
        self.calls = []

    def generate(self, text, *, max_output_tokens, timeout):
        self.calls.append({
            "text_length": len(text),
            "max_output_tokens": max_output_tokens,
            "timeout": timeout,
        })
        return {"text": "synthetic response"}


def test_oversized_input_is_rejected_before_model_call():
    client = FakeModelClient()
    limits = Limits(max_text_chars=5)

    try:
        run_bounded_task("sixsix", client, limits)
    except LimitExceeded:
        pass
    else:
        raise AssertionError("Expected oversized input to be rejected")

    assert client.calls == []
```

This test uses no real model API. Expand it with fake clocks or controlled timeout exceptions to verify deadlines and retry budgets deterministically.

<br/>

### Practice tasks

1. Define the resource limits for a text-only endpoint and a document-Q&A endpoint.
2. Add file-byte, page-count, and extracted-text limits to the document workflow.
3. Add per-user and per-tenant quotas with a small in-memory test implementation.
4. Bound concurrency and queue depth.
5. Add a total deadline that includes retrieval, model calls, and tool execution.
6. Verify that a rejected request does not call downstream services.
7. Verify that retries do not exceed the configured count or deadline.
8. Confirm that logs record the reason for rejection without storing full private payloads.
9. Simulate an exhausted budget and verify that no new expensive operation begins.
10. Document which limits are enforced by the gateway, application, orchestration layer, and provider.

<br/>

## 13. Checkpoint

**Checkpoint:** Explain why an output-token cap alone does not bound every cost or resource risk.

A complete answer should cover:

1. Input bytes, input tokens, conversation history, and retrieved context.
2. File and media processing before generation.
3. Embeddings, retrieval, reranking, and other upstream operations.
4. Agent loops, parallel tool calls, batch size, and downstream fan-out.
5. Retries, timeouts, abandoned work, queue depth, and concurrency.
6. Per-user, per-tenant, per-operation, and global budgets.
7. The difference between a rate limit, a concurrency limit, a deadline, and a spending budget.
8. How fake clients and small local tests demonstrate enforcement without real cost.

A strong answer identifies where each limit is enforced and explains what happens when the limit is reached. It does not rely on a prompt instruction or a final output cap as the only resource control.

<br/>

## 14. Review Questions

1. Why can a short model response still be expensive?
2. What is the difference between rate limiting and concurrency limiting?
3. Why must uploaded files be bounded by more than their compressed byte size?
4. Why should an end-to-end deadline include retries and downstream calls?
5. How can retries make an outage worse?
6. Why should quotas exist at per-tenant and global scopes?
7. What is the difference between usage quotas and spending budgets?
8. Why is a client-supplied tenant identifier insufficient for quota enforcement?
9. How should a service behave when its queue is full?
10. Why must a timed-out tool operation be treated carefully if it may have side effects?
11. What does a fake client help test, and what does it not prove?
12. Why should essential authorization and validation controls remain active during graceful degradation?

<br/>

### Suggested answers

1. The request may have used expensive input processing, retrieval, embeddings, reranking, media conversion, or tool calls before generating the short response.
2. Rate limiting controls arrivals over time; concurrency limiting controls the number of active operations.
3. Compressed files may expand dramatically, contain many entries, or require costly parsing and decoding.
4. Otherwise, each stage or retry can consume a fresh timeout and make total latency unbounded.
5. Many clients may repeatedly call an already failing dependency, increasing load and delaying recovery.
6. Per-tenant quotas limit noisy neighbors; global quotas protect the service and shared provider budgets.
7. Usage quotas constrain a measured resource or operation count; spending budgets constrain financial consumption.
8. A client can claim another tenant's identity; the server should derive tenant scope from authenticated, authorized identity.
9. Reject or shed work predictably, possibly with safe retry guidance, rather than accepting an unbounded backlog.
10. The operation may have completed despite the missing response; retrying without idempotency or reconciliation can duplicate the side effect.
11. A fake client verifies application logic and call bounds without real traffic or spend, but does not prove provider behavior or distributed production capacity.
12. Removing these controls can turn an availability incident into a security or safety incident.

<br/>

## Key Takeaways

- Resource protection must cover the entire request path, not only generated output.
- Bound bytes, tokens, media dimensions and duration, batches, tool calls, retries, and total elapsed time.
- Combine rate limits, concurrency limits, bounded queues, and global capacity controls.
- Enforce quotas using trusted identity and atomic accounting at application-controlled boundaries.
- Treat timeouts and uncertain execution status carefully when actions have side effects.
- Reject overload gracefully and preserve essential security controls.
- Use fake clients and small local tests to prove that limits are enforced before costly work begins.

<br/>

## Further Reading

- OWASP API Security Top 10 — https://owasp.org/www-project-api-security/
- OWASP Top 10 for LLM Applications — https://genai.owasp.org/
- Google SRE Book: Addressing Cascading Failures — https://sre.google/sre-book/addressing-cascading-failures/
- Your model provider's official documentation for token limits, rate limits, timeouts, concurrency, and usage reporting.
- Your API gateway, cloud platform, and task-queue documentation for request limits, quotas, backpressure, and workload isolation.
