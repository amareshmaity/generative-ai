# 09. RAG Answer Quality and Groundedness

## Learning Objectives

By the end of this chapter, you should be able to:

-   Evaluate retrieval and generation independently before inspecting
    the full RAG pipeline.
-   Assess answer correctness, evidence coverage, faithful use of
    evidence, and citation support.
-   Verify citation identifiers and whether cited passages support their
    associated claims.
-   Include unanswerable, conflicting-source, stale-source, and
    permission-restricted cases.
-   Keep authorization tests distinct from relevance and answer-quality
    scores.
-   Diagnose whether a failure came from absent evidence or misuse of
    available evidence.

<br/>

## 1. Why RAG Needs Stage-by-Stage Evaluation

Retrieval-augmented generation (RAG) systems combine at least two
important stages:

1.  **Retrieval:** find evidence relevant to the user's query.
2.  **Generation:** use the retrieved evidence to produce an answer.

A final answer can fail because the retriever did not find the needed
evidence, because the generator misused evidence that was available, or
because both stages failed. Evaluating only the final answer does not
reliably identify the cause.

A RAG evaluation should therefore measure:

-   **Retrieval quality:** Was sufficient, relevant, authorized evidence
    retrieved?
-   **Generation quality given retrieved context:** Did the model use
    that context accurately?
-   **End-to-end answer quality:** Did the user receive a correct,
    complete, relevant, well-supported answer?
-   **Citation quality:** Do citation IDs resolve, and do cited passages
    support the claims they accompany?
-   **Authorization behavior:** Was the system permitted to retrieve and
    disclose the information?

Authorization is a separate security requirement. A highly relevant
answer can still be a critical failure if it reveals information the
user is not allowed to access.

``` mermaid
flowchart TD
    A[Query and user permissions] --> B[Retriever]
    B --> C[Retrieved passages]
    C --> D[Evaluate retrieval sufficiency and relevance]
    C --> E[Generator]
    E --> F[Answer and citations]
    F --> G[Evaluate correctness, completeness, faithfulness, citations]
    A --> H[Authorization tests]
    B --> H
    F --> H
    D --> I[Stage diagnosis]
    G --> I
    H --> J[Separate security result]
    I --> K[End-to-end decision]
    J --> K
```

<br/>

## 2. The Main Dimensions of RAG Answer Quality

 | Dimension                   | Evaluation question                                                       | Example failure                                    |
| --------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------- |
| Answer correctness          | Is the answer factually correct for the task and time frame?              | Gives an incorrect deadline                        |
| Relevance                   | Does it answer the user's actual question?                                | Provides background but not the requested result   |
| Completeness                | Does it cover all required parts?                                         | Omits an exception or a second requested item      |
| Evidence coverage           | Is sufficient evidence available and used to support the answer's claims? | Leaves a key requested claim unsupported           |
| Faithfulness / groundedness | Does the answer preserve the meaning and limits of retrieved evidence?    | Converts "may" into "will"                         |
| Citation validity           | Does each cited identifier resolve to a real retrieved source or passage? | References a nonexistent passage ID                |
| Citation support            | Does the cited passage support the specific claim?                        | Cites a paragraph that discusses a different topic |
| Authorization               | Is the user allowed to receive this information?                          | Discloses a restricted record                      |

Do not collapse these dimensions into one vague "RAG score." A system
can retrieve good evidence but generate an incorrect answer, or generate
a plausible answer when retrieval found no adequate evidence.

<br/>

## 3. Evaluate Retrieval and Generation Independently

### 3.1 Retrieval evaluation

Before inspecting generated answers, evaluate the retriever against
known relevance judgments or a curated evidence set.

Questions include:

-   Did the top-(k) results contain the evidence needed to answer?
-   Were key passages ranked high enough to enter the generator's
    context window?
-   Were relevant passages omitted?
-   Were duplicates or irrelevant passages crowding out useful evidence?
-   Were all retrieved sources authorized for the current user?
-   Were source versions current enough for the task?

Use retrieval metrics from the previous chapter where appropriate, such
as Precision@k, Recall@k, MRR, or nDCG. Add an **evidence sufficiency**
label when the task requires a specific passage or combination of
passages to answer.

<br/>

### 3.2 Generation evaluation with retrieved context

