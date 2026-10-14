# Chapter 17: Optimization from Measured Trade-offs

## Learning Objectives

By the end of this chapter, you should be able to:

-   Select one diagnosed quality, latency, or cost issue and formulate a
    testable optimization hypothesis.
-   Compare prompt simplification, model selection, context selection,
    retrieval tuning, and output budgets.
-   Evaluate batching, concurrency, and caching with correctness,
    privacy, and isolation safeguards.
-   Compare quality, latency, reliability, and cost instead of
    optimizing a single metric blindly.
-   Re-evaluate after each meaningful change and preserve unsuccessful
    experiments.
-   Justify an optimization using measured benefits and acceptable
    regressions.

<br/>

## 1. Optimization Starts with a Measured Problem

Optimization is not simply making prompts shorter, choosing a smaller
model, reducing retrieval depth, or adding a cache. Each intervention
can improve one dimension while damaging another.

Start with a specific, observed problem:

-   **Quality:** unsupported claims, incomplete answers, schema
    failures, weak retrieval, or poor performance in a particular slice.
-   **Latency:** slow time to first token, long end-to-end duration,
    expensive retrieval, retries, or queueing.
-   **Cost:** high input/output token usage, excessive
    retrieval/reranking, repeated requests, or expensive model
    selection.
-   **Reliability:** provider errors, timeouts, inconsistent results, or
    failures under concurrency.

A useful optimization statement contains four parts:

1.  **Observed issue:** a measurable symptom.
2.  **Hypothesis:** a plausible mechanism that explains it.
3.  **Intervention:** one targeted change.
4.  **Success and guardrail metrics:** what should improve and what must
    not degrade.

<br/>

### Example hypothesis

> Observed issue: median latency is acceptable, but p95 latency is too
> high for long-context policy questions. Hypothesis: assembling and
> sending redundant context increases prompt processing time.
> Intervention: remove near-duplicate passages while preserving required
> evidence and source metadata. Success metric: lower p95 end-to-end
> latency. Guardrails: no material decrease in grounded-answer pass
> rate, citation support, or critical-case success.

This is a hypothesis to test, not a guaranteed explanation. Measure the
relevant stages before selecting the intervention.

<br/>

## 2. Establish an Unchanged Baseline

Before changing the system, capture a baseline under a defined workload.

Record:

-   Dataset version and exact case IDs.
-   Prompt, model, schema, retrieval, and tool configuration.
-   Code/dependency versions and runtime environment.
-   Concurrency, arrival pattern, timeout, retry, fallback, and cache
    policy.
-   Task-quality metrics and critical-case outcomes.
-   End-to-end and stage-level latency, including p50/p95 where
    appropriate.
-   Input/output tokens, cost calculation assumptions, and failure
    counts.
-   Raw outputs and per-case results.
-   Known limitations and missing telemetry.

The baseline should be immutable for the comparison. Do not update the
baseline configuration in place after an experiment; create a new
version or run ID.

<br/>

### Comparison principle

Run baseline and candidate on matched cases and equivalent workload
conditions whenever possible. If the candidate uses a different
denominator because of timeouts or missing outputs, explain that
difference rather than comparing percentages without qualification.

For latency, ensure the measurement boundary is identical. For cost, use
the same rate card and accounting rules. For quality, keep the evaluator
and label version fixed.

<br/>

## 3. Define the Optimization Objective

GenAI systems have multiple objectives. Common dimensions include:

-   Task correctness and completeness.
-   Faithfulness or groundedness.
-   Schema and business-rule validity.
-   Critical-case and subgroup performance.
-   Latency and throughput.
-   Token usage and monetary cost.
-   Reliability, availability, and recovery behavior.
-   Privacy, security, and policy compliance.

A change is useful only if it improves the intended objective while
remaining within acceptable limits on the other dimensions.

<br/>

### Guardrail-first optimization

Define non-negotiable constraints before testing:

-   Critical security and privacy behavior must not regress.
-   Required schema and business rules must continue to pass.
-   High-consequence cases must meet the declared gate.
-   Quality must remain above the minimum acceptable threshold.
-   Latency and cost must fit product budgets.
-   Access controls and tenant isolation must remain intact.

A faster system that returns materially worse answers may not be an
optimization. A cheaper system that leaks restricted context is
unacceptable regardless of the savings.

<br/>

## 4. Compare Candidate Optimization Levers

Use the diagnosed mechanism to select the intervention. The table
summarizes common levers and the measurements needed to assess them.

