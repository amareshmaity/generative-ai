# 04. Human Evaluation

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Write annotation instructions with concrete, observable scoring
    anchors.
-   Reduce reviewer bias by blinding candidate identities where
    feasible.
-   Use overlapping samples to inspect agreement and identify unclear
    criteria.
-   Adjudicate uncertain cases while preserving genuine ambiguity.
-   Account for reviewer expertise, fatigue, privacy, and annotation
    effort.
-   Distinguish subjective preference from evidence-supported task
    correctness.

<br/>

## 2. What Is Human Evaluation?

Human evaluation is the systematic review of model outputs by people
using defined task criteria. It is especially useful when output quality
involves meaning, context, usefulness, or nuanced judgment that is
difficult to capture with simple deterministic checks.

Human review is not automatically objective. Reviewers may interpret
instructions differently, prefer fluent wording over accurate content,
or disagree about what a task requires. A reliable process therefore
needs clear annotation guidance, reviewer training, quality checks, and
documented resolution of disagreements.

Human evaluation can be used to:

-   Judge factual correctness and completeness.
-   Assess relevance, clarity, tone, and instruction following.
-   Verify whether claims are supported by provided evidence.
-   Compare two candidate outputs.
-   Identify failure patterns that automated metrics miss.
-   Calibrate or audit automated evaluation methods, including
    LLM-as-a-judge.

<br/>

## 3. Design Annotation Instructions

An annotation guide explains what reviewers should evaluate and how to
assign labels. It should be specific enough that two qualified reviewers
can apply it consistently.

Include:

1.  **Task and audience:** What is the application supposed to do, and
    who uses its output?
2.  **Evaluation unit:** Whole response, individual claim, field,
    citation, or candidate pair.
3.  **Evidence boundary:** Which source text, documents, policies, or
    reference facts may be used?
4.  **Criteria:** The dimensions to score, such as correctness,
    coverage, relevance, and faithfulness.
5.  **Scoring anchors:** Concrete definitions and examples for each
    score.
6.  **Critical failures:** Errors that cause a response to fail
    regardless of its aggregate score.
7.  **Uncertainty labels:** How to mark ambiguous, unverifiable, or
    insufficiently supported cases.
8.  **Tie and abstention rules:** When candidates are equally good or
    neither is acceptable.
9.  **Escalation procedure:** How reviewers flag cases that cannot be
    resolved from the guide.
10. **Privacy instructions:** What data may be viewed, copied,
    annotated, or retained.

Avoid instructions such as "choose the best answer" without defining
what "best" means. The criteria should reflect the application's
intended use and consequences of error.

<br/>

## 4. Example Annotation Guide for a Support Summary

### Task

Review a generated summary of a customer-support conversation. Determine
whether it preserves the main issue, the actions taken, the current
status, and any confirmed next step.

<br/>

### Evidence boundary

Use only the supplied conversation and approved case metadata. Do not
use external assumptions to fill gaps. If a fact is not stated or cannot
be verified from the supplied evidence, mark it as unsupported or
uncertain rather than assuming it is true.

<br/>

### Scoring anchors

Score each dimension from 0 to 2.

| Score                | Meaning                                                         |
| -------------------- | --------------------------------------------------------------- |
| **2 --- Acceptable** | Meets the criterion with no material defect                     |
| **1 --- Borderline** | Partially meets the criterion; an omission or ambiguity remains |
| **0 --- Failing**    | Violates the criterion or contains a material error             |


| Criterion       | 2 --- Acceptable                                     | 1 --- Borderline                                | 0 --- Failing                                         |
| --------------- | ---------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------- |
| Main issue      | Accurately identifies the customer's problem         | Describes the issue vaguely                     | Misstates or omits the main issue                     |
| Actions taken   | Preserves relevant actions and escalation            | Mentions an action but misses important context | Invents or contradicts an action                      |
| Current status  | Correctly states resolved/unresolved status          | Status is unclear                               | Claims resolution without evidence                    |
| Factual support | Material claims are supported by the source          | One non-critical claim is ambiguous             | Includes a consequential unsupported claim            |
| Conciseness     | Includes essential facts without needless repetition | Some unnecessary detail or omission             | So verbose or incomplete that the handoff is unusable |


