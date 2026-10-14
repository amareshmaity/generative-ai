# 06. Hallucination, Correctness, Relevance, and Faithfulness

## Learning Objectives

By the end of this chapter, you should be able to:

-   Distinguish factual correctness from support in supplied evidence.
-   Define relevance, completeness, unsupported claims, and
    contradictions.
-   Separate an answer's fluency from its truth or source fidelity.
-   Evaluate individual claims against evidence and mark unverifiable
    cases explicitly.
-   Explain why a single overall "quality" label can hide important
    failure modes.

<br/>

## 1. The Core Problem: Quality Has Multiple Dimensions

A GenAI answer can sound polished and still be wrong. It can be
factually correct by coincidence while not being supported by the
supplied documents. It can accurately repeat a source that itself
contains an error. It can answer a related topic without answering the
user's actual question.

These are different failure modes, so evaluation should record them
separately.

| Dimension                 | Main question                                                        | Typical failure                                           |
| ------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------- |
| Factual correctness       | Is the claim true in the relevant world or domain?                   | A false date, number, name, or explanation                |
| Evidence support          | Does the supplied evidence justify the claim?                        | A plausible statement with no supporting passage          |
| Faithfulness              | Does the answer accurately represent the supplied source or context? | Misstating, exaggerating, or contradicting source content |
| Relevance                 | Does the answer address the user's question and intent?              | Correct facts that do not answer the question             |
| Completeness              | Does the answer cover the required parts of the task?                | Omitting a key condition, exception, or requested item    |
| Contradiction consistency | Does the answer conflict with itself or with the evidence?           | Two incompatible dates in one answer                      |
| Fluency and clarity       | Is the answer understandable and well expressed?                     | Ambiguous wording or confusing structure                  |


**Important distinction:** factual correctness, evidence support, and
faithfulness are related but not interchangeable. Their relationship
depends on the task and the available evidence.

<br/>

## 2. Correctness Versus Evidence Support

### 2.1 Factual correctness

A claim is factually correct when it matches the relevant facts, given
the task's scope and time frame.

Example: A response says, "The meeting starts at 3:00 PM," and an
authoritative calendar confirms that time.

Correctness may require checking external authoritative information. If
no such information is available, an evaluator may not be able to
determine whether the claim is true.

<br/>

### 2.2 Evidence support

A claim is supported when the permitted evidence actually entails or
reasonably justifies it.

Example supplied note: "The meeting begins at 3:00 PM."

Answer: "The meeting begins at 3:00 PM."

The answer is directly supported by the note.

Now suppose the answer says, "The meeting begins at 3:00 PM in Room 12."
The note supports the time but says nothing about the room. The room
claim is unsupported even if it happens to be correct.

<br/>

### 2.3 The four-way distinction

| Actual-world status | Supported by supplied evidence?         | Evaluation label                                                          |
| ------------------- | --------------------------------------- | ------------------------------------------------------------------------- |
| Correct             | Yes                                     | Correct and supported                                                     |
| Correct             | No                                      | Correct but unsupported (or unverified by supplied evidence)              |
| Incorrect           | Yes, because the source itself is wrong | Faithful to an incorrect source; source correctness fails                 |
| Incorrect           | No                                      | Incorrect and unsupported; may be fabricated if invented without evidence |


These labels require different evidence. Without an independent way to
establish actual truth, do not label a claim "correct but unsupported"
as a certainty; use **"unsupported; truth not independently verified."**

"Fabricated" should be used carefully. It describes content presented as
factual despite lacking an adequate basis, especially when it includes
invented specifics. Lack of support alone does not prove intentional
deception.

<br/>

## 3. Relevance and Completeness

### 3.1 Relevance

Relevance measures whether the answer addresses the user's actual
question, intent, and constraints.

User: "Which two risks did the report identify?"

Answer: "The report was published in 2024 and has six sections."

