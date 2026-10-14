# 02. Task-Specific Quality Criteria

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Define the intended users, task, expected outcome, and consequential
    failure types for a GenAI application.
-   Translate broad requirements into observable criteria and anchored
    scoring rubrics.
-   Separate hard requirements, quality preferences, and operational
    budgets.
-   Specify when the system should answer, express uncertainty, ask for
    clarification, or abstain.
-   Explain what a passing evaluation score does---and does
    not---establish.

<br/>

## 2. Why Task-Specific Criteria Matter

"Good output" is not a universal property. A useful answer depends on
the user, task, context, and consequences of error.

For example, a concise summary may be excellent for an executive
briefing but inadequate for a compliance audit that requires every
exception to be listed. A plausible answer may be acceptable for
brainstorming but unacceptable for extracting a medical dosage or a
contractual deadline.

Evaluation criteria should therefore begin with the application's
purpose, not with a generic model score.

A task specification should identify:

1.  **User:** Who relies on the output, and what expertise or
    constraints do they have?
2.  **Task:** What must the system do?
3.  **Expected outcome:** What should a successful result enable the
    user to understand or do?
4.  **Evidence and context:** Which sources may support the answer?
5.  **Failure types:** What mistakes matter, and how severe are their
    consequences?
6.  **Operating constraints:** What latency, cost, format, and
    availability limits apply?

<br/>

## 3. From Product Requirement to Evaluation Criterion

Broad requirements are difficult to test directly. Convert them into
observable behaviors that can be judged consistently.

Example requirement:

> "The assistant should provide reliable summaries of customer-support
> conversations."

This is too vague to score consistently. It can be decomposed into
criteria:

-   Preserve the customer's main issue.
-   Preserve actions already taken and unresolved next steps.
-   Do not invent dates, promises, refunds, or policy details.
-   Distinguish confirmed facts from uncertain or conflicting
    statements.
-   Follow the requested length and format.
-   Finish within the service's latency and cost budgets.

Each criterion should describe evidence of success or failure. "Sounds
professional" may be a preference; "does not invent a refund approval"
is a testable requirement.

<br/>

### 3.1 Define the evaluation unit

Specify what is being scored:

-   **Whole response:** Is the final answer acceptable overall?
-   **Claim or fact:** Is each material claim supported?
-   **Field:** Is each structured field correct?
-   **Conversation or task:** Did the system complete the user's overall
    goal?
-   **Request or session:** Did the application meet latency, cost, and
    reliability constraints?

The unit affects the denominator. If one response contains five factual
claims, scoring only the response as "good" or "bad" can hide which
claim failed.

<br/>

## 4. Hard Requirements, Preferences, and Operational Budgets

These categories should be documented separately because they have
different consequences.

| Layer                   | Primary question                                     | Typical evidence                                                 |
| ----------------------- | ---------------------------------------------------- | ---------------------------------------------------------------- |
| Software tests          | Does the application obey its technical contract?    | Assertions, status codes, schema checks, integration results     |
| Task-quality evaluation | Is the answer good for the intended task?            | Rubric scores, reference checks, reviewed examples, task metrics |
| Operational monitoring  | Is the service reliable and efficient in production? | Latency, errors, throughput, usage, cost, feedback               |


Do not average away a critical hard-requirement violation. A response
that is beautifully written but fabricates a financial commitment should
fail if factual fidelity is mandatory.

Likewise, an answer can meet every content criterion but still be
unsuitable for production if its latency or cost exceeds the
application's budget.

<br/>

### 4.1 Example acceptance policy

For a support-summary application:

-   Hard requirements:
    -   No fabricated customer commitments.
    -   No omission of a critical unresolved issue.
    -   Output must conform to the required response schema.
-   Preferences:
    -   Concise, readable wording.
    -   Neutral and professional tone.
-   Operational budgets:
    -   p95 latency below 3 seconds at the defined test concurrency.
    -   Average cost below the application's agreed per-request limit.

The numeric latency target is illustrative. A real target must come from
product requirements and a documented workload.

<br/>

## 5. Designing an Anchored Scoring Rubric

A rubric defines criteria and what different scores mean. **Anchors**
are concrete descriptions or examples that distinguish score levels.
Without anchors, reviewers may interpret "4 out of 5" differently.

A simple 0--2 scale can be enough for a learning project:

-   **2 --- Pass:** Meets the criterion; no material defect.
-   **1 --- Borderline:** Partially meets it; a limited omission or
    ambiguity remains, but impact is bounded.
-   **0 --- Fail:** Violates the criterion or creates a consequential
    error.

Use criterion-specific anchors rather than relying only on generic
labels.

<br/>

### 5.1 Example: support-conversation summarization rubric

