# 07. Evaluating Structured Outputs

## Learning Objectives

By the end of this chapter, you should be able to:

-   Separate parse success, schema validity, field accuracy, and
    business-rule compliance.
-   Evaluate missing values, extra fields, enums, nested records, and
    source evidence.
-   Track refusals, truncation, invalid responses, and unsupported
    requests explicitly.
-   Report field-level and complete-record performance where useful.
-   Explain how invalid outputs affect evaluation denominators and
    reported results.

<br/>

## 1. Why Structured Output Needs Its Own Evaluation

Structured outputs include JSON objects, API payloads, tool arguments,
extracted records, classification objects, and responses validated
against a schema. They are often consumed by downstream software, so a
response can fail even when its prose seems reasonable.

Structured-output evaluation must distinguish several layers:

1.  **Parse success:** Can the response be decoded into the expected
    data format?
2.  **Schema validity:** Does the parsed value satisfy the structural
    schema and data types?
3.  **Field accuracy:** Are the values correct for the task and source?
4.  **Business-rule compliance:** Do values satisfy domain constraints
    and cross-field rules?
5.  **Evidence support:** Are extracted or asserted values supported by
    permitted evidence?
6.  **Task completion:** Did the response provide the requested record,
    or did it refuse, truncate, or fail?

A response that passes an earlier layer does not automatically pass
later layers. Valid JSON can contain incorrect values; a schema-valid
invoice can contain a total that does not equal its line items.

<br/>

## 2. The Evaluation Layers

| Layer                    | Question                                                      | Example failure                          |
| ------------------------ | ------------------------------------------------------------- | ---------------------------------------- |
| Parse success            | Is the output valid JSON or the required serialization?       | Missing closing brace                    |
| Schema validity          | Does it match required keys, types, nesting, and constraints? | `amount` is a string instead of a number |
| Field accuracy           | Does each value match the reference or source?                | Correct type, wrong invoice number       |
| Business-rule compliance | Are domain and cross-field rules satisfied?                   | Total does not equal subtotal plus tax   |
| Evidence support         | Can source evidence justify the value?                        | Invented customer address                |
| Task outcome             | Did the model complete the request appropriately?             | Truncated output or unjustified refusal  |


A useful evaluation pipeline is:

``` mermaid
flowchart TD
    A[Model response] --> B{Response outcome}
    B -->|Refusal| R[Record refusal status]
    B -->|Empty or truncated| T[Record incomplete status]
    B -->|Candidate payload| C{Parses successfully?}
    C -->|No| P[Parse failure]
    C -->|Yes| D{Schema valid?}
    D -->|No| S[Schema failure]
    D -->|Yes| E[Check field values]
    E --> F[Check business rules]
    F --> G[Check source evidence]
    G --> H[Report each dimension and overall outcome]
    P --> H
    S --> H
    R --> H
    T --> H
```

This flow is a diagnostic sequence, not a reason to discard failed
responses. Record each response's outcome in the evaluation report.

<br/>

## 3. Parse Success

Parse success measures whether the output can be decoded using the
required parser.

For JSON, these are different:

``` json
{"invoice_id": "INV-104", "total": 125.50}
```

``` text
Here is the JSON you requested:
{"invoice_id": "INV-104", "total": 125.50}
```

The second response may contain a valid JSON fragment but fail a strict
whole-response JSON parser because it includes extra prose. Whether that
is a failure depends on the declared output contract. If the contract
requires a JSON object and nothing else, the extra prose violates it.

Record parse outcomes with a defined status, for example:

-   `parse_success`
-   `parse_failure`
-   `empty_response`
-   `truncated_response`
-   `refusal`
-   `unsupported_request`

Do not silently repair malformed JSON for the primary metric unless
repair is explicitly part of the production pipeline. If repair is part
of the application, report both raw parse success and post-repair
success.

<br/>

## 4. Schema Validity

Schema validity checks structure and declared constraints, not whether
the values are factually right.

A schema may specify:

-   Required and optional fields.
-   Primitive types: string, number, integer, boolean, array, object, or
    null.
-   Enumerated values.
-   Minimum/maximum values and string lengths.
-   Nested objects and arrays.
-   Whether additional properties are allowed.

Example schema-like contract:

``` json
{
  "invoice_id": "string",
  "currency": "one of USD, EUR, INR",
  "total": "number greater than or equal to 0",
  "line_items": "array of objects with description and amount"
}
```

A payload can be schema-valid even if it names the wrong invoice or uses
a plausible but incorrect total. Conversely, a correct value in the
wrong type may be invalid under the contract.

<br/>

### Missing and extra fields

Define policy before evaluation:

-   **Missing required field:** schema failure and usually a task
    failure.
-   **Missing optional field:** acceptable if omission is permitted;
    otherwise it may reduce completeness.
