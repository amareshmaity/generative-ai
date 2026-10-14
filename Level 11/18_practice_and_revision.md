# Chapter 18 — Practice and Revision

## 1. Chapter Objective

This chapter consolidates the Level 11 topics in audio, speech, and video generation. The goal is to compare task families, explain their representations and interfaces, demonstrate practical audio workflows, review the video-generation experiment, and make a defensible workflow recommendation.

The final recommendation must be based on observed quality, resource requirements, permitted use, and remaining limitations. Do not treat a planned experiment, a mock response, or an unmeasured expectation as a successful result.

<br/>

## 2. Learning Outcomes

By the end of this revision chapter, you should be able to:

- Distinguish recognition, synthesis, transformation, and generation tasks.
- Explain how audio and video representations affect processing and model interfaces.
- Describe timestamps, synchronization, streaming, buffering, and partial results.
- Demonstrate a transcription-to-summary workflow with evidence traceability.
- Demonstrate text-to-speech generation with a versioned script and permitted voice.
- Evaluate a video-generation experiment or document why a live run was unavailable.
- Compare quality, latency, compute, cost, and operational constraints.
- Recommend a workflow that is suitable for a concrete use case and explicitly state its limitations.

<br/>

## 3. Revision Map: Audio, Speech, and Video Tasks

| Task family    | Input                                          | Output                                               | Main objective                                      | Typical evaluation focus                              |
| -------------- | ---------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------- |
| Recognition    | Audio, speech, or video-derived signals        | Text, labels, timestamps, or structured observations | Infer what is present in the input                  | Recognition accuracy, omissions, timing, attribution  |
| Synthesis      | Text or structured controls                    | Generated speech or other media                      | Produce media that expresses the specified content  | Intelligibility, fidelity, naturalness, pronunciation |
| Transformation | Existing audio/video/media                     | Modified or converted media                          | Change a property while preserving intended content | Preservation, artifact rate, semantic consistency     |
| Generation     | Text, image, audio, or structured conditioning | New audio or video                                   | Create content conditioned on the supplied inputs   | Prompt adherence, coherence, quality, controllability |

These categories describe common objectives, not mutually exclusive model architectures. A system may combine recognition and generation, or transform an input while generating new segments. State the actual input-output contract when classifying a system.

<br/>

### Quick classification exercise

Classify each task and explain the primary evidence you would inspect:

1. Convert a meeting recording into timestamped words.
2. Generate narration from a fixed script.
3. Change the language of a spoken recording while preserving its intended message.
4. Generate a short scene from a text prompt.
5. Turn an input image into a moving clip.
6. Transcribe speech and summarize its key decisions.

Suggested answers:

- 1: Recognition (automatic speech recognition, ASR).
- 2: Synthesis (text-to-speech, TTS).
- 3: Transformation, usually involving recognition and synthesis stages.
- 4: Generation (text-to-video).
- 5: Conditional generation (image-to-video).
- 6: A pipeline combining recognition and evidence-grounded summarization.

<br/>

## 4. Representations and Model Interfaces

A model interface determines how the application supplies inputs, configures the task, receives results, and handles errors. The underlying representation determines how information is encoded for processing.

### Audio representations

Common representations include:

- **Waveform samples:** amplitude values indexed over time.
- **Spectrograms:** time-frequency representations derived from a signal.
- **Acoustic features:** compact features used by some recognition or synthesis systems.
- **Discrete audio tokens:** token sequences produced by a learned codec or tokenizer.
- **Text tokens:** a representation used for transcript or language-model processing.

These representations are not interchangeable without conversion. Sample rate, channel layout, tokenization, and model-specific preprocessing can affect compatibility and quality.

<br/>

### Video representations

A video is a temporally ordered sequence of frames, usually accompanied by timing information and optionally an audio stream. Important properties include:

- Frame dimensions and aspect ratio.
- Frame rate and presentation timestamps.
- Color format and codec.
- Clip duration.
- Audio stream presence and synchronization.
- Temporal relationships between frames.

A few extracted frames can help inspect a clip but cannot fully establish motion coherence. Watch the entire clip at normal speed as well.

