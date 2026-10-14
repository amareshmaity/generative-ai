# Chapter 18: Evaluation Gates in CI/CD

## Learning Objectives

By the end of this chapter, you should be able to:

-   Design layered evaluation gates for a Generative AI application.
-   Separate fast deterministic checks, fixed regression evaluations,
    and optional live comparisons.
-   Define quality thresholds, critical failures, sample requirements,
    and reviewer escalation.
-   Version baselines and prevent missing or failed evaluations from
    silently passing.
-   Protect secrets and private evaluation data in logs and reports.
-   Attach evaluation evidence to a change and support release blocking
    or rollback.
-   Implement a gate that catches a critical failure and reports an
    inconclusive evaluation explicitly.

<br/>

## 1. What Is an Evaluation Gate?

An **evaluation gate** is a predefined decision rule that determines
whether a code, prompt, model, retrieval, or configuration change can
proceed to the next release stage.

A gate is more than a metric threshold. It needs:

-   A versioned evaluation protocol.
-   A known baseline and candidate configuration.
-   Required checks and valid result conditions.
-   Explicit pass, fail, and inconclusive states.
-   Rules for critical failures and escalation.
-   A record of the evidence behind the decision.

A gate should never treat "evaluation did not run," "results are
missing," or "the evaluator crashed" as equivalent to "all tests
passed."

<br/>

### Gate outcomes

| Outcome          | Meaning                                                               | Typical action                          |
| ---------------- | --------------------------------------------------------------------- | --------------------------------------- |
| **Pass**         | All required checks completed and release criteria are satisfied      | Allow the next stage                    |
| **Fail**         | A release-blocking criterion was violated                             | Block release; investigate or roll back |
| **Inconclusive** | Evidence is missing, invalid, underpowered, or otherwise insufficient | Do not auto-approve; rerun or escalate  |
| **Warning**      | A non-blocking issue or monitored deviation was found                 | Record and review according to policy   |


A warning should not be used for a condition that policy defines as
release-blocking. Likewise, a critical failure should not be averaged
away by a good overall score.

<br/>

## 2. Layer the Evaluation Pipeline

Use a layered approach so inexpensive, deterministic checks run before
costly model evaluations.

``` mermaid
flowchart TD
    A[Code, prompt, model or config change] --> B[Layer 1: Static and unit checks]
    B --> C[Layer 2: Deterministic contract tests]
    C --> D[Layer 3: Fixed offline regression suite]
    D --> E[Layer 4: Optional live comparison]
    E --> F[Aggregate, slice and critical-case review]
    F --> G{Gate decision}
    G -- Pass --> H[Promote artifact]
    G -- Fail --> I[Block release or roll back]
    G -- Inconclusive --> J[Hold and rerun or escalate]
```

The exact layers depend on the application. A prompt-only change may not
require every infrastructure test; a provider SDK upgrade may need
integration tests even if the prompt is unchanged.

<br/>

### Layer 1: Static checks and unit tests

Fast checks that should usually be deterministic:

-   Configuration and manifest validation.
-   Prompt-template rendering.
-   Type checks, linting, and unit tests.
-   Metric calculation and aggregation tests.
-   Secret scanning.
-   Schema definition and parser unit tests.
-   Retry, timeout, and error-handling logic.

<br/>

### Layer 2: Deterministic contract tests

Use fixed fixtures and controlled dependencies to test contracts such
as:

-   Required JSON keys and types.
-   Business rules and field constraints.
-   Tool argument schemas.
-   Access-control and tenant-isolation filters.
-   Handling of malformed input.
-   Correct reporting of missing results and failed tests.

These checks should not need a live LLM unless the contract specifically
depends on provider integration.

<br/>

### Layer 3: Fixed offline regression suite

Run a versioned set of stable cases with expected behavior and defined
scoring rules. Compare candidate results with a versioned baseline.

Include:

-   Important successful cases.
-   Known past failures.
-   Critical and must-pass cases.
-   Representative task and source-type slices.
-   High-consequence, permission, and unsupported-input cases.

Store case-level outcomes as well as aggregate scores. An overall
improvement must not hide a critical failure or a material subgroup
regression.

<br/>

### Layer 4: Optional live comparison

Live evaluation may be needed to verify provider behavior, current
hosted-model responses, tool integrations, latency, or cost. It can be
expensive and nondeterministic.

Record model/provider metadata, timestamps, retries, errors, and missing
outputs. Define repeat policies and minimum sample requirements before
running. If the live service is unavailable, the gate should report an
infrastructure failure or inconclusive result according to the
predefined policy---not silently pass.

