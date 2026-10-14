# Chapter 16: Prompt and Model Regression Testing

## Learning Objectives

By the end of this chapter, you should be able to:

-   Maintain a versioned regression suite containing important
    successful cases and known failures.
-   Compare prompt or model changes against a stable baseline using task
    metrics and critical-case checks.
-   Identify changes to prompts, model versions, tokenizers/templates,
    retrieval, and dependencies that require evaluation.
-   Define acceptable variation and review unexpected differences.
-   Separate deterministic software checks from potentially flaky live
    model evaluations.
-   Explain how aggregate improvements can conceal a critical subgroup
    regression.

<br/>

## 1. What Is Regression Testing in a GenAI System?

A regression occurs when a change causes previously acceptable behavior
to become worse. In a Generative AI application, a change can improve
average quality while breaking an important behavior, such as respecting
an access boundary, extracting a required field, or answering correctly
in a particular language.

**Prompt and model regression testing** checks whether a new
configuration preserves required behavior while delivering its intended
changes.

Changes that may trigger regression tests include:

-   System, developer, or task prompt edits.
-   Model ID, provider, snapshot, or routing changes.
-   Tokenizer, chat template, message formatting, or output-token-limit
    changes.
-   Retrieval corpus/index, embedding, chunking, filtering, ranking, or
    reranker changes.
-   Tool schemas, orchestration logic, parsing, validation, and
    retry/fallback changes.
-   Library, SDK, dependency, runtime, and infrastructure changes.
-   Evaluator prompts, rubrics, metric code, or normalization changes.

A regression suite should not only contain cases that previously failed.
It must also preserve **important successful behavior**. Otherwise, a
system can "fix" one failure by breaking behavior that was already
working.

<br/>

## 2. Build a Stable Regression Suite

A useful regression suite is a versioned collection of cases with known
expectations, priorities, and coverage labels.

### 2.1 Sources of regression cases

Include cases from:

-   Representative task examples.
-   Previously successful high-value workflows.
-   Confirmed production incidents and support cases, appropriately
    redacted.
-   Adversarial, boundary, ambiguous, and unsupported inputs.
-   Cases that exposed past prompt or model regressions.
-   Important languages, source types, user workflows, and permission
    boundaries.
-   Structured-output edge cases and tool-call failures.
-   Safety, privacy, security, and other high-consequence scenarios.

Do not build the suite only from recent incidents. A collection of
failures alone cannot measure how often the system breaks previously
successful behavior.

<br/>

### 2.2 What a regression case should contain

A regression case can include:

| Field               | Purpose                                             |
| ------------------- | --------------------------------------------------- |
| `case_id`           | Stable unique identifier                            |
| `case_version`      | Version of the test case                            |
| `task_type`         | Task or workflow being evaluated                    |
| `input_ref`         | Input or controlled reference to it                 |
| `expected_behavior` | Required outcome, acceptable range, or rubric       |
| `criticality`       | Ordinary, high, or critical                         |
| `slice_tags`        | Language, source type, task, permission class, etc. |
| `assertions`        | Deterministic checks and semantic requirements      |
| `baseline_run_id`   | Run used as the comparison baseline                 |
| `owner`             | Team or role responsible for the case               |
| `last_reviewed`     | Date the case and expected behavior were checked    |

For generative outputs, an expected behavior is often better than a
single exact string. Use exact matching for deterministic contracts and
stable outputs; use rubric-based or evidence-based assertions for
open-ended answers.

<br/>

### 2.3 Version the suite

Store the suite version, case IDs, labels/references, rubrics, and
inclusion rules. A changed expected answer can change the evaluation
outcome even when the system output stays the same. Keep the history of
why a case or expected behavior changed.

Cases should be retired only with a documented reason, such as an
obsolete product behavior or a source that is no longer valid. Do not
delete a difficult case merely because the candidate fails it.

<br/>

## 3. Baselines and Comparison Reports

A **baseline** is a versioned reference configuration and its outcomes.
It is not necessarily the oldest version or the current production
model; it should be the comparison target defined by the release
process.

Record at least:

-   Baseline and candidate run IDs.
-   Regression-suite version and exact case IDs.
-   Prompt, model, tokenizer/template, retrieval, schema, and dependency
    versions.
-   Metric code, rubric, and evaluator version.
-   Execution settings, including timeout, retries, cache, and seed
    support.
-   Per-case outputs and statuses.
-   Aggregate metrics and critical-case outcomes.
-   Acceptable-variation thresholds and release decision.

