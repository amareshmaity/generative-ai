# Chapter 13: Quality, Latency, and Compute Trade-offs

## Learning Objectives

By the end of this chapter, you should be able to:

- Choose quality metrics that match the media task rather than relying on a universal score.
- Calculate word error rate (WER) for reference-based automatic speech recognition (ASR) evaluation and explain its limitations.
- Evaluate speech intelligibility, pronunciation, naturalness, script fidelity, audio artifacts, video prompt adherence, continuity, and motion.
- Measure latency across preprocessing, upload, queueing, inference, download, and playback readiness where available.
- Explain real-time factor (RTF), time to first playable audio, and total processing time.
- Record hardware, memory, media duration, resolution, usage units, and cost assumptions.
- Compare two supported configurations on matched inputs without confusing estimates with observed measurements.

<br/>

## 1. Evaluation Starts with the Task

There is no single metric that adequately captures the quality of every audio or video workflow. A useful evaluation begins with the task's objective and failure costs.

Examples:

- **ASR/transcription:** Was the spoken content recognized correctly, including names, numbers, and domain terms?
- **Text-to-speech (TTS):** Is the speech intelligible, natural, correctly pronounced, and faithful to the script?
- **Audio-to-audio generation:** Does the output meet the intended transformation while avoiding artifacts?
- **Video generation:** Does the clip follow the prompt, maintain continuity, and produce plausible motion?
- **Streaming media:** Does the system meet its latency budget without unstable playback or excessive resource use?

A configuration may be faster but less accurate, more natural but more expensive, or visually appealing while failing the intended action. Report quality and operational measurements together.

<br/>

## 2. ASR Quality: Word Error Rate

**Word error rate (WER)** compares a hypothesis transcript with a reference transcript using word-level substitutions, deletions, and insertions.

$$
\mathrm{WER} = \frac{S + D + I}{N}
$$

Where:

- $S$: number of word substitutions.
- $D$: number of word deletions.
- $I$: number of word insertions.
- $N$: number of words in the reference transcript.

WER is often expressed as a fraction or percentage. Because insertions can make the numerator larger than the reference length, WER can exceed 100%.

<br/>

### Example

Reference:

> Turn left at the next street.

Hypothesis:

> Turn right at next street.

One word is substituted (`left` → `right`) and one word is deleted (`the`). There are no insertions. The reference has six words.

$$
\mathrm{WER} = \frac{1 + 1 + 0}{6} = 0.333\ldots \approx 33.3\%
$$

This is an illustrative calculation.

<br/>

### Basic Python implementation

```python
def word_error_rate(reference: str, hypothesis: str) -> float:
    """Compute WER using word-level Levenshtein distance."""
    ref = reference.strip().split()
    hyp = hypothesis.strip().split()

    if not ref:
        raise ValueError("Reference must contain at least one word.")

    # dp[i][j] = minimum edit operations for ref[:i] -> hyp[:j]
    dp = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]

    for i in range(len(ref) + 1):
        dp[i][0] = i
    for j in range(len(hyp) + 1):
        dp[0][j] = j

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            substitution_cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,                  # deletion
                dp[i][j - 1] + 1,                  # insertion
                dp[i - 1][j - 1] + substitution_cost,
            )

    edit_distance = dp[-1][-1]
    return edit_distance / len(ref)


reference = "Turn left at the next street."
hypothesis = "Turn right at next street."

# This simple example does not normalize punctuation/case.
print(word_error_rate(reference, hypothesis))
```

**Implementation caveat:** The function above uses whitespace tokenization and does not normalize case, punctuation, contractions, or language-specific word boundaries. Production evaluation should apply a documented, consistent normalization policy to both reference and hypothesis before scoring.

<br/>

### Limitations of WER

WER is useful, but it does not capture everything:

- Different mistakes have different consequences. Misrecognizing a person's name, medication, address, or negation can be more serious than an article error.
- It depends on the reference transcript and normalization rules.
- Word segmentation varies by language and writing system.
- A transcript with similar meaning can still score poorly if its wording differs.
- A transcript can have a low WER while omitting speaker labels, timestamps, punctuation, or required formatting.
- A score averaged over a dataset can hide poor performance for specific speakers, accents, environments, or domains.
- WER is not a direct measure of semantic correctness or downstream task success.

