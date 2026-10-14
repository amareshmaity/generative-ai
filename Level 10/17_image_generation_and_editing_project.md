# Chapter 17: Image Generation and Editing Project

## Learning Objectives

By the end of this chapter, you should be able to:

- Build a reproducible image-generation and editing workflow as a notebook, command-line tool, or small application.
- Generate text-to-image samples and compare prompts and settings systematically.
- Add an image-to-image or inpainting task using permitted reference inputs.
- Save outputs alongside configurations, validation results, and error records.
- Build a comparison gallery that includes quality observations, runtime, and hardware details.
- Explain observed failures and document the resource requirements of the selected workflow.

<br/>

## 1. Project Overview

The goal is to build a small but auditable image-generation application. It should demonstrate both **creative generation** and **image editing**, while retaining enough information to reproduce or investigate each result.

Choose one implementation format:

- **Notebook:** useful for experimentation, visual inspection, and charts.
- **Command-line workflow:** useful for repeatable runs, automation, and batch generation.
- **Small application:** useful when users need an interface for prompts, reference images, settings, and result review.

Keep the first version small. A working workflow with recorded settings and known limitations is more valuable than a large application that cannot be reproduced.

<br/>

### 1.1 Required capabilities

1. Generate text-to-image outputs.
2. Compare at least two prompt or configuration variants.
3. Perform one image-to-image edit or inpainting task.
4. Save images, manifests, validation records, and errors.
5. Produce a comparison gallery.
6. Record runtime, memory where measurable, and hardware/software configuration.
7. Document limitations, permissions, and safety considerations.

<br/>

### 1.2 Suggested project structure

```text
image-generation-project/
├── README.md
├── requirements.txt
├── config/
│   └── experiment.yaml
├── inputs/
│   ├── references/
│   └── masks/
├── outputs/
│   ├── generated/
│   ├── edited/
│   ├── gallery/
│   └── manifests/
├── reports/
│   ├── experiment_summary.md
│   └── resource_report.csv
├── src/
│   ├── generate.py
│   ├── edit.py
│   ├── validate.py
│   └── gallery.py
└── tests/
    └── test_validation.py
```

This is a suggested layout, not a required framework. A notebook-first project may keep equivalent sections in one notebook, but should still save outputs and manifests in a consistent structure.

<br/>

## 2. Define the Task Before Choosing the Model

Write a short task specification before implementation.

Example:
- **Creative task:** Generate a misty forest scene containing a white owl perched on a branch.
- **Editing task:** Change the background of a permitted reference image while preserving the main subject.
- **Success criteria:** The required subject and setting are present; major artifacts are absent; the edit affects the intended region; output files and settings are recorded.
- **Constraints:** Use a model and input images permitted for the intended use; fit within available hardware; retain reproducible experiment records.

Define hard constraints separately from aesthetic preferences. “Exactly two objects” may be a pass/fail requirement, while “dramatic lighting” may be a subjective preference.

<br/>

### 2.1 Select an execution route

**Hosted API**
- Use the provider's documented endpoint or SDK.
- Confirm input and output schemas, credentials, rate limits, and usage terms.
- Record model identifiers, request IDs, and settings the service actually exposes.

**Local pipeline**
- Use a compatible, trusted model and documented inference library.
- Check license, component compatibility, memory requirements, and dependencies.
- Pin model revisions and software versions.

The examples below use Hugging Face Diffusers for local execution. They are illustrative templates: select a model that supports the task and adapt the pipeline class, parameters, precision, and dimensions to its documentation.

<br/>

## 3. Environment and Configuration

Create an isolated Python environment and install compatible versions of the selected libraries. Pin the versions used for the final experiment.

Example `requirements.txt`:

```text
diffusers
transformers
accelerate
safetensors
torch
Pillow
PyYAML
pandas
```

These are package names, not a guaranteed compatible lock file. Resolve versions for your Python version, operating system, accelerator, and chosen model, then record the exact installed versions.

