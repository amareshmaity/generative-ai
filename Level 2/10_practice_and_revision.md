# Chapter 10 — Practice and Revision

## 1. Purpose and Learning Objectives

This chapter consolidates Level 2: Generative Model Architectures. It is designed to help you explain the main approaches, trace their training and generation processes, compare their objectives, and justify a model choice for a practical task.

By completing the chapter, you should be able to:

- Explain autoregressive generation, transformer-based generation, VAEs, GANs, and diffusion models using a diagram and a concrete example.
- Trace the main training and inference flow for each approach.
- Compare next-element prediction, reconstruction with distribution regularization, adversarial learning, and denoising.
- Explain latent representations and why architecture, learning objective, and generation procedure are different dimensions.
- Identify common failure modes and application constraints.
- Complete an architecture comparison brief and defend a selection with at least one plausible alternative.

**Scope reminder:** This is a conceptual revision chapter. Detailed attention mathematics, advanced diffusion mathematics, and implementation-specific image-generation workflows belong to their designated later levels.

<br/>

## 2. The Five Core Approaches at a Glance

| Approach                     | Main idea                                                                                             | What training teaches                                                    | How new output is generated                                            | Typical concern                                                                  |
| ---------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Autoregressive generation    | Predict the next element from preceding context                                                       | A conditional next-element distribution                                  | Repeatedly predict, select, and append an element                      | Sequential latency and error propagation                                         |
| Transformer-based generation | Use transformer layers to build contextual representations; the task depends on the model's objective | Task-dependent; for a decoder-only language model, next-token prediction | Depends on the system; autoregressive models generate sequentially     | Context and compute requirements; a transformer is not automatically a generator |
| VAE                          | Encode an input as a latent distribution and reconstruct it                                           | Reconstruction plus regularization toward a prior                        | Sample a latent vector from the prior and decode it                    | Reconstruction-detail trade-offs and possible posterior collapse                 |
| GAN                          | Train a generator and discriminator with competing objectives                                         | A generator that improves against discriminator feedback                 | Pass noise, optionally with a condition, through the trained generator | Training instability and mode collapse                                           |
| Diffusion                    | Learn a denoising-related prediction across noise levels                                              | A denoiser and its learned mapping from noisy states to a target         | Start from noise and iteratively denoise using a sampling procedure    | Iterative inference cost and imperfect control                                   |

**Important:** The rows are not all mutually exclusive categories. “Transformer” names an architecture, while autoregression describes a sequence modeling/generation approach. A transformer can be used for autoregressive generation or as a denoiser in a diffusion system.

<br/>

## 3. Explain Each Approach with a Diagram and Example

### 3.1 Autoregressive generation

**Example:** Complete the prompt, “The sky looks”.

```text
Prompt: "The sky looks"
        |
        v
Predict next-token distribution
        |
        v
Select "blue"
        |
        v
Updated context: "The sky looks blue"
        |
        v
Predict the next token using the updated context
        |
        v
Continue until a stopping condition is met
```

**Training:** The model learns to predict each known target token from the preceding context in training sequences. Training implementations can compute predictions for many positions in parallel.

**Generation:** The future token is not known in advance. The model predicts a distribution, a selection procedure chooses a token, and that token is added to the context.

**Key point:** Each generated token becomes part of the context that influences later predictions.

<br/>

### 3.2 Transformer-based generation

**Example:** A decoder-only transformer generates a response to “Generative AI can”.

```text
Prompt
  -> Tokenization and embeddings
  -> Decoder-only transformer with causal attention
  -> Next-token distribution
  -> Select and append token
  -> Repeat until stop
  -> Generated continuation
```

**Training:** For an autoregressive language model, the model learns next-token predictions while causal masking prevents a position from using future target tokens. Multiple known positions can be processed in parallel.

**Generation:** The selected token is appended to the context and used for the next prediction.

**Key point:** The transformer builds contextual representations; the objective and generation procedure determine what the system does. Encoder-only transformers are not automatically text generators.

<br/>

### 3.3 Variational autoencoder (VAE)

