# 11. Combining Text with Image, Audio, or Video Inputs

## Learning Objectives

By the end of this chapter, you should be able to:

- Structure a multimodal request using the content-part formats supported by the selected interface.
- Reference each media item unambiguously and preserve the relationship between media and text.
- Maintain ordering, timestamps, and cross-modal correspondence.
- Select complementary inputs without sending redundant material unnecessarily.
- Handle disagreement between text, images, transcripts, and video observations.
- Bound media count, total duration, file size, and context usage.

<br/>

## 1. Why Combine Modalities?

Many tasks require more than one kind of evidence. A document page may contain both selectable text and a chart image. A video may need visual frames and an audio transcript. A photograph may be paired with a question that identifies a specific region or object.

Combining modalities can provide richer context, but only when each input contributes useful information. Duplicate or poorly referenced inputs can increase cost and ambiguity without improving the answer.

| Use case | Complementary inputs | Why combine them? |
|---|---|---|
| Document question answering | Page image, extracted text, page number, question | Text supports exact wording; image preserves layout and visual evidence |
| Meeting analysis | Audio or transcript, timestamps, speaker labels where available | Text supports search; timestamps help locate the original utterance |
| Video summarization | Timestamped frames, transcript, audio-event notes | Frames show visual states; transcript and audio may provide spoken or acoustic context |
| Product inspection | Image, product description, focused question | Description provides context; image supplies visual evidence to check |
| Diagram explanation | Diagram image, extracted labels, specific question | Labels aid text matching; the image preserves relationships and spatial structure |

A modality should be included because it contributes evidence, not simply because it is available.

<br/>

## 2. Supported Content Parts and Media References

A multimodal request may contain text and one or more media content parts. The exact structure depends on the model API or application framework.

Conceptually, a request may include:
- A text instruction or question.
- A document page image.
- Extracted text from that same page.
- A timestamp or page identifier.
- An explicit mapping between each item and its role.

Do not assume that all interfaces use the same JSON schema, image format, audio representation, or video structure. Use the exact content-part format documented for the chosen model and endpoint.

<br/>

### Example: a provider-neutral request plan

The following is a planning representation, not a directly executable API payload:

```python
request_plan = {
    "task": "answer a question using a document page",
    "question": "What is the total shown in the bottom-right summary cell?",
    "media_items": [
        {
            "id": "page_4_image",
            "type": "image",
            "source": "document_page_4.png",
            "role": "visual evidence",
            "page_number": 4,
        },
        {
            "id": "page_4_text",
            "type": "text",
            "source": "extracted text from page 4",
            "role": "textual evidence",
            "page_number": 4,
        },
    ],
    "rules": [
        "Use only evidence from page 4.",
        "If the value is unreadable or absent, say so.",
        "Do not infer a value from unrelated pages.",
    ],
}
```

This plan makes each source identifiable. An implementation must translate it into the selected interface's actual content-part structure.

<br/>

### Make references explicit

Avoid vague phrases such as “look at this,” “compare the other one,” or “use the earlier audio” when several items are present.

Prefer stable identifiers and descriptions:
- `page_4_image` — image of page 4.
- `page_4_text` — extracted text from page 4.
- `frame_012_at_00-00-06.000` — sampled video frame at six seconds.
- `audio_segment_03_from_00-00-12_to_00-00-18` — audio segment with its original time interval.
- `transcript_segment_03` — transcript aligned to that audio interval.

Use identifiers consistently throughout the prompt, metadata, logs, and returned evidence. An identifier is useful only if the application maintains a reliable mapping from it to the actual media item.

<br/>

## 3. Preserve Ordering, Timestamps, and Correspondence

Multimodal inputs often have relationships that are as important as their content.

### Ordering

Preserve the intended sequence of pages, frames, audio segments, or conversation turns. If a request contains multiple items, specify whether they should be compared independently, read in sequence, or treated as parts of one source.

<br/>

### Timestamps

For audio and video, keep timestamps tied to the original timeline. If media is trimmed or split, store both the segment-local time and the original offset when relevant.

For example:

| Item ID | Original interval | Role |
|---|---|---|
| `frame_01` | 00:00:02.000 | Shows scene before the action |
| `frame_02` | 00:00:04.000 | Shows scene after the action |
| `audio_01` | 00:00:01.500–00:00:04.500 | Contains the relevant sound |
| `transcript_01` | 00:00:02.100–00:00:03.200 | Transcript aligned to the audio |