This might be true, but it does not identify the two risks. It is
therefore irrelevant or non-responsive to the requested task.

An answer can contain relevant background and still fail if the
requested output is missing. Evaluate the requested deliverable, not
merely topic similarity.

<br/>

### 3.2 Completeness

Completeness measures whether the answer includes all required
components.

User: "List the two risks and one mitigation for each."

Answer: "The risks are data leakage and latency."

This answer is relevant but incomplete because it omits the mitigations.

For evaluation, define the expected elements before reviewing outputs.
Examples include required fields, named entities, steps, caveats, time
ranges, citations, or explicit uncertainty statements.

<br/>

### 3.3 Relevance and completeness are separate

-   **Relevant but incomplete:** addresses the question but omits a
    required part.
-   **Complete but irrelevant:** supplies many details, but not the
    requested details.
-   **Relevant and complete:** covers the intended task and all required
    elements.
-   **Neither:** fails to address the task and omits the required
    deliverable.

<br/>

## 4. Faithfulness to Supplied Evidence

Faithfulness evaluates whether the response preserves the meaning and
limits of the supplied context. It is especially important in
retrieval-augmented generation (RAG), document Q&A, summarization, and
evidence-grounded assistants.

A faithful answer should:

-   Preserve the source's qualifiers, uncertainty, and scope.
-   Avoid adding details that the source does not establish.
-   Avoid changing correlation into causation or possibility into
    certainty.
-   Avoid omitting a limitation that changes the meaning.
-   Represent disagreements between sources rather than silently
    choosing one.
-   Distinguish what the source says from what the evaluator
    independently knows.

<br/>

### Example: Faithful to an incorrect source

Supplied document: "The fictional city of Northport was founded in
1987."

Answer: "The document states that Northport was founded in 1987."

The answer is faithful to the document because it accurately reports
what the document says. Whether the date is historically correct is a
separate question. If an authoritative historical record shows the city
was founded in 1887, then the answer remains source-faithful but the
source is factually incorrect.

This distinction matters when evaluating document-grounded tasks: the
expected behavior may be to report the source accurately, while also
flagging a known source error if the task asks for verification.

<br/>

## 5. Unsupported Claims, Contradictions, and Fabrication

### 5.1 Unsupported claims

A claim is unsupported when the permitted evidence does not provide
enough basis for it. Unsupported does not necessarily mean false.

Example evidence: "The product supports CSV import."

Answer: "The product supports CSV import and exports to Excel."

Only the CSV-import claim is supported. The Excel-export claim requires
additional evidence.

<br/>

### 5.2 Contradictions

Check for at least two forms of contradiction:

1.  **Internal contradiction:** two claims in the answer cannot both be
    true under the same conditions.
2.  **Evidence contradiction:** a claim conflicts with the supplied
    evidence.

Example: The answer first says "The deadline is 12 May" and later says
"The deadline is 15 May." This is an internal contradiction unless the
answer explains different deadlines or versions.

Evidence contradiction example: The source says "No tests were run," but
the answer says "All tests passed."

<br/>

### 5.3 Fabricated details

Examples include invented citations, nonexistent quotations, made-up
document sections, unsupported numerical results, or named entities
absent from the permitted evidence.

A model may generate a plausible detail because it resembles patterns in
training data. Plausibility is not evidence. Evaluate the claim and its
evidence trail rather than inferring the model's intent.

<br/>

### 5.4 Fluency is not evidence

Grammar, confidence, detail, and persuasive style do not establish
truth. Evaluate wording quality separately from correctness and source
fidelity. A fluent answer with fabricated citations may be worse than a
hesitant answer that explicitly identifies what cannot be verified.

<br/>

## 6. Evidence-Backed Claim Checking

Use a claim-level workflow rather than assigning a single
impressionistic score to the entire answer.

