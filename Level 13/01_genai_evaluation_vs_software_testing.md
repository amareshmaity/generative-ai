# 01. Why GenAI Evaluation Differs from Conventional Testing

## 1. Learning Objectives

By the end of this chapter, you should be able to:

-   Compare deterministic application contracts with variable
    generative-model behavior.
-   Distinguish software unit/integration tests, task-quality
    evaluation, and operational monitoring.
-   Explain why a task can have multiple acceptable answers and why
    repeated model runs can differ.
-   Identify when exact expected values are still the right test.
-   Design separate endpoint tests and quality checks for a
    summarization service.

<br/>

## 2. The Core Difference

Conventional software usually follows explicitly programmed logic. Given
the same inputs and environment, a deterministic function is expected to
return the same result. A test can often assert an exact value.

``` python
def add_tax(price: float, rate: float) -> float:
    return round(price * (1 + rate), 2)

assert add_tax(100.00, 0.05) == 105.00
```

A generative AI application includes a model that predicts or generates
an output based on learned patterns. Even when the request is unchanged,
outputs can vary because of sampling settings, model/provider changes,
hidden system behavior, or other inference conditions. A correct
response may also be worded in several different ways.

For example, a summarization service may summarize the same paragraph
as:

-   "The launch was delayed because testing uncovered two critical
    defects."
-   "Two critical defects found during testing pushed back the launch."
-   "Testing found two serious bugs, so the launch was postponed."

These differ lexically but may convey the same essential information. An
exact string comparison would reject two valid summaries.

**Key principle:** Test deterministic contracts deterministically.
Evaluate generated content against task-specific criteria rather than
assuming that one exact wording is the only correct answer.

<br/>

## 3. Deterministic Contracts vs. Probabilistic Outputs
| Dimension        | Conventional application behavior                    | GenAI behavior                                                                    |
| ---------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| Expected result  | Often specified exactly                              | Often described by criteria or a rubric                                           |
| Output variation | Usually a defect when not expected                   | May be normal and acceptable                                                      |
| Test oracle      | Exact expected value or invariant                    | Reference facts, rubric, evidence, task-specific metrics, and/or human review     |
| Failure examples | Wrong status code, corrupted value, broken invariant | Omission, fabrication, irrelevance, unsupported claim, poor instruction following |
| Repeated runs    | Commonly expected to match for deterministic logic   | May differ; stability must be measured where important                            |
| Main question    | "Did the program obey its contract?"                 | "Did the application produce a useful, correct, and appropriate result?"          |


A model-backed application still contains ordinary software contracts.
Do not treat every failure as an "AI problem." An HTTP 500 response is
an endpoint failure; a fluent but inaccurate summary is a task-quality
failure. The same request can fail in both ways.

<br/>

### 3.1 Sources of variation

Generated results may change due to:

-   **Sampling settings:** temperature, top-p, or other supported
    decoding parameters.
-   **Model or provider updates:** a model identifier may point to a
    revised implementation, or service behavior may change.
-   **Prompt and context changes:** even small edits can affect the
    output.
-   **Retrieved evidence:** a RAG application may retrieve different
    passages when the index or ranking configuration changes.
-   **Execution conditions:** retries, truncation, token limits, or
    tool/API errors can alter what the user receives.

Setting temperature to zero can reduce some sampling variation, but it
does **not** guarantee universal bit-for-bit reproducibility across all
providers, model versions, hardware, or service updates.

<br/>

## 4. Three Complementary Evaluation Layers

A reliable GenAI application needs multiple kinds of checks. They answer
different questions and should not be collapsed into a single score.

``` mermaid
flowchart TD
    A[User request] --> B[Application and API]
    B --> C[Model inference]
    C --> D[Generated response]
    D --> E[Software contract tests]
    D --> F[Task-quality evaluation]
    B --> G[Operational telemetry]
    C --> G
    E --> H[Release decision]
    F --> H
    G --> H
```

<br/>

### 4.1 Unit and integration tests

**Purpose:** Verify that the surrounding software behaves according to
its contract.

Examples:

-   The endpoint rejects a missing required field.
-   Authentication is enforced.
-   The model client is called with the intended prompt and
    configuration.
-   The response is valid JSON and conforms to a schema.
-   Timeouts and provider errors are handled safely.
-   An integration test verifies that the API, model adapter, and
    persistence layer work together.

These tests should be repeatable and fast where possible. Use mocks or
fixed model-output fixtures for deterministic tests of application
logic. A fixture is a prepared example, not evidence of live model
quality.