Assume the source conversation states that a customer cannot export a
report, support has escalated the issue to engineering, and no
resolution date has been promised.

| Criterion          | 2 --- Acceptable                                                  | 1 --- Borderline                                              | 0 --- Failing                                        |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| Main issue         | Clearly states that report export fails                           | Mentions a report problem but is vague                        | Omits or changes the main issue                      |
| Actions and status | States that the issue was escalated and remains unresolved        | Mentions escalation but leaves status unclear                 | Claims it was resolved when it was not               |
| Factual fidelity   | Adds no unsupported details or promises                           | Uses ambiguous wording that could imply an unconfirmed detail | Invents a fix, refund, or resolution date            |
| Next steps         | Preserves the actual next step or clearly says none was specified | Gives a vague next step without changing the facts            | Invents an owner, deadline, or commitment            |
| Conciseness        | Includes decision-relevant details without repetition             | Some repetition or unnecessary detail                         | So verbose or incomplete that it defeats the purpose |


A score of 0 for a critical factual-fidelity violation should trigger a
failure even if other criteria score 2. Define such veto rules before
running the evaluation.

<br/>

### 5.2 Weighted scoring

When criteria have different importance, a weighted score can summarize
performance:

$$
S = \frac{\sum_{i=1}^{n} w_i s_i}{\sum_{i=1}^{n} w_i s_{i,\max}} \times 100
$$

Where:

- $s_i$ is the score for criterion $i$.
- $s_{i,\max}$ is the maximum possible score for that criterion.
- $w_i$ is its weight.

**Illustrative example:** Four criteria receive scores of 2, 2, 1, and 2 on a 0–2 scale, with equal weights.

$$
S = \frac{2+2+1+2}{2+2+2+2} \times 100 = 87.5\%
$$

That percentage is a summary, not a universal guarantee of quality. If
the score of 1 reflects a critical requirement, the application may
still fail. Report critical failures separately from the aggregate
score.

<br/>

## 6. Define Abstention and Acceptable Uncertainty

A reliable system should not be forced to answer every question.
**Abstention** means explicitly declining to provide a substantive
answer when the available evidence or confidence is insufficient for the
task.

Possible actions include:

-   **Answer:** Evidence is sufficient and the request is within scope.
-   **Answer with qualification:** Provide a limited answer while
    clearly stating uncertainty or evidence gaps.
-   **Ask for clarification:** A missing detail changes the answer
    materially.
-   **Abstain or escalate:** Evidence is absent, conflicting, out of
    scope, or too weak for the consequences of an error.

These behaviors should be evaluated as part of task success---not
treated automatically as failures.

<br/>

### 6.1 Example decision policy

``` mermaid
flowchart TD
    A[Receive request] --> B{Is the request in scope?}
    B -- No --> E[Explain limitation or abstain]
    B -- Yes --> C{Is sufficient evidence available?}
    C -- Yes --> D[Answer with supported claims]
    C -- Partly --> F{Can clarification resolve the gap?}
    F -- Yes --> G[Ask a focused question]
    F -- No --> H[Give a qualified answer or abstain]
    C -- No --> I[Abstain or escalate]
```

For a knowledge-base assistant, if a user asks for a policy deadline and
no authorized source contains that deadline, the assistant should not
invent one. A passing response might state that the deadline could not
be verified and direct the user to the appropriate process.

<br/>

### 6.2 Acceptable uncertainty depends on risk

The acceptable uncertainty threshold is application-specific:

-   **Low consequence:** A brainstorming assistant can offer
    possibilities with clear caveats.
-   **Moderate consequence:** A support assistant should distinguish
    confirmed policy from an inference and escalate unresolved cases.
-   **High consequence:** A system used in consequential domains may
    require verified evidence and human review; abstention may be
    preferable to a speculative answer.

Do not treat a model's self-reported confidence as calibrated
probability unless it has been validated for that purpose. Fluent
wording is not evidence of certainty.

<br/>

## 7. Worked Example: Score Three Outputs

### Scenario

A support agent asks the model to summarize this conversation:

> The customer cannot export a monthly report. Support reproduced the
> issue and escalated it to engineering. Engineering has not confirmed a
> fix or delivery date.

Required facts:

1.  The export problem remains unresolved.
2.  Support escalated it to engineering.
3.  No fix or delivery date is confirmed.
4.  The summary must not invent commitments.

**Output A --- Acceptable**

> Monthly report export is failing. Support reproduced the issue and
> escalated it to engineering; no fix or delivery date has been
> confirmed.

Why it passes: It preserves the issue, action, unresolved status, and
uncertainty without adding claims.

**Output B --- Borderline**

> The customer has a reporting issue, and engineering is looking into
> it.