<br/>

### 3.1 Example experiment configuration

Save configuration separately from code so that runs can be compared without editing the implementation.

```yaml
experiment_name: owl_scene_baseline
model_id: "publisher/model-repository"
revision: "PINNED_COMMIT_OR_VERSION"

runtime:
  device: "cuda"
  precision: "fp16"

generation:
  prompt: "A white owl perched on a branch in a misty forest"
  negative_prompt: null
  width: 768
  height: 768
  steps: 25
  guidance_scale: 5.0
  seeds: [101, 202]

editing:
  task: "inpainting"
  reference_image: "inputs/references/reference.png"
  mask_image: "inputs/masks/mask.png"
  prompt: "Replace the masked region with a misty forest background"

output:
  root_dir: "outputs"
```

The sample settings are placeholders, not universal defaults. Verify that the chosen model supports the dimensions, precision, prompt arguments, scheduler settings, and editing pipeline. Do not put API keys or other secrets in this file.

<br/>

## 4. Build the Text-to-Image Workflow

A minimal generation workflow should:
1. Load the documented pipeline and pinned model revision.
2. Create a deterministic generator for each seed where supported.
3. Run generation with recorded settings.
4. Save every planned output.
5. Save a manifest with model, settings, software versions, timing, and errors.
6. Validate the output file before reporting success.

<br/>

### 4.1 Example local generation function

```python
from pathlib import Path
import json
import time
import torch
import diffusers
from diffusers import DiffusionPipeline

MODEL_ID = "publisher/model-repository"
REVISION = "PINNED_COMMIT_OR_VERSION"
OUTPUT_DIR = Path("outputs/generated")
MANIFEST_DIR = Path("outputs/manifests")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

load_start = time.perf_counter()
pipe = DiffusionPipeline.from_pretrained(
    MODEL_ID,
    revision=REVISION,
    torch_dtype=dtype,
)
pipe = pipe.to(device)
load_seconds = time.perf_counter() - load_start

def generate_one(prompt, seed, steps=25, guidance_scale=5.0,
                 width=768, height=768, run_id="sample"):
    generator = torch.Generator(device=device).manual_seed(seed)
    start = time.perf_counter()
    result = pipe(
        prompt=prompt,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
        generator=generator,
    )
    if device == "cuda":
        torch.cuda.synchronize()
    generation_seconds = time.perf_counter() - start

    image = result.images[0]
    image_path = OUTPUT_DIR / f"{run_id}.png"
    image.save(image_path)

    manifest = {
        "run_id": run_id,
        "task": "text-to-image",
        "model_id": MODEL_ID,
        "revision": REVISION,
        "prompt": prompt,
        "seed": seed,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "width": width,
        "height": height,
        "device": device,
        "precision": str(dtype),
        "load_seconds": load_seconds,
        "generation_call_seconds": generation_seconds,
        "output_path": str(image_path),
        "diffusers_version": diffusers.__version__,
        "torch_version": torch.__version__,
        "status": "success",
    }
    with open(MANIFEST_DIR / f"{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return image_path, manifest
```

**Adaptation required:** not every model supports the generic `DiffusionPipeline` class or every argument shown. Some pipelines require a specialized class, different prompt arguments, or model-specific settings. Test a single small run before launching a batch.

<br/>

### 4.2 Compare prompts and settings

Choose one baseline and change one factor at a time.

Example experiment:
- A: “A white owl perched on a branch in a misty forest.”
- B: Same prompt, but add composition details such as “centered subject, wide establishing shot.”
- C: Same prompt as A, but change one supported inference setting.

Keep the seed, resolution, and other settings fixed where possible. Do not change prompt, model, resolution, steps, and guidance all at once if the goal is to learn which factor changed the result.

Generate multiple seeds for each variant. Save all outputs, not just the best-looking sample.

<br/>

## 5. Add an Editing Task

