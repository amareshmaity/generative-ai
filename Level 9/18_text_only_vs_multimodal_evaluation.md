# Chapter 18: Text-Only versus Multimodal Evaluation

## Learning Objectives

By the end of this chapter, you should be able to:

- Build matched evaluation cases with explicit expected facts or scoring rubrics.
- Compare text-only representations with direct-media and combined-media inputs.
- Separate input-information effects from model, preprocessing, and configuration changes.
- Include visually necessary questions, text-sufficient questions, and unanswerable cases.
- Evaluate correctness, completeness, evidence support, structured-output validity, latency, and cost.
- Label comparisons honestly when multiple factors change.
- Categorize both improvements and regressions after a fixed comparison.

<br/>

## 1. Why Compare Text-Only and Multimodal Systems?

A text-only pipeline may receive OCR, captions, transcripts, or extracted document text. A multimodal pipeline may receive the original image, page, audio, or video alongside text. These inputs do not necessarily contain the same information.

A comparison can help answer questions such as:

- Does direct media input recover facts lost by OCR or captions?
- Does it improve understanding of diagrams, charts, or spatial relationships?
- Does it help when text alone already contains the answer?
- Does it increase unsupported claims, latency, or cost?
- Are differences caused by the input representation, the model, preprocessing, or a combination?

The central rule is to make the comparison design explicit. If multiple factors change at once, report a **full-system comparison** rather than claiming that the modality alone caused the difference.

<br/>

## 2. Define the Evaluation Question and Success Criteria

Start with a narrow application task, such as extracting fields from a report, answering questions about diagrams, or summarizing a short video.

Before running any model, define:

1. The target behavior.
2. The facts or answer elements expected for each case.
3. What counts as correct, partially correct, unsupported, or unanswerable.
4. How citations or evidence references will be checked.
5. The output schema, if a structured response is required.
6. Latency and cost measurements.
7. Acceptance thresholds for the intended use.

Do not write the expected answer after seeing the model outputs. Doing so can bias the rubric toward whichever system happened to be run first.

<br/>

### Example rubric

| Score | Interpretation |
|---|---|
| 2 — Correct | All required facts are correct and supported by the source |
| 1 — Partial | Some required facts are correct, but important details are missing or ambiguous |
| 0 — Incorrect | The answer is materially wrong, unsupported, or fails the task |

For unanswerable cases, score a justified abstention as correct and an invented answer as incorrect. Define the rubric for the task before scoring.

## 3. Build Matched Evaluation Cases

A **matched case** uses the same source, question, expected facts, and scoring rubric across the systems being compared. Only the intended experimental factor should change.

Include at least three types of cases.

### 3.1 Text-sufficient cases

The answer is available in extracted text without needing visual inspection.

Examples:
- A report title clearly appears in selectable text.
- A paragraph explicitly states a date or procedure.
- A transcript contains the phrase needed to answer the question.

These cases reveal whether multimodal input adds value when the textual representation already contains the answer.

<br/>

### 3.2 Visually necessary cases

The answer depends on visual details that are absent or poorly represented in extracted text.

Examples:
- Which component an arrow points to in a diagram.
- Which line corresponds to a particular series in a chart.
- The spatial relationship between two objects.
- A label that appears only inside an image.

These cases test whether direct media input recovers information unavailable from text alone.

<br/>

### 3.3 Unanswerable or ambiguous cases

The source does not contain enough evidence to answer reliably.

Examples:
- Asking for a serial number that is not visible.
- Asking which person spoke when speaker identity is not established.
- Asking for a value obscured by blur or cropping.
- Asking about an event outside the supplied video segment.

These cases test whether a system can acknowledge missing evidence instead of guessing.

### Example test-case dataset