Hold the retrieved context fixed and assess whether the generator uses
it correctly.

Questions include:

-   Are answer claims entailed or reasonably supported by the retrieved
    passages?
-   Does the answer include every required point?
-   Does it preserve uncertainty, qualifications, and scope?
-   Does it avoid adding unsupported facts?
-   Does it cite the correct passages for the claims?
-   Does it abstain when the supplied context is insufficient,
    conflicting, or outside the permitted scope?

This isolates generator behavior from retriever behavior.

<br/>

### 3.3 Generation with known-sufficient evidence

For diagnosis, run a separate test using curated evidence known to be
sufficient for the question. This can help answer: "Could the generator
have answered correctly if the needed evidence had been available?"

-   If generation succeeds with known-sufficient evidence but fails with
    the retriever's context, retrieval or context assembly is a likely
    cause.
-   If generation fails even with known-sufficient evidence, generation,
    prompt instructions, context interpretation, or answer formatting
    may be at fault.
-   If both tests fail, more than one component may need investigation.

Known-sufficient evidence is a diagnostic fixture, not a substitute for
evaluating the production retriever.

<br/>

## 4. Evidence Coverage, Faithfulness, and Correctness

### 4.1 Evidence coverage

Evidence coverage asks whether the answer's required claims are backed
by adequate evidence and whether the evidence needed to answer the
question is represented.

For multi-part questions, create a checklist of required answer elements
and link each element to evidence. An answer may be grounded in one
claim but omit another essential claim.

<br/>

### 4.2 Faithfulness / groundedness

Faithfulness checks whether the answer accurately represents the
supplied context. Look for:

-   Unsupported additions.
-   Distorted numbers, names, dates, or relationships.
-   Lost qualifiers such as "may," "typically," or "in the tested
    environment."
-   Unsupported causal claims.
-   Omitted limitations that change the meaning.
-   Silent resolution of disagreements between sources.

A response can be faithful to a flawed source and still be factually
wrong in the world. If the task is source-grounded question answering,
assess source faithfulness; if the task requires fact-checking,
independently verify claims too.

<br/>

### 4.3 Correctness

Correctness asks whether the answer itself is right according to the
task's reference standard. The reference may be a gold answer, a
verified record, a domain expert, or an authoritative source.

A faithful answer is not necessarily correct if the source is stale or
erroneous. Likewise, an answer may be correct by coincidence but
unsupported by the retrieved evidence. Record both properties
separately.

<br/>

## 5. Citation Identifiers and Citation Support

Citations need at least two independent checks.

### 5.1 Citation validity

Does the citation identifier resolve to a real source or passage that
was available to the system?

Examples of citation-validity failures:

-   A passage ID does not exist.
-   A citation refers to a source not included in the retrieval result
    or permitted evidence set.
-   A document identifier is malformed or points to the wrong version.
-   The answer cites a URL or document that the evaluator cannot access.

A valid identifier is only a pointer. It does not prove that the source
supports the claim.

<br/>

### 5.2 Citation support

For every cited factual claim, inspect whether the cited passage
supports that claim.

A practical claim-citation review can use these labels:

-   `supported`: passage directly supports the claim.
-   `partially_supported`: passage supports only part of a compound
    claim.
-   `unsupported`: passage does not provide adequate support.
-   `contradicted`: passage conflicts with the claim.
-   `not_verifiable`: citation cannot be inspected or evidence is
    insufficient to decide.

Example:

Source P12: "The service supports PDF uploads up to 20 MB."

Answer: "The service supports PDF uploads up to 20 MB [P12]."

- Citation ID valid: yes, if P12 exists in the permitted retrieved set.
- Citation support: yes.

Answer: "The service supports PDF uploads up to 100 MB [P12]."

- Citation ID valid: yes.
- Citation support: no; the passage specifies 20 MB, not 100 MB.

Answer: "The service supports PDF uploads up to 20 MB [P99]."

- Citation ID valid: no, if P99 does not exist in the permitted retrieved set.
- Citation support: no / unsupported.

-   Citation ID valid: no, if P99 does not exist.
-   Citation support: cannot be established through P99, even if another
    passage happens to contain the correct limit.

<br/>

### 5.3 Citation granularity

Define whether citations must support:

-   Every factual sentence.
-   Every atomic factual claim.
-   Each bullet or paragraph.
-   A specific answer field.