Choose **image-to-image** or **inpainting**. Use a reference image that you have permission to process and retain.

### 5.1 Image-to-image

Image-to-image starts from an input image and uses a strength or noise parameter to control how far the output may depart from the reference. Higher strength often allows larger changes; the precise behavior is pipeline-dependent.

Example pattern:

```python
from PIL import Image
from diffusers import AutoPipelineForImage2Image
import torch

model_id = "publisher/model-repository"
revision = "PINNED_COMMIT_OR_VERSION"

pipe_img2img = AutoPipelineForImage2Image.from_pretrained(
    model_id,
    revision=revision,
    torch_dtype=torch.float16,
).to("cuda")

reference = Image.open("inputs/references/reference.png").convert("RGB")
reference = reference.resize((768, 768))

generator = torch.Generator(device="cuda").manual_seed(303)

result = pipe_img2img(
    prompt="A watercolor illustration of the same scene in soft morning light",
    image=reference,
    strength=0.45,
    num_inference_steps=25,
    guidance_scale=5.0,
    generator=generator,
)

result.images[0].save("outputs/edited/image_to_image.png")
```

This example assumes a compatible image-to-image pipeline and CUDA device. Confirm the actual pipeline class and input requirements for the selected model.

<br/>

### 5.2 Inpainting

Inpainting changes a masked region while using the surrounding image as context. Verify mask polarity and expected format in the chosen pipeline: common conventions use white for the region to change and black for the region to preserve, but confirm the model documentation.

Example pattern:

```python
from PIL import Image
import torch
from diffusers import AutoPipelineForInpainting

model_id = "publisher/inpainting-model"
revision = "PINNED_COMMIT_OR_VERSION"

pipe_inpaint = AutoPipelineForInpainting.from_pretrained(
    model_id,
    revision=revision,
    torch_dtype=torch.float16,
).to("cuda")

image = Image.open("inputs/references/reference.png").convert("RGB")
mask = Image.open("inputs/masks/mask.png").convert("RGB")

# Ensure image and mask dimensions match the model's supported input size.
image = image.resize((768, 768))
mask = mask.resize((768, 768))

generator = torch.Generator(device="cuda").manual_seed(404)

result = pipe_inpaint(
    prompt="A misty forest background with soft natural light",
    image=image,
    mask_image=mask,
    num_inference_steps=25,
    guidance_scale=5.0,
    generator=generator,
)

result.images[0].save("outputs/edited/inpainting.png")
```

Use a checkpoint and pipeline that actually support inpainting. Resizing a mask can alter its boundary; for a real project, preserve alignment, inspect the mask visually, and record any preprocessing. The generic code does not guarantee that pixels outside the mask remain unchanged.

<br/>

### 5.3 Editing validation

Review:
- Did the intended region change?
- Did protected regions change unexpectedly?
- Are there seams, halos, or inconsistent lighting?
- Did subject identity or defining details drift?
- Is the result consistent with the prompt?
- Were reference-image permissions and provenance recorded?

For a simple preservation check, compare protected regions before and after editing. Pixel metrics can help identify unintended changes, but they do not fully capture semantic preservation.

<br/>

## 6. Output Validation and Error Records

Treat each generation as a run with a status, not merely as a file saved to disk.

### 6.1 Minimum validation

Check:
- The output file exists and is non-empty.
- The file can be opened as an image.
- Dimensions and format are expected.
- The run manifest exists and includes the configuration.
- The result was reviewed against the task's hard constraints.

Example validator:

```python
from pathlib import Path
from PIL import Image

def validate_image(path, expected_size=None):
    path = Path(path)
    errors = []

    if not path.exists():
        return {"valid": False, "errors": ["file_missing"]}

    if path.stat().st_size == 0:
        return {"valid": False, "errors": ["file_empty"]}

    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            actual_size = image.size
            actual_format = image.format
    except Exception as exc:
        return {
            "valid": False,
            "errors": ["image_decode_failed"],
            "detail": str(exc),
        }

    if expected_size and actual_size != expected_size:
        errors.append("unexpected_dimensions")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "size": actual_size,
        "format": actual_format,
        "bytes": path.stat().st_size,
    }
```

