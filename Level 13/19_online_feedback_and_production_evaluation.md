# Chapter 19: Online Feedback and Production Evaluation

## Learning Objectives

By the end of this chapter, you should be able to:

-   Distinguish explicit user ratings, observed task outcomes, and noisy
    behavioral signals.
-   Design a privacy-conscious feedback pipeline with provenance, access
    controls, and retention limits.
-   Monitor sampled production failures, distribution shifts, and
    delayed outcomes.
-   Explain shadow evaluation, canary rollout, and controlled
    experiments.
-   Convert verified production failures into reviewed regression cases
    without exposing private data.
-   Explain why user satisfaction alone is not proof of correctness,
    groundedness, or safety.

<br/>

## 1. Why Online Evaluation Matters

Offline evaluation tests a system against a prepared dataset in a
controlled setting. Online evaluation examines behavior under real
production conditions: actual user inputs, changing distributions, real
latency and infrastructure, and outcomes that may become visible only
later.

Production evidence can reveal failures that offline tests did not
anticipate. However, production data is not automatically reliable
ground truth. It may be incomplete, biased toward certain users,
delayed, noisy, or subject to privacy restrictions.

**Core principle:** use online evidence to discover and prioritize
risks; use reviewed, appropriately de-identified evidence and repeatable
offline tests to validate changes before broad release.

<br/>

### Offline and online evidence

| Dimension        | Offline evaluation                                   | Online / production evaluation                                         |
| ---------------- | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| Inputs           | Curated, versioned cases                             | Real traffic or permitted samples                                      |
| Conditions       | Controlled and reproducible                          | Variable, concurrent, evolving                                         |
| Labels           | Reviewed references or rubric judgments              | Ratings, outcomes, delayed labels, investigations                      |
| Strength         | Comparable experiments and regression detection      | Real-world coverage and operational behavior                           |
| Limitations      | May miss distribution shifts and real usage patterns | Confounding, incomplete labels, privacy risk, changing conditions      |
| Typical decision | Is a candidate ready for release?                    | Is the live system behaving as expected, and what needs investigation? |


Neither replaces the other. Offline evaluation gives controlled
comparison; online evidence tests whether assumptions continue to hold
in the field.

<br/>

## 2. Three Types of Feedback

Do not combine all feedback into a single "quality" metric. Different
signals support different conclusions.

### 2.1 Explicit ratings

Examples include thumbs-up/down, star ratings, or a short user survey.

**Advantages** - Directly expresses a user's reported experience. - Can
identify confusing, irrelevant, or unhelpful responses. - Can be linked
to a specific interaction when consent and policy allow.

**Limitations** - Only a subset of users respond. - Ratings can reflect
tone, wait time, expectations, or disagreement rather than factual
accuracy. - A user may rate a confident but incorrect answer
positively. - The absence of a rating is not a negative rating.

<br/>

### 2.2 Observed task outcomes

These are signals that a task succeeded or failed, such as: - A valid
structured response was accepted by a downstream system. - A support
issue was reopened after an AI-generated answer. - A user successfully
completed a workflow. - A human reviewer confirmed that an answer
resolved a request. - A transaction was rejected by a business-rule
validator.

Outcomes can be more actionable than satisfaction ratings, but they
still require interpretation. A task may fail because of an unrelated
service outage, poor UI design, or a downstream dependency rather than
the model response itself.

<br/>

### 2.3 Behavioral signals

Examples include copy, retry, regeneration, edit, abandonment, dwell
time, or repeated queries.

These are **proxies**, not labels. A user may copy an answer to verify
it, regenerate because they want a different tone, or leave because they
were interrupted. Avoid inferring sensitive attributes or intent from
behavioral data without a legitimate basis and appropriate safeguards.

| Signal               | What it may indicate                         | What it does **not** prove                  |
| -------------------- | -------------------------------------------- | ------------------------------------------- |
| Positive rating      | User reports satisfaction                    | Factual correctness or safety               |
| Negative rating      | User reports a problem                       | Exact root cause                            |
| Task completed       | Workflow reached a defined success state     | Every answer claim was correct              |
| Retry / regeneration | First response may not have met expectations | Model failure without further evidence      |
| Long dwell time      | User spent time on the interaction           | Confusion, engagement, or success by itself |
| No feedback          | Nothing directly                             | Satisfaction or dissatisfaction             |


