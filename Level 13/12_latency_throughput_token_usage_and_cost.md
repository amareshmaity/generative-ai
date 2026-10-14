# 12. Latency, Throughput, Token Usage, and Cost

## Learning Objectives

By the end of this chapter, you should be able to:

-   Measure end-to-end and stage latency, distinguishing time to first
    token from completion time.
-   Report latency percentiles with workload, sample count, and
    concurrency.
-   Track input/output token usage, retries, cache behavior, and missing
    usage fields.
-   Separate provider-reported measurements from local estimates.
-   Calculate cost using verified rates and explicit accounting
    assumptions.
-   Compare quality and reliability under the same workload, not speed
    alone.

<br/>

## 1. Why Operational Evaluation Matters

A GenAI application can produce high-quality answers but still be
unsuitable for production if it is too slow, unreliable, expensive, or
unstable under concurrent traffic. Performance evaluation should measure
quality and operational behavior together.

Important dimensions include latency, time to first token (TTFT),
completion time, throughput, token usage, cost, reliability, and task
quality. A performance comparison is meaningful only when the workload
and measurement rules are comparable.

<br/>

## 2. Latency: End-to-End and Stage-Level

### End-to-end latency

End-to-end latency is the elapsed time from the defined start of a user
request to the defined completion point. For a streaming interface,
completion usually means the final response event or end-of-stream, not
the first token.

Depending on the application, it may include request validation, query
rewriting, retrieval, reranking, prompt assembly, provider
request/response, tool calls, retries, post-processing, schema
validation, and serialization. State explicitly if any stage is
excluded.

<br/>

### Stage latency

Instrument individual stages to identify bottlenecks.

| Stage            | Start/end definition                           | Example measurement |
| ---------------- | ---------------------------------------------- | ------------------- |
| Retrieval        | Retriever invocation to ranked results         | 45 ms               |
| Reranking        | Reranker invocation to reordered list          | 70 ms               |
| Model TTFT       | Provider request start to first token received | 620 ms              |
| Model completion | Provider request start to final token received | 2,400 ms            |
| Validation       | Parsed output to validation result             | 8 ms                |
| End-to-end       | User request start to completed response       | 2,650 ms            |


These numbers are illustrative. Stage times may overlap or exclude
orchestration overhead, so do not simply add them unless instrumentation
confirms that they are sequential and cover the same interval.

<br/>

### Time to first token versus completion time

-   **TTFT** measures how soon a streaming request produces its first
    visible output token.
-   **Completion time** measures how long until the full response is
    available.
-   **Inter-token latency** or token-generation rate may help diagnose
    streaming smoothness.

A system can have low TTFT but long completion time if it generates many
tokens slowly. For non-streaming requests, TTFT may be unavailable or
not meaningful; record `N/A`, not zero.

<br/>

## 3. Percentiles, Sample Count, and Concurrency

Average latency can hide slow outliers. Report p50, p90, p95, and p99
when sample sizes support meaningful estimates.

-   **p50 (median):** Half of measured requests complete at or below
    this latency.
-   **p90:** 90% complete at or below this latency.
-   **p95:** 95% complete at or below this latency.
-   **p99:** 99% complete at or below this latency.

Always record the number of assigned requests and successful
measurements, failures and timeouts, concurrency and request arrival
pattern, warm-up/cold-start policy, model/provider/region,
input/output-length distributions, streaming mode, cache state, retry
policy, measurement tool, and percentile calculation method.

Very small samples cannot support precise tail-percentile claims. A p99
estimate from only 20 requests is especially unstable; report sample
counts and avoid overstating precision.

<br/>

## 4. Throughput and Concurrency

Throughput measures work completed per unit of time. Depending on the
system, report request throughput, token throughput, and
**goodput**---successful requests that meet quality and latency
requirements per unit of time.

$$
\text{Request Throughput} =
\frac{\text{Successful completed requests}}
{\text{Measurement window in seconds}}
$$

Be explicit about whether failures count toward the numerator. Report
successful throughput and failure rate separately.

Concurrency is the number of requests in flight at the same time.
Increasing concurrency can increase throughput up to a limit, but may
also increase queueing, latency, timeouts, rate-limit errors, and
retries. Compare systems at the same concurrency and arrival pattern, or
present a load curve across multiple concurrency levels. A
single-request test does not establish performance under concurrent
production traffic.

