# Latent Representations and Latent Spaces

**Level 2: Generative Model Architectures · Chapter 02**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Define a representation and a latent variable at a conceptual level.
- Explain how learned representations can support compression, feature learning, reconstruction, and generation.
- Distinguish observed data space from a learned latent space.
- Explain latent sampling and interpolation with simple examples.
- Distinguish VAE latent variables, GAN input noise, and latent diffusion representations.
- Explain why an embedding or hidden representation is not necessarily a probabilistic latent variable.
- Understand why latent dimensions do not always correspond to human-readable attributes.
- Trace how an input can be transformed into an internal representation and then into an output.

<br/>

## 2. What Is a Representation?

A **representation** is an internal form of data that a model uses to process information.

Raw data is often inconvenient for direct computation. Images contain pixel values, text is represented using tokens or token IDs, and audio can be represented using waveform samples or other features. Neural networks transform these inputs into numerical forms that their layers can process.

Examples:

- An image can be represented as a grid of pixel values.
- A word or token can be represented by an embedding vector.
- A neural network can transform an image into a feature vector that captures useful visual patterns.
- A generative model can use an internal representation to reconstruct or generate data.

A representation may be hand-designed or learned from data. In modern neural networks, many useful representations are learned during training.

<br/>

### 2.1 A Simple Input-to-Representation Flow

```text
Observed input
     |
     v
Model or encoder
     |
     v
Internal representation
     |
     v
Downstream model component
     |
     v
Output
```

For example, an image encoder may transform an image into a feature vector. A downstream component may use that vector for classification, retrieval, reconstruction, or generation, depending on the system design.

**Key idea:** A representation is a numerical form used to express information for computation. It does not automatically imply that the representation is compressed, probabilistic, or directly generative.

<br/>

## 3. What Is a Latent Representation?

A **latent representation** is an internal representation of data that is not directly observed in the original input. It is inferred or learned by a model to capture useful structure in the data.

The term *latent* means hidden or not directly observed. A model may learn internal variables that help describe patterns in images, text, or other data.

For example, a model trained on face images may learn internal features related to overall shape, lighting, or appearance. However, individual dimensions of the representation are not guaranteed to correspond cleanly to these human concepts.

A latent representation may be a vector, a collection of vectors, a feature map, or another structured internal state.

<br/>

### 3.1 Representation, Hidden State, and Latent Variable

These terms are related but are not interchangeable in every context.

- **Representation:** A general term for a numerical form of information used by a model.
- **Hidden representation or hidden state:** An internal activation produced by a model layer or component.
- **Latent variable:** An unobserved variable used in a model's formulation to explain or represent observed data.
- **Probabilistic latent variable:** A latent variable defined through a probability distribution, as in a Variational Autoencoder (VAE).

Not every embedding or hidden representation is a probabilistic latent variable. For example, a text embedding may be a learned vector used for semantic search without being sampled from an explicit latent probability distribution.

**Key takeaway:** “Latent” generally refers to something not directly observed, but the exact meaning depends on the model and mathematical formulation.

<br/>

## 4. Observed Data Space and Latent Space

### 4.1 Observed Data Space

The **observed data space** is the space in which the original data is represented.

Examples include:

- Images represented as pixel arrays.
- Text represented as token sequences.
- Audio represented as waveforms or spectrograms.
- Tabular records represented as collections of feature values.

An image with height $H$, width $W$, and $C$ channels can be represented as a tensor with shape $H \times W \times C$. Each valid combination of pixel values corresponds to a possible point in that numerical space, although most combinations may not resemble meaningful natural images.

<br/>

### 4.2 Latent Space

A **latent space** is a space of internal representations that a model uses to encode, organize, or generate data.

A latent vector might contain fewer dimensions than the raw input, or it might use a different structure that is useful for the model's task. Latent spaces can support sampling, interpolation, reconstruction, and transformations, depending on how the model was trained.

For example, an image may contain thousands of pixel values, while an encoder may map it to a much smaller vector. This can provide a more compact internal representation of patterns in the image.

```text
Observed data space                 Latent space

Image / input                       Compact or structured vector
+--------------------+              +------------------+
| many pixel values  | -- encoder ->| z = [z1, z2, ...]|
+--------------------+              +------------------+
                                           |
                                           v
                                     decoder / model
                                           |
                                           v
                                      output data
```

The diagram is conceptual. Not every model uses a single compact vector, and not every latent space has a decoder.

<br/>

### 4.3 Why Use a Latent Space?

A learned latent space can help a model:

1. **Represent useful features:** Capture patterns that matter for a task.
2. **Compress information:** Encode an input with fewer values or a more compact structure.
3. **Reconstruct data:** Decode a representation back into an approximation of the original input.
4. **Generate samples:** Use sampled latent values as inputs to a generative component.
5. **Interpolate:** Move between representations to explore intermediate outputs.
6. **Support downstream tasks:** Provide features for classification, retrieval, clustering, or other processing.

These capabilities are not guaranteed by the word *latent* alone. They depend on the model's structure, training objective, and learned representation.

<br/>

## 5. Compression, Learned Features, and Reconstruction

### 5.1 Compression

**Compression** means representing information in a more compact form. In a neural network, an encoder may map a large input into a smaller representation.

For example:

```text
Image: 256 x 256 x 3 values
          |
          v
       Encoder
          |
          v
Latent vector: 128 values
```

This is only an illustrative shape example; actual models use different dimensions and structures.

A compact representation can reduce the amount of information passed to later components. However, compression can discard details. The goal is usually to retain information that is useful for the model's objective, not necessarily every detail of the original input.

A latent representation is not always smaller than the observed input. Some models use high-dimensional latent feature maps or token sequences.

<br/>

### 5.2 Learned Features

**Learned features** are patterns or characteristics that a model discovers from training data by adjusting its parameters.

In image data, early layers might respond to local visual patterns, while later layers may combine information into more complex representations. In text, embeddings and contextual hidden states can represent semantic or syntactic relationships useful for a task.

These descriptions are intuitive rather than guarantees about exactly what each neuron or dimension represents.

Learned features differ from manually designed features because the model adjusts its internal transformations based on the training objective and data.

<br/>

### 5.3 Reconstruction

**Reconstruction** means producing an approximation of an original input from a representation of that input.

A common encoder-decoder flow is:

```text
Original input x
      |
      v
Encoder
      |
      v
Representation z
      |
      v
Decoder
      |
      v
Reconstruction x_hat
```

The reconstructed output, often written as $\hat{x}$, is compared with the original input $x$. A reconstruction loss measures the discrepancy according to a chosen metric or probability model.

A simple conceptual objective is:

$$
\mathcal{L}_{\text{reconstruction}} = d(x,\hat{x})
$$

where $d$ is a suitable distance or discrepancy measure. The exact loss depends on the data and model.

Reconstruction does not mean the output must be identical to the input. Compression, model capacity, noise, and the training objective can all affect the result.

**Example:** An autoencoder trained on images compresses an image into an internal representation and then attempts to reconstruct it. A VAE uses a probabilistic latent formulation and adds a regularization term to its training objective.

<br/>

## 6. Sampling in Latent Space

**Sampling** means drawing a value from a specified distribution or sampling procedure.

In generative models, a sampled latent value can be passed to a decoder or generator to produce a new output. The meaning of the sample depends on the model.

### 6.1 VAE Sampling

A VAE encoder typically predicts parameters of a distribution over latent variables. A latent vector is sampled from that distribution during training. After training, new outputs can often be generated by sampling from a chosen prior distribution and passing the sample through the decoder.

Conceptually:

```text
Latent prior p(z)
       |
       v
Sample z
       |
       v
Trained VAE decoder
       |
       v
Generated output
```

For a common VAE formulation, the prior is a standard normal distribution, but this is not universal to every latent-variable model.

<br/>

### 6.2 GAN Input Noise

A GAN generator commonly receives a random noise vector as an input. The generator transforms this vector into a synthetic sample.

```text
Random noise z
      |
      v
GAN generator
      |
      v
Synthetic sample
```

The GAN input noise is not automatically the same thing as a VAE's posterior latent variable. In a standard GAN, the noise is an input to the generator; the model does not necessarily contain an encoder that maps each real training example to a latent distribution.

Conditional GANs can also receive labels or other conditioning information.

<br/>

### 6.3 Latent Diffusion Representations

In a **latent diffusion model**, the diffusion process takes place in a learned latent representation rather than directly in pixel space.

A typical high-level pipeline is:

```text
Training image
      |
      v
Trained image encoder
      |
      v
Latent representation
      |
      v
Noise is added to latent during training
      |
      v
Denoiser learns to predict a denoising target

Generation:
Initial latent noise
      |
      v
Iterative latent denoising
      |
      v
Trained decoder
      |
      v
Generated image
```

This approach can reduce the cost of processing high-resolution images compared with operating directly on all pixels, although actual resource use depends on the model and implementation.

Not all diffusion models operate in latent space. Some diffuse directly in data or pixel space.

<br/>

## 7. Interpolation Through Latent Space

**Interpolation** means constructing intermediate values between two representations.

Suppose two latent vectors are $z_A$ and $z_B$. A simple linear interpolation is:

$$
z(t)=(1-t)z_A+t z_B,\quad 0\leq t\leq 1
$$

