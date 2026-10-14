# Chapter 15: Controlled Comparisons and Uncertainty

## Learning Objectives

By the end of this chapter, you should be able to:

-   Compare candidate GenAI systems on matched evaluation cases under
    controlled conditions.
-   Identify confounding variables that make comparisons unreliable.
-   Repeat selected cases to measure stochastic variation.
-   Report confidence intervals or bootstrap estimates with their
    assumptions.
-   Interpret small samples, rare failures, subgroup results, and
    repeated experiment selection cautiously.
-   Protect a final assessment set from repeated tuning.
-   Report observed quality differences together with uncertainty and
    coverage limitations.

<br/>

## 1. Why a Point Estimate Is Not Enough

Suppose a baseline system passes 82% of an evaluation set and a
candidate passes 85%. The observed difference is three percentage
points. That difference is a useful description of the tested sample,
but it does not automatically establish that the candidate is better in
general.

The result may depend on:

-   Which cases were included.
-   Whether baseline and candidate saw the same cases.
-   Differences in prompts, models, retrieval, decoding, or runtime
    configuration.
-   Random variation between model runs.
-   Small sample size or a few influential cases.
-   Label noise or evaluator disagreement.
-   Repeatedly trying candidates and reporting only the best result.
-   Coverage gaps between the evaluation set and real-world usage.

A sound comparison separates three questions:

1.  **What did we observe?** The measured difference on the evaluated
    cases.
2.  **How uncertain is that estimate?** How much could it vary under a
    stated sampling or repeated-run model?
3.  **How far does the result generalize?** Which tasks, languages,
    sources, users, and operating conditions are represented---or not
    represented?

Statistical uncertainty does not capture every source of uncertainty. A
narrow confidence interval cannot fix a biased dataset, incorrect
labels, a changed evaluator, or a benchmark that poorly represents
production.

<br/>

## 2. Use Matched Cases

A matched or paired comparison evaluates baseline and candidate on the
same cases, using the same reference labels and scoring policy.

For case $i$, let:

-   $b_i$ be the baseline score.
-   $c_i$ be the candidate score.
-   $d_i = c_i - b_i$ be the paired difference.

The average paired difference is:

$$
\bar{d} = \frac{1}{N}\sum_{i=1}^{N}(c_i-b_i)
$$

Pairing controls for differences in case difficulty: both systems face
the same evaluation examples. It does not eliminate model stochasticity,
evaluator error, or dataset bias.

<br/>

### Why matched cases matter

Imagine that a candidate is evaluated mostly on easy questions while the
baseline is evaluated mostly on difficult questions. The candidate may
appear better even if its underlying behavior is unchanged. Matched
cases make the comparison more interpretable.

For a binary pass/fail metric, each case-level difference is:

-   $+1$: candidate passes and baseline fails.
-   $0$: both pass or both fail.
-   $-1$: baseline passes and candidate fails.

These paired outcomes reveal more than two independent aggregate pass
rates. In particular, inspect how many cases improved, regressed, and
remained unchanged.

<br/>

### Comparison checklist

-   Use the same immutable case IDs and reference-label version.
-   Apply the same evaluator, rubric, normalization, and denominator
    policy.
-   Keep workload and execution conditions comparable.
-   Record model, prompt, retrieval, schema, tool, and runtime
    differences.
-   Treat missing outputs, timeouts, retries, and exclusions
    consistently.
-   Preserve per-case outcomes and examine regressions, not just the
    average.
-   Document any unavoidable mismatch between runs.

If a candidate intentionally changes both the prompt and retrieval
configuration, the experiment can estimate the effect of the combined
change. It cannot reliably attribute the gain to either component alone.
Use a controlled factorial or sequential experiment when attribution
matters.

<br/>

## 3. Control the Workload and Environment

The same nominal test set is not sufficient if the systems are run under
materially different conditions.

Control or record:

-   Input cases, order, and any randomization.
-   Model identifier and available version/snapshot.
-   Prompt templates and rendered variables.
-   Retrieval corpus/index version and filters.
-   Generation settings, output-token limits, and seed support.
-   Tool versions, tool results, and orchestration paths.
-   Concurrency, arrival pattern, timeouts, retries, and fallbacks.
-   Cache state and warm-up policy.
-   Evaluator model, rubric, and metric implementation.
-   Date/time and provider metadata for hosted services.

For latency or cost comparisons, workload matching is especially
important. Different concurrency, cache conditions, output lengths, or
retry behavior can make a performance comparison misleading even when
the prompts are identical.

<br/>

### Change one factor when you need attribution

When practical, isolate the factor being studied. For example:

| Experiment | Prompt    | Retrieval | Purpose                                         |
| ---------- | --------- | --------- | ----------------------------------------------- |
| A          | Baseline  | Baseline  | Reference condition                             |
| B          | Candidate | Baseline  | Estimate prompt change under baseline retrieval |
| C          | Baseline  | Candidate | Estimate retrieval change under baseline prompt |
| D          | Candidate | Candidate | Measure combined configuration                  |


The combined effect need not equal the sum of individual effects;
components can interact. This design is illustrative and should be
adapted to the available budget and experimental question.

<br/>

## 4. Separate Case Sampling Variation from Model Variation

GenAI evaluations can contain at least two distinct forms of variation.

### 4.1 Case-sampling variation

The tested cases are only a sample from a larger population of tasks. A
different representative sample may produce a different estimated
quality difference.

<br/>

### 4.2 Run-to-run or model variation

The same case can produce different outputs across repeated executions
because of sampling, nondeterministic execution, changing external
tools, or provider-side model changes.

These are different questions:

-   **Case uncertainty:** Would the result change if we evaluated
    another representative sample of cases?
-   **Run uncertainty:** Would the result change if we executed the same
    cases again under the same intended configuration?

Repeatedly running the same cases can characterize run-to-run variation,
but it does not replace broader case coverage. Conversely, evaluating
many distinct cases once may characterize case-level performance while
missing important stochastic variability.

<br/>

### Repeated-case protocol

1.  Select cases in advance that are representative and/or especially
    sensitive to generation variability.
2.  Define the number of repeats and the reason for selecting these
    cases.
3.  Keep settings fixed and record any seed or provider metadata.
4.  Record every output, not only the best or most convenient one.
5.  Score repeats with the same versioned evaluator.
6.  Report within-case variability and the fraction of cases whose
    pass/fail outcome changes.
7.  If hosted-model behavior changes over time, record timestamps and
    treat the comparison accordingly.

Do not repeat only cases that support a preferred conclusion. If the
repeat set is targeted rather than random, describe it as targeted and
avoid generalizing its variation estimate to every case.

<br/>

## 5. Confidence Intervals for a Quality Difference

A point estimate summarizes the observed result. An interval
communicates uncertainty under a statistical model and its assumptions.

For paired case scores, a confidence interval for the mean difference
can be estimated from the distribution of $d_i$. A simple large-sample
interval is:

$$
\bar{d} \pm 1.96\frac{s_d}{\sqrt{N}}
$$

where:

-   $\bar{d}$ is the mean paired difference.
-   $s_d$ is the sample standard deviation of paired differences.
-   $N$ is the number of independent paired cases.

This normal-approximation interval can be inaccurate for very small
samples, strongly skewed outcomes, clustered cases, or unusual
distributions. The multiplier 1.96 corresponds to an approximate 95%
interval under the usual large-sample assumptions; it is not a universal
guarantee.

For binary outcomes, report the paired transition counts as well.
Methods designed for paired proportions or binary differences may be
preferable to treating the two pass rates as independent.

<br/>

### Confidence interval interpretation

A 95% confidence interval is produced by a procedure that, under its
assumptions, covers the target parameter in about 95% of repeated
samples. It is **not** a statement that there is a 95% probability that
this particular fixed interval contains the parameter.

If an interval for the difference includes zero, the data may be
compatible with no average difference as well as with some positive or
negative differences. This does not prove the systems are identical. If
the interval excludes zero, the result still needs practical-impact,
validity, and coverage checks.

<br/>

## 6. Bootstrap Estimates

