# 05. Exact-Match and Task-Specific Metrics

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- Decide when exact match is appropriate and when it is too strict.
- Define normalization rules without erasing meaningful errors.
- Select accuracy, precision, recall, F1, extraction field accuracy,
  or text-overlap metrics based on the task.
- Define the evaluation unit, aggregation method, denominator, and
  treatment of invalid or missing outputs.
- Explain what a metric measures---and what it does not measure.

<br/>

## 2. Why Metric Selection Matters

A metric converts evaluation outcomes into a summary number. That number
is useful only if it measures behavior relevant to the task.

A metric can be mathematically correct and still be misleading when
applied to the wrong problem. For example:

- Exact string match is suitable for a fixed identifier but often too
  strict for an open-ended summary.
- Accuracy can look high when a classifier predicts the majority class
  while missing most rare positive cases.
- Word overlap can reward a response that repeats reference wording
  while missing the intended meaning.
- A valid extraction format does not guarantee that the extracted
  value is correct.

**Principle:** Choose the metric from the task's acceptance criteria,
not from convenience or familiarity.

Before calculating a score, define:

1.  The evaluation unit: request, response, label, field, claim, or
    token sequence.
2.  The reference: fixed target, class label, expected fields, or
    reference text.
3.  The matching rule: exact, normalized, threshold-based, or graded.
4.  The denominator and aggregation method.
5.  How invalid, missing, refused, or truncated outputs are counted.
6.  What the metric cannot tell you about quality.

<br/>

## 3. Exact Match

**Exact match** counts an output as correct only when it matches the
expected target under a defined comparison rule.

$$
\text{Exact Match Rate} = \frac{\text{Number of exact matches}}{\text{Number of evaluated cases}}
$$

It is useful when the acceptable output is genuinely fixed or can be
normalized unambiguously.

<br/>

### 3.1 Suitable uses

- Extracting a known invoice identifier.
- Converting a date to a required canonical format.
- Returning one of a fixed set of labels.
- Producing a required machine-readable enum value.
- Verifying a deterministic transformation with a precisely defined
  contract.

<br/>

### 3.2 Unsuitable or incomplete uses

Exact match is usually too strict for free-form explanations, summaries,
and conversational responses where different wording can express the
same meaning.

For example, the reference summary is:

> The launch was delayed because testing found two critical defects.

Candidate A:

> Testing found two critical defects, so the launch was postponed.

Candidate B:

> The launch proceeded as planned after minor testing issues.

A strict string comparison marks both candidates as non-matches. Yet
Candidate A preserves the meaning, while Candidate B contradicts it.
Exact match alone cannot distinguish them.

For open-ended tasks, use task-specific criteria such as factual
correctness, required-fact coverage, faithfulness, relevance, and human
review. Exact match may still be useful for a subset of fixed fields or
constraints.

<br/>

## 4. Normalization: Helpful but Dangerous

Normalization applies defined transformations before comparison. It can
prevent irrelevant formatting differences from being counted as errors,
but overly broad normalization can hide real defects.

### 4.1 Common normalization choices

Depending on the task, normalization may include:

- Trimming leading and trailing whitespace.
- Standardizing line endings.
- Converting case when case is explicitly irrelevant.
- Parsing dates and comparing canonical date values.
- Removing permitted punctuation differences.
- Normalizing Unicode representations where appropriate.
- Parsing structured values and comparing specified fields rather than
  raw serialized strings.

<br/>

### 4.2 Do not erase meaningful differences

Normalization must preserve distinctions that matter to the task.

Examples:

- `INV-0017` and `INV-017` may be different identifiers.
- `0.5 mg` and `5 mg` are not equivalent.
- `2026-10-14` and `2026-14-10` must not be treated as equivalent if
  one is invalid.
- Case may matter in passwords, API tokens, product codes, and some
  identifiers.
- Removing negation words can turn "not approved" into "approved."
- Ignoring decimal separators can alter monetary values.

Write the normalization policy before scoring, test it on edge cases,
and version it alongside the evaluation code.

<br/>

### 4.3 Example: canonical date comparison

```python
from datetime import date

def canonical_date(value: str) -> str:
    # This function accepts only ISO YYYY-MM-DD dates.
    return date.fromisoformat(value).isoformat()

reference = canonical_date("2026-10-14")
candidate = canonical_date("2026-10-14")

assert candidate == reference
```