-   **Explicit null:** valid only if the schema permits null for that
    field.
-   **Empty string or zero:** not automatically equivalent to missing or
    null.
-   **Extra field:** invalid if additional properties are forbidden;
    otherwise may be accepted but still checked for unintended content.

Avoid silently treating missing values as correct. In extraction tasks,
missing values should usually count as failures for required fields,
while legitimate "not present in source" cases need an explicit
representation such as `null`, `unknown`, or a documented abstention
value.

<br/>

### Enums and nested records

For enumerations, compare against the allowed set and separately assess
whether the selected enum is correct.

Example: `status: "approved"` may be a valid enum but wrong if the
source says "pending."

For nested records, evaluate both the structure and the content. A
nested `shipping_address` can have valid keys and types while containing
the wrong postal code. Arrays may also require order-sensitive or
order-insensitive comparison, depending on task semantics.

<br/>

## 5. Field Accuracy

Field accuracy measures whether extracted or generated values match a
reference under declared comparison rules.

For (N) expected fields across evaluated records:

$$
\text{Field Accuracy} = \frac{\text{Number of correct expected fields}}{\text{Number of expected fields evaluated}}
$$

The denominator and treatment of missing/invalid values must be defined.
For required fields, a missing or unparseable value should generally
count as incorrect rather than disappear from the denominator.

<br/>

### Field-level comparison rules

Rules may include:

-   Exact string comparison for IDs and codes.
-   Normalization of whitespace or case only when semantics are
    unchanged.
-   Numeric tolerance for measured values, if the task permits it.
-   Date normalization for equivalent representations of the same date.
-   Set comparison for unordered collections.
-   Order-sensitive comparison for sequences where order matters.
-   Semantic or evidence-based review for free-text fields.

Do not normalize away meaningful distinctions. For example, invoice IDs
`INV-010` and `INV-10` may not be equivalent even though they look
numerically similar.

<br/>

### Field accuracy is not record accuracy

Consider three required fields: invoice ID, date, and total. If two
fields are correct and one is wrong, the field accuracy is (2/3
`\approx 66.7`{=tex}%). The record may still be considered failed if all
three fields are required for downstream processing.

<br/>

## 6. Complete-Record Performance

Complete-record accuracy measures the proportion of records for which
every required field meets its acceptance criteria.

$$
\text{Complete-Record Accuracy} = \frac{\text{Records with all required fields correct}}{\text{All eligible evaluation records}}
$$

Define "eligible" carefully. For a fixed benchmark, the denominator
should normally include every assigned case, including refusals and
invalid outputs, unless the task definition explicitly excludes a class
before evaluation. Exclusions must be documented and reported.

Example with four records:

| Record | Invoice ID   | Date    | Total   | All fields correct? |
| ------ | ------------ | ------- | ------- | ------------------- |
| A      | Correct      | Correct | Correct | Yes                 |
| B      | Correct      | Correct | Wrong   | No                  |
| C      | Correct      | Missing | Correct | No                  |
| D      | Invalid JSON | ---     | ---     | No                  |


Field accuracy and complete-record accuracy answer different questions.
Field-level scores reveal where errors occur; complete-record
performance estimates how often a downstream consumer receives a fully
usable record.

<br/>

## 7. Business-Rule Compliance

Business rules are domain-specific constraints that may span multiple
fields.

Examples:

-   `quantity >= 0`
-   `line_total = quantity * unit_price` within a defined rounding
    tolerance
-   `invoice_total = subtotal + tax - discount`
-   `start_date <= end_date`
-   An order cannot be marked `shipped` if required shipping details are
    absent.
-   A classification value must be consistent with an explicitly stated
    eligibility rule.

Separate two questions:

1.  **Rule validity:** Does the payload satisfy the rule?
2.  **Source/task correctness:** Does the rule-consistent payload
    represent the actual source correctly?

A fabricated amount can satisfy arithmetic rules. Business-rule
compliance is necessary in many applications but does not prove factual
accuracy.

<br/>

## 8. Evidence Support for Extracted Fields

For extraction and document Q&A, validate values against source
evidence.

Example source text:

> Invoice INV-104 is dated 12 October 2026. Subtotal: ₹1,000. Tax: ₹180.
> Total: ₹1,180.

Candidate output:

``` json
{
  "invoice_id": "INV-104",
  "date": "2026-10-12",
  "subtotal": 1000,
  "tax": 180,
  "total": 1180,
  "payment_status": "paid"
}
```

The invoice ID, date, subtotal, tax, and total are supported by the
source, assuming the date conversion rule is agreed. The
`payment_status` value is unsupported because the source does not state
that payment occurred. It may be a valid string and an allowed enum, but
it lacks evidence.

A useful field-level ledger contains:

-   Field name and predicted value.
-   Reference value or expected status.
-   Evidence passage or source location.
-   Schema result.
-   Accuracy result.
-   Business-rule result.
-   Support status (`supported`, `unsupported`, `contradicted`, or
    `not_assessed`).

<br/>

## 9. Refusals, Truncation, Invalid Responses, and Unsupported Requests

These outcomes must be represented explicitly because they affect
practical system performance.

| Outcome             | Meaning                                                  | Recommended reporting                                                       |
| ------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------- |
| Refusal             | Model declines to provide the requested output           | Count and classify appropriate vs inappropriate refusals                    |
| Truncation          | Output ends before the required payload is complete      | Count as incomplete; include in task-success denominator                    |
| Empty response      | No usable content returned                               | Count as a failed response unless the contract defines a valid empty result |
| Parse failure       | Raw response cannot be parsed as required                | Parse-failure rate; record any repair outcome separately                    |
| Schema failure      | Parsed output violates the declared contract             | Schema-validity rate and failure categories                                 |
| Unsupported request | Request is outside permitted capability or evidence      | Measure whether the model appropriately abstains or escalates               |
| Valid abstention    | Contract explicitly allows `unknown`, `null`, or refusal | Evaluate whether abstention was justified                                   |


A refusal is not always a failure. If the request is unsafe, outside
scope, or impossible to answer from the supplied evidence, a correct
refusal or abstention may be the expected behavior. Conversely, an
unjustified refusal on a supported, answerable case is a task failure.

For safety- or policy-sensitive tasks, evaluate refusal appropriateness
separately from formatting success.

<br/>

## 10. Worked Example: Valid JSON with Wrong Values

### Task and reference

Reference record:

``` json
{
  "invoice_id": "INV-104",
  "currency": "INR",
  "subtotal": 1000,
  "tax": 180,
  "total": 1180,
  "payment_status": "unknown"
}
```

Candidate response:

``` json
{
  "invoice_id": "INV-140",
  "currency": "INR",
  "subtotal": 1000,
  "tax": 180,
  "total": 1180,
  "payment_status": "paid"
}
```

Assume the JSON parses, the schema permits these values, and all six
fields are required.

| Field            | Candidate | Reference | Schema valid?          | Correct? |
| ---------------- | --------- | --------- | ---------------------- | -------- |
| `invoice_id`     | `INV-140` | `INV-104` | Yes                    | No       |
| `currency`       | `INR`     | `INR`     | Yes                    | Yes      |
| `subtotal`       | `1000`    | `1000`    | Yes                    | Yes      |
| `tax`            | `180`     | `180`     | Yes                    | Yes      |
| `total`          | `1180`    | `1180`    | Yes                    | Yes      |
| `payment_status` | `paid`    | `unknown` | Yes, if enum allows it | No       |


Results:

-   Parse success: **1**
-   Schema validity: **1**
-   Field accuracy: (4/6 `\approx 66.7`{=tex}%)
-   Complete-record accuracy: **0/1 = 0%**
-   Business-rule compliance for `total = subtotal + tax`: **Pass**
-   Evidence support: the incorrect invoice ID and unsupported payment
    status fail their checks.

This example demonstrates why parse success and schema validity must not
be reported as if they were task correctness.

<br/>

## 11. Worked Example: Invalid Outputs Must Stay in the Denominator

Suppose a benchmark contains 10 assigned cases:

-   6 responses are schema-valid and fully correct.
-   2 responses are valid JSON but contain wrong required values.
-   1 response is malformed JSON.
-   1 response is an unjustified refusal.

If the task requires a usable, correct record for every case:

-   Parse success: (9/10 = 90%) if the refusal is non-JSON and counted
    as not parseable.
-   Schema-valid payload rate: (8/10 = 80%), assuming the refusal is not
    schema-valid and only the six correct plus two wrong-value responses
    pass the schema.
-   Complete task success: (6/10 = 60%).

Do **not** report correctness as (6/8 = 75%) without prominently
explaining that the malformed output and refusal were excluded. That
conditional rate can be useful for diagnosis, but it does not describe
end-to-end performance.

Report both: - **End-to-end success:** successes divided by all assigned
cases. - **Conditional metric:** performance among outputs that reached
a specified stage, clearly labeled with its denominator.

If a refusal or abstention is valid for a particular case, score it
against the task's expected behavior rather than automatically counting
it as a failure.

<br/>

## 12. A Reproducible Evaluation Procedure

1.  Freeze the test cases, expected records, schema, and comparison
    rules.
2.  Record the raw model response and run metadata.
3.  Classify the response outcome: payload, refusal, empty, truncated,
    or other.
4.  Parse the raw response without silent repair.
5.  Validate schema constraints.
6.  Compare each expected field with its reference under documented
    rules.
