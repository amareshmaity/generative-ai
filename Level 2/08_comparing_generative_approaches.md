# Chapter 08 — Comparing Generative Approaches

## 1. Learning Objectives and Prerequisites

By the end of this chapter, you should be able to:

- Compare the learning objectives and learned components of autoregressive models, VAEs, GANs, and diffusion models.
- Compare the inputs and procedures used during inference.
- Explain differences in latent-space use, conditioning, and output representations.
- Compare fidelity, diversity, controllability, and common failure modes.
- Discuss training and inference resource requirements qualitatively.
- Explain how categories can overlap, using an autoregressive transformer and a transformer-based diffusion model as examples.
- Explain why performance depends on data, model size, training, implementation, and evaluation.

**Prerequisites:** Chapters 03–07: Autoregressive Generation, Transformer-Based Generation, VAEs, GANs, and Diffusion Models.

**Central principle:** These approaches are not all mutually exclusive categories. Some describe a generation procedure, some describe a model architecture, and others describe a generative framework or training objective. A fair comparison keeps these dimensions separate.

<br/>

## 2. A Fair Comparison: Separate the Dimensions

Before comparing model families, distinguish three questions:

1. **Architecture:** What neural-network structure processes the input? Examples include a transformer, U-Net, or encoder-decoder network.
2. **Learning objective or framework:** What is the model trained to learn? Examples include next-token prediction, VAE reconstruction plus distribution regularization, or adversarial learning.
3. **Generation procedure:** How is a new output produced at inference time? Examples include sequential next-token prediction, latent sampling followed by decoding, or iterative denoising.

These dimensions can overlap. For example, a transformer can be used for autoregressive next-token generation, while a transformer can also serve as a denoiser inside a diffusion model.

<br/>

### A conceptual map

```text
Architecture
  - Transformer
  - U-Net
  - Encoder-decoder network
          |
          | can be components in
          v
Generative framework / objective
  - Autoregressive next-element prediction
  - VAE objective
  - GAN adversarial objective
  - Diffusion denoising objective
          |
          | works with a
          v
Generation procedure
  - Sequential token generation
  - Sample latent vector and decode
  - Generate with a trained generator
  - Iterative denoising
```

This diagram is illustrative rather than a strict taxonomy. In practice, architecture and objective choices interact, and some systems combine multiple components or training objectives.


<br/>


## 3. Comparison of the Core Approaches

The following table focuses on common patterns. Specific implementations can differ.

| Approach | Main learning objective or framework | What is learned? | Typical inference input | Typical generation procedure |
|---|---|---|---|---|
| Autoregressive generation | Predict the next element conditioned on preceding context | A conditional next-element distribution | Prompt or initial context | Predict, select, and append elements sequentially |
| VAE | Reconstruction plus regularization of an input-conditioned latent distribution toward a prior | Encoder distribution and decoder | Latent vector sampled from a prior for new samples; an input for reconstruction | Sample latent vector and decode |
| GAN | Adversarial training between generator and discriminator | Generator and discriminator | Noise, optionally with a condition | Pass noise/condition through the trained generator |
| Diffusion | Learn to predict noise or another denoising-related target across noise levels | Denoiser and related model components | Initial noise, optionally with conditioning | Iteratively denoise using a sampling procedure |

**Important:** Autoregressive generation is a procedure or probabilistic factorization, not a single neural-network architecture. Transformers are commonly used to implement it, but autoregressive models need not all use the same architecture.


<br/>


## 4. Architecture Is a Separate Dimension

A common mistake is to compare “transformers” directly with “diffusion models” as if they were equivalent categories. A transformer is an architecture; diffusion is a generative framework and sampling process. A diffusion model can use a transformer as its denoiser.