**Rule:** record the signal type and its limitations. Never silently
convert a proxy into a verified label.


<br/>


## 3. Design a Minimal Feedback Event

Collect only the fields needed to investigate, evaluate, and improve the
system. Establish the purpose and legal/policy basis before collecting
production content.

A minimal event might contain:

``` json
{
  "event_id": "evt_001",
  "timestamp": "2026-10-14T10:15:00Z",
  "system_version": "assistant-v3.2",
  "prompt_version": "prompt-17",
  "retrieval_version": "index-42",
  "signal_type": "task_outcome",
  "signal_value": "failed",
  "task_type": "document_qa",
  "failure_category": "unsupported_claim",
  "review_status": "unreviewed",
  "privacy_classification": "restricted",
  "retention_until": "2026-11-13T00:00:00Z"
}
```

This is an illustrative schema, not a universal standard. In real
systems, avoid including raw prompts, responses, documents, account
identifiers, or direct personal identifiers unless they are necessary,
authorized, and appropriately protected.

<br/>

### 3.1 Provenance and lineage

For every signal, preserve enough provenance to interpret it: -
**Source:** rating, automated validator, human review, or downstream
event. - **Time:** when the interaction and outcome occurred. - **System
identity:** model, prompt, retrieval index, tool, and application
versions where relevant. - **Definition:** what "success," "failure," or
a rating value means. - **Review status:** unreviewed, under
investigation, confirmed, rejected, or inconclusive. - **Data
handling:** classification, permitted purpose, access policy, and
expiry/retention rule.

Provenance prevents teams from treating a user opinion, an automated
heuristic, and a confirmed defect as interchangeable evidence.

<br/>

### 3.2 Data minimization and retention

Use the following controls:

1.  Define a specific evaluation purpose before collection.
2.  Prefer event metadata and structured categories over raw
    conversation text.
3.  Redact or transform direct identifiers and sensitive content when
    feasible.
4.  Restrict access by role and log access to sensitive records.
5.  Encrypt data in transit and at rest where appropriate.
6.  Set a retention period and delete or aggregate records when it
    expires.
7.  Keep evaluation datasets separate from general analytics when access
    needs differ.
8.  Verify that collection, reuse, and model-training use are permitted
    by applicable policy and law.
9.  Apply the same protections to exports, dashboards, notebooks, logs,
    and backups.

Pseudonymization is not the same as anonymization. Removing a name may
not prevent re-identification when records contain distinctive details.


<br/>


## 4. Production Monitoring and Sampling

Monitoring should combine aggregate health metrics with structured
review of sampled interactions. Aggregates can show that something
changed; case review helps explain why.

### 4.1 Monitor multiple dimensions

**Quality and task outcomes** - Explicit rating rates and rating
distribution. - Task completion, rejection, escalation, reopen, or
correction rates. - Structured-output validation failures. -
Human-confirmed correctness, groundedness, or safety failures. -
Abstention and clarification rates.

**Operational behavior** - Error and timeout rates. - Latency
percentiles, such as p50 and p95. - Throughput, token usage, and cost
per successful task. - Tool failures, retrieval failures, and dependency
availability.

**Distribution and coverage** - Task type, language, document/source
type, and workflow stage. - Input length and output length. - Rates of
missing, malformed, or unsupported inputs. - New categories or uncommon
cases not well represented in the offline dataset.

Use slices only when they are justified, privacy-preserving, and large
enough to avoid misleading conclusions or exposing individuals.

<br/>

### 4.2 Sampled failure review

A practical sampling design can combine:

-   **Random samples:** estimate ordinary production behavior without
    selecting only dramatic cases.
-   **Risk-based samples:** review high-impact workflows and known
    failure modes.
-   **Trigger-based samples:** inspect validator failures, repeated
    retries, escalations, or user reports.
-   **Shift-based samples:** review new input types or changed source
    distributions.

Keep the sampling method and selection probability when possible. A
sample deliberately enriched with failures is useful for diagnosis, but
its raw failure percentage is not an unbiased estimate of the production
failure rate.

<br/>

### 4.3 Distribution shift

A distribution shift occurs when production inputs or operating
conditions differ from those represented in the evaluation data.
Examples: - New terminology, languages, or document formats. - Changes
to the knowledge base or retrieval index. - A new customer workflow. -
Longer prompts or more tool-dependent requests. - A change in the
proportion of answerable and unanswerable questions.

