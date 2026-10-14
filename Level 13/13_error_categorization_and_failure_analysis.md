# Chapter 13: Error Categorization and Failure Analysis

## Learning Objectives

By the end of this chapter, you should be able to:

-   Classify failures across a Generative AI application pipeline.
-   Separate observed symptoms from root-cause hypotheses.
-   Analyze failure patterns across relevant dataset slices.
-   Prioritize remediation using severity, frequency, user impact, and
    feasibility.
-   Propose targeted changes and specify evidence that would confirm or
    reject each suspected cause.

<br/>

## 1. Why Failure Analysis Matters

An aggregate score tells you how often a system succeeds, but it rarely
tells you **why it fails** or what to change. Failure analysis converts
individual bad outcomes into structured evidence that can guide
engineering work.

A useful failure-analysis loop is:

1.  Detect and preserve a failed case.
2.  Record the observable symptom and expected behavior.
3.  Assign one or more provisional failure categories.
4.  Form a testable root-cause hypothesis.
5.  Gather evidence that can confirm or reject the hypothesis.
6.  Choose a targeted intervention.
7.  Rerun the failed case and a regression set.
8.  Record whether the intervention improved the intended outcome
    without creating new regressions.

A failure category is a label for *where or how the failure appears*. A
root-cause hypothesis is an explanation that still needs evidence. Do
not treat the category itself as proof of cause.

<br/>

## 2. A Pipeline-Oriented Failure Taxonomy

A typical GenAI application may contain input handling, retrieval,
context construction, generation, parsing, validation, and
infrastructure components. Categorize failures in a way that maps to
components your application actually has.

``` mermaid
flowchart TD
    A[Input] --> B[Parsing and normalization]
    B --> C[Retrieval]
    C --> D[Context assembly]
    D --> E[Generation]
    E --> F[Output parsing]
    F --> G[Validation]
    A -. service dependency .-> H[Infrastructure and orchestration]
    B -. service dependency .-> H
    C -. service dependency .-> H
    D -. service dependency .-> H
    E -. service dependency .-> H
    F -. service dependency .-> H
    G -. service dependency .-> H
```

The diagram is conceptual. Real systems may have parallel branches,
retries, tools, moderation, caches, or multiple validation stages.

<br/>

### 2.1 Input failures

**Typical symptoms**

-   Required fields are missing or malformed.
-   Input exceeds supported length or contains unexpected encodings.
-   User intent is ambiguous, contradictory, or outside the supported
    task.
-   A language, file type, or modality is not supported by the
    configured workflow.

**Possible causes to investigate**

-   Client-side or API validation is incomplete.
-   Normalization changes meaning or removes important characters.
-   The supported-input contract is unclear.
-   A routing rule sends a request to the wrong workflow.

**Evidence to collect**

-   Original input and normalized input, with sensitive data
    appropriately redacted.
-   Validation errors and routing decisions.
-   Input length, language, file type, and relevant metadata.
-   Expected behavior for malformed, ambiguous, and unsupported
    requests.

**Potential targeted changes**

-   Add explicit schema and size validation.
-   Improve normalization tests for multilingual text and special
    characters.
-   Route ambiguous requests to clarification rather than guessing.
-   Return a clear unsupported-input response when a capability is
    unavailable.

<br/>

### 2.2 Parsing and normalization failures

Parsing may apply to uploaded documents, tool results, model outputs, or
structured user inputs.

**Typical symptoms**

-   A document produces empty or garbled text.
-   JSON decoding fails.
-   A valid value is converted into the wrong type.
-   Tables, headings, page order, or character boundaries are lost.

**Possible causes to investigate**

-   An incorrect parser or encoding assumption.
-   A schema mismatch or malformed output.
-   OCR or extraction quality issues.
-   A normalization rule that is too aggressive.

**Evidence to collect**

-   Raw input, parser version, extracted representation, and error logs.
-   Parse success rate by file type and source.
-   A small manually inspected sample of correct and incorrect
    extractions.