**Example:** Reconstruct a training image, or sample a latent vector to generate a new image.

```text
RECONSTRUCTION
Input image
  -> Encoder
  -> Input-conditioned latent distribution
  -> Sample latent vector
  -> Decoder
  -> Reconstruction


NEW-SAMPLE GENERATION
Prior distribution
  -> Sample latent vector
  -> Decoder
  -> New sample
```

**Training:** The encoder predicts parameters of a latent distribution. A latent sample is decoded, and training balances reconstruction loss with regularization toward a prior.

**Generation:** For a new sample, draw a latent vector from the prior and pass it through the decoder.

**Key point:** A VAE learns a distribution over latent representations, not only a fixed encoding. Prior regularization encourages useful sampling but does not guarantee perfect output quality.

<br/>

### 3.4 Generative adversarial network (GAN)

**Example:** Generate synthetic images.

```text
TRAINING
Real examples ---------------------------+
                                          |
Noise -> Generator -> Fake examples ------+-> Discriminator
                                                |
                                                v
                                         Adversarial feedback
                                                |
                                  Update discriminator/generator
                                                |
                                              Repeat
```

```text
INFERENCE
Noise (optionally + condition)
        -> Trained generator
        -> Generated sample
```

**Training:** The discriminator learns to distinguish real from generated examples. The generator is updated using adversarial feedback. Training commonly alternates between updates to the two networks.

**Generation:** The trained generator ordinarily produces new samples directly from noise, optionally combined with a condition. The discriminator is not usually required in the generation path.

**Key point:** Mode collapse means a narrow range of outputs is produced; those outputs can still look realistic individually.

<br/>

### 3.5 Diffusion models

**Example:** Generate a new image from random noise.

```text
TRAINING: FORWARD NOISING
Clean training image
  -> Add noise at a selected timestep
  -> Noisy image + timestep
  -> Denoiser predicts noise or another target
  -> Compare prediction with target
  -> Update model
```

```text
GENERATION: ITERATIVE DENOISING
Initial random noise
  -> Denoiser + sampling update
  -> Less noisy state
  -> Denoiser + sampling update
  -> Repeat
  -> Generated output
```

**Training:** A defined forward process adds noise to training data. The denoiser learns a noise-related or denoising-related prediction at different noise levels.

**Generation:** A newly sampled noisy state is iteratively updated using learned predictions and a sampling procedure.

**Key point:** Generation does not simply undo the exact noise sequence from a training image. It uses learned denoising behavior to create a plausible sample.

<br/>

## 4. Compare the Training Objectives

The training objective shapes what each approach learns.

| Concept                                | What the model is encouraged to learn                                                              | Core question                                                                                |
| -------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Next-element prediction                | Predict each next element from preceding context                                                   | “Given what came before, what could come next?”                                              |
| VAE reconstruction plus regularization | Reconstruct inputs while organizing the latent distribution toward a prior                         | “Can the model preserve input information and learn a useful probabilistic latent space?”    |
| GAN adversarial learning               | Improve generated samples against a discriminator's ability to distinguish real and generated data | “Can the generator produce samples that satisfy its objective against the discriminator?”    |
| Diffusion denoising                    | Predict noise or another denoising-related target at different noise levels                        | “Given a noisy state and timestep, what denoising-related prediction should the model make?” |

These objectives are not interchangeable. They provide different learning signals and support different generation procedures.

<br/>

### Training versus inference recap

| Approach       | Training data or input                                                         | What happens at inference                              |
| -------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------ |
| Autoregressive | Known sequences provide target next elements                                   | Generate tokens sequentially from a prompt/context     |
| VAE            | Inputs are encoded; reconstructions and latent regularization are optimized    | Reconstruct an input or sample from a prior and decode |
| GAN            | Real data and generator-produced samples train the discriminator and generator | Use the trained generator to create samples            |
| Diffusion      | Real data is corrupted at selected noise levels to train the denoiser          | Start from noise and iteratively denoise               |

<br/>

## 5. Review Latent Representations and Overlapping Categories

