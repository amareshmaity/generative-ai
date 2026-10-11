# Chapter 07 — Diffusion Models

## 1. Learning Objectives and Prerequisites

By the end of this chapter, you should be able to:

- Trace gradual noise addition during the forward training process.
- Explain at a high level how a model learns to predict noise or another denoising target.
- Trace iterative generation from noise using a learned denoiser and sampling procedure.
- Distinguish training timesteps from inference sampling steps.
- Describe conditioning, guidance, and noise schedules conceptually.
- Compare diffusion in data space with diffusion in a learned latent space.
- Discuss quality, compute, latency, and controllability trade-offs.
- Recognize that a denoiser may use a U-Net or transformer architecture.

**Prerequisites:** Understand the distinction between training and inference, latent representations, and generative models such as VAEs and GANs. This chapter explains the main workflow without detailed diffusion mathematics.

**Depth boundary:** Image-generation APIs, practical scheduler configuration, inpainting, and advanced control methods belong to Level 10. Detailed mathematics and related flow-based approaches are optional extensions.


<br/>


## 2. Intuition: Learning to Denoise

A diffusion model is a generative model that learns to produce data by reversing a gradual corruption process.

Imagine starting with a clear image and repeatedly adding small amounts of random noise. After enough steps, the image becomes difficult or impossible to recognize. During training, a neural network learns to estimate the noise or another target that helps recover a less noisy version of the data.

For generation, the process begins with random noise. A learned denoiser and a sampling procedure repeatedly transform the current noisy state into a state that is expected to be closer to a plausible sample. After multiple steps, the process produces a generated output.

**Core intuition:** Training teaches the model how to denoise corrupted data at different noise levels. Generation applies that learned behavior iteratively, starting from noise.

This is not simply a matter of replaying a known noise sequence backward. The exact random noise added during training is generally not available for a new sample at inference time. The model has learned a denoising relationship from many examples and uses that learned relationship during generation.


<br/>


## 3. The Forward Process: Gradually Adding Noise

The **forward noising process** starts with a real training example and progressively adds noise according to a defined noise schedule.

For an image, the stages might look conceptually like this:

```text
Clean training image
        |
        v
Image with a small amount of noise
        |
        v
Image with more noise
        |
        v
Image with still more noise
        |
        v
Nearly pure noise
```

The forward process is designed and specified by the model's training setup. It is not the neural network learning how to add noise. Instead, the training procedure uses this known corruption process to construct noisy inputs for the denoiser to learn from.

<br/>

### Why add noise gradually?

Training across different noise levels teaches the model to handle different degrees of corruption. At a low noise level, much of the original structure may remain visible. At a high noise level, the input contains much less directly recognizable information.

The exact mathematical formulation and the number of training timesteps depend on the diffusion method. For this chapter, the important point is that the model sees noisy versions of training examples at different stages of the schedule.

<br/>

### What is a noise schedule?

A **noise schedule** specifies how the amount or scale of noise changes across forward timesteps. It controls the progression from relatively clean data toward a highly corrupted state.

Different schedules can affect training behavior and the quality or efficiency of generation. A schedule is part of the diffusion setup; it is not the same thing as the denoising neural-network architecture.


<br/>


## 4. Learning a Denoising Target

During training, a noisy example is provided to a neural network along with information about the current noise level or timestep. The network is trained to predict a target associated with that corruption process.

In many diffusion models, the target is the noise added to the original example. Other formulations can predict a different denoising-related quantity. The exact target depends on the method.

<br/>

### Conceptual training flow

```text
Clean training example
        |
        v
Add noise at a selected timestep
        |
        +----> Record the training target
        |
        v
Noisy example + timestep information
        |
        v
Neural-network denoiser
        |
        v
Predicted noise or other target
        |
        v
Compare prediction with target
        |
        v
Update model parameters
```

The model learns from many examples and noise levels. It is not simply memorizing a separate reverse path for each training image; it learns a denoising function that can be applied to new noisy states.

<br/>

### The denoiser is not necessarily a specific architecture

The denoising network may use a **U-Net**, a **transformer**, or another suitable architecture. The diffusion process describes the generative framework, while U-Net and transformer describe possible neural-network architectures used within that framework.


<br/>


## 5. The Reverse Process: Generating from Noise

At inference time, the model generates a new sample by starting with a noise-like state and repeatedly applying the learned denoiser according to a sampling procedure.

### Conceptual generation flow