| Lever                 | Potential benefit                                                   | Main risk                                            | Evidence to collect                                                       |
| --------------------- | ------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------- |
| Prompt simplification | Fewer input tokens, clearer instructions, less conflicting guidance | Removes essential constraints or examples            | Input tokens, quality rubric, critical cases, output behavior             |
| Model choice          | Lower cost/latency or better task performance                       | Quality, language, tool, or format regressions       | Matched quality results, latency, cost, capability tests                  |
| Context selection     | Less prompt processing and less irrelevant evidence                 | Drops qualifiers, exceptions, or necessary sources   | Context tokens, evidence coverage, groundedness, citation support         |
| Retrieval tuning      | Better evidence ranking or fewer irrelevant passages                | Misses required evidence or adds noise               | Recall\@k, nDCG/MRR where relevant, context quality, final answer quality |
| Output budget         | Lower generation time and output cost                               | Truncation, incomplete answers, invalid structure    | Output tokens, truncation rate, completeness, schema validity             |
| Batching              | Better utilization and throughput                                   | Queueing delay, failure blast radius, request mixing | Throughput, p95 latency, queue time, isolation tests                      |
| Concurrency           | More parallel work and potentially higher throughput                | Rate limits, contention, retries, tail latency       | Throughput, error rate, p95/p99, provider limits                          |
| Caching               | Avoid repeated computation and latency                              | Stale results, wrong cache keys, privacy leakage     | Hit rate, freshness, key isolation, quality, latency, cost                |


<br/>

### 4.1 Prompt simplification

Simplify prompts when the current prompt is demonstrably redundant,
contradictory, or unnecessarily verbose.

Test whether the revised prompt preserves:

-   Task intent and constraints.
-   Required evidence use and citation behavior.
-   Refusal, clarification, and abstention behavior.
-   Structured-output requirements.
-   Critical examples and edge cases.

Do not remove instructions merely because they consume tokens. First
identify which parts are redundant and verify that the prompt still
expresses the required behavior.

<br/>

### 4.2 Model choice

A smaller or cheaper model may be adequate for a subset of tasks, but
model choice must be evaluated on the target workload.

Compare:

-   Task-specific quality and high-severity failures.
-   Language, source-type, and task slices.
-   Structured output and tool use.
-   Latency and cost at the intended concurrency.
-   Reliability, context limits, and provider behavior.

If using a routing strategy, evaluate both the router and the end-to-end
system. A router can reduce cost while sending difficult cases to an
unsuitable model.

<br/>

### 4.3 Context selection

Reduce context when it contains duplicates, irrelevant passages, or
unnecessary boilerplate. Preserve information that changes the meaning
of the evidence, such as dates, exceptions, qualifiers, source identity,
and conflicting statements.

Evaluate both retrieval and the exact context delivered to the model. A
reduction in token count is not sufficient evidence of success if
groundedness or answer completeness falls.

<br/>

### 4.4 Retrieval tuning

Tune chunking, filters, top-*k*, query rewriting, lexical/dense hybrid
weights, or reranking when retrieval metrics or case traces identify a
retrieval problem.

Measure retrieval quality separately from final answer quality.
Increasing top-*k* can improve evidence recall but may add noise, cost,
and latency. Lowering top-*k* can make context shorter while omitting
essential evidence.

<br/>

### 4.5 Output budgets

A lower output-token limit can reduce cost and generation time, but it
can truncate answers or structured data.

Test:

-   Completeness on long and multi-part questions.
-   JSON/schema validity near the limit.
-   Citation completion.
-   Refusal and clarification behavior.
-   Truncation and finish-reason metadata where available.

Set budgets based on task requirements and observed output
distributions, not on a single average response.

<br/>

## 5. Batching, Concurrency, and Caching

These operational techniques can improve resource utilization, but they
change execution behavior and require explicit safeguards.

### 5.1 Batching

Batching combines multiple items into a shared request or processing
unit when the service supports it.

Potential benefits: - Reduced per-request overhead. - Higher
throughput. - More efficient hardware or provider utilization.

Potential risks: - Waiting for a batch to fill increases latency. - One
malformed item can complicate batch handling. - Results can be
misassociated with the wrong case. - Mixed sensitivity levels can create
inappropriate data exposure if isolation is weak.

Evaluate throughput and tail latency together. Test partial failures,
batch boundaries, and result-to-case mapping.

<br/>

### 5.2 Concurrency

Concurrency allows independent work to execute in parallel.

Potential benefits: - Better utilization while requests wait on I/O. -
Higher throughput under an appropriate workload.

Potential risks: - Provider rate limits and throttling. - Resource
contention and queue growth. - Increased p95/p99 latency under
saturation. - Duplicate side effects if retries are not idempotent. -
Cross-request state or context leakage in poorly isolated
implementations.