For high-stakes or audit-sensitive use, claim-level citation checks are
often more informative than checking whether the answer contains any
citations at all.

<br/>

## 6. A Claim-to-Evidence Ledger

Create a ledger to make groundedness review auditable.

| Claim ID | Answer claim                              | Evidence ID | Support label | Correctness                     | Notes                         |
| -------- | ----------------------------------------- | ----------- | ------------- | ------------------------------- | ----------------------------- |
| C1       | "The migration failed during validation." | P3          | Supported     | Verified against task reference | Direct statement              |
| C2       | "The fix will ship tomorrow."             | None        | Unsupported   | Unknown                         | No date in retrieved evidence |
| C3       | "The service supports 100 MB uploads."    | P12         | Contradicted  | False relative to source        | Source says 20 MB             |


A ledger should preserve the exact claim and the evidence used to judge
it. For each run, record the query, user permission context, retrieved
passage IDs, source versions, prompt/model versions, and evaluation
rubric version.

A useful record schema may include:

``` json
{
  "query_id": "q-017",
  "claim_id": "c2",
  "claim_text": "The fix will ship tomorrow.",
  "citation_ids": [],
  "citation_id_validity": "not_applicable",
  "evidence_support": "unsupported",
  "correctness": "unknown",
  "answerability": "insufficient_evidence",
  "authorization": "permitted"
}
```

These values are illustrative. Define allowed labels and decision rules
in the evaluation protocol.

<br/>

## 7. Essential Test Cases

A robust RAG evaluation set should include more than ordinary answerable
questions.

### 7.1 Answerable with sufficient evidence

The required facts exist in current, authorized sources. The expected
answer should be accurate, complete, and appropriately cited.

<br/>

### 7.2 Unanswerable from the corpus

The answer is not present in the permitted corpus. The expected behavior
may be a clear statement of insufficient evidence, a clarifying
question, or a permitted escalation.

Do not mark a system wrong for failing to retrieve nonexistent evidence.
Evaluate whether it avoids inventing an answer and handles the request
appropriately.

<br/>

### 7.3 Conflicting sources

Two or more sources disagree. The evaluation rubric should specify
whether the system must prefer an authoritative source, use the latest
valid version, explain the conflict, or abstain pending clarification.

Example: - Policy version 1 says a limit is 10. - Policy version 2 says
a limit is 15. - The task context does not identify which policy
applies.

A strong response should not silently present one value as certain
unless a documented precedence rule resolves the conflict.

<br/>

### 7.4 Stale sources

A retrieved document may be relevant but out of date. Include version,
effective-date, or supersession metadata in test cases. Evaluate whether
the system uses the current source or communicates the uncertainty when
currency cannot be established.

<br/>

### 7.5 Permission-restricted sources

Some sources may be relevant but unavailable to the current user. Tests
should verify that retrieval filters enforce access controls and that
the answer does not reveal restricted content indirectly.

Authorization failures should be treated as security failures, not
merely low relevance or low answer-quality scores.

<br/>

### 7.6 Adversarial and ambiguous questions

Include misleading premises, ambiguous references, requests for
information outside the corpus, and prompts that encourage the model to
ignore source limitations. Define whether the correct response is
clarification, evidence-qualified answering, or abstention.

<br/>

## 8. Authorization Tests Must Remain Separate

Relevance asks whether a passage helps answer the question.
Authorization asks whether the user is permitted to access it. These are
independent.

A restricted passage can be highly relevant and still must not be
returned or disclosed. Conversely, an authorized passage can be
irrelevant.

Track security outcomes such as:

-   Unauthorized document retrieved.
-   Restricted text included in prompt context.
-   Restricted fact disclosed in the answer.
-   Citation exposed a restricted document or metadata.
-   Permission filter applied correctly.
-   User-specific access rules changed between retrieval and response.

Use access-control fixtures with explicit user identities or permission
classes in a controlled test environment. Do not place real sensitive
content in general-purpose evaluation datasets. Test both retrieval
filtering and downstream leakage: a document may be filtered from
visible citations but still leak through generated text if it entered
the model context.

Report authorization pass rate and critical leakage counts separately
from relevance, groundedness, and answer correctness. A zero-tolerance
release gate may be appropriate for unauthorized disclosure, depending
on the application risk.