Bootstrap methods estimate uncertainty by resampling observed data and
recalculating a statistic.

For a paired comparison, resample **case pairs**, not baseline and
candidate results independently. Keeping each case's two outcomes
together preserves the pairing.

<br/>

### Paired bootstrap procedure

1.  Start with $N$ matched case records.
2.  Sample $N$ records with replacement from those pairs.
3.  Calculate the candidate-minus-baseline difference for the resampled
    set.
4.  Repeat the process many times.
5.  Use selected quantiles of the bootstrap distribution as an interval.
6.  Record the resampling unit, number of resamples, interval method,
    and random seed.

For a simple percentile interval, if
$\Delta^{*(1)}, \ldots, \Delta^{*(B)}$ are bootstrap estimates, use the
2.5th and 97.5th percentiles for a nominal 95% interval.

<br/>

### Bootstrap assumptions and limitations

-   The evaluation cases should represent the population you want to
    describe.
-   Resampling units should reflect dependence. If several cases come
    from the same document, user, conversation, or source, a cluster
    bootstrap may be more appropriate than treating every case as
    independent.
-   A bootstrap cannot repair selection bias, mislabeled cases, or
    missing population segments.
-   Very small datasets can produce unstable intervals.
-   Rare failures may be absent from the sample, leaving the bootstrap
    unable to reveal their true prevalence.
-   For repeated model runs, case resampling alone does not capture all
    run-level variation. A hierarchical design may be needed when both
    case and run effects matter.

<br/>

### Python: paired bootstrap for a mean difference

The following example accepts numeric case-level scores. The baseline
and candidate arrays must be aligned by case ID and use a comparable
scoring scale.

``` python
import numpy as np


def paired_bootstrap_mean_difference(
    baseline_scores,
    candidate_scores,
    n_resamples=10_000,
    confidence=0.95,
    seed=42,
):
    baseline = np.asarray(baseline_scores, dtype=float)
    candidate = np.asarray(candidate_scores, dtype=float)

    if baseline.ndim != 1 or candidate.ndim != 1:
        raise ValueError("Scores must be one-dimensional.")
    if len(baseline) != len(candidate):
        raise ValueError("Baseline and candidate must be paired by case.")
    if len(baseline) < 2:
        raise ValueError("At least two paired cases are required.")
    if not np.isfinite(baseline).all() or not np.isfinite(candidate).all():
        raise ValueError(
            "Resolve missing/non-finite outcomes using a declared policy first."
        )
    if n_resamples < 1:
        raise ValueError("n_resamples must be positive.")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")

    differences = candidate - baseline
    observed = float(differences.mean())

    rng = np.random.default_rng(seed)
    n = len(differences)
    bootstrap_estimates = np.empty(n_resamples)

    for b in range(n_resamples):
        indices = rng.integers(0, n, size=n)
        bootstrap_estimates[b] = differences[indices].mean()

    alpha = 1 - confidence
    lower, upper = np.quantile(
        bootstrap_estimates,
        [alpha / 2, 1 - alpha / 2],
    )

    return {
        "n_paired_cases": n,
        "observed_mean_difference": observed,
        "confidence_level": confidence,
        "percentile_interval": (float(lower), float(upper)),
        "n_resamples": n_resamples,
        "seed": seed,
    }


baseline = [1, 1, 0, 1, 0, 1, 1, 0]
candidate = [1, 1, 1, 1, 0, 1, 1, 0]

print(paired_bootstrap_mean_difference(baseline, candidate))
```

This is an educational implementation of a paired percentile bootstrap.
The small illustrative dataset is not sufficient for a stable real-world
claim. For production analysis, also inspect transition counts, sampling
design, dependence between cases, rare-event risk, and whether a
different interval method is warranted.

<br/>

## 7. Small Samples and Rare Failures

Small evaluation sets produce imprecise estimates, especially when
outcomes are binary and failures are uncommon.

For example, observing zero failures in 20 cases does not prove that the
true failure rate is zero. The sample may simply not have included a
failure-prone case. As a rough rule under independent Bernoulli
sampling, the "rule of three" says that after zero observed events in
$N$ trials, an approximate 95% upper bound on the event rate is $3/N$
for reasonably large $N$.

