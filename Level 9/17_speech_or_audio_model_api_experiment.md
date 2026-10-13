# Chapter 17: Speech or Audio Model API Experiment

## Learning Objectives

By the end of this chapter, you should be able to:

- Select one transcription, speech-synthesis, or audio-understanding API.
- Verify current input formats, request limits, usage metadata, and data-handling rules.
- Run a bounded experiment using a public, synthetic, or consented sample.
- Validate returned text, metadata, or generated audio files.
- Handle unsupported inputs, service errors, timeouts, and malformed responses.
- Measure task-specific quality and processing time, and record cost where available.
- Distinguish observed service results from prepared fixtures and estimated performance.

<br/>

## 1. Experiment Scope

This chapter is an implementation exercise, not a survey of every audio API. Choose **one** task and complete it end to end.

| Experiment type | Input | Output | Example evaluation |
|---|---|---|---|
| Speech recognition / transcription | Short speech recording | Text transcript, possibly timestamps or other metadata | Word error rate, critical-term accuracy, latency |
| Speech synthesis / text-to-speech | Text | Audio file or audio stream | Intelligibility, pronunciation, naturalness, duration, latency |
| Audio understanding | Short audio clip plus a question or task | Text answer or structured interpretation | Task correctness, evidence support, uncertainty, latency |

Choose the task that best matches the available account, endpoint, and project goal. Do not attempt to compare multiple model families before completing one reproducible baseline.

<br/>

### Deliverables

1. A documented API and model selection.
2. A short input sample and recorded input metadata.
3. A working request or a clearly labeled fixture-based integration test.
4. Validated output text, metadata, or audio.
5. A test report with quality, latency, errors, and cost information where available.
6. A statement of what was measured and what remains unmeasured.

<br/>

## 2. Verify the Current API Contract First

Before writing the request, consult the current official documentation for the chosen service, model, and endpoint. Record the verification date because formats, limits, model identifiers, and pricing can change.

Verify the following:

- Supported input file types and codecs.
- Sample-rate and channel requirements, if specified.
- Maximum file size, duration, or request payload.
- Whether the endpoint accepts file uploads, URLs, streams, or encoded data.
- Required parameters and supported response formats.
- Returned metadata and usage fields.
- Timeout, retry, and error behavior.
- Current pricing and the unit used for billing.
- Data retention, training-use, privacy, and regional or contractual requirements that apply to the account.

Do not infer the API contract from a tutorial or a response produced by a different model. If a detail is not documented, mark it as unverified rather than inventing a limit.

<br/>

### Experiment configuration record

```yaml
experiment_id: audio-api-001
task: transcription  # transcription, synthesis, or audio_understanding
provider: fill_in
endpoint: fill_in
model_id: fill_in
documentation_checked_on: YYYY-MM-DD
input_format: fill_in
input_duration_seconds: fill_in
input_size_bytes: fill_in
request_settings: {}
expected_output: fill_in
data_authorization: public_synthetic_or_consented
```

This is a template. Replace every `fill_in` value and use the actual date before treating the experiment as reproducible.

<br/>

## 3. Choose a Safe, Bounded Sample

Use a short public, synthetic, or properly consented sample. Do not upload private conversations, sensitive recordings, or someone else's voice without appropriate authorization.

### For transcription

Use a short clip with a known reference transcript. Include ordinary speech and, if relevant to your task, a small number of names, numbers, or domain-specific terms.

<br/>

### For speech synthesis

Use a short text sample that includes punctuation and one or two pronunciation challenges. Avoid imitating a real person's voice unless the use is authorized and supported by the applicable policy.

<br/>

### For audio understanding

Choose a clip with a narrow, answerable question—for example, whether a clearly audible doorbell occurs, or what phrase is spoken in a short synthetic recording. Record what evidence should support the answer.

<br/>

### Record input properties

- File name or safe sample ID.
- Actual decoded format, not just the filename extension.
- File size and duration.
- Sample rate and channel count where applicable.
- Source and authorization status.
- Reference transcript, expected audio properties, or expected answer.
- Any preprocessing or conversion applied.

<br/>

## 4. Inspect Audio Files Locally

For common local formats, `soundfile` and NumPy can inspect metadata and signal values. The library may not support every codec; use a suitable decoder such as FFmpeg when necessary and permitted.

Install the dependencies:

```bash
pip install soundfile numpy
```

Inspect a supported audio file:

```python
from pathlib import Path
import soundfile as sf
import numpy as np

def inspect_audio(path: str) -> dict:
    audio_path = Path(path)
    if not audio_path.is_file():
        raise FileNotFoundError("Audio file does not exist.")

    info = sf.info(str(audio_path))
    audio, sample_rate = sf.read(str(audio_path), always_2d=True)

    duration_seconds = len(audio) / sample_rate
    peak_amplitude = float(np.max(np.abs(audio))) if audio.size else 0.0
    rms_amplitude = float(np.sqrt(np.mean(audio ** 2))) if audio.size else 0.0

    return {
        "format": info.format,
        "subtype": info.subtype,
        "sample_rate_hz": sample_rate,
        "channels": audio.shape[1],
        "frames": len(audio),
        "duration_seconds": round(duration_seconds, 3),
        "file_size_bytes": audio_path.stat().st_size,
        "peak_amplitude": round(peak_amplitude, 5),
        "rms_amplitude": round(rms_amplitude, 5),
    }
```

A successful metadata read does not prove that the audio is intelligible or accepted by the target API. Validate the file against the endpoint's documented requirements.

<br/>

## 5. Example Experiment A: Speech Recognition

The following is an illustrative OpenAI Python SDK example for a transcription endpoint. Confirm the current endpoint syntax, available model identifiers, accepted file formats, and response options in the official documentation before running it.

### Install and configure

```bash
pip install openai soundfile numpy
```

Set the API key through an environment variable rather than storing it in source code.

**Windows PowerShell**

```powershell
$env:OPENAI_API_KEY = "your_api_key"
```

**macOS/Linux**

```bash
export OPENAI_API_KEY="your_api_key"
```

<br/>

### Submit a short recording

```python
from pathlib import Path
from openai import OpenAI
import os
import time

client = OpenAI()

def transcribe_audio(audio_path: str, model_id: str) -> dict:
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError("Audio file does not exist.")

    started = time.perf_counter()
    with path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(
            model=model_id,
            file=audio_file,
        )
    elapsed = time.perf_counter() - started

    transcript = getattr(result, "text", None)
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("The transcription response contained no usable text.")

    usage = getattr(result, "usage", None)
    return {
        "model_id": model_id,
        "transcript": transcript,
        "elapsed_seconds": round(elapsed, 3),
        "usage": usage,
    }

# Supply a model ID documented for your account and endpoint.
# result = transcribe_audio("samples/consented_clip.wav", "your_transcription_model")
# print(result)
```

This example records client-observed elapsed time, including network and service time from the client's perspective. It is not a pure measurement of provider compute time. If the endpoint returns usage metadata, preserve it; do not assume every endpoint returns the same fields.

