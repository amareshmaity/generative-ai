# Chapter 19: Practice and Revision

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain which modalities a model or API supports and how media is represented at a high level.
- Describe image preparation, audio interfaces, and the temporal limitations of video processing.
- Construct supported mixed-modality inputs and validate structured model responses.
- Demonstrate image question answering, mixed-document processing, and an audio API experiment.
- Compare text-only and multimodal approaches using controlled tests and measured results.
- Recommend an approach that accounts for quality, limitations, cost, latency, privacy, and data-handling requirements.

<br/>

## 1. Review Modality Support and High-Level Representations

A multimodal application can accept or produce more than one data type, but support is specific to the selected model, endpoint, and API version. Verify current provider documentation before implementation.

| Modality     | Common input or output                             | High-level representation                                      | Important limitation                                                         |
| ------------ | -------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Text         | Prompts, extracted text, generated responses       | Token sequences                                                | Context limits, ambiguity, missing source evidence                           |
| Image        | Photos, screenshots, page renders                  | Image payloads, patches, crops, or visual tokens               | Small text, resolution, cropping, and visual ambiguity                       |
| Audio        | Recordings, speech, generated sound                | Encoded audio, audio tokens, or intermediate transcripts       | Noise, language/accent variation, duration, and timing                       |
| Video        | Clips, sampled frames, timestamps, sometimes audio | Temporal sequence of frames and/or synchronized media segments | Sparse sampling can miss brief events and motion details                     |
| Mixed inputs | Text plus one or more media payloads               | Ordered content parts with source associations                 | Payload limits, ordering, unsupported combinations, and conflicting evidence |

**Key distinction:** accepting a media file does not guarantee that a model can interpret every detail accurately. Likewise, a model that can generate audio or images may use a different endpoint from one that accepts them as input.

<br/>

### Revision questions

1. Why must model and endpoint capabilities be checked separately?
2. Why can a frame-based video summary miss an event?
3. What is the difference between extracted document text and the original page image?

<br/>

## 2. Image Preparation

A reliable image workflow checks the file before sending it to a model.

1. **Validate the input:** confirm that the file exists, decodes correctly, and uses an accepted format.
2. **Inspect dimensions and size:** large images may increase latency, payload size, or processing cost.
3. **Preserve useful detail:** resize only when necessary; avoid downscaling small text, labels, or fine visual evidence.
4. **Normalize orientation where appropriate:** ensure that the image is displayed in the intended orientation.
5. **Use crops deliberately:** crop a region of interest when it helps, but preserve enough surrounding context to interpret it.
6. **Keep provenance:** record the source identifier, page or frame number, and any preprocessing applied.
7. **Validate the answer:** compare important claims against the image instead of trusting fluent output.

For documents, text extraction and page rendering can complement each other. Extracted text is often efficient for searchable prose; page images can preserve layout, tables, charts, handwriting, and relationships that plain text extraction may lose.

<br/>

## 3. Audio Interfaces

Audio applications commonly use different interfaces for different tasks:

- **Speech recognition (ASR):** audio input produces a transcript, sometimes with timestamps or speaker information.
- **Audio understanding:** audio input is analyzed for meaning or other requested properties; the output may be text.
- **Text-to-speech (TTS):** text input produces an audio file or stream.
- **Audio generation or transformation:** a supported model creates or modifies audio based on text or other audio.

Before making a request, check accepted file types, file-size and duration limits, sample-rate/channel expectations, streaming behavior, output format, usage limits, pricing, and data-handling terms. These details vary by provider and endpoint.

For evaluation, distinguish transcript quality from downstream task correctness. A transcript can contain errors even if it reads naturally, and a correct transcript does not prove that an audio-understanding task was completed correctly.

Useful measures include:

- **Word Error Rate (WER)** for transcription against a reference transcript.
- **Task accuracy or rubric scores** for audio understanding.
- **Intelligibility, naturalness, and pronunciation** for speech synthesis.
- **Latency and cost per completed task** for operational comparison.

<br/>