<br/>

### Interface types

| Interface           | Typical behavior                           | Engineering concern                         |
| ------------------- | ------------------------------------------ | ------------------------------------------- |
| Request/response    | Submit input and receive output            | Payload validation, timeout, retries        |
| Asynchronous job    | Submit a job, poll status, retrieve result | State tracking, polling, cancellation       |
| Streaming           | Receive output in chunks or partial events | Buffering, ordering, incomplete results     |
| Local model runtime | Run model in a controlled environment      | Hardware, dependencies, memory, versioning  |
| Hosted API          | Call a remote service                      | Credentials, network, quotas, privacy, cost |

Do not assume that a feature is supported because it can be described in a prompt. Verify whether it is a documented parameter, a UI control, or merely a requested behavior.

<br/>

## 5. Synchronization, Timestamps, and Streaming

### Timestamp principles

- Preserve source timestamps when supplied.
- Identify whether timestamps refer to the original media or a cropped/transformed asset.
- Convert crop-relative times back to the original timeline using the crop offset.
- Keep segment order and allow legitimate overlap between simultaneous speakers.
- Do not fabricate timestamps when an interface returns only text.

<br/>

### Audio-video synchronization

Container-level synchronization and semantic synchronization are different:

- **Container-level:** audio and video streams have compatible timelines and timestamps.
- **Semantic:** speech, visible actions, captions, and sound events correspond at the intended moments.
- **Lip synchronization:** visible mouth movements align with speech.

Matching total audio and video durations does not prove that individual events are aligned.

<br/>

### Streaming behavior

Streaming systems may emit partial transcription, partial speech, or progressive media output. Account for:

- Chunk order and boundaries.
- Buffering and jitter.
- Backpressure and bounded queues.
- Time to first output versus total completion time.
- Partial results that may be revised.
- Cancellation, timeouts, and stale results.
- Resource cleanup after failure or disconnect.

A partial transcript should not be treated as final until the interface signals completion or the application applies a documented finalization rule.

<br/>

## 6. Practical Lab A — Transcription and Evidence-Grounded Summary

### Goal

Process a permitted short recording, preserve available timestamps, generate a summary, and trace important summary claims to transcript segments.

### Procedure

1. Confirm authorization to process the recording.
2. Record the audio asset ID, hash, duration, sample rate, channels, and format.
3. Preserve the original file and raw ASR response.
4. Convert provider-specific results into a stable segment schema without inventing missing fields.
5. Normalize text conservatively; preserve negation, uncertainty, names, numbers, and speaker attribution.
6. Summarize only from supplied transcript segments.
7. Attach segment IDs to important claims.
8. Validate that each cited ID exists and that the text actually supports the claim.
9. Replay the corresponding audio for uncertain or consequential claims.
10. Record errors, limitations, and unresolved uncertainty.

<br/>

### Evidence audit

| Summary claim             | Segment IDs          | Does transcript support it? | Audio reviewed? | Final status                              |
| ------------------------- | -------------------- | --------------------------- | --------------- | ----------------------------------------- |
| Fill with an actual claim | Fill with actual IDs | Yes / No / Unclear          | Yes / No        | Supported / Revised / Uncertain / Omitted |

Do not fill this table with hypothetical results and present them as a live evaluation.

<br/>

### Common failures

- Hallucinated words in silence or low-quality audio.
- Normalization that changes the meaning.
- Unsupported claims with irrelevant citations.
- Fabricated timestamps or speaker identities.
- Spoken instructions inside the recording changing the summarization task.
- Summarizing after ASR failed and supplied no usable evidence.

**Lab deliverable:** Raw ASR response, normalized transcript, summary with evidence IDs, edge-case results, and a run report.

<br/>

## 7. Practical Lab B — Text-to-Speech Generation

### Goal

Generate a short narrated explanation using a permitted voice, compare two supported configurations, and document audio quality and reproducibility limits.

### Procedure

