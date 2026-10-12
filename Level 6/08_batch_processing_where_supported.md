# 08. Batch Processing Where Supported

## Learning objectives

By the end of this chapter, you should be able to:

-   Compare provider-managed batch jobs with bounded concurrent client
    requests.
-   Prepare records with stable identifiers and validated inputs.
-   Trace submission, status checks, results, and cancellation where
    available.
-   Match results by identifier rather than assuming input order is
    preserved.
-   Handle per-item failures and retry only appropriate items.
-   Compare delayed processing with interactive latency requirements.

> **Scope:** Batch APIs are provider-specific. This chapter explains
> common design principles and uses an illustrative provider-neutral
> workflow. Exact file formats, endpoints, statuses, completion windows,
> result ordering, cancellation support, and pricing depend on the
> provider's current batch API.

<br/>

## 1. What batch processing means

Batch processing groups many independent inputs into a workload that is
submitted and processed as a unit. It is useful when results do not need
to be returned immediately---for example, offline classification,
document enrichment, dataset labeling, or scheduled evaluation.

Two approaches are commonly called "batching," but they are different.

| Approach                               | How It Works                                                                                                                   | Typical Fit                                                                             |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| **Provider-managed batch job**         | Submit a job or input file to a provider's batch API; the provider processes it asynchronously and exposes status and results. | Large offline workloads where delayed results are acceptable.                           |
| **Bounded concurrent client requests** | The application sends ordinary API requests concurrently, while enforcing its own limits.                                      | Smaller jobs, interactive work, or workloads needing tighter control over each request. |


A provider-managed batch API may have different limits, supported
endpoints, result formats, cancellation behavior, and pricing from its
normal interactive API. Do not assume every provider offers batch
processing or that all models and features are supported.


``` mermaid
flowchart TD
    A[Validated input records] --> B{Choose execution mode}
    B -->|Delayed results acceptable| C[Provider-managed batch job]
    B -->|Need direct request control| D[Bounded concurrent requests]
    C --> E[Submit job or input file]
    E --> F[Poll or wait for job status]
    F --> G[Retrieve result records]
    D --> H[Send limited requests]
    H --> I[Collect per-request outcomes]
    G --> J[Match results by stable ID]
    I --> J
    J --> K[Validate and store outcomes]
```


<br/>


## 2. Decide whether batch processing fits

Batch processing is a good candidate when:

-   Many independent records can be processed without a user waiting for
    each one.
-   A delayed completion window is acceptable.
-   The provider's batch endpoint supports the required model and task.
-   The workload benefits from provider-managed queuing or
    batch-specific pricing, if offered.
-   The application can persist job state and recover after restarts.

Bounded concurrent requests may be preferable when:

-   The application needs a result during a user-facing request.
-   The workload is small or requires fine-grained control.
-   The provider batch API does not support the required operation.
-   Individual retries and immediate progress feedback are important.
-   The operational complexity of a batch job is not justified.

Batch processing is not automatically faster for every workload. Compare
end-to-end latency, throughput, operational overhead, failure recovery,
and cost using the provider's current terms.


<br/>


## 3. Prepare records with stable identifiers

Each input record should have an application-owned identifier that
remains stable throughout the job. Do not rely on line number or output
order to associate results with inputs.

For example, a small classification workload might contain:

``` python
records = [
    {"record_id": "ticket-1001", "text": "I cannot log in to my account."},
    {"record_id": "ticket-1002", "text": "Please update my billing address."},
    {"record_id": "ticket-1003", "text": "The app crashes when I open settings."},
]
```

Validate input before submission:

-   Required fields exist and have the expected types.
-   Text length and payload size are within configured limits.
-   Identifiers are unique within the job.
-   Sensitive data is minimized or handled according to policy.
-   The intended model, prompt version, and task schema are recorded.
-   Empty or malformed records are rejected or explicitly classified
    before submission.

A stable ID allows the application to join results to the source record
even if results arrive out of order, some items fail, or the provider
emits a separate error record.