Increase concurrency gradually under a representative load test. Monitor
throughput, error rate, queue time, latency percentiles, and retry
behavior. Do not assume that maximum concurrency yields maximum goodput.

<br/>

### 5.3 Caching

Caching avoids repeating work for equivalent requests or intermediate
results.

Potential benefits: - Lower latency. - Reduced provider calls and
cost. - Reuse of expensive retrieval, embedding, or computation results.

Potential risks: - Stale answers after source or index updates. -
Incorrect cache keys that merge semantically different requests. -
User-specific data returned to another user or tenant. - Reuse across
different model, prompt, tool, or permission versions. - Cache poisoning
or untrusted content being reused.

A cache key should reflect every factor that materially changes the
result, which may include tenant/permission scope, normalized input,
prompt version, model version, retrieval index version, tool
configuration, and relevant parameters. Never share a cached result
across authorization boundaries merely because the text of the query
matches.

Define freshness and invalidation rules. Test cache hits and misses
separately, and verify that cached and uncached outputs satisfy the same
correctness and isolation requirements.

<br/>

## 6. A Controlled Optimization Workflow

``` mermaid
flowchart TD
    A[Measure baseline] --> B[Diagnose one issue]
    B --> C[Write a testable hypothesis]
    C --> D[Choose one targeted intervention]
    D --> E[Run matched comparison]
    E --> F[Measure quality, latency, cost, reliability]
    F --> G{Benefit meets target and guardrails pass?}
    G -- Yes --> H[Record and retain change]
    G -- No --> I[Reject, revise, or investigate]
    H --> J[Add regression tests]
    I --> K[Record unsuccessful experiment]
```

Recommended sequence:

1.  Select one diagnosed issue.
2.  Identify the stage and likely mechanism using traces or case-level
    evidence.
3.  State a falsifiable hypothesis.
4.  Define the primary metric, guardrails, sample, and decision rule.
5.  Change one major factor where practical.
6.  Evaluate on matched cases and equivalent workload.
7.  Review aggregate metrics, case-level regressions, critical cases,
    and relevant slices.
8.  Record the result, including unsuccessful experiments.
9.  Keep the change only if the measured benefit justifies the
    trade-offs.
10. Add or update regression tests so the improvement is not
    accidentally lost.

If multiple components must change together, document that the
experiment estimates their combined effect. Do not claim that one
component caused the improvement without a design that supports that
conclusion.

<br/>

## 7. Quantify the Trade-off

Report both absolute and relative changes, with units and a consistent
direction convention.

For a metric where higher is better:

$$
\Delta_{\text{absolute}} = M_{\text{candidate}} - M_{\text{baseline}}
$$

For a positive baseline metric where relative change is meaningful:

$$
\Delta_{\text{relative}} =
\frac{M_{\text{candidate}} - M_{\text{baseline}}}
{M_{\text{baseline}}}\times 100\\%
$$

For latency and cost, lower is usually better, so explicitly state the
direction rather than interpreting a negative change as a failure.

Example with hypothetical values:

| Metric                    | Baseline | Candidate | Interpretation          |
| ------------------------- | -------- | --------- | ----------------------- |
| Grounded-answer pass rate | 88%      | 87%       | Down 1 percentage point |
| p95 latency               | 4.0 s    | 3.0 s     | Down 25%                |
| Cost per 1,000 requests   | $8.00    | $6.40     | Down 20%                |
| Critical-case failures    | 0        | 1         | New critical regression |

Although latency and cost improve, the new critical-case failure may
invalidate the candidate under the release policy. Do not average
incompatible metrics into one score unless the weighting and constraints
are justified and explicitly documented.

<br/>

### Distinguish percentage points from percent

A pass rate changing from 80% to 84% is an increase of 4 percentage
points and a relative increase of 5%. Reports should use the correct
term.

<br/>

## 8. Pareto Trade-offs and Constraints

A candidate is **Pareto-dominated** if another candidate is at least as
good on every relevant objective and strictly better on at least one,
with the same constraints and evaluation basis.

For example, if Candidate A is slower and more expensive than Candidate
B while offering no quality or reliability benefit, A is dominated. If
one candidate is faster but slightly less accurate, neither necessarily
dominates the other; the choice depends on product constraints and the
cost of errors.

<br/>

### A practical selection process

1.  Eliminate candidates that violate critical security, safety,
    privacy, or correctness gates.
2.  Eliminate candidates that exceed hard latency or cost budgets.
3.  Compare remaining candidates on task quality, reliability, latency,
    and cost.