<br/>

### Compare more than one aggregate metric

A regression report should include:

1.  **Overall task quality:** e.g., exact accuracy, grounded-answer pass
    rate, extraction F1.
2.  **Critical-case status:** whether any must-pass assertion failed.
3.  **Slice metrics:** language, task, source type, and other meaningful
    groups.
4.  **Operational behavior:** failures, timeouts, latency, token usage,
    and cost where relevant.
5.  **Output contract:** parse success, schema validity, and
    business-rule compliance.
6.  **Case-level differences:** improved, regressed, unchanged, or
    missing.
7.  **Configuration differences:** what changed between the two runs.

For paired binary outcomes, count transitions:

-   Baseline fail → candidate pass: improvement.
-   Baseline pass → candidate fail: regression.
-   Both pass or both fail: unchanged on the binary metric.

The transition counts are essential because an aggregate score can
conceal a small set of serious regressions.

<br/>

## 4. Critical Cases and Release Gates

Some cases should be designated **must-pass** because failure is
unacceptable or requires explicit risk acceptance. Examples include
permission boundaries, required refusal behavior, valid structured
output for a critical workflow, or a high-consequence policy exception.

Define criticality and gate behavior before inspecting candidate
results.

Example gate policy:

-   Any confirmed critical security or privacy regression: block release
    and investigate.
-   Any failure in a required must-pass case: block or require
    documented, authorized exception.
-   Overall metric drop beyond the agreed tolerance: block or require
    review.
-   Material regression in a protected or operationally important slice:
    investigate and decide using the predefined policy.
-   Small differences within expected noise: report and monitor rather
    than treating them automatically as meaningful.
-   Infrastructure failures or missing results above a defined
    threshold: invalidate or rerun the comparison.

A must-pass list should remain small enough to review carefully, but
broad enough to cover high-consequence behaviors. A green aggregate
score does not override a critical gate.

<br/>

## 5. Define Acceptable Variation

Generative systems can vary between runs, so a regression test needs an
explicit policy for expected variation.

Different assertions require different treatment:

### Deterministic checks

Examples:

-   JSON parses.
-   Required keys exist.
-   A tool result has the required fields.
-   A permission filter excludes a restricted document.
-   A calculation matches a known expected value.
-   An output stays within a hard token or size limit.

These should usually be exact, stable checks when the system contract
supports that expectation.

<br/>

### Semantic checks

Examples:

-   An answer is supported by provided evidence.
-   A summary preserves the essential facts.
-   A response follows the requested task.
-   A citation supports the associated claim.

These may require a rubric, reference-based checks, human review, or a
calibrated judge. Define the pass criteria and evaluator version
explicitly.

<br/>

### Potentially stochastic checks

For an endpoint with variable generation, one output may pass and
another may fail. Decide in advance whether the test policy uses:

-   A fixed supported seed and one run.
-   A specified number of repeats.
-   A pass-rate threshold over repeats.
-   A targeted human review.
-   A separate deterministic contract test plus a live quality
    evaluation.

The correct policy depends on the consequence of failure and the source
of variation. Do not loosen thresholds after observing a bad candidate
result merely to make the release pass.

<br/>

## 6. Separate Deterministic Tests from Live Evaluations

A reliable regression pipeline uses different test layers because not
all checks have the same stability, cost, or diagnostic value.

``` mermaid
flowchart TD
    A[Code or configuration change] --> B[Static checks and unit tests]
    B --> C[Deterministic contract tests]
    C --> D[Offline regression suite]
    D --> E[Live or repeated model evaluation]
    E --> F[Critical-case and slice review]
    F --> G{Release policy satisfied?}
    G -- Yes --> H[Approve with recorded evidence]
    G -- No --> I[Block, investigate, or roll back]
```

<br/>

### Layer 1: Static checks and unit tests

Test code paths without calling a model provider where possible:

-   Schema definitions and configuration validation.
-   Prompt template rendering.
-   Token-budget calculations.
-   Metric and aggregation functions.
-   Retry and timeout policy logic.
-   Access-control filter logic using controlled fixtures.

These tests should be fast and deterministic.

<br/>

### Layer 2: Deterministic contract tests

Use fixed inputs and controlled dependencies to check:

-   Parsing and schema validation.
-   Business rules and required fields.
-   Tool-call argument validation.
-   Permission boundaries.
-   Known deterministic calculations.
-   Error handling for malformed inputs.