<br/>

## 5. Token Usage and Cache Behavior

Track token usage per request whenever available:

-   Input/prompt tokens.
-   Output/completion tokens.
-   Cached input tokens or cache-read tokens.
-   Cache-write tokens, if charged or reported.
-   Tool-call and auxiliary usage categories, if applicable.
-   Total tokens as defined by the provider.

Token categories differ across providers. Some report cached tokens as a
subset of input tokens; others report them separately. Define the
accounting rule to avoid double-counting.

<br/>

### Missing usage fields

Usage may be missing when a request fails before usage is returned,
streaming usage is not requested or included, the provider/SDK does not
expose a field, or a timeout occurs before completion.

Represent missing usage as `unknown` or `null`, and record why it is
missing. Do not replace missing usage with zero: a request with unknown
usage did not necessarily consume zero tokens.

<br/>

### Cache behavior

Record whether prompt caching or response caching was active, whether
the request was a cache hit, and which token categories were billed.
Compare warm-cache and cold-cache behavior separately when caching
materially affects latency or cost. If cache conditions differ, report
that difference as part of the experiment.

<br/>

## 6. Provider-Reported Values Versus Local Estimates

| Measurement              | Possible source                                     | Interpretation                                                          |
| ------------------------ | --------------------------------------------------- | ----------------------------------------------------------------------- |
| Input/output token usage | Provider response usage fields                      | Provider-reported count under its accounting rules                      |
| Charged amount           | Provider invoice or billing record                  | Strongest source for actual billed cost, subject to billing granularity |
| Estimated token count    | Local tokenizer                                     | Estimate; may differ from provider tokenization                         |
| End-to-end latency       | Local monotonic clock around application request    | Includes the measured client/application path                           |
| Provider latency         | Provider telemetry or response metadata, if exposed | Covers only the provider-defined interval                               |
| Throughput               | Load-test harness                                   | Depends on workload and success definition                              |
| Cost estimate            | Local calculation from a rate card                  | Estimate, not an invoice                                                |


Use a monotonic clock for elapsed-time measurements. Keep units
consistent and label each field's source, for example
`provider_reported`, `locally_measured`, `locally_estimated`, or
`billing_confirmed`.

<br/>

## 7. Cost Calculation

Cost depends on verified provider rates and the token categories to
which those rates apply. Rates may vary by model, region, service tier,
batch mode, cache status, or effective date. Verify the applicable rate
card at the time of the experiment.

If rates are stated per one million tokens:

$$
\text{Estimated Cost} =
\frac{T_{\text{input}}}{1{,}000{,}000} R_{\text{input}}
+
\frac{T_{\text{output}}}{1{,}000{,}000} R_{\text{output}}
$$

Here, $T_{\text{input}}$ and $T_{\text{output}}$ are billable token
counts, and $R_{\text{input}}$ and $R_{\text{output}}$ are verified
rates per million tokens.

If cached input tokens have a different rate, split them out and apply
the correct rate. Add tool, image/audio/video, storage, or other charges
only when applicable and rates are known.

### Example

Assume a hypothetical, verified rate card for a tested configuration
states: - Input: \$2.00 per million billable tokens. - Output: \$8.00
per million billable tokens.

For 10,000 input tokens and 2,000 output tokens:

$$
\text{Input Cost} = \frac{10{,}000}{1{,}000{,}000} \times \$2.00 = \$0.02
$$

$$
\text{Output Cost} = \frac{2{,}000}{1{,}000{,}000} \times \$8.00 = \$0.016
$$

$$
\text{Estimated Total} = \$0.036
$$

The rates are hypothetical and must not be treated as current prices for
any provider. In a real report, cite or archive the actual rate card and
record its effective date.

Document whether retries and failed requests are included, how cached
tokens are billed, whether tools or modalities incur extra charges,
whether taxes/discounts/fees are included, whether the figure is
estimated or billing-confirmed, and any currency conversion assumptions.

Report average and distribution of cost per request, and consider cost
per successful, quality-passing answer. A cheap response that fails the
task may be less efficient than a more expensive response that succeeds
reliably.

