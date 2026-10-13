# Level 9: Multimodal Generative AI

**Goal:** Understand models that process or generate more than one modality, with emphasis on practical applications.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 9`, following the previous levels. The filenames below are planned files, not existing chapter links.

**Depth guidance:** This level introduces multimodal model capabilities and application patterns. Image-generation techniques are explored further in Level 10; audio, speech, and video generation techniques in Level 11.

## Prerequisites

- Complete [Level 8: Retrieval-Augmented Generation (RAG)](<../Level 8/README.md>).
- Review prompting, structured outputs, validation, model APIs, and safe file handling from earlier levels.
- Understand token budgets, source attribution, and retrieval permissions.
- Use an isolated Python environment and public, synthetic, or appropriately consented images, documents, and audio.
- Model access is useful for experiments. Prepared fixtures support offline application testing but do not establish model performance.

## Learning outcomes

After completing this level, you should be able to:

- Distinguish input understanding from output generation for each modality.
- Explain VLMs and high-level image representations.
- Build an image-question-answering application and a mixed text/image document workflow.
- Describe audio, speech, and video capabilities and their limitations.
- Construct supported mixed-modality requests and validated structured outputs.
- Explain multimodal RAG, evidence provenance, and access boundaries.
- Compare text-only and multimodal approaches using task-quality, latency, and cost measurements.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_multimodal_models_overview.md` | Modalities, understanding, and generation |
| 2 | `02_text_only_and_multimodal_capabilities.md` | Capability matrices and model selection |
| 3 | `03_vision_language_models.md` | Visual encoding and language integration |
| 4 | `04_image_inputs_and_visual_question_answering.md` | Image requests, questions, and evidence |
| 5 | `05_resolution_crops_patches_and_visual_tokens.md` | Image preparation and representation budgets |
| 6 | `06_document_understanding_with_text_and_images.md` | Layout, tables, charts, and mixed evidence |
| 7 | `07_audio_inputs_and_outputs.md` | Formats, sampling, duration, and interfaces |
| 8 | `08_speech_recognition_and_text_to_speech.md` | Transcription and speech synthesis |
| 9 | `09_audio_generation_fundamentals.md` | Speech, music, sound, and conditioning |
| 10 | `10_video_understanding_and_generation.md` | Frames, temporal evidence, and generation concepts |
| 11 | `11_combining_text_image_audio_and_video.md` | Mixed inputs, ordering, and synchronization |
| 12 | `12_multimodal_prompting_and_structured_outputs.md` | Task specifications and output validation |
| 13 | `13_multimodal_rag_concepts.md` | Cross-modal retrieval and source-grounded answers |
| 14 | `14_limitations_latency_cost_and_responsible_use.md` | Evaluation, resource use, and data handling |
| 15 | `15_image_question_answering_project.md` | A validated image Q&A application |
| 16 | `16_mixed_document_extraction_and_summary_project.md` | Structured extraction and supported summaries |
| 17 | `17_speech_or_audio_api_experiment.md` | One bounded audio-service experiment |
| 18 | `18_text_only_vs_multimodal_evaluation.md` | Matched comparisons and failure analysis |
| 19 | `19_practice_and_revision.md` | Consolidation and the level report |

## Chapter outlines

### 01. What Multimodal Models Are

- Define modalities and distinguish supported input and output combinations.
- Introduce joint representations, modality-specific encoders, and integration conceptually.
- Compare a single multimodal model with a pipeline of specialized models.
- Distinguish understanding existing media from generating new media.
- Explain why support for one modality does not imply support for every task in that modality.

**Practice:** Draw input/output diagrams for three multimodal applications.

**Checkpoint:** Explain a model's capabilities without assuming all multimodal models generate images, audio, and video.

### 02. Text-Only versus Multimodal Capabilities

- Compare text descriptions, OCR transcripts, and direct image inputs.
- Identify information lost when converting media into text.
- Map input/output requirements to documented model capabilities.
- Compare native support with preprocessing through separate services.
- Consider simpler text-only baselines when they satisfy the task.

**Practice:** Create a capability matrix for candidate approaches without relying on marketing labels.

**Checkpoint:** Explain when direct media inputs offer useful information beyond a text representation.