```text
Initial random noise
        |
        v
Denoiser at current timestep
        |
        v
Sampling procedure updates the state
        |
        v
Less noisy state
        |
        v
Denoiser at next step
        |
        v
Sampling procedure updates the state
        |
       ...
        |
        v
Final generated sample
```

At each step, the denoiser estimates a noise-related or denoising-related target. The sampling procedure uses that prediction, the current state, and the timestep information to compute the next state.

The denoiser and sampler have related but distinct roles:

- **Denoiser:** predicts the quantity the model was trained to estimate.
- **Sampling procedure:** determines how the current state is updated to move toward the final sample.

The final result depends on the learned model, the sampling method, conditioning information, and other settings.

<br/>

### Why this is not simply reversing the original noise

During training, the forward process corrupts real examples using known noise operations. During generation, the initial state is a newly sampled noise-like input, not a clean training image corrupted along a known path. The exact sequence of noise values from a training example is not available to reverse.

Instead, the learned denoiser estimates how a noisy state relates to the data distribution. The sampling procedure uses these estimates to iteratively produce a plausible sample. It does not recover a unique original image from arbitrary noise.


<br/>


## 6. Training Timesteps vs. Inference Sampling Steps

The terms *training timesteps* and *inference sampling steps* are related but should not be treated as identical.

### Training timesteps

Training uses a defined range of noise levels or timesteps. During training, examples are corrupted at selected timesteps, and the denoiser learns to predict the corresponding target. The model can learn across many noise levels without running a complete generation trajectory for every training example.

<br/>

### Inference sampling steps

Inference uses a sampling procedure to move from an initial noisy state toward an output. The number of inference steps may be different from the number of timesteps used in the training formulation. Some samplers use a subset or a different spacing of timesteps to reduce generation cost.

| Aspect | Training timesteps | Inference sampling steps |
|---|---|---|
| Purpose | Teach the denoiser across noise levels | Iteratively create a sample |
| Input | Noisy versions of real training data | Current noisy state, often beginning with random noise |
| Model activity | Predict training targets and update parameters | Predict denoising-related targets using trained parameters |
| Relationship | Defined by the training formulation | Chosen by the inference sampling procedure |
| Must the counts match? | Not necessarily | Not necessarily |

A smaller number of inference steps can reduce latency, but the effect on output quality depends on the model and sampler. Fewer steps do not automatically preserve the same quality.


<br/>


## 7. Conditioning and Guidance

A diffusion model can be **unconditional** or **conditional**.

- **Unconditional generation:** the model generates according to its learned data distribution without a specific external condition such as a text prompt.
- **Conditional generation:** the model uses additional information to guide the generated output.

Possible conditions include text, class labels, an input image, or other task-specific information. The model's architecture and training setup determine how the condition is supplied.

<br/>

### Conditioning

Conditioning gives the denoising process information about the intended output. For example, a text-conditioned image model can use a prompt representation while denoising so that the resulting image is guided by the text.

<br/>

### Guidance

**Guidance** refers broadly to techniques that steer the generation process toward a condition or desired behavior. In text-to-image diffusion, guidance can influence how strongly the output follows the prompt. The specific method and trade-offs depend on the model.

Guidance is not a guarantee of exact compliance. Stronger steering may improve alignment with a condition in some settings, but it can also affect diversity, artifacts, or other aspects of quality.

<br/>

### Conceptual conditional generation

```text
Random noise -------------------+
                                |
Condition (e.g., text prompt) --> Denoising process
                                |
                                v
                       Generated output
```

The condition influences the denoising process across its steps; it is not necessarily appended to the final image or output as ordinary text.


<br/>


## 8. Diffusion in Data Space vs. Latent Space

Diffusion can operate directly on data representations or on a learned latent representation.

### 8.1 Data-space diffusion

The forward noising process acts directly on the data representation, such as image pixels. The denoiser works on noisy versions of that representation, and generation produces an output in that same representation space.

```text
Image data
   -> Add noise in image space
   -> Learn to denoise image representations
   -> Generate image from noise
```

Working directly in data space can require substantial computation for high-dimensional data such as large images.

<br/>

### 8.2 Latent diffusion

A latent-diffusion system uses a separate encoder-decoder, commonly an autoencoder, to work with a more compact representation.

A simplified workflow is:

```text
TRAINING
Image -> Encoder -> Latent representation
                         |
                         v
                   Add noise in latent space
                         |
                         v
                Train latent-space denoiser


GENERATION
Latent noise
     |
     v
Latent-space denoising process
     |
     v
Generated latent representation
     |
     v
Decoder
     |
     v
Generated image
```