Do not log secrets, signed URLs, or unnecessary private prompt/reference data in error messages.

<br/>

### 6.2 Error categories

Record errors with a run ID and concise category:
- Model loading or compatibility failure.
- Invalid prompt or unsupported parameter.
- Out-of-memory error.
- Timeout or network error.
- Provider rate limit or rejected request.
- Job failure.
- Invalid or unavailable output.
- Validation failure.
- Human review failure against a hard constraint.

For hosted APIs, also retain request/job identifiers when available. Retry only failures that are plausibly transient, use a bounded retry policy, and avoid duplicate paid jobs after uncertain outcomes.

<br/>

## 7. Save a Comparison Gallery

A gallery should make it easy to compare outputs with their prompt, configuration, and measurements. It should not silently hide failed runs or show only the most favorable image.

### 7.1 Gallery fields

For each output, include:
- Thumbnail or image path.
- Run ID.
- Task type: text-to-image, image-to-image, or inpainting.
- Prompt or a safe prompt reference.
- Model/revision.
- Seed and settings where available.
- Quality scores and review notes.
- Runtime and memory measurements.
- Validation status and error details.
- Reference image and mask identifiers for editing tasks.

<br/>

### 7.2 Example CSV schema

```csv
run_id,task,config_id,seed,prompt,output_path,status,quality_score,adherence_score,runtime_seconds,peak_memory_gb,hardware,notes
txt_a_101,text-to-image,A,101,"A white owl in a misty forest",outputs/generated/txt_a_101.png,success,,,,,,
edit_b_303,image-to-image,B,303,"Watercolor style, same scene",outputs/edited/edit_b_303.png,success,,,,,,
```

These rows are illustrative. Populate measurements from actual runs; leave unavailable values blank and explain why in the report. Avoid putting confidential prompts or private reference paths in a public gallery.

<br/>

### 7.3 Gallery review protocol

1. Sort or filter by task, configuration, or status.
2. Compare matched prompts and seeds when supported.
3. Score outputs using the same rubric.
4. Keep failed outputs and mark them clearly.
5. Include representative successes and failures.
6. Report runtime and memory with the hardware and measurement method.
7. Record the final decision and known limitations.

<br/>

## 8. Resource and Reproducibility Report

For every experiment, record the configuration needed to interpret the result.

### 8.1 Hardware and software

| Field | What to record |
|<br/>|<br/>|
| CPU and system RAM | Exact model/capacity where available |
| GPU/accelerator and VRAM | Device model and memory capacity |
| Operating system and driver | Versions |
| Python and libraries | Python, PyTorch, Diffusers, Transformers, SDK versions |
| Model artifacts | Repository, pinned revision, required components |
| Precision | FP32, FP16, BF16, or quantization scheme |
| Runtime strategy | CPU, GPU, offloading, memory-efficient options |

<br/>

### 8.2 Runtime measurements

Separate:
- Model initialization/loading.
- Warm-up.
- Input preprocessing and encoding.
- Denoising or generation call.
- VAE decoding, if separately measurable.
- Postprocessing and file saving.
- End-to-end latency.

Record peak GPU allocated/reserved memory or device-wide usage where measurable. State which metric was used. A post-run memory snapshot does not reveal an earlier peak, and framework-reserved memory is not the same as total device-wide usage.

<br/>

### 8.3 Reproducibility limits

Even with a fixed seed, exact pixel-level reproduction may not be guaranteed across different hardware, kernels, library versions, model revisions, or hosted services. Record the environment and describe the level of repeatability actually achieved.

<br/>

## 9. Practice: Demonstrate a Creative Task and an Editing Task