<br/>

## 3. Define Release Criteria Before Running

A release gate needs criteria that can be evaluated consistently.

Examples include:

-   Overall quality must meet a minimum threshold.
-   Candidate quality must not fall more than an allowed margin below
    baseline.
-   Critical cases must pass.
-   High-priority slices must remain within declared regression limits.
-   Schema validity and business-rule checks must pass.
-   Sample counts and evaluation coverage must meet minimum
    requirements.
-   Timeout, error, and missing-result rates must remain below limits.
-   Latency and cost must fit the relevant budgets.
-   Required reviewer approval must be recorded.

Thresholds should reflect product requirements, risk, and measurement
uncertainty. Do not invent or loosen a threshold after seeing an
unfavorable result merely to make a candidate pass.

<br/>

### Absolute threshold versus regression threshold

An **absolute threshold** asks whether the candidate is good enough:

$$
M_{\text{candidate}} \geq T_{\text{minimum}}
$$

A **regression threshold** asks whether the candidate has deteriorated
too much relative to baseline:

$$
M_{\text{candidate}} - M_{\text{baseline}} \geq -\delta
$$

Here, $T_{\text{minimum}}$ is the minimum acceptable metric and $\delta$
is the allowed drop for a higher-is-better metric. For lower-is-better
metrics such as latency, define the direction explicitly.

Passing a regression threshold does not necessarily mean the candidate
is acceptable: it may still fail the absolute threshold. Conversely, a
candidate can exceed an absolute threshold but regress too much relative
to a strong baseline. Both checks may be needed.

<br/>

## 4. Critical Failures and Must-Pass Checks

Some failures must be evaluated independently of aggregate quality.

Examples:

-   Cross-user or cross-tenant data exposure.
-   Unauthorized document retrieval.
-   A prohibited action or unsafe tool execution.
-   A critical policy exception omitted from a consequential answer.
-   Invalid output that could trigger an unsafe downstream action.
-   Failure to enforce required authentication or authorization.
-   Leakage of secrets into logs or public artifacts.

For these conditions, define the expected behavior and release response
in advance. A critical failure should generally block release and
trigger investigation. If the failure indicates active exposure, follow
the relevant incident-response process as well.

Do not rely solely on an aggregate score, a judge score, or a weighted
average to detect these issues. Use explicit test cases, deterministic
assertions where possible, and appropriate expert review for semantic
requirements.

<br/>

## 5. Sample Requirements and Inconclusive Results

A gate can produce a misleading result if it evaluates too few cases,
excludes failures, or receives incomplete data.

Define minimum requirements such as:

-   Minimum number of assigned and completed cases.
-   Required coverage of critical cases and important slices.
-   Maximum allowed missing or invalid result count.
-   Required number of repeats for selected stochastic cases.
-   Minimum number of valid paired cases for baseline comparisons.
-   Valid evaluator and dataset versions.
-   Valid run manifest and artifact references.

The appropriate values depend on the risk and statistical design; there
is no universal sample size for all GenAI applications.

<br/>

### Conditions that should be inconclusive or invalid

-   Regression suite failed to load or did not run.
-   Dataset or label version does not match the declared protocol.
-   Baseline or candidate artifacts are missing.
-   Too few valid cases were scored.
-   Case IDs do not match for a paired comparison.
-   Required critical cases were skipped.
-   Evaluator crashed or returned unparseable results.
-   Too many requests timed out or returned no output.
-   A live provider was unavailable and the live check was required.
-   Metric calculations failed or produced non-finite values.

The gate should distinguish an actual quality failure from insufficient
evidence. Both can block automatic promotion, but they require different
remediation.

<br/>

## 6. Version the Baseline and Evaluation Protocol

A gate is only meaningful if the baseline is identifiable and the
evaluation protocol is stable.

Record and validate:

-   Baseline run ID and candidate run ID.
-   Regression-suite version and case IDs.
-   Dataset, labels, references, and rubric versions.
-   Prompt and output-schema versions.
-   Model identifier and available snapshot/version.
-   Retrieval corpus/index and configuration.
-   Code commit, dependency lockfile, and runtime.
-   Metric implementation and denominator policy.
-   Timeout, retry, fallback, cache, and concurrency policy.
-   Threshold policy and gate implementation version.

Use immutable IDs or hashes where appropriate. Aliases such as `latest`
are not sufficient by themselves if they can point to different
artifacts over time.

If the baseline must be updated, do so through a reviewed process. A new
baseline should not silently overwrite the evidence used for prior
releases.