With zero failures in 20 cases, this rough upper bound is about 15%. It
is a warning against overinterpreting a clean but small test set, not a
substitute for an exact interval.

<br/>

### Rare high-severity events

When a failure is rare but consequential, overall average quality may be
an inadequate release criterion. Consider:

-   Dedicated safety, security, privacy, and high-consequence test
    suites.
-   Adversarial and boundary cases.
-   Per-severity failure counts and rates.
-   Exact or suitable rare-event interval methods.
-   Explicit acceptance rules for critical failures.
-   Human review and incident analysis where appropriate.

A candidate that improves average quality but introduces a critical
security failure should not be declared better merely because the
aggregate metric rose.

<br/>

## 8. Subgroup Uncertainty and Coverage

Subgroup analysis can reveal regressions hidden by the aggregate.
Examples include language, source type, task, input length, domain, or
workflow.

For each important subgroup, report:

-   Number of cases and failures.
-   Baseline and candidate scores.
-   Paired difference where cases are matched.
-   An uncertainty interval where appropriate.
-   Data-coverage limitations.
-   Whether the subgroup was specified before or discovered after
    looking at results.

<br/>

### Avoid overinterpreting small slices

A subgroup with 8 cases can show a dramatic percentage change from one
case. Do not present the percentage without its denominator. If you
inspect dozens or hundreds of subgroups, some will look unusually good
or bad by chance.

Also check whether slices overlap. For example, scanned PDFs may
disproportionately contain a particular language or task. The apparent
"source type effect" may actually reflect OCR quality, language, or task
composition.

A subgroup result is evidence about the cases sampled in that subgroup.
It is not automatically evidence about every user or document with the
same label.

<br/>

## 9. Repeated Experiment Selection and the Winner's Curse

If a team tries many prompts, models, retrieval settings, and
thresholds, then reports only the best observed result, the reported
winner is likely to benefit from favorable noise. This is sometimes
called the **winner's curse**.

For example, if many candidates have similar true quality, one may
appear substantially better simply because it received a favorable
sample or random run. Selecting that candidate and reporting its
original score exaggerates the expected improvement.

<br/>

### Reduce selection bias

-   Define the primary metric and comparison protocol before testing.
-   Record all attempted configurations and results, not just the
    winner.
-   Use a development set for iterative tuning.
-   Use a validation set to compare a smaller set of candidates.
-   Reserve a final assessment set for a limited, predeclared
    evaluation.
-   Avoid repeatedly checking the final set and changing the system in
    response.
-   If the final set is used to make further changes, treat it as part
    of development and obtain a new independent final set when feasible.
-   For extensive comparisons, consider multiplicity-aware analysis or
    independent confirmation.

Do not claim that a single untouched final set guarantees universal
generalization. It supports a stronger assessment only for the
population and conditions it represents.

<br/>

## 10. Development, Validation, and Final Assessment Sets

A useful separation is:

| Set              | Purpose                                                                     | May guide tuning?                           |
| ---------------- | --------------------------------------------------------------------------- | ------------------------------------------- |
| Development      | Debugging, error analysis, prompt/model iteration                           | Yes                                         |
| Validation       | Compare shortlisted candidates and select a configuration                   | Yes, within the declared selection process  |
| Final assessment | Estimate performance of the selected candidate under a predeclared protocol | Not repeatedly; avoid tuning to its results |


The split should be appropriate to the data-generating process. For
example, documents from the same source, repeated questions from the
same conversation, or near-duplicate records may leak across splits. In
those cases, split by source, user/session, time, or another meaningful
grouping rather than randomly splitting every row.

<br/>

### Final-set discipline

1.  Define the target population and primary metric before opening the
    final results.
2.  Freeze candidate configuration and evaluation rules.
3.  Run the final assessment once for the declared comparison, where
    practical.
4.  Report the result, uncertainty, coverage, exclusions, and
    deviations.
5.  If the outcome triggers more tuning, record that the final set has
    now influenced development.