Use WER with targeted error review and, where relevant, metrics for character error rate, timestamps, diarization, or task-specific correctness.

<br/>

## 3. Speech Quality: Intelligibility, Pronunciation, Naturalness, and Fidelity

For TTS and generated speech, separate several dimensions.

### Intelligibility

Can a listener understand the words at normal playback volume and speed? Evaluate in realistic listening conditions, not only through a waveform or a technical status code.

<br/>

### Pronunciation

Are names, abbreviations, numbers, units, dates, and domain-specific terms spoken correctly? A voice can sound smooth but pronounce a critical name or number incorrectly.

<br/>

### Naturalness and prosody

Does speech have plausible rhythm, stress, intonation, pauses, and phrasing? Is the delivery suitable for the context? Naturalness is partly subjective, so use a consistent rubric and, when possible, multiple listeners.

<br/>

### Script fidelity

Does the generated audio preserve the required words, order, and content? It may omit a sentence, repeat a phrase, insert an unintended word, or alter a number. Compare the audio with the source script, using a verified transcript when needed.

<br/>

### Example rubric

| Dimension | 1 — Poor | 3 — Acceptable | 5 — Strong |
|---|---|---|---|
| Intelligibility | Frequently difficult to understand | Main content is understandable | Clear at normal listening level |
| Pronunciation | Critical errors or repeated mispronunciations | Minor errors; key terms correct | Key terms and wording are correct |
| Naturalness | Strongly robotic or awkward timing | Understandable with noticeable roughness | Natural rhythm and appropriate phrasing |
| Script fidelity | Major omissions or additions | Minor deviations | Required text is faithfully spoken |
| Artifacts | Severe clipping, clicks, distortion, or glitches | Occasional noticeable artifacts | No distracting artifacts detected |

For each rating, record an example or timestamp. If the application requires exact spoken text, script fidelity should be treated as a key acceptance criterion rather than traded away for a higher naturalness score.

<br/>

## 4. General Audio Quality and Artifacts

Depending on the task, inspect:

- Clipping or saturation.
- Clicks, pops, dropouts, or discontinuities.
- Background noise and unwanted ambience.
- Distortion or metallic/warbling artifacts.
- Abrupt changes in loudness or timbre.
- Unnatural pauses or repeated segments.
- Unwanted changes to source content in enhancement/transformation tasks.
- Excessive silence, truncated endings, or inconsistent channel layout.

A clean waveform does not necessarily sound natural, and a visually smooth waveform does not prove that speech is intelligible. Use listening tests alongside technical checks.

For transformations, define **preservation criteria**: what must remain unchanged, what may change, and which artifacts are unacceptable. For generated music or effects, evaluate whether the sound matches the prompt and whether transitions are clean.

<br/>

## 5. Video Quality: Adherence, Continuity, and Motion

Video evaluation should separate the requested content from how it evolves over time.

### Prompt adherence

Does the clip contain the requested subject, setting, action, framing, and visual style? Check whether important prompt requirements are missing or contradicted.

<br/>

### Temporal continuity

Does subject identity, geometry, texture, lighting, and background remain coherent across frames? Look for flicker, identity drift, disappearing objects, warping, and abrupt discontinuities.

<br/>

### Motion coherence

Are motion paths and interactions plausible? Does the camera behave as requested? Do subjects remain attached to objects they hold or ride? Does the action unfold in a readable sequence?

<br/>

### Technical validity

Check duration, dimensions, frame rate, encoding, and whether the output decodes correctly. Technical validity is necessary but not sufficient for creative quality.

<br/>

### Video review rubric

| Dimension | What to record |
|---|---|
| Prompt adherence | Required elements present/missing; timestamped evidence |
| Identity and geometry | Whether subjects and objects remain stable |
| Motion | Plausibility, continuity, interaction failures |
| Camera behavior | Match to requested movement and framing |
| Artifacts | Flicker, warping, object changes, visual glitches |
| Technical validity | Duration, dimensions, frame rate, codec/container, decode success |