This is appropriate only when the contract specifies ISO dates. If
natural-language dates are allowed, a parser may be needed---but
ambiguous formats should be rejected or clarified rather than guessed.

<br/>

## 5. Classification Metrics

For classification, the metric should reflect the consequences of false
positives and false negatives.

Consider a binary classifier:

- **True positive (TP):** Correctly predicts positive.
- **True negative (TN):** Correctly predicts negative.
- **False positive (FP):** Predicts positive when the true label is
  negative.
- **False negative (FN):** Predicts negative when the true label is
  positive.

<br/>

### 5.1 Accuracy

$$
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
$$

Accuracy measures the fraction of all cases classified correctly. It is
useful when classes and error costs make overall correctness meaningful,
but it can be misleading with class imbalance.

<br/>

### 5.2 Precision

$$
\text{Precision} = \frac{TP}{TP + FP}
$$

Precision measures the fraction of predicted positives that are truly
positive. It matters when false alarms are costly.

<br/>

### 5.3 Recall

$$
\text{Recall} = \frac{TP}{TP + FN}
$$

Recall measures the fraction of actual positives that are found. It
matters when missing positive cases is costly.

<br/>

### 5.4 F1 score

$$
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$

F1 is the harmonic mean of precision and recall. It balances the two but
does not include true negatives and does not encode every application's
error costs.

<br/>

### 5.5 Worked classification example

Suppose a support-ticket classifier has:

- TP = 36
- TN = 54
- FP = 6
- FN = 4

Then:

- Accuracy = ((36 + 54) / 100 = 90%)
- Precision = (36 / (36 + 6) `\approx 85.7`{=tex}%)
- Recall = (36 / (36 + 4 = 40) = 90%)
- F1 (`\approx 87.8`{=tex}%)

The confusion matrix gives more diagnostic information than accuracy
alone. For multiclass tasks, define whether metrics are macro-, micro-,
or support-weighted averages; these aggregations answer different
questions.

<br/>

## 6. Extraction Field Accuracy

Information extraction often produces several fields in one
response---for example, invoice number, invoice date, currency, and
total amount.

A structured output may be syntactically valid but contain incorrect
values. Score fields against their references using field-specific
rules.

$$
\text{Field Accuracy} = \frac{\text{Correct evaluated fields}}{\text{Total evaluated fields}}
$$

For a record with four fields, suppose the invoice number, date, and
currency are correct, but the amount is wrong. Field accuracy is (3/4 =
75%).

Also consider:

- **Exact record match:** All required fields in a record are correct.
- **Field-level accuracy:** Fraction of fields correct across the
  dataset.
- **Missing-field rate:** Fraction of required fields omitted.
- **Invalid-field rate:** Fraction of fields that fail parsing or
  schema constraints.
- **Critical-field accuracy:** Accuracy for fields where errors have
  especially high consequences.

Do not let correct easy fields hide a critical error. Report per-field
performance when fields have different risk levels.

<br/>

### 6.1 Missing and extra fields

Decide in advance how to score missing fields, extra fields, nulls, and
invalid values. A missing required field should not silently disappear
from the denominator. Extra fields may be acceptable, ignored, or a
contract violation depending on the schema.

<br/>

## 7. Overlap-Based Text Metrics

Text-overlap metrics compare generated text with one or more reference
texts. They can be useful for constrained generation tasks, but lexical
overlap is not the same as semantic correctness.

### 7.1 BLEU

BLEU uses modified n-gram precision and a brevity penalty. It was
designed primarily for machine translation evaluation. Higher scores
indicate more n-gram overlap with reference text under the metric's
configuration.

Limitations:

- Valid paraphrases may receive low scores.
- A response can overlap with a reference while still containing a
  factual error.
- Scores depend on tokenization, reference count, and configuration.
- A BLEU score is not a direct percentage of correctness.

<br/>

### 7.2 ROUGE

ROUGE is a family of overlap metrics commonly used in summarization
evaluation. ROUGE-N measures n-gram overlap; ROUGE-L uses a
longest-common-subsequence concept.

Limitations:

- It can penalize valid summaries that use different wording.
- It may reward copied phrases without confirming factual fidelity.
- It does not reliably detect unsupported claims or contradictions.
- Results depend on the selected ROUGE variant and implementation.

<br/>

### 7.3 When to use overlap metrics

Use BLEU or ROUGE as one signal when reference overlap is meaningful,
such as comparing constrained translation or summary outputs. Pair them
with task-specific checks, human review, and evidence-based correctness
measures when meaning matters.

Do not use an overlap score as the sole acceptance criterion for
open-ended GenAI answers.

<br/>

## 8. Choosing a Metric by Task

| Task                        | Suitable primary metric(s)                            | Important additional checks                                 |
| --------------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
| Fixed identifier extraction | Exact match after safe normalization                  | Missing/invalid rate; critical-field accuracy               |
| Fixed-label classification  | Accuracy, precision, recall, F1                       | Confusion matrix; class imbalance; per-class metrics        |
| Multi-field extraction      | Field accuracy; exact record match                    | Schema validity; critical fields; missing/extra fields      |
| Summarization               | Rubric-based correctness and coverage; possibly ROUGE | Faithfulness, unsupported claims, relevance, human review   |
| Machine translation         | BLEU or other task-appropriate metrics                | Human review, meaning preservation, domain-specific errors  |
| Open-ended Q\&A             | Evidence-backed correctness, rubric, human review     | Answerability, citation support, uncertainty and abstention |
| Structured JSON generation  | Parse/schema validity and field-level correctness     | Semantic/business-rule validation; invalid output rate      |

Metric selection should follow the task contract. These are starting
points, not universal prescriptions.

<br/>

## 9. Aggregation, Denominators, and Invalid Outputs

A score is not interpretable unless its denominator and aggregation rule
are clear.

### 9.1 Define the denominator

Possible denominators include:

- All submitted test cases.
- All cases with a valid reference.
- All required fields.
- All predicted positive cases.
- All actual positive cases.
- All outputs successfully parsed.

These choices are not interchangeable. For example, calculating
extraction accuracy only on successfully parsed outputs can hide a high
rate of invalid responses.

<br/>

### 9.2 Recommended reporting

Report at least:

- Number of cases attempted.
- Number of valid, invalid, missing, refused, and truncated outputs.
- Number included in each metric's denominator.
- Metric definition and normalization policy.
- Aggregation method.
- Results by important case categories or risk groups.

For application-level quality, it is often useful to report both
conditional quality among valid outputs and end-to-end success across
all attempted cases. If a refusal is correct for an unsupported request,
it should be evaluated according to the expected behavior rather than
automatically treated as failure.

<br/>

### 9.3 Micro, macro, and weighted averages

For multiclass classification:

- **Micro average:** Aggregate TP, FP, and FN across classes before
  calculating the metric. Frequent classes have greater influence.
- **Macro average:** Calculate the metric per class and take the
  unweighted mean. Each class has equal influence.
- **Weighted average:** Average class-level metrics weighted by class
  support.

State which average is used. Two reports can show different F1 values
because they use different aggregation methods even on the same
predictions.

<br/>

## 10. Practice: A Suitable Metric vs. a Misleading Metric

### Example A --- Invoice number extraction

Reference invoice numbers:

`INV-101`, `INV-102`, `INV-103`, `INV-104`

Model outputs:

`INV-101`, `INV-120`, `INV-103`, `INV-104`

- Exact match accuracy: (3/4 = 75%).
- A loose substring or character-overlap metric could give partial
  credit to `INV-120`, even though it is the wrong identifier.

**Interpretation:** Exact match is appropriate because an identifier
must match the expected value. A forgiving text-overlap metric would be
misleading.

<br/>

### Example B --- Summarization

Reference:

> The launch was delayed after testing found two critical defects.

Candidate A:

> Testing found two critical defects, so the launch was postponed.

Candidate B:

> The launch happened on schedule after minor issues were resolved.

- Strict exact match gives both candidates 0.
- A task-specific rubric identifies Candidate A as semantically
  faithful and Candidate B as factually contradictory.

**Interpretation:** Exact match is misleading as the only metric for an
open-ended summary. Use a rubric for factuality, coverage, and
unsupported claims; overlap metrics may be supplementary.

