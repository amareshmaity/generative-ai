# 11. Pairwise Comparisons and Preference Evaluation

## Learning Objectives

By the end of this chapter, you should be able to:

-   Compare candidate outputs using explicit task criteria and allow
    ties or abstentions.
-   Randomize or swap candidate order to inspect position effects.
-   Distinguish relative preference from absolute acceptability.
-   Define win-rate denominators and treatment of ties, missing results,
    and failures.
-   Run a small blinded comparison and justify decisions with
    rubric-based reasons.

<br/>

## 1. What Is Pairwise Preference Evaluation?

Pairwise evaluation presents two candidate outputs for the same task and
asks a reviewer or judge to compare them. The evaluator decides which
candidate better satisfies the stated criteria, whether they are tied,
or whether the comparison cannot be judged reliably.

It is useful when: - Two prompts, models, retrieval strategies, or
application versions produce open-ended answers. - A single reference
answer is difficult to define. - Human reviewers can make more reliable
relative judgments than absolute numeric ratings. - Teams need to
compare candidate systems during development.

Pairwise preference answers a **relative** question: "Which candidate is
better under this rubric?" It does not automatically answer the
**absolute** question: "Is either candidate good enough to ship?"

<br/>

## 2. Define the Comparison Contract

Before comparing candidates, specify the task, criteria, evidence, and
allowed outcomes.

### 2.1 Task and evidence

Provide both candidates with the same user query and the same permitted
evidence when the goal is to compare generation quality. If comparing
retrieval systems, evaluate each system's retrieved evidence according
to a common relevance rubric. Record any differences in context, tools,
or configuration that are part of the experiment.

<br/>

### 2.2 Explicit criteria

Use task-specific criteria rather than asking "Which answer is better?"
without guidance.

Example rubric for a document-grounded answer:

| Criterion         | What to inspect                                               |
| ----------------- | ------------------------------------------------------------- |
| Correctness       | Does the answer match the reference facts?                    |
| Evidence support  | Are material claims supported by permitted evidence?          |
| Completeness      | Does it cover the requested elements?                         |
| Relevance         | Does it answer the actual question?                           |
| Clarity           | Is it understandable without unnecessary complexity?          |
| Citation quality  | Do citations exist and support the claims?                    |
| Critical failures | Does it invent a key fact or disclose restricted information? |


Define the priority order. For example, a polished answer must not beat
a less polished answer that is factually correct and evidence-grounded
if correctness and grounding are hard requirements.

<br/>

### 2.3 Allowed outcomes

A useful outcome set is:

-   `A_wins`: Candidate A is better under the rubric.
-   `B_wins`: Candidate B is better under the rubric.
-   `tie`: No meaningful difference under the stated criteria.
-   `abstain`: Insufficient evidence, ambiguous criteria, or a
    comparison that cannot be judged reliably.

Do not force a winner when both answers are equivalent or the evidence
is insufficient. Define whether a critical failure automatically makes
an answer unacceptable, even if the other answer is also poor.

<br/>

## 3. Blind Candidate Identity and Randomize Order

Candidate labels can influence reviewers. If reviewers know which output
came from a preferred model or newer system, brand reputation or
expectations may affect their choices.

Use neutral labels such as A and B. Hide model names, version names, and
other identifying details where practical. Randomize the display order
across examples.

<br/>

### Position-effect check

For a sample of cases, repeat the comparison with the same two
candidates in swapped order. If the preferred candidate changes merely
because it appears first, the evaluation may have position bias.

``` mermaid
flowchart TD
    A[Choose query and rubric] --> B[Generate candidates A and B]
    B --> C[Hide model identity]
    C --> D[Randomize display order]
    D --> E[Judge with explicit criteria]
    E --> F[Record winner, tie, or abstention]
    F --> G[Swap order on a sample]
    G --> H[Measure preference consistency]
    H --> I[Inspect disagreements and position effects]
```

Randomization reduces systematic order effects but does not eliminate
them. Record the randomization seed or assignment procedure for
reproducibility.

<br/>

## 4. Preference Is Not Absolute Acceptability

Suppose Candidate A is incorrect and Candidate B is even more incorrect.
Candidate B can lose the comparison, but that does not make Candidate A
acceptable.

Use two separate decisions:

1.  **Absolute gate:** Does the candidate meet minimum correctness,
    safety, grounding, and operational requirements?
2.  **Relative preference:** Among candidates that are being compared,
    which one better satisfies the rubric?

Example:

-   A gives an unsupported answer with a plausible explanation.
-   B gives an unsupported answer and also invents a citation.
-   A may win pairwise because it has fewer failures.
-   A still fails an absolute groundedness requirement and should not be
    approved for production.

Pairwise comparisons are especially useful for ranking candidates, but
they should be paired with absolute quality thresholds and
critical-failure checks.

<br/>

## 5. Win Rate and Its Denominator

A win rate summarizes how often a candidate wins comparisons. The exact
formula depends on how ties and non-comparable cases are treated.

### 5.1 Win rate excluding ties

One common definition is:

$$
\text{Win Rate}_A = \frac{W_A}{W_A + W_B}
$$