<br/>

## 8. Reliability and Quality Under the Same Workload

For each configuration, measure the same representative workload and
report quality metrics, end-to-end latency, TTFT where relevant,
throughput at defined concurrency, token usage, cost,
success/timeout/refusal/invalid-output rates, retries, cache state, and
missing measurements.

The workload should use the same query set, context, output
requirements, concurrency pattern, timeout policy, and measurement
boundaries unless a difference is an intentional part of the experiment.
Randomized or interleaved runs can reduce the influence of changing
provider load or time-of-day effects.

$$
\text{Goodput} =
\frac{\text{Requests passing quality and latency gates}}
{\text{Measurement window}}
$$

This is meaningful only if the gates are explicit and identical across
candidates. Report component metrics too; a composite measure can hide
why a system performed poorly.

<br/>

## 9. Worked Measurement Table: Two Configurations

Suppose Configuration A and Configuration B are tested with the same
100-request workload at concurrency 10. Values below are illustrative,
not measured results.

| Metric                 | Configuration A | Configuration B | Measurement status / notes                              |
| ---------------------- | --------------- | --------------- | ------------------------------------------------------- |
| Assigned requests      | 100             | 100             | Same workload                                           |
| Successful completions | 96              | 98              | Local harness                                           |
| Timeouts               | 3               | 1               | Local harness                                           |
| Other failures         | 1               | 1               | Local harness                                           |
| End-to-end latency p50 | 1.8 s           | 1.6 s           | Successful requests only; failures reported separately  |
| End-to-end latency p95 | 4.9 s           | 4.2 s           | Successful requests only                                |
| TTFT p50               | 0.7 s           | 0.6 s           | Streaming requests                                      |
| TTFT p95               | 1.8 s           | N/A             | B's TTFT telemetry unavailable; not zero                |
| Input tokens, mean     | 2,400           | 2,350           | Provider-reported for successful responses only         |
| Output tokens, mean    | 520             | 480             | Provider-reported for successful responses only         |
| Usage missing          | 4 requests      | 2 requests      | Reported separately; may overlap with failures          |
| Retry rate             | 8%              | 3%              | Application logs                                        |
| Cache-hit rate         | 20%             | 18%             | Same cache policy; actual state varied                  |
| Estimated cost/request | $0.006          | $0.0055         | Illustrative rate card; excludes unknown-usage requests |
| Task quality pass rate | 88%             | 91%             | Review method and sample size must be reported          |
| Successful throughput  | 0.80 req/s      | 0.82 req/s      | Depends on actual measurement-window duration           |


Interpretation: - B appears faster and has fewer timeouts in this
illustrative run. - B's p95 TTFT is unavailable, so a full TTFT
percentile comparison cannot be made. - Cost estimates exclude requests
with missing usage, so they are conditional and may understate
end-to-end cost. - Quality pass rates should not be compared confidently
without sample sizes, review method, and uncertainty. - The table alone
does not establish production readiness.

Do not copy these illustrative values into a real benchmark report as
measured results.

<br/>

## 10. Python Example: Summarize Local Latency Measurements

This example uses local measurements in milliseconds. It excludes
unavailable observations from latency percentiles while preserving their
count.

``` python
def percentile_nearest_rank(values, p):
    # Nearest-rank percentile for 0 < p <= 1.
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, int(p * len(ordered) + 0.999999))
    return ordered[rank - 1]

def summarize_latency(samples_ms):
    measured = [value for value in samples_ms if value is not None]
    missing = len(samples_ms) - len(measured)

    return {
        "assigned_samples": len(samples_ms),
        "measured_samples": len(measured),
        "missing_samples": missing,
        "p50_ms": percentile_nearest_rank(measured, 0.50),
        "p95_ms": percentile_nearest_rank(measured, 0.95),
        "p99_ms": percentile_nearest_rank(measured, 0.99),
        "mean_ms": sum(measured) / len(measured) if measured else None,
    }

config_a = [820, 910, 1100, 1400, 1700, 2100, None, 2600]
config_b = [780, 850, 1000, 1250, 1500, 1900, 2300, None]

print("A:", summarize_latency(config_a))
print("B:", summarize_latency(config_b))
```