4.  Inspect important subgroup and critical-case behavior.
5.  Choose the candidate that best fits the declared product objective.
6.  Record the trade-off and why it is acceptable.

The fastest or cheapest configuration is not automatically the best.
Optimization should improve the product outcome, not a single isolated
metric.

<br/>

## 9. Record Failed Experiments

An unsuccessful experiment is useful evidence if its setup and result
are preserved.

Record:

-   Hypothesis and motivation.
-   Baseline run and candidate run IDs.
-   Exact configuration differences.
-   Dataset and case IDs.
-   Metrics, uncertainty, and failure counts.
-   Unexpected regressions and affected slices.
-   Why the intervention was rejected or inconclusive.
-   Follow-up hypothesis or next action.

Examples of useful negative findings:

-   Reducing top-*k* lowered latency but caused missing evidence on
    exception cases.
-   Shortening the prompt reduced input tokens but increased invalid
    structured outputs.
-   Raising concurrency increased throughput until rate limits caused
    retries and worse tail latency.
-   Caching reduced average latency but failed freshness requirements
    after corpus updates.

Do not discard failed experiments from the record. Without them, teams
may repeat the same ineffective change or overstate how systematically
the final configuration was selected.

<br/>

## 10. Python: Compare a Baseline and Candidate

This illustrative function summarizes quality, p95 latency, cost per
request, and critical failures. It uses explicit guardrails instead of
collapsing all metrics into one weighted score.

``` python
from dataclasses import dataclass


@dataclass
class RunSummary:
    name: str
    quality_pass_rate: float   # fraction from 0.0 to 1.0
    p95_latency_seconds: float
    cost_per_request: float
    critical_failures: int


def compare_runs(
    baseline: RunSummary,
    candidate: RunSummary,
    min_quality: float,
    max_p95_latency: float,
    max_cost_per_request: float,
) -> dict:
    """Illustrative gate-based comparison; values must use matched workloads."""
    checks = {
        "quality_meets_minimum":
            candidate.quality_pass_rate >= min_quality,
        "latency_meets_budget":
            candidate.p95_latency_seconds <= max_p95_latency,
        "cost_meets_budget":
            candidate.cost_per_request <= max_cost_per_request,
        "no_new_critical_failures":
            candidate.critical_failures <= baseline.critical_failures,
    }

    return {
        "baseline": baseline.name,
        "candidate": candidate.name,
        "quality_delta_percentage_points":
            100 * (
                candidate.quality_pass_rate - baseline.quality_pass_rate
            ),
        "p95_latency_change_percent": (
            100 * (
                candidate.p95_latency_seconds
                - baseline.p95_latency_seconds
            ) / baseline.p95_latency_seconds
            if baseline.p95_latency_seconds > 0 else None
        ),
        "cost_change_percent": (
            100 * (
                candidate.cost_per_request
                - baseline.cost_per_request
            ) / baseline.cost_per_request
            if baseline.cost_per_request > 0 else None
        ),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


baseline = RunSummary(
    name="baseline-v1",
    quality_pass_rate=0.88,
    p95_latency_seconds=4.0,
    cost_per_request=0.008,
    critical_failures=0,
)

candidate = RunSummary(
    name="candidate-v2",
    quality_pass_rate=0.87,
    p95_latency_seconds=3.0,
    cost_per_request=0.0064,
    critical_failures=1,
)

print(compare_runs(
    baseline,
    candidate,
    min_quality=0.86,
    max_p95_latency=3.5,
    max_cost_per_request=0.007,
))
```

**Limitations:** The example assumes inputs are already valid, measured
consistently, and comparable. It does not calculate confidence
intervals, validate sample sizes, compare slices, or define whether a
critical failure is new versus pre-existing by case ID. A production
gate should inspect case-level outcomes, run validity, uncertainty, and
explicit release policy in addition to these summary checks.

<br/>

## 11. Practice: Make One Targeted Optimization

### Scenario

A RAG application has the following baseline results on a matched
workload:

-   Grounded-answer pass rate: 90%.
-   p95 latency: 4.8 seconds.
-   Cost per 1,000 requests: \$10.00.
-   Critical-case failures: 0.
-   Analysis shows many requests include near-duplicate passages in the
    assembled context.

The team proposes deduplicating near-identical passages while preserving
source identifiers and qualifiers.

After the change, the candidate results are:

-   Grounded-answer pass rate: 89.5%.
-   p95 latency: 3.6 seconds.
-   Cost per 1,000 requests: \$8.50.
-   Critical-case failures: 0.
-   The candidate has one regression on a mixed-language case; all other
    tested cases are unchanged or improved.

These values are hypothetical.

<br/>

