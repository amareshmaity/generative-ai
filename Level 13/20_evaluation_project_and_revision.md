# Chapter 20: Evaluation Project and Revision

## Learning Objectives

By the end of this chapter, you should be able to:

-   Build a reproducible evaluation suite for one Generative AI
    application.
-   Compare two prompts, models, or configurations on the same
    evaluation cases.
-   Evaluate retrieval separately from answer generation in a RAG
    system.
-   Add regression checks and implement a justified quality/resource
    optimization.
-   Document failures, uncertainty, release criteria, and remaining
    limitations.
-   Defend whether a candidate should be adopted, revised, rejected, or
    evaluated with more data.

<br/>

## 1. Project Overview

This capstone brings together the evaluation and optimization workflow
from the previous chapters. Choose one GenAI application and create an
evaluation process that another engineer can run and interpret.

Possible applications include:

-   A retrieval-augmented generation (RAG) knowledge-base assistant.
-   A document summarizer.
-   A structured information extraction service.
-   A support-response drafting assistant.
-   A question-answering tool that must abstain when evidence is
    insufficient.

Keep the project narrow enough to measure. Define the task, intended
users, expected behavior, critical failure modes, and deployment
constraints before comparing candidates.

<br/>

### Deliverables

1.  A versioned evaluation dataset with documented provenance.
2.  A baseline and candidate configuration.
3.  A reproducible runner or clearly documented execution procedure.
4.  Task-appropriate quality metrics and, where needed, human or
    LLM-judge review.
5.  Separate retrieval evaluation for RAG.
6.  Regression tests that detect a deliberately introduced failure.
7.  A resource and latency comparison.
8.  A decision report with uncertainty, release gates, and limitations.


<br/>


## 2. Define the Application and Its Risks

Write a concise task specification before creating test cases.

  -----------------------------------------------------------------------
  Item                                Questions to answer
  ----------------------------------- -----------------------------------
  Intended user                       Who will rely on the output?

  Task                                What input is accepted and what
                                      output is expected?

  Success                             What observable result counts as
                                      success?

  Evidence boundary                   What sources may the system use?

  Abstention                          When should it ask a question,
                                      escalate, or decline to answer?

  Critical failures                   Which errors must block release
                                      regardless of aggregate score?

  Resource budget                     What latency, throughput, and cost
                                      limits apply?

  Data handling                       What inputs, outputs, and traces
                                      may be retained?
  -----------------------------------------------------------------------

<br/>

### Example project: RAG knowledge-base assistant

**Task:** Answer questions using an approved knowledge base, cite
supporting passages, and abstain when the retrieved evidence does not
support an answer.

**Candidate comparison:** Baseline prompt versus revised prompt. Keep
the model, retrieval index, top-k, and evaluation cases fixed so that
the prompt change is the main independent variable.

**Potential critical failures:** - Unsupported factual claims. - Invalid
or misleading citations. - Revealing content the user is not authorized
to access. - Answering confidently when the evidence is insufficient.

This example is illustrative. Choose metrics and thresholds that fit the
actual application and risk profile rather than copying arbitrary
values.


<br/>


## 3. Build the Evaluation Dataset

A useful evaluation suite contains more than easy, typical examples.

Include representative cases such as:

-   Common, answerable requests.
-   Ambiguous or underspecified requests.
-   Unanswerable requests.
-   Conflicting, stale, or incomplete evidence.
-   Long inputs and edge cases.
-   Expected abstention, clarification, or escalation.
-   Known historical failures.
-   High-impact cases relevant to the application.

<br/>

### 3.1 Recommended case schema

A JSONL record can store one test case per line:

``` json
{
  "case_id": "kb_001",
  "task_type": "document_qa",
  "input": "What is the documented refund period?",
  "expected_behavior": "answer_with_evidence",
  "reference_answer": "The policy states a 30-day refund period.",
  "required_evidence_ids": ["policy_refund_v2"],
  "criticality": "high",
  "tags": ["answerable", "policy"],
  "review_status": "approved"
}
```

Keep private or confidential content out of the dataset unless its use
is authorized and necessary. Prefer synthetic or sanitized examples when
they preserve the failure mode.

<br/>

### 3.2 Dataset splits and leakage prevention

Use separate data for: - **Development:** create and debug prompts,
evaluators, and thresholds. - **Validation:** compare candidate changes
and tune settings. - **Held-out regression/final set:** check
generalization after choices are made.