<br/>

## 7. Keep Evaluation Failures Separate from Product Failures

A gate needs clear status handling.

Examples:

-   **Product-quality failure:** a valid output is wrong or unsupported.
-   **Contract failure:** output violates a required schema or business
    rule.
-   **Infrastructure failure:** provider timeout, unavailable
    dependency, or failed connection.
-   **Evaluation failure:** evaluator crash, missing labels, invalid
    metric output, or incomplete artifacts.
-   **Inconclusive result:** the run completed partially but does not
    satisfy sample or coverage requirements.

These categories may lead to different actions. A quality failure can
require a prompt/model fix. An infrastructure failure can require a
rerun or operational investigation. An evaluation failure means the
decision cannot be trusted.

Never convert missing results to passes. If policy counts timeouts as
failures for a product-level metric, apply that policy consistently;
also retain the operational status so the cause can be diagnosed.

<br/>

## 8. Protect Secrets and Private Evaluation Data

CI/CD logs and artifacts may be visible to developers, contractors,
external contributors, or public build systems. Evaluation inputs and
outputs can contain private or confidential information.

Recommended controls:

-   Do not print API keys, credentials, access tokens, or secrets in
    logs.
-   Use secret managers or the CI platform's protected secret mechanism.
-   Redact sensitive input/output fields before logging.
-   Store full raw artifacts in restricted storage, not public build
    output.
-   Use least-privilege access to datasets, logs, and model endpoints.
-   Avoid uploading private evaluation cases to public pull-request
    artifacts.
-   Apply retention and deletion policies to temporary evaluation data.
-   Sanitize model-generated strings before rendering them in logs or
    reports.
-   Ensure that debugging output cannot expose cross-tenant context or
    retrieved private documents.

A report can include aggregate counts, case IDs, and controlled artifact
references without exposing full sensitive prompts or answers. If a
developer needs access to a failed case, use the approved restricted
workflow.

<br/>

## 9. Attach Evidence to Changes and Support Rollback

Every gate decision should be attached to the code or configuration
change it evaluates.

A useful report includes:

-   Commit, pull request, release, or configuration-change ID.
-   Baseline and candidate run IDs.
-   Dataset and regression-suite versions.
-   Gate policy version and decision.
-   Overall metrics and absolute/relative differences.
-   Critical failures and affected case IDs.
-   Slice metrics and coverage.
-   Missing, invalid, timed-out, and excluded case counts.
-   Latency/cost/resource summaries where relevant.
-   Links or restricted references to raw artifacts.
-   Reviewer decision, timestamp, and reason for any override.

<br/>

### Release and rollback flow

1.  Run the required checks on the candidate.
2.  Evaluate gate outcomes and validate that the evidence is complete.
3.  Block promotion on a fail or inconclusive result, unless an explicit
    authorized policy says otherwise.
4.  Promote only the artifact/configuration that was evaluated.
5.  Monitor post-release quality and operational metrics.
6.  Roll back or disable the change if release criteria are violated in
    production.
7.  Preserve the incident and evaluation artifacts for diagnosis.

Do not evaluate one configuration and then deploy a different one
without rerunning the relevant checks. The deployed artifact must match
the tested artifact.

<br/>

## 10. Example Gate Policy

The following policy is illustrative. Set actual thresholds based on
your product requirements and risk analysis.

| Check                           | Example rule                                     | Outcome if violated                     |
| ------------------------------- | ------------------------------------------------ | --------------------------------------- |
| Static/unit tests               | All required tests pass                          | Fail                                    |
| Schema/business rules           | All must-pass assertions pass                    | Fail                                    |
| Critical security/privacy cases | Zero confirmed critical failures                 | Fail                                    |
| Evaluation completeness         | Required artifacts and versions present          | Inconclusive                            |
| Sample size                     | At least the declared minimum valid paired cases | Inconclusive                            |
| Overall quality                 | Meets minimum threshold                          | Fail                                    |
| Quality regression              | Drop no larger than declared tolerance           | Fail or review, per policy              |
| Important subgroup              | No violation of subgroup guardrail               | Fail or escalate                        |
| Live provider check             | Required live test completes with valid results  | Inconclusive on unavailable/invalid run |
| Latency/cost                    | Within product budget                            | Fail or review, per policy              |
| Human approval                  | Required reviewer decision recorded              | Inconclusive until reviewed             |


The distinction between fail and inconclusive should be explicit in the
policy. A candidate can fail a quality criterion even when all data is
present; it can be inconclusive when the data needed to make the
decision is absent.