Why it is borderline: It broadly captures the issue and investigation
but omits the specific export failure and does not preserve the explicit
absence of a confirmed fix or date. It may be insufficient for a support
handoff.

**Output C --- Failing**

> Engineering will fix the export issue tomorrow.

Why it fails: It invents both a commitment and a deadline. If avoiding
fabricated commitments is a hard requirement, this is a critical failure
regardless of style or brevity.

<br/>

## 8. Practice

### Exercise A --- Define the task

Choose a GenAI application, such as a document Q&A assistant, support
summarizer, or invoice extractor. Write:

-   Intended user.
-   Input and task.
-   Expected successful outcome.
-   Evidence the system is allowed to use.
-   Three consequential failure types.
-   One hard requirement, one quality preference, and one operational
    budget.

<br/>

### Exercise B --- Write an anchored rubric

For a summarization service, define at least four criteria. For each
criterion, specify what an acceptable, borderline, and failing output
looks like. Include one critical failure that cannot be offset by a high
average score.

<br/>

### Exercise C --- Define abstention

Write a policy for three cases:

1.  The answer is supported by an authorized source.
2.  The evidence is incomplete or ambiguous.
3.  No evidence supports the requested fact.

Specify whether the system should answer, qualify, clarify, abstain, or
escalate.

<br/>

## 9. Practice Example Answer

For a customer-support summarizer:

-   **User:** Support agent taking over an ongoing case.
-   **Task:** Summarize the customer's issue, actions taken, current
    status, and next step.
-   **Expected outcome:** A concise handoff that preserves all
    decision-relevant facts.
-   **Allowed evidence:** The supplied conversation and approved case
    metadata.
-   **Consequential failures:** Fabricated refund or deadline; falsely
    claiming resolution; omission of a critical unresolved issue.
-   **Hard requirement:** No invented commitments.
-   **Preference:** Concise, neutral language.
-   **Operational budget:** p95 latency under a product-defined
    threshold at a documented concurrency.

Example rubric:

| Criterion          | 2 --- Acceptable                                                  | 1 --- Borderline                                              | 0 --- Failing                                        |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| Main issue         | Clearly states that report export fails                           | Mentions a report problem but is vague                        | Omits or changes the main issue                      |
| Actions and status | States that the issue was escalated and remains unresolved        | Mentions escalation but leaves status unclear                 | Claims it was resolved when it was not               |
| Factual fidelity   | Adds no unsupported details or promises                           | Uses ambiguous wording that could imply an unconfirmed detail | Invents a fix, refund, or resolution date            |
| Next steps         | Preserves the actual next step or clearly says none was specified | Gives a vague next step without changing the facts            | Invents an owner, deadline, or commitment            |
| Conciseness        | Includes decision-relevant details without repetition             | Some repetition or unnecessary detail                         | So verbose or incomplete that it defeats the purpose |


Abstention policy:

-   Supported by an authorized source: answer with the supporting facts.
-   Evidence incomplete: qualify the answer or ask a focused
    clarification question.
-   No evidence: state that the fact cannot be verified; abstain or
    escalate rather than inventing an answer.

<br/>

## 10. Checkpoint

**Question:** Explain what a passing score means for the application.

**Answer:** A passing score means the evaluated outputs met the
predefined acceptance criteria on the specified dataset, under the
documented evaluation procedure and thresholds. It does not mean that
every possible request will be handled correctly or that the application
is automatically production-ready. The conclusion depends on dataset
representativeness, rubric quality, critical-failure rules, sample size,
uncertainty, operating conditions, and the application's latency, cost,
privacy, and reliability requirements. A critical violation may still
fail the application even when the average score is high.

<br/>

## 11. References

-   [OpenAI --- Evaluation best
    practices](https://platform.openai.com/docs/guides/evaluation-best-practices)
-   [OpenAI Cookbook --- Evals examples](https://cookbook.openai.com/)
-   [Pydantic --- Models and
    validation](https://docs.pydantic.dev/latest/concepts/models/)
-   [NIST --- AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)

Use the references as supporting implementation guidance. The acceptance
criteria and scoring anchors must be tailored to the specific
application and its consequences.

<br/>

## 12. Revision Summary

-   Start evaluation design with users, tasks, outcomes, evidence, and
    consequential failures.
-   Translate vague requirements into observable criteria and anchored
    examples.
-   Keep hard requirements, preferences, and operational budgets
    distinct.
-   Define answer, qualification, clarification, abstention, and
    escalation behavior explicitly.
-   Use weighted scores carefully and report critical failures
    separately.
-   A passing score is evidence about the tested cases and
    procedure---not a universal guarantee of correctness or production
    readiness.