Input drift is a **signal to investigate**, not proof that quality has
declined. If possible, measure outcome quality by relevant slices and
compare against a stable baseline.

<br/>

### 4.4 Delayed outcomes

Some outcomes arrive after the interaction: - A support ticket is
reopened days later. - A human audit confirms an error after a review
queue clears. - A user later corrects an extracted record. - A
downstream process rejects an answer asynchronously.

Track event time and outcome time separately. Recent cohorts may appear
better simply because failures have not yet surfaced. Compare cohorts
with similar follow-up windows, or mark recent results as provisional.


<br/>


## 5. Production Evaluation Workflow

A safe feedback-to-dataset workflow separates signal collection, triage,
verification, and regression testing.

``` mermaid
flowchart TD
    A[Production interaction] --> B[Collect permitted minimal event]
    B --> C[Apply access, retention, and privacy controls]
    C --> D[Aggregate metrics and sample cases]
    D --> E[Triage signal and investigate context]
    E --> F{Failure verified?}
    F -- No --> G[Reject, defer, or mark inconclusive]
    F -- Yes --> H[Redact or transform sensitive details]
    H --> I[Reviewer approves reusable test case]
    I --> J[Add to versioned regression dataset]
    J --> K[Run offline evaluation against baseline]
    K --> L{Release criteria met?}
    L -- No --> M[Block or roll back candidate]
    L -- Yes --> N[Controlled rollout and continued monitoring]
```

<br/>

### Workflow stages

1.  **Capture:** collect a permitted signal and minimal context.
2.  **Triage:** classify the case and assign severity.
3.  **Investigate:** determine whether the model, retrieval, tools, UI,
    or external systems caused the issue.
4.  **Verify:** use authorized evidence and qualified review to confirm
    the failure.
5.  **Sanitize:** remove unnecessary personal or confidential
    information; replace specific details with synthetic equivalents
    where possible.
6.  **Approve:** a reviewer checks that the test case is useful, valid,
    and safe to retain.
7.  **Version:** record the case ID, source category, review date,
    expected behavior, and dataset version.
8.  **Test:** run the case against the current baseline and candidate.
9.  **Decide:** use predefined release criteria; do not waive a critical
    safety or correctness gate because aggregate satisfaction improved.
10. **Monitor:** after deployment, check whether the fix works and
    whether it introduces regressions.

A production report should not automatically become a golden label. A
report is evidence to investigate; a reviewed case is a controlled
evaluation asset.


<br/>


## 6. Shadow Evaluation, Canary Rollout, and Controlled Experiments

These approaches answer different questions and carry different risks.

### 6.1 Shadow evaluation

A candidate system receives a copy of permitted production inputs while
the current system remains responsible for the user-visible result.
Candidate outputs are evaluated without being shown to users or
triggering real actions.

**Useful for:** checking compatibility, latency, failure patterns, and
offline-style quality on current traffic.

**Controls:** - Prevent candidate tool calls from producing external
side effects. - Enforce data permissions and purpose limitation for
duplicated inputs. - Control additional cost and load. - Do not assume
shadow traffic is harmless merely because outputs are hidden.

<br/>

### 6.2 Canary rollout

A candidate is deployed to a small, controlled portion of traffic, with
the existing system available as a fallback.

**Useful for:** validating live operational behavior and user-visible
effects at limited exposure.

A canary should have: - A defined eligible traffic segment. - A minimum
observation period and sufficient sample size. - Quality, safety,
reliability, and latency thresholds. - Clear stop and rollback
conditions. - A named owner and an operational rollback procedure.

Do not increase exposure just because a small sample has no observed
failures; rare failures require sufficient exposure to detect.

<br/>

### 6.3 Controlled experiments

A controlled experiment compares variants under a defined assignment
method and outcome plan. Random assignment can help reduce confounding
when it is ethical, permitted, and operationally feasible.

Specify in advance: - Hypothesis and primary metric. - Eligibility and
assignment unit. - Baseline and candidate versions. - Guardrail metrics
and critical failure conditions. - Minimum sample size or stopping
rule. - Analysis plan, including delayed outcomes and missing data.

Avoid changing several major components at once if the goal is to
attribute the result to one change. A higher rating rate does not
justify a release if correctness, safety, or task completion
deteriorates.

