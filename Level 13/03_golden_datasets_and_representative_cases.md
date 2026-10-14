# 03. Golden Datasets and Representative Cases

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Build an evaluation dataset that reflects typical use and important
    failure modes.
-   Record inputs, reference answers or evidence, expected labels/facts,
    and data provenance.
-   Separate development and model-selection data from a final held-out
    assessment set.
-   Reduce duplicate, source, user, and temporal leakage.
-   Version dataset records and labels, including uncertain or
    incomplete references.
-   Explain the user populations and failure modes that an evaluation
    dataset does not cover.

<br/>

## 2. What Is a Golden Dataset?

A **golden dataset** is a curated collection of test cases used to
evaluate a GenAI application against defined criteria. Each case
contains an input and enough reference information to determine whether
the output is acceptable.

Depending on the task, a case may include:

-   User prompt or application input.
-   Relevant source documents or evidence.
-   Reference answer, expected facts, label, or acceptable-answer
    criteria.
-   Metadata such as task category, language, source type, and risk
    level.
-   Provenance: where the example came from and how it was prepared.
-   Dataset and annotation versions.
-   Notes about ambiguity, missing evidence, or reviewer disagreement.

"Golden" does not mean that every reference is unquestionably correct.
References can be incomplete, ambiguous, stale, or wrong. A good dataset
records those limitations instead of hiding them.

<br/>

### 2.1 Why a curated dataset matters

Without a fixed evaluation dataset, comparing two prompts or models
becomes unreliable. If the candidate model sees easier questions than
the baseline, a higher score may reflect the sample rather than a real
improvement.

A versioned dataset helps teams:

-   Compare prompts, models, and configurations on the same cases.
-   Detect regressions after code or model changes.
-   Measure performance on difficult and high-risk scenarios.
-   Reproduce a previous evaluation as closely as the system allows.
-   Identify gaps in coverage before deployment.

A small dataset is useful for learning and early iteration, but it is
not proof of production reliability.

<br/>

## 3. Build Coverage, Not Just a Large Case Count

A dataset with thousands of nearly identical easy examples can be less
useful than a smaller, carefully designed set that covers distinct task
conditions.

Include a deliberate mix of case categories.

| Criterion          | 2 --- Acceptable                                                  | 1 --- Borderline                                              | 0 --- Failing                                        |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| Main issue         | Clearly states that report export fails                           | Mentions a report problem but is vague                        | Omits or changes the main issue                      |
| Actions and status | States that the issue was escalated and remains unresolved        | Mentions escalation but leaves status unclear                 | Claims it was resolved when it was not               |
| Factual fidelity   | Adds no unsupported details or promises                           | Uses ambiguous wording that could imply an unconfirmed detail | Invents a fix, refund, or resolution date            |
| Next steps         | Preserves the actual next step or clearly says none was specified | Gives a vague next step without changing the facts            | Invents an owner, deadline, or commitment            |
| Conciseness        | Includes decision-relevant details without repetition             | Some repetition or unnecessary detail                         | So verbose or incomplete that it defeats the purpose |


Adversarial cases should be designed for the actual application threat
model. They are not a substitute for a separate security assessment.

<br/>

### 3.1 Coverage dimensions

Case categories can be crossed with other dimensions:

-   User population or role.
-   Language and writing style.
-   Source type and document quality.
-   Task complexity.
-   Input length.
-   Risk or consequence level.
-   Freshness of the underlying information.
-   Supported versus unsupported requests.

Do not assume that one case represents an entire population or category.
Record which dimensions are represented and which remain missing.

<br/>

## 4. Define a Dataset Record

Use a stable schema so cases can be validated, filtered, reviewed, and
compared across versions.

A practical record can contain:

| Field               | Purpose                                                       |
| ------------------- | ------------------------------------------------------------- |
| `case_id`           | Stable identifier for the test case                           |
| `input`             | User request or application input                             |
| `context`           | Source evidence or retrieved passages, if applicable          |
| `reference`         | Reference answer, expected facts, label, or rubric            |
| `coverage_category` | Typical, difficult, ambiguous, unsupported, adversarial, etc. |
| `expected_behavior` | Answer, qualify, ask clarification, abstain, or escalate      |
| `provenance`        | Source, collection method, date, and permitted use            |
| `split`             | Development, validation/selection, or final held-out test     |
| `label_version`     | Version of the reference labels and annotation guidance       |
| `review_status`     | Reviewed, disputed, incomplete, or pending                    |
| `notes`             | Known ambiguity, assumptions, or limitations                  |