<br/>

### Example C --- Imbalanced classification

Suppose 100 requests contain 5 genuinely urgent cases and 95 non-urgent
cases. A classifier labels every request non-urgent.

- Accuracy = (95/100 = 95%).
- Urgent-class recall = (0/5 = 0%).

**Interpretation:** Accuracy alone creates a misleading impression.
Recall for the urgent class is essential if missing urgent requests is
costly.

<br/>

## 11. Small Python Example

The following example computes exact-match accuracy for fixed
identifiers and precision/recall/F1 for a binary classifier.

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Fixed identifiers: exact match is the appropriate criterion.
reference_ids = ["INV-101", "INV-102", "INV-103", "INV-104"]
predicted_ids = ["INV-101", "INV-120", "INV-103", "INV-104"]

id_accuracy = sum(
    pred == ref for pred, ref in zip(predicted_ids, reference_ids)
) / len(reference_ids)

print(f"Identifier exact-match accuracy: {id_accuracy:.1%}")

# Binary classification: 1 means urgent.
y_true = [1, 1, 1, 0, 0, 0, 0, 0]
y_pred = [1, 0, 1, 0, 0, 1, 0, 0]

print(f"Accuracy:  {accuracy_score(y_true, y_pred):.3f}")
print(f"Precision: {precision_score(y_true, y_pred, zero_division=0):.3f}")
print(f"Recall:    {recall_score(y_true, y_pred, zero_division=0):.3f}")
print(f"F1:        {f1_score(y_true, y_pred, zero_division=0):.3f}")
```

Install the dependency with `pip install scikit-learn`.

This example uses prepared labels and outputs. It demonstrates metric
calculation; it is not a live model evaluation.

<br/>

## 12. Common Mistakes

- Using exact match for paraphrasable answers without defining
  semantic equivalence.
- Normalizing away meaningful differences in identifiers, numbers,
  negation, or units.
- Reporting accuracy alone for imbalanced classification.
- Treating BLEU or ROUGE as a direct measure of truth.
- Scoring only successfully parsed outputs and ignoring invalid
  responses.
- Failing to state the denominator or averaging method.
- Combining low-risk and critical fields into one score without
  separate reporting.
- Changing normalization or reference labels after inspecting results
  without versioning the change.

<br/>

## 13. Checkpoint

**Question:** Connect each metric to the task behavior it actually
measures.

**Answer:**

- **Exact match** measures whether an output equals a fixed target
  under a stated comparison and normalization rule.
- **Accuracy** measures the fraction of all classified examples
  assigned the correct label.
- **Precision** measures how often predicted positive cases are truly
  positive.
- **Recall** measures how many actual positive cases are detected.
- **F1** summarizes the balance between precision and recall.
- **Extraction field accuracy** measures the fraction of evaluated
  fields that match their references under field-specific rules.
- **BLEU and ROUGE** measure forms of lexical overlap with reference
  text, not factual correctness or semantic equivalence by themselves.

A metric is appropriate when the behavior it measures aligns with the
task's acceptance criteria. Denominators, normalization, aggregation,
invalid outputs, and missing results must be explicit so scores remain
interpretable.

<br/>

## 14. References

- [scikit-learn --- Model
  evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [scikit-learn --- Classification
  metrics](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html)
- [Hugging Face Evaluate ---
  BLEU](https://huggingface.co/spaces/evaluate-metric/bleu)
- [Hugging Face Evaluate ---
  ROUGE](https://huggingface.co/spaces/evaluate-metric/rouge)
- [Pydantic --- Models and
  validation](https://docs.pydantic.dev/latest/concepts/models/)

Check the metric implementation's current documentation for
tokenization, defaults, and averaging behavior before using it in a
production evaluation suite.

<br/>

## 15. Revision Summary

- Use exact match when the acceptable output is fixed and comparison
  rules are explicit.
- Normalize only differences that are genuinely irrelevant to the
  task.
- Select classification and extraction metrics based on the relevant
  error types and fields.
- Treat BLEU and ROUGE as text-overlap signals, not direct measures of
  truth.
- Define denominators, aggregation, invalid outputs, refusals, and
  missing-result handling before evaluation.
- Explain every reported metric in terms of the task behavior it
  measures and its known limitations.