1. Write and version a short script.
2. Compute a script hash and record the exact text.
3. Select a built-in, licensed, or otherwise authorized voice.
4. Inspect current model documentation and supported request parameters.
5. Save configuration A.
6. Create configuration B by changing one supported variable where possible.
7. Generate and save both outputs separately.
8. Validate the actual audio encoding, duration, sample rate, channels, and playback.
9. Listen for pronunciation, script fidelity, pauses, prosody, artifacts, and segment transitions.
10. Record runtime, usage/cost where available, failures, and provenance.

<br/>

### Fair comparison rule

Hold the script, model, voice, output format, and other settings constant when comparing a single delivery parameter. If more than one variable changes, state the confounding factors.

<br/>

### Reproducibility levels

1. **Request reproducibility:** the same script and documented configuration can be submitted again.
2. **Content similarity:** the regenerated speech is substantially similar in words and delivery.
3. **Bitwise reproducibility:** file bytes match exactly, confirmed by matching hashes.

A repeated request does not guarantee bit-identical audio. Hosted model updates, nondeterministic generation, voice assets, decoding, chunking, and metadata can affect the result.

**Lab deliverable:** Versioned script, two configurations, audio files, output metadata, comparison table, and experiment report.

<br/>

## 8. Practical Lab C — Video-Generation Experiment Review

### Goal

Review a bounded text-to-video or image-to-video experiment. If no live service was accessible, submit a documented request plan and evaluation design instead.

<br/>

### Procedure for a live run

1. Check current official documentation, model availability, terms, and account requirements.
2. Record the exact model ID and supported parameters.
3. Define one prompt and measurable success criteria.
4. Record prompt version and reference-image hash if applicable.
5. Submit one bounded request and preserve its request/job ID.
6. Track job status and errors.
7. Save the output and response metadata.
8. Validate the file, duration, resolution, frame rate, and playback.
9. Watch the clip at normal speed and inspect selected frames.
10. Score prompt adherence, temporal stability, motion coherence, and runtime using actual evidence.

<br/>

### If access is unavailable

- Record the exact missing prerequisite.
- Prepare a provider-specific request using current documentation.
- Validate the local manifest or mock control flow.
- Mark generation as `not_run` and quality as `not evaluated`.
- Do not invent a request ID, clip, runtime, cost, or score.

<br/>

### Video evaluation rubric

| Dimension          | Evidence to collect                                                 |
| ------------------ | ------------------------------------------------------------------- |
| Prompt adherence   | Requested subject, attributes, action, and setting                  |
| Temporal stability | Identity, geometry, textures, lighting, and background over time    |
| Motion coherence   | Plausible movement, object interactions, and camera behavior        |
| Start/end quality  | Abrupt cutoffs, blank frames, incomplete action                     |
| Technical validity | Decoding, duration, dimensions, frame rate, audio presence          |
| Runtime/resources  | Submission, queue, generation, download, usage/cost where available |

**Lab deliverable:** Actual clip and metadata, or a clearly labeled not-run plan, plus the completed evidence-based report.

<br/>

## 9. Quality and Resource Trade-offs

Do not collapse all quality dimensions into one score without explaining how it was constructed.

| Workflow             | Quality dimensions                                             | Resource/operational costs                                       | Typical limitation                                         |
| -------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| ASR + summarization  | Word accuracy, timestamps, evidence support, coverage          | ASR and LLM latency/cost; review time                            | Recognition errors can propagate into summaries            |
| TTS                  | Script fidelity, pronunciation, intelligibility, naturalness   | Generation latency, usage charges, output storage                | Natural prosody does not guarantee exact script fidelity   |
| Audio transformation | Content preservation, target transformation quality, artifacts | Model/runtime cost, input/output handling                        | May alter voice, timing, or non-target content             |
| Text-to-video        | Prompt adherence, motion, temporal stability                   | Often substantial generation time and compute/usage cost         | Requested details may be inconsistent across frames        |
| Image-to-video       | Reference preservation, motion, temporal stability             | Image preparation plus generation and review                     | Motion may distort reference identity or geometry          |
| Streaming media      | Time to first output, end-to-end latency, continuity           | Persistent connections, buffers, compute, operational complexity | Partial outputs may change or require cancellation/cleanup |