## 4. Temporal Video Limitations

Video is not merely a collection of unrelated images. Meaning can depend on motion, order, duration, and synchronization with audio.

A system that samples only a subset of frames may miss:

- Brief events between sampled frames.
- The order or duration of actions.
- Fast movement, transitions, or small visual changes.
- Audio cues that explain what is happening.
- The difference between simultaneous and sequential events.

Record the sampling strategy—for example, frame rate, timestamps, and any scene-based selection—so that results are interpretable. When temporal precision matters, evaluate the relevant interval directly and include audio if the task requires it and the chosen interface supports it.

Do not claim that a video was reviewed continuously if the implementation only inspected sampled frames.

<br/>

## 5. Building Supported Mixed Inputs

A mixed-modality request combines text instructions with one or more supported media parts. Its structure depends on the API.

Recommended design:

1. State one clear task and define the expected output.
2. Include only media that is relevant to the task.
3. Keep source identifiers and ordering stable.
4. Associate extracted text with its document, page, or source.
5. Include timestamps for time-based evidence where supported.
6. Do not assume that arbitrary combinations of text, image, audio, and video are accepted by every endpoint.
7. Handle unsupported media, oversized payloads, malformed requests, refusals, and partial responses.
8. Validate the returned structure and then independently verify important factual claims.

<br/>

### Example: provider-neutral request plan

```python
request_plan = {
    "task": "Extract the invoice total and explain its evidence",
    "sources": [
        {
            "source_id": "invoice-001",
            "kind": "page_image",
            "page_number": 1,
            "purpose": "Verify layout and the printed total"
        },
        {
            "source_id": "invoice-001",
            "kind": "extracted_text",
            "page_number": 1,
            "purpose": "Support efficient text lookup"
        }
    ],
    "output_fields": [
        "invoice_total",
        "currency",
        "evidence",
        "uncertainty"
    ]
}
```

This is an application-level plan, not a universal API payload. Convert it into the content-part format documented for the selected provider and endpoint.

<br/>

## 6. Structured Response Validation

A response that looks like JSON is not necessarily valid JSON, and valid JSON is not necessarily correct.

Use multiple validation layers:

1. **Syntax validation:** can the response be parsed?
2. **Schema validation:** are required fields present and correctly typed?
3. **Business-rule validation:** are values plausible and internally consistent?
4. **Evidence validation:** does the source actually support the claim?
5. **Completeness validation:** are required fields missing or left ambiguous?
6. **Operational validation:** was the response complete, or was it truncated or refused?

Example with Pydantic v2:

```python
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class ExtractionResult(BaseModel):
    answer: Optional[str] = None
    evidence: list[str] = Field(default_factory=list)
    uncertainty: Optional[str] = None

def validate_result(payload: dict) -> ExtractionResult:
    try:
        return ExtractionResult.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Invalid model output: {exc}") from exc
```

This validates the structure only. It does **not** establish that the answer or evidence is factually correct. For critical values, compare against the source or an independent rule.

<br/>

## 7. Demonstration Portfolio

Complete the three application demonstrations and retain the same source fixtures wherever possible.

### Demonstration A: Image Question Answering

**Goal:** answer a question using evidence in an image.

Tasks:

- Choose a small, clearly understood image and define the expected answer.
- Validate the file and prepare it using the selected API's documented image interface.
- Ask a focused question; request uncertainty or evidence when appropriate.
- Compare the output with a manually verified answer.
- Test at least one difficult case, such as small text, ambiguity, or missing evidence.

Record:

- Model and endpoint
- Image dimensions and preprocessing
- Prompt and expected answer
- Correctness, evidence support, latency, and measured usage or cost
- Failure cases and next action

<br/>

### Demonstration B: Mixed-Document Processing

**Goal:** extract and summarize information from a document that may contain both text and visual structure.

Tasks:

- Select a PDF with a table, chart, form, or layout that matters.
- Extract text and render relevant pages to images.
- Compare text-only, image-only, and combined evidence where the chosen model supports the comparison.
- Return a structured result with source/page references.
- Check totals, dates, units, table relationships, and key statements against the original document.