``` python
def validate_records(records: list[dict]) -> list[dict]:
    seen: set[str] = set()
    validated = []

    for record in records:
        record_id = record.get("record_id")
        text = record.get("text")

        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("Each record needs a non-empty record_id.")
        if record_id in seen:
            raise ValueError(f"Duplicate record_id: {record_id}")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Missing text for {record_id}")

        seen.add(record_id)
        validated.append({
            "record_id": record_id,
            "text": text.strip(),
        })

    return validated
```

For a real provider batch API, map each application ID to the provider's
documented per-request identifier field. Do not invent a field name and
assume the provider preserves it.


<br/>


## 4. Track the batch as a stateful workflow

A provider-managed batch job typically has multiple stages, but the
exact lifecycle is provider-specific. A generic conceptual workflow is:

1.  **Prepare:** validate records and build provider-compatible input.
2.  **Submit:** send the job or input file and persist the returned job
    identifier.
3.  **Track:** inspect the provider's status using its documented
    method.
4.  **Retrieve:** download or read completed results and error records.
5.  **Reconcile:** match each result to its original input by stable
    identifier.
6.  **Validate:** check successful outputs against the expected schema
    and business rules.
7.  **Persist:** store outcomes and mark the application job complete or
    partially complete.
8.  **Recover:** retry only eligible failed items, if safe and
    supported.

``` mermaid
stateDiagram-v2
    [*] --> Prepared
    Prepared --> Submitted
    Submitted --> Running
    Running --> Completed
    Running --> PartiallyFailed
    Running --> Failed
    Submitted --> CancelRequested
    Running --> CancelRequested
    CancelRequested --> Cancelled
    Completed --> Reconciled
    PartiallyFailed --> Reconciled
    Failed --> ReconcileErrors
    Reconciled --> [*]
    ReconcileErrors --> [*]
    Cancelled --> [*]
```

This diagram is a conceptual model, not a promise that a specific
provider uses these exact statuses or permits cancellation from each
state. Map the actual provider statuses to your application's own state
model.

<br/>

### Persist enough state to recover

At minimum, consider storing:

-   Application batch ID.
-   Provider job ID, if applicable.
-   Submission timestamp and current state.
-   Record IDs included in the job.
-   Model and prompt/configuration version.
-   Result and error locations or references.
-   Counts of submitted, succeeded, failed, and unresolved records.
-   Retry attempts and timestamps.

Do not store API credentials or unnecessary sensitive input content in
job metadata.


<br/>


## 5. Submission, status checks, results, and cancellation

A provider-managed batch API may use input files, job creation calls,
polling, downloadable output files, or other mechanisms. The application
should follow the provider's documented contract.

### Submission

-   Validate all records before submitting.
-   Record the exact set of IDs included.
-   Persist the returned job identifier immediately.
-   Make submission recoverable if the client loses the response.
-   Avoid blindly resubmitting after a timeout: the provider may have
    accepted the original job.

<br/>

### Status checks

-   Use the provider's documented status endpoint or retrieval
    mechanism.
-   Poll at a sensible interval and use backoff where appropriate.
-   Distinguish terminal states from queued or running states.
-   Avoid aggressive polling that creates unnecessary traffic.
-   Use webhooks or notifications only if the provider documents and
    supports them.

<br/>

### Result retrieval

-   Expect successful outputs and per-item errors to be represented
    separately where the API supports that pattern.
-   Parse each result according to the documented format.
-   Validate outputs before storing them as successful application
    results.
-   Reconcile missing, duplicate, unexpected, or malformed result IDs.

<br/>

### Cancellation

Cancellation is not universally supported, and its meaning varies. Some
APIs may allow cancellation only in certain states; others may not
support it. Even when cancellation is accepted, some work may already
have completed.

Treat cancellation as a requested state transition, verify the
provider's resulting status, and reconcile any outputs that were already
produced. Do not assume cancellation refunds usage or removes the need
to process partial results.

<br/>


## 6. Match results by identifier, not order

A common mistake is to assume that the first output belongs to the first
input, the second output to the second input, and so on. Providers may
return results in a different order, split success and error records, or
omit results for unresolved items.

Use identifiers to reconcile outcomes:

``` python
inputs = {
    "ticket-1001": "I cannot log in to my account.",
    "ticket-1002": "Please update my billing address.",
    "ticket-1003": "The app crashes when I open settings.",
}

# Illustrative normalized result records; not a provider-specific payload.
results = [
    {"record_id": "ticket-1003", "status": "succeeded", "label": "technical_issue"},
    {"record_id": "ticket-1001", "status": "succeeded", "label": "account_access"},
    {"record_id": "ticket-1002", "status": "failed", "error_code": "temporary_error"},
]

result_by_id = {}
for result in results:
    record_id = result["record_id"]
    if record_id not in inputs:
        raise ValueError(f"Unexpected result ID: {record_id}")
    if record_id in result_by_id:
        raise ValueError(f"Duplicate result ID: {record_id}")
    result_by_id[record_id] = result

for record_id in inputs:
    result = result_by_id.get(record_id)
    if result is None:
        print(record_id, "-> unresolved: no result received")
    elif result["status"] == "succeeded":
        print(record_id, "->", result["label"])
    else:
        print(record_id, "-> failed:", result.get("error_code"))
```

A robust reconciliation stage should detect:

-   **Missing IDs:** inputs with no corresponding result.
-   **Unknown IDs:** results that do not belong to the submitted input
    set.
-   **Duplicate IDs:** multiple results for one input when only one is
    expected.
-   **Per-item errors:** known failures that need classification.
-   **Malformed results:** output that cannot be parsed or validated.
-   **Partial job completion:** some items succeeded while others remain
    unresolved.

Keep provider job status and per-item status separate. A provider job
can finish processing while some individual records fail.


<br/>


## 7. Per-item failures and safe retries

Do not retry every failure indiscriminately. Classify errors before
deciding what to do.

| Failure Category                        | Typical Handling                                                                                            |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Invalid input or schema error           | Fix or reject the input; retrying unchanged data usually will not help.                                     |
| Authentication or permission failure    | Correct credentials or permissions before resubmission.                                                     |
| Rate limit or transient service error   | Retry only according to documented guidance, using backoff and limits.                                      |
| Timeout with unknown submission outcome | Reconcile whether the original job was accepted before resubmitting.                                        |
| Model output fails validation           | Consider a controlled repair or retry only if the task permits it; preserve the original failure for audit. |
| Missing result                          | Check job completion and provider output/error records before retrying.                                     |
| Permanent unsupported operation         | Change the workflow or use a supported endpoint.                                                            |


<br/>

### Retry only eligible records

Maintain a separate list of records that are safe and appropriate to
retry. Use bounded retry attempts and backoff. For operations with side
effects, design idempotency and duplicate protection before retrying.
For pure classification, repeated inference is often easier to tolerate,
but it can still cost money and may return a different result.

``` python
def retry_candidates(results: list[dict]) -> list[str]:
    retryable_codes = {"temporary_error", "rate_limited"}
    candidates = []

    for result in results:
        if (
            result.get("status") == "failed"
            and result.get("error_code") in retryable_codes
        ):
            candidates.append(result["record_id"])

    return candidates
```

This example's error codes are application-defined placeholders. Replace
them with the actual provider error categories and your retry policy.


<br/>


## 8. Batch jobs versus bounded concurrent requests

| Dimension          | Provider-managed Batch                                       | Bounded Concurrent Requests                                   |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------- |
| Result timing      | Often delayed; job may run asynchronously                    | Each request returns as it completes                          |
| Application state  | Requires job lifecycle tracking                              | Requires per-request tracking and aggregation                 |
| Throughput control | Often controlled partly by provider batch infrastructure     | Application sets concurrency and rate limits                  |
| Result association | Reconcile per-record IDs from output records                 | Associate each result with the input task/ID                  |
| Partial failure    | Inspect output and error records                             | Handle exceptions/status per request                          |
| Cancellation       | Only if supported by the provider, and often state-dependent | Cancel local tasks where possible; remote work may continue   |
| Best fit           | Offline, large, non-interactive workloads                    | Smaller or latency-sensitive workloads needing direct control |


A batch API may offer a different cost or quota profile, but this is not
guaranteed. Compare the current provider's pricing, eligible models,
throughput limits, completion windows, and supported endpoint operations
before deciding.


<br/>