``` mermaid
flowchart TD
    A[Answer] --> B[Split into factual claims]
    B --> C[Identify permitted evidence]
    C --> D{Evidence supports claim?}
    D -->|Yes| E[Check source consistency]
    D -->|No| F[Mark unsupported]
    E --> G{Independent truth check required and available?}
    G -->|Yes| H[Verify against authoritative source]
    G -->|No| I[Record truth as not independently verified]
    H --> J[Label correctness and faithfulness separately]
    I --> J
    F --> K[Do not assume false; record uncertainty]
    J --> L[Check relevance, completeness, and contradictions]
```

<br/>

### Step 1: Decompose the answer into atomic claims

Break compound sentences into claims that can be evaluated
independently.

Answer: "The service launched in 2023, supports PDF uploads, and reduces
processing time by 40%."

Claims: 1. The service launched in 2023. 2. The service supports PDF
uploads. 3. The service reduces processing time by 40%.

One sentence may contain both supported and unsupported claims. Do not
give the whole sentence a single label if its parts differ.

<br/>

### Step 2: Identify the evidence boundary

Record what evidence is permitted for the task:

-   Supplied document or retrieved passages only.
-   Supplied evidence plus a specified authoritative source.
-   General domain knowledge, with an explicit verification standard.
-   No evidence available, so truth cannot be assessed.

For a RAG faithfulness evaluation, retrieved context is commonly the
evidence boundary. For a fact-checking task, external authoritative
evidence may also be required.

<br/>

### Step 3: Match claims to evidence

For each claim, record the exact passage, record ID, URL, or other
evidence reference. Mark a claim as unsupported if no adequate evidence
is found. Do not invent a citation or treat a loosely related passage as
proof.

<br/>

### Step 4: Assign separate labels

A practical claim-level schema:

| Field                 | Example values                                                                    |
| --------------------- | --------------------------------------------------------------------------------- |
| `claim_id`            | `c1`, `c2`                                                                        |
| `claim_text`          | Atomic factual statement                                                          |
| `evidence_ref`        | Passage ID, URL, or `null`                                                        |
| `support_status`      | `supported`, `partially_supported`, `unsupported`, `contradicted`, `not_assessed` |
| `truth_status`        | `verified_true`, `verified_false`, `unknown`                                      |
| `faithfulness_status` | `faithful`, `distorted`, `not_applicable`, `uncertain`                            |
| `relevance_status`    | `relevant`, `partially_relevant`, `irrelevant`                                    |
| `notes`               | Why the label was assigned                                                        |


These are example schema values, not universal standards. Define them in
the evaluation rubric before scoring.

<br/>

### Step 5: Mark unverifiable cases explicitly

Use labels such as `unknown`, `not_assessed`, or
`insufficient_evidence`. Do not force an uncertain claim into a
true/false category. If sources conflict, record the conflict and the
source versions rather than silently resolving it.

<br/>

### Step 6: Evaluate the answer as a whole

After claim checks, assess:

-   Relevance to the user request.
-   Completeness against the expected elements.
-   Internal contradictions.
-   Evidence contradictions.
-   Clarity and readability.
-   Any critical failure that should override an average score.

<br/>

## 7. Worked Example: Document-Grounded Assistant

**User question:** "According to the supplied report, what caused the
delay and when will the issue be resolved?"

**Supplied report excerpt:**

> "The deployment was delayed because a database migration failed during
> validation. The team is investigating. No resolution date has been
> confirmed."

**Candidate answer A:**

> "The delay was caused by a database migration failure during
> validation. The team has not confirmed a resolution date."

-   Correctly represents the stated cause.
-   Supported by the excerpt.
-   Relevant to both parts of the question.
-   Complete within the available evidence.
-   Faithful to the report's uncertainty.

**Candidate answer B:**

> "The delay was caused by a database migration failure, and the issue
> will be resolved tomorrow."

-   Cause: supported, although "during validation" is omitted.
-   Resolution tomorrow: unsupported and more certain than the source.
-   Overall: partly supported, partly unsupported; incomplete evidence
    cannot justify the promised date.
