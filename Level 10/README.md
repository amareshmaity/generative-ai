# Level 10: Image Generation with Diffusion Models

**Goal:** Understand and use modern image-generation systems.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 10`, following the previous levels. The filenames below are planned files, not existing chapter links.

**Depth guidance:** Architecture, training objectives, and sampling theory are part of the core conceptual material. Detailed mathematical derivations, custom-model training, and advanced control techniques are optional extensions.

## Prerequisites

- Complete [Level 9: Multimodal Generative AI](<../Level 9/README.md>).
- Review diffusion and latent representations from Level 2, attention from Level 3, and inference/resource trade-offs from Level 4.
- Understand Python environments, model APIs, image inputs, and safe configuration.
- Review probability, Gaussian noise, loss functions, and neural-network training conceptually.
- Use public, synthetic, or appropriately licensed reference images. Local execution requires compatible hardware; a hosted service is an alternative.

## Learning outcomes

After completing this level, you should be able to:

- Explain forward noising, learned denoising, and iterative generation.
- Trace pixel-space and latent-diffusion architectures, including text conditioning.
- Compare noise schedules, sampling steps, guidance, seeds, and resolution.
- Generate images from text and perform image-to-image or masked editing.
- Explain structural controls, reference adapters, and model-specific compatibility.
- Choose checkpoints and execution options using quality, license, hardware, and cost requirements.
- Evaluate prompt adherence, visual quality, runtime, and limitations reproducibly.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_image_generation_overview.md` | Tasks and the complete generation pipeline |
| 2 | `02_diffusion_theory_and_denoising.md` | Forward process, learning objective, and reverse generation |
| 3 | `03_diffusion_model_architecture.md` | Denoisers, timestep information, U-Nets, and transformers |
| 4 | `04_latent_diffusion_and_latent_spaces.md` | Autoencoders and generation in compressed representations |
| 5 | `05_text_encoders_and_conditioning.md` | Prompt representations and their integration |
| 6 | `06_noise_schedules_samplers_and_steps.md` | Training schedules versus inference procedures |
| 7 | `07_guidance_and_conditioning_controls.md` | Conditional guidance and its trade-offs |
| 8 | `08_text_to_image_generation.md` | Prompts, seeds, resolution, and reproducible requests |
| 9 | `09_image_to_image_generation.md` | Starting images, noise strength, and preservation |
| 10 | `10_inpainting_and_outpainting.md` | Masked edits and canvas extension |
| 11 | `11_structural_control_and_adapters.md` | Edges, depth, pose, reference images, and adapters |
| 12 | `12_checkpoints_and_model_selection.md` | Components, compatibility, versions, and licenses |
| 13 | `13_image_apis_and_open_model_ecosystems.md` | Hosted requests and local pipeline execution |
| 14 | `14_gpu_memory_and_runtime_requirements.md` | Resource measurement and optimization trade-offs |
| 15 | `15_image_quality_and_prompt_adherence.md` | Rubrics, controlled comparisons, and failure analysis |
| 16 | `16_responsible_use_licensing_and_provenance.md` | Inputs, outputs, consent, and documentation |
| 17 | `17_image_generation_and_editing_project.md` | A reproducible generation/editing workflow |
| 18 | `18_practice_and_revision.md` | Consolidation and experiment report |

## Chapter outlines

### 01. Image Generation Overview

- Compare text-to-image, image-to-image, inpainting, and outpainting tasks.
- Trace input preparation, conditioning, iterative generation, decoding, and output handling.
- Distinguish image-understanding models from image-generation models.
- Explain that not every image generator is a diffusion model.

**Practice:** Diagram a text-to-image pipeline and identify user-controlled settings.

**Checkpoint:** Separate the model architecture from the generation task and service interface.

### 02. Diffusion Theory and Denoising

- Explain gradual corruption of training images with noise.
- Introduce timestep sampling and noise-level conditioning during training.
- Compare noise, clean-sample, and velocity prediction targets conceptually.
- Explain denoising losses and the learned reverse-generation process.
- Distinguish learning from noisy examples from running every sampling step during each training update.
- Explain why generation is not simply reversing one known noise sequence.