6.  Seek fresh independent evidence before making a new strong
    generalization claim.

<br/>

## 11. Report Quality Differences with Uncertainty

A clear comparison report should include more than a single percentage.

### Recommended report structure

-   **Question:** What decision is this experiment intended to support?
-   **Population:** Which cases and operating conditions are
    represented?
-   **Protocol:** How were baseline and candidate matched and
    controlled?
-   **Sample size:** How many cases were assigned, completed, paired,
    failed, and excluded?
-   **Primary result:** Baseline score, candidate score, and absolute
    difference.
-   **Uncertainty:** Confidence interval or bootstrap interval, method,
    and assumptions.
-   **Transitions:** Number of cases improved, regressed, and unchanged.
-   **Subgroups:** Important slices with counts and limitations.
-   **Other constraints:** Latency, cost, reliability, security, safety,
    and operational feasibility.
-   **Limitations:** Label quality, model nondeterminism, missing cases,
    and external validity.
-   **Decision:** What the evidence supports, what it does not support,
    and what should happen next.

<br/>

### Example report

The values below are hypothetical and illustrate reporting style rather
than a real experiment.

> On 200 matched held-out cases, the candidate achieved an 85% pass rate
> compared with 82% for the baseline, an observed increase of 3
> percentage points. A paired bootstrap interval for the mean case-level
> pass/fail difference was estimated using the same 200 case pairs; the
> interval and resampling configuration should be reported with the
> actual result. The candidate improved some cases and regressed others.
> The test set contains limited coverage of low-resource languages and
> scanned documents, so the result does not establish improvement for
> those groups. The candidate's higher p95 latency also needs to be
> assessed against the product's latency budget. The observed gain is
> promising but should not be described as a confident general
> improvement unless the uncertainty, coverage, and operational
> constraints support that conclusion.

Do not invent an interval to make a report look complete. Compute it
from actual case-level data, record the method, and state when the
sample is too limited for a reliable estimate.

<br/>

## 12. Practice: Report a Difference with Uncertainty

### Scenario

A team evaluates a baseline and a candidate on 40 matched cases. The
baseline passes 30 cases; the candidate passes 33. On the matched
case-level comparison:

-   6 cases change from fail to pass.
-   3 cases change from pass to fail.
-   27 cases have the same outcome.
-   The set includes 30 English cases and 10 mixed-language cases.
-   Only 4 cases involve scanned PDFs.
-   The candidate was selected after 12 prompt/model configurations were
    tried on the same development set.

<br/>

### Tasks

1.  Calculate the baseline and candidate pass rates and the observed
    absolute difference.
2.  Explain why the paired transitions matter.
3.  State what additional information is needed to estimate uncertainty
    appropriately.
4.  Identify at least three coverage limitations.
5.  Explain how trying 12 configurations affects the interpretation of
    the selected candidate's score.
6.  Draft a concise report that avoids claiming more than the evidence
    supports.
7.  Recommend the next evaluation step.

<br/>

## 13. Answer Key

### 1. Point estimates

-   Baseline pass rate: $30/40 = 75\\%$.
-   Candidate pass rate: $33/40 = 82.5\\%$.
-   Observed absolute difference: $82.5\\%-75\\% = 7.5$ percentage
    points.

The difference is an observed result on this sample, not proof of a
population-level improvement.

<br/>

### 2. Paired transitions

Six cases improved and three regressed. The net gain is three additional
passing cases, which matches the aggregate count change. The transition
pattern reveals that the candidate did not simply improve every case;
some regressions may be important even when the net result is positive.

<br/>

### 3. Uncertainty information

Use the paired case outcomes and a declared method suited to the metric
and sampling design. Record the resampling unit, interval method, sample
size, and assumptions. If the same source or conversation contributes
multiple cases, account for clustering where appropriate. A valid
interval cannot be calculated from only the two aggregate pass counts if
the pairing information is unavailable.

<br/>

### 4. Coverage limitations

-   Only 40 total cases.
-   Only 10 mixed-language cases.
-   Only 4 scanned-PDF cases.
-   Unknown coverage of task difficulty, source diversity, and
    production traffic.