Record omissions, incorrect values, unsupported claims, citation support, latency, and measured usage or cost. Do not assume that combining text and images will always improve the result; measure it.

<br/>

### Demonstration C: Audio API Experiment

**Goal:** test one supported speech or audio task.

Choose one task:

- ASR: transcribe a recording and compare it with a reference transcript.
- Audio understanding: answer a defined question about a recording and verify the result.
- TTS: generate speech from fixed text and review the resulting audio.

Tasks:

- Inspect the source audio and verify the endpoint's accepted format and limits.
- Use a fixed input and record model/endpoint configuration.
- Validate the returned text or audio file.
- Measure task quality, latency, and usage/cost where available.
- Record any language, noise, pronunciation, clipping, or timing issues.

Do not report estimated cost or expected behavior as if it were measured. Mark unavailable measurements explicitly.

<br/>

## 8. Comparing Text-Only and Multimodal Results

Use matched test cases so the comparison isolates the value of the modality rather than differences in the questions or expected answers.

Classify each case:

- **Text-sufficient:** reliable extracted text contains the needed evidence.
- **Visual evidence required:** layout, chart structure, spatial relationships, handwriting, or image details matter.
- **Temporal/audio evidence required:** the task depends on timing, motion, speech, or sound.
- **Insufficient evidence:** neither approach has enough reliable information to answer.

Track a compact evaluation table:

| Metric              | What to record                                                                |
| ------------------- | ----------------------------------------------------------------------------- |
| Task correctness    | Whether the answer meets a verified reference or rubric                       |
| Evidence support    | Whether each important claim is supported by the source                       |
| Completeness        | Whether required facts or fields were omitted                                 |
| Abstention behavior | Whether the system admits insufficient evidence                               |
| Schema validity     | Whether structured outputs pass parsing and schema checks                     |
| Latency             | End-to-end time, measured consistently                                        |
| Cost/usage          | Actual provider usage and cost where available; otherwise mark unavailable    |
| Data handling       | Media sent, processing location/retention terms, access controls, and logging |

Use the same evaluation criteria for each approach. Report sample size and important test conditions. Separate measured results from qualitative observations and estimates.

<br/>

### Simple evaluation record

```python
evaluation_record = {
    "case_id": "case-001",
    "approach": "multimodal",
    "expected_answer": "verified reference",
    "actual_answer": "model output",
    "correct": None,          # Fill after review
    "evidence_supported": None,
    "schema_valid": None,
    "latency_ms": None,       # Fill from measurement
    "usage_or_cost": None,    # Fill from provider data if available
    "notes": "Document preprocessing and failure conditions"
}
```

Do not calculate a score from placeholder `None` values. Define the scoring rubric before evaluating the outputs.

<br/>

## 9. Troubleshooting by Pipeline Stage

| Symptom                        | Likely area to inspect                                              | Diagnostic action                                                                 |
| ------------------------------ | ------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Image answer misses small text | Resolution, crop, image quality, or visual capability               | Inspect the source dimensions and test a targeted crop                            |
| Document total is wrong        | Text extraction, table layout, arithmetic, or grounding             | Compare extracted text and page image; verify the calculation independently       |
| Audio transcript is inaccurate | Recording quality, language, noise, endpoint settings               | Inspect the audio and compare errors against a reference                          |
| Video summary misses an event  | Frame sampling or missing audio                                     | Review timestamps and sample the relevant interval more densely                   |
| Mixed request fails            | Unsupported content combination, payload limit, or malformed schema | Check the endpoint contract and reduce the request to a minimal reproducible case |
| JSON cannot be parsed          | Formatting, truncation, or incomplete response                      | Inspect the raw response and use supported structured-output features             |
| Output is valid but incorrect  | Evidence selection, model reasoning, or weak evaluation             | Verify claims against source evidence; add targeted tests                         |
| Results vary across runs       | Sampling, model version, prompt, or input variation                 | Record configuration and repeat matched tests                                     |