Avoid repeatedly tuning against the final set. If every failure is used
to revise the candidate and the same set is repeatedly used to declare
success, the reported result becomes optimistically biased.

Version the cases, labels, source documents, retrieval index, and
evaluator instructions. Record additions and changes with a short
rationale.


<br/>


## 4. Establish a Baseline Before Changing Anything

The baseline is the reference against which the candidate is judged. Run
it before optimization and save its configuration and raw outputs.

Record at minimum:

-   Application and code version.
-   Model identifier and provider/version where available.
-   Prompt/template version.
-   Retrieval corpus/index version and retrieval settings, if
    applicable.
-   Decoding parameters, tools, and relevant dependencies.
-   Dataset version and case count.
-   Evaluator version and metric definitions.
-   Run date, environment, seeds where supported, and known
    nondeterminism.
-   Latency, token usage, failures, and cost inputs.

Do not rely only on a final aggregate score. Save per-case outputs and
errors so regressions can be traced to specific behaviors.


<br/>


## 5. Compare Candidates Fairly

Choose one primary change for the initial comparison.

Examples: - Prompt A vs. Prompt B. - Model A vs. Model B. - Retrieval
top-k of 4 vs. 8. - A full model vs. a smaller model. - A long prompt
vs. a concise prompt.

Use the same cases, references, scoring rules, and workload conditions.
Where possible, use paired comparisons: evaluate both candidates on each
same case. This reduces noise from differences in case difficulty.

If a configuration change also changes retrieval, model, and prompt
simultaneously, you may learn which configuration performs better, but
it will be harder to explain why. For diagnosis, change one major factor
at a time or use a planned factorial experiment.

<br/>

### Example results table

  --------------------------------------------------------------------------
  Metric                      Baseline            Candidate Interpretation
  --------------- -------------------- -------------------- ----------------
  Task success                     84%                  88% Candidate
                                                            improves the
                                                            observed rate

  Supported                        91%                  89% Candidate
  answers                                                   regresses on
                                                            evidence support

  Critical                           0                    1 Candidate
  failures                                                  violates the
                                                            example release
                                                            gate

  p95 latency                    1.8 s                1.4 s Candidate is
                                                            faster

  Cost per 1,000                  \$12                  \$9 Candidate is
  tasks                                                     less expensive
  --------------------------------------------------------------------------

These values are fictional and demonstrate a trade-off only. They are
not a recommended target or a claim about a real model. In this example,
a critical failure may block adoption even when average task success
improves.


<br/>


## 6. Choose Metrics That Match the Task

Use a small set of metrics that are interpretable and aligned with user
and business risks.

### 6.1 General GenAI metrics

-   **Task success:** did the application complete the intended task?
-   **Correctness:** are factual claims or extracted values correct?
-   **Relevance:** does the response address the request?
-   **Completeness:** are required points or fields present?
-   **Faithfulness / groundedness:** are claims supported by allowed
    evidence?
-   **Abstention quality:** does the system abstain when evidence is
    insufficient and answer when it is sufficient?
-   **Format validity:** does the response satisfy the required schema
    or output contract?
-   **Safety / policy compliance:** does it respect defined
    restrictions?
-   **Latency and cost:** what resources are required to deliver an
    acceptable result?

Use exact match or task-specific metrics where possible for
deterministic tasks. For open-ended outputs, use explicit rubrics and
validated human or judge assessments. Automated judge scores should be
calibrated against reviewed cases.

<br/>

### 6.2 Aggregate scores can hide critical failures

Report: - Overall metrics. - Critical failure counts. - Performance by
important slice. - Per-case regressions and improvements. - Sample size
and uncertainty. - Missing, invalid, and unreviewed outcomes.

Do not let a weighted average override a hard safety, privacy, or
correctness requirement.


<br/>


## 7. Evaluate Retrieval Separately in RAG

For a RAG application, end-to-end answer quality depends on at least two
stages:

1.  **Retrieval:** did the system retrieve the necessary and permitted
    evidence?
2.  **Generation:** did the answer use the available evidence correctly?

Measure retrieval using suitable relevance judgments and metrics such as
Recall@k, Precision@k, MRR, or nDCG. Document the relevance-labeling
protocol and the value of (k).

Then evaluate generated answers for correctness, relevance,
completeness, groundedness, citation support, and appropriate
abstention.

<br/>