-   Possible dependence among cases if multiple examples come from the
    same document or workflow.

<br/>

### 5. Twelve tried configurations

Selecting the best observed result after many attempts can overstate
expected performance because the winner may benefit from favorable
noise. The report should document the search process. Use the
development set for tuning and assess the selected configuration on a
reserved final set that did not guide selection.

<br/>

### 6. Example report

> On 40 matched cases, the candidate passed 33 cases (82.5%) compared
> with 30 (75%) for the baseline, an observed increase of 7.5 percentage
> points. Six cases improved, three regressed, and 27 were unchanged.
> The sample is small and has limited coverage of mixed-language input
> and scanned PDFs. The candidate was selected after 12 configurations
> were tried on the development set, so the observed gain may be
> optimistic. We need a paired uncertainty estimate, case-level
> regression review, and a predeclared assessment on a reserved final
> set before making a strong general improvement claim.

<br/>

### 7. Next step

Freeze the selected candidate, metric, and evaluation protocol. Evaluate
baseline and candidate on the same reserved final cases, preserving
per-case outputs and failures. Calculate an appropriate paired
uncertainty interval, inspect high-severity regressions and relevant
slices, and report operational trade-offs. Do not continue tuning to the
final-set results without acknowledging that the set has become part of
development.

<br/>

## 14. Checkpoint: Why a Small Observed Gain May Not Be Convincing

**Checkpoint prompt:** Explain why a small observed gain may not support
a confident improvement claim.

A strong answer should address:

-   The size and representativeness of the sample.
-   Matched-case design and consistency of evaluation settings.
-   Run-to-run variation and hosted-model nondeterminism.
-   Confidence or bootstrap interval and its assumptions.
-   Regressions and rare high-severity failures.
-   Subgroup sample sizes and coverage gaps.
-   Multiple candidate trials and selection bias.
-   Whether the final assessment set influenced tuning.
-   Latency, cost, reliability, and safety constraints.

<br/>

### Model checkpoint answer

A small observed gain may reflect sampling noise, run-to-run model
variation, evaluator disagreement, or the fact that the candidate was
selected from many tried configurations. The point estimate alone does
not show how uncertain the difference is. I would verify that baseline
and candidate were evaluated on the same cases with identical scoring
rules, inspect paired improvements and regressions, and compute an
uncertainty interval using a method suited to the outcome and sampling
design. I would also examine rare high-severity failures and subgroup
coverage, because aggregate quality can hide critical regressions.
Finally, I would confirm that the final assessment set was not
repeatedly used for tuning and check latency, cost, and reliability.
Until those checks support the result, I would describe the gain as
observed and provisional rather than a confident general improvement.

<br/>

## Key Takeaways

-   Matched cases and controlled workloads make comparisons more
    interpretable.
-   Case-sampling uncertainty and run-to-run variation are distinct.
-   Confidence intervals and bootstrap estimates depend on assumptions;
    neither fixes biased data.
-   Small samples and rare failures require explicit coverage and
    uncertainty caveats.
-   Subgroup rates need denominators and careful interpretation,
    especially with many comparisons.
-   Repeatedly selecting the best of many candidates can inflate the
    apparent gain.
-   Reserve a final assessment set and avoid repeatedly tuning to its
    results.
-   Report the point estimate, uncertainty, transitions, coverage
    limits, regressions, and operational trade-offs together.

<br/>

## Further Reading

-   [scikit-learn: Model
    Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
    --- metric selection and evaluation methodology.
-   [SciPy: Statistical
    Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
    --- confidence intervals and statistical procedures.
-   [NumPy Random
    Sampling](https://numpy.org/doc/stable/reference/random/index.html)
    --- reproducible random sampling and generators.
-   [NIST/SEMATECH e-Handbook of Statistical
    Methods](https://www.itl.nist.gov/div898/handbook/) --- statistical
    intervals, experimental design, and uncertainty.
-   [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) ---
    recording experiment parameters, metrics, and artifacts.


<br/>


**Chapter 15 complete.** The next chapter is **Prompt and Model
Regression Testing**.