| Method                | User sees candidate output? | Main purpose                                      | Key caution                                |
| --------------------- | --------------------------- | ------------------------------------------------- | ------------------------------------------ |
| Shadow                | No                          | Evaluate candidate on live-like inputs            | Privacy, side effects, added cost          |
| Canary                | Yes, for limited traffic    | Limit exposure while checking production behavior | Needs explicit rollback gates              |
| Controlled experiment | Yes, by assigned variant    | Estimate comparative effect                       | Confounding, sample size, delayed outcomes |


<br/>


## 7. Failure Triggers, Escalation, and Rollback

Define triggers before deployment. Examples include: - Any confirmed
critical safety or privacy incident. - A rise above a predefined
threshold in task failure or schema rejection. - A statistically or
operationally meaningful quality regression on a high-impact slice. -
Error, timeout, or p95 latency exceeding a service-level objective. - A
sustained increase in unsupported claims or failed citations. - A
material distribution shift combined with insufficient evaluation
coverage.

A trigger should lead to an explicit action: investigate, pause rollout,
reduce traffic, revert to the previous version, or disable a risky
capability. The response depends on severity and confidence.

<br/>

### Suggested decision states

-   **Continue:** required metrics are within limits and evidence is
    adequate.
-   **Investigate:** a signal changed, but cause or significance is
    uncertain.
-   **Pause / rollback:** a predefined critical threshold is breached.
-   **Inconclusive:** sample size, label maturity, or data quality is
    insufficient to make a reliable decision.

Do not silently treat missing telemetry as a pass. Missing or delayed
evidence should be visible in the decision record.


<br/>


## 8. Avoid Common Interpretation Errors

### Satisfaction is not correctness

A friendly, confident, or convenient answer can still be false,
ungrounded, or unsafe. Ratings measure reported experience, not
objective truth.

<br/>

### Completion is not universal quality

A workflow can complete even when one claim is wrong. Define the outcome
precisely and pair it with checks for high-risk properties.

<br/>

### Correlation is not causation

A quality change after deployment may be due to traffic mix,
seasonality, data-source changes, or an unrelated dependency. Use
matched comparisons or controlled assignment where appropriate.

<br/>

### Alert volume is not a production rate

A failure-enriched sample deliberately over-represents failures. Use
sampling weights or a separate representative sample for rate estimates.

<br/>

### Recent outcomes may be immature

Delayed labels can make current cohorts appear artificially healthy.
Mark provisional cohorts and compare like-for-like follow-up windows.

<br/>

### Drift is not automatically degradation

A distribution change indicates that the system may be operating outside
familiar conditions. It should trigger targeted evaluation, not an
automatic conclusion that the model is worse.


<br/>


## 9. Example: Feedback Event to Reviewed Regression Case

Suppose users report that a knowledge-base assistant gives a confident
answer unsupported by the available document.

**Initial signal:** a negative rating and a report of an unsupported
claim.

**Investigation:** 1. Confirm the relevant application and retrieval
versions. 2. Inspect authorized evidence and the retrieved passages. 3.
Determine whether the evidence was absent, overlooked, stale, or
contradicted. 4. Classify the cause and severity. 5. Remove
user-identifying and confidential details that are not needed. 6. Create
a minimal test with a synthetic question and a representative document.
7. Define expected behavior: answer only from supported evidence, cite
the supporting passage, or abstain when evidence is insufficient. 8.
Have a reviewer validate the expected behavior. 9. Add the case to a
versioned regression dataset. 10. Verify the candidate against this case
and the broader suite before canary rollout.

This process preserves the lesson without retaining an entire private
conversation unnecessarily.


<br/>


## 10. Practice

### Exercise A --- Classify the signal

For each observation, identify whether it is an explicit rating,
observed task outcome, behavioral proxy, operational metric, or verified
label.

1.  A user clicks thumbs-down.
2.  A downstream validator rejects the generated JSON.
3.  A user regenerates the answer three times.
4.  The p95 latency rises from 1.2 seconds to 2.0 seconds.
5.  A qualified reviewer confirms that a cited sentence does not support
    the answer.

<br/>

### Exercise B --- Design the workflow

A customer-support assistant has more reopened tickets after a prompt
update. Design a feedback-to-dataset workflow. Include: - Minimal event
fields and provenance. - A sampling strategy. - How you will distinguish
model failures from unrelated support-process failures. - Privacy and
retention controls. - A regression case approval process. - Rollback
triggers.