The diffusion process takes place in latent space rather than directly in pixel space. The decoder maps the final latent representation back to image space.

This is different from treating every latent vector as interchangeable with VAE noise or a GAN's input noise. A latent-diffusion representation is a learned representation of data on which the diffusion process operates; the exact design depends on the system.

<br/>

### Comparison

| Aspect | Data-space diffusion | Latent diffusion |
|---|---|---|
| Where noise is added | Directly to the data representation | To a learned latent representation |
| Denoiser input | Noisy data-space representation | Noisy latent representation |
| Final output path | Denoised data representation | Denoised latent representation followed by decoding |
| Main trade-off | Can be computationally demanding for high-dimensional data | Can reduce denoising cost, but depends on the representation and decoder |
| Potential limitation | Expensive processing at high resolution | Compression or decoder limitations can affect output fidelity |

Latent diffusion is not automatically superior in every case. The trade-off depends on the quality of the learned representation, the denoiser, and the application.


<br/>

## 9. Quality, Compute, Latency, and Controllability

Diffusion models can generate high-quality and diverse outputs, but the iterative sampling process introduces costs and trade-offs.

### Quality

Repeated denoising can gradually shape a noisy state into a coherent output. The result depends on the model, training data, sampling procedure, conditioning, and number of inference steps. High quality is not guaranteed for every prompt or random seed.

<br/>

### Compute and memory

Denoising repeatedly calls a neural network. Large models, high-resolution outputs, and long or complex conditioning inputs can increase computational and memory requirements. Latent diffusion can reduce the size of the representation processed during denoising, although the encoder and decoder also have costs.

<br/>

### Latency

Generation commonly requires multiple denoising steps. More steps often mean more model evaluations and higher latency, though specific samplers and implementations differ. Reducing the step count can improve speed but may affect quality.

<br/>

### Controllability

Conditions and guidance can steer outputs toward a requested class, prompt, or source input. Control is not perfect: outputs can omit details, misinterpret prompts, or contain artifacts. The degree of control depends on the training data, conditioning method, model, and sampling setup.

<br/>

### Summary of trade-offs

| Design choice | Potential benefit | Potential cost or limitation |
|---|---|---|
| More inference steps | May improve sample quality in some settings | More model evaluations and latency |
| Higher output resolution | More spatial detail may be possible | Higher compute and memory demand |
| Latent-space denoising | Lower-dimensional denoising can be more efficient | Representation and decoder may limit fidelity |
| Stronger guidance | May increase alignment with a condition | Can affect diversity or introduce artifacts |
| Larger denoiser | May increase capacity | Greater compute, memory, and deployment cost |

These are general tendencies rather than guarantees. Actual results must be evaluated for the chosen model and task.


<br/>


## 10. Strengths, Limitations, and Common Misconceptions

### Strengths

- **High-quality synthesis:** diffusion models can produce detailed outputs in suitable settings.
- **Diversity:** random initial states and sampling can yield varied outputs.
- **Flexible conditioning:** models can be designed to use prompts, labels, images, or other conditions.
- **Multiple representation choices:** diffusion can operate in data space or in learned latent space.
- **Architectural flexibility:** denoisers may use U-Nets, transformers, or other suitable networks.

<br/>

### Limitations

- **Iterative generation cost:** multiple denoising steps can make inference slower than a single-pass generator.
- **Resource requirements:** large denoisers and high-resolution outputs can be expensive.
- **Imperfect control:** conditions guide generation but do not guarantee exact results.
- **Representation limitations:** latent diffusion depends on the quality and capacity of its learned representation and decoder.
- **Sampling sensitivity:** quality and latency depend on the sampling method and its settings.

<br/>

### Common misconceptions

- **Misconception:** “A diffusion model simply subtracts the exact noise added to a training image.”  
  **Correction:** The model learns a denoising-related prediction from many noisy examples. At generation time, it starts from a new noise sample and uses learned predictions with a sampling procedure.

- **Misconception:** “The denoiser and sampler are the same thing.”  
  **Correction:** The denoiser predicts a target; the sampler uses that prediction to update the state.

- **Misconception:** “Training timesteps and inference steps must be equal.”  
  **Correction:** They are related, but inference can use a different set or number of sampling steps.

- **Misconception:** “Every diffusion model works directly on pixels.”  
  **Correction:** Latent-diffusion systems perform the iterative process on learned latent representations and decode the result afterward.

- **Misconception:** “All diffusion denoisers use a U-Net.”  
  **Correction:** U-Nets are common, but transformers and other architectures can also be used.