Official reference: [OpenAI audio guide](https://platform.openai.com/docs/guides/audio)

<br/>

### Evaluate the transcript

For a known reference transcript, word error rate (WER) is a common metric:

$
\mathrm{WER} = \frac{S + D + I}{N}
$

Where:

- $S$ = substitutions.
- $D$ = deletions.
- $I$ = insertions.
- $N$ = number of words in the reference transcript.

Install an evaluation library:

```bash
pip install jiwer
```

```python
from jiwer import wer

reference = "turn left at the next street"
hypothesis = "turn left at next street"

print("WER:", wer(reference, hypothesis))
```

WER can exceed 1.0 when insertions are numerous. It also treats all words equally, so review critical names, numbers, dates, and domain-specific terms separately. Normalize text consistently before comparison, and document any normalization rules.

<br/>

## 6. Example Experiment B: Speech Synthesis

Use this path if speech generation is more relevant than transcription. The exact model, voice options, output format, and streaming behavior depend on the current endpoint contract.

Illustrative SDK pattern:

```python
from pathlib import Path
from openai import OpenAI
import time

client = OpenAI()

def synthesize_speech(
    text: str,
    model_id: str,
    voice: str,
    output_path: str,
) -> dict:
    if not text.strip():
        raise ValueError("Text must not be empty.")

    started = time.perf_counter()
    response = client.audio.speech.create(
        model=model_id,
        voice=voice,
        input=text,
    )
    elapsed = time.perf_counter() - started

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    response.stream_to_file(target)

    if not target.is_file() or target.stat().st_size == 0:
        raise ValueError("Generated audio file is missing or empty.")

    return {
        "model_id": model_id,
        "voice": voice,
        "output_path": str(target),
        "output_size_bytes": target.stat().st_size,
        "elapsed_seconds": round(elapsed, 3),
    }

# Use only model and voice values supported by current documentation.
# result = synthesize_speech(
#     "Please check the package number before dispatch.",
#     "your_tts_model",
#     "documented_voice",
#     "outputs/generated_speech.mp3",
# )
# print(result)
```

Do not assume that a file extension proves the generated file's actual encoding. Validate the output by decoding it with an appropriate audio library or media tool. If the response object or streaming method differs in the installed SDK version, follow the current SDK reference rather than forcing this illustrative code to work unchanged.

Evaluate synthesis using a short listening review and, where relevant, intelligibility, pronunciation, clipping, duration, and format checks. A successful API response does not prove naturalness or correct pronunciation.

<br/>

## 7. Example Experiment C: Audio Understanding

Audio-understanding APIs differ significantly in whether they accept audio directly, use transcription as an intermediate step, or support real-time audio streams. Verify the selected endpoint's contract before implementing this variant.

A bounded test should define:

- One audio clip.
- One narrow question or task.
- Expected evidence in the clip.
- What counts as a correct answer.
- How uncertainty should be handled.
- Whether the model's answer can be independently checked.

For example, use a synthetic clip containing a clear, short spoken phrase and ask the system to identify the phrase. Do not use a broad question such as “Explain everything in this recording” for the first experiment.

If the chosen API does not support the desired direct audio input, a documented transcription-plus-text-analysis workflow can be used instead. Label it as a two-stage pipeline; do not report it as native audio understanding.

<br/>

## 8. Validate Responses and Handle Failures

Treat API responses and generated files as untrusted external outputs. Validate them before downstream use.

### Request and response failure cases

- Missing input file.
- Unsupported codec or format.
- File too large or too long for the documented endpoint.
- Empty or silent input.
- Network timeout or connection failure.
- Authentication or permission failure.
- Rate limit or quota error.
- Server-side error.
- Empty, truncated, or unexpected response.
- Generated file missing, empty, or undecodable.

<br/>

### Defensive wrapper pattern

```python
def run_experiment_safely(experiment_fn, *args, **kwargs):
    try:
        result = experiment_fn(*args, **kwargs)
        return {
            "status": "success",
            "result": result,
            "error_type": None,
        }
    except FileNotFoundError as exc:
        return {
            "status": "input_error",
            "result": None,
            "error_type": type(exc).__name__,
        }
    except ValueError as exc:
        return {
            "status": "validation_error",
            "result": None,
            "error_type": type(exc).__name__,
        }
    except Exception as exc:
        # In a real application, classify known SDK/network exceptions
        # and avoid returning raw exception text to untrusted users.
        return {
            "status": "service_or_unexpected_error",
            "result": None,
            "error_type": type(exc).__name__,
        }
```

This wrapper demonstrates error categorization, not complete retry logic. In a real integration, handle known SDK exceptions explicitly, distinguish retryable from non-retryable failures, use bounded retries with backoff when appropriate, and avoid retrying invalid requests indefinitely. Do not log credentials, raw audio, or sensitive transcript text in error messages.

<br/>

## 9. Measure Quality, Time, Usage, and Cost

A small experiment should record both the task result and the operational behavior.

### Core measurements

| Dimension | Transcription | Synthesis | Audio understanding |
|---|---|---|---|
| Task quality | WER, critical-term accuracy | Pronunciation, intelligibility, clipping | Correctness, evidence support, uncertainty |
| Input validation | Format, duration, sample rate | Text validity and request settings | Format and task compatibility |
| Processing time | Client-observed elapsed time | Client-observed elapsed time | Client-observed elapsed time |
| Output validation | Transcript type and presence | File existence, size, decodability | Response schema and evidence |
| Usage | Provider-reported units where available | Provider-reported units where available | Provider-reported units where available |
| Cost | Verified rate × applicable usage | Verified rate × applicable usage | Verified rate × applicable usage |
| Failure rate | Errors / total attempts | Errors / total attempts | Errors / total attempts |

<br/>

### Cost-reporting rules

- Read the current pricing page for the exact endpoint and model.
- Capture actual usage metadata if the service returns it.
- Label estimates clearly when usage is not reported.
- Record the pricing date and billing unit.
- Include relevant preprocessing, storage, transfer, and review costs if estimating end-to-end cost.
- Do not infer provider compute time from client-observed elapsed time.

If pricing or usage is unavailable, record **“not observed”** or **“not available from this response”** instead of inventing a number.

<br/>

## 10. If API Access Is Unavailable: Use Fixtures Honestly

A fixture is a prepared example response used to test application integration without calling the real service. Fixtures are useful for validating parsers, schemas, file handling, and downstream logic.

Example fixture:

```python
TRANSCRIPTION_FIXTURE = {
    "text": "The package will arrive on Friday.",
    "source": "prepared_fixture",
    "usage": None,
}
```

Use a clear source label when passing it through your pipeline:

```python
def validate_transcription_result(result: dict) -> dict:
    text = result.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Missing transcript text.")

    source = result.get("source")
    if source not in {"live_service", "prepared_fixture"}:
        raise ValueError("Result source must be identified.")

    return {
        "text": text,
        "source": source,
        "usage": result.get("usage"),
    }

checked = validate_transcription_result(TRANSCRIPTION_FIXTURE)
print(checked)
```

**A fixture does not measure model quality, real service latency, actual usage, or live-service reliability.** It tests only the application behavior exercised by the prepared example. Keep these categories separate in the final report:

- **Observed service result:** produced by a real API request.
- **Prepared fixture:** supplied by the developer for integration testing.
- **Estimated performance:** a forecast based on assumptions or external measurements.

Do not present a fixture transcript as a live transcription result.

<br/>

## 11. Experiment Report Template

Complete this report after the experiment.

### Setup

- **Experiment ID:**
- **Task selected:**
- **Provider, endpoint, and model ID:**
- **Documentation checked on:**
- **Input sample ID and authorization:**
- **Input format, duration, size, sample rate, channels:**
- **Preprocessing and conversion:**
- **Request settings:**

<br/>

### Results

- **Result source:** live service / prepared fixture
- **Observed output or safe summary:**
- **Expected output:**
- **Quality metric and result:**
- **Critical errors or uncertainty cases:**
- **Client-observed elapsed time:**
- **Provider-reported usage:**
- **Cost:** measured / estimated / unavailable
- **Error handling tested:**
- **Output validation result:**

<br/>

### Interpretation

- **What was directly observed?**
- **What was supplied by a fixture?**
- **What was estimated?**
- **What remains unmeasured?**
- **Largest limitation:**
- **Next experiment:**

<br/>

## 12. Revision Questions and Answers

**1. Why verify the current API contract before coding?**  
Supported formats, model IDs, request limits, response fields, and pricing can change. The current documentation is the appropriate basis for implementation.

**2. What does client-observed elapsed time measure?**  
It measures the time between the client starting and finishing the operation, including network and service delays and possibly local file handling. It is not a direct measurement of provider compute time.

**3. Why validate a generated audio file after a successful response?**  
A successful request does not guarantee that the file exists, is non-empty, has the expected encoding, or can be decoded and played.

**4. Why is WER not enough for evaluating transcription?**  
WER treats words uniformly and may understate the impact of errors in names, numbers, dates, or safety-critical terms. Review those terms separately.

**5. What can a fixture-based test establish?**  
It can test input handling, response parsing, validation, and downstream integration for the supplied example. It cannot establish live model quality, real latency, usage, or reliability.

**6. How should cost be reported when the API does not return usage metadata?**  
Use a documented and clearly labeled estimate if sufficient information is available, or report the cost as unavailable. Never label an estimate as measured usage.

**7. Why use a short public, synthetic, or consented sample?**  
It limits exposure and makes the experiment easier to reproduce while respecting the rights and privacy of people whose speech may be recorded.

<br/>

## 13. Completion Checklist

- [ ] Select one transcription, synthesis, or audio-understanding task.
- [ ] Verify current formats, limits, response fields, pricing, and data-handling rules.
- [ ] Use a short public, synthetic, or consented sample.
- [ ] Record the sample's actual audio metadata.
- [ ] Run a live API request or clearly labeled fixture test.
- [ ] Validate the response or generated file.
- [ ] Test at least one failure path.
- [ ] Measure task-specific quality and client-observed processing time where possible.
- [ ] Record usage and cost as measured, estimated, or unavailable.
- [ ] State what remains unmeasured.

<br/>

## Checkpoint

**Distinguish observed service results from prepared examples and estimated performance.**

A live API response is an observed service result for that request. A fixture is a prepared example used to test application integration. An estimate is a forecast based on stated assumptions. Keep these categories separate in logs and reports. If API access is unavailable, document what the fixture test validates and explicitly state that real model quality, latency, usage, and reliability remain unmeasured.

<br/>

## Further Reading

Use the current official documentation for the exact endpoint, model, and SDK version selected.

- [OpenAI audio guide](https://platform.openai.com/docs/guides/audio)
- [OpenAI API reference](https://platform.openai.com/docs/api-reference)
- [OpenAI API pricing](https://openai.com/api/pricing/)
- [SoundFile documentation](https://python-soundfile.readthedocs.io/)
- [NumPy documentation](https://numpy.org/doc/)
- [JiWER documentation](https://jitsi.github.io/jiwer/)