<br/>

## 9. Worked Diagnosis: Retrieved Context Versus Known-Sufficient Evidence

### Query

"What caused the deployment delay, and is a resolution date confirmed?"

<br/>

### Reference evidence

> "The deployment was delayed because a database migration failed during
> validation. The team is investigating. No resolution date has been
> confirmed."

<br/>

### Run A: Retriever omitted the key passage

Retrieved context: - P1: "The deployment team uses a weekly release
process." - P2: "Database migrations are reviewed before release."

Generated answer: \> "The report does not specify the cause of the delay
or a confirmed resolution date."

Evaluation: - The answer is appropriately cautious relative to the
retrieved context. - Retrieval failed to supply the key evidence, so the
context was insufficient. - The generator may have behaved correctly
given the available evidence. - End-to-end task performance still fails
to answer the cause.

Now provide known-sufficient evidence to the same generation setup.

Generated answer with reference evidence: \> "The delay was caused by a
database migration failure during validation. No resolution date has
been confirmed."

If this answer succeeds, the likely primary failure is retrieval or
context assembly, not generation.

<br/>

### Run B: Retriever found the key passage, but generation misused it

Retrieved context: - P3: "The deployment was delayed because a database
migration failed during validation. The team is investigating. No
resolution date has been confirmed."

Generated answer: \> "A database migration failed during validation, and
the deployment will be fixed tomorrow."

Evaluation: - Retrieval supplied sufficient evidence. - The stated cause
is supported. - "Will be fixed tomorrow" is unsupported and contradicts
the source's uncertainty. - This is a generation faithfulness failure,
even though retrieval succeeded.

<br/>

### Diagnostic matrix

| Retrieved evidence                         | Answer behavior                         | Likely diagnosis                                        |
| ------------------------------------------ | --------------------------------------- | ------------------------------------------------------- |
| Insufficient                               | Correctly abstains or states limitation | Retrieval/context-assembly gap for the requested answer |
| Insufficient                               | Invents confident answer                | Retrieval gap plus generation groundedness failure      |
| Sufficient                                 | Uses evidence accurately                | Successful retrieval and generation                     |
| Sufficient                                 | Omits or distorts evidence              | Generation, prompt, or answer-assembly failure          |
| Restricted evidence retrieved or disclosed | Any otherwise-good answer               | Authorization/security failure                          |


This matrix helps localize failures without assuming that every bad
final answer was caused by the generator.

<br/>

## 10. Python Example: Separate Stage Outcomes

The following small example records retrieval sufficiency, generation
groundedness, and authorization independently. The labels are supplied
by an evaluator or another validated process; the code does not infer
them automatically.

``` python
from dataclasses import dataclass, asdict
import json

@dataclass
class RAGEvaluation:
    query_id: str
    retrieval_sufficient: bool
    answer_correct: str       # "yes", "no", "unknown"
    answer_faithful: str      # "yes", "no", "unknown"
    citation_ids_valid: str   # "yes", "no", "not_applicable"
    citations_supported: str  # "yes", "no", "partial", "unknown"
    authorization_pass: bool
    failure_stage: str

cases = [
    RAGEvaluation(
        query_id="q-01",
        retrieval_sufficient=False,
        answer_correct="unknown",
        answer_faithful="yes",
        citation_ids_valid="not_applicable",
        citations_supported="unknown",
        authorization_pass=True,
        failure_stage="retrieval_or_context_assembly"
    ),
    RAGEvaluation(
        query_id="q-02",
        retrieval_sufficient=True,
        answer_correct="no",
        answer_faithful="no",
        citation_ids_valid="yes",
        citations_supported="partial",
        authorization_pass=True,
        failure_stage="generation"
    ),
]

print(json.dumps([asdict(case) for case in cases], indent=2))
```

For production evaluation, also store the retrieved passage IDs, source
versions, query category, expected answer elements, model and prompt
versions, latency, and reviewer notes. Define the label vocabulary and
use consistent annotation instructions.

<br/>

## 11. Practice: Compare Retrieved and Known-Sufficient Evidence

For each case, determine whether the primary failure is retrieval,
generation, both, or neither. Also assess correctness, faithfulness,
citation support, and authorization separately.

<br/>