### 03. Vision-Language Models (VLMs)

- Introduce visual encoders, representation projection, and language integration at a high level.
- Discuss captioning, visual question answering, document analysis, and image comparison.
- Distinguish image understanding from text-to-image generation.
- Discuss visual grounding and the limits of spatial, counting, and fine-detail performance.
- Explain that architecture and supported image handling vary across models.

**Practice:** Annotate a conceptual image-to-text model flow.

**Checkpoint:** Describe how image information can influence a language response without assuming a universal architecture.

### 04. Image Inputs, Image Understanding, and Visual Question Answering

- Prepare supported formats, sizes, and request representations.
- Ask questions that identify the image and required evidence clearly.
- Handle multiple images and distinguish comparisons from independent descriptions.
- Separate visible observations from inferred explanations.
- Handle unreadable, ambiguous, missing, or unsupported inputs.
- Validate uploads and treat text visible inside images as untrusted content.

**Practice:** Test questions about synthetic scenes, signs, and simple diagrams, including an unanswerable question.

**Checkpoint:** Avoid presenting inferred or invisible details as direct observations.

### 05. Image Resolution, Crops, Patches, and Visual Tokens

- Introduce resizing, aspect ratio, crops, tiling, and patch-based representations conceptually.
- Explain detail loss from downsampling and loss of surrounding context from cropping.
- Discuss visual-token or image-input accounting where documented.
- Distinguish conceptual patches from provider-specific processing and billing units.
- Compare quality, input size, latency, and resource use.

**Practice:** Compare full-image and cropped inputs for a small-text or chart-reading task.

**Checkpoint:** State preprocessing and accounting assumptions rather than inventing a universal image-token formula.

### 06. Document Understanding Using Text and Images

- Combine extracted text with page images while preserving page identity.
- Interpret headings, columns, tables, charts, captions, and text-image relationships.
- Compare OCR/text-only processing with visual or combined processing.
- Preserve source locators and evidence for extracted fields.
- Handle unreadable regions, conflicting representations, and unsupported numerical interpretation.

**Practice:** Extract fields and summarize a public or synthetic report containing a table or chart.

**Checkpoint:** Trace extracted facts back to page evidence and identify where visual interpretation is uncertain.

### 07. Audio Inputs and Outputs

- Introduce audio formats, sample rates, channels, duration, and encoding.
- Distinguish uploaded audio, streaming audio, and generated audio outputs.
- Compare waveform-based and tokenized representations conceptually.
- Inspect supported interfaces and input/output limits.
- Handle clipping, noise, silence, incomplete files, and processing failures.

**Practice:** Inspect a short permitted audio file and document its format and model-interface requirements.

**Checkpoint:** Explain why file format, duration, and acoustic quality affect processing.

### 08. Speech Recognition and Text-to-Speech Concepts

- Distinguish transcription from synthesis and from general audio understanding.
- Introduce language, accents, timestamps, speaker labels, and noise considerations.
- Separate recognized speech from verified facts about its content.
- Discuss pronunciation, intelligibility, pacing, and available voice controls.
- Treat transcribed instructions as untrusted input to later processing.

**Practice:** Compare a transcription against a known script or evaluate synthesized speech from a short script.

**Checkpoint:** Explain that transcription and speech synthesis are related pipeline tasks but not identical generative capabilities.

### 09. Audio Generation Fundamentals

- Introduce generated speech, music, sound effects, and audio-to-audio tasks.
- Discuss text or audio conditioning and high-level representations.
- Compare intelligibility, acoustic quality, prompt adherence, and diversity.
- Introduce duration, continuity, compute, and latency trade-offs.
- Discuss consent, permitted voice use, attribution, and provenance.

**Practice:** Design an audio-generation request and a task-specific evaluation rubric.

**Checkpoint:** Distinguish speech quality from factual correctness and general audio quality.

**Depth boundary:** Detailed generation workflows, expressive speech, and real-time media techniques belong to Level 11.

### 10. Video Understanding and Video Generation Fundamentals