7.  Run business-rule checks.
8.  Link each factual field to evidence where required.
9.  Compute field-level, complete-record, and operational rates.
10. Report all denominators, exclusions, and stage-conditional metrics.
11. Review failures and preserve reproducible examples.

<br/>

### Example evaluation manifest

``` json
{
  "dataset_version": "invoice-eval-v1",
  "schema_version": "invoice-schema-v2",
  "comparison_policy_version": "field-rules-v1",
  "run_id": "candidate-2026-10-14-01",
  "include_all_assigned_cases_in_end_to_end_denominator": true,
  "repair_malformed_json_before_primary_parse_metric": false
}
```

The values are illustrative. In a real run, use identifiers tied to
actual artifacts and record the model, prompt, decoding configuration,
and application version.

<br/>

## 13. Practice: Score Valid JSON with Wrong Values

Use this contract:

-   Required fields: `order_id` (string), `quantity` (integer greater
    than zero), `status` (`pending`, `shipped`, or `cancelled`).
-   All three fields must match the reference.
-   Extra properties are forbidden.
-   Complete-record success requires every field to be correct.

<br/>

### Case A

Reference:

``` json
{"order_id": "ORD-10", "quantity": 2, "status": "pending"}
```

Candidate:

``` json
{"order_id": "ORD-10", "quantity": 2, "status": "pending"}
```

<br/>

### Case B

Reference:

``` json
{"order_id": "ORD-11", "quantity": 3, "status": "shipped"}
```

Candidate:

``` json
{"order_id": "ORD-11", "quantity": 3, "status": "pending"}
```

<br/>

### Case C

Reference:

``` json
{"order_id": "ORD-12", "quantity": 1, "status": "cancelled"}
```

Candidate:

``` json
{"order_id": "ORD-12", "quantity": "1", "status": "cancelled"}
```

<br/>

### Case D

Reference:

``` json
{"order_id": "ORD-13", "quantity": 4, "status": "pending"}
```

Candidate:

``` json
{"order_id": "ORD-13", "quantity": 4, "status": "pending", "customer_note": "priority"}
```

Questions:

1.  Which cases parse successfully?
2.  Which cases satisfy the schema?
3.  Which cases have all fields correct?
4.  If all four cases are assigned, what is the complete-record success
    rate?
5.  Why should Case C not be counted as correct simply because `"1"`
    represents the same apparent number as `1`?

<br/>

## 14. Practice Answers

-   **Case A:** Parses; schema-valid; all three fields correct;
    complete-record success.
-   **Case B:** Parses; schema-valid; `status` is wrong; two of three
    fields correct; record fails.
-   **Case C:** Parses; schema-invalid because `quantity` is a string
    rather than an integer; the type mismatch must not be normalized
    away unless the declared contract explicitly permits coercion. Under
    the stated contract, record fails.
-   **Case D:** Parses; schema-invalid because extra properties are
    forbidden; required values match, but the record fails the contract.

All four parse, but only Case A passes the schema and complete-record
criteria. Complete-record success is (1/4 = 25%). The other cases remain
failures in the end-to-end denominator.

<br/>

## 15. Checkpoint

**Prompt:** Explain how invalid outputs contribute to the reported
result rather than silently excluding them.

**Model answer:**

Invalid outputs should be recorded as explicit outcomes and included in
end-to-end denominators when every assigned case is expected to produce
a usable response. Parse failures, schema failures, truncation, and
unjustified refusals generally count as task failures under that
contract. A conditional metric among parseable or schema-valid responses
can still be useful for diagnosis, but its denominator and exclusions
must be reported. Appropriate refusals or abstentions should be scored
against the expected behavior for that case. This prevents a system from
appearing accurate merely because its hardest failures were discarded.

<br/>

## 16. Further Reading

-   [JSON Schema](https://json-schema.org/) --- standard for defining
    and validating JSON structure and constraints.
-   [Pydantic documentation](https://docs.pydantic.dev/) --- Python data
    validation and schema-driven models.
-   [JSON Lines](https://jsonlines.org/) --- practical format for
    storing one JSON record per line.
-   [OpenAI Structured Outputs
    guide](https://platform.openai.com/docs/guides/structured-outputs)
    --- schema-constrained model output concepts.
-   [LangSmith evaluation
    concepts](https://docs.smith.langchain.com/evaluation) ---
    evaluation workflows for LLM applications.



<br/>

## Chapter Summary

Structured-output evaluation is layered: parse success, schema validity,
field accuracy, business-rule compliance, evidence support, and
end-to-end task success are distinct measures. Valid JSON can still
contain wrong values. Report field-level and complete-record performance
separately, track refusals and malformed or incomplete responses
explicitly, and document all denominators and exclusions so invalid
outputs cannot silently disappear from the results.
