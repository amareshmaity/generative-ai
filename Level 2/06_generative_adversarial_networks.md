# Chapter 06 — Generative Adversarial Networks (GANs)

## 1. Learning Objectives and Prerequisites

By the end of this chapter, you should be able to:

- Explain the roles of a GAN's generator and discriminator.
- Describe how real and generated examples are used during training.
- Trace the alternating updates and adversarial feedback loop conceptually.
- Explain how a trained generator creates outputs from noise or conditioning information.
- Identify which GAN component is ordinarily used for generation.
- Discuss realism, training instability, and mode collapse.
- Recognize conditional GANs and image translation as examples of GAN applications.

**Prerequisites:** Understand latent representations and generative models at a high level. This chapter focuses on the core GAN training concept rather than the mathematical derivation of its objective.

<br/>

## 2. Intuition: Two Networks with Different Roles

A **Generative Adversarial Network (GAN)** is a generative modeling framework built around two neural networks trained in competition.

- The **generator** creates synthetic examples intended to resemble examples from the training data.
- The **discriminator** evaluates examples and learns to distinguish real training examples from generated examples.

For example, in an image GAN, the generator may create a synthetic image of a face. The discriminator receives real images from the dataset and generated images, and learns to tell the two sources apart.

The generator is updated using feedback related to how well its outputs fool the discriminator. As training progresses, the generator aims to create more convincing samples, while the discriminator aims to become better at distinguishing real from generated data.

<br/>

### A simple analogy

Imagine an artist producing counterfeit paintings and an inspector trying to identify them. The artist improves by learning what the inspector detects; the inspector improves by examining both genuine and synthetic paintings. This analogy captures the competition, but actual GANs learn through an optimization procedure rather than conscious judgment.


<br/>


## 3. The Two Main Components

### 3.1 Generator

The generator maps an input—commonly a random noise vector, and optionally conditioning information—to a synthetic example.

Conceptually:

```text
Random noise z
      |
      v
  Generator
      |
      v
Generated sample x_fake
```

The noise provides variation. Different noise inputs can lead to different outputs, assuming the generator has learned to use that variation effectively.

A conditional generator can also receive information such as a class label, a text representation, or a source image, depending on the GAN design.

<br/>

### 3.2 Discriminator

The discriminator receives an example and produces a score or prediction indicating whether the example is real or generated, according to the model's training setup.

```text
Real sample x_real ------+
                         |
                         v
                    Discriminator
                         |
                         v
                 Real/fake prediction
                         ^
                         |
Generated sample x_fake -+
```

During training, the discriminator learns from both real examples and generated examples. The exact output representation and loss depend on the GAN variant.

<br/>

### Important distinction

The discriminator does not ordinarily generate the final data sample. It supplies a learning signal during training. In a conventional GAN after training, the **generator** is the component used to produce new samples.


<br/>


## 4. How Real and Generated Examples Enter Training

GAN training uses two sources of examples:

1. **Real examples:** samples drawn from the training dataset.
2. **Generated examples:** samples produced by the current generator.

The discriminator is trained to distinguish these two sources. The generator is trained to produce samples that improve its objective against the discriminator.

<br/>

### Conceptual training flow

```text
                         TRAINING DATA
                              |
                              v
                         Real examples
                              |
                              +--------------------+
                                                   |
                                                   v
Random noise z -> Generator -> Generated examples -> Discriminator
                                                   ^
                                                   |
Real examples -------------------------------------+
                                                   |
                                                   v
                                        Real/fake assessment
```

This sketch emphasizes that both kinds of examples are presented to the discriminator. The generator creates the fake examples; the discriminator assesses them.

The generator and discriminator have different optimization goals. Training coordinates these goals through the adversarial objective.


<br/>


## 5. Alternating Updates and Adversarial Feedback

A common conceptual GAN training loop alternates between improving the discriminator and improving the generator. The exact update schedule and objective vary by GAN design.

### Step 1: Update the discriminator

- Draw a batch of real examples from the training dataset.
- Generate a batch of synthetic examples using the current generator.
- Train the discriminator to distinguish the real examples from the generated examples.

<br/>

### Step 2: Update the generator

- Draw noise vectors and produce synthetic examples.
- Evaluate the generated examples through the discriminator.
- Update the generator so its outputs improve the generator's objective—commonly by encouraging the discriminator to classify generated examples as real.

<br/>

### Step 3: Repeat

Repeat the updates over many training iterations. The discriminator's response provides an adversarial learning signal that helps the generator adjust its parameters.

<br/>

### Conceptual loop