| Example system | Architecture | Learning objective or framework | Generation procedure |
|---|---|---|---|
| Decoder-only language model | Transformer | Autoregressive next-token prediction | Sequential token generation |
| VAE for images | Encoder and decoder networks | Reconstruction plus latent-distribution regularization | Sample latent vector, then decode |
| Image GAN | Generator and discriminator networks, architecture varies | Adversarial learning | Generate directly from noise or noise plus condition |
| U-Net diffusion model | U-Net denoiser | Diffusion denoising objective | Iterative denoising |
| Transformer-based diffusion model | Transformer denoiser | Diffusion denoising objective | Iterative denoising |

<br/>

### Overlapping example 1: Autoregressive transformer

A decoder-only transformer can be trained to predict the next token from preceding tokens. During inference, it repeatedly predicts and appends tokens.

- **Architecture:** Transformer.
- **Learning objective:** Autoregressive next-token prediction.
- **Generation procedure:** Sequential token generation.

<br/>

### Overlapping example 2: Transformer-based diffusion model

A transformer can instead process noisy representations and timestep information to predict a denoising-related target. A sampling procedure uses these predictions repeatedly to produce an output.

- **Architecture:** Transformer.
- **Learning objective:** Diffusion denoising objective.
- **Generation procedure:** Iterative denoising.

Both systems use transformers, but their training targets and generation procedures differ. Therefore, “transformer” alone does not tell you how a model generates its output.


<br/>


## 5. Latent-Space Use and Output Representations

Latent representations appear in multiple generative approaches, but their roles differ.

| Approach | Role of latent space or internal representation | Output representation |
|---|---|---|
| Autoregressive generation | May operate on tokens or other ordered representations; a latent vector is not required by the basic procedure | A sequence of elements, such as text tokens or learned codes |
| VAE | The encoder predicts an input-conditioned latent distribution; a latent sample is decoded | Reconstructed or newly generated data, such as an image |
| GAN | Noise is mapped by the generator to a sample; intermediate latent representations may also be used | Generated sample, such as an image |
| Data-space diffusion | The iterative noising and denoising process operates directly on a data representation | Denoised data representation |
| Latent diffusion | The iterative process operates on a learned latent representation, which is decoded afterward | Output produced from the final latent representation |

Do not treat every latent-like vector as the same object:

- A VAE's latent vector is sampled from an input-conditioned distribution during reconstruction or from a prior for new-sample generation.
- A GAN's input noise is a source of variation mapped by the generator.
- A latent-diffusion representation is a learned representation of the data on which the diffusion process operates.
- An autoregressive model can operate directly on token sequences without requiring a VAE-style latent distribution.

The details depend on the design of the specific model.


<br/>


## 6. Conditioning and Controllability

**Conditioning** means providing additional information that influences what the model generates. The available controls depend on the model and its training setup.

| Approach | Common conditioning pattern | Main qualification |
|---|---|---|
| Autoregressive generation | Prompt or preceding context | Output is conditioned on available context; it may still ignore or misinterpret details |
| VAE | Conditional inputs can be incorporated into the encoder, decoder, or both in conditional variants | A basic VAE is not automatically conditioned on a text prompt |
| GAN | Noise plus a class label, source image, or other condition in conditional variants | Condition-following depends on training and design |
| Diffusion | Text, labels, images, or other conditions may guide denoising | Guidance can steer output but does not guarantee exact adherence |

Controllability is not an all-or-nothing property. A model may follow broad conditions well while missing fine details. Evaluation should match the task: for example, prompt adherence for text-conditioned image generation, or correctness of required fields for structured output.


<br/>


## 7. Fidelity, Diversity, and Common Failure Modes

The terms *fidelity* and *diversity* describe different properties.

- **Fidelity:** How well an output matches the desired data characteristics or task requirements.
- **Diversity:** How well the model produces varied examples rather than repeating a narrow subset.
- **Controllability:** How reliably the output responds to a prompt, label, source input, or other condition.

A model can perform well on one dimension and poorly on another. Realistic samples do not prove that a model covers the full data distribution.