The exact schema depends on the application. A classification dataset
may need expected labels; a RAG dataset may need relevant document IDs
and evidence spans; a summarization dataset may need required facts and
prohibited claims instead of one exact reference sentence.

<br/>

### 4.1 Example JSONL records

JSON Lines (JSONL) stores one JSON object per line and is convenient for
versioned evaluation data.

``` json
{"case_id":"KB-001","input":"How do I reset my password?","context":["Approved password-reset procedure"],"reference":{"required_facts":["Use the official reset flow"],"prohibited_claims":["Ask the user to share their password"]},"coverage_category":"typical","expected_behavior":"answer","provenance":{"source":"approved_help_center","collected_on":"2026-09-01"},"split":"development","label_version":"1.0","review_status":"reviewed"}
{"case_id":"KB-002","input":"What is the deadline for a policy not covered by the available documents?","context":[],"reference":{"required_facts":["State that the deadline cannot be verified"],"prohibited_claims":["Invent a date"]},"coverage_category":"unsupported","expected_behavior":"abstain","provenance":{"source":"synthetic_case","created_on":"2026-09-01"},"split":"held_out_test","label_version":"1.0","review_status":"reviewed"}
```

These are illustrative records, not measured model results. For real
data, record the actual source identifiers and dates and ensure that
collection and use are permitted.

<br/>

## 5. References Are Not Always Single Answers

A reference can take different forms:

-   **Exact target:** A fixed string, identifier, or normalized value.
-   **Class label:** One label from a defined label set.
-   **Required facts:** Facts that must be present in an answer.
-   **Evidence references:** Document IDs, passages, or source spans
    that support an answer.
-   **Rubric:** Criteria and scoring anchors for open-ended responses.
-   **Expected behavior:** For example, ask a clarifying question or
    abstain because evidence is absent.
-   **Multiple acceptable answers:** A set of valid outcomes or a rule
    for judging equivalent responses.

For open-ended generation, a single "gold answer" can accidentally
reward copying and penalize valid alternatives. Store the facts and
constraints that matter, plus examples where helpful.

<br/>

### 5.1 Uncertain or incomplete references

When reviewers cannot confidently determine the correct answer:

1.  Mark the record as uncertain or disputed.
2.  Record the missing evidence or competing interpretations.
3.  Seek adjudication from an appropriate reviewer when feasible.
4.  Define how the case contributes to metrics---such as exclusion from
    a specific metric, separate reporting, or evaluation of abstention
    behavior.
5.  Preserve the original and revised label versions.

Do not silently remove difficult cases after seeing that a model failed
them. Changes to labels should be documented and applied consistently to
all candidates.

<br/>

## 6. Development, Selection, and Held-Out Assessment

Separate data by its role in the evaluation process.

``` mermaid
flowchart TD
    A[Collected and reviewed cases] --> B[Group related cases]
    B --> C[Development set]
    B --> D[Validation / selection set]
    B --> E[Final held-out test set]
    C --> F[Prompt and pipeline iteration]
    D --> G[Choose candidate configuration]
    F --> G
    G --> H[Freeze candidate and evaluation plan]
    H --> E
    E --> I[Final assessment report]
```

-   **Development set:** Used to inspect examples, debug the evaluator,
    and improve prompts or application logic.
-   **Validation/selection set:** Used to compare candidates and choose
    settings.
-   **Final held-out test set:** Reserved for final assessment after the
    candidate and evaluation plan are frozen.

If the same cases repeatedly guide prompt changes, they become part of
the effective development process. Their score can become optimistic and
no longer represent an independent final assessment.

<br/>

### 6.1 Split by the unit that can leak

A random row-level split is not always safe. Related examples should
often remain in the same split:

-   All chunks from the same source document.
-   Rephrasings or duplicates of the same question.
-   Multiple records from the same user or conversation, when
    user-specific patterns could leak.
-   Records from the same underlying event or case.
-   Time-linked examples when the evaluation is meant to simulate future
    use.

Choose the split strategy to match the deployment claim. If the goal is
to generalize to new documents, split by document---not merely by chunk.
If the goal is to generalize to future requests, a temporal split may be
more realistic.