### Diagnostic matrix

  -----------------------------------------------------------------------
  Retrieval result        Answer result           Likely interpretation
  ----------------------- ----------------------- -----------------------
  Required evidence       Correct, supported      Desired behavior
  retrieved               answer                  

  Required evidence       Unsupported or          Generation, context
  retrieved               incorrect answer        use, or
                                                  instruction-following
                                                  problem

  Required evidence       Incorrect answer        Retrieval failure may
  missing                                         be the primary cause;
                                                  generation may also
                                                  fail by not abstaining

  Required evidence       Appropriate abstention  Potentially correct
  missing                                         behavior, depending on
                                                  retrieval requirements

  Unauthorized evidence   Any answer              Permission or
  retrieved                                       retrieval-control
                                                  defect; treat as
                                                  critical where
                                                  applicable
  -----------------------------------------------------------------------

A good answer by coincidence does not prove retrieval worked. Likewise,
a bad answer cannot be attributed solely to generation if the necessary
evidence never reached the model.


<br/>


## 8. Add Regression Checks

Regression tests protect previously correct behavior while the system
changes.

Include: - Deterministic contract checks for schemas, required fields,
and tool arguments. - Known factual and evidence-grounding cases. -
Unanswerable questions that must trigger abstention. - Citation validity
and citation-support checks. - Historical failures converted into
reviewed test cases. - High-impact slices and critical safety/privacy
cases. - Latency and resource guardrails where measurable.

For nondeterministic outputs, avoid brittle full-string comparisons
unless the task truly requires exact text. Prefer structural checks,
semantic rubrics, explicit invariants, and repeated measurements where
needed.

<br/>

### 8.1 Demonstrate that the suite detects a regression

A regression demonstration should have two runs:

1.  Run the suite against a known-good baseline and confirm the expected
    tests pass.
2.  Introduce a deliberate, controlled defect in a test fixture or
    candidate configuration.
3.  Re-run the same suite and confirm the relevant assertion fails.
4.  Confirm the failure is classified and reported correctly.
5.  Remove the defect and verify that the suite returns to the expected
    state.

For example, create a test case that requires a citation. The baseline
response includes a valid supporting citation. The deliberately faulty
fixture removes the citation; a regression assertion checks for a
citation ID and marks the case as failed. This demonstrates the
evaluator itself can detect the targeted failure. It does not prove the
suite catches every possible production failure.


<br/>


## 9. Example Regression Test in Python

The following self-contained example tests a simple response contract.
It is deliberately small so that the regression behavior is visible. In
a real project, integrate the assertions with your test runner,
evaluator, and versioned dataset.

``` python
def validate_response(response, required_fields):
    if not isinstance(response, dict):
        return False, "response_not_object"

    missing = [field for field in required_fields if field not in response]
    if missing:
        return False, f"missing_fields:{','.join(missing)}"

    if not isinstance(response.get("answer"), str) or not response["answer"].strip():
        return False, "empty_answer"

    citations = response.get("citations")
    if not isinstance(citations, list):
        return False, "citations_not_list"

    return True, "ok"


required_fields = ["answer", "citations"]

good_response = {
    "answer": "The documented period is 30 days.",
    "citations": ["policy_refund_v2"]
}

ok, reason = validate_response(good_response, required_fields)
assert ok, reason
print("Baseline case passed")

# Deliberately introduced regression: citation list is missing.
regressed_response = {
    "answer": "The documented period is 30 days."
}

ok, reason = validate_response(regressed_response, required_fields)
assert not ok, "Regression should have been detected"
assert reason == "missing_fields:citations"
print("Regression detected:", reason)
```

Expected output:

``` text
Baseline case passed
Regression detected: missing_fields:citations
```

This checks contract completeness, not whether a citation actually
supports a claim. Citation support requires a separate evidence-aware
evaluator or human review.


<br/>


## 10. Implement One Justified Optimization

An optimization should be driven by measured evidence and should
preserve required quality.

Possible levers: - Shorten redundant prompt instructions. - Reduce
unnecessary context while retaining required evidence. - Tune retrieval
top-k based on retrieval and answer metrics. - Route simple requests to
a smaller model and complex requests to a stronger one. - Constrain
output length when shorter outputs still satisfy the task. - Cache
stable, permitted computations or repeated retrieval results. - Batch
requests or adjust concurrency within service limits.

<br/>

### Optimization procedure

1.  Identify a measured bottleneck or quality defect.
2.  State a hypothesis.
3.  Change one major factor where possible.
4.  Re-run the same evaluation cases.
5.  Compare quality, critical failures, latency, token usage, and cost.
6.  Check important slices and uncertainty.
7.  Adopt only if mandatory quality gates pass and the resource
    improvement is meaningful.