| Approach | Potential strengths | Common failure modes or limitations |
|---|---|---|
| Autoregressive generation | Context-sensitive sequence continuation; flexible output length within configured limits | Errors can influence later tokens; sequential latency; limited context |
| VAE | Probabilistic latent representations; reconstruction and prior-based sampling | Reconstruction-detail trade-offs; prior mismatch; posterior collapse in some settings |
| GAN | Can produce convincing samples; direct generation through the trained generator | Training instability; mode collapse; poor coverage despite realistic examples |
| Diffusion | Can produce detailed and varied outputs; flexible conditioning in suitable designs | Iterative inference cost; artifacts; imperfect prompt adherence; sampling sensitivity |

These are common patterns, not universal rankings. The exact failure modes and their severity depend on the architecture, objective, data, and implementation.

<br/>

### A practical evaluation lesson

When evaluating a generative system, ask more than “Does one output look good?”

- Does it consistently produce valid outputs?
- Does it cover the range of examples the task requires?
- Does it follow the given condition?
- Does it remain reliable across different prompts or inputs?
- What are the latency and resource costs?
- Is the evaluation method suitable for the intended use?


<br/>


## 8. Training and Inference Resource Requirements

Resource use should be considered separately for training and inference.

| Approach | Training: qualitative considerations | Inference: qualitative considerations |
|---|---|---|
| Autoregressive generation | Large sequence models can be expensive to train; training can compute predictions at multiple known positions in parallel | Sequential output steps can increase latency for long generations |
| VAE | Must train encoder and decoder and balance reconstruction with regularization | Often a latent sample and decoder pass are sufficient for new-sample generation |
| GAN | Must optimize generator and discriminator; adversarial training can be sensitive and unstable | The generator commonly produces an output in one forward pass, though model cost still matters |
| Diffusion | Must train a denoiser over noisy examples and timesteps | Multiple denoising evaluations commonly increase latency and compute |

This table describes common qualitative patterns, not a fixed cost order. A small diffusion model can be cheaper than a very large autoregressive model in a particular setting; a high-resolution GAN can also be expensive. Hardware, batching, model size, output size, implementation, and inference optimizations can change the comparison substantially.

<br/>

### Why no universal speed ranking works

“Fastest” depends on what is being measured:

- Time to first output versus time to complete output.
- Single-request latency versus throughput across a batch.
- Training cost versus inference cost.
- Output length or image resolution.
- Hardware and software optimizations.
- Quality or reliability required for the task.

For example, a GAN generator may produce a sample in one forward pass, while diffusion typically requires multiple denoising steps. That difference is useful, but it does not prove that every GAN system is faster than every diffusion system under all workloads.


<br/>


## 9. Why Performance Depends on More Than Model Family

A model family's name is not enough to predict its practical performance. Results depend on several interacting factors.

### Data

The quality, quantity, diversity, labeling, and relevance of training data affect what the model can learn. Missing or biased patterns in the data can limit generation and evaluation.

<br/>

### Model size and architecture

Capacity and architectural choices affect the patterns the model can represent, but a larger model is not automatically better for every task. The architecture must fit the objective and data.

<br/>

### Training procedure

Optimization, loss functions, regularization, training duration, and stability all influence the learned model. GANs, VAEs, autoregressive models, and diffusion models have different training considerations.

<br/>

### Implementation and hardware

Memory layout, batching, precision, kernel implementations, sampling settings, and hardware affect speed and resource use. Two implementations of the same model family may have different latency and throughput.

<br/>

### Evaluation

Metrics capture different aspects of quality. A metric focused on visual fidelity may not measure diversity or prompt adherence well. Evaluation should use multiple suitable tests and, where appropriate, human judgment or task-specific checks.

**Conclusion:** Model-family comparisons identify typical trade-offs. They do not replace evaluation on the intended task and deployment environment.


<br/>


## 10. Practice: Build a Comparison Table

Create a table with one row for each approach and separate columns for:

1. Architecture (keep this separate from the model family)
2. Learning objective or framework
3. Learned components
4. Inference input
5. Generation procedure
6. Latent-space use
7. Conditioning options
8. Fidelity and diversity considerations
9. Common failure modes
10. Training and inference resource considerations