## 9. Practice: design a classification batch with mixed outcomes

Use these application records:

``` python
records = [
    {"record_id": "msg-001", "text": "I need help resetting my password."},
    {"record_id": "msg-002", "text": "Where can I download my invoice?"},
    {"record_id": "msg-003", "text": ""},  # Invalid: empty text
    {"record_id": "msg-004", "text": "The mobile app closes when I open it."},
    {"record_id": "msg-005", "text": "Please change the billing email."},
]
```

Assume the target labels are `account_access`, `billing`, and
`technical_issue`. The batch should produce one application-level
outcome per input ID, including invalid inputs that are rejected before
submission.

<br/>

### Suggested design

1.  Validate all inputs and separate invalid records from valid ones.
2.  Assign or preserve a stable `record_id` for every record.
3.  Build provider-compatible requests with a consistent classification
    instruction and output schema.
4.  Submit through the chosen provider batch API, if it supports the
    model and operation; otherwise use bounded concurrent requests.
5.  Persist the returned provider job ID or per-request task IDs.
6.  Simulate a mix of successful labels, one transient error, and one
    malformed model output.
7.  Reconcile by `record_id`, not array position.
8.  Retry only the transient failure after checking whether retry is
    safe.
9.  Mark malformed output as failed validation until corrected or
    reprocessed.
10. Report counts for valid inputs, rejected inputs, successes,
    retryable failures, permanent failures, and unresolved records.

<br/>

### Example normalized outcomes

| Record ID | Example Outcome          | Application Action                                  |
| --------- | ------------------------ | --------------------------------------------------- |
| `msg-001` | `account_access`         | Store validated label.                              |
| `msg-002` | `billing`                | Store validated label.                              |
| `msg-003` | Invalid input            | Reject before provider submission.                  |
| `msg-004` | Temporary provider error | Retry if eligible and within retry budget.          |
| `msg-005` | Malformed output         | Mark validation failure; do not silently accept it. |


These are illustrative outcomes for the exercise, not model predictions.

<br/>

### Practice extensions

-   Shuffle result order and confirm reconciliation still works.
-   Add an unknown or duplicate result ID and make the reconciliation
    stage reject it.
-   Simulate a job timeout after submission and define how to avoid
    duplicate submission.
-   Add a maximum retry count and retry backoff.
-   Compare the workflow's delayed completion requirements with a
    user-facing latency target.


<br/>


## 10. Checkpoint: what depends on the provider's batch API?

The **provider-specific** parts include whether batch jobs exist,
supported models and endpoints, input-file format, submission method,
job ID format, status names, polling or webhook support, completion
windows, result/error formats, result ordering guarantees, cancellation
availability, per-job limits, quotas, and pricing.

The **application-owned** responsibilities include validating inputs,
assigning stable IDs, persisting job state, reconciling results by
identifier, validating outputs, classifying failures, deciding retry
eligibility, enforcing privacy and authorization, and reporting partial
completion.

**Checkpoint answer:** Do not design around assumed batch API behavior.
Confirm the provider's documented contract, then place it behind an
adapter so provider-specific submission, status, result, and
cancellation behavior does not leak throughout the application.

<br/>

## 11. Key takeaways

-   Provider-managed batch jobs and bounded concurrent requests are
    different execution models.
-   Batch is best suited to workloads that can tolerate delayed results.
-   Validate records and assign stable IDs before submission.
-   Persist provider job identifiers and track lifecycle state.
-   Match results by identifier; never assume order is preserved unless
    the provider explicitly guarantees it.
-   Treat job-level completion and per-item success as separate
    concepts.
-   Retry only eligible failures with limits and backoff.
-   Verify provider-specific limits, statuses, output formats,
    cancellation, and pricing in current documentation.

<br/>

## References

-   OpenAI API documentation --- Batch API:
    https://platform.openai.com/docs/guides/batch
-   OpenAI API reference --- Batches:
    https://platform.openai.com/docs/api-reference/batch
-   OpenAI Python SDK: https://github.com/openai/openai-python

The links above are provider-specific reference examples. For another
provider, consult its current batch API documentation and use the
corresponding contract rather than assuming equivalent behavior.