-   Do not mark the date as false unless independent evidence
    establishes that it is false.

**Candidate answer C:**

> "The report has a section on deployment operations and describes
> several validation procedures."

-   Potentially true, but it does not answer the cause or
    resolution-date question.
-   Relevant only at a broad topic level; non-responsive to the
    requested facts.
-   Incomplete.

**Candidate answer D:**

> "The delay was caused by a database migration failure during
> validation. No resolution date has been confirmed. The issue will
> definitely be fixed tomorrow."

-   The first two statements are supported.
-   The final sentence contradicts the stated uncertainty and introduces
    an unsupported prediction.
-   The answer contains an internal/evidence-level inconsistency.

<br/>

## 8. Practice: Label the Failure Mode

For each example, identify correctness, support, faithfulness,
relevance, and completeness separately. Treat truth as unknown unless
evidence is supplied.

### Exercise 1: Correct but unsupported

Evidence: "The office opens at 9:00 AM."

Answer: "The office opens at 9:00 AM and closes at 6:00 PM."

Questions: - Which claim is supported? - What label should be assigned
to the closing time if no independent source is available?

<br/>

### Exercise 2: Faithful to an incorrect source

Source document: "The capital of Australia is Sydney."

Answer: "The document states that Sydney is the capital of Australia."

Questions: - Is the answer faithful to the source? - Is the source's
claim factually correct?

<br/>

### Exercise 3: Irrelevant answer

User: "Which model had the lowest measured latency?"

Evidence: "Model A: 420 ms; Model B: 310 ms; Model C: 390 ms."

Answer: "Model A has a context window of 128,000 tokens."

Questions: - Is the answer necessarily false? - Does it answer the
question?

<br/>

### Exercise 4: Fabricated or unsupported detail

Evidence: "The evaluation included 50 test cases."

Answer: "The evaluation included 50 test cases and achieved 97.4%
accuracy."

Questions: - Which claim is supported? - What evidence is needed before
accepting the accuracy figure?

<br/>

### Exercise 5: Faithfulness versus truth

Source: "The device may reduce energy use in some workloads."

Answer: "The device always reduces energy use."

Questions: - What qualifier has been lost? - Which faithfulness failure
occurred?

<br/>

### Exercise 6: Contradiction

Answer: "The model passed all 30 tests. Three tests failed."

Questions: - What kind of contradiction is present? - What additional
information could reconcile the statements, if any?

<br/>

## 9. Suggested Answers

1.  The opening time is supported. The closing time is unsupported; its
    actual truth remains unknown unless independently verified.
2.  The answer is faithful to what the source says, but the source's
    claim is factually incorrect. Australia's capital is Canberra. In a
    source-only task, report what the source says; in a verification
    task, flag the error.
3.  The context-window claim may be true or false, but it does not
    answer the latency question. Model B has the lowest measured latency
    in the supplied data at 310 ms.
4.  The count of 50 cases is supported. The 97.4% accuracy figure
    requires a recorded evaluation result, metric definition, dataset
    identity, and reproducible run details.
5.  "May" and "in some workloads" have been converted into "always."
    This is an overstatement and a faithfulness failure; the stronger
    claim is unsupported by the source.
6.  The answer contains an internal contradiction if both statements
    refer to the same test run and pass/fail definition. It could be
    reconciled only if the statements refer to different runs, suites,
    or meanings of "passed," which must be made explicit.

<br/>

## 10. Implementation Pattern

The following Python example illustrates a small, auditable claim
ledger. It does not automatically determine truth; it records an
evaluator's evidence-backed decisions.