<br/>

### Suggested answer

| Approach | Architecture (example, not mandatory) | Objective / framework | Inference input and procedure | Latent-space use | Key trade-off or failure mode |
|---|---|---|---|---|---|
| Autoregressive generation | Often a decoder-only transformer | Next-element prediction | Prompt; predict and append sequentially | May use tokens or other sequence representations directly | Sequential latency; earlier errors can affect later output |
| VAE | Encoder and decoder | Reconstruction plus distribution regularization | Prior sample -> decoder for new output | Explicit probabilistic latent representation | Reconstruction versus regularization trade-off; posterior collapse |
| GAN | Generator and discriminator | Adversarial learning | Noise/condition -> generator | Noise input mapped to data; additional latent structure varies | Training instability and mode collapse |
| Diffusion | U-Net or transformer denoiser, among other options | Denoising-related objective | Initial noise -> repeated denoising and sampling | Data space or learned latent space | Iterative inference cost; quality depends on sampler and model |

The architecture column contains examples, not requirements. For instance, transformer-based diffusion uses a transformer denoiser but retains the diffusion generation procedure.


<br/>


## 11. Revision Questions

**1. Why should architecture and generation procedure be compared separately?**  
Because the same architecture can support different objectives and generation procedures. A transformer can be used for autoregressive generation or as a denoiser in a diffusion model.

**2. What does an autoregressive model learn?**  
A conditional distribution for the next sequence element given the preceding context.

**3. What are the two major conceptual parts of a VAE objective?**  
Reconstruction and regularization of the input-conditioned latent distribution toward a prior.

**4. What is the discriminator's role in a GAN?**  
It learns to distinguish real from generated examples and provides adversarial feedback during training.

**5. What is the learned component in a diffusion model?**  
A denoiser that predicts noise or another denoising-related target, used with a sampling procedure at inference time.

**6. Why are latent representations not interchangeable across all model families?**  
They serve different purposes: a VAE uses a probabilistic latent distribution, GAN noise is mapped by a generator, and latent diffusion denoises a learned data representation.

**7. Why is realism alone not enough to evaluate a generative model?**  
A model may produce realistic individual samples but lack diversity, omit important data modes, or fail to follow conditions.

**8. Why can no model family be declared universally fastest?**  
Speed depends on model size, output requirements, hardware, implementation, batching, and what latency or throughput is being measured.


<br/>


## 12. Summary and Checkpoint

### Summary

- Autoregressive generation, VAEs, GANs, and diffusion models differ in objectives, learned components, inference inputs, and generation procedures.
- Architecture, learning objective, and generation procedure are separate dimensions.
- Transformers can implement autoregressive generation or act as denoisers in diffusion systems.
- Latent representations play different roles across VAEs, GANs, and latent diffusion.
- Fidelity, diversity, and controllability are distinct properties and should be evaluated separately.
- Each approach has characteristic trade-offs, but no model family wins universally.
- Training and inference costs depend on the particular model, data, implementation, hardware, and output requirements.
- Evaluation must reflect the intended task and deployment setting.

<br/>

### Checkpoint

**Avoid universal claims such as one family always being fastest or producing the best output.**

A strong answer should explain that model families have different typical strengths and costs, but results depend on data quality and diversity, model capacity, training procedure, architecture, implementation, hardware, sampling settings, and evaluation criteria. A fair comparison specifies the task and conditions, measures both quality and resource use, and avoids treating a common tendency as a universal rule.


<br/>


## 13. References and Optional Extensions

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — transformer architecture.
- [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — variational autoencoders.
- [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — generative adversarial networks.
- [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — diffusion-based generation.
- [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — diffusion in learned latent space.

**Optional extension:** For a project, compare candidate models on the same task and dataset, then record output quality, diversity, condition adherence, latency, memory, and operating cost. Make sure the evaluation methods measure the properties that matter to the application.

**Next chapter:** `09_strengths_limitations_and_use_cases.md`