Use timestamped observations rather than relying only on an overall impression. A few attractive frames do not establish that the full sequence is coherent.

<br/>

## 6. Measure Latency by Stage

Total processing time alone can hide the stage responsible for delay. Where instrumentation allows, record:

1. **Preprocessing:** decoding, resampling, resizing, chunking, or normalization.
2. **Upload/transport:** sending media and receiving acknowledgements.
3. **Queueing:** waiting for provider or local worker capacity.
4. **Inference/generation:** model execution.
5. **Download/retrieval:** fetching output media or result payloads.
6. **Postprocessing:** decoding, conversion, normalization, muxing, or validation.
7. **Playback readiness:** time until the first usable audio segment or complete media file can play.
8. **End-to-end completion:** total elapsed time from the declared start point to the declared completion condition.

Use a consistent start/end definition. For an uploaded video-generation job, “request start” might mean local submission start, while “output ready” might mean a fully downloaded, decodable file. For streaming TTS, the first playable chunk may be useful long before the entire response is complete.

<br/>

### Timing diagram

```mermaid
flowchart LR
    A[Preprocess] --> B[Upload]
    B --> C[Queue]
    C --> D[Inference]
    D --> E[Download]
    E --> F[Postprocess]
    F --> G[Playback ready]
```

Not every architecture has every stage. Some hosted APIs hide queueing or internal inference timing; mark those components as unavailable instead of guessing.

<br/>

### Instrumentation example

```python
from time import perf_counter

def timed_step(label, function, *args, **kwargs):
    start = perf_counter()
    result = function(*args, **kwargs)
    elapsed = perf_counter() - start
    print(f"{label}: {elapsed:.3f} seconds")
    return result, elapsed

# Example usage with your own functions:
# preprocessed, t_pre = timed_step("preprocessing", preprocess, input_media)
# response, t_submit = timed_step("submission", submit_request, preprocessed)
# output, t_download = timed_step("download", download_output, response)
```

This helper measures elapsed time around the function calls supplied to it. If a function returns immediately with a job ID, the measurement is submission latency—not the full remote generation time. Measure polling/queueing and completion separately where observable.

<br/>

## 7. Real-Time Factor and Audio Responsiveness

### Real-time factor (RTF)

For an audio processing task, a common definition is:

$$
\mathrm{RTF} = \frac{\text{processing time}}{\text{audio duration}}
$$

Under this convention:
- RTF below 1 means processing took less time than the audio duration.
- RTF equal to 1 means processing time equaled audio duration.
- RTF above 1 means processing took longer than the audio duration.

Always state the convention. Some reports use a reciprocal speed factor, so values must not be compared without checking definitions.

Example: processing 30 seconds of audio in 6 seconds gives:

$$
\mathrm{RTF} = \frac{6}{30} = 0.2
$$

This is an illustrative calculation, not a benchmark.

RTF is useful for offline ASR, enhancement, and TTS comparisons, but it does not fully describe streaming responsiveness. A streaming system can have a good overall RTF but poor time to first output because it buffers too much before starting.

<br/>

### Time to first playable audio

**Time to first playable audio** measures elapsed time from a declared request/speech start to the moment the first audio segment is ready for playback. Define whether the endpoint is the provider's first chunk, a locally decoded chunk, or audio actually scheduled for playback.

<br/>

### Total processing time

Total processing time should be defined for the workflow. It may end at final transcript availability, complete generated-file download, validated media readiness, or another task-specific milestone.

Do not compare an RTF measured on a complete offline file with a first-chunk latency measured in a streaming system as if they were the same metric.

<br/>

## 8. Compute, Hardware, Memory, and Cost

Quality and latency results are meaningful only when the workload and execution conditions are recorded.

### Record the environment

- Hardware: CPU model/cores, GPU model, accelerator, or hosted provider.
- Software: OS, runtime, library and model versions.
- Memory: peak RAM and, when applicable, peak GPU/accelerator memory.
- Media: duration, sample rate/channels for audio, dimensions/frame rate for video.
- Configuration: model, quality mode, chunk size, batch size, resolution, seed or other supported settings.
- Usage: provider-defined units such as input/output tokens, audio seconds, generated seconds, frames, or credits.
- Cost assumptions: rate card/date, billed units, retries, storage, and data transfer where applicable.