<br/>

### 4.2 Task-quality evaluation

**Purpose:** Assess whether the model output accomplishes the user's
task.

For summarization, criteria might include:

-   **Factual correctness:** Are statements consistent with the source?
-   **Coverage:** Are the important points included?
-   **Faithfulness:** Does the summary avoid adding unsupported claims?
-   **Relevance:** Does it focus on the requested information?
-   **Conciseness:** Does it avoid unnecessary detail?
-   **Instruction following:** Does it obey length, audience, or format
    requirements?

Task-quality evaluation can combine deterministic checks, task-specific
metrics, human review, and a calibrated LLM judge. The method should fit
the task; no single metric is suitable for every generative task.

<br/>

### 4.3 Operational monitoring

**Purpose:** Determine how the application behaves in real use.

Monitor measures such as:

-   End-to-end latency and, for streaming, time to first token.
-   Request volume, throughput, and error rate.
-   Input/output token usage and estimated or provider-reported cost.
-   Rate-limit events, retries, timeouts, and truncation.
-   User feedback and verified task outcomes, where collection is
    permitted.
-   Changes in input distribution or quality over time.

Monitoring is not a substitute for offline evaluation. A low latency or
low error rate does not prove that the answers are correct. Conversely,
a model may be high-quality in an offline test set but fail
operationally under load.

| Layer                   | Primary question                                     | Typical evidence                                                 |
| ----------------------- | ---------------------------------------------------- | ---------------------------------------------------------------- |
| Software tests          | Does the application obey its technical contract?    | Assertions, status codes, schema checks, integration results     |
| Task-quality evaluation | Is the answer good for the intended task?            | Rubric scores, reference checks, reviewed examples, task metrics |
| Operational monitoring  | Is the service reliable and efficient in production? | Latency, errors, throughput, usage, cost, feedback               |


<br/>

## 5. Multiple Acceptable Answers and Test Oracles

A **test oracle** is the mechanism used to decide whether a result is
acceptable.

For deterministic transformations, the oracle may be an exact expected
value. For open-ended generation, a better oracle often describes
required facts and constraints.

<br/>

### Example: summarization

**Source text**

> The company planned to release the reporting feature on 12 June.
> During final testing, the team found two critical defects affecting
> exported reports. The release was postponed until the defects could be
> fixed and verified. The team has not announced a new release date.

**Possible acceptable summary**

> The reporting feature's 12 June release was postponed after testing
> found two critical export defects. A new date has not been announced.

**Possible unacceptable summary**

> The reporting feature launched on 12 June after the team fixed two
> minor defects.

The unacceptable version changes the release status, downgrades defect
severity, and invents a successful launch.

A useful rubric can specify required facts and disallowed claims:

| Layer                   | Primary question                                     | Typical evidence                                                 |
| ----------------------- | ---------------------------------------------------- | ---------------------------------------------------------------- |
| Software tests          | Does the application obey its technical contract?    | Assertions, status codes, schema checks, integration results     |
| Task-quality evaluation | Is the answer good for the intended task?            | Rubric scores, reference checks, reviewed examples, task metrics |
| Operational monitoring  | Is the service reliable and efficient in production? | Latency, errors, throughput, usage, cost, feedback               |


A reference summary is useful, but it should not always be treated as
the only valid wording. Evaluate semantic content and task constraints.

<br/>

## 6. When Exact Expected Values Are Appropriate

Exact assertions remain important. Use them when the contract genuinely
requires a fixed value or a precisely defined transformation.

Good candidates include:

-   HTTP status codes and error codes.
-   Required JSON keys, data types, enum values, and schema constraints.
-   Deterministic parsing or formatting rules.
-   Fixed labels for a classification task when the label space is
    defined.
-   Exact extraction of an identifier, date, or amount when source
    formatting and normalization rules are explicit.
-   Tool/function arguments when a specific structured call is required.
-   Safety invariants, such as never returning a secret included only in
    a protected test fixture.

For natural-language generation, exact matching can be appropriate if
the task explicitly requires a fixed string, template, or controlled
vocabulary. Otherwise, exact matching can create false failures for
valid paraphrases.

**Do not confuse "exact match is too strict for some tasks" with "exact
checks are obsolete."** A robust evaluation suite uses exact assertions
for exact contracts and semantic/task-level criteria for open-ended
content.

<br/>

## 7. Worked Example: Test a Summarization Endpoint

The following small example separates API-contract checks from a simple
task-quality check. It uses a **fixed fixture** so the test is
reproducible; it does not call a live model.