These values are illustrative. In a real application, use measured timestamps from the actual media rather than invented or rounded values that could mislead the reader.

<br/>

### Correspondence

If extracted text came from a specific page, retain that page reference. If a transcript came from an audio segment, retain the segment and time interval. If a frame was extracted from a video, preserve its timestamp and sampling metadata.

Without correspondence, the model may combine evidence from unrelated pages, time intervals, speakers, or media items.

<br/>

## 4. Choose Complementary Inputs

Before adding another input, ask what it contributes.

- Extracted text may make exact wording searchable, while the page image preserves layout, table structure, handwriting, or visual relationships.
- A transcript may make speech easier to search, while the audio remains necessary to review pronunciation, overlapping speakers, tone, or non-speech sounds.
- Video frames show selected visual states, while audio may reveal speech or events not visible in the frames.
- A concise text description can establish the task context, but should not be mistaken for independently verified visual evidence.

<br/>

### Avoid unnecessary duplication

Sending the same information repeatedly can increase token or processing usage, make references less clear, and crowd out more relevant context.

However, apparent duplication may be justified when representations have different purposes. For example, extracted text and a page image are not fully interchangeable: the text may preserve exact words, while the image preserves spatial relationships.

Use a simple inclusion test:

1. Does this item add distinct evidence or necessary metadata?
2. Is the item relevant to the specific question?
3. Can the application reference it unambiguously?
4. Is its size and processing cost justified?
5. Would omitting it create a meaningful information gap?

<br/>

## 5. Handling Disagreement Between Modalities

Different inputs may disagree because of OCR errors, transcription errors, stale descriptions, ambiguous visuals, or genuine inconsistencies in the source.

Examples:
- Extracted text says “18.5,” but the page image appears to show “16.5.”
- A transcript says “fifteen,” while the audio is unclear or may contain “fifty.”
- A caption describes a red vehicle, but the sampled frame does not clearly establish its color.
- A video transcript and visual timeline appear to place an event at different times.

<br/>

### A disciplined resolution process

1. **Identify the conflict.** State exactly which sources disagree.
2. **Check provenance.** Confirm that the text and media came from the same page, recording, version, and time interval.
3. **Inspect the original evidence.** When permitted, review the original page, audio interval, or relevant video frames.
4. **Respect modality limits.** A transcript may not preserve acoustic ambiguity; a still frame may not establish motion; extracted text may lose table layout.
5. **Avoid silent reconciliation.** Do not choose a value simply because it seems more plausible.
6. **Report unresolved uncertainty.** If the source remains ambiguous, say so and request a clearer input or human review when necessary.

There is no universal rule that one modality always overrides another. The appropriate evidence depends on the question. For exact printed wording, a clear source image may help resolve OCR errors. For what was actually audible, the recording may be more informative than a noisy transcript. For factual truth, neither representation alone is necessarily sufficient.

<br/>

## 6. Bound Media Count, Duration, Size, and Context

Multimodal context is constrained by more than text length. Images, audio, and video may have different preprocessing and accounting rules, and limits vary by interface.

### Media count

Send the items needed for the task, not every available asset. Group or select relevant pages and intervals when supported, while retaining source identifiers.

<br/>

### Total duration

For audio and video, track both individual segment duration and total duration. Many short segments can still produce substantial aggregate processing work.

### File size and representation

A compressed file's byte size does not directly indicate the amount of model processing required. Image resolution, video frame selection, audio duration, and the model's internal representation may affect processing independently.

<br/>

### Context usage

Textual descriptions, extracted text, timestamps, and metadata all consume context. Keep metadata concise but sufficient to preserve provenance and correspondence. Summarize long sources only when the task permits it, and keep the original source available for verification.

<br/>

### Preflight checklist

Before sending a request, verify:
- The endpoint supports each media type and the chosen content-part format.
- Every item has a stable ID and relevant source metadata.
- Page order or media chronology is preserved.
- Total media count, size, duration, and context fit documented limits.
- The question identifies which sources should be used.
- Error handling exists for missing, rejected, or unreadable media.
- The response can identify supporting source items where required.

<br/>

## 7. Practical Exercise: Combine a Document Page, Extracted Text, and a Question