```text
Draw real examples + sample noise
               |
               v
       Generate fake examples
               |
               v
    Update discriminator using
      real and fake examples
               |
               v
    Update generator using
     discriminator feedback
               |
               v
          Repeat training
```

This is a simplified view. Some GAN variants use different loss functions, update ratios, regularization, or training procedures.

<br/>

### What “adversarial” means

The networks have related but competing objectives:

- The discriminator aims to distinguish real from generated samples.
- The generator aims to create samples that satisfy its objective against the discriminator.

The competition provides a training signal, but it does not guarantee that training will converge smoothly or that the final generator will cover every type of example in the dataset.


<br/>


## 6. Generation After Training

After training, ordinary GAN generation uses the generator to create samples. The discriminator is generally not required in the inference path.

### Inference diagram

```text
Sample noise z
      |
      v
Trained generator
      |
      v
Generated output
```

For a conditional GAN, the path may include a condition:

```text
Noise z + condition c
          |
          v
    Trained generator
          |
          v
    Conditioned output
```

Examples of conditions include a class label or an input image, depending on the model.

<br/>

### Why the discriminator is ordinarily unnecessary

The discriminator helps train the generator by evaluating generated examples and providing feedback. Once training is complete, the trained generator's mapping can be used directly to produce new examples. The discriminator may still be useful for evaluation or research, but it is not ordinarily needed to generate each sample.


<br/>


## 7. Conditional GANs and Image Translation

### 7.1 Conditional GANs

An unconditional GAN commonly generates samples from noise. A **conditional GAN (cGAN)** additionally uses information that guides what should be generated.

A condition might specify a category, attribute, or source input. The generator is trained to create outputs compatible with that condition, while the discriminator's design may also incorporate the condition.

Examples include:

- Generating an image associated with a specified class label.
- Producing an output image conditioned on an input image.
- Learning a mapping between related visual domains.

The condition guides generation; it does not by itself guarantee that the output will follow the condition perfectly.

<br/>

### 7.2 Image-to-image translation

Image translation uses an input image from one domain to generate a corresponding image in another domain. Examples might include translating sketches into photographs, maps into aerial-style images, or one visual style into another.

A GAN-based translation system can use a generator to map the source image to an output image, with discriminator-based feedback encouraging realistic results. The exact design depends on the task and whether paired examples are available.

Not every image-translation system is a GAN, and not every GAN performs image translation.


<br/>


## 8. Strengths, Limitations, and Common Failure Modes

### Strengths

- **Realistic samples:** GANs can learn to produce visually convincing outputs in suitable settings.
- **Direct sample generation:** after training, the generator can map noise or conditioning inputs to outputs.
- **Conditional control:** conditional designs can guide the generated output.
- **Flexible applications:** GANs have been used for image synthesis, image translation, and other data-generation tasks.

<br/>

### Limitations

- **Training instability:** the generator and discriminator must learn in balance. One network may become too strong or the optimization may oscillate.
- **Mode collapse:** the generator may produce only a limited variety of outputs, even when the training data contains many different modes or categories.
- **Evaluation challenges:** realistic individual samples do not establish that the generator covers the full data distribution.
- **Sensitivity to design:** performance can depend on architecture, objective, optimization settings, data, and regularization.
- **No guaranteed convergence:** adversarial competition does not ensure stable training or a perfect generator.

<br/>

### 8.1 Mode collapse

Mode collapse occurs when a generator produces a narrow range of outputs instead of representing the diversity of the training distribution.

Imagine a dataset containing many different kinds of birds. A collapsed generator might produce images resembling only one type of bird, or even near-duplicates, regardless of different noise inputs.

The outputs might look realistic individually, yet the generator would fail to represent the range of examples in the data.

<br/>

### Mode collapse vs. successful diverse generation

| Property | Successful diverse generator | Generator with mode collapse |
|---|---|---|
| Realism | Outputs may look realistic | Some outputs may also look realistic |
| Diversity | Covers a broad range of relevant patterns | Produces a limited set of patterns |
| Response to different noise inputs | Can produce meaningfully varied outputs | Different inputs may lead to similar outputs |
| Coverage of the data distribution | Better coverage, though never assumed perfect | Important modes or categories are missing |

**Key point:** Realism and diversity are different qualities. A generator can create convincing examples while still failing to cover the variety of the training data.

<br/>

### 8.2 Training instability

GAN training is a coupled optimization problem. If the discriminator becomes very effective too early, the generator may receive an unhelpful learning signal in some setups. If the generator improves faster than the discriminator, the discriminator may not provide sufficiently informative feedback. Oscillations and sensitivity to hyperparameters can also occur.