```python
cases = [
    {
        "case_id": "TXT-001",
        "category": "text_sufficient",
        "question": "What reporting period is stated in the introduction?",
        "expected_facts": ["Q2 2026"],
        "source_pages": [1],
        "unanswerable": False,
    },
    {
        "case_id": "VIS-001",
        "category": "visually_necessary",
        "question": "Which component does the arrow point to?",
        "expected_facts": ["pressure sensor"],
        "source_pages": [4],
        "unanswerable": False,
    },
    {
        "case_id": "ABS-001",
        "category": "unanswerable",
        "question": "What is the serial number on the hidden underside?",
        "expected_facts": [],
        "source_pages": [2],
        "unanswerable": True,
    },
]
```

These are illustrative fixtures. Replace the examples with facts manually verified from your own authorized evaluation sources.

<br/>

## 4. Design the Comparison to Isolate Causes

### 4.1 Controlled comparison

To estimate the effect of input representation, hold constant as many other factors as possible:

- Same source documents and questions.
- Same expected answers and scoring rubric.
- Same model and model version, if it supports both input paths.
- Same system instructions and task instructions.
- Same output schema and validation rules.
- Same decoding settings where applicable.
- Same preprocessing, except for the transformation required to create the intended input representation.
- Same number of attempts and comparable evaluation conditions.

Then compare text-only input with direct-media input or combined input.

Even under these controls, the representations may differ in information content, tokenization, or internal processing. Describe the result as evidence from the chosen setup rather than a universal causal law.

<br/>

### 4.2 Factorial comparison

When feasible, separate two factors: input representation and model choice.

| Condition | Input representation | Model |
|---|---|---|
| A | Text-only | Model 1 |
| B | Multimodal | Model 1 |
| C | Text-only | Model 2 |
| D | Multimodal | Model 2 |

This design can help reveal whether the benefit of multimodal input depends on the model. It requires that the selected models support the relevant input paths and that their outputs can be scored comparably.

<br/>

### 4.3 When factors cannot be held constant

Sometimes a text-only model cannot accept images, or the media path requires a different endpoint, preprocessing pipeline, or model. In that case, compare the systems as complete solutions and label the result **full-system comparison**.

Do not write “multimodal input improved accuracy” if the model, prompt, preprocessing, and endpoint all changed together. A more defensible statement is: “System B scored higher under this evaluation setup; the contribution of each changed factor is unresolved.”

<br/>

## 5. Evaluation Dimensions

No single metric adequately describes system quality. Score each dimension separately.

### 5.1 Correctness

Are the claims and extracted values factually correct relative to the source?

Possible measurements:
- Exact-match accuracy for fields with a single expected value.
- Task-specific accuracy or rubric score.
- Numeric error for appropriate numeric prediction tasks.
- Critical-field accuracy for names, dates, IDs, or values where mistakes have high impact.

Define normalization rules before scoring—for example, whether capitalization, punctuation, or equivalent date formats count as a match.

<br/>

### 5.2 Completeness

Did the system include all required facts without adding unnecessary unsupported material?

A response can be correct but incomplete. Score required facts individually when possible, then calculate the fraction of required facts correctly included.

<br/>

### 5.3 Evidence support and citation quality

Check whether each important claim is supported by the cited passage, page, image region, audio segment, or video timestamp.

Track:
- Claims with valid supporting evidence.
- Claims with missing or incorrect citations.
- Claims whose cited source mentions the topic but does not support the conclusion.
- Unsupported claims, including claims that happen to be plausible.

A citation's presence is not proof of grounding. Review the source itself.

<br/>

### 5.4 Unanswerable-case behavior

For cases without sufficient evidence, measure:
- Correct abstentions or explicit uncertainty.
- Unsupported answers.
- Overly broad refusals on answerable cases.

A system that answers every question can score poorly if it guesses on missing evidence.

<br/>

### 5.5 Structured-output validity

If the application requires JSON or a schema:
- Parse the response.
- Validate required fields and data types.
- Check enum values and constraints.
- Apply independent business and evidence checks.
- Record parse and validation failures separately from factual errors.

Valid JSON can still contain incorrect values.

<br/>

### 5.6 Latency, usage, and cost

Measure client-observed end-to-end latency under comparable conditions. If possible, separately measure preprocessing, upload, model request, and post-processing.