**Critical failure rule:** A fabricated commitment, refund approval, or
resolution date is an automatic failure if the application treats
factual fidelity as a hard requirement. Do not allow a high average
score to hide this violation.

<br/>

### Required reviewer output

For each case, record:

-   Case ID.
-   Score for each criterion.
-   Overall acceptability: pass, fail, or uncertain.
-   Evidence excerpt or source location for each material issue.
-   Short rationale tied to the rubric.
-   Reviewer confidence or uncertainty flag, if defined by the protocol.

A rationale should explain the decision with reference to the source and
criteria, not simply state "sounds good."

<br/>

## 5. Blind Review to Reduce Bias

When feasible, hide candidate identities and irrelevant metadata from
reviewers. For example, label two outputs "A" and "B" rather than
displaying model names, version names, or which output is the new
candidate.

Blinding can reduce:

-   **Brand or model reputation bias:** Preferring an output because it
    came from a familiar model.
-   **Confirmation bias:** Expecting the new version to be better
    because the team invested in it.
-   **Anchoring:** Seeing another reviewer's score before forming an
    independent judgment.
-   **Order effects:** Preferring the first or second candidate by
    default.

Practical safeguards:

-   Randomize or counterbalance candidate order.
-   Keep reviewer instructions identical across candidates.
-   Hide model/provider identity when it is not necessary for the task.
-   Collect independent judgments before showing others' ratings.
-   Preserve candidate IDs in the analysis metadata so results remain
    traceable after review.

Blinding is not always possible. A reviewer may infer a model's identity
from its style, or the task may require metadata that reveals the
candidate. Document these limitations instead of claiming perfect
blindness.

<br/>

## 6. Overlapping Samples and Reviewer Agreement

An **overlapping sample** is a set of cases independently reviewed by
more than one person. Overlap helps reveal whether the rubric is
understandable and whether scores are reproducible across reviewers.

A practical workflow is:

1.  Train reviewers on a small set of examples.
2.  Have them score the same calibration cases independently.
3.  Compare labels and rationales.
4.  Discuss disagreements and refine unclear instructions.
5.  Independently review an overlap sample during the main annotation
    run.
6.  Track disagreement by criterion and case category.
7.  Revisit the guide if disagreement is systematic.

<br/>

### 6.1 Agreement is not the same as correctness

Two reviewers can agree and still be wrong if both misunderstand the
source or share the same bias. Conversely, disagreement may reveal
genuine ambiguity rather than poor reviewer performance.

Report more than a single agreement number where useful:

-   Raw agreement: fraction of overlapping cases with the same label.
-   Confusion table: which labels reviewers disagree on.
-   Criterion-level disagreement.
-   Cohen's kappa or another suitable chance-corrected statistic for
    appropriate label designs.
-   Notes on sample size and label prevalence.

For two reviewers with categorical labels, raw agreement is:

$$
\text{Agreement} = \frac{\text{Number of matching labels}}{\text{Number of jointly reviewed cases}}
$$

**Illustrative calculation:** If reviewers give the same label on 42 of
50 overlapping cases, raw agreement is (42/50 = 84%). This does not, by
itself, establish that the labels are correct or that agreement is
adequate for every use case.

Use chance-corrected statistics carefully: their interpretation depends
on the labeling design and prevalence. Do not rely on one statistic to
conceal which disagreements matter.

<br/>

## 7. Adjudicate Disagreements Without Erasing Ambiguity

**Adjudication** is the process of reviewing conflicting judgments and
deciding how the case should be recorded.

A useful process:

``` mermaid
flowchart TD
    A[Reviewers score independently] --> B{Do labels agree?}
    B -- Yes --> C[Record label and evidence]
    B -- No --> D[Compare rationales and source evidence]
    D --> E{Can the rubric resolve the disagreement?}
    E -- Yes --> F[Apply the rubric consistently]
    E -- No --> G[Escalate to qualified adjudicator]
    G --> H{Is there enough evidence for one label?}
    H -- Yes --> I[Record adjudicated label and rationale]
    H -- No --> J[Mark ambiguous or insufficient evidence]
    F --> K[Update audit trail if guidance changes]
    I --> K
    J --> K
```

During adjudication:

-   Re-read the source and annotation instructions.
-   Identify whether the disagreement is about facts, criteria,
    interpretation, or reviewer error.
-   Apply the same rule to all relevant cases, not only the current
    example.
-   Record the final label, rationale, and any change to guidance.
-   Preserve the original independent labels for auditability.
-   Mark genuine ambiguity when evidence cannot support a unique answer.

Do not force a consensus label simply to make the dataset look clean. A
documented "uncertain" label is often more accurate than false
precision.

If the rubric changes materially, version the guidance and consider
re-reviewing affected cases. Otherwise, earlier and later labels may not
be comparable.

<br/>

## 8. Reviewer Expertise, Fatigue, Privacy, and Cost

Human annotation is a resource-intensive process. Plan it like a
measurement workflow rather than assuming reviewers can assess unlimited
outputs consistently.

### 8.1 Expertise

Match the reviewer to the task:

-   General writing quality may be reviewed by trained generalists.
-   Domain-specific factual claims may require subject-matter experts.
-   Legal, medical, financial, or other consequential evaluations may
    require appropriately qualified reviewers and additional governance.
-   Source-faithfulness checks require access to the relevant source
    evidence.

Domain expertise does not eliminate bias; reviewers still need
consistent criteria and documented evidence.

<br/>

### 8.2 Fatigue and workload

Long review sessions can increase missed details, inconsistent scoring,
and shortcut behavior.

Mitigations include:

-   Keep annotation batches manageable.
-   Pilot the estimated review time per case.
-   Insert calibration cases or quality-control checks.
-   Monitor score drift across a session.
-   Allow breaks and avoid unrealistic throughput targets.
-   Use targeted sampling for expensive expert review while preserving
    coverage of critical cases.

<br/>

### 8.3 Privacy and data handling

Reviewers should see only the data necessary for the task. Use redaction
or synthetic examples where possible, restrict access, and define
retention and deletion procedures. Do not copy sensitive source content
into unapproved annotation tools or free-text comments.

<br/>

### 8.4 Annotation effort

Estimate effort before scaling:

$$
\text{Total review hours} \approx \frac{N \times R \times T}{60}
$$

where:

- $N$ = number of cases,
- $R$ = average number of reviewers per case,
- $T$ = average review minutes per case.

For example, 300 cases, 2 reviewers per case, and 3 minutes per review
require approximately (300 `\times 2`{=tex} `\times 3`{=tex} / 60 = 30)
reviewer-hours, excluding training, adjudication, and administration.

Use this estimate to choose where independent overlap is most valuable.
Do not remove overlap entirely just to reduce cost when reviewer
consistency is a key risk.

<br/>

## 9. Practice: Independently Review and Reconcile Outputs

### Scenario

The source conversation says:

> A customer cannot export a monthly report. Support reproduced the
> error and escalated it to engineering. Engineering has not confirmed a
> fix or a delivery date.

**Output A**

> The monthly report export is failing. Support reproduced the error and
> escalated it to engineering; no fix or delivery date has been
> confirmed.

**Output B**

> Engineering is fixing the report export problem and expects to deliver
> the fix tomorrow.

<br/>

### Independent review worksheet

Before reading the example answer, score each output against the
criteria.
| Criterion                  | Output A (0--2) | Output B (0--2) |
| -------------------------- | --------------- | --------------- |
| Main issue preserved       |                 |                 |
| Actions taken preserved    |                 |                 |
| Current status accurate    |                 |                 |
| Claims supported by source |                 |                 |
| Conciseness                |                 |                 |
                                  