### 7.1 Example output contract

``` python
from pydantic import BaseModel, Field

class SummaryResponse(BaseModel):
    summary: str = Field(min_length=1)
```

This schema verifies that `summary` is a non-empty string. It does not
prove that the string is factually correct.

<br/>

### 7.2 Contract validation

``` python
from pydantic import ValidationError

valid_response = {"summary": "The release was postponed after testing found two critical defects."}
parsed = SummaryResponse.model_validate(valid_response)
assert parsed.summary

# A missing field violates the contract.
try:
    SummaryResponse.model_validate({"message": "No summary field"})
except ValidationError:
    pass
else:
    raise AssertionError("Expected schema validation to fail")
```

This test checks the response structure. It does not check whether the
summary accurately represents the source.

<br/>

### 7.3 A simple task-quality check

``` python
source_facts = {
    "postponed": True,
    "two_critical_defects": True,
    "new_date_announced": False,
}

def check_summary(summary: str) -> dict[str, bool]:
    text = summary.lower()
    return {
        "mentions_postponement": "postpon" in text or "delay" in text,
        "mentions_two_defects": "two" in text and ("defect" in text or "bug" in text),
        "does_not_claim_launch": "launched" not in text and "released on 12 june" not in text,
    }

fixture = (
    "The reporting feature's release was postponed after testing found "
    "two critical defects. A new date has not been announced."
)

checks = check_summary(fixture)
print(checks)
assert all(checks.values())
```

**Important limitation:** These keyword checks are illustrative
heuristics, not a robust semantic evaluator. They can miss paraphrases,
negation, subtle contradictions, and fabricated details. Production
evaluation should use reviewed test cases and stronger task-specific
checks.

<br/>

### 7.4 Example test plan

| Test category      | Example test                                | Expected outcome                                 |
| ------------------ | ------------------------------------------- | ------------------------------------------------ |
| Input contract     | Request omits required source text          | Reject with the documented client-error response |
| API behavior       | Valid request reaches the model adapter     | Correct adapter invocation                       |
| Output schema      | Response has a non-empty `summary` string   | Pass                                             |
| Task quality       | Summary preserves release status and reason | Pass only if facts are preserved                 |
| Unsupported claims | Summary invents a new date                  | Fail                                             |
| Reliability        | Provider times out                          | Bounded retry or safe error response             |
| Operations         | Measure response latency and token usage    | Record under a documented workload               |


For a live endpoint, add tests for authentication, request validation,
timeout behavior, provider failures, and logging. Keep the quality
evaluation dataset separate from the endpoint's unit tests.

<br/>

## 8. Evaluation Workflow

``` mermaid
flowchart TD
    A[Define task and users] --> B[Specify technical contract]
    B --> C[Define quality rubric]
    C --> D[Create representative test cases]
    D --> E[Run software tests]
    D --> F[Run model outputs on fixed cases]
    E --> G[Inspect contract failures]
    F --> H[Score quality and review failures]
    G --> I[Combine evidence]
    H --> I
    I --> J[Release, revise, or gather more evidence]
    J --> K[Monitor production behavior]
```

A practical workflow is:

1.  Define what the application must do and what counts as a critical
    failure.
2.  Specify deterministic API and data contracts.
3.  Define task-specific quality criteria with clear passing and failing
    examples.
4.  Build representative cases, including ambiguous and unsupported
    inputs.
5.  Run software tests and task-quality evaluations separately.
6.  Record failures and their categories rather than relying only on an
    aggregate score.
7.  Measure latency, usage, and cost under a stated workload.
8.  Set release criteria and monitor production behavior after
    deployment.

<br/>

## 9. Common Mistakes

-   **Treating valid JSON as a correct answer:** Parsing proves syntax
    and structure, not truth.
-   **Using one reference sentence as the only acceptable summary:**
    This penalizes valid paraphrases.
-   **Using only subjective impressions:** Reviewers need explicit
    criteria and examples.
-   **Using only an LLM judge:** Model judges can be biased or
    inconsistent and should be calibrated for consequential evaluation.
-   **Mixing API failures with quality failures:** This makes root-cause
    analysis harder.
-   **Ignoring repeated-run variation:** A single successful result may
    hide instability.
-   **Reporting a score without its denominator:** State how many cases
    were evaluated and how invalid or missing outputs were handled.
-   **Treating fixtures as live performance results:** Prepared outputs
    validate the evaluator or application logic, not current model
    quality.

<br/>

## 10. Practice

### Exercise A --- Classify each check