**Practice:** Sketch forward-noising and reverse-generation trajectories with a toy image.

**Checkpoint:** Distinguish the training objective from the inference sampling procedure.

### 03. Diffusion Model Architecture

- Identify the noisy image or latent input, timestep/noise-level representation, conditioning, and prediction output.
- Trace U-Net downsampling, intermediate blocks, upsampling, and skip connections conceptually.
- Introduce transformer-based denoisers and patch/token representations.
- Explain attention and conditioning integration without assuming all models use identical blocks.
- Distinguish a denoiser from the full generation pipeline.

**Practice:** Annotate U-Net-based and transformer-based denoiser diagrams.

**Checkpoint:** Explain how timestep and prompt information influence the denoiser.

### 04. Latent Diffusion and Latent Spaces

- Compare pixel-space and latent-space generation.
- Trace image encoding, latent diffusion, and image decoding.
- Explain the autoencoder's role and reconstruction limitations.
- Discuss spatial compression, latent scaling, and component compatibility.
- Distinguish image latents from text embeddings and input noise.

**Practice:** Draw separate training, reconstruction, and text-to-image generation paths.

**Checkpoint:** Explain why latent diffusion can reduce computation while introducing representation constraints.

### 05. Text Encoders and Conditioning

- Trace prompt tokenization and text representations.
- Explain cross-attention and other conditioning mechanisms at a high level.
- Discuss prompt length limits, truncation, and model-dependent prompt handling.
- Distinguish positive prompts, negative prompts where supported, and other conditions.
- Discuss composition, attribute binding, and ambiguous instructions.

**Practice:** Compare prompts specifying subject, setting, composition, and visual style explicitly.

**Checkpoint:** Explain why a prompt influences output without acting as a guaranteed scene specification.

### 06. Noise Schedules, Samplers, and Sampling Steps

- Distinguish training noise schedules from inference timestep selection and sampling algorithms.
- Introduce stochastic and deterministic sampling concepts.
- Discuss step count, noise levels, numerical approximation, and model compatibility.
- Compare quality/runtime trade-offs without assuming more steps always improve quality.
- Record the sampler and schedule rather than only the number of steps.

**Practice:** Compare two supported step counts or samplers while holding other settings fixed.

**Checkpoint:** Explain why equal step counts do not establish equivalent generation workloads or quality.

### 07. Guidance and Conditioning Controls

- Explain classifier guidance and classifier-free guidance conceptually.
- Introduce conditional/unconditional predictions in standard classifier-free guidance.
- Discuss model-specific guidance variants and unsupported controls.
- Compare adherence, diversity, oversaturation, and artifacts.
- Separate guidance strength from sampling steps and image-to-image strength.

**Practice:** Compare supported guidance values using fixed prompts and seeds where available.

**Checkpoint:** Explain why stronger guidance does not automatically produce a better image.

### 08. Text-to-Image Generation

- Specify a task, prompt, output dimensions, sample count, and supported settings.
- Record seeds where available and explain reproducibility limits across hardware and versions.
- Compare prompt variants with controlled settings and several outputs.
- Preserve original outputs and an experiment manifest.
- Handle invalid requests, refusals, partial failures, and budget limits.

**Practice:** Generate a small image set from a fixed prompt suite.

**Checkpoint:** Reproduce the request configuration without promising identical pixels across environments.

### 09. Image-to-Image Generation

- Trace reference-image preparation, encoding/noising, conditioning, and generation.
- Explain strength or starting-noise controls where supported.
- Compare preservation of layout, identity, color, and content with transformation goals.
- Discuss resizing, aspect ratio, and reference-image provenance.

**Practice:** Apply a controlled transformation at two supported strength settings.

**Checkpoint:** Explain why an input image is a condition rather than a guarantee of exact preservation.

### 10. Inpainting and Outpainting

