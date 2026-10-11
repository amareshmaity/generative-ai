# Level 2: Generative Model Architectures

Build a conceptual understanding of the main approaches used to generate content, how information moves through each model, and their strengths, limitations, and typical uses.

This README is a plan for creating notes one by one. Keep the numbered Markdown notes directly in `Level 2`, following the layout of your existing Level 1 notes. The filenames below are planned files, not existing links.

<br/>

## Prerequisites

- Complete [Level 1: Generative AI Fundamentals](<../Level 1/README.md>).
- Understand training, inference, generation, and input/output modalities.
- Review vectors, matrices, probability, neural networks, and loss functions conceptually.
- Basic Python is useful for optional demonstrations; training large models is not required.

<br/>

## Learning outcomes

After completing this level, you should be able to:

- Explain autoregressive generation and its sequential dependency.
- Describe how transformers can support generation without deriving attention mathematics.
- Trace training and generation for VAEs, GANs, and diffusion models.
- Explain latent representations and distinguish different uses of latent spaces.
- Compare approaches by learning objective, generation process, strengths, and failure modes.
- Recommend an approach for a use case while recognizing that architecture alone does not determine quality.

<br/>

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_generative_architecture_overview.md` | Approaches, architectures, objectives, and generation processes |
| 2 | `02_latent_representations_and_spaces.md` | Representations, compression, sampling, and interpolation |
| 3 | `03_autoregressive_generation.md` | Generating a sequence one element at a time |
| 4 | `04_transformer_based_generation.md` | Transformer roles and high-level generation flow |
| 5 | `05_variational_autoencoders.md` | Encoder, latent distribution, decoder, and reconstruction |
| 6 | `06_generative_adversarial_networks.md` | Generator, discriminator, and adversarial training |
| 7 | `07_diffusion_models.md` | Forward noising, learned denoising, and sampling |
| 8 | `08_comparing_generative_approaches.md` | Side-by-side comparison and overlapping categories |
| 9 | `09_strengths_limitations_and_use_cases.md` | Selecting approaches for practical scenarios |
| 10 | `10_practice_and_revision.md` | Diagrams, scenario exercises, and the level deliverable |

**Terminology note:** These categories are not mutually exclusive. Autoregression describes a generation factorization, transformers describe an architecture, and diffusion describes a modeling and generation approach. A transformer may be autoregressive or serve as a diffusion denoiser. Compare these dimensions explicitly rather than treating every label as a competing architecture.

<br/>

## Chapter outlines

### 01. Generative Architecture Overview

- Distinguish model architecture, learning objective, and generation procedure.
- Introduce autoregressive models, transformers, VAEs, GANs, and diffusion models.
- Identify training inputs, learned components, inference inputs, and generated outputs.
- Introduce conditional versus unconditional generation.
- Distinguish conceptual diagrams from full implementation details.

**Practice:** Annotate a generic training-to-generation diagram.

**Checkpoint:** Explain why a model's architecture and its generation approach are separate descriptions.

<br/>

### 02. Latent Representations and Latent Spaces

- Define representations and latent variables at a high level.
- Introduce compression, learned features, and reconstruction.
- Compare observed data space with a learned latent space.
- Introduce sampling and interpolation through simple visual examples.
- Distinguish VAE latent variables, GAN input noise, and latent diffusion representations.
- Explain that not every embedding or hidden representation is a probabilistic latent variable.
- Discuss why latent dimensions need not correspond to human-readable attributes.

**Practice:** Draw how a representation connects an input, an internal model state, and an output.

**Checkpoint:** Explain how latent representations can support generation without assuming all models use them identically.

<br/>

### 03. Autoregressive Generation

- Explain predicting the next element conditioned on previous elements.
- Introduce sequence probability factorization conceptually.
- Trace a text example from initial context to successive tokens.
- Distinguish training on known sequences from sequential generation at inference.
- Introduce sampling and stopping conditions without detailed decoding algorithms.
- Discuss sequential latency, error accumulation, and conditioning limits.
- Recognize that autoregression can apply to representations beyond text.

**Practice:** Trace a short generation example, showing the context available at each step.

**Checkpoint:** Explain why later generated elements depend on the earlier sequence.

<br/>

### 04. Transformer-Based Generation

- Introduce tokens, embeddings, attention, and contextual representations intuitively.
- Describe decoder-only and encoder-decoder generation flows.
- Explain causal masking as preventing access to future sequence elements.
- Distinguish parallel training computations from sequential autoregressive generation.
- Discuss context length and computational requirements conceptually.
- Recognize transformers as components in language, multimodal, and diffusion systems.
- Explain why an encoder-only transformer is not automatically a text generator.

**Practice:** Draw a high-level input-to-output diagram for decoder-only and encoder-decoder generation.

**Checkpoint:** Explain the transformer's role without deriving attention equations.

**Depth boundary:** Attention mathematics, query/key/value details, positional encoding, normalization, and KV caching are studied systematically in Level 3.

<br/>

### 05. Variational Autoencoders (VAEs)

- Briefly compare ordinary autoencoders with VAEs.
- Trace encoder, latent distribution, sampling, and decoder.
- Explain reconstruction loss and distribution regularization conceptually.
- Introduce the reparameterization trick as a training concept, without derivation.
- Distinguish reconstructing an input from generating through latent sampling.
- Discuss prior sampling and interpolation.
- Introduce reconstruction-quality trade-offs and posterior collapse at a high level.
- Identify uses in representation learning and generative pipelines.

**Practice:** Draw separate reconstruction and new-sample generation paths.

**Checkpoint:** Explain why a VAE learns a distribution rather than only a fixed encoding.

<br/>

### 06. Generative Adversarial Networks (GANs)

- Define generator and discriminator roles.
- Explain how real examples and generated examples enter training.
- Trace alternating updates and adversarial feedback conceptually.
- Explain generation from noise or conditioning after training.
- Identify which component is ordinarily needed for generation.
- Discuss realism, training instability, and mode collapse.
- Introduce conditional GANs and image translation as examples.

**Practice:** Draw the training loop and a separate inference diagram.

**Checkpoint:** Distinguish mode collapse from a successful generator covering diverse examples.

<br/>

### 07. Diffusion Models

- Trace gradual noise addition during the forward training process.
- Explain learning to predict noise or another denoising target at a high level.
- Trace iterative generation from noise using a learned denoiser and sampling procedure.
- Distinguish training timesteps from inference sampling steps.
- Introduce conditioning, guidance, and noise schedules conceptually.
- Compare diffusion in data space with diffusion in a learned latent space.
- Discuss quality, compute, latency, and controllability trade-offs.
- Recognize that the denoiser may use a U-Net or transformer architecture.

**Practice:** Annotate a diagram showing forward noising and generation through denoising steps.

**Checkpoint:** Explain why generation involves learned denoising rather than simply undoing a known noise sequence.

**Depth boundary:** Image generation APIs, schedulers in practice, inpainting, and advanced control methods belong to Level 10. Detailed mathematics and related flow-based approaches are optional extensions.

<br/>

### 08. Comparing Generative Approaches

- Compare learning objectives and learned components.
- Compare inference inputs and generation procedures.
- Compare latent-space use, conditioning, and output representations.
- Discuss fidelity, diversity, controllability, and failure modes.
- Compare qualitative training and inference resource needs.
- Show overlapping categories with an autoregressive transformer and a transformer-based diffusion model.
- Explain why performance depends on data, model size, training, implementation, and evaluation.

**Practice:** Build a comparison table for autoregressive generation, VAEs, GANs, and diffusion, recording the architecture separately.

**Checkpoint:** Avoid universal claims such as one family always being fastest or producing the best output.

<br/>

### 09. Strengths, Limitations, and Use Cases

- Examine sequence generation, image synthesis, reconstruction, and representation-learning scenarios.
- Map required modalities and outputs to suitable candidate approaches.
- Consider conditional generation, editing, and control requirements.
- Assess quality, latency, memory, data availability, and deployment constraints.
- Separate conceptual suitability from the availability of a usable pretrained model or service.
- Consider licensing, data provenance, and responsible-use requirements.
- Identify when an existing model or conventional software solution is sufficient.

**Practice:** Recommend candidates for text completion, image generation, and reconstruction-based representation learning. State what evidence would be needed to validate each recommendation.

**Checkpoint:** Explain trade-offs and assumptions rather than selecting solely from a model-family label.

<br/>

### 10. Practice and Revision

- Explain each approach using a diagram and a concrete example.
- Trace what happens during training and during generation.
- Compare reconstruction, adversarial learning, next-element prediction, and denoising.
- Review latent representations and overlapping categories.
- Analyze typical failure modes and application constraints.
- Complete the architecture comparison brief below.

**Checkpoint:** Defend an approach selection and identify at least one plausible alternative.

<br/>

## Level deliverable: Architecture comparison brief

Create `architecture_comparison_brief.md` in this folder with:

1. A glossary distinguishing architecture, objective, generation procedure, conditioning, and latent representation.
2. Training and generation diagrams for autoregressive models, VAEs, GANs, and diffusion models.
3. A comparison table covering learned components, objectives, generation steps, latent-space use, strengths, limitations, and typical applications.
4. Examples showing where transformers fit into more than one generation approach.
5. Three use-case recommendations with requirements, alternatives, trade-offs, and assumptions.
6. A walkthrough of diffusion generation from initial noise to an output.
7. References supporting technical claims and any limitations of the comparison.

Conceptual diagrams and explanations are sufficient. If you include a small experiment, record its model, inputs, settings, environment, and results. Large-model training and paid APIs are not required.

<br/>

## Suggested format for each note

1. Learning objectives and prerequisites.
2. Intuition and a concrete example.
3. Key components and terminology.
4. Training flow versus generation flow.
5. A diagram or comparison table.
6. Strengths, limitations, and common misconceptions.
7. A short exercise and revision questions with answers.
8. References and optional extensions.

Use mathematics only where it clarifies a concept. Keep provider-specific examples optional and verify them when writing the notes.

<br/>

## Completion checklist

- [ ] Distinguish architectures from objectives and generation approaches.
- [ ] Explain latent representations without treating every hidden state as the same kind of latent variable.
- [ ] Trace autoregressive generation step by step.
- [ ] Explain the high-level role of transformers in generation.
- [ ] Draw VAE training, reconstruction, and generation paths.
- [ ] Draw GAN training and generation paths.
- [ ] Trace diffusion noising and iterative generation.
- [ ] Compare approaches with qualified trade-offs and typical failure modes.
- [ ] Recommend candidates for three practical scenarios.
- [ ] Complete and review the architecture comparison brief.

<br/>

## Scope and next step

This level focuses on conceptual understanding and practical distinctions. Full mathematical derivations, implementing every architecture, and training large models from scratch are optional extensions.

Next: **Level 3 — Transformer Architecture and Tokenization** in the [main course outline](../README.md).
