# Chapter 05 — Variational Autoencoders (VAEs)

## 1. Learning Objectives and Prerequisites

By the end of this chapter, you should be able to:

- Compare ordinary autoencoders with variational autoencoders (VAEs).
- Trace the encoder, latent distribution, sampling, and decoder.
- Explain reconstruction loss and distribution regularization conceptually.
- Describe the reparameterization trick as a training technique, without deriving it.
- Distinguish input reconstruction from generating a new sample through latent sampling.
- Explain prior sampling and latent-space interpolation.
- Recognize the reconstruction-quality trade-off and posterior collapse at a high level.
- Identify applications in representation learning and generative pipelines.

**Prerequisites:** Understand the difference between an input representation and a latent representation, as introduced in Chapter 02. Detailed probability derivations and optimization mathematics are outside this chapter's scope.

<br/>

## 2. Intuition: From Autoencoders to VAEs

An autoencoder learns to compress an input into a latent representation and then reconstruct the input from that representation.

For example, an image is passed through an encoder that produces a compact representation. A decoder uses that representation to reconstruct the image. Training usually encourages the reconstruction to resemble the original input.

A **variational autoencoder (VAE)** is a generative model that makes the latent representation probabilistic. Rather than mapping an input only to one fixed latent vector, its encoder predicts a probability distribution over possible latent vectors. The model can sample from this distribution and decode the sample.

This probabilistic design gives the model a principled way to sample latent representations for generation.

<br/>

### Ordinary autoencoder vs. VAE

| Aspect | Ordinary autoencoder | Variational autoencoder |
|---|---|---|
| Encoder output | Commonly a fixed latent vector | Parameters describing a latent probability distribution |
| Latent representation | A learned code for an input | A distribution from which a latent vector can be sampled |
| Training focus | Reconstruct the input | Reconstruct the input while regularizing the latent distribution |
| New-sample generation | Not automatically supported by a well-behaved sampling procedure | Can sample from a chosen prior and decode the sample |
| Latent-space organization | Depends on the training objective and data | Distribution regularization encourages latent codes to follow a chosen prior approximately |

An ordinary autoencoder can be adapted for generation, but its latent space is not automatically organized to make arbitrary samples from a simple prior decode into plausible data. VAEs explicitly include a distribution-regularization objective to encourage a more structured latent space.


<br/>


## 3. The VAE Components

A VAE has four key conceptual stages.

### 3.1 Encoder

The encoder receives an input $x$ and produces parameters of a latent probability distribution, commonly a mean vector and a variance-related vector.

Instead of saying, “This input is exactly latent vector $z$,” the encoder represents uncertainty about the latent code with a distribution such as:

$$
q_\phi(z \mid x)
$$

Read this as: the encoder's approximate distribution over latent variables $z$, given input $x$. The symbol $\phi$ represents encoder parameters.

For a common VAE design, the distribution is Gaussian. The encoder outputs parameters such as its mean and variance; it does not need to output every possible latent vector.

<br/>

### 3.2 Latent distribution

The latent distribution describes plausible latent vectors for the input. A sample from it is used as the decoder's latent input.

The model also defines a prior distribution $p(z)$, often a standard normal distribution. During training, regularization encourages the input-conditioned latent distributions to stay reasonably close to this prior.