- Define edit regions, masks, and preserved context.
- Verify mask polarity and resizing behavior for the selected implementation.
- Compare dedicated editing models with generic pipeline support.
- Discuss boundary blending, consistency, and changes outside the intended region.
- Introduce canvas extension and missing-content generation.

**Practice:** Perform an inpainting or outpainting edit and inspect both edited and intended-to-be-preserved regions.

**Checkpoint:** Explain mask semantics and measure whether the edit respected its boundaries.

### 11. Image-to-Image Control and Adapter-Based Methods

- Introduce edge, depth, pose, and segmentation conditions.
- Explain ControlNet-style structural conditioning and reference-image adapters conceptually.
- Distinguish structural/reference conditioning from LoRA-based parameter adaptation.
- Discuss preprocessing, condition strength, and conflicting controls.
- Verify base-model, adapter, and pipeline compatibility.

**Practice:** Design or run one controlled example using a permitted reference or structural guide.

**Checkpoint:** Explain what information the control supplies and what remains unconstrained.

**Depth boundary:** Training adapters, combining several advanced controls, and detailed implementation internals are optional extensions.

### 12. Model Checkpoints and Model Selection

- Distinguish full pipelines, component checkpoints, fine-tuned weights, and adapters.
- Inspect model cards, licenses, intended uses, and compatibility requirements.
- Record versions, artifact identifiers, required components, and precision.
- Compare task support, output quality, hardware needs, and operating cost.
- Use trusted artifact sources and avoid unsafe arbitrary-code loading.

**Practice:** Create a selection matrix for two candidate model configurations.

**Checkpoint:** Explain why compatible architecture, tokenizer, text encoder, and autoencoder components matter.

### 13. Image Generation APIs and Open Model Ecosystems

- Compare hosted image requests with local pipeline execution.
- Inspect supported inputs, settings, job status, output formats, and usage reporting.
- Handle credentials, polling where needed, timeouts, bounded retries, and output storage.
- Record SDK/library versions and provider-side configuration limits.
- Keep provider-specific capability differences explicit.

**Practice:** Implement one minimal generation workflow through an available API or local library.

**Checkpoint:** Distinguish documented service controls from settings exposed by a local model pipeline.

### 14. GPU, Memory, and Runtime Requirements

- Separate model weights, activations, temporary tensors, and component-loading overhead.
- Discuss precision, image resolution, batch size, and architecture-dependent memory use.
- Compare CPU execution, GPU execution, and offloading where supported.
- Introduce memory-efficient attention, slicing/tiling, and quantization as implementation-dependent options.
- Measure initialization separately from generation and decoding.
- Report peak memory where measurable; avoid universal hardware estimates.

**Practice:** Record hardware, configuration, runtime, and memory for a small generation task.

**Checkpoint:** Explain why reducing sampling steps may reduce runtime without proportionally reducing peak memory.

### 15. Image Quality, Prompt Adherence, and Trade-offs

- Define rubrics for visual quality, requested objects/attributes, composition, and edit preservation.
- Evaluate text rendering, counting, spatial relations, anatomy, and repeated patterns.
- Compare multiple outputs rather than selecting only the most favorable sample.
- Change one factor at a time and record regressions as well as improvements.
- Discuss limitations of automated similarity metrics and model-based judges.
- Compare quality with runtime, memory, cost, and reproducibility.

**Practice:** Score a fixed prompt suite under two configurations with the same rubric.

**Checkpoint:** Separate aesthetic preference from task completion and evidence of consistent performance.

### 16. Responsible Use, Licensing, and Provenance

- Check model, adapter, reference-image, and service usage terms separately.
- Discuss consent and impersonation risks for identifiable people.
- Keep source attribution and generation/editing disclosures where appropriate.
- Record model versions, prompts, settings, references, and output history without exposing private data.
- Introduce provenance metadata and its limitations; absence of metadata does not establish authenticity.
- Follow applicable service restrictions and review outputs before consequential use.

**Practice:** Prepare a provenance manifest and permitted-use checklist for the project assets.