### 5.1 Do not treat all latent-like values as equivalent

- **VAE latent vector:** A sample from an input-conditioned latent distribution during reconstruction, or from a prior during new-sample generation.
- **GAN noise input:** A source of variation mapped by the generator into a sample. It is not automatically the same as a VAE posterior sample.
- **Latent-diffusion representation:** A learned representation of data on which the diffusion process operates, usually decoded after denoising.
- **Autoregressive token sequence:** A model can generate directly over tokens or other ordered elements without requiring a VAE-style latent distribution.

<br/>

### 5.2 Architecture, objective, and generation procedure

| Dimension                    | Example                                                                                               | What it tells you                      |
| ---------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Architecture                 | Transformer, U-Net, encoder-decoder network                                                           | How neural computations are structured |
| Learning objective/framework | Next-token prediction, VAE objective, GAN objective, diffusion denoising objective                    | What the model is trained to learn     |
| Generation procedure         | Sequential token selection, latent sampling and decoding, generator forward pass, iterative denoising | How a new output is produced           |

**Overlapping example A: Autoregressive transformer**

- Architecture: transformer.
- Objective: next-token prediction.
- Generation: sequentially predict and append tokens.

**Overlapping example B: Transformer-based diffusion model**

- Architecture: transformer denoiser.
- Objective: diffusion denoising.
- Generation: iteratively denoise a state using a sampling procedure.

The architecture label alone does not identify the model's objective or inference procedure.

<br/>

## 6. Analyze Failure Modes and Application Constraints

| Approach                  | Typical failure modes                                                                           | Constraints to assess                                                        |
| ------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Autoregressive generation | Earlier errors can influence later tokens; factual mistakes; context limitations                | Output length, context window, latency, correctness, and prompt adherence    |
| Transformer-based system  | Failure depends on its task and objective; context and compute limits may apply                 | Whether the chosen configuration actually supports the required task         |
| VAE                       | Reconstruction detail can trade off against regularization; posterior collapse in some settings | Reconstruction quality, latent usefulness, sampling quality, and compute     |
| GAN                       | Training instability and mode collapse                                                          | Output diversity, quality, stability, generator cost, and data availability  |
| Diffusion                 | Artifacts, imperfect condition adherence, expensive iterative inference                         | Sampling steps, latency, memory, output resolution, and control requirements |

<br/>

### Evaluation dimensions

Do not evaluate a generative model using only one appealing output. Consider:

- **Fidelity:** Does the output have the required quality or resemble the intended data?
- **Diversity:** Does it produce a useful range of outputs rather than repetitions?
- **Controllability:** Does it follow prompts, labels, or input conditions?
- **Correctness:** Does it meet task-specific factual, structural, or business requirements?
- **Latency and throughput:** Does it meet interactive or production needs?
- **Memory and cost:** Can it run within the available infrastructure and budget?
- **Governance:** Are licensing, data provenance, privacy, and responsible-use requirements satisfied?

No model family is universally fastest or best. The result depends on data, model size, training, implementation, hardware, sampling choices, and evaluation.

<br/>

## 7. Architecture Comparison Brief

Use this brief to justify a model choice for a practical task.

### Brief template

**1. Task and objective**

- What problem must be solved?
- What does a successful output look like?

**2. Input and output**

- What modality is provided?
- What modality and format must be returned?

**3. Candidate approach**

- Which model or system is the leading candidate?
- What architecture, objective, and generation procedure does it use?

**4. Rationale and assumptions**

- Why is it a plausible fit?
- What assumptions are being made about data, model capabilities, and conditions?

**5. Plausible alternative**

- What is at least one other approach that could meet the requirement?
- What trade-off might make it preferable or less suitable?

**6. Validation plan**

- Which representative examples will be tested?
- Which quality, diversity, control, and correctness checks will be used?
- How will latency, memory, throughput, and cost be measured?

**7. Data and governance**

- Is the model or service licensed for the intended use?
- Are data provenance, privacy, and responsible-use requirements addressed?

**8. Decision rule**

- What evidence would make you accept the candidate?
- What failure or cost threshold would make you reject it or switch alternatives?