Record:
- Median and p95 latency.
- Timeout and retry rate.
- Provider-reported usage where available.
- Estimated cost using the verified current pricing and documented usage units.
- Cost per successful task, not just cost per request.

Label estimates and measured usage separately. Avoid treating client-observed latency as a measurement of provider compute time.

<br/>

## 6. A Practical Scoring Model

Keep raw dimension-level scores even if you later calculate an aggregate score. A weighted score can hide a severe failure in a safety-critical dimension.

An illustrative scorecard:

| Dimension | Measure | Evaluation method |
|---|---|---|
| Correctness | Required facts correct / total required facts | Compare against gold labels |
| Completeness | Required facts present / total required facts | Fact-level review |
| Evidence support | Claims with valid evidence / claims checked | Inspect source locators |
| Abstention | Correct decisions on unanswerable cases | Compare with case labels |
| Schema validity | Valid outputs / total outputs | Parser and schema validator |
| Latency | Median and p95 end-to-end duration | Instrumented runs |
| Cost | Cost per successful task | Usage plus verified rates |
| Reliability | Successful requests / total attempts | Run logs |

If a single weighted score is used for a particular business decision, document the weights and justify them. Keep safety constraints as explicit pass/fail gates rather than allowing high performance elsewhere to compensate for them.

<br/>

## 7. Run a Fixed Comparison

A basic experiment loop can keep the case set consistent:

```python
def evaluate_cases(cases, run_system, score_output):
    results = []

    for case in cases:
        output = run_system(case)
        score = score_output(case, output)

        results.append({
            "case_id": case["case_id"],
            "category": case["category"],
            "output": output,
            "score": score,
        })

    return results
```

Use a `run_system` function for each configuration, such as text-only, direct-media, or combined input. Ensure each function records its model identifier, prompt version, preprocessing settings, elapsed time, and usage when available.

The example is a skeleton, not a complete benchmark harness. Add robust exception handling, output validation, source-evidence checks, and safe logging for your application.

<br/>

### Repeated runs

Model output may vary across requests. For a small exploratory study, one run per case can identify obvious differences, but it may not establish stable performance. If repeatability matters:

- Use documented deterministic settings where available.
- Run multiple trials when budget permits.
- Keep case ordering and scoring rules consistent.
- Report the number of trials.
- Separate per-case variability from aggregate results.

Do not claim statistical significance from a tiny sample without an appropriate analysis.

<br/>

## 8. Categorize Improvements and Regressions

After scoring, classify each meaningful difference.

| Category | Example |
|---|---|
| Improvement | Multimodal input correctly identifies a diagram connection omitted from OCR |
| No meaningful change | Both systems correctly extract a title already present in text |
| Regression | Multimodal input misreads a small label that text extraction captured correctly |
| Safety regression | One system invents a value on an unanswerable case |
| Operational regression | Quality improves slightly but p95 latency or cost increases substantially |
| Inconclusive | Several factors changed, so the cause of the difference cannot be isolated |

For every improvement, also look for regressions. A multimodal system may help on diagrams while being slower or less reliable on simple text extraction.

<br/>

### Result summary template

| Metric | Text-only | Multimodal / combined | Difference |
|---|---:|---:|---:|
| Correctness | Fill in | Fill in | Calculate |
| Completeness | Fill in | Fill in | Calculate |
| Evidence support | Fill in | Fill in | Calculate |
| Correct abstention rate | Fill in | Fill in | Calculate |
| Structured-output validity | Fill in | Fill in | Calculate |
| Median latency | Fill in | Fill in | Calculate |
| p95 latency | Fill in | Fill in | Calculate |
| Cost per successful task | Fill in | Fill in | Calculate |

Fill this table from measured runs. Do not invent results or mix estimates with measurements without labeling them.

<br/>

## 9. Practice: Fixed Comparison and Error Analysis

### Task

Build a small, fixed evaluation set with at least:

- Three text-sufficient cases.
- Three visually necessary cases.
- Three unanswerable or ambiguous cases.