<br/>

## 11. Python: A Small Gate with Explicit Inconclusive State

This example checks critical failures, minimum sample size, missing
outcomes, and a quality threshold. It uses three outcomes: `PASS`,
`FAIL`, and `INCONCLUSIVE`.

``` python
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class EvaluationCase:
    case_id: str
    passed: Optional[bool]
    critical: bool = False


@dataclass
class GateResult:
    status: GateStatus
    reasons: list[str]
    evaluated_cases: int
    missing_cases: int
    pass_rate: Optional[float]


def evaluate_gate(
    cases: list[EvaluationCase],
    minimum_cases: int,
    minimum_pass_rate: float,
) -> GateResult:
    reasons: list[str] = []

    # Empty or undersized evaluations do not provide enough evidence.
    if len(cases) < minimum_cases:
        reasons.append(
            f"Insufficient assigned cases: {len(cases)} < {minimum_cases}"
        )

    missing = [case for case in cases if case.passed is None]
    evaluated = [case for case in cases if case.passed is not None]

    if missing:
        reasons.append(f"{len(missing)} case outcome(s) are missing")

    # Any confirmed critical failure is a release-blocking failure.
    critical_failures = [
        case.case_id
        for case in evaluated
        if case.critical and case.passed is False
    ]
    if critical_failures:
        reasons.append(
            "Critical failure(s): " + ", ".join(critical_failures)
        )

    pass_rate = (
        sum(case.passed is True for case in evaluated) / len(evaluated)
        if evaluated else None
    )

    # A confirmed critical failure is FAIL even if other evidence is missing.
    if critical_failures:
        status = GateStatus.FAIL
    elif len(cases) < minimum_cases or missing or pass_rate is None:
        status = GateStatus.INCONCLUSIVE
    elif pass_rate < minimum_pass_rate:
        status = GateStatus.FAIL
        reasons.append(
            f"Pass rate {pass_rate:.3f} is below "
            f"minimum {minimum_pass_rate:.3f}"
        )
    else:
        status = GateStatus.PASS
        reasons.append("All implemented gate checks passed")

    return GateResult(
        status=status,
        reasons=reasons,
        evaluated_cases=len(evaluated),
        missing_cases=len(missing),
        pass_rate=pass_rate,
    )


example_cases = [
    EvaluationCase("normal-001", True),
    EvaluationCase("normal-002", True),
    EvaluationCase("privacy-001", False, critical=True),
    EvaluationCase("normal-004", None),
]

result = evaluate_gate(
    cases=example_cases,
    minimum_cases=4,
    minimum_pass_rate=0.90,
)

print("Status:", result.status.value)
print("Reasons:", result.reasons)
print("Evaluated:", result.evaluated_cases)
print("Missing:", result.missing_cases)
print("Pass rate:", result.pass_rate)
```

<br/>

### What the example demonstrates

-   A confirmed critical failure produces `FAIL`.
-   Missing outcomes or insufficient sample size produce `INCONCLUSIVE`
    when no confirmed critical failure already requires `FAIL`.
-   A complete evaluation below the quality threshold produces `FAIL`.
-   Only a sufficiently complete evaluation that meets the implemented
    checks can return `PASS`.

<br/>

### Important limitations

This is a teaching example, not a production-ready gate. A production
implementation should also validate unique case IDs, dataset and
baseline versions, required critical-case coverage, schema validity,
evaluator errors, timeouts, paired-case identity, subgroup thresholds,
latency/cost budgets, and confidence intervals where appropriate. It
should verify that the manifest and artifacts correspond to the exact
candidate being released.

The precedence rule matters: a known critical failure is not made
inconclusive merely because other cases are missing. Conversely, missing
data must never be silently treated as a passing outcome.

<br/>

## 12. Practice: Design a Gate

### Scenario

A candidate release has the following evaluation results:

-   500 cases were assigned.
-   492 outcomes were valid; 8 are missing.
-   The measured pass rate among valid outcomes is 93%.
-   The declared minimum pass rate is 92%.
-   One confirmed critical permission-boundary case failed.
-   The report references a baseline alias called `latest`, but no
    immutable baseline run ID is recorded.
-   A live provider check timed out.
-   The candidate report contains full prompts and answers in a public
    CI log.

<br/>

### Tasks

1.  What is the gate decision: pass, fail, or inconclusive?
2.  Which issue independently blocks release?
3.  Which issues make the evaluation evidence incomplete or unauditable?
4.  What should happen to the public log and exposed data?
5.  List the minimum corrections needed before a valid rerun.
6.  Explain why the 93% pass rate does not justify release.