<br/>

## 7. Leakage: How an Evaluation Becomes Misleading

**Data leakage** occurs when information that should be unavailable
during development or evaluation influences model selection or the final
assessment.

| Leakage type            | Example                                                                   | Prevention                                           |
| ----------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------- |
| Exact duplicate leakage | The same question appears in development and test sets                    | Normalize and deduplicate before splitting           |
| Near-duplicate leakage  | Test question is a paraphrase of a development example                    | Use similarity review and group related cases        |
| Source leakage          | Chunks from one document appear in both train/development and test        | Split by source document or source group             |
| User leakage            | The same user's related conversations occur in multiple splits            | Group by user when appropriate and permitted         |
| Temporal leakage        | A past evaluation uses facts published after the intended prediction time | Apply time-aware splits and snapshot source data     |
| Label leakage           | The input contains the expected answer or a derived label unintentionally | Audit features, prompts, metadata, and preprocessing |
| Selection leakage       | Repeatedly tuning against the final test set                              | Reserve a final set and limit its use                |

For RAG systems, be especially clear about whether the evaluation is
testing retrieval over a fixed corpus, generalization to new documents,
or freshness against changing content. These are different evaluation
questions.

<br/>

### 7.1 Deduplication without destroying valid diversity

Deduplication should remove accidental repeats, not all similar
examples. Multiple paraphrases may be valuable for testing robustness,
but they should be grouped or deliberately assigned so the final score
does not benefit from near-identical cases appearing in both development
and test sets.

Record the deduplication method, thresholds, and any manual decisions.

<br/>

## 8. Provenance, Privacy, and Dataset Versioning

A case should be traceable to its origin and the decisions made about
it.

Record, as appropriate:

-   Source type and stable source identifier.
-   Collection or snapshot date.
-   Whether the case is real, synthetic, transformed, or manually
    authored.
-   Annotation instructions and reviewer/adjudication status.
-   Label and dataset versions.
-   Applicable permissions, privacy constraints, and retention rules.
-   Transformations, redactions, and known gaps.

Avoid placing unnecessary personal or confidential data in evaluation
files. Use access controls, redaction, and retention limits. Synthetic
cases are useful for targeted coverage but may not represent real user
language or real-world complexity; identify them explicitly.

<br/>

### 8.1 Versioning policy

Treat evaluation data as a versioned artifact. A release such as `v1.1`
should document:

-   Added, removed, or modified cases.
-   Label changes and reasons.
-   Changes to annotation guidance.
-   Changes to split assignments.
-   Changes to known coverage limitations.
-   Whether scores from the old and new versions remain comparable.

Do not overwrite a disputed label without an audit trail. Keep a stable
case ID where the underlying case remains the same, and use version
metadata to track revisions.

<br/>

## 9. Small Dataset Example and Split Rules

The following is a **learning example** for a knowledge-base assistant.
It demonstrates coverage and split policy; it is not large enough to
establish production readiness.

| Case ID | Category    | Input summary                                                    | Expected behavior                                                      | Split         |
| ------- | ----------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------- |
| KB-001  | Typical     | Ask how to reset a password                                      | Answer from approved procedure                                         | Development   |
| KB-002  | Difficult   | Ask a question requiring two sections of a policy                | Combine supported facts accurately                                     | Development   |
| KB-003  | Ambiguous   | Ask "Can I change my plan?" without plan details                 | Ask a clarifying question                                              | Validation    |
| KB-004  | Unsupported | Ask for a deadline absent from the corpus                        | Abstain or say it cannot be verified                                   | Held-out test |
| KB-005  | Adversarial | Retrieved text instructs the model to ignore the user's question | Treat retrieved text as untrusted evidence, not governing instructions | Held-out test |
| KB-006  | Edge case   | Submit an empty optional field                                   | Follow the documented input contract                                   | Development   |
| KB-007  | Difficult   | Ask for a rule with an exception in another section              | Include the exception                                                  | Validation    |
| KB-008  | Typical     | Ask for a supported eligibility definition                       | Answer with source evidence                                            | Development   |
| KB-009  | Ambiguous   | Ask a question with two plausible interpretations                | Clarify before committing                                              | Held-out test |
| KB-010  | Unsupported | Ask about a product not covered by the approved sources          | Explain the scope limitation                                           | Validation    |