<br/>

### Worked example: Text completion

**Task:** Generate a coherent continuation from a user's prompt.

- **Leading candidate:** An existing pretrained autoregressive language model, commonly implemented with a decoder-only transformer.
- **Rationale:** Its generation procedure predicts successive tokens from the prompt and generated context.
- **Assumptions:** The available model supports the required language, context length, and deployment terms.
- **Alternative:** An encoder-decoder model may be appropriate if the task is better framed as transforming a distinct source input into a separate output.
- **Validation:** Test representative prompts for relevance, factuality where required, completeness, format adherence, latency, cost, and failure rate. Review licensing and privacy terms.
- **Decision rule:** Select the candidate only if it meets task-specific quality and operational thresholds; otherwise test the alternative or use a hybrid with retrieval and deterministic validation.

<br/>

### Worked example: Image generation

**Task:** Generate images guided by text prompts.

- **Leading candidate:** A suitable pretrained text-conditioned diffusion model.
- **Rationale:** Diffusion models can iteratively generate image outputs while using conditioning information.
- **Assumptions:** A model is available that supports the required prompts, resolution, license, and deployment environment.
- **Alternative:** A conditional GAN may fit some image-generation tasks if its control, quality, and output diversity are adequate.
- **Validation:** Review fidelity and artifacts, test diversity across repeated runs, assess prompt adherence, and measure latency, memory, and cost.
- **Decision rule:** Choose based on the required quality-control-resource balance rather than assuming one family is universally superior.

<br/>

### Worked example: Reconstruction-based representation learning

**Task:** Learn compact representations while reconstructing input data.

- **Leading candidate:** A VAE if probabilistic latent representations and prior-based sampling are useful; an ordinary autoencoder is also a candidate if fixed encodings and reconstruction are sufficient.
- **Rationale:** Both can encode and reconstruct inputs; a VAE additionally regularizes a latent distribution.
- **Assumptions:** Reconstruction and latent representations are suitable for the downstream task.
- **Alternative:** An ordinary autoencoder may be simpler if probabilistic generation is not required.
- **Validation:** Measure reconstruction quality, evaluate latent usefulness on the downstream task, and inspect prior-sampling behavior if generation is needed.
- **Decision rule:** Choose the VAE only if the probabilistic latent structure provides value that justifies its trade-offs.

<br/>

## 8. Practice Exercises

### Exercise 1 — Identify the objective

Match each description to the best-fitting approach.

A. A model learns to predict the next token from preceding tokens.  
B. Two networks compete: one creates samples and one distinguishes real from generated examples.  
C. A model learns to reconstruct inputs while regularizing a latent distribution.  
D. A model learns a denoising-related prediction across different noise levels.

**Answers:** A — autoregressive generation; B — GAN; C — VAE; D — diffusion.

<br/>

### Exercise 2 — Separate the dimensions

A system uses a transformer to predict the next text token.

Identify:

- Architecture
- Learning objective
- Generation procedure

**Suggested answer:**

- Architecture: transformer.
- Objective: autoregressive next-token prediction.
- Generation procedure: sequential token selection and appending.

Now consider a transformer used as a diffusion denoiser.

**Suggested answer:**

- Architecture: transformer.
- Objective/framework: diffusion denoising.
- Generation procedure: iterative denoising using a sampling procedure.

<br/>

### Exercise 3 — Reconstruction or generation?

For each action, identify the path.

1. Encode a real image, sample from its input-conditioned latent distribution, and decode it.
2. Draw a latent vector from a VAE prior and decode it.
3. Start with random noise and repeatedly denoise to generate an image.
4. Feed random noise to a trained GAN generator.

**Answers:**

1. VAE reconstruction.
2. VAE new-sample generation.
3. Diffusion generation.
4. GAN generation.

<br/>

### Exercise 4 — Diagnose a failure

A GAN produces images that look realistic, but almost every output resembles the same category.

**Question:** What is the likely issue, and what should be evaluated?