- Compare frame-based image analysis with temporal video understanding.
- Introduce frame sampling, timestamps, motion, and event order.
- Discuss missed short events and ambiguity from sparse sampling.
- Introduce text-to-video and image-to-video generation conceptually.
- Discuss temporal consistency, motion coherence, and audio-video synchronization.
- Distinguish native video support from application-controlled frame extraction.

**Practice:** Plan a timestamped summary of a short permitted clip and identify what frame sampling could miss.

**Checkpoint:** Explain why a set of still images may be insufficient to establish an event sequence.

### 11. Combining Text with Image, Audio, or Video Inputs

- Use supported content-part formats and explicit references to each media item.
- Preserve ordering, timestamps, and correspondence between modalities.
- Select complementary inputs rather than duplicating information unnecessarily.
- Handle disagreement between text, images, and transcripts.
- Bound media count, total duration, size, and context use.

**Practice:** Design a request combining a document page, extracted text, and a specific question.

**Checkpoint:** Explain how the application makes cross-modal references unambiguous.

### 12. Multimodal Prompting and Structured Outputs

- Specify task, evidence boundaries, output schema, and uncertainty handling.
- Request source/page/image/timestamp references that the application can validate.
- Validate generated JSON with Pydantic and independent business rules.
- Separate schema validity from correct media interpretation.
- Handle refusals, truncation, unsupported content types, and partial results.
- Recognize prompt injection in visible text, audio transcripts, and document content.

**Practice:** Create a structured document-extraction prompt with nullable unknown fields and evidence references.

**Checkpoint:** Explain why schema constraints do not guarantee correct visual or acoustic conclusions.

### 13. Multimodal RAG Concepts

- Compare text-only retrieval over OCR/captions with direct media retrieval.
- Introduce compatible image-text embedding spaces and cross-modal queries.
- Preserve links between retrieved text, original pages, images, and time segments.
- Assemble permitted mixed-modality evidence for answer generation.
- Enforce access controls before fetching media or sending it to external services.
- Discuss information loss, retrieval mismatch, context limits, and citation support.

**Practice:** Draw a RAG pipeline for a knowledge base containing text and diagrams.

**Checkpoint:** Distinguish retrieving a textual description from retrieving and inspecting the underlying media.

**Depth boundary:** A conceptual design or small extension of Level 8 is sufficient; a full multimodal retrieval platform is optional.

### 14. Modality-Specific Limitations, Latency, Cost, and Responsible Use

- Categorize visual-detail, speech-recognition, temporal, and cross-modal failures.
- Measure preprocessing, upload, model processing, and output handling separately where possible.
- Inspect documented usage units such as text tokens, image processing, audio duration, or video processing.
- Distinguish measured usage from estimates and verify pricing for any cost calculations.
- Handle private images, faces, voices, document contents, and media retention appropriately.
- Discuss consent, licensing, provenance, and review for consequential interpretations.
- Avoid exposing media or extracted sensitive content through logs and source links.

**Practice:** Create a failure/risk matrix and measurement plan for one application.

**Checkpoint:** Compare task quality with operational and data-handling costs rather than accuracy alone.

### 15. Image-Question-Answering Application

- Build a small notebook, command-line tool, or FastAPI application accepting a validated image and question.
- Select a documented image-understanding model and input settings.
- Return an answer with explicit uncertainty where evidence is unclear.
- Test unsupported files, unreadable content, absent evidence, and misleading questions.
- Record preprocessing choices, model configuration, and observed results.

**Practice:** Demonstrate the application on public or synthetic scenes, diagrams, and text-containing images.

**Checkpoint:** Trace each answer to visible evidence and document cases the model cannot handle reliably.

### 16. Mixed-Document Extraction and Summary Project

- Process a document containing both text and visual information.
- Compare extracted-text-only input with page-image or combined input.
- Produce schema-validated fields and an evidence-supported summary.
- Preserve page locators and inspect numerical/table claims independently.
- Document omissions, hallucinations, and differences between approaches.

**Practice:** Demonstrate extraction and summarization with inspectable source evidence.

**Checkpoint:** Explain which facts required visual information and which were available from text alone.

### 17. Speech or Audio Model API Experiment

- Select one available transcription, speech-synthesis, or audio-understanding API.
- Verify its current formats, limits, usage metadata, and data-handling rules.
- Use a short public, synthetic, or consented sample.
- Validate returned metadata or generated files and handle failures.
- Measure task-specific quality and processing time; record cost where available.