where (W_A) and (W_B) are the counts of decisive wins for A and B. Ties
and abstentions are excluded from this denominator. Always report their
counts and the number of decisive comparisons.

### 5.2 Win rate including ties as half-wins

Another convention assigns half credit for a tie:

$$
\text{Tie-Adjusted Win Rate}_A = \frac{W_A + 0.5T}{W_A + W_B + T}
$$

where (T) is the number of ties. Abstentions and missing comparisons are
still handled separately unless the protocol explicitly says otherwise.

These definitions answer slightly different questions. Name the
convention in reports and do not compare scores calculated under
different rules.

<br/>

### 5.3 Example

Across 100 assigned comparisons: - A wins 48. - B wins 32. - 12 are
ties. - 5 are abstentions. - 3 have missing outputs.

Excluding ties, abstentions, and missing outputs:

$$
\text{Win Rate}_A = \frac{48}{48+32} = 0.60
$$

Tie-adjusted, using decisive results plus ties:

$$
\frac{48 + 0.5(12)}{48+32+12} = \frac{54}{92} \approx 0.587
$$

Report both the rate and coverage. The decisive win rate is 60%, but
only 80 of the 100 assigned comparisons were decisive. The tie-adjusted
rate is about 58.7% over 92 comparisons with a winner or tie. Five
abstentions and three missing cases should not disappear from the
report.

<br/>

## 6. Ties, Abstentions, Missing Outputs, and Failures

Define each case before calculating win rates.

| Outcome              | Recommended handling                                                             |
| -------------------- | -------------------------------------------------------------------------------- |
| Tie                  | Record explicitly; include or exclude according to the named win-rate convention |
| Abstention           | Record why comparison was not possible; report count and rate                    |
| Missing output       | Treat as an evaluation outcome, not silently drop it                             |
| Parse/schema failure | Apply the task contract; a failed candidate may lose or fail an absolute gate    |
| Refusal              | Judge whether refusal was appropriate for the query                              |
| Invalid citation     | Score citation quality and any critical-failure rule separately                  |
| Both candidates fail | A relative winner may exist, but both may fail the absolute gate                 |


For end-to-end system comparison, missing or invalid outputs may count
as failures under the task contract. If such cases are excluded from a
conditional preference analysis, also report end-to-end success and the
exclusions.

Do not automatically count every refusal as a loss: a refusal may be
correct for an unsafe, unauthorized, or unanswerable request.

<br/>

## 7. Reasons Must Refer to the Rubric

A preference label is more useful when it includes a short reason tied
to explicit criteria.

Weak reason: \> "A sounds better."

Useful reason: \> "A wins because it answers both requested parts and
cites the passage that supports the deadline. B omits the deadline and
adds an unsupported prediction."

Reason codes can support aggregation:

-   `correctness`
-   `evidence_support`
-   `completeness`
-   `relevance`
-   `citation_quality`
-   `clarity`
-   `critical_failure`
-   `no_material_difference`
-   `insufficient_evidence`

Reasons should explain the decision, not merely restate the winner. For
high-stakes tasks, reviewers should identify the relevant claim or
evidence passage.

<br/>

## 8. Pairwise Evaluation Workflow

1.  Define the task, target population, and comparison objective.
2.  Freeze the rubric and any absolute acceptance thresholds.
3.  Generate both candidates under documented configurations.
4.  Remove model identities and randomize display order.
5.  Have reviewers or a calibrated judge compare the candidates.
6.  Record winner, tie, abstention, reason codes, and evidence
    references.
7.  Swap order on a subset to test position sensitivity.
8.  Review disagreements and adjudicate when necessary.
9.  Calculate win rates using a stated denominator policy.
10. Report coverage, failures, uncertainty, and absolute-gate results.
11. Validate the preferred candidate against a held-out set and
    operational requirements.

For repeatable experiments, keep the query set fixed, but avoid
overfitting prompt changes to a small set of pairwise examples.

<br/>

## 9. Worked Example: Blinded Comparison

**Task:** Answer a question using only the supplied policy excerpt.

**Policy excerpt:** "Employees may claim up to ₹5,000 per trip. Claims
must be submitted within 30 days."

**Question:** "What is the reimbursement limit and submission deadline?"

Candidate A: \> "The limit is ₹5,000 per trip, and claims must be
submitted within 30 days."

Candidate B: \> "Employees can claim ₹5,000 per day. Claims should be
submitted within 30 days."

Using the rubric: - Correctness and evidence support: A preserves "per
trip"; B changes it to "per day." - Completeness: both mention a limit
and a deadline. - Clarity: both are understandable. - Faithfulness: B
distorts the policy's unit.

**Decision:** A wins. The reason should identify the specific factual
distinction rather than simply saying A is clearer.

Now consider a second pair:

Candidate A: \> "The policy says the limit is ₹5,000 per trip and the
deadline is 30 days."

Candidate B: \> "The policy allows a maximum reimbursement of ₹5,000 per
trip. Claims must be submitted within 30 days."

If both are fully supported and complete, a tie is reasonable. Do not
invent a meaningful preference merely to force a ranking.

<br/>