### Case 1: Missing evidence, cautious answer

Question: "What is the approved reimbursement limit?"

Known source: "The approved reimbursement limit is ₹5,000 per trip."

Retrieved context contains only a general travel-policy introduction and
does not mention the limit.

Answer: "The retrieved material does not state the reimbursement limit."

<br/>

### Case 2: Missing evidence, invented answer

Use the same question and retrieved context as Case 1.

Answer: "The approved reimbursement limit is ₹10,000 per trip."

<br/>

### Case 3: Evidence available, but distorted

Retrieved source: "The approved reimbursement limit is ₹5,000 per trip."

Answer: "The approved reimbursement limit is ₹5,000 per day."

<br/>

### Case 4: Citation ID invalid

Retrieved passage P4: "The service supports exports in CSV format."

Answer: "The service supports CSV exports \[P99\]."

Assume P99 does not exist in the retrieved set.

<br/>

### Case 5: Relevant but restricted

A retrieved document contains the exact answer to the user's question,
but the current user does not have permission to access that document.
The system includes the restricted fact in its response.

<br/>

### Case 6: Conflicting sources

Source P1, last updated in 2022: "The retention period is 30 days."

Source P2, effective in 2026: "The retention period is 90 days."

The application has a documented rule to prefer the current effective
policy. The answer says: "The retention period is 30 days \[P1\]."

<br/>

### Suggested answers

1.  **Retrieval/context-assembly failure for answering the question.**
    The answer is appropriately cautious given the retrieved context,
    but end-to-end completion fails. With known-sufficient evidence, the
    generator should be tested again.
2.  **Retrieval and generation failure.** The evidence was absent from
    context, and the answer invents a value. Correctness is
    unsupported/unknown without independent verification; groundedness
    fails.
3.  **Generation faithfulness failure.** The source says "per trip," but
    the answer changes it to "per day." Retrieval was sufficient; the
    answer distorts the evidence.
4.  **Citation validity failure.** The claim may be supported by P4 in
    the retrieved context, but the cited ID P99 is invalid. Citation
    support cannot be established through the cited identifier.
5.  **Authorization/security failure.** Relevance does not grant
    permission. The disclosure is a critical access-control failure
    regardless of answer correctness.
6.  **Source selection and generation failure under the stated
    precedence rule.** The answer uses a stale source despite a current
    effective source. The evaluation should check both source-version
    selection and the final claim.

<br/>

## 12. Checkpoint

**Prompt:** Explain whether a failure comes from absent evidence or
misuse of available evidence.

**Model answer:**

First, evaluate the retrieved context independently against the evidence
needed to answer the query. If required evidence is absent, retrieval or
context assembly is a likely failure. Then provide known-sufficient
evidence to the generator. If the generator answers correctly with that
evidence but not with retrieved context, the retrieval stage is
implicated. If sufficient evidence was already present and the answer
omits, distorts, contradicts, or overstates it, the likely failure is
generation or answer assembly. If both the retrieved context and the
generated answer are deficient, both stages may need changes. Citation
validity and support must be checked separately, and authorization must
remain a distinct security evaluation.

<br/>

## 13. Further Reading

-   [RAGAS documentation](https://docs.ragas.io/) --- RAG evaluation
    concepts and metrics.
-   [LangSmith evaluation
    concepts](https://docs.smith.langchain.com/evaluation) ---
    evaluation workflows for LLM applications.
-   [DeepEval documentation](https://docs.confident-ai.com/) --- LLM
    evaluation metrics and testing workflows.
-   [OWASP Top 10 for LLM
    Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
    --- security risks including sensitive information disclosure and
    access-control concerns.
-   [NIST AI Risk Management
    Framework](https://www.nist.gov/itl/ai-risk-management-framework)
    --- broader AI risk management context.


<br/>


## Chapter Summary

Evaluate RAG retrieval, generation, citations, and authorization as
distinct but connected components. First establish whether sufficient,
current, relevant, and authorized evidence was retrieved. Then assess
whether the generator used that evidence accurately, completely, and
faithfully. Verify both citation identifiers and claim-level support.
Include unanswerable, conflicting-source, stale-source, and
permission-restricted cases. Diagnose absent evidence separately from
misuse of available evidence, and never treat a relevance score as proof
of authorization or end-to-end answer quality.