Mock external dependencies when the purpose is to test application
logic. Keep separate integration tests for actual provider and tool
behavior.

<br/>

### Layer 3: Offline regression evaluation

Run a versioned set of representative cases and compare per-case and
aggregate outcomes. Store outputs and configuration. Use the same
scoring rules as the baseline.

<br/>

### Layer 4: Live or repeated model evaluation

Use this for behaviors that cannot be adequately tested with mocks, such
as provider integration, current model behavior, or stochastic quality.
It may be slower, costlier, and less stable. Record provider/model
metadata, repeats, errors, and uncertainty.

A live evaluation that fails because of a provider outage is different
from a semantic regression. Classify the failure rather than silently
counting it as either a pass or a model-quality failure.

<br/>

## 7. Test Changes to the Full Application Contract

A prompt or model may appear unchanged while a surrounding component
changes its behavior.

### Prompt changes

Check instruction adherence, answer quality, refusal/clarification
behavior, output format, and critical edge cases.

<br/>

### Model changes

Check task quality, hallucination/groundedness, language and subgroup
performance, latency, token usage, cost, and supported capabilities.

<br/>

### Tokenizer or chat-template changes

Check message boundaries, role formatting, special-token handling,
truncation, token counts, and whether the rendered request matches the
intended template. A template change can alter what the model receives
even if the visible prompt text looks identical.

<br/>

### Retrieval changes

Check index freshness, Recall@k or other retrieval metrics, source
permissions, context assembly, citation support, and final answer
quality. Include cases where the correct answer depends on exceptions,
dates, or conflicting documents.

<br/>

### Dependency or orchestration changes

Check parser behavior, SDK request construction, retry/fallback paths,
tool schema compatibility, error mapping, and telemetry. Keep
infrastructure failures distinguishable from task-quality failures.

<br/>

### Evaluator changes

An updated rubric, judge prompt, model, or metric implementation can
change reported scores without any change to the system being evaluated.
Run evaluator calibration checks and preserve the evaluator version. If
both the candidate system and evaluator change, the result is harder to
interpret; separate the changes where possible.

<br/>

## 8. Slice-Level Regression Detection

Averages can hide regressions concentrated in a subset of cases. Track
slices that reflect real risks or meaningful operating conditions.

Examples:

-   Language and locale.
-   Task type.
-   Source type: scanned PDF, digital PDF, HTML, database, or API.
-   Input length or complexity.
-   High-consequence workflow.
-   Permission class or tenant boundary.
-   Answerable versus unanswerable questions.
-   Tool-required versus no-tool cases.

For each slice, report baseline and candidate denominators, scores,
difference, and important case-level failures. Avoid drawing strong
conclusions from very small slices; mark low coverage and investigate
high-severity examples individually.

<br/>

### Example: aggregate improvement, subgroup regression

All values below are hypothetical.

| Group                      | Baseline | Candidate | Difference             |
| -------------------------- | -------- | --------- | ---------------------- |
| Common English cases (900) | 90%      | 94%       | +4 percentage points   |
| Mixed-language cases (100) | 80%      | 65%       | −15 percentage points  |
| Overall (1,000)            | 89%      | 91.1%     | +2.1 percentage points |

The candidate improves the overall score because the large English slice
dominates the aggregate. But it substantially regresses on
mixed-language cases. If that subgroup is important to the product, the
release decision should consider the regression directly rather than
relying on the overall score.

A slice-level alert is not automatically proof of a systematic cause,
particularly with small samples. It is a signal for investigation, not a
substitute for examining case-level evidence and uncertainty.

<br/>

## 9. Deliberate Regression Exercise

A deliberate regression is a controlled test change intended to verify
that the comparison system can detect a known failure.

Examples:

-   Modify a prompt so it omits a required exception.
-   Remove a required field from a structured-output template.
-   Change a test fixture so a permission filter incorrectly includes a
    restricted document.
-   Alter a parser mapping so one field is assigned to the wrong key.
-   Use a retrieval configuration that drops the passage needed by a
    known test case.

Perform this only in a test branch or isolated environment, using
synthetic or approved test data. Never intentionally weaken a live
security boundary.

<br/>

### What the report should reveal

The regression report should identify:

-   The affected case IDs.
-   The failed assertion or quality criterion.
-   Baseline and candidate outcomes.
-   Any critical gate violation.
-   The affected slice.
-   Whether the aggregate score changed and by how much.
-   The run/configuration identifiers needed to reproduce the result.