-   Whether the same input succeeds with a different supported parser.

**Potential targeted changes**

-   Add parser-specific regression fixtures.
-   Validate types and required fields before downstream use.
-   Add OCR or alternate extraction only when the file and quality
    evidence justify it.
-   Preserve raw content and intermediate representations for debugging,
    subject to retention and privacy rules.

<br/>

### 2.3 Retrieval failures

Retrieval failures occur when a search or retriever does not return
evidence needed for the task.

**Typical symptoms**

-   The correct document or passage is absent from the top-*k* results.
-   Results are irrelevant, redundant, stale, or from the wrong
    collection.
-   A query returns no results even though the corpus contains relevant
    evidence.
-   A document is returned despite being unauthorized for the requesting
    user.

**Possible causes to investigate**

-   Query wording does not match the corpus vocabulary.
-   Chunk boundaries split key evidence.
-   Metadata filters, access controls, or index configuration are
    incorrect.
-   Embedding, lexical-search, ranking, or index versions are
    mismatched.
-   The required document was never ingested or the index is stale.

**Evidence to collect**

-   Query, filters, corpus/index version, and ranked document IDs.
-   Relevance judgments for known test queries.
-   Retrieval metrics such as Recall@k, Precision@k, MRR, or nDCG, where
    appropriate.
-   Ingestion timestamps and permission-filter decisions.
-   A direct check that the expected source exists in the indexed
    corpus.

**Potential targeted changes**

-   Repair ingestion or index freshness if the expected document is
    missing.
-   Tune query rewriting, chunking, filters, or ranking only after
    locating the failure.
-   Add targeted examples for vocabulary mismatch.
-   Fix authorization filters as a high-priority security defect; do not
    solve it by exposing more documents.

<br/>

### 2.4 Context construction failures

A retriever can find useful evidence while the generation model still
receives a poor context.

**Typical symptoms**

-   Relevant evidence is retrieved but omitted from the final prompt.
-   Important content is truncated.
-   Context contains duplicate, contradictory, stale, or low-value
    passages.
-   Source identifiers or metadata needed for citations are lost.

**Possible causes to investigate**

-   Context-budget logic removes important passages.
-   Ranking or ordering places critical evidence poorly.
-   Deduplication or compression drops qualifiers.
-   Metadata formatting makes source boundaries unclear.
-   Context assembly mixes documents across users, tenants, or
    permissions.

**Evidence to collect**

-   Retrieved candidates versus the exact context sent to the model.
-   Token counts, truncation markers, ordering, and source metadata.
-   A comparison between failures with full evidence and the production
    context.
-   Tenant and authorization metadata, checked without exposing
    restricted content.

**Potential targeted changes**

-   Correct token-budget and truncation policies.
-   Preserve source IDs, dates, and qualifiers during compression.
-   Deduplicate repeated passages and make document boundaries explicit.
-   Add tests that assert required evidence survives context assembly.
-   Treat cross-tenant context leakage as a security incident, not
    merely a relevance issue.

<br/>

### 2.5 Generation failures

Generation failures occur when the model receives an adequate
input/context but produces an unsuitable answer.

**Typical symptoms**

-   The answer is factually wrong or unsupported.
-   The answer ignores instructions or relevant evidence.
-   The response is incomplete, irrelevant, overly verbose, or
    inconsistent.
-   The model should abstain or ask a clarifying question but instead
    guesses.
-   The answer is fluent but contradicts the supplied evidence.

**Possible causes to investigate**

-   Prompt instructions are ambiguous or conflict with other
    instructions.
-   The model lacks capability for the task or language.
-   Sampling settings introduce undesirable variability.
-   The context is difficult to interpret even though the needed facts
    are present.
-   The task requires a different model, tool, or workflow.

**Evidence to collect**

-   Exact prompt, context, model/version, parameters, tool results, and
    output.
-   Human-reviewed examples with a task-specific rubric.
-   Repeated runs when stochastic variability is relevant.
-   Comparison against a controlled baseline using the same cases and
    settings.