**Checkpoint:** Distinguish access to model weights from permission to use every input or output in every context.

### 17. Image Generation and Editing Project

- Build a notebook, command-line workflow, or small application for generation and editing.
- Generate text-to-image samples and compare prompts/settings.
- Add image-to-image or inpainting using permitted inputs.
- Save outputs with configurations and validation/error records.
- Include a comparison gallery with quality, runtime, and hardware observations.

**Practice:** Demonstrate a reproducible creative task and an editing task.

**Checkpoint:** Explain observed failures and the resource requirements of the selected workflow.

### 18. Practice and Revision

- Review theory, architecture, latent representations, and conditioning.
- Compare schedules, samplers, guidance, and edit controls.
- Explain component compatibility and local/hosted execution choices.
- Evaluate adherence, preservation, quality, and resource trade-offs.
- Complete the experiment report below.

**Checkpoint:** Defend a configuration choice using recorded outputs and measurements.

## Level deliverable: Image-generation experiment report

Create `image_generation_experiment_report.md` in this folder with:

1. A training-versus-inference diagram and an annotated latent-diffusion architecture.
2. A documented model/pipeline choice, component versions, license checks, and environment.
3. A fixed suite of at least five prompts covering composition, attributes, and known challenging cases.
4. Text-to-image outputs and a controlled comparison varying one prompt or supported generation setting.
5. Several samples per configuration, with seed handling and reproducibility limits documented.
6. An image-to-image or inpainting example with permitted source assets and preservation checks.
7. A quality/adherence rubric, scored results, and both successes and failures.
8. Runtime, hardware, peak memory, and usage/cost where available; distinguish estimates from observations.
9. A provenance manifest connecting sources, settings, and outputs.
10. Remaining limitations and a recommended configuration for the chosen task.

Use a small, bounded experiment. Hosted services and local tools are both suitable; paid APIs and custom training are not required. If generation access is unavailable, prepare the workflow and mark experiments pending rather than presenting fixtures as measured results.

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Intuition and a concrete generation/editing example.
3. Architecture diagram, notation, or worked calculation.
4. Minimal workflow and documented controls.
5. Comparison outputs and evaluation criteria.
6. Failure cases, compatibility constraints, and resource trade-offs.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current model capabilities, licenses, library APIs, hardware support, and service pricing when writing implementation notes. Define symbols before equations and separate conceptual assumptions from model-specific behavior.

## Optional extensions

- Derive forward-process equations, variational objectives, and reverse sampling updates.
- Study score matching and continuous-time formulations.
- Compare diffusion with related flow-matching and rectified-flow approaches without treating their objectives as identical.
- Train a toy model on a small permitted dataset or fine-tune a compatible model.
- Explore adapter training, multi-condition control, and consistency across repeated subjects.
- Investigate distillation and faster sampling methods with suitable quality comparisons.

## Completion checklist

- [ ] Explain diffusion training and iterative denoising.
- [ ] Trace U-Net-based and transformer-based architecture roles.
- [ ] Explain latent diffusion, autoencoders, and text conditioning.
- [ ] Distinguish schedules, samplers, steps, guidance, and edit strength.
- [ ] Generate images from prompts and compare settings reproducibly.
- [ ] Complete an image-to-image or inpainting experiment.
- [ ] Explain structural controls and adapter compatibility.
- [ ] Select checkpoints and an execution approach using explicit requirements.
- [ ] Document runtime, hardware, memory, and measurement limits.
- [ ] Evaluate visual quality and prompt adherence separately.
- [ ] Record licensing, consent, and provenance considerations.
- [ ] Complete and review the image-generation experiment report.

## Scope and next step

This level covers conceptual diffusion theory and practical image generation/editing. Large-model training, detailed mathematical derivations, and advanced controls are optional extensions. Comprehensive evaluation, security, and deployment are expanded in Levels 13–15.

Next: **Level 11 — Audio, Speech, and Video Generation** for another media specialization. See the [main course outline](../README.md).