- **Misconception:** “A text prompt guarantees the exact image requested.”  
  **Correction:** Conditioning and guidance steer the output but do not guarantee perfect adherence.


<br/>


## 11. Practice: Annotate Forward Noising and Reverse Generation

Draw a two-part diagram and label the direction of each process.

### A. Forward process during training

Include:

1. Clean training example
2. Noise added according to a schedule
3. Intermediate noisy states
4. Highly noisy state
5. Noisy example and timestep supplied to the denoiser during training
6. Predicted target compared with the training target

<br/>

### B. Generation through denoising

Include:

1. Initial random noise
2. Denoiser using the current state and timestep
3. Sampling procedure updates the state
4. Repeated denoising steps
5. Final generated output
6. Optional condition influencing the denoising process

<br/>

### Suggested answer

```text
FORWARD NOISING — TRAINING

Clean example
     |
     | Add noise using the forward schedule
     v
Partly noisy example
     |
     | Add more noise
     v
More noisy example
     |
     | Continue across timesteps
     v
Highly noisy example

At a selected timestep:
Noisy example + timestep
     -> Denoiser
     -> Predicted noise/target
     -> Compare with known training target
     -> Update model
```

```text
GENERATION — INFERENCE

Initial random noise
     |
     v
Denoiser(current state, timestep, optional condition)
     |
     v
Sampling procedure updates state
     |
     v
New state for next step
     |
     +----> Repeat denoising
     |
     v
Final generated sample
```

The forward process constructs training inputs by adding noise to real data. Generation begins with noise and repeatedly uses learned denoising predictions; it does not require the original noise sequence from a training example.


<br/>


## 12. Revision Questions

**1. What happens in the forward process?**  
A defined process gradually adds noise to real training examples according to a noise schedule.

**2. What does the denoiser learn?**  
It learns to predict noise or another denoising-related target from noisy inputs and timestep information.

**3. How does diffusion generation begin?**  
It commonly begins with a random noise-like state and iteratively applies a learned denoiser and a sampling procedure.

**4. What is the difference between a denoiser and a sampler?**  
The denoiser predicts a target; the sampler uses the prediction to calculate the next state.

**5. Must inference sampling steps equal training timesteps?**  
No. A sampling procedure may use a different number or selection of timesteps.

**6. What is conditioning?**  
Additional information, such as a text prompt or class label, that guides the denoising process toward a desired output.

**7. How does latent diffusion differ from data-space diffusion?**  
Latent diffusion adds and removes noise in a learned latent representation and decodes the final latent output, whereas data-space diffusion operates directly on the data representation.

**8. Why can diffusion generation be slow?**  
It commonly requires multiple sequential denoising evaluations, each of which consumes computation.

**9. Which architectures can be used as a denoiser?**  
U-Nets, transformers, and other architectures suited to the model and task.


<br/>


## 13. Summary and Checkpoint

### Summary

- Diffusion models learn a generative process using a forward noising process and a learned denoising process.
- During training, noise is added to real data at selected timesteps, and a denoiser learns to predict noise or another target.
- During inference, generation starts from random noise and repeatedly uses the denoiser and sampling procedure to produce a sample.
- Training timesteps and inference sampling steps are related but need not have the same count.
- Conditioning and guidance can steer generation, but exact adherence is not guaranteed.
- Diffusion can operate directly in data space or in a learned latent space.
- Iterative denoising can support high-quality generation but may increase latency and computational cost.
- U-Nets and transformers are both possible denoiser architectures.

<br/>

### Checkpoint

**Explain why generation involves learned denoising rather than simply undoing a known noise sequence.**

A strong answer should explain that the forward process adds noise to training examples, but inference begins with a newly sampled noise-like state rather than a known corrupted version of a particular original image. The model has learned a denoising-related prediction from many noisy training examples. At each inference step, a sampling procedure uses that prediction to update the current state. Repeating this process produces a plausible sample, but it does not recover a unique original image or reverse the exact noise sequence from training.


<br/>

## 14. References and Optional Extensions

- [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — a foundational paper on diffusion-based generation.
- [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — introduces latent diffusion for high-resolution image synthesis.
- [Scalable Diffusion Models with Transformers](https://arxiv.org/abs/2212.09748) — an example of using transformer architectures for diffusion denoising.

**Level 10 boundary:** Practical image-generation APIs, scheduler selection, inpainting, and advanced control methods are covered later in Level 10. Detailed derivations and flow-based generative approaches are optional extensions.

**Next chapter:** `08_comparing_generative_approaches.md`