**Potential targeted changes**

-   Clarify the instruction and define the expected answer format.
-   Add examples only if they address a demonstrated failure pattern.
-   Use tools or deterministic computation for tasks better handled by
    them.
-   Add an abstention or clarification path for unsupported or ambiguous
    requests.
-   Evaluate an alternative model only under a controlled comparison.

<br/>

### 2.6 Output parsing and validation failures

These failures occur after generation when the response must satisfy a
machine-readable contract or business rule.

**Typical symptoms**

-   Invalid JSON or malformed structured output.
-   Required keys are missing or values use unsupported types.
-   Values parse successfully but violate business rules.
-   An enum, date, identifier, or reference is invalid.
-   A schema-valid answer contains incorrect semantic values.

**Possible causes to investigate**

-   The model was not given a clear output contract.
-   The parser is stricter or looser than the intended schema.
-   The schema does not represent real business constraints.
-   Validation errors are silently ignored or incorrectly retried.

**Evidence to collect**

-   Raw model response, parse error, schema version, and validation
    result.
-   Field-level error counts and business-rule failures.
-   Whether the failure is syntactic, structural, semantic, or
    domain-specific.
-   The retry path and final user-visible outcome.

**Potential targeted changes**

-   Use schema-constrained generation when supported and appropriate.
-   Validate output at the application boundary.
-   Provide bounded repair or retry logic for recoverable formatting
    errors.
-   Do not assume a valid schema guarantees factual correctness.
-   Fail safely when a critical business rule is violated.

<br/>

### 2.7 Infrastructure and orchestration failures

**Typical symptoms**

-   Timeouts, rate limits, connection failures, or provider errors.
-   Tool calls fail or return unexpected results.
-   Requests are duplicated, dropped, or completed out of order.
-   Retries increase latency or cost without improving success.
-   Logs or usage metadata are missing.

**Possible causes to investigate**

-   Capacity limits, network instability, dependency outages, or quota
    exhaustion.
-   Incorrect timeout and retry policies.
-   Circuit-breaker, queue, or concurrency configuration.
-   Non-idempotent retries or race conditions.
-   Incomplete observability.

**Evidence to collect**

-   Request and trace IDs, timestamps, status codes, retry history, and
    stage durations.
-   Provider and tool health signals.
-   Concurrency, queue depth, rate-limit responses, and timeout rates.
-   Success rates split by provider, region, model, and time window.

**Potential targeted changes**

-   Use bounded retries with backoff and jitter for retryable failures.
-   Set stage-specific timeouts and end-to-end deadlines.
-   Make retried operations idempotent where possible.
-   Add circuit breakers, fallbacks, or queue controls where justified.
-   Monitor missing telemetry as a data-quality problem in its own
    right.

<br/>

## 3. Symptoms, Categories, and Root-Cause Hypotheses

These are different levels of analysis:

| Level                 | Meaning                                             | Example                                                                         |
| --------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------- |
| Symptom               | What was observed                                   | Answer omitted the policy exception                                             |
| Failure category      | Where/how it manifested                             | Context construction or generation                                              |
| Root-cause hypothesis | A testable explanation                              | Context truncation removed the exception                                        |
| Evidence              | Observation that supports or weakens the hypothesis | The exception is present in retrieved passages but absent from the final prompt |
| Intervention          | A targeted change                                   | Preserve high-priority exception passages during context packing                |
| Verification          | A controlled test of the change                     | Rerun affected cases and the regression suite                                   |

A hypothesis should be specific enough that evidence could disprove it.
"The model is bad" is not a useful root-cause hypothesis. "The current
context packer truncates the final paragraph containing policy
exceptions when the prompt exceeds the configured token budget" is
testable.

<br/>

### Avoid premature attribution

One symptom can have multiple plausible causes. For example, a wrong RAG
answer could result from:

1.  Missing or stale source data.
2.  Retrieval failure.
3.  Context truncation.
4.  Conflicting evidence.
5.  Generation error.
6.  A faulty evaluator or reference answer.