If the deliberate regression is not visible, improve the suite,
assertion, slicing, or report before relying on it as a release gate.

<br/>

## 10. Python: Compare Baseline and Candidate Outcomes

This small example compares paired binary outcomes and exposes
regressions, improvements, and must-pass failures. It assumes case IDs
are stable and outcomes are booleans.

``` python
from typing import Any


def compare_regression_runs(
    baseline: list[dict[str, Any]],
    candidate: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare paired pass/fail outcomes by stable case ID."""
    baseline_by_id = {row["case_id"]: row for row in baseline}
    candidate_by_id = {row["case_id"]: row for row in candidate}

    baseline_ids = set(baseline_by_id)
    candidate_ids = set(candidate_by_id)
    if baseline_ids != candidate_ids:
        return {
            "valid_comparison": False,
            "missing_from_candidate": sorted(baseline_ids - candidate_ids),
            "missing_from_baseline": sorted(candidate_ids - baseline_ids),
            "message": "Case populations differ; resolve or document before comparison.",
        }

    improved = []
    regressed = []
    unchanged = []
    critical_failures = []

    for case_id in sorted(baseline_ids):
        old = baseline_by_id[case_id]
        new = candidate_by_id[case_id]

        old_pass = old["passed"]
        new_pass = new["passed"]
        if not isinstance(old_pass, bool) or not isinstance(new_pass, bool):
            raise ValueError(f"Non-boolean pass value for case {case_id}")

        record = {
            "case_id": case_id,
            "baseline_passed": old_pass,
            "candidate_passed": new_pass,
            "slice_tags": new.get("slice_tags", old.get("slice_tags", [])),
        }

        if not old_pass and new_pass:
            improved.append(record)
        elif old_pass and not new_pass:
            regressed.append(record)
        else:
            unchanged.append(record)

        if new.get("criticality") == "critical" and not new_pass:
            critical_failures.append(case_id)

    n = len(baseline_ids)
    baseline_pass_rate = (
        sum(row["passed"] for row in baseline) / n if n else None
    )
    candidate_pass_rate = (
        sum(row["passed"] for row in candidate) / n if n else None
    )

    return {
        "valid_comparison": True,
        "n_cases": n,
        "baseline_pass_rate": baseline_pass_rate,
        "candidate_pass_rate": candidate_pass_rate,
        "difference": (
            candidate_pass_rate - baseline_pass_rate
            if n else None
        ),
        "improved_count": len(improved),
        "regressed_count": len(regressed),
        "unchanged_count": len(unchanged),
        "critical_failures": critical_failures,
        "improved_cases": improved,
        "regressed_cases": regressed,
    }


baseline = [
    {"case_id": "en-001", "passed": True, "criticality": "normal"},
    {"case_id": "mix-001", "passed": True, "criticality": "high"},
    {"case_id": "sec-001", "passed": True, "criticality": "critical"},
]

candidate = [
    {"case_id": "en-001", "passed": True, "criticality": "normal"},
    {"case_id": "mix-001", "passed": False, "criticality": "high"},
    {"case_id": "sec-001", "passed": False, "criticality": "critical"},
]

print(compare_regression_runs(baseline, candidate))
```

**Limitations:** This is a compact illustration, not a complete release
gate. It assumes one binary outcome per case, does not calculate
uncertainty, and does not automatically aggregate subgroup metrics.
Production code should validate duplicate IDs, missing fields, schema
versions, denominator policies, and per-slice counts. It should also
ensure that a case's criticality and slice tags are versioned
consistently.

<br/>

## 11. Practice: Introduce a Deliberate Regression

### Scenario

A baseline prompt instructs the system to return a policy answer with
the general rule and any applicable exceptions. A candidate prompt is
shortened and no longer explicitly asks for exceptions.

Your regression suite includes:

-   100 ordinary policy questions.
-   20 questions where the general rule has a documented exception.
-   10 unanswerable questions that should trigger abstention.
-   10 permission-boundary cases.

The candidate improves the ordinary questions but omits exceptions in 8
of the 20 exception cases. All other outcomes are unchanged.

<br/>

### Tasks

1.  Calculate the exception-case pass rate if the baseline passed all 20
    and the candidate passes 12.
2.  Explain why the overall metric might still improve.
3.  Identify the exact evidence the regression report should expose.
4.  Define a release policy for the exception cases and
    permission-boundary cases.
5.  Suggest a targeted prompt change and a regression test.
6.  Explain which parts should be tested deterministically and which
    require semantic evaluation.