``` python
from dataclasses import dataclass, asdict
from typing import Optional
import json

@dataclass
class ClaimReview:
    claim_id: str
    claim_text: str
    evidence_ref: Optional[str]
    support_status: str
    truth_status: str
    faithfulness_status: str
    relevance_status: str
    notes: str

reviews = [
    ClaimReview(
        claim_id="c1",
        claim_text="The migration failed during validation.",
        evidence_ref="report:p3",
        support_status="supported",
        truth_status="unknown",  # not independently fact-checked
        faithfulness_status="faithful",
        relevance_status="relevant",
        notes="Directly stated in the supplied report."
    ),
    ClaimReview(
        claim_id="c2",
        claim_text="The issue will be resolved tomorrow.",
        evidence_ref=None,
        support_status="unsupported",
        truth_status="unknown",
        faithfulness_status="distorted",
        relevance_status="relevant",
        notes="The report says no resolution date is confirmed."
    ),
]

print(json.dumps([asdict(item) for item in reviews], indent=2))
```

**Implementation cautions:**

-   Do not treat a judge model's label as ground truth without
    calibration.
-   Preserve the exact evidence passage or a stable reference to it.
-   Use `unknown` when independent truth verification is unavailable.
-   Review compound answers at claim level; one supported sentence does
    not validate every other claim.
-   For high-impact domains, use qualified human review and
    authoritative sources.
-   Store evaluator version, rubric version, model/prompt version,
    dataset version, and run ID for reproducibility.

<br/>

## 11. Why These Dimensions Must Not Be Collapsed

A single vague label such as "good" or "bad" hides the reason an answer
succeeds or fails.

-   **Correctness without support** can be accidental and is not
    reliable evidence-grounded behavior.
-   **Support without truth** can reproduce an error in the source.
-   **Faithfulness without relevance** can accurately summarize the
    wrong material.
-   **Relevance without completeness** can omit a critical field or
    caveat.
-   **Fluency without truth** can make fabricated details unusually
    persuasive.
-   **A high average score** can hide a critical unsupported claim,
    contradiction, or safety-relevant error.

Keep dimensions separate so teams can diagnose failures, select the
right intervention, compare systems fairly, and establish meaningful
release gates. For example, retrieval changes may improve evidence
support, prompt changes may improve relevance or completeness, and
source verification may be needed to address incorrect source material.
No single metric proves all dimensions.

<br/>

## 12. Checkpoint

**Prompt:** Explain why factual correctness, evidence support,
faithfulness, relevance, completeness, and fluency must be evaluated
separately.

**Model answer:**

They measure different properties. Correctness concerns whether a claim
is true; evidence support concerns whether permitted evidence justifies
it; faithfulness concerns whether the answer preserves the source's
meaning and limitations; relevance concerns whether it addresses the
user's intent; completeness concerns whether it covers all required
elements; and fluency concerns readability. A response may be fluent and
relevant but fabricated, or faithful to a source that is wrong.
Combining these dimensions into one score can conceal failure modes and
make debugging or release decisions unreliable. Evaluate claims against
evidence, record uncertainty explicitly, and aggregate dimensions only
after defining their individual criteria and any critical-failure rules.

<br/>

## 13. Further Reading

-   [RAGAS documentation](https://docs.ragas.io/) --- evaluation
    concepts for RAG and LLM applications.
-   [DeepEval documentation](https://docs.confident-ai.com/) --- LLM
    evaluation framework and evaluation metrics.
-   [LangSmith evaluation
    concepts](https://docs.smith.langchain.com/evaluation) ---
    evaluation workflows for LLM applications.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- risk management context for trustworthy AI.
-   [TruthfulQA paper](https://arxiv.org/abs/2109.07958) --- benchmark
    focused on truthful responses to questions.


<br/>


## Chapter Summary

Evaluate GenAI outputs across distinct dimensions rather than relying on
fluency or a single quality score. Break answers into atomic claims,
identify the evidence boundary, record supporting references, separate
source faithfulness from actual-world correctness, and explicitly mark
unsupported or unverifiable claims. Then assess relevance, completeness,
contradictions, and clarity against task-specific criteria.