Inspect the pipeline stage by stage before changing prompts or models.
Preserve uncertainty explicitly, for example:
`hypothesis_status = untested | supported | rejected | inconclusive`.

<br/>

## 4. A Practical Failure Record

Use a structured record so failures can be grouped, compared, and
replayed.

``` json
{
  "case_id": "rag-042",
  "task_type": "policy_question",
  "language": "en",
  "source_type": "pdf",
  "expected_behavior": "Explain the rule and its exception",
  "observed_symptom": "Exception omitted",
  "failure_categories": ["context", "generation"],
  "severity": "high",
  "user_impact": "Could lead to an incorrect policy decision",
  "hypothesis": "Context truncation removed the exception",
  "hypothesis_status": "untested",
  "evidence_needed": [
    "Retrieved passage IDs",
    "Exact model context",
    "Token and truncation logs"
  ],
  "proposed_change": "Preserve exception passage during context packing",
  "verification_plan": "Replay case and run policy-question regression set"
}
```

The values are illustrative. Avoid storing secrets, credentials, or
unnecessary personal data in evaluation records. Apply access controls,
redaction, retention limits, and approved logging policies.

<br/>

### Recommended fields

-   **Identity:** case ID, trace ID, dataset version, timestamp.
-   **Task context:** task type, language, input modality, source type,
    relevant segment.
-   **Expected/observed:** expected behavior, actual output, failure
    symptom.
-   **Classification:** primary category, secondary categories,
    severity.
-   **Diagnosis:** root-cause hypothesis, confidence/status, evidence
    for and against.
-   **Remediation:** proposed change, owner, feasibility, dependencies.
-   **Verification:** regression cases, metrics, pass/fail decision,
    experiment version.

Choose one primary category for reporting when practical, while
retaining secondary categories for failures that span stages. This
reduces double-counting without losing causal complexity.

<br/>

## 5. Slice Analysis: Find Where Failures Cluster

An aggregate failure rate can hide a serious localized problem. Group
results by dimensions that are relevant to the product and supported by
enough data.

Useful slices include:

-   **Task:** classification, extraction, summarization, question
    answering, tool use.
-   **Language:** language, locale, code-switching, script, dialect
    where relevant.
-   **Source type:** PDF, HTML, database record, scanned image, API
    response.
-   **Input characteristics:** short/long, ambiguous/clear, noisy/clean,
    in/out of distribution.
-   **Retrieval characteristics:** corpus, index version, query type,
    number of relevant passages.
-   **Generation configuration:** model/version, prompt version,
    temperature, tool configuration.
-   **Operational context:** provider, region, latency band, retry
    count, time window.
-   **User/workflow context:** permission class or workflow, only where
    necessary and privacy-compliant.

For each slice, report at least the number of evaluated cases, number of
failures, failure rate, and uncertainty where sample size matters.

$$
\text{Failure Rate}_{s} =
\frac{\text{Failed Cases in Slice }s}
{\text{Evaluated Cases in Slice }s}
$$

A slice with 4 failures out of 10 cases (40%) is not as stable an
estimate as 400 failures out of 1,000 cases (also 40%). Avoid ranking
slices by rate alone; examine denominators, case mix, severity, and
uncertainty.

<br/>

### Example slice table

| Slice                           | Evaluated | Failed | Failure rate | Initial interpretation                      |
| ------------------------------- | --------- | ------ | ------------ | ------------------------------------------- |
| English policy questions        | 200       | 12     | 6%           | Baseline slice                              |
| Mixed-language policy questions | 40        | 10     | 25%          | Investigate language handling; small sample |
| Scanned PDFs                    | 60        | 15     | 25%          | Inspect OCR and extraction path             |
| API records                     | 300       | 6      | 2%           | Lower observed failure rate                 |


These numbers are hypothetical. They suggest where to investigate, not
what the cause is. Do not infer that mixed-language input itself causes
the problem until controlled evidence supports that claim.

<br/>

### Slice-analysis cautions