<br/>

### Exercise C --- Choose the rollout method

Choose shadow evaluation, canary rollout, or a controlled experiment for
each goal and explain why:

1.  Test a new candidate against current traffic without showing its
    answers.
2.  Expose a new prompt to a small portion of eligible users with a fast
    rollback.
3.  Estimate whether a response-format change improves successful task
    completion compared with the baseline.

<br/>

### Exercise D --- Interpret the evidence

A new version increases positive ratings by 8%, but verified unsupported
claims also rise from 1.0% to 1.8%. What should the team do?

**Answer key**

-   **A1:** Explicit rating. It expresses reported experience, not
    correctness.
-   **A2:** Observed task outcome or validator signal. It indicates a
    contract failure but may require investigation to locate the cause.
-   **A3:** Behavioral proxy. Repeated regeneration suggests possible
    dissatisfaction but does not establish why.
-   **A4:** Operational metric. Check sample size, workload, and
    service-level limits.
-   **A5:** Verified label, assuming the reviewer followed a defined
    protocol and had suitable evidence.
-   **B:** Capture a permitted event with task ID or pseudonymous
    correlation ID, time, system/prompt versions, reopen outcome, and
    review status. Use a representative sample plus targeted review of
    reopened tickets. Inspect ticket history and downstream workflow to
    separate answer defects from unrelated causes. Minimize or redact
    content, restrict access, set expiry, and require reviewer approval
    before converting cases into reusable tests. Define a rollback
    trigger in advance for a critical confirmed failure or a sustained
    breach of the task-failure threshold.
-   **C1:** Shadow evaluation. It avoids exposing candidate outputs but
    still requires privacy, cost, and side-effect controls.
-   **C2:** Canary rollout. It limits user exposure and should have
    explicit guardrails and rollback conditions.
-   **C3:** Controlled experiment, if assignment is appropriate and the
    metric and analysis plan are specified in advance.
-   **D:** Do not approve the release based on ratings alone.
    Investigate the increase in unsupported claims, inspect affected
    slices, and pause or roll back if the predefined correctness gate is
    breached. Ratings are useful evidence, but they cannot override a
    critical quality requirement.


<br/>


## 11. Checkpoint

**Question:** Explain how online evidence complements rather than
replaces offline assessment.

**Model answer:**

Online evidence reveals real-world behavior, emerging failure modes,
changes in input distributions, operational issues, and outcomes that
may arrive after deployment. However, ratings and behavioral signals are
noisy, outcomes may be confounded or delayed, production samples may be
biased, and raw interactions can contain private information. Therefore,
teams should collect minimal permitted data, preserve provenance,
monitor representative samples and targeted failures, investigate and
verify reports, and convert sanitized, reviewed cases into versioned
regression datasets. Offline evaluation then provides controlled,
repeatable comparisons of candidate changes, while shadow evaluation and
guarded rollout help assess production behavior. Release decisions
should combine these sources with explicit thresholds, uncertainty
handling, and rollback criteria. Online feedback expands coverage; it
does not replace reviewed ground truth, controlled experiments, or
safety and correctness gates.


<br/>


## 12. Key Takeaways

-   Explicit ratings, task outcomes, behavioral proxies, and verified
    labels are different evidence types.
-   Production feedback needs provenance, purpose limitation, access
    controls, minimization, and retention rules.
-   Random samples help estimate typical behavior; targeted samples help
    diagnose failures.
-   Distribution shifts and delayed outcomes must be accounted for when
    interpreting metrics.
-   Shadow evaluation, canary rollout, and controlled experiments serve
    different purposes.
-   Only verified, sanitized, reviewed cases should become durable
    regression assets.
-   User satisfaction is important, but it cannot independently
    establish correctness, groundedness, or safety.
-   Use online evidence to discover and prioritize problems, and offline
    evaluation to compare changes reproducibly.

<br/>

## Further Reading

-   Google SRE Book --- monitoring distributed systems and alerting
    principles.
-   NIST AI Risk Management Framework --- governance, measurement,
    monitoring, and risk management.
-   OWASP Top 10 for LLM Applications --- risks relevant to production
    LLM systems.
-   Your organization's privacy, data-retention, incident-response, and
    release-management policies.