<br/>

## 13. Answer Key

### 1. Gate decision

The gate should be **FAIL** because a confirmed critical
permission-boundary case failed. The result is also incomplete and
unauditable in several respects, but the critical failure independently
blocks release.

<br/>

### 2. Independent blocker

The permission-boundary failure is a critical security issue. It should
be investigated and fixed under the appropriate security process before
promotion.

<br/>

### 3. Incomplete or unauditable evidence

-   Eight outcomes are missing.
-   The baseline is identified only by a mutable alias, not an immutable
    run ID.
-   The live provider check timed out, so a required live evaluation may
    be incomplete.
-   Full prompts and answers were exposed in a public CI log.
-   The reported pass rate is calculated only over valid outcomes; the
    denominator policy must state how missing results are treated.

<br/>

### 4. Public log and exposed data

Restrict or remove public access according to incident-response and
platform capabilities, preserve necessary audit evidence in approved
restricted storage, assess what sensitive information was exposed, and
rotate any exposed credentials if applicable. Follow organizational
security/privacy incident procedures. Do not copy the private content
into another public artifact.

<br/>

### 5. Corrections before rerun

-   Fix the permission-boundary defect and add a regression test.
-   Resolve and record an immutable baseline run ID.
-   Investigate missing outcomes and apply the declared denominator
    policy.
-   Rerun the required live provider check or document a policy-approved
    alternative.
-   Remove sensitive data from public logs and switch to redacted logs
    plus restricted artifact references.
-   Verify dataset, evaluator, candidate, and run-manifest versions.
-   Recompute metrics and inspect critical cases and relevant slices.

<br/>

### 6. Why 93% is insufficient

The aggregate rate hides a confirmed critical security regression. It is
also based on incomplete outcomes and lacks a fully auditable baseline.
A metric above its minimum threshold cannot override critical-case gates
or missing evidence requirements.

<br/>

## 14. Checkpoint: Which Checks Block a Release and Why?

**Checkpoint prompt:** Explain which checks block a release and why.

A strong answer should distinguish:

-   **Fail:** confirmed violation of a release criterion, such as a
    critical failure, quality threshold breach, or required contract
    test failure.
-   **Inconclusive:** insufficient or invalid evidence, such as missing
    results, too few cases, missing baseline identity, or evaluator
    failure.
-   **Pass:** every required check completed, evidence is valid, and all
    release criteria are met.
-   **Warning:** a non-blocking issue explicitly permitted by policy.

<br/>

### Model checkpoint answer

I would block release for confirmed critical security, privacy, safety,
or high-consequence correctness failures; failed deterministic contract
tests; or quality, subgroup, latency, and cost thresholds that the
release policy defines as mandatory. I would also prevent automatic
promotion when evaluation is inconclusive because required cases or
artifacts are missing, the baseline is not immutable, the sample
requirement is unmet, or a required live evaluation did not complete.
Inconclusive does not necessarily mean the candidate is poor; it means
the evidence is insufficient to approve it. I would approve only when
the evaluated artifact matches the release candidate, all mandatory
checks complete, and the versioned gate policy is satisfied.

<br/>

## Key Takeaways

-   Use layered checks: fast deterministic tests first, fixed offline
    regression next, and live evaluations when required.
-   Define thresholds, critical cases, sample requirements, and
    escalation rules before evaluating a candidate.
-   A critical failure cannot be averaged away by a strong aggregate
    score.
-   Missing or invalid evaluations must be reported as inconclusive or
    failed according to a documented policy, never silently passed.
-   Version baselines, datasets, prompts, models, evaluators, and gate
    rules.
-   Keep secrets and private evaluation data out of public logs and
    artifacts.
-   Attach evidence to the exact change and release artifact.
-   Block promotion or roll back when release criteria fail.

<br/>

## Further Reading

-   [GitHub Actions Documentation](https://docs.github.com/actions) ---
    workflows, job dependencies, artifacts, and secrets.
-   [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/) ---
    pipelines, jobs, artifacts, and protected variables.
-   [pytest Documentation](https://docs.pytest.org/) --- deterministic
    testing and assertions.
-   [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) ---
    experiment parameters, metrics, and artifacts.
-   [OpenTelemetry Documentation](https://opentelemetry.io/docs/) ---
    tracing and operational diagnostics.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- risk-aware evaluation and governance.


<br/>


**Chapter 18 complete.** The next chapter is **Online Feedback and
Production Evaluation**.