-   **Small samples:** rates can vary sharply; report counts and
    uncertainty.
-   **Confounding:** a slice may also differ in task difficulty, source
    quality, or model configuration.
-   **Multiple comparisons:** searching many slices increases the chance
    of finding a misleading high rate.
-   **Selection bias:** only analyzing reported failures hides
    successful but difficult cases and unreported failures.
-   **Privacy:** avoid exposing sensitive attributes or creating
    unjustified user-level profiles.
-   **Actionability:** analyze slices that could lead to a concrete,
    safe intervention.

<br/>

## 6. Prioritize Failures for Remediation

Not every failure deserves the same engineering effort. Prioritization
should consider severity, frequency, user impact, and feasibility, while
explicitly elevating security, privacy, safety, and compliance risks.

A simple triage rubric:

| Dimension   | Low                             | Medium                       | High                                                                               |
| ----------- | ------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------- |
| Severity    | Cosmetic or minor inconvenience | Degrades task outcome        | Incorrect consequential action, security/privacy exposure, or major workflow break |
| Frequency   | Rare in representative traffic  | Recurs in a limited segment  | Common across cases or growing rapidly                                             |
| User impact | Easy to detect and recover      | Causes rework or delay       | Material harm, lost trust, or blocked workflow                                     |
| Feasibility | Expensive or uncertain fix      | Requires focused engineering | Clear, low-risk fix with a quick verification path                                 |


Do not use a single numeric score as a substitute for judgment. A
security or privacy failure may need immediate containment even if it is
rare. Frequency should be measured against a defined denominator and
time window.

If a lightweight score is useful for sorting ordinary bugs, define the
scales first and document the formula. For example:

$$
\text{Triage Score} =
\text{Severity} \times \text{Frequency} \times \text{User Impact}
$$

Feasibility can then help order items with similar impact. This score is
only a queueing aid; it must not downgrade mandatory security, safety,
privacy, or compliance work.

<br/>

### Prioritization workflow

1.  Contain urgent security, privacy, or safety failures.
2.  Rank remaining issues by severity and actual user impact.
3.  Estimate frequency from representative cases or production
    telemetry.
4.  Identify the likely affected workflows and whether users can
    recover.
5.  Estimate fix effort, confidence, dependencies, and regression risk.
6.  Choose a targeted intervention and define a success metric.
7.  Add the failed case to the regression suite.
8.  Reassess priority after the fix and new evidence.

<br/>

## 7. From Recurring Category to Targeted Change

Prefer the smallest intervention that addresses the demonstrated failure
mechanism.

| Recurring category   | Candidate intervention                          | Evidence needed before/after                            |
| -------------------- | ----------------------------------------------- | ------------------------------------------------------- |
| Input validation     | Add validation for a specific malformed field   | Failure count for that input pattern before/after       |
| Parsing              | Fix parser configuration or encoding handling   | Raw input and extracted output on known fixtures        |
| Retrieval            | Repair index freshness or tune ranking          | Expected document presence and retrieval metrics        |
| Context construction | Change token budgeting or preserve key evidence | Retrieved evidence versus final model context           |
| Generation           | Clarify instructions or add an abstention path  | Rubric scores on affected and regression cases          |
| Output validation    | Enforce schema and business rules               | Parse success and semantic/business-rule accuracy       |
| Infrastructure       | Adjust bounded retry or timeout policy          | Error rate, latency percentiles, duplicate side effects |
| Evaluator            | Repair rubric or reference labels               | Adjudicated examples and agreement with expert review   |


The table lists candidate interventions, not universal prescriptions.
Confirm the suspected mechanism first. For example, raising `top_k` is
not a general fix for every wrong RAG answer: it may increase noise and
cost if the missing evidence is caused by ingestion or filtering.

<br/>

## 8. Confirming or Rejecting a Root-Cause Hypothesis

For every recurring issue, state the hypothesis, the evidence that would
support it, evidence that would contradict it, and a discriminating
test.

### Example: policy exception omitted