<br/>

## 10. Recommendation and Data-Handling Report

Complete this report after the demonstrations.

### A. Recommended approach

- **Use case and user need:**
- **Recommended approach:** text-only, multimodal, or a staged/hybrid pipeline
- **Why this approach fits the evidence requirements:**
- **Alternatives considered:**

<br/>

### B. Measured benefits

- Evaluation dataset and number of cases:
- Quality metric and results by approach:
- Evidence-support and completeness results:
- Latency measurements:
- Provider-reported usage/cost:
- Important qualitative observations:

<br/>

### C. Limitations and residual risks

- Cases where the approach failed:
- Evidence that remains ambiguous or unavailable:
- Known modality or temporal limitations:
- Conditions requiring abstention or human review:
- Tests still needed before production:

<br/>

### D. Data-handling requirements

- Types of personal, confidential, or sensitive data involved:
- Data sent to the model/provider:
- Provider retention and training-use terms verified:
- Access control, encryption, and deletion requirements:
- Logging and redaction policy:
- Consent, copyright, voice/image rights, and provenance considerations:
- Applicable organizational or legal requirements:

<br/>

### E. Decision

State the recommendation, the measured benefit over the alternative, the largest remaining weakness, and the safeguards required before deployment. If the evidence is insufficient, say so and identify the next experiment.

<br/>

## 11. Common Questions

**Q1. Is multimodal always better than text-only?**  
No. Multimodal input is useful when the needed evidence is visual, acoustic, or temporal. It can add cost, latency, complexity, and new failure modes when extracted text already contains the necessary information.

**Q2. Does valid structured output guarantee a correct answer?**  
No. Schema validation checks form and types, not whether the answer is supported by the source.

**Q3. Can sampled frames establish everything that happened in a video?**  
No. Events between sampled frames may be missed. State the sampling strategy and test the time intervals relevant to the task.

**Q4. What should be reported when an API does not expose exact cost?**  
Report the available usage fields, document the pricing assumptions used for any estimate, and label estimates clearly. Never present an estimate as an observed charge.

**Q5. What is the main principle for a production recommendation?**  
Choose the least complex approach that meets the verified quality and evidence requirements, then document its measured trade-offs and data-handling controls.

<br/>

## 12. Final Checklist

- [ ] Verified modality support for the chosen model, endpoint, and API version.
- [ ] Explained high-level image, audio, and video representations and limitations.
- [ ] Validated media files and documented preprocessing.
- [ ] Built only combinations supported by the chosen API.
- [ ] Validated structured responses and checked claims against evidence.
- [ ] Completed image Q&A, mixed-document, and audio demonstrations.
- [ ] Compared text-only and multimodal methods on matched cases.
- [ ] Recorded correctness, evidence support, completeness, latency, and available usage/cost.
- [ ] Distinguished measurements, estimates, and qualitative observations.
- [ ] Documented privacy, retention, access, deletion, consent, and provenance requirements.
- [ ] Written a recommendation with measured benefits and residual weaknesses.

<br/>

## Checkpoint

**Recommend an approach with measured benefits, limitations, and data-handling requirements.**

A defensible recommendation must connect the use case to verified evidence, show results from a controlled comparison, disclose failure cases and operational trade-offs, and state how source media will be protected. If the experiments do not establish a meaningful benefit, recommend the simpler approach or collect more evidence before deciding.

<br/>

## References

Use the current official documentation for the exact provider and endpoint selected in your experiment. Interfaces, supported modalities, limits, prices, and data-handling terms can change.

- OpenAI API documentation: https://platform.openai.com/docs
- OpenAI image and vision guide: https://platform.openai.com/docs/guides/images-vision
- OpenAI audio guide: https://platform.openai.com/docs/guides/audio
- OpenAI structured outputs guide: https://platform.openai.com/docs/guides/structured-outputs
- Pydantic documentation: https://docs.pydantic.dev/
- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- jiwer (word error rate): https://github.com/jitsi/jiwer