**Practice:** Run and document one bounded experiment. If access is unavailable, use fixtures for integration practice and identify the unmeasured model-quality portion.

**Checkpoint:** Distinguish observed service results from prepared examples and estimated performance.

### 18. Text-Only versus Multimodal Evaluation

- Build matched cases with explicit expected facts or task rubrics.
- Compare text-only representations with direct or combined media input.
- Separate input-information differences from changes in model choice and settings.
- Include visually necessary questions, text-sufficient questions, and unanswerable cases.
- Evaluate correctness, completeness, evidence support, structured-output validity, latency, and cost.
- Label comparisons as full-system comparisons when multiple factors change.

**Practice:** Run a fixed comparison and categorize both improvements and regressions.

**Checkpoint:** Explain whether a gain comes from added information, model differences, preprocessing, or an unresolved combination.

### 19. Practice and Revision

- Review modality support and high-level representations.
- Explain image preparation, audio interfaces, and temporal video limitations.
- Build supported mixed inputs and validate structured responses.
- Demonstrate image Q&A, mixed-document processing, and an audio experiment.
- Compare text-only and multimodal results and complete the report below.

**Checkpoint:** Recommend an approach with measured benefits, limitations, and data-handling requirements.

## Level deliverable: Multimodal applications and comparison report

Create `multimodal_comparison_report.md` in this folder with:

1. A capability matrix identifying supported input and output modalities for each selected model or pipeline.
2. A reproducible image-Q&A application with sample inputs and expected evidence.
3. A mixed-document extraction and summary workflow with validated fields and page references.
4. One documented speech/audio API experiment, or a clearly labeled access limitation with fixture-based integration checks.
5. At least ten matched text-only/multimodal test cases with expected facts or rubrics, including unclear and unanswerable inputs.
6. Input preprocessing, model identifiers, prompts, settings, SDK versions, and experiment dates.
7. Separate results for task quality, evidence support, output validity, latency, and usage/cost where available.
8. Tests for invalid media, unsupported requests, and application error handling.
9. A conceptual multimodal RAG diagram showing provenance and authorization boundaries.
10. Failure analysis, consent/licensing considerations, remaining limitations, and a recommended approach.

The projects may share one codebase and need not be deployed. Local models and available services are both suitable. Paid services and video generation are not required; prepared fixtures must not be reported as live model results.

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Input/output capability definition and a concrete example.
3. Representation or request-flow diagram.
4. Minimal implementation or worked comparison.
5. Media preparation, schemas, and validation.
6. Failure cases, trust boundaries, and quality/latency/cost trade-offs.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current model capabilities, supported media formats, provider accounting, SDK behavior, and licenses when writing implementation notes. Preserve test media versions and document preprocessing to make comparisons reproducible.

## Completion checklist

- [ ] Distinguish modality understanding from generation.
- [ ] Compare text-only and multimodal capabilities explicitly.
- [ ] Explain VLMs and image representation concepts.
- [ ] Prepare supported image inputs and evaluate visual Q&A.
- [ ] Explain resolution, cropping, patches, and model-specific visual accounting.
- [ ] Extract and summarize mixed text/image documents with provenance.
- [ ] Explain audio inputs, speech recognition, synthesis, and general audio generation.
- [ ] Explain video understanding, frame sampling, and generation fundamentals.
- [ ] Construct mixed-modality prompts and validate structured outputs.
- [ ] Explain multimodal RAG and access boundaries.
- [ ] Complete an audio-service experiment or document its access limitation.
- [ ] Compare text-only and multimodal approaches using matched cases.
- [ ] Complete and review the multimodal comparison report.

## Scope and next step

This level introduces multimodal capabilities and practical application patterns. Detailed image generation belongs to Level 10; detailed audio, speech, and video generation to Level 11. Comprehensive evaluation, security, and deployment are expanded in Levels 13–15. Autonomous multimodal agents remain outside this course.

Next: **Level 10 — Image Generation with Diffusion Models**, or **Level 11 — Audio, Speech, and Video Generation** for an audio/video specialization. See the [main course outline](../README.md).