Also record:

-   Overall decision: pass, fail, or uncertain.
-   Evidence for every score below 2.
-   Any critical failure.
-   A short rationale tied to the rubric.

<br/>

### Example reconciliation

| Criterion                  | Output A | Output B |
| -------------------------- | -------- | -------- |
| Main issue preserved       | 2        | 2        |
| Actions taken preserved    | 2        | 1        |
| Current status accurate    | 2        | 0        |
| Claims supported by source | 2        | 0        |
| Conciseness                | 2        | 2        |

**Interpretation:**

-   Output A preserves the known issue, escalation, and absence of a
    confirmed fix or date. It is acceptable under this rubric.
-   Output B invents an active fix commitment and a delivery date. Those
    claims are unsupported by the source and violate the critical
    factual-fidelity requirement.

These scores are illustrative. In an actual annotation exercise,
reviewers should score independently before seeing a reference judgment,
then compare rationales and resolve disagreements.

<br/>

### Reconciliation questions

1.  Did reviewers disagree about a factual claim, the rubric, or the
    importance of an omission?
2.  Can the source evidence resolve the disagreement?
3.  Does the rubric need a clearer anchor?
4.  If the case remains ambiguous, how will that uncertainty be
    represented in the dataset?

<br/>

## 10. Common Failure Modes in Human Evaluation

-   **Vague criteria:** "Helpful" or "high quality" is not operationally
    defined.
-   **Preference substituted for correctness:** A polished answer is
    favored despite unsupported claims.
-   **Unblinded review:** Model identity or candidate order influences
    ratings.
-   **No independent overlap:** Reviewer inconsistency remains
    undiscovered.
-   **Forced consensus:** Genuine ambiguity is hidden behind a single
    label.
-   **No evidence rationale:** Scores cannot be audited or reconciled.
-   **Expertise mismatch:** Reviewers cannot reliably judge the domain.
-   **Fatigue ignored:** Annotation quality declines without being
    detected.
-   **Privacy overlooked:** Sensitive data is exposed through review
    workflows.
-   **Agreement overinterpreted:** High agreement is treated as proof of
    truth.

<br/>

## 11. Checkpoint

**Question:** Distinguish reviewer preference from evidence-supported
task correctness.

**Answer:** Reviewer preference expresses which output a person likes or
finds clearer, more fluent, or more persuasive. Evidence-supported task
correctness asks whether the output satisfies the task criteria and
whether its material claims are supported by the allowed evidence.
Preference can be useful when evaluating style or user experience, but
it cannot override a factual contradiction or an unsupported commitment.
A reliable annotation process defines the criteria in advance, asks
reviewers to cite evidence for material judgments, blinds candidates
where feasible, records disagreements, and preserves uncertainty when
the evidence does not support a definitive conclusion.

<br/>

## 12. References

-   [OpenAI --- Evaluation best
    practices](https://platform.openai.com/docs/guides/evaluation-best-practices)
-   [NIST --- AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
-   [scikit-learn --- Model
    evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
-   [Cohen, J. --- A coefficient of agreement for nominal scales
    (1960)](https://doi.org/10.1177/001316446002000104)

Verify that any agreement statistic matches the number of reviewers,
label type, and study design before using it to make quality claims.

<br/>

## 13. Revision Summary

-   Human evaluation needs explicit annotation instructions, evidence
    boundaries, and concrete scoring anchors.
-   Blinding and randomized candidate order can reduce some reviewer
    biases.
-   Overlapping samples reveal disagreement and unclear rubric
    definitions.
-   Adjudication should preserve original judgments and retain genuine
    ambiguity where evidence is insufficient.
-   Reviewer expertise, fatigue, privacy, and annotation cost affect
    evaluation reliability.
-   Preference is not proof of correctness; material judgments should be
    tied to the task criteria and available evidence.