The approximate posterior $q_\phi(z \mid x)$ and the prior \(p(z)$ play different roles:

- $q_\phi(z \mid x)$: the encoder's distribution for a particular input.
- $p(z)$: the reference distribution used to organize the latent space and support new-sample generation.

<br/>

### 3.3 Sampling

A latent vector $z$ is sampled from the encoder's distribution during reconstruction training. The decoder then uses this vector to reconstruct the input.

The sampled vector can vary across runs, even for the same input, because the encoder represents a distribution rather than only a single fixed code.

<br/>

### 3.4 Decoder

The decoder maps a latent vector back into the data space, producing a reconstruction or generated sample.

For an image VAE, the decoder may output pixel values or parameters of a distribution over pixels. For other domains, its output representation depends on the data and model design.

<br/>

### Conceptual architecture

```text
Input x
   |
   v
Encoder
   |
   v
Latent distribution parameters
(e.g., mean and variance)
   |
   v
Sample latent vector z
   |
   v
Decoder
   |
   v
Reconstruction x_hat
```

The encoder maps from the data space to a latent distribution; the decoder maps a sampled latent vector back toward the data space.


<br/>


## 4. Training Objective: Reconstruction and Distribution Regularization

A VAE balances two conceptual goals.

### 4.1 Reconstruction loss

Reconstruction loss measures how different the decoder's output is from the original input. It encourages the model to preserve information needed to reconstruct the data.

The exact loss depends on the data type and likelihood model. For example, a model may use a suitable pixel-level reconstruction objective for images or another likelihood-based objective for different data.

If reconstruction loss is the only objective, the model may learn codes that reconstruct training inputs well without organizing the latent space into a useful distribution for generation.

<br/>

### 4.2 Distribution regularization

The VAE also regularizes the encoder's latent distribution toward a prior, often a standard normal distribution. This is commonly expressed using a divergence measure between the approximate posterior and the prior.

Conceptually, this discourages the encoder from placing every input in an unrelated, arbitrary region of latent space. It encourages a latent organization in which sampling from the prior can produce latent vectors the decoder has learned to use.

This regularization does not guarantee that every prior sample will produce a perfect or realistic output. It is a training objective that encourages useful behavior.

<br/>

### 4.3 The trade-off

The two objectives can compete:

- Emphasizing reconstruction can encourage the model to preserve more input-specific detail.
- Stronger distribution regularization can encourage a more organized latent space, but may limit how much input-specific information is retained.

A VAE therefore balances faithful reconstruction with a latent space suitable for probabilistic sampling. The best balance depends on the task and model.

<br/>

### Simplified objective

A common conceptual description of the VAE objective is:

$$
\text{Objective} \approx
\text{Reconstruction loss}
+
\text{Distribution regularization}
$$

In the usual evidence lower bound formulation, the terms are arranged so that training improves reconstruction while penalizing divergence between the approximate posterior and the prior. The equation above is a conceptual summary, not a full derivation or a specification of exact signs and scaling.

<br/>

## 5. The Reparameterization Trick

Sampling appears to create a challenge during training: a model needs to learn encoder parameters even though sampling is a stochastic operation.

The **reparameterization trick** expresses a latent sample as a differentiable transformation of the encoder's parameters and an auxiliary random variable. In a common Gaussian VAE, the encoder predicts a mean and a scale, and random noise is used to form the latent sample.

Conceptually:

```text
Encoder predicts distribution parameters
                |
                v
Draw auxiliary random noise
                |
                v
Combine parameters and noise
                |
                v
Obtain sampled latent vector z
                |
                v
Decode and calculate training loss
```

This formulation lets gradient-based optimization update the encoder and decoder through the sampling pathway. The random noise supplies stochasticity, while the distribution parameters remain part of the differentiable computation.

**What to remember:** The trick makes stochastic latent sampling compatible with the usual gradient-based training process. You do not need to derive the equation here.


<br/>


## 6. Reconstruction vs. Generating a New Sample

These two paths use the same encoder-decoder components but begin differently.

### 6.1 Reconstruction path

A reconstruction starts with a real input. The encoder produces a latent distribution, a latent vector is sampled from it, and the decoder reconstructs the input.

```text
Existing input x
      |
      v
Encoder -> latent distribution
      |
      v
Sample z from q(z | x)
      |
      v
Decoder
      |
      v
Reconstruction x_hat
```

The purpose is to reproduce the input's important characteristics. The reconstruction may differ from the original because of information loss, stochastic sampling, model capacity, and the training objective.

<br/>

### 6.2 New-sample generation path

New-sample generation does not require an existing input to encode. Instead, a latent vector is sampled from the model's prior and passed to the decoder.

```text
Sample z from prior p(z)
          |
          v
        Decoder
          |
          v
    Generated sample
```

For a common VAE, the prior is a standard normal distribution. The decoder has been trained on latent vectors drawn from encoder distributions that were encouraged to align with this prior.

This alignment is what makes prior sampling useful. It does not mean every random sample will decode into a high-quality result.

<br/>

### Key distinction

| Question | Reconstruction | New-sample generation |
|---|---|---|
| Starting point | Existing data input | Sample from the prior |
| Encoder required for that path? | Yes | Not necessarily |
| Latent source | Encoder's distribution conditioned on the input | Prior distribution |
| Goal | Reproduce an input | Produce a new sample |
| Is the output identical to training data guaranteed? | No | No |


<br/>


## 7. Prior Sampling and Latent-Space Interpolation

### 7.1 Prior sampling

A prior distribution provides a rule for drawing latent vectors. The decoder transforms these vectors into generated outputs.

For example, if $z$ is sampled from a standard normal prior, the decoder maps that vector to a candidate sample. Repeated draws can produce different outputs.

Prior sampling is central to a VAE's generative use. The model's distribution regularization encourages the decoder to work with latent vectors from regions represented by the prior, though output quality still depends on the model and training.

<br/>

### 7.2 Interpolation

Latent-space interpolation explores points between two latent vectors. A simple linear interpolation is:

$$
z_\alpha = (1-\alpha)z_a + \alpha z_b,
\qquad 0 \leq \alpha \leq 1
$$

- When $\alpha=0$, the interpolated vector is $z_a$.
- When $\alpha=1$, the interpolated vector is $z_b$.
- Intermediate values produce points between them in the latent space.

The decoder can generate outputs for these intermediate vectors. If the latent space is organized well, the outputs may change gradually and meaningfully.

However, smooth interpolation is not guaranteed for every model or every pair of points. Linear interpolation may pass through regions that are poorly represented, and visual smoothness does not necessarily imply semantic consistency.


<br/>


## 8. Limitations and Common Concepts

### 8.1 Reconstruction-quality trade-off

A VAE's probabilistic regularization can make its latent space useful for sampling, but it may also make reconstructions less detailed than desired for some tasks. The result depends on the model architecture, data, likelihood assumptions, and balance between reconstruction and regularization.

Do not interpret this as a rule that every VAE produces blurry outputs. It is a known trade-off in many common VAE setups, particularly in some image-generation settings.

<br/>

### 8.2 Posterior collapse

**Posterior collapse** is a failure mode in which the encoder's approximate posterior becomes very similar to the prior for many inputs, so the latent variable carries little input-specific information.

At a high level, the decoder then behaves as though it has little need to use the latent code. The model may reconstruct or generate outputs without making effective use of the information the encoder was intended to provide.

Posterior collapse is not the same as ordinary reconstruction error. It specifically concerns the latent representation becoming uninformative. It can arise in some model designs and training settings; it is not inevitable in every VAE.

<br/>

### 8.3 Other limitations

- **Sampling variability:** different latent samples can produce different outputs.
- **Prior mismatch:** the learned latent distributions may not align perfectly with the chosen prior.
- **Limited fidelity:** model capacity and the training objective may restrict output detail.
- **Evaluation difficulty:** good reconstructions do not alone prove that prior-generated samples are diverse or high quality.

<br/>

### Common misconceptions

- **Misconception:** “A VAE encoder returns one fixed code, just like every ordinary autoencoder.”  
  **Correction:** A standard VAE encoder predicts parameters of a latent distribution from which a code can be sampled.

- **Misconception:** “The prior and the encoder's distribution are identical.”  
  **Correction:** The encoder produces an input-conditioned approximate posterior; the prior is a reference distribution. Training encourages them to be close, not necessarily identical.

- **Misconception:** “Reconstruction and generation are the same operation.”  
  **Correction:** Reconstruction begins with an input and encodes it; new-sample generation can begin by sampling directly from the prior.

- **Misconception:** “Every prior sample must produce a realistic output.”  
  **Correction:** Prior regularization encourages useful sampling, but output quality is not guaranteed.

- **Misconception:** “Posterior collapse means the decoder reconstructs poorly.”  
  **Correction:** It means the latent variable carries little input-specific information. Reconstruction quality and posterior collapse are related only indirectly and should not be treated as the same issue.


<br/>


## 9. Applications

VAEs are used or studied in several kinds of generative and representation-learning workflows.

| Application | How a VAE can help |
|---|---|
| Representation learning | Learn compact probabilistic latent representations of data |
| Reconstruction | Encode an input and decode a reconstruction |
| New-sample generation | Sample from a prior and decode a new candidate sample |
| Latent-space exploration | Interpolate between latent vectors and inspect generated changes |
| Anomaly-related workflows | Use reconstruction behavior or latent likelihood-related signals as one possible feature; suitability depends on the specific method and evaluation |
| Generative pipelines | Provide latent representations or components used alongside other generative methods |

These are possible uses, not guarantees of performance. For anomaly detection in particular, reconstruction error alone may not reliably identify every anomaly; the approach needs task-specific validation.


<br/>


## 10. Practice: Draw Two Separate Paths

Draw both diagrams and label the source of the latent vector.

### A. Reconstruction path

Include:

1. Existing input
2. Encoder
3. Latent distribution parameters
4. Sampling from the input-conditioned distribution
5. Decoder
6. Reconstruction

### B. New-sample generation path

Include:

1. Prior distribution
2. Sample a latent vector
3. Decoder
4. Generated sample

### Suggested answer

```text
RECONSTRUCTION

Input x
  -> Encoder
  -> Parameters of q(z | x)
  -> Sample z
  -> Decoder
  -> Reconstruction x_hat
```

```text
NEW-SAMPLE GENERATION

Prior p(z)
  -> Sample z
  -> Decoder
  -> New generated sample
```

The central difference is the source of the latent vector: the encoder's input-conditioned distribution for reconstruction, versus the prior for new-sample generation.


<br/>


## 11. Revision Questions

**1. How does a VAE differ from an ordinary autoencoder?**  
A VAE models a probability distribution over latent representations and regularizes that distribution toward a prior, rather than relying only on a fixed encoded vector and reconstruction objective.

**2. What does the encoder produce in a common VAE?**  
Parameters of a latent distribution, often a Gaussian distribution.

**3. What are the two conceptual parts of the VAE training objective?**  
Reconstruction loss and distribution regularization.

**4. What does the reparameterization trick accomplish?**  
It expresses stochastic latent sampling in a form that allows gradient-based training to update the model parameters.

**5. How does reconstruction differ from new-sample generation?**  
Reconstruction encodes an existing input and decodes a sample from its input-conditioned latent distribution. New-sample generation draws a latent vector from the prior and decodes it.

**6. Why is prior sampling useful?**  
It provides a way to obtain latent vectors without first encoding a real input; the decoder maps them into candidate generated samples.

**7. What is posterior collapse?**  
A failure mode where the encoder's latent distribution becomes close to the prior and carries little input-specific information.

**8. Does a well-regularized latent space guarantee perfect generations?**  
No. It encourages useful prior sampling but does not guarantee realism, diversity, or perfect reconstruction.


<br/>


## 12. Summary and Checkpoint

### Summary

- An ordinary autoencoder learns an encoding and reconstruction; a VAE models a distribution over latent representations.
- The encoder predicts latent-distribution parameters, a latent vector is sampled, and the decoder produces a reconstruction.
- VAE training balances reconstruction with regularization toward a prior distribution.
- The reparameterization trick supports gradient-based learning through stochastic sampling.
- Reconstruction uses an input-conditioned latent distribution; new-sample generation can sample directly from the prior.
- Prior sampling and interpolation are ways to explore the latent space, but output quality and smoothness are not guaranteed.
- Reconstruction fidelity can trade off against latent-space regularization.
- Posterior collapse occurs when the latent variable carries little input-specific information.
- VAEs are used for representation learning, reconstruction, latent-space exploration, and generative workflows.

<br/>

### Checkpoint

**Explain why a VAE learns a distribution rather than only a fixed encoding.**

A strong answer should state that the encoder predicts parameters of an input-conditioned latent probability distribution, from which latent vectors can be sampled. Training combines reconstruction loss with regularization that encourages this distribution to align with a prior. This helps organize the latent space so that a model can sample from the prior and decode new candidate outputs, rather than only reconstructing inputs that have first been encoded.


<br/>


## 13. References and Optional Extensions

- [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — the foundational VAE paper introducing the variational autoencoder framework and reparameterization approach.
- [Tutorial on Variational Autoencoders](https://arxiv.org/abs/1606.05908) — a tutorial-style introduction to the model and its objective.

**Optional extension:** Later, study the evidence lower bound (ELBO), KL divergence, latent-variable distributions, and alternative VAE objectives if your work requires deeper mathematical understanding.

**Next chapter:** `06_generative_adversarial_networks.md`