<br/>

## 12. Answer Key

### 1. Exception-case pass rate

-   Baseline: $20/20 = 100\\%$.
-   Candidate: $12/20 = 60\\%$.
-   Difference: $-40$ percentage points.

<br/>

### 2. Why the overall metric might improve

If the candidate improves enough ordinary cases, those gains can
outweigh exception failures in a single aggregate rate. The overall
metric does not indicate which cases regressed or whether the failures
have greater consequence than the improvements.

<br/>

### 3. Evidence the report should expose

-   The 8 exception-case IDs that changed from pass to fail.
-   Baseline and candidate outputs or protected references to them.
-   The expected exception behavior and rubric version.
-   The exact prompt versions and run IDs.
-   Baseline/candidate pass rates for ordinary, exception, unanswerable,
    and permission-boundary slices.
-   Criticality tags and any must-pass gate violations.
-   Configuration, evaluator, and dataset versions.

<br/>

### 4. Release policy

Treat exception cases according to their business consequence. If
omitting an exception can produce a consequentially incorrect decision,
designate those cases as high-priority or must-pass and block release
when the gate is violated. Permission-boundary failures should be
treated as critical security failures and block release pending
investigation. These policies should be defined before evaluating the
candidate.

<br/>

### 5. Targeted change and test

Restore an explicit instruction to identify relevant exceptions and
their conditions, grounded in the supplied policy evidence. Add the 8
regressed cases to the permanent regression suite, retain successful
ordinary cases, and rerun all policy and permission-boundary cases.
Confirm that exception coverage improves without creating unsupported
exceptions or weakening access controls.

<br/>

### 6. Deterministic versus semantic checks

Deterministic checks can verify JSON/schema validity, required fields,
case IDs, access-control filtering, and that the regression report
counts failures correctly. Semantic evaluation is needed to decide
whether the answer correctly states the general rule and exception,
whether evidence supports the answer, and whether an unanswerable case
is handled appropriately. Live model evaluation may need repeats or
review if outputs vary.

<br/>

## 13. Checkpoint: Aggregate Improvement Can Hide a Critical Regression

**Checkpoint prompt:** Explain how aggregate improvements can conceal a
critical subgroup regression.

A strong answer should cover:

-   Unequal subgroup sizes and the dominance of high-volume slices.
-   The difference between aggregate metrics and case-level outcomes.
-   Why high-severity regressions need separate gates.
-   The importance of denominators and subgroup coverage.
-   The need to inspect baseline-to-candidate transitions.
-   The role of predefined thresholds and release policy.

<br/>

### Model checkpoint answer

An aggregate score weights outcomes according to the evaluated case mix,
so a large, common subgroup can dominate the result. If the candidate
improves ordinary English cases but regresses on a smaller
mixed-language or high-consequence subgroup, the overall score can still
rise. I would compare baseline and candidate on matched cases, report
counts and rates for each important slice, inspect the individual
regressed cases, and track critical-case gate status separately. A
critical security, privacy, or consequential correctness regression
should not be overridden by an aggregate gain. I would also account for
subgroup sample size and uncertainty, verify that the evaluation
population is representative, and use the predefined release policy
rather than inventing thresholds after seeing the results.

<br/>

## Key Takeaways

-   Regression suites must preserve both important successes and known
    failures.
-   Version the test cases, expected behavior, rubrics, and baseline
    configuration.
-   Compare per-case outcomes, overall metrics, slices, and
    critical-case gates.
-   Define acceptable variation and release thresholds before inspecting
    candidate results.
-   Separate deterministic software checks from stochastic live model
    evaluations.
-   Include tokenizer/template, retrieval, dependency, evaluator, and
    orchestration changes in the test plan when relevant.
-   A higher aggregate score does not excuse a critical subgroup
    regression.
-   A deliberate regression test verifies that the suite and report can
    expose a known failure.

<br/>

## Further Reading

-   [pytest Documentation](https://docs.pytest.org/) --- deterministic
    tests, fixtures, parametrization, and test organization.
-   [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) ---
    versioned run parameters, metrics, and artifacts.
-   [OpenTelemetry Documentation](https://opentelemetry.io/docs/) ---
    traces and metrics for diagnosing live evaluation failures.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- risk-aware evaluation and governance.
-   [scikit-learn: Model
    Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
    --- metrics, scoring, and evaluation considerations.


<br/>


**Chapter 16 complete.** The next chapter is **Optimization and
Trade-offs**.