These are qualitative tendencies, not measured results for a particular model. Replace them with observed values from your experiments wherever possible.

<br/>

### Performance measures

- **WER:** $\mathrm{WER} = (S + D + I)/N$, using a documented reference and normalization policy.
- **TTS real-time factor:** generation wall-clock time divided by generated audio duration, where meaningful.
- **Latency:** measure stage boundaries and distinguish time to first output from total completion.
- **Usage/cost:** use provider-reported values when available; label calculations as estimates.
- **Review effort:** record human inspection time, especially for high-impact errors.

Do not compare systems using different scripts, prompts, assets, output settings, or evaluation rules without documenting the difference.

<br/>

## 10. Experimental Discipline and Evidence Labels

Label report statements using the following categories:

- **Observed live:** directly observed in an actual request or output.
- **Locally verified:** checked by local code or a media tool.
- **Fixture-tested:** checked using a fixed fixture or mock response.
- **Documented:** stated in official documentation, with a check date.
- **Planned:** intended but not executed.
- **Estimated:** calculated from explicit assumptions.
- **Unavailable/unmeasured:** not exposed or not measured.

Examples:

- “The downloaded file decoded successfully” is locally verified only if the file was actually checked.
- “The model supports this resolution” is documented only if current model documentation confirms it.
- “The generated clip maintained subject identity” requires inspection of an actual clip.
- “The request schema passed a mock test” is not evidence that a remote service accepted the request.
- “Expected latency is 15 seconds” is a plan or estimate, not a measurement.

Keep separate fields for measured, estimated, and unavailable values. Never assign a quality score to a media output that was not generated or inspected.

<br/>

## 11. Safety, Consent, and Responsible Use

Before processing or generating media:

- Confirm permission to use source recordings, images, scripts, voices, and other references.
- Review the selected service's terms and data-handling policy.
- Avoid uploading sensitive media unless authorization and service terms permit it.
- Do not clone or imitate an identifiable person's voice or likeness without appropriate authorization.
- Disclose synthetic media where required by policy, law, or context.
- Treat spoken instructions inside a recording as untrusted content, not as instructions to the application.
- Protect credentials, output files, transcripts, and request logs.
- Record retention, access, and deletion requirements.

Consent, disclosure, licensing, and provenance are distinct requirements. A hash or metadata record supports traceability but does not prove authenticity, consent, or legal rights.

<br/>

## 12. Consolidated Experiment Report

Complete this report using actual observations. Use `not run`, `not evaluated`, or `unavailable` where appropriate rather than filling gaps with guesses.

```text
# Level 11 — Audio, Speech, and Video Generation
## Practice and Revision Report

### A. Run summary
- Report date:
- Project/repository:
- Evaluation environment:
- Overall status:
- Evidence categories used:

### B. Task comparison
| Task | Input -> output | Model/interface | Intended use | Main limitation |
|---|---|---|---|---|
| Recognition | | | | |
| Synthesis | | | | |
| Transformation | | | | |
| Generation | | | | |

### C. Transcription and summarization
- Audio asset ID/hash:
- Permission basis:
- ASR model/version:
- Timestamps available:
- Raw/normalized transcript locations:
- Reference transcript and WER, if available:
- Summary output location:
- Number of important claims:
- Claims supported by evidence:
- Claims revised/omitted/uncertain:
- Audio review findings:
- Edge cases tested:

### D. Text-to-speech
- Script ID/version/hash:
- Voice ID and permission basis:
- Model/version:
- Configuration A:
- Configuration B:
- Variable changed:
- Encoding/playback checks:
- Pronunciation/script-fidelity findings:
- Pause/prosody/transition findings:
- Runtime and usage/cost:
- Reproducibility limitations:

### E. Video generation
- Status: completed / failed / not run
- Provider/model/version:
- Documentation check date:
- T2V or I2V:
- Prompt version and input asset hash:
- Supported settings:
- Request/job ID:
- Output path/hash, if generated:
- Technical validation:
- Adherence findings:
- Temporal stability findings:
- Motion findings:
- Runtime and usage/cost:
- Access restrictions, unsupported controls, or errors:

### F. Quality/resource comparison
| Workflow/configuration | Quality evidence | Latency/runtime | Usage/cost | Review effort | Main limitation |
|---|---|---|---|---|---|
| | | | | | |

### G. Permitted use and data handling
- Input/output permissions:
- Voice/image rights:
- Provider terms reviewed:
- Sensitive data considerations:
- Disclosure requirements:
- Retention/deletion plan:

### H. Recommendation
- Recommended workflow:
- Intended use:
- Evidence supporting the recommendation:
- Resource requirements:
- Permitted-use basis:
- Remaining limitations:
- Conditions that would change the recommendation:
- Next experiment:
```