At $t=0$, the result is $z_A$. At $t=1$, it is $z_B$. Values between zero and one produce intermediate vectors.

```text
Latent vector A -------- Intermediate vectors -------- Latent vector B
     z_A                       z(t)                         z_B
      |                          |                            |
      v                          v                            v
   Output A                 Output at t                 Output B
```

If the representation is used by a suitable decoder, these intermediate vectors can be decoded to produce intermediate outputs.

For example, interpolating between two latent representations of faces might produce a sequence of images that gradually changes in appearance. This is an illustrative possibility, not a guarantee that each intermediate step will correspond to a meaningful or smooth semantic change.

<br/>

### 7.1 When Interpolation Is Useful

- Exploring variation in generated images.
- Visualizing how a learned representation changes between examples.
- Studying whether a latent space has smooth regions.
- Creating transitions between outputs in suitable generative systems.

### 7.2 Limitations of Interpolation

- Straight lines in latent space may pass through regions poorly represented during training.
- Intermediate outputs may be blurry, unrealistic, or semantically unexpected.
- Linear interpolation is not always appropriate for the geometry or probability distribution of the latent space.
- Smooth numerical movement does not guarantee a smooth human-perceived change.

**Key takeaway:** Interpolation is a way to explore a representation space, but the meaning of the path depends on the model and its learned geometry.

<br/>

## 8. Three Different Uses of Latent-Like Inputs

The word *latent* is used in related but different ways across generative model families. Avoid treating these representations as interchangeable.

| Aspect | VAE latent variable | GAN input noise | Latent diffusion representation |
|---|---|---|---|
| Role | Probabilistic representation of an input, and a source for generation | Random input used by the generator | Compressed or transformed representation in which diffusion is performed |
| How it is obtained | Encoder predicts distribution parameters; a sample is drawn | Sampled from a chosen noise distribution | Produced by an encoder for training data; generation commonly begins from latent noise |
| Main learned component | Encoder and decoder | Generator and discriminator during training | Denoiser and, in many systems, a learned encoder-decoder |
| Typical generation path | Sample from prior, then decode | Noise or condition, then generator | Latent noise, iterative denoising, then decode |
| Probabilistic meaning | Explicitly modeled in the VAE formulation | Noise has a distribution, but is not necessarily an inferred latent variable for each real example | Depends on the formulation; the representation is not automatically a VAE posterior variable |
| Common use | Representation learning and generative sampling | Synthetic sample generation | More computationally efficient image generation in a learned space |

<br/>

### 8.1 The Important Distinction

- A **VAE latent variable** is part of a probabilistic encoder-decoder formulation.
- A **GAN noise vector** is typically a random input to a generator; it does not imply that the GAN has inferred a latent distribution for each observed example.
- A **latent diffusion representation** is the space in which a diffusion process operates. It is often produced by a separately trained or jointly trained encoder, depending on the system.

All three involve internal numerical values, but their mathematical roles and training objectives differ.

<br/>

## 9. Not Every Embedding or Hidden Representation Is a Probabilistic Latent Variable

An **embedding** is a numerical representation, often a vector, that places an item in a space useful for a task.

For example, a text embedding model can map a sentence to a vector so that semantically similar sentences tend to be near each other under a suitable similarity measure.

A **hidden representation** is an internal activation generated by a neural network layer. It may change as information passes through the model.

These representations may be called latent in a broad informal sense because they are internal rather than directly observed. However, they are not necessarily probabilistic latent variables.

Compare:

| Representation | Typical role | Explicit probability distribution required? |
|---|---|---|
| Text embedding for semantic search | Represent semantic similarity | No |
| Transformer hidden state | Carry contextual information through layers | No |
| VAE latent variable | Represent data through a probabilistic latent model | Yes, in the VAE formulation |
| GAN noise input | Provide stochastic input to a generator | A noise distribution is commonly specified, but it is not necessarily an inferred latent variable for each observed sample |
| Latent diffusion representation | Represent data in the space used for diffusion | Not necessarily a VAE-style posterior distribution |

The key is to examine the model's formulation rather than infer its mathematics from terminology alone.

<br/>

## 10. Why Latent Dimensions Are Not Necessarily Human-Readable

A latent vector may be written as:

$$
z=[z_1,z_2,\ldots,z_d]
$$

where \(d\) is the number of dimensions in the vector.

It may be tempting to assume that each dimension represents a clear property, such as color, shape, age, or orientation. In general, this assumption is not justified.

<br/>

### 10.1 Distributed Representations

A model can distribute information across multiple dimensions. A concept may be represented by a combination of values rather than a single coordinate.

Likewise, one dimension may contribute to several patterns. The interpretation depends on the learned parameters, data, objective, and architecture.