These are high-level patterns, not a complete diagnostic guide. Different GAN variants address instability in different ways.

<br/>

### Common misconceptions

- **Misconception:** “The discriminator generates the samples.”  
  **Correction:** The generator creates the samples; the discriminator assesses them during training.

- **Misconception:** “The discriminator is always needed during inference.”  
  **Correction:** Ordinary GAN generation uses the trained generator directly.

- **Misconception:** “If generated images look realistic, the GAN has succeeded completely.”  
  **Correction:** Realism alone does not establish diversity or coverage of the data distribution.

- **Misconception:** “Mode collapse means every generated output looks obviously fake.”  
  **Correction:** Outputs can be realistic but repetitive or insufficiently diverse.

- **Misconception:** “Every GAN generates only from random noise.”  
  **Correction:** Conditional GANs also use conditions such as labels or input images.


<br/>


## 9. Practice: Draw the Training Loop and Inference Path

Draw two separate diagrams. Keep training and inference distinct.

### A. Training loop

Include:

1. Real examples from the dataset
2. Random noise (and condition, if applicable)
3. Generator creates fake examples
4. Discriminator assesses real and fake examples
5. Discriminator update
6. Generator update using adversarial feedback
7. Repeat

<br/>

### B. Inference path

Include:

1. Random noise, optionally with a condition
2. Trained generator
3. Generated output

Do not put the discriminator in the ordinary inference path unless your particular application explicitly uses it.

<br/>

### Suggested answer

```text
TRAINING

Real dataset examples ----------------------+
                                            |
Noise z -> Generator -> Fake examples ------+--> Discriminator
                                                   |
                                                   v
                                          Real/fake feedback
                                                   |
                          +------------------------+
                          |                         |
                          v                         v
                 Update discriminator       Update generator
                          |                         |
                          +----------- Repeat -----+
```

```text
INFERENCE

Noise z ( + condition c )
          |
          v
    Trained generator
          |
          v
    Generated sample
```

The training diagram contains both networks and the feedback loop. The inference diagram ordinarily contains only the trained generator and its input.

<br/>


## 10. Revision Questions

**1. What are the roles of the generator and discriminator?**  
The generator creates synthetic examples; the discriminator learns to distinguish real examples from generated examples during training.

**2. Which examples does the discriminator use during training?**  
Both real examples from the dataset and generated examples from the current generator.

**3. What is adversarial feedback?**  
The discriminator's response supplies a learning signal used to improve the generator's outputs against the discriminator's objective.

**4. Which GAN component is ordinarily used for generation after training?**  
The generator.

**5. What is a conditional GAN?**  
A GAN in which generation is guided by additional information, such as a label or source image.

**6. What is mode collapse?**  
A failure mode in which the generator produces a limited variety of outputs and misses important modes of the training distribution.

**7. Why is realism alone insufficient to evaluate a GAN?**  
Individual outputs may look convincing while the generator produces repetitive samples or fails to cover the data's diversity.

**8. Why can GAN training be unstable?**  
The generator and discriminator are coupled, competing networks whose learning dynamics can become unbalanced or oscillate.


<br/>


## 11. Summary and Checkpoint

### Summary

- A GAN trains a generator and discriminator in an adversarial framework.
- The generator creates synthetic examples; the discriminator compares real and generated examples.
- Training commonly alternates between updating the discriminator and updating the generator using adversarial feedback.
- After training, the generator is ordinarily sufficient for generating new samples from noise or from noise plus a condition.
- Conditional GANs guide generation with additional information and can be used for tasks such as image translation.
- GANs can produce realistic outputs but may suffer from instability and mode collapse.
- Mode collapse is primarily a diversity and distribution-coverage problem; its outputs may still look realistic.

<br/>

### Checkpoint

**Distinguish mode collapse from a successful generator covering diverse examples.**

A strong answer should explain that a successful generator produces a varied range of outputs representing different patterns in the training distribution. In mode collapse, the generator repeatedly produces a narrow subset of outputs and misses other modes. Individual samples may still appear realistic, so diversity and coverage must be considered separately from realism.


<br/>


## 12. References and Optional Extensions

- [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — the original GAN paper by Ian Goodfellow and colleagues.
- [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784) — introduces conditioning information into GAN generation.
- [Image-to-Image Translation with Conditional Adversarial Networks](https://arxiv.org/abs/1611.07004) — a prominent example of GAN-based image translation.

**Optional extension:** Later, study GAN loss functions, common stabilization methods, and quantitative evaluation of sample quality and diversity if your projects require deeper GAN engineering.

**Next chapter:** `07_diffusion_models.md`