For hosted services, the provider may not expose its underlying hardware or queue time. Record those as **not disclosed/not observable**, not as zero.

<br/>

### Cost estimate vs. actual cost

A simple estimate may be expressed as:

$$
\text{estimated cost} = \sum_i (\text{estimated billable units}_i \times \text{unit price}_i)
$$

This estimate depends on the applicable pricing schedule, rounding rules, free allowances, retries, and other billable components. Record the pricing source and date. A dashboard or invoice is stronger evidence of actual billed cost than a calculation based on assumed usage.

<br/>

### Resource-efficiency measures

Depending on the workload, report:
- Processing seconds per media second.
- Peak memory.
- Generated media seconds per wall-clock minute.
- Time to first playable output.
- Cost per processed or generated media minute.
- Quality score at a fixed latency/cost budget.

Do not use a metric just because it is easy to measure. Select measures that reflect the application's constraint.

<br/>

## 9. Fair Comparison of Two Configurations

A meaningful comparison controls the input and clearly identifies what changed.

### Match the workload

Hold constant where practical:
- Input media and reference transcript/prompt.
- Input duration and preprocessing.
- Evaluation rubric and normalization policy.
- Output requirements and success criteria.
- Hardware or hosted environment, unless environment is the variable being tested.
- Warm-up policy and number of repetitions.
- Measurement start/end definitions.

Change one major configuration variable at a time when diagnosing its effect. If several variables change, describe the result as a configuration comparison rather than attributing the outcome to one factor.

<br/>

### Repeat measurements

Latency varies due to queueing, network conditions, warm-up, and system load. For small experiments, report each run or at least the number of runs and a summary such as median and range. Do not hide large outliers behind a single mean.

For subjective audio/video quality, use the same rubric and ideally more than one evaluator. Keep qualitative observations alongside numeric scores.

<br/>

### Separate observation from estimate

Label results clearly:

- **Measured:** observed from an actual run with recorded start/end points.
- **Calculated:** derived from measured values using a stated formula.
- **Estimated:** predicted from assumptions, pricing, or prior measurements.
- **Planned:** a proposed experiment that has not been run.
- **Unavailable:** the service does not expose the required measurement.

Never present an estimate, a placeholder, or an illustrative example as an observation.

<br/>

## 10. Practice: Compare Two Supported Configurations

Choose one task and compare two configurations supported by the same model or service, where possible.

Possible examples:
- ASR with two supported decoding/configuration choices.
- TTS with two supported voice or quality settings.
- Video generation at two supported resolutions or durations.
- Streaming audio with two supported chunk sizes.

Do not compare unlike tasks, such as one configuration processing a short audio file offline and another producing a long video asynchronously, then infer a universal winner.

<br/>

### Procedure

1. Define the task and the quality dimension that matters most.
2. Select two valid configurations from the actual endpoint or model documentation.
3. Use matched input media and identical evaluation rules.
4. Record all configuration settings and environment details.
5. Measure available stages: preprocessing, upload, queueing, inference, download, and playback readiness.
6. Measure the relevant quality dimensions.
7. Repeat runs if feasible; report run count and variability.
8. Calculate derived metrics such as WER, RTF, or cost per media minute using documented formulas.
9. Identify trade-offs and limitations.
10. Recommend a configuration for a stated use case—not as a universal winner.

<br/>

### Comparison report template

| Field | Configuration A | Configuration B |
|---|---|---|
| Task/model/version | | |
| Explicit settings | | |
| Input duration and format | | |
| Hardware/provider | | |
| Preprocessing time | | |
| Upload time | | |
| Queue time | | |
| Inference/generation time | | |
| Download/postprocessing time | | |
| Time to first playable output | | |
| Total elapsed time | | |
| Quality metrics | | |
| Peak memory | | |
| Usage units | | |
| Estimated or actual cost | | |
| Run count / variability | | |
| Observed failure modes | | |

Below the table, write:
- What improved?
- What regressed?
- Which metrics were unavailable?
- What assumptions limit the conclusion?
- Which configuration is preferable for the intended workload, and why?