**Task:** Complete one reproducible text-to-image experiment and one image-editing experiment.

### Experiment A — Creative generation

1. Select a trusted, licensed model and pin its revision.
2. Define a fixed prompt suite with at least two prompt variants.
3. Use a fixed seed list where supported.
4. Save all generated images and manifests.
5. Compare prompt adherence, composition, visual quality, and failure modes.
6. Record initialization time, generation latency, and memory where measurable.

<br/>

### Experiment B — Editing

1. Select a permitted reference image.
2. Choose image-to-image or inpainting.
3. Save the original input and, for inpainting, the aligned mask.
4. Record edit settings and seed where supported.
5. Save the edited result and manifest.
6. Inspect the target region, protected regions, boundaries, and identity preservation.
7. Record any unwanted changes and the limitations of the method.

<br/>

### Submission checklist

- [ ] Reproducible setup and pinned versions recorded.
- [ ] Model license and input-image permissions reviewed.
- [ ] At least two creative prompt/configuration variants generated.
- [ ] One editing task completed.
- [ ] All planned outputs, including failures, retained.
- [ ] Configuration manifests and validation/error records saved.
- [ ] Comparison gallery created.
- [ ] Quality rubric applied consistently.
- [ ] Runtime, hardware, and memory observations recorded.
- [ ] Limitations and next steps documented.

<br/>

### Final report structure

1. **Objective and success criteria**
2. **Model and environment**
3. **Experiment design**
4. **Creative-generation results**
5. **Editing results**
6. **Gallery and scoring summary**
7. **Runtime and memory measurements**
8. **Failures and root-cause hypotheses**
9. **Permissions, provenance, and disclosure**
10. **Conclusion and recommended next experiment**

<br/>

## 10. Checkpoint Answer

**Question:** How should you explain observed failures and the resource requirements of the selected workflow?

**Answer:**

Describe failures with evidence from the actual runs. Identify the task, prompt, model revision, settings, input assets, error record, and whether the failure was technical or qualitative. Technical failures include incompatible components, unsupported parameters, timeouts, and out-of-memory errors. Quality failures include missing objects, incorrect attributes, broken spatial relations, artifacts, and unintended changes outside an edit region.

Use controlled experiments to test likely causes. Change one factor at a time where feasible, retain unsuccessful outputs, and distinguish a confirmed cause from a hypothesis. Do not assume that a fluent prompt or a successful API response guarantees task completion.

Report resource requirements for the exact tested configuration: hardware, model revision, precision, dimensions, batch size, inference steps, memory optimizations, loading time, warm-up, generation latency, and peak memory where measurable. Separate loading, generation, decoding, and saving when instrumentation allows. Avoid universal GPU estimates; state the measurement method and limits of the evidence.

<br/>

## 11. Essential References

- Hugging Face Diffusers — Documentation: https://huggingface.co/docs/diffusers/index
- Hugging Face Diffusers — Loading pipelines: https://huggingface.co/docs/diffusers/using-diffusers/loading
- Hugging Face Diffusers — Image-to-image: https://huggingface.co/docs/diffusers/using-diffusers/img2img
- Hugging Face Diffusers — Inpainting: https://huggingface.co/docs/diffusers/using-diffusers/inpaint
- Hugging Face Hub — Model cards: https://huggingface.co/docs/hub/model-cards
- PyTorch — CUDA semantics and memory: https://docs.pytorch.org/docs/stable/notes/cuda.html
- Python `time` module: https://docs.python.org/3/library/time.html
- Pillow documentation: https://pillow.readthedocs.io/en/stable/

Verify the current documentation for the selected model, pipeline class, API, and library version. The examples above are starting templates, not a guarantee of compatibility with every image-generation model.

**Chapter takeaway:** a complete image-generation project includes more than producing images. It includes a controlled experiment, a permitted editing input, validation and error records, a comparison gallery, and measured resource requirements—so another person can understand what worked, what failed, and under which conditions.