**Symptom:** The answer states the general policy but omits a relevant
exception.

**Hypothesis A:** The exception is absent from the indexed corpus.

-   Support: the source document contains the exception, but the current
    index has no corresponding passage.
-   Reject: the correct passage exists in the index and can be retrieved
    directly.

**Hypothesis B:** Retrieval fails to rank the exception passage highly
enough.

-   Support: the passage exists, but it is consistently missing from
    top-*k* results for representative queries.
-   Reject: the passage is consistently retrieved in the tested cases.

**Hypothesis C:** Context construction drops the passage.

-   Support: the passage appears in retrieved candidates but not in the
    exact prompt sent to the model.
-   Reject: the complete passage and its qualifiers are present in the
    prompt.

**Hypothesis D:** Generation ignores evidence that is available.

-   Support: the exact prompt contains clear, sufficient evidence, but
    the answer repeatedly omits or contradicts it.
-   Reject: the evidence is absent, truncated, ambiguous, or
    contradicted elsewhere in the context.

A strong diagnostic test changes one relevant factor while keeping the
rest of the setup controlled. For instance, compare the production
context with a context that explicitly includes the exception passage.
If the answer improves, that supports a context-related explanation, but
it does not by itself prove which context-assembly rule caused the
original omission.

<br/>

## 9. Practical Failure-Analysis Workflow

``` mermaid
flowchart TD
    A[Collect failed case] --> B[Describe observable symptom]
    B --> C[Assign provisional category]
    C --> D[Form testable hypothesis]
    D --> E[Collect discriminating evidence]
    E --> F{Hypothesis supported?}
    F -- No --> G[Reject or revise hypothesis]
    G --> D
    F -- Yes --> H[Choose targeted intervention]
    H --> I[Replay failed cases]
    I --> J[Run regression and slice checks]
    J --> K{Improves target without unacceptable regressions?}
    K -- No --> L[Rollback or revise intervention]
    L --> D
    K -- Yes --> M[Document evidence and monitor]
```

The workflow is iterative. A supported hypothesis does not guarantee the
proposed fix is effective; intervention success must be measured
separately.

<br/>

## 10. Python: Build a Failure Summary

The following example groups evaluation records by primary failure
category and reports evaluated counts, failed counts, and failure rates.
It assumes each record has a boolean `failed` field and an optional
`primary_category`.

``` python
from collections import defaultdict
from typing import Any


def summarize_failures(
    records: list[dict[str, Any]],
    category_key: str = "primary_category",
) -> list[dict[str, Any]]:
    """Summarize failure rates by a single primary category.

    Records should represent evaluated cases. If a case can fail in
    multiple stages, retain secondary categories separately rather than
    counting the same case repeatedly in this summary.
    """
    groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {"evaluated": 0, "failed": 0}
    )

    for record in records:
        category = record.get(category_key) or "uncategorized"
        if "failed" not in record or not isinstance(record["failed"], bool):
            continue

        groups[category]["evaluated"] += 1
        groups[category]["failed"] += int(record["failed"])

    summary = []
    for category, counts in groups.items():
        evaluated = counts["evaluated"]
        failed = counts["failed"]
        summary.append({
            "category": category,
            "evaluated": evaluated,
            "failed": failed,
            "failure_rate": failed / evaluated if evaluated else None,
        })

    return sorted(
        summary,
        key=lambda row: (
            row["failure_rate"] is not None,
            row["failure_rate"] or 0,
            row["failed"],
        ),
        reverse=True,
    )


example_records = [
    {"case_id": "1", "primary_category": "retrieval", "failed": True},
    {"case_id": "2", "primary_category": "retrieval", "failed": False},
    {"case_id": "3", "primary_category": "generation", "failed": True},
    {"case_id": "4", "primary_category": "generation", "failed": True},
    {"case_id": "5", "primary_category": "generation", "failed": False},
]

for row in summarize_failures(example_records):
    print(row)
```

