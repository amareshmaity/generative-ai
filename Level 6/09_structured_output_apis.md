# 09. Structured Output APIs

## Learning objectives

-   Translate an application schema into supported provider request
    options.
-   Distinguish JSON syntax constraints from schema-constrained
    generation.
-   Validate returned data with Pydantic and independent business rules.
-   Handle unsupported schema features, refusals, truncation, and
    invalid output.
-   Use bounded recovery and explicit failure responses.

> **Scope:** Examples use Python, Pydantic, and the OpenAI Responses
> API. Provider features, schema subsets, request parameters, and SDK
> helpers vary. Confirm current documentation and pinned versions before
> using provider-specific options.

<br/>

## 1. Why structured output matters

Plain text is flexible for people, but application code often needs a
predictable shape. A support-ticket classifier may need a category and
evidence field rather than a paragraph.

Structured output can reduce parsing ambiguity, but it does not
guarantee that values are true, relevant, authorized, or consistent with
business rules.

A robust extraction pipeline separates these stages:

1.  Define the application schema.
2.  Configure a supported provider output mode.
3.  Generate the response.
4.  Check completion and refusal state.
5.  Parse and validate the returned data.
6.  Apply independent semantic and business-rule checks.
7.  Return a typed result or an explicit failure.

``` mermaid
flowchart TD
    A[Define application schema] --> B[Map schema to provider options]
    B --> C[Request structured output]
    C --> D{Generation completed?}
    D -->|No| E[Handle incomplete or provider failure]
    D -->|Yes| F{Refusal present?}
    F -->|Yes| G[Return refusal outcome]
    F -->|No| H[Parse and validate schema]
    H -->|Invalid| I[Bounded recovery or failure]
    H -->|Valid| J[Apply business rules]
    J -->|Pass| K[Return validated result]
    J -->|Fail| L[Reject as semantically invalid]
```

<br/>

## 2. JSON mode versus schema-constrained output

**JSON syntax constraints** aim to produce syntactically valid JSON.
Syntax validity alone does not ensure required keys exist or values have
the expected types.

For example, this is valid JSON:

``` json
{"category": 42}
```

But it may violate an application schema that requires `category` to be
a string.

**Schema-constrained generation** asks the provider to generate data
matching a supplied schema, within the subset of schema features
supported by that provider. Depending on the API, constraints may cover
fields, types, required properties, enumerated values, and object
structure.

Even if the provider enforces a supported schema, the application must
still validate the response and enforce business rules. Provider
constraints do not prove factual correctness.

| Aspect                 | JSON Syntax Mode           | Schema-Constrained Output       |
| ---------------------- | -------------------------- | ------------------------------- |
| Main goal              | Produce valid JSON syntax  | Match a supported schema        |
| Required fields        | Not necessarily guaranteed | Can be constrained if supported |
| Field types            | Not necessarily guaranteed | Can be constrained if supported |
| Business-rule validity | Not guaranteed             | Not guaranteed                  |
| Factual correctness    | Not guaranteed             | Not guaranteed                  |
| Local validation       | Required                   | Still required                  |


The precise distinction and request parameters depend on the provider.
Use the documented output mode rather than assuming all JSON features
are equivalent.

<br/>

## 3. Define the application schema first

The schema should represent what downstream code actually needs, not
merely mirror whatever output the model tends to produce.

``` python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class TicketExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: Literal[
        "account_access",
        "billing",
        "technical_issue",
        "other",
    ]
    summary: str = Field(min_length=5, max_length=300)
    evidence: str = Field(min_length=1, max_length=500)
```

Design considerations:

-   Use `Literal` or enums when only a fixed set of values is
    acceptable.
-   Use length and numeric bounds where they reflect genuine
    requirements.
-   Decide whether extra fields should be rejected or ignored.
-   Use nullable fields only when "unknown" or "not provided" is
    meaningful.
-   Do not require a field merely because it is convenient if the source
    may not contain it.
-   Keep extracted facts distinct from facts inferred by the model.

A schema expresses structural constraints. Put complex domain rules in
explicit validation code when that is clearer or when the provider does
not support the needed feature.

<br/>

## 4. Translate the schema into provider request options

Provider APIs differ in how they accept structured-output schemas. Some
accept JSON Schema directly; some provide SDK helpers based on Pydantic;
some support only a subset of JSON Schema; others may not offer an
equivalent feature for every endpoint.

### Example with the OpenAI Python SDK

The following illustrates the Pydantic-based parsing helper in SDK
versions that support it:

``` python
from openai import OpenAI

client = OpenAI()

response = client.responses.parse(
    model="YOUR_SUPPORTED_MODEL",
    input=[
        {
            "role": "system",
            "content": (
                "Extract support-ticket fields from the user's text. "
                "Do not invent missing facts. Put source evidence in evidence."
            ),
        },
        {
            "role": "user",
            "content": "I cannot sign in after resetting my password.",
        },
    ],
    text_format=TicketExtraction,
)

result = response.output_parsed
if result is None:
    raise RuntimeError("No parsed structured result was returned.")

print(result.model_dump())
```

Notes:

-   Replace the placeholder with a model supporting the chosen
    structured-output feature.
-   Check that your installed SDK version supports the shown helper and
    parameters.
-   Parsing helpers do not eliminate the need to inspect refusal and
    completion behavior.
-   Do not assume every Pydantic or JSON Schema feature is supported.
-   For unsupported features, simplify the provider-facing schema where
    safe, then enforce the full application contract locally.

Keep provider-specific configuration in an adapter rather than spreading
it through application routes:

``` python
def extract_ticket(provider_client, ticket_text: str) -> TicketExtraction:
    # Provider-specific request configuration belongs here.
    # Inspect completion/refusal state, validate the result,
    # and apply business rules before returning.
    raise NotImplementedError("Implement for the selected provider and SDK version")
```

<br/>

## 5. Validate locally with Pydantic

Even when using schema-constrained generation, validate returned content
at the application boundary.

``` python
from pydantic import ValidationError

payload = {
    "category": "account_access",
    "summary": "User cannot sign in after a password reset.",
    "evidence": "I cannot sign in after resetting my password.",
}

try:
    extraction = TicketExtraction.model_validate(payload)
except ValidationError as exc:
    print("Schema validation failed:", exc)
else:
    print(extraction.model_dump())
```

For raw JSON text:

``` python
raw_json = '''
{
  "category": "billing",
  "summary": "User requests an invoice.",
  "evidence": "Where can I download my invoice?"
}
'''

extraction = TicketExtraction.model_validate_json(raw_json)
```

Local validation protects against unexpected responses, adapter
mistakes, fixture errors, schema changes, and invalid data entering
downstream code. Do not silently coerce or discard invalid values unless
that behavior is explicitly part of the application contract.

<br/>

## 6. Schema validity is not semantic validity

A response can match the schema and still be wrong. If the source says
"I cannot sign in," the model could return the allowed category
`billing`. The schema accepts that category because it is permitted,
even though the classification is incorrect.

Independent checks can include:

-   Cross-field consistency.
-   Numeric limits and domain invariants.
-   Evidence presence and provenance.
-   Source-grounding checks.
-   Authorization and policy checks.
-   Reconciliation with trusted database records.
-   Human review for high-impact decisions.

``` python
def validate_ticket_semantics(
    result: TicketExtraction,
    source_text: str,
) -> None:
    if not result.evidence.strip():
        raise ValueError("Evidence must not be empty.")

    # Illustrative rule only; production rules should be task-specific.
    if result.category == "account_access":
        source = source_text.casefold()
        access_terms = ("sign in", "login", "log in", "password", "account")
        if not any(term in source for term in access_terms):
            raise ValueError(
                "Account-access category lacks expected source evidence."
            )
```

This rule is intentionally simple. Keyword checks can produce false
positives and false negatives; they are not proof that the
classification is correct. More demanding applications may need
domain-specific validators, trusted retrieval, test datasets, or human
review.

<br/>

## 7. Handle refusals, truncation, and invalid output

### Refusals

A refusal is not the same as malformed JSON. Inspect the provider's
documented refusal representation before parsing structured output.
Handle refusal as its own outcome, not as a transient error to retry
repeatedly.

<br/>

### Incomplete or truncated output

Generation may stop early, leaving a payload cut off or missing required
fields. Check completion status and incomplete details before parsing.
Never treat partial structured output as valid.

<br/>

### Unsupported schema features

Provider schema support may be a subset of JSON Schema. If a feature is
unsupported:

1.  Confirm the documented limitation.
2.  Simplify the provider-facing schema where safe.
3.  Keep stricter application validation locally.
4.  Test that the local contract still holds.
5.  Do not remove constraints essential for security or business
    correctness.

<br/>

### Invalid output

Invalid output includes malformed JSON, missing required fields,
unexpected values, and semantic violations. Keep these categories
distinct so monitoring and retry logic can respond appropriately.

<br/>

## 8. Bounded recovery and explicit failures

Repeated retries can increase cost and latency without improving
correctness. Use a policy such as:

-   **Transient transport/service error:** retry according to documented
    guidance and a bounded retry budget.
-   **Incomplete response:** retry or continue only through a documented
    mechanism, when safe.
-   **Schema validation failure:** optionally make one controlled repair
    attempt if appropriate; validate the repaired output from scratch.
-   **Semantic/business-rule failure:** reject or escalate; do not
    assume another generation will make the answer true.