Important: - This uses nearest-rank percentiles; other tools may use
different interpolation conventions. - Report the method and sample
count. - Missing values remain in the assigned-sample count but are
excluded from the measured latency distribution. - If missing
measurements are caused by timeouts, excluding them can make a system
look faster. Report timeout rates and treat timeouts as failures for
relevant service-level objectives.

<br/>

## 11. Practice: Compare Two Configurations

Both configurations were assigned the same 50 queries at concurrency 5.

| Metric                     | Config A            | Config B            |
| -------------------------- | ------------------- | ------------------- |
| Completed responses        | 48                  | 49                  |
| Timeouts                   | 2                   | 1                   |
| p50 end-to-end latency     | 1.4 s               | 1.3 s               |
| p95 end-to-end latency     | 3.8 s               | 4.1 s               |
| p95 TTFT                   | 0.9 s               | N/A                 |
| Mean input tokens          | 1,800               | 1,750               |
| Mean output tokens         | 400                 | 460                 |
| Usage fields missing       | 1                   | 3                   |
| Quality pass rate          | 90% (n=20 reviewed) | 92% (n=12 reviewed) |
| Estimated cost per request | $0.0040             | $0.0043             |

Tasks: 1. Which configuration has lower p50 latency? Which has lower p95
latency? 2. Can p95 TTFT be compared? 3. Why might Config B's cost
estimate be less certain? 4. Why is it risky to conclude that Config B
has better quality from 92% versus 90% alone? 5. List at least four
conditions that should be checked before making a valid performance
comparison. 6. Propose a measurement table field that would prevent
failures from being silently omitted.

<br/>

### Suggested answers

1.  Config B has lower p50 latency (1.3 s vs 1.4 s). Config A has lower
    p95 latency (3.8 s vs 4.1 s).
2.  No. Config B's p95 TTFT is unavailable. `N/A` is not zero.
3.  Config B has three missing usage records versus one for A. Its
    estimate may exclude more requests and may not represent end-to-end
    cost.
4.  Reviewed sample sizes differ (20 versus 12), and the evaluation
    method and uncertainty are not supplied.
5.  Check workload/query set, concurrency and arrival pattern, provider
    configuration/region, cache policy, timeout/retry policy,
    measurement boundaries, output limits, and usage accounting rules.
6.  Include assigned requests, successful completions, timeouts, other
    failures, and missing-measurement counts.

<br/>

## 12. Checkpoint

**Prompt:** Explain the conditions under which performance comparisons
are valid.

**Model answer:**

Comparisons are valid when candidates are measured on equivalent
workloads with consistent query sets, input/context sizes, output
requirements, concurrency and arrival patterns, timeout and retry
policies, cache conditions, and measurement boundaries. Model/provider
configuration, rate-card version, token accounting rules, percentile
method, sample count, and treatment of failures and missing data must
also be documented. Compare quality and reliability alongside latency,
throughput, usage, and cost. If one configuration has missing telemetry
or a different workload, state the limitation instead of presenting the
results as directly comparable.

<br/>

## 13. Further Reading

-   [OpenTelemetry documentation](https://opentelemetry.io/docs/) ---
    tracing and instrumentation for application stages.
-   [OpenAI API pricing](https://openai.com/api/pricing/) --- verify
    current pricing when using OpenAI APIs; archive rate assumptions for
    each experiment.
-   [Locust documentation](https://docs.locust.io/) --- load testing and
    concurrency-based workload generation.
-   [k6 documentation](https://grafana.com/docs/k6/latest/) --- load
    testing and performance measurement.
-   [LangSmith evaluation
    concepts](https://docs.smith.langchain.com/evaluation) ---
    evaluating application quality alongside system behavior.


<br/>


## Chapter Summary

Operational evaluation must measure latency, throughput, token usage,
cost, reliability, and task quality under a defined workload.
Distinguish TTFT from completion time, report percentiles with sample
counts and concurrency, and label provider-reported values separately
from local estimates. Track failures, retries, cache behavior, and
missing usage explicitly. Calculate costs from verified rates and
documented assumptions. Never claim a performance winner from speed
alone or compare results whose workload, measurement boundaries, or
accounting rules differ.