<br/>

## 13. Final Practice Checklist

- [ ] Classify each task by input, output, and objective.
- [ ] Explain the relevant audio/video representation and interface.
- [ ] Explain timestamps, synchronization, and partial streaming results.
- [ ] Complete a transcription-to-summary run or document why it was not run.
- [ ] Trace important summary claims to transcript segments and, where needed, audio.
- [ ] Generate and review TTS audio with a permitted voice, or document the access limitation.
- [ ] Compare two supported TTS settings while controlling other variables.
- [ ] Review the video experiment or prepare a runnable request and evaluation plan.
- [ ] Separate live observations from local checks, fixtures, plans, estimates, and unavailable data.
- [ ] Compare quality and resource needs using explicit evidence.
- [ ] Record consent, permissions, provenance, and data-handling constraints.
- [ ] State the largest remaining limitation and the next useful experiment.

<br/>

## 14. Checkpoint: Recommend a Workflow

Choose a specific use case—for example, producing an accessible narration from a permitted script, summarizing a meeting recording, or prototyping a short generated clip. Then make a recommendation that answers:

1. **Quality:** What observed evidence shows that the workflow meets the required quality bar?
2. **Resources:** What latency, compute, storage, usage, cost, and review effort are required?
3. **Permitted use:** Are inputs, voices, references, outputs, and provider terms compatible with the intended use?
4. **Limitations:** What errors, unsupported controls, uncertainty, or reproducibility constraints remain?
5. **Alternatives:** What simpler or more controllable workflow could meet the same requirement?
6. **Decision boundary:** What new evidence would cause you to change the recommendation?

**Checkpoint standard:** Recommend a workflow using observed quality, resource needs, permitted uses, and remaining limitations. If the experiments were not run, present a provisional recommendation based on documented capabilities and clearly identify the missing evidence.

<br/>

## 15. Review Questions

1. How do recognition, synthesis, transformation, and generation differ?
2. Why are waveforms, spectrograms, and discrete audio tokens not interchangeable?
3. Why can a partial streaming transcript change before completion?
4. What is the difference between container synchronization and semantic synchronization?
5. How can ASR errors propagate into a generated summary?
6. Why must TTS script fidelity be evaluated separately from naturalness?
7. Which properties must be inspected over time in a generated video?
8. How should unavailable usage or runtime data be reported?
9. What evidence is needed to recommend a workflow for production use?
10. How should consent, permitted use, and data-handling constraints affect model selection?

<br/>

## 16. Essential References

- Hugging Face audio ASR task documentation: https://huggingface.co/docs/transformers/tasks/asr
- Hugging Face text-to-speech task documentation: https://huggingface.co/docs/transformers/tasks/text-to-speech
- OpenAI Speech-to-Text guide: https://platform.openai.com/docs/guides/speech-to-text
- OpenAI Text-to-Speech guide: https://platform.openai.com/docs/guides/text-to-speech
- Google Cloud Vertex AI generative AI documentation: https://cloud.google.com/vertex-ai/generative-ai/docs
- Hugging Face Diffusers documentation: https://huggingface.co/docs/diffusers/index
- FFmpeg documentation: https://ffmpeg.org/ffmpeg.html
- FFprobe documentation: https://ffmpeg.org/ffprobe.html

Verify current provider documentation, access, model availability, parameters, costs, and terms before executing a live experiment.