Use a document page that you are permitted to process. Choose a page containing both text and a visual element such as a table, chart, diagram, or summary box.

### Step 1 — Select the evidence

Collect:
- The page image.
- Extracted text from the same page.
- The page number and source document identifier.
- One precise question that needs the page's evidence.

<br/>

### Step 2 — Define the references

Use stable identifiers, such as `report_A_page_4_image` and `report_A_page_4_text`. Confirm that both items really correspond to the same page.

<br/>

### Step 3 — Write the request

Example request:

> Answer the question using only the two items identified below. `report_A_page_4_image` is the visual rendering of page 4, and `report_A_page_4_text` is extracted text from that same page. Question: What total is shown in the bottom-right summary cell? Use the page image to inspect the cell and layout, and use extracted text as supporting evidence. If the sources disagree or the value is unreadable, report the conflict or uncertainty instead of guessing. Identify the source item supporting the answer.

Translate this instruction into the actual content-part format required by the selected model interface.

<br/>

### Step 4 — Test ambiguity and disagreement

Check whether:
- The page image and extracted text are correctly paired.
- The relevant cell can be distinguished from neighboring values.
- The extracted text preserves the value and table structure adequately.
- The answer remains grounded in page 4 rather than outside knowledge.
- Any disagreement is reported rather than silently resolved.

<br/>

### Practice report template

| Field | Notes |
|---|---|
| Source document and page | |
| Image item ID | |
| Extracted-text item ID | |
| Question | |
| Interface and content-part format | |
| Size/context limits checked | |
| Evidence supporting the answer | |
| Disagreement or uncertainty | |
| Final answer and source references | |
| Main design improvement | |

<br/>

## 8. Revision Questions and Answers

**1. Why combine text with an image or other media?**  
Different modalities may provide complementary evidence. Extracted text can help with exact wording, while an image can preserve layout and visual relationships.

**2. Why use explicit media identifiers?**  
They make it clear which page, frame, segment, or transcript a statement refers to and help prevent evidence from being mixed up.

**3. Why preserve timestamps and ordering?**  
They maintain temporal context and make it possible to relate an observation to the correct moment in the original recording.

**4. Should every available image, transcript, or frame be included?**  
No. Include relevant items that add evidence or necessary context. Unnecessary duplication can increase processing cost and ambiguity.

**5. What should an application do when a transcript conflicts with audio?**  
Confirm the source mapping, inspect the relevant original audio when permitted, consider the limitations of each representation, and report unresolved uncertainty rather than guessing.

**6. Does extracted text replace a document image completely?**  
No. Extracted text may lose layout, spatial relationships, handwriting, and visual details such as chart structure.

**7. Why are media limits more complex than text limits?**  
Each modality may have its own size, duration, resolution, encoding, and preprocessing constraints. Actual accounting depends on the selected interface and model.

**8. How can an application make cross-modal references unambiguous?**  
Assign stable IDs, preserve source metadata and timestamps, explicitly describe each item's role, maintain ordering, and refer to those IDs consistently in the request and evidence returned.

<br/>

## Chapter Checkpoint

**Explain how the application makes cross-modal references unambiguous.**

A strong answer should explain that the application assigns each media item a stable identifier and retains its source, type, page number or timestamp, and relationship to associated text. The request names each item and explains its role, while preserving order and timeline information. This lets the model and downstream application distinguish, for example, an image of a specific page from extracted text belonging to that page. The application should validate these mappings and report conflicts rather than silently combining unrelated or contradictory evidence.

<br/>

## Completion Checklist

- [ ] I can describe supported multimodal content parts without assuming one universal API schema.
- [ ] I can assign stable IDs and explicit roles to media items.
- [ ] I can preserve page order, timestamps, and media-to-text correspondence.
- [ ] I can choose complementary inputs and avoid unnecessary duplication.
- [ ] I can handle disagreement between text, images, transcripts, and video evidence.
- [ ] I can check media count, duration, file-size, and context limits.
- [ ] I can design a document question-answering request with traceable evidence.

<br/>

## References

Content-part formats, supported modalities, and limits vary by provider, model, and endpoint. Verify the current documentation for the exact interface you use.

- [OpenAI platform documentation](https://platform.openai.com/docs/overview)
- [OpenAI API reference](https://platform.openai.com/docs/api-reference)
- [Hugging Face documentation](https://huggingface.co/docs)