**Interpretation:** This summary identifies categories with high
observed failure rates. It does not establish root cause or prioritize
by severity. Add slice dimensions, confidence intervals, case-mix
checks, and severity/user-impact data before making a high-stakes
decision. The example also assumes the input list contains the full
intended evaluation population; filtering only failed cases would make
the denominator invalid.

<br/>

## 11. Practice

### Exercise 1: Classify the failure

A RAG application answers a policy question incorrectly. The expected
paragraph exists in the source PDF, but the extracted text contains
broken words and omits a line.

1.  What is the observed symptom?
2.  Which failure category should be investigated first?
3.  What evidence would help confirm the suspected cause?
4.  Suggest one targeted change and one regression test.

<br/>

### Exercise 2: Separate symptom from hypothesis

A structured-output endpoint returns a response with a missing required
field.

Write: - One symptom statement. - Two distinct root-cause hypotheses. -
One piece of evidence that could distinguish the hypotheses. - One
targeted intervention for each hypothesis, conditional on evidence.

<br/>

### Exercise 3: Interpret slices

An evaluation reports: - Scanned PDFs: 18 failures out of 60 cases. -
API records: 12 failures out of 600 cases. - Mixed-language queries: 8
failures out of 25 cases.

1.  Calculate each failure rate.
2.  Which slices deserve investigation first, and why?
3.  Why would it be premature to conclude that source type or language
    is the root cause?
4.  What additional fields or controlled tests would help isolate the
    cause?

<br/>

### Exercise 4: Prioritize a queue

A team has three issues:

-   Issue A: frequent formatting defect, low user impact, simple fix.
-   Issue B: rare cross-tenant document exposure, severe security
    impact.
-   Issue C: moderate rate of incorrect answers in a high-volume
    workflow, medium-to-high user impact, expensive fix.

Propose an order of action. Explain why a simple frequency-weighted
score may be unsafe.

<br/>

### Exercise 5: Design a discriminating test

The answer omits a relevant passage. The passage is in the indexed
corpus, but you do not yet know whether retrieval, context assembly, or
generation is responsible.

Design a sequence of checks that isolates these stages without changing
multiple variables at once.

<br/>

## 12. Answer Key

### Exercise 1

1.  Symptom: the answer is incorrect because a required policy detail is
    unavailable or not used.
2.  Start with document parsing/extraction because the extracted text is
    visibly corrupted and omits source content.
3.  Compare the source PDF, extracted text, parser/OCR logs, and
    downstream indexed passage. Confirm whether the missing line
    survives ingestion.
4.  Candidate change: correct extraction/OCR configuration for the
    affected PDF pattern. Regression test: add the document as a fixture
    and assert that the required line appears in extracted text and is
    retrievable.

<br/>

### Exercise 2

-   Symptom: output lacks a required field.
-   Hypothesis A: the model did not emit the field.
-   Hypothesis B: the parser or post-processing step removed or renamed
    it.
-   Distinguishing evidence: compare raw model output with the parsed
    application object and validation errors.
-   Conditional interventions: improve schema-constrained generation or
    prompt contract if the raw output is missing the field; repair
    parser mapping if the raw output contains it but the parsed object
    does not.

<br/>

### Exercise 3

-   Scanned PDFs: $18/60 = 30\\%$.
-   API records: $12/600 = 2\\%$.
-   Mixed-language queries: $8/25 = 32\\%$.
-   Investigate the scanned-PDF and mixed-language slices because their
    observed rates are high, but retain the counts and uncertainty.
    Their small samples make estimates less stable.
-   The slices may differ in task difficulty, input length, source
    quality, model routing, or overlapping characteristics.
-   Inspect extraction output, language routing, task mix, prompt/model
    versions, and case-level traces. Compare matched cases or run
    controlled tests that vary one factor at a time.

<br/>

### Exercise 4

Contain Issue B immediately because cross-tenant exposure is a critical
security issue even if rare. Then assess Issue C based on user impact,
workflow volume, and whether a mitigation can reduce risk while a
durable fix is developed. Issue A can be fixed quickly, particularly if
it affects a broad user population, but it should not displace urgent
containment. A frequency-weighted score can bury rare catastrophic
failures.