-   **Refusal:** return the refusal outcome or apply documented policy.
-   **Unsupported schema configuration:** fix the request/schema instead
    of retrying the same configuration.

``` python
from pydantic import ValidationError

def validate_extraction(payload: object) -> TicketExtraction:
    try:
        return TicketExtraction.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Extraction failed schema validation.") from exc
```

Convert failures into explicit application outcomes such as validation
error, controlled retry, or review-required status. Avoid returning a
fabricated default object to make the pipeline appear successful.

<br/>

## 9. Practice: extraction with four fixture types

This offline exercise needs no provider API key. It tests four cases:
valid data, malformed JSON, a missing required field, and structurally
valid but semantically invalid data.

``` python
from pydantic import ValidationError

fixtures = {
    "valid": '''
    {
      "category": "account_access",
      "summary": "User cannot sign in after a password reset.",
      "evidence": "I cannot sign in after resetting my password."
    }
    ''',
    "malformed_json": '''
    {
      "category": "billing",
      "summary": "User needs an invoice",
      "evidence": "Where can I download my invoice?"
    ''',
    "missing_field": '''
    {
      "category": "billing",
      "summary": "User needs an invoice."
    }
    ''',
    "semantically_invalid": '''
    {
      "category": "billing",
      "summary": "User cannot sign in after resetting a password.",
      "evidence": "I cannot sign in after resetting my password."
    }
    ''',
}

source_text = "I cannot sign in after resetting my password."

def evaluate_fixture(name: str, raw: str) -> dict:
    try:
        result = TicketExtraction.model_validate_json(raw)
    except ValidationError as exc:
        return {
            "fixture": name,
            "outcome": "schema_or_json_invalid",
            "details": str(exc),
        }

    try:
        validate_ticket_semantics(result, source_text)
    except ValueError as exc:
        return {
            "fixture": name,
            "outcome": "semantic_validation_failed",
            "details": str(exc),
        }

    return {
        "fixture": name,
        "outcome": "valid",
        "data": result.model_dump(),
    }

for name, raw in fixtures.items():
    print(evaluate_fixture(name, raw))
```

Expected interpretation:

| Fixture                | Expected Result              | Why                                                                                             |
| ---------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------- |
| `valid`                | `valid`                      | JSON parses, fields satisfy the schema, and the illustrative semantic check passes.             |
| `malformed_json`       | `schema_or_json_invalid`     | The JSON object is not closed correctly.                                                        |
| `missing_field`        | `schema_or_json_invalid`     | The required `evidence` field is absent.                                                        |
| `semantically_invalid` | `semantic_validation_failed` | The structure is valid, but the category conflicts with the source under the illustrative rule. |


The semantic validator is intentionally simplistic. It demonstrates that
structural and semantic validation are separate; it is not a
production-grade classifier.

<br/>

### Practice extensions

-   Add an invalid category value.
-   Add a summary that exceeds the maximum length.
-   Add source text that does not support the claimed evidence.
-   Simulate a refusal and incomplete provider response before parsing.
-   Add one bounded repair attempt and validate the final output again.
-   Track separate counts for provider, JSON, schema, and semantic
    failures.

<br/>

## 10. Checkpoint: why schema compliance does not establish factual correctness

Schema compliance means that returned data satisfies structural
constraints---for example, required keys exist, values have expected
types, and fields use allowed values. It does not establish that those
values accurately represent the source or real world.

A model can produce valid JSON containing a wrong category, invented
evidence, an unsupported date, or a false claim. Structured output
should therefore be treated as **well-formed data, not automatically
verified truth**.

Combine schema validation with source-grounding checks, independent
business rules, trusted data lookups, or human review where appropriate.
Consequential actions should depend on the validated application
contract, not JSON validity alone.

<br/>

## 11. Key takeaways

-   Define the application schema before choosing provider options.
-   JSON syntax validity and schema compliance are different guarantees.
-   Provider schema support may be limited to a documented subset.
-   Validate every result locally, even when using constrained
    generation.
-   Apply independent business rules and evidence checks after schema
    validation.
-   Treat refusals, incomplete output, malformed data, and semantic
    failures as distinct outcomes.
-   Keep retries bounded and never fabricate a default result to hide
    failure.

<br/>

## References

-   OpenAI API documentation --- Structured Outputs:
    https://platform.openai.com/docs/guides/structured-outputs
-   OpenAI API reference --- Responses:
    https://platform.openai.com/docs/api-reference/responses
-   OpenAI Python SDK: https://github.com/openai/openai-python
-   Pydantic documentation --- Models:
    https://docs.pydantic.dev/latest/concepts/models/
-   Pydantic documentation --- JSON parsing:
    https://docs.pydantic.dev/latest/concepts/json/

Verify current provider schema support, SDK helper signatures, and model
compatibility before deploying these examples.