<br/>

## 11. Checkpoint: Choose Task-Appropriate Metrics

A metric is useful only if it measures a property relevant to the task.

Examples:
- Use WER for reference-based ASR, while also checking critical entities and transcript formatting.
- Use intelligibility, pronunciation, naturalness, script fidelity, and artifact review for TTS.
- Use prompt adherence, temporal consistency, motion coherence, and technical validity for generated video.
- Use time to first playable audio and end-to-end latency for interactive speech.
- Use RTF for processing speed relative to audio duration, with the definition stated.
- Use memory and cost measures when resource limits or unit economics are part of the decision.

<br/>

### Checkpoint answer template

> I selected metrics based on the task's success criteria. For ASR, I used a normalized reference-based error metric and inspected consequential errors; for speech generation, I evaluated intelligibility, pronunciation, naturalness, script fidelity, and artifacts; for video, I reviewed prompt adherence, temporal continuity, and motion. I measured latency by stage where observable, stated the RTF convention, and recorded hardware, media properties, usage, and cost assumptions. The recommendation reflects matched inputs and observed trade-offs, not one universal media-quality score.

Adapt the answer to the task you actually tested.

<br/>

## 12. Review Questions and Answers

**1. What does WER measure?**  
It measures word-level edit errors—substitutions, deletions, and insertions—relative to the number of words in a reference transcript.

**2. Can WER exceed 100%?**  
Yes. The number of insertions and other edit operations can exceed the reference word count.

**3. Why is WER not enough to evaluate ASR?**  
It depends on reference and normalization rules, treats many errors equally, and does not fully measure semantics, timestamps, speaker attribution, formatting, or downstream consequences.

**4. How do intelligibility and naturalness differ?**  
Intelligibility is whether listeners can understand the words. Naturalness concerns how plausible and appropriate the speech sounds.

**5. What is RTF under the convention used here?**  
Processing time divided by media duration. Below 1 means processing is faster than the media's duration, under this definition.

**6. Why measure time to first playable audio separately from total processing time?**  
Streaming applications may provide useful audio before the full output is complete. Total time alone hides how quickly the user receives the first usable result.

**7. Why record hardware, duration, and resolution?**  
These factors influence resource use and latency, so results cannot be interpreted or reproduced fairly without them.

**8. What is the difference between an estimated cost and actual cost?**  
An estimate applies assumptions and a price schedule to expected units. Actual cost comes from observed billing/usage records.

**9. How can two configurations be compared fairly?**  
Use matched inputs, documented settings, consistent metrics and timing definitions, and comparable environments; repeat runs where practical and disclose unavailable measurements.

<br/>

## 13. Further Reading

- [Word Error Rate — Hugging Face Evaluate](https://huggingface.co/spaces/evaluate-metric/wer) — overview and implementation of WER.
- [Hugging Face Evaluate documentation](https://huggingface.co/docs/evaluate/index) — evaluation workflows and metric usage.
- [FFmpeg documentation](https://ffmpeg.org/documentation.html) — media inspection and processing.
- [FFprobe documentation](https://ffmpeg.org/ffprobe.html) — stream and container metadata.
- [OpenAI API documentation](https://platform.openai.com/docs/overview) — verify current model interfaces, usage units, and supported controls.
- [NIST Speech Recognition evaluations](https://www.nist.gov/itl/iad/mig/speech-recognition) — speech recognition evaluation context.

Check current API capabilities and pricing before running a comparison. Documentation and rate cards can change.


<br/>


## Chapter Summary

- Choose metrics according to the task; no single media-quality score captures every requirement.
- WER quantifies reference-based ASR edit errors but has important normalization and consequence-related limitations.
- Evaluate generated speech across intelligibility, pronunciation, naturalness, script fidelity, and artifacts.
- Evaluate video across prompt adherence, temporal continuity, motion coherence, and technical validity.
- Measure latency by stage where possible, and distinguish RTF, time to first playable audio, and total processing time.
- Record hardware, memory, media duration/resolution, usage units, and cost assumptions.
- Compare matched workloads and label every result as measured, calculated, estimated, planned, or unavailable.