<br/>

### Example hypothesis

> The prompt contains repeated instructions that increase input tokens
> without improving evidence support. Removing duplicated wording should
> reduce input-token usage and latency while preserving groundedness and
> abstention behavior.

Test the hypothesis rather than assuming it is true. If the candidate
becomes cheaper but increases unsupported claims, it fails the quality
constraint.

<br/>

### Constrained decision rule

Let (Q) be a quality metric and (C) a resource cost. An optimization may
seek to minimize (C) subject to a quality floor:

$$
\min C(\theta)
\quad \text{subject to} \quad
Q(\theta) \geq Q_{\min}
$$

Here, (`\theta`{=tex}) represents the model/prompt/configuration choice.
Critical failures should be handled as hard constraints, not merely
included in an average score.


<br/>


## 11. Uncertainty and Fair Interpretation

An observed difference is not necessarily a reliable improvement.

Record: - Number of cases and number of valid evaluated outputs. -
Missing or failed runs and how they were handled. - Whether comparisons
were paired. - Confidence intervals or other appropriate uncertainty
estimates. - Variation across repeated runs for nondeterministic
systems. - Subgroup results for important slices. - Known evaluator
limitations and possible judge bias.

For binary outcomes, report the numerator and denominator, not only the
percentage. For example, "8 failures among 400 cases" is more
informative than "2% failure" alone.

For paired candidate comparisons, compare per-case outcomes and use a
suitable paired method, such as paired bootstrap for a metric
difference. Small samples and rare critical failures need special
caution: observing zero failures in a small sample does not prove the
true failure rate is zero.

If evidence is insufficient, mark the result **inconclusive** and
collect more representative data rather than declaring a winner.


<br/>


## 12. Release Criteria and Decision Categories

Define release gates before reviewing the final comparison.

A sample gate set might require: - All deterministic contract tests
pass. - No confirmed critical safety, privacy, or authorization
failure. - Correctness and groundedness meet defined floors. - No
unacceptable regression on required high-impact slices. - Latency and
cost remain within agreed budgets. - The sample size and evaluation
quality meet minimum requirements.

These are examples. Actual thresholds must come from the application's
requirements, risk assessment, and operating constraints.

<br/>

### Decision categories

  -----------------------------------------------------------------------
  Decision                When it is justified    Next action
  ----------------------- ----------------------- -----------------------
  **Adopt**               Mandatory gates pass;   Roll out according to
                          improvement is          deployment policy and
                          meaningful; evidence is monitor
                          adequate                

  **Revise**              A promising candidate   Modify the candidate
                          has a diagnosable,      and rerun affected plus
                          fixable failure         full required tests

  **Reject**              It violates a hard gate Keep the baseline or
                          or has an unacceptable  choose another approach
                          trade-off               

  **Assess with more      Results are uncertain,  Collect more cases or
  data**                  underpowered, immature, wait for delayed
                          or unrepresentative     outcomes
  -----------------------------------------------------------------------

A candidate should not be adopted merely because its average score is
higher. Decisions should account for critical failures, uncertainty,
resource budgets, and the consequences of error.


<br/>


## 13. Project Report Template

Complete this report using actual project measurements. Do not present
illustrative values as measured results.

### A. Application and intended behavior

-   **Application:**
-   **Intended users and task:**
-   **Evidence sources and permissions:**
-   **Expected behavior:**
-   **Required abstention/escalation behavior:**
-   **Critical failure modes:**

<br/>

### B. Dataset and reproducibility

-   **Dataset version and source:**
-   **Number of cases:**
-   **Coverage of typical, edge, unanswerable, and high-risk cases:**
-   **Train/development/validation/held-out separation, if applicable:**
-   **Privacy review and sanitization:**
-   **Model, prompt, retrieval, tool, and dependency versions:**
-   **Evaluator version and metric definitions:**
-   **Run configuration and known nondeterminism:**

<br/>

### C. Candidate comparison

-   **Baseline configuration:**
-   **Candidate configuration:**
-   **Primary hypothesis:**
-   **Metrics and denominators:**
-   **Baseline results:**
-   **Candidate results:**
-   **Per-case wins, ties, and regressions:**
-   **Important slice results:**
-   **Uncertainty and limitations:**

<br/>

### D. RAG evaluation, if applicable