Use the same source evidence, questions, expected facts, and scoring rubric across the configurations you compare.

<br/>

### Procedure

1. Manually verify the expected answer or rubric for every case.
2. Record the model, prompt, preprocessing, and input representation for each system.
3. Run all systems on the same case set.
4. Validate structured outputs and inspect cited evidence.
5. Score correctness, completeness, evidence support, abstention, latency, and usage.
6. Classify each result as improvement, no meaningful change, regression, or inconclusive.
7. Explain whether the cause is likely added information, model choice, preprocessing, or an unresolved combination.
8. Document remaining limitations and any safety-gate failures.

<br/>

### Practice report template

- **Task and use case:**
- **Evaluation dataset and source permissions:**
- **Case counts by category:**
- **Gold-label creation and review:**
- **System A configuration:**
- **System B configuration:**
- **Factors held constant:**
- **Factors changed:**
- **Correctness and completeness results:**
- **Evidence and citation results:**
- **Unanswerable-case results:**
- **Schema-validity results:**
- **Latency and cost results:**
- **Improvements:**
- **Regressions:**
- **Causal attribution confidence:**
- **Largest remaining weakness:**

<br/>

## 10. Revision Questions and Answers

**1. What makes two evaluation cases matched?**  
They use the same source, question, expected facts, and scoring rubric across the systems being compared.

**2. Why include text-sufficient questions?**  
They show whether multimodal input adds value when the textual representation already contains enough information, and they can expose regressions or unnecessary cost.

**3. Why include visually necessary questions?**  
They test whether direct media access recovers information such as layout, arrows, visual relationships, or image-only labels that text extraction may miss.

**4. Why include unanswerable cases?**  
They reveal whether systems invent answers when the source lacks sufficient evidence and whether uncertainty behavior is appropriate.

**5. When should a comparison be labeled full-system?**  
When multiple important factors—such as model, endpoint, prompt, preprocessing, and input representation—change together and their individual contributions cannot be isolated.

**6. Why is structured-output validity separate from correctness?**  
A response can parse successfully and satisfy the schema while still containing false or unsupported facts.

**7. Why report cost per successful task?**  
Cost per request ignores failures and retries. Cost per successful task better reflects the resources required to deliver the intended outcome.

**8. How should an inconclusive comparison be reported?**  
State the observed result, list the factors that changed, and explain that the available design does not identify which factor caused the difference.

<br/>

## 11. Completion Checklist

- [ ] Create matched cases with manually verified expected facts or rubrics.
- [ ] Include text-sufficient, visually necessary, and unanswerable cases.
- [ ] Keep model and settings fixed where the experiment intends to isolate input representation.
- [ ] Label multi-factor comparisons as full-system comparisons.
- [ ] Score correctness and completeness separately.
- [ ] Inspect evidence support and citation accuracy.
- [ ] Test structured-output validity and uncertainty behavior.
- [ ] Measure latency, usage, and cost where available.
- [ ] Categorize both improvements and regressions.
- [ ] Explain which causal conclusions are supported and which remain unresolved.

<br/>

## Checkpoint

**Explain whether a gain comes from added information, model differences, preprocessing, or an unresolved combination.**

A defensible explanation depends on the comparison design. If the same model and settings receive matched cases with only the intended input representation changed, the result provides stronger evidence about the effect of that representation. If model, preprocessing, prompt, or endpoint also changes, report the result as a full-system comparison and avoid attributing the gain to multimodality alone.

<br/>

## Further Reading

Use current official documentation for the selected model, input modality, response format, and pricing. Exact capabilities and billing units vary by provider and model version.

- [OpenAI image and vision guide](https://platform.openai.com/docs/guides/images-vision)
- [OpenAI audio guide](https://platform.openai.com/docs/guides/audio)
- [OpenAI API reference](https://platform.openai.com/docs/api-reference)
- [OpenAI API pricing](https://openai.com/api/pricing/)
- [Pydantic documentation](https://docs.pydantic.dev/)