## 10. Python Example: Calculate Win Rates Transparently

``` python
from collections import Counter

outcomes = [
    "A_wins", "A_wins", "B_wins", "tie",
    "A_wins", "B_wins", "abstain", "missing",
    "A_wins", "tie"
]

counts = Counter(outcomes)
a_wins = counts["A_wins"]
b_wins = counts["B_wins"]
ties = counts["tie"]
abstentions = counts["abstain"]
missing = counts["missing"]

decisive_total = a_wins + b_wins
win_rate_excluding_ties = (
    a_wins / decisive_total if decisive_total else None
)

decisive_plus_ties = a_wins + b_wins + ties
tie_adjusted_rate = (
    (a_wins + 0.5 * ties) / decisive_plus_ties
    if decisive_plus_ties else None
)

print("Outcome counts:", dict(counts))
print("Assigned comparisons:", len(outcomes))
print("Decisive win rate for A:", win_rate_excluding_ties)
print("Tie-adjusted rate for A:", tie_adjusted_rate)
print("Abstentions:", abstentions)
print("Missing:", missing)
```

This code calculates two common summaries. A production report should
also include: - The number of assigned comparisons. - Counts and rates
of ties, abstentions, and missing results. - The absolute pass rate for
each candidate. - The rubric and model/prompt versions. - Uncertainty
estimates when the sample supports them. - Results by task category and
critical failure type.

<br/>

## 11. Practice: Small Blinded Comparison

A team compares Candidate A and Candidate B on six tasks. Model
identities are hidden, and reasons must refer to the rubric.

| Case | Candidate A                            | Candidate B                              | Review outcome                                                                      |
| ---- | -------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------- |
| 1    | Correct, complete, grounded            | Correct, complete, grounded              | Tie                                                                                 |
| 2    | Omits one requested field              | Includes all fields with evidence        | B wins: completeness                                                                |
| 3    | Correct answer with supported citation | Correct answer with nonexistent citation | A wins: citation validity                                                           |
| 4    | Concise and fully supported            | Longer, includes unsupported claim       | A wins: evidence support                                                            |
| 5    | Both answers contradict the source     | One also invents a citation              | Tie or B wins only if the rubric explicitly ranks severity; both fail absolute gate |
| 6    | Refuses an answerable question         | Answers correctly with evidence          | B wins, assuming no safety or permission issue                                      |


Tasks:

1.  Record a winner, tie, or abstention for each case.
2.  Explain each decision using a rubric criterion.
3.  Calculate A's decisive win rate, excluding ties.
4.  Calculate A's tie-adjusted win rate, including ties as half-wins.
5.  Explain why Case 5 cannot establish that either candidate is
    production-ready.
6.  Suggest a position-swap test to inspect order bias.

<br/>

### Suggested answers

1.  Cases 1 and 5 are ties under the stated default; B wins Cases 2 and
    6; A wins Cases 3 and 4.
2.  The reasons are respectively no material difference, completeness,
    citation validity, evidence support, both candidates fail the
    absolute criteria, and appropriate answering of an answerable
    request.
3. A has 2 wins and B has 3, so A's decisive win rate is $\frac{2}{2+3} = 40\%$.
4. With two ties, A's tie-adjusted rate is $\frac{2 + 0.5 \times 2}{2+3+2} = \frac{3}{7} \approx 42.9\%$.
5.  A relative preference between two bad answers does not satisfy an
    absolute correctness or groundedness threshold. Both must be marked
    as failing the absolute gate.
6.  Present each pair twice, once with A first and once with B first,
    using neutral labels. Record whether the preference flips despite
    unchanged content.

<br/>

## 12. Checkpoint

**Prompt:** Explain why winning against a weak baseline does not
establish production readiness.

**Model answer:**

Pairwise preference is relative to the alternatives being compared. A
candidate can win because the baseline is worse while still containing
hallucinations, omissions, invalid citations, security failures, or
unacceptable latency and cost. Production readiness requires absolute
acceptance thresholds, critical-failure checks, representative held-out
evaluation, uncertainty analysis, and operational validation. Pairwise
win rates should be reported with explicit denominators, ties,
abstentions, missing outputs, and failure counts; they are one part of
the release decision, not a substitute for it.

<br/>

## 13. Further Reading

-   [LangSmith evaluation
    concepts](https://docs.smith.langchain.com/evaluation) ---
    evaluation workflows, including comparative evaluation.
-   [RAGAS documentation](https://docs.ragas.io/) --- evaluation methods
    for RAG and LLM applications.
-   [DeepEval documentation](https://docs.confident-ai.com/) --- LLM
    evaluation metrics and testing workflows.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- risk-based evaluation and governance context.


<br/>


## Chapter Summary

Pairwise evaluation is effective for comparing open-ended outputs when
criteria are explicit and candidate identities are hidden. Allow ties
and abstentions, randomize order, inspect position effects, and attach
rubric-based reasons to decisions. State exactly how win rates handle
ties, missing outputs, and failures, and report coverage alongside
preference. Most importantly, distinguish relative preference from
absolute acceptability: a candidate that beats a weak baseline may still
fail production requirements.