For each item, identify the primary layer: **software test**,
**task-quality evaluation**, or **operational monitoring**.

1.  The endpoint returns HTTP 200 for a valid request.
2.  A summary preserves the source's main conclusion.
3.  The service's p95 latency is 2.4 seconds under 50 concurrent
    requests.
4.  The response contains a non-empty `summary` field.
5.  A summary invents a product launch date.
6.  Provider timeouts increased from 0.5% to 4% of requests.

<br/>

### Exercise B --- Design a summarization rubric

Create three to five criteria for a summarizer used to brief a manager.
Include at least one criterion for factual accuracy, one for coverage,
and one for conciseness. Write one passing example and one failing
example for each criterion.

<br/>

### Exercise C --- Decide whether exact matching fits

For each task, decide whether exact matching is appropriate,
inappropriate, or useful only for part of the evaluation:

1.  Convert `2026-10-14` to `14 October 2026` under a fixed formatting
    contract.
2.  Summarize a two-page report in three sentences.
3.  Return one of `positive`, `neutral`, or `negative` for a sentiment
    classifier.
4.  Extract an invoice number from a document.
5.  Explain a scientific concept to a beginner.

<br/>

## 11. Exercise Answers

### Exercise A

1.  **Software test** --- verifies the HTTP contract.
2.  **Task-quality evaluation** --- checks semantic coverage.
3.  **Operational monitoring/performance test** --- measures latency
    under a specified workload.
4.  **Software test** --- validates a structural requirement; it does
    not prove usefulness.
5.  **Task-quality evaluation** --- checks for unsupported content.
6.  **Operational monitoring** --- tracks a reliability signal over
    time.

<br/>

### Exercise B --- Example rubric

-   **Factual accuracy:** All claims agree with the source; fabricated
    claims fail.
-   **Coverage:** Includes the main conclusion and decision-relevant
    facts.
-   **Conciseness:** Meets the requested length and avoids repetition.
-   **Relevance:** Prioritizes information useful to the manager.
-   **Uncertainty:** Preserves qualifications and does not turn
    tentative findings into certainty.

Passing example: "The launch is delayed because two critical defects
remain unresolved; the team has not set a new date."

Failing example: "The launch succeeded yesterday." This contradicts the
source if the source says the launch was delayed.

<br/>

### Exercise C

1.  **Exact matching is appropriate** if the output format is fixed and
    normalization is defined.
2.  **Exact matching is generally inappropriate** for the full summary;
    evaluate facts, coverage, relevance, and length.
3.  **Exact matching is useful** for the allowed label, alongside
    class-level precision/recall/F1 across a dataset.
4.  **Exact matching is useful** for the extracted identifier after
    clearly defined normalization; also measure field-level accuracy and
    missing/invalid values.
5.  **Exact matching is inappropriate** for open-ended explanation; use
    a rubric and evidence-based review.

<br/>

## 12. Checkpoint

**Question:** Why does passing schema validation not establish that a
GenAI output is useful?

**Answer:** Schema validation checks whether the output conforms to a
structural contract---for example, whether a required field exists and
contains a string. It does not establish that the content is correct,
complete, relevant, faithful to the source, appropriately uncertain, or
free of unsupported claims. A response such as
`{"summary": "The product launched successfully."}` may be valid JSON
and satisfy the schema while being completely wrong if the source says
the launch was postponed. Therefore, structural validation and
task-quality evaluation are separate, complementary checks.

<br/>

## 13. References

-   [Pydantic --- Models and
    validation](https://docs.pydantic.dev/latest/concepts/models/)
-   [pytest --- Getting
    started](https://docs.pytest.org/en/stable/getting-started.html)
-   [OpenAI --- Evaluation best
    practices](https://platform.openai.com/docs/guides/evaluation-best-practices)
-   [OpenAI Cookbook --- Evals examples](https://cookbook.openai.com/)
-   [Google Cloud --- Introduction to generative AI
    evaluation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview)

Use provider documentation to verify current API behavior and supported
evaluation features before implementing a production evaluation
pipeline.

<br/>

## 14. Revision Summary

-   Software tests check whether the application obeys its technical
    contract.
-   Task-quality evaluation checks whether the output accomplishes the
    intended task.
-   Operational monitoring checks service behavior, reliability,
    latency, and resource usage.
-   Generative outputs can vary, and multiple wordings can be equally
    valid.
-   Exact assertions remain valuable for fixed contracts; open-ended
    generation needs task-specific criteria.
-   A valid schema is necessary when required, but it is not evidence by
    itself of a correct or useful answer.