-   **Retrieval corpus/index version:**
-   **Relevance-labeling method:**
-   **Retrieval metrics and k values:**
-   **Required evidence recall:**
-   **Answer correctness and groundedness:**
-   **Citation validity and support:**
-   **Failures attributable to retrieval, generation, or both:**

<br/>

### E. Regression demonstration

-   **Known-good tests passed:**
-   **Deliberate defect introduced:**
-   **Assertion expected to fail:**
-   **Observed failure and diagnostic message:**
-   **Defect removed and suite rechecked:**
-   **What this demonstration does not prove:**

<br/>

### F. Optimization and resource impact

-   **Measured bottleneck:**
-   **Change made:**
-   **Quality before and after:**
-   **Latency before and after:**
-   **Token usage/cost before and after:**
-   **Quality constraints preserved?:**
-   **Decision and rationale:**

<br/>

### G. Failures and release decision

-   **Most important failures:**
-   **Root cause and evidence confidence:**
-   **Critical gate results:**
-   **Release thresholds and sample requirements:**
-   **Decision: adopt / revise / reject / assess with more data**
-   **Rollback plan:**
-   **Remaining limitations and next experiment:**


<br/>


## 14. Practice

Complete the report template for one GenAI application. Run a baseline
and one candidate on the same versioned cases. Include raw per-case
outcomes and aggregate metrics.

Then perform a deliberate regression test: 1. Choose a critical,
testable invariant such as "every factual answer must include a valid
citation." 2. Confirm the baseline satisfies the invariant on the
relevant test case. 3. Deliberately remove or corrupt the citation in a
controlled fixture or test configuration. 4. Run the suite and capture
the failure message. 5. Restore the correct behavior and rerun the test.
6. Document what the test covers and what it cannot detect.

Finally, implement one measured optimization and decide whether the
trade-off is acceptable under your release gates.

<br/>

### Practice checklist

-   [ ] The task and critical risks are defined.
-   [ ] Dataset and evaluator versions are recorded.
-   [ ] Baseline and candidate use the same cases.
-   [ ] Metrics, denominators, and missing outcomes are explicit.
-   [ ] RAG retrieval is evaluated separately, where relevant.
-   [ ] The regression test passes on the good case and fails on the
    deliberate defect.
-   [ ] One optimization is measured for both quality and resource use.
-   [ ] Failure analysis and uncertainty are documented.
-   [ ] Release thresholds were defined before the decision.
-   [ ] The report contains a decision and a rollback plan.


<br/>


## 15. Checkpoint

**Question:** Defend whether the candidate should be adopted, revised,
rejected, or assessed with more data.

**Model answer framework:**

-   **Adopt** when the candidate passes every mandatory gate, shows a
    meaningful improvement or justified resource benefit, has adequate
    and representative evidence, and does not introduce unacceptable
    slice regressions.
-   **Revise** when failures have a plausible, testable remedy and the
    candidate has not crossed a non-negotiable boundary that rules it
    out.
-   **Reject** when a hard gate is breached, a critical failure is
    confirmed, or the resource improvement requires unacceptable loss of
    quality or safety.
-   **Assess with more data** when sample size, uncertainty, label
    maturity, or coverage prevents a defensible decision.

A defensible decision cites measured results, case counts, critical
failures, uncertainty, and the predefined release criteria. It separates
facts from hypotheses and explicitly states what evidence could change
the decision.


<br/>


## 16. Key Takeaways

-   Define the application, risks, and release criteria before comparing
    candidates.
-   Version the dataset, evaluator, prompts, model, retrieval assets,
    and run configuration.
-   Compare candidates on the same cases and retain per-case results.
-   For RAG, measure retrieval quality separately from generated-answer
    quality.
-   Regression suites should test known-good behavior and known failure
    modes.
-   A deliberate regression demonstration validates a specific check,
    not the completeness of the entire suite.
-   Optimize resource use only while preserving required quality and
    hard constraints.
-   Report uncertainty, denominators, slice behavior, and missing
    outcomes.
-   Choose among adopt, revise, reject, and assess with more data using
    predefined gates.
-   A reproducible evaluation report should let another engineer
    understand and rerun the decision.

<br/>

## Further Reading

-   NIST AI Risk Management Framework --- risk management and evaluation
    context.
-   Google SRE Book --- monitoring, service objectives, and release
    reliability.
-   scikit-learn documentation --- metrics, validation, and evaluation
    utilities.
-   Your chosen GenAI framework's documentation for tracing, evaluators,
    and dataset management.
-   Your organization's privacy, security, model governance, and release
    policies.