<br/>

### Exercise 5

1.  Confirm the expected passage exists in the source and current index.
2.  Run the query and inspect ranked retrieval results, filters, and
    permissions.
3.  Compare retrieved candidates with the exact assembled model context.
4.  If the passage is missing from retrieval, investigate ingestion,
    query, filters, and ranking.
5.  If it is retrieved but absent from context, investigate token
    budgets, ordering, deduplication, and compression.
6.  If it is present clearly in context, inspect prompt instructions and
    the generated answer; repeat a controlled test if stochastic
    variability matters.
7.  After the targeted fix, rerun the failed case, representative cases
    in the affected slice, and the full relevant regression set.

<br/>

## 13. Checkpoint: Evidence-Based Diagnosis

**Task:** Identify what evidence would confirm the suspected cause.

For a recurring failure, complete this template:

-   **Observed symptom:** What exactly happened?
-   **Primary category:** Where did the failure manifest?
-   **Root-cause hypothesis:** What specific mechanism might explain it?
-   **Supporting evidence:** What observations would support the
    hypothesis?
-   **Contradictory evidence:** What observations would weaken or reject
    it?
-   **Discriminating test:** What controlled check separates this
    hypothesis from alternatives?
-   **Targeted change:** What is the smallest plausible intervention?
-   **Success measure:** Which metric or case-level outcome should
    improve?
-   **Regression checks:** What must not get worse?
-   **Priority rationale:** How severe, frequent, impactful, and
    feasible is the issue?
-   **Decision:** Fix, investigate further, monitor, or defer---and why?

<br/>

### Model checkpoint answer

-   **Observed symptom:** A policy answer omits a required exception.
-   **Primary category:** Undetermined until the pipeline is inspected;
    possible retrieval, context, or generation failure.
-   **Root-cause hypothesis:** Context assembly removes the exception
    passage under the token budget.
-   **Supporting evidence:** The passage appears in retrieved candidates
    but not in the exact model context, with a corresponding truncation
    or selection log.
-   **Contradictory evidence:** The complete passage appears in the
    exact model context with its qualifying conditions intact.
-   **Discriminating test:** Replay the same case with the original
    context and with a controlled context that explicitly includes the
    exception, keeping model and generation settings fixed.
-   **Targeted change:** If the hypothesis is supported, update context
    selection to preserve high-priority exception passages.
-   **Success measure:** Higher exception coverage and policy-answer
    correctness on the affected test set.
-   **Regression checks:** Context token usage, latency, citation
    support, unrelated policy cases, and permission boundaries.
-   **Priority rationale:** Prioritize according to the consequence of
    an omitted exception, observed frequency, affected workflow volume,
    and fix feasibility. Elevate any security or compliance risk.
-   **Decision:** Do not attribute the failure to context truncation
    until the retrieved candidates and exact prompt provide supporting
    evidence.

<br/>

## Key Takeaways

-   A failure label organizes observations; it does not prove root
    cause.
-   Preserve the exact input, intermediate artifacts, configuration, and
    output needed to replay a case.
-   Analyze both overall performance and meaningful slices, including
    denominators.
-   Use discriminating tests to separate retrieval, context, generation,
    validation, and infrastructure causes.
-   Prioritize severe security, privacy, safety, and compliance failures
    independently of raw frequency.
-   A fix is successful only when the target failure improves and
    relevant regression checks remain acceptable.

<br/>

## Further Reading

-   [OpenTelemetry Documentation](https://opentelemetry.io/docs/) ---
    traces, metrics, and logs for diagnosing distributed systems.
-   [Google SRE Book: Monitoring Distributed
    Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
    --- service signals and operational diagnosis.
-   [scikit-learn: Model
    Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
    --- evaluation metrics and their interpretation.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- risk-aware evaluation and governance.


<br/>



**Chapter 13 complete.** The next chapter is **Experiment Tracking and
Reproducibility**.