### Tasks

1.  State the optimization hypothesis.
2.  Calculate the relative p95 latency reduction and cost reduction.
3.  State the quality difference in percentage points.
4.  Decide what additional evidence is needed before accepting the
    candidate.
5.  Propose regression checks for mixed-language and exception cases.
6.  Write a concise decision explaining whether to retain, revise, or
    reject the change.

<br/>

## 12. Answer Key

### 1. Hypothesis

Near-duplicate passages increase context length and processing cost
without adding useful evidence. Deduplicating them while preserving
source identity and qualifiers should reduce p95 latency and cost
without materially reducing grounded-answer quality.

<br/>

### 2. Resource changes

Latency reduction:

$$
\frac{4.8 - 3.6}{4.8}\times100\\% = 25\\%
$$

Cost reduction:

$$
\frac{10.00 - 8.50}{10.00}\times100\\% = 15\\%
$$

<br/>

### 3. Quality difference

The pass rate changes from 90% to 89.5%, a decrease of 0.5 percentage
points. This is the observed difference; whether it is acceptable
depends on sample size, uncertainty, guardrails, and the product's
quality requirements.

<br/>

### 4. Additional evidence

-   Number of matched cases and uncertainty for the quality difference.
-   The exact mixed-language regression and its severity.
-   Evidence that deduplication preserved qualifiers, source IDs, and
    conflicting evidence.
-   Retrieval and context traces for affected cases.
-   Performance under the same workload and measurement boundary.
-   Critical-case and subgroup results, especially exception and
    multilingual cases.

<br/>

### 5. Regression checks

Keep the mixed-language regression as a permanent test. Add cases where
repeated-looking passages differ in dates, exceptions, scope, or source
authority. Verify that deduplication does not merge distinct evidence or
remove citations. Check groundedness, answer completeness, and source
attribution.

<br/>

### 6. Example decision

> The change reduces p95 latency by 25% and cost per 1,000 requests by
> 15%, with an observed 0.5-percentage-point decrease in grounded-answer
> pass rate and no critical-case failures in this run. The resource
> gains are promising, but the mixed-language regression must be
> inspected and the quality difference assessed with its sample size and
> uncertainty. Retain the candidate only if the regression is understood
> and the predefined quality and subgroup guardrails pass; otherwise
> revise deduplication and rerun the matched regression suite.

<br/>

## 13. Checkpoint: Justify the Change

**Checkpoint prompt:** Justify the optimization using measured benefit
and acceptable regressions.

A strong answer should include:

-   The diagnosed issue and evidence supporting it.
-   The hypothesis and exact intervention.
-   Baseline and candidate run IDs and matched workload.
-   Quality, latency, cost, and reliability results.
-   Critical-case and subgroup outcomes.
-   Uncertainty and sample-size limitations.
-   Regression guardrails and release decision.
-   Unsuccessful experiments and follow-up work.

<br/>

### Model checkpoint answer

I would retain an optimization only when its measured benefit addresses
a diagnosed problem and its regressions remain within predefined limits.
I would compare baseline and candidate on matched cases under equivalent
workload conditions, report quality differences with uncertainty, and
measure latency, cost, reliability, and critical-case behavior. A
reduction in latency or cost does not justify a new critical failure or
an unacceptable subgroup regression. I would document the exact
configuration change, preserve the per-case evidence, add the relevant
cases to regression testing, and record the decision---including a
rejection if the guardrails are not met.

<br/>

## Key Takeaways

-   Start with a measured problem and a falsifiable hypothesis.
-   Change one major factor at a time when attribution matters.
-   Compare on matched cases and equivalent workload conditions.
-   Evaluate prompt, model, context, retrieval, output budget, batching,
    concurrency, and caching as distinct levers.
-   Protect correctness, privacy, security, and critical-case behavior
    with explicit guardrails.
-   Consider quality, latency, cost, reliability, and coverage together.
-   Keep failed experiments in the record and add discovered regressions
    to the test suite.
-   Accept a change based on measured benefits and acceptable
    trade-offs, not intuition or a single improved metric.

<br/>

## Further Reading

-   [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) ---
    preserve experiment parameters, metrics, and artifacts.
-   [OpenTelemetry Documentation](https://opentelemetry.io/docs/) ---
    measure stage-level latency and service behavior.
-   [scikit-learn: Model
    Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
    --- compare task metrics and evaluation methods.
-   [DVC Documentation](https://dvc.org/doc) --- version data and
    reproducible pipelines.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- incorporate risk into system evaluation and governance.


<br/>


**Chapter 17 complete.** The next chapter is **Evaluation Gates in
CI/CD**.