<br/>

### 10.2 No Guaranteed Semantic Alignment

Unless the model is designed or trained to produce interpretable dimensions, there is no general guarantee that:

- One dimension corresponds to one human concept.
- Increasing a coordinate changes only one attribute.
- Similar numerical distances correspond to equally meaningful semantic differences everywhere.
- Two models' latent dimensions can be compared directly.

<br/>

### 10.3 What About Disentangled Representations?

Some methods attempt to learn **disentangled representations**, in which different latent factors correspond more independently to meaningful variations in the data.

For example, a representation might aim to separate factors such as object position and lighting. Whether the model actually achieves this depends on the objective, data, assumptions, and evaluation method.

Disentanglement is a goal in some models, not an automatic property of every latent space.

**Key takeaway:** Latent dimensions are mathematical coordinates. Their human interpretation must be demonstrated, not assumed.

<br/>

## 11. Practice: Connect an Input, Representation, and Output

### Exercise 1 — Draw the Flow

Complete this generic diagram for a system that uses a learned internal representation:

```text
Observed input x
       |
       v
[ Encoder / model ]
       |
       v
[ Internal representation ]
       |
       v
[ Decoder / downstream component ]
       |
       v
Output x_hat or generated sample
```

Annotate the diagram with:

1. What the observed input contains.
2. What the internal representation stores or captures.
3. Whether the representation is deterministic, sampled, or otherwise constructed.
4. What the downstream component does.
5. Whether the output is a reconstruction or a newly generated sample.

Repeat the exercise for:
- A VAE reconstructing an input.
- A VAE generating from a prior sample.
- A GAN generating from noise.
- A latent diffusion model generating from latent noise.

<br/>

### Exercise 2 — Check Your Understanding

1. What is the difference between an observed data space and a latent space?
2. Why can a latent representation be useful for compression and reconstruction?
3. How does a VAE latent variable differ from a GAN noise vector?
4. What does interpolation between two latent vectors mean?
5. Why is a text embedding not necessarily a probabilistic latent variable?
6. Why should you not assume that each latent dimension represents one human-readable attribute?
7. Does every diffusion model operate in latent space? Explain.

### Suggested Answers

1. **Observed data space** describes the original data representation, such as pixels or token sequences. **Latent space** describes internal representations learned or used by a model.
2. An encoder can map input data into a compact or structured representation, and a decoder can use it to reconstruct an approximation. The amount and type of information preserved depend on the model and objective.
3. A VAE uses a probabilistic latent-variable formulation, typically with an encoder that predicts a distribution. A GAN noise vector is usually a random input to the generator and does not necessarily represent an encoded real example.
4. It constructs intermediate vectors between two representations. A suitable decoder may turn these vectors into intermediate outputs, but semantic smoothness is not guaranteed.
5. An embedding can be a learned deterministic vector used for similarity or another task. It does not require an explicit probability distribution over latent variables.
6. Information can be distributed across dimensions, and the learned coordinates are not guaranteed to align with human concepts.
7. No. Diffusion can operate in the original data space, such as pixel space, or in a learned latent space.

<br/>

## 12. Chapter Summary

A **representation** is a numerical form of information used by a model. A **latent representation** is an internal representation that is not directly observed in the input. Depending on the model, representations can support feature learning, compression, reconstruction, sampling, interpolation, and generation.

The observed data space describes the original data, while a latent space provides an internal space used by a model. However, not every latent-like representation is probabilistic, compact, interpretable, or generative.

Three important cases are:

- **VAE:** Uses probabilistic latent variables and a decoder for reconstruction and generation.
- **GAN:** Commonly transforms random input noise into synthetic samples through a trained generator.
- **Latent diffusion:** Performs iterative denoising in a learned representation space before decoding the result.

The mathematical role of a representation matters more than its label. An embedding, a hidden state, a VAE latent variable, GAN input noise, and a latent diffusion representation should not be treated as identical concepts.

**Checkpoint:** You should be able to explain how a latent representation connects an input, an internal model state, and an output—and explain why different generative models use these representations in different ways.

<br/>

## 13. References and Further Reading

1. Kingma and Welling (2013), *Auto-Encoding Variational Bayes* — https://arxiv.org/abs/1312.6114
2. Goodfellow et al. (2014), *Generative Adversarial Nets* — https://arxiv.org/abs/1406.2661
3. Ho, Jain, and Abbeel (2020), *Denoising Diffusion Probabilistic Models* — https://arxiv.org/abs/2006.11239
4. Rombach et al. (2021), *High-Resolution Image Synthesis with Latent Diffusion Models* — https://arxiv.org/abs/2112.10752

**Next chapter:** `03_autoregressive_generation.md` — Autoregressive Generation.