**Suggested answer:** The behavior is consistent with mode collapse. Evaluate both sample fidelity and diversity/coverage; realistic individual outputs do not establish that the generator represents the range of the training distribution.

<br/>

### Exercise 5 — Make a model choice

A product team wants a generated output to be visually attractive, follow a condition, run within a strict latency budget, and use a model with acceptable licensing terms.

**Question:** Is choosing “diffusion” enough to make the decision?

**Suggested answer:** No. Diffusion is a plausible candidate family, but the team must identify an available model or service and validate quality, condition adherence, latency, memory, cost, licensing, privacy, and deployment compatibility. A faster or simpler alternative may be preferable if it meets the requirements.

<br/>

## 9. Final Revision Questions

**1. What is the key difference between autoregressive prediction and diffusion denoising?**  
Autoregressive prediction selects the next sequence element from preceding context. Diffusion generation starts from a noisy state and iteratively updates it using a learned denoising-related prediction and a sampling procedure.

**2. How does a VAE differ from a GAN?**  
A VAE uses an encoder-conditioned latent distribution and a decoder, trained with reconstruction and distribution regularization. A GAN trains a generator and discriminator with adversarial objectives.

**3. Which GAN component is ordinarily needed for inference generation?**  
The trained generator; the discriminator is ordinarily used during training rather than each generation step.

**4. Why are training and inference different for autoregressive models?**  
Training uses known sequences as targets and can compute predictions at multiple positions in parallel. Inference must select each next token before using it as context for later predictions.

**5. Why can diffusion generation be computationally expensive?**  
The sampling procedure commonly performs multiple denoising steps, each requiring model computation.

**6. Why is a transformer not synonymous with a generative approach?**  
It is an architecture that can support different objectives and procedures, including autoregressive generation and diffusion denoising.

**7. What is the difference between fidelity and diversity?**  
Fidelity concerns how well an output matches desired characteristics; diversity concerns the range of outputs the model can produce.

**8. What should a model-selection brief include?**  
Task and input/output requirements, leading candidate and rationale, assumptions, a plausible alternative, validation evidence, operational and governance constraints, and a decision rule.

**9. Why is a plausible alternative important?**  
It makes trade-offs explicit and prevents a decision from depending on an untested assumption that the leading candidate is the only viable option.

<br/>

## 10. Level 2 Completion Check

Before moving on, verify that you can:

- [ ] Explain the basic workflow of autoregressive generation, a VAE, a GAN, and a diffusion model.
- [ ] Distinguish training flow from inference/generation flow.
- [ ] Explain the roles of a generator and discriminator.
- [ ] Explain why a VAE uses a latent distribution and prior.
- [ ] Explain why diffusion generation uses learned denoising and iterative sampling.
- [ ] Explain how a transformer can support different generative procedures.
- [ ] Distinguish architecture, learning objective, and generation procedure.
- [ ] Compare fidelity, diversity, controllability, latency, memory, and cost.
- [ ] Identify licensing, data provenance, privacy, and deployment constraints.
- [ ] Defend a candidate approach and name at least one plausible alternative.

If any item is difficult, revisit the corresponding chapter before proceeding.

<br/>

## 11. Final Checkpoint

**Defend an approach selection and identify at least one plausible alternative.**

A strong response should:

1. Define the task and required input/output.
2. Explain why the chosen approach fits the task's generation procedure and conditioning needs.
3. Identify assumptions about data, available models, and deployment.
4. Name a plausible alternative and explain the trade-off.
5. Specify validation evidence for quality, diversity, control, latency, memory, cost, and governance.
6. State a decision rule for accepting the candidate or switching to the alternative.

The goal is not to memorize a universal ranking. It is to make a reasoned, testable model-selection decision.

<br/>

## 12. References

- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) — autoregressive language modeling.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — transformer architecture.
- [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — variational autoencoders.
- [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — generative adversarial networks.
- [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — diffusion models.
- [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — latent diffusion.

**Level 2 complete:** You should now be able to explain the main generative approaches, compare their workflows and trade-offs, and defend a candidate approach for a task without assuming that one family is universally best.