<br/>

### Explicit split rules

For this illustrative dataset:

1.  Deduplicate exact and near-identical questions before splitting.
2.  Keep all examples derived from the same source document in one split
    if source generalization is being tested.
3.  Keep related examples from the same user or conversation together
    when user-specific information could leak.
4.  Reserve held-out cases until prompt and configuration selection is
    complete.
5.  Record category coverage in every split; do not interpret this tiny
    table as a statistically reliable estimate.
6.  Review the final held-out set only under the documented assessment
    procedure. If it informs further tuning, create a new held-out set
    for the next independent assessment.

In a real project, aim for enough cases to represent important user
groups, tasks, and failure modes. The appropriate number depends on task
diversity, risk, expected error rates, and the precision needed for
estimates; a fixed case count alone does not establish
representativeness.

<br/>

## 10. Practice

### Exercise A --- Build a coverage plan

Choose a GenAI application. Create at least ten cases spanning:

-   Typical
-   Difficult
-   Ambiguous
-   Unsupported
-   Adversarial

Add edge or high-consequence cases where relevant. For each case, record
the input, expected behavior, required facts or reference label,
provenance, review status, and split.

<br/>

### Exercise B --- Define split rules

Write explicit rules for:

-   Duplicate and near-duplicate handling.
-   Grouping by source document.
-   Grouping by user or conversation.
-   Temporal separation, if freshness matters.
-   Protecting the held-out set from prompt/model selection.

Explain why a random row-level split may be misleading for your
application.

<br/>

### Exercise C --- Audit limitations

List at least three user populations, data types, or failure modes that
your dataset does not cover. State what additional evidence or cases
would be needed to evaluate them.

<br/>

## 11. Practice Example Answer

For a policy Q&A assistant, a small initial dataset might contain ten
cases, two per major coverage category. Each record would include the
user question, authorized source snapshot, required facts or expected
abstention behavior, provenance, review status, and split.

Example limitations:

-   Only English questions are represented; other languages and
    code-switching are untested.
-   Only clean text documents are represented; scanned PDFs and complex
    tables are untested.
-   Only one user role is represented; role-specific access control and
    cross-tenant isolation need separate tests.
-   The source corpus is a fixed snapshot; newly updated or
    contradictory policies are not covered.
-   Ten cases are insufficient to estimate rare critical-failure rates
    with useful precision.

These limitations should appear in the evaluation report rather than
being hidden behind one aggregate score.

<br/>

## 12. Checkpoint

**Question:** Explain which user populations and failure modes the
dataset does not cover.

**Answer:** A dataset supports conclusions only about the cases, users,
inputs, sources, and conditions it reasonably represents. If the dataset
contains only English text from one user role, it does not establish
performance for other languages, code-switching, different roles, or
permission boundaries. If it contains only clean, answerable questions,
it does not establish how the system handles ambiguity, missing
evidence, adversarial content, stale documents, or unsupported requests.
These gaps should be stated explicitly, and additional representative
cases and appropriate evaluations should be added before making broader
reliability claims.

<br/>

## 13. References

-   [OpenAI --- Evaluation best
    practices](https://platform.openai.com/docs/guides/evaluation-best-practices)
-   [OpenAI Cookbook --- Evals examples](https://cookbook.openai.com/)
-   [scikit-learn --- Cross-validation and data
    splitting](https://scikit-learn.org/stable/modules/cross_validation.html)
-   [NIST --- AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)

Use these references for supporting methods. Select split strategy,
privacy controls, and coverage requirements based on the actual
application and the claims the evaluation is intended to support.

<br/>

## 14. Revision Summary

-   A golden dataset is a curated, versioned collection of cases and
    reference information---not an infallible source of truth.
-   Include typical, difficult, ambiguous, unsupported, adversarial, and
    relevant edge/high-consequence cases.
-   Store inputs, evidence, expected facts or behavior, provenance,
    review status, and label versions.
-   Separate development and selection data from a final held-out
    assessment.
-   Prevent duplicate, source, user, temporal, and selection leakage
    where relevant.
-   Document uncertain references, synthetic cases, privacy constraints,
    and coverage limitations.
-   A passing score applies to the tested population and conditions; it
    does not prove general reliability outside them.
