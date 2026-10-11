# Chapter 04 — Transformer-Based Generation

## 1. Learning Objectives and Prerequisites

By the end of this chapter, you should be able to:

- Explain the roles of tokens, embeddings, attention, and contextual representations at a high level.
- Describe decoder-only and encoder-decoder generation flows.
- Explain why causal masking prevents a model from using future sequence elements during autoregressive prediction.
- Distinguish parallel computations during training from sequential autoregressive generation.
- Discuss context length and computational requirements conceptually.
- Recognize transformers as components in language, multimodal, and some diffusion systems.
- Explain why an encoder-only transformer is not automatically a text generator.

**Prerequisites:** Understand tokens, training versus inference, and the autoregressive generation process from Chapter 03.

**Depth boundary:** This chapter stays conceptual. Attention mathematics, query/key/value details, positional encoding, normalization, and KV caching are studied systematically in Level 3.

<br/>

## 2. Intuition: What Does a Transformer Do?

A transformer is a neural-network architecture that processes representations of input elements and learns relationships among them. In language systems, those elements are commonly tokens.

For example, consider:

> The dog chased the ball because it was excited.

To interpret `it`, a model benefits from considering other words in the sentence. A transformer uses attention mechanisms to help representations incorporate information from relevant parts of the available context. The resulting representations are **contextual**: the representation of a token can depend on the other tokens the model is allowed to consider.

A transformer is not, by itself, a complete description of a generative system. The model's configuration and training objective help determine what it learns to do, while the generation procedure determines how outputs are produced.

<br/>

### The main concepts

- **Token:** A unit of input or output, such as a word, part of a word, punctuation mark, or learned symbol.
- **Embedding:** A numerical vector representing a token or another input element. Neural networks operate on numerical representations rather than raw text characters directly.
- **Attention:** A mechanism that lets the model combine information from different positions in the available input or sequence.
- **Contextual representation:** A representation that has incorporated information from other permitted positions.
- **Transformer:** An architecture that processes these representations using attention and other neural-network operations.

The key idea is that a transformer builds useful representations by modeling relationships between elements in context.


<br/>


## 3. From Input Tokens to Output

A simplified language-model path looks like this:

```text
Input text
    |
    v
Tokenization
    |
    v
Token IDs
    |
    v
Embeddings and position-related information
    |
    v
Transformer layers
(attention + other neural-network operations)
    |
    v
Output scores for possible next tokens
    |
    v
Selection of a token
    |
    v
Append token and continue, or stop
```

This is a conceptual view rather than a complete implementation specification. Exact processing steps depend on the model design.

The transformer layers create representations that are useful for the model's objective. In an autoregressive language model, these representations are used to estimate a distribution over the next token. A generation procedure selects a token and repeats the process.

**Important distinction:** Attention helps the model process relationships within the permitted context. It does not independently decide which output token must be generated; the model's output distribution and the generation procedure together determine the continuation.


<br/>


## 4. Decoder-Only Generation

Decoder-only transformers are commonly used for autoregressive language generation.

### Conceptual flow

```text
Prompt
  |
  v
Tokenization and embeddings
  |
  v
Decoder-only transformer
with causal attention
  |
  v
Next-token distribution
  |
  v
Select next token
  |
  v
Append token to context
  |
  +----> Repeat until a stopping condition is met
  |
  v
Generated continuation
```

<br/>

### Example

Prompt:

> Generative AI can

The model predicts a distribution over possible next tokens. Suppose the selected token is `create`. The context becomes:

> Generative AI can create

The model then predicts the next token from the updated context. It may continue with `content`, `images`, or another plausible token, depending on its learned behavior and selection method.

In a decoder-only autoregressive model, the generated sequence is extended token by token. The same model can condition each new prediction on the prompt and the tokens already generated, subject to the context window and model configuration.


<br/>


## 5. Causal Masking: Preventing Access to Future Tokens

For autoregressive prediction, a token's prediction must not use tokens that occur later in the target sequence. **Causal masking** restricts attention so that each position can access only permitted earlier positions and itself, rather than future positions.

Consider the known sequence:

> The cat sleeps

When training a causal language model:

- The prediction at `The` must not use `cat` or `sleeps` as future context.
- The prediction at `cat` can use `The`, but must not use `sleeps`.
- The prediction at `sleeps` can use the preceding tokens.

A conceptual access pattern is:

| Position making a prediction | Earlier positions available | Future positions available |
|---|---|---|
| `The` | Beginning/context as defined by the model | No |
| `cat` | `The` | No |
| `sleeps` | `The`, `cat` | No |

This restriction aligns the model's training computation with the information available when predicting the next token at inference time.

Causal masking is not a claim that the model cannot use context at all. It can use the preceding context; it is specifically prevented from looking ahead to future target elements.


<br/>


## 6. Encoder-Decoder Generation

Encoder-decoder transformers separate processing of the input from generation of the output.

The **encoder** reads the input sequence and builds contextual representations. The **decoder** uses those representations, along with the output tokens generated so far, to produce the next output token.

### Conceptual flow

```text
Source input
    |
    v
Tokenization and embeddings
    |
    v
Encoder
    |
    v
Contextual source representations
    |
    +----------------------------------+
                                       |
Previously generated output tokens     |
    |                                  |
    v                                  |
Decoder with causal access to          |
output tokens so far                   |
    |                                  |
    +------ uses source information <--+
    |
    v
Next-output-token distribution
    |
    v
Select token and append to output
    |
    +----> Repeat until a stopping condition is met
    |
    v
Generated output
```

<br/>

### Example: translation

Source input:

> Good morning.

The encoder builds representations of the source sentence. The decoder generates a target-language sequence one token at a time, using the source representations and the target tokens already generated.

The encoder-decoder design is useful for tasks where an input sequence guides a distinct output sequence, such as translation or summarization. The details depend on the specific model and task.

### Decoder-only vs. encoder-decoder

| Aspect | Decoder-only | Encoder-decoder |
|---|---|---|
| Main structure | Decoder stack | Encoder stack plus decoder stack |
| Input context | Prompt and generated sequence | Encoded source input plus generated output sequence |
| Generation | Predict and append next token | Predict and append next output token conditioned on source representations |
| Typical examples | General-purpose autoregressive language generation | Translation and other input-to-output sequence tasks |
| Key conceptual feature | One sequence is extended | A source sequence guides a separate output sequence |

These are common patterns, not absolute rules for every model.


<br/>


## 7. Parallel Training vs. Sequential Generation

A common source of confusion is assuming that autoregressive generation must also make training sequential in exactly the same way.

### Training

During training, the complete target sequence is known. With causal masking, the model can compute predictions for many token positions in parallel while ensuring that each position cannot access future target tokens. The training objective compares predictions with known target tokens.

### Inference

During autoregressive generation, the next token is not known in advance. The model predicts it, the generation procedure selects it, and that token becomes part of the context for the next step. This dependency makes ordinary autoregressive decoding sequential across generated tokens.

| Question | Training | Autoregressive inference |
|---|---|---|
| Are target tokens known? | Yes | Future generated tokens are not known |
| Can positions be computed in parallel? | Many positions can be processed in parallel | The next generated token generally depends on previous generated tokens |
| Is the sequence extended using model-selected tokens? | Not in the same way; targets come from the training data | Yes |
| Main goal | Learn from known examples | Generate a new continuation |

**Takeaway:** The autoregressive objective constrains what each position may use, but training implementations can still parallelize computations across positions. Generation retains a sequential dependency between newly generated tokens.


<br/>


## 8. Context Length and Computational Requirements

### Context length

A model's **context window** is the amount of input and generated sequence it can consider within a model call or generation state, as defined by its design and configuration.

A larger context window can make more prior information available, but it does not guarantee that the model will use every detail correctly. Practical limits can include:

- The model's configured context capacity.
- Memory and computational cost.
- Latency when processing long inputs.
- Application-level limits on input and output length.

When a conversation or document exceeds the supported context, an application may need to truncate, summarize, retrieve, or otherwise manage information. These are system-level strategies, not a guarantee that a transformer automatically remembers unlimited history.

<br/>

### Computational requirements

Transformer computation depends on factors such as sequence length, model size, batch size, and the chosen implementation. Processing longer sequences can require substantially more computation and memory. Autoregressive generation also repeats work across output steps, although implementations can use optimizations to reduce overhead.

For this level, remember the qualitative trade-off: **more context and larger models can increase capability, but they also tend to increase resource requirements.** Exact costs depend on the architecture, sequence length, hardware, and implementation.


<br/>


## 9. Transformers Across Generative AI

Transformers are used in several types of generative systems, but their role differs by system.

| System type | Possible role of a transformer |
|---|---|
| Language generation | Process token context and predict next tokens |
| Multimodal systems | Process text and/or representations of images, audio, video, or other modalities |
| Diffusion systems | Serve as a component that processes conditioning information or learned representations during denoising, depending on the design |

Not every multimodal or diffusion model uses a transformer. Architectures vary, and some systems combine transformers with other neural-network components.

<br/>

### Why an encoder-only transformer is not automatically a text generator

An encoder-only transformer is generally designed to build contextual representations of an input sequence. For example, those representations can support classification, retrieval, or other understanding-oriented tasks.

That does not automatically provide the next-token prediction objective and autoregressive output process needed for ordinary left-to-right text generation. A text-generating system needs an appropriate training objective, output head, and generation procedure; an encoder-only architecture should not be assumed to have these simply because it is a transformer.

The distinction is about the model's design and objective, not about whether the architecture is capable of representing language.


<br/>

## 10. Strengths, Limitations, and Common Misconceptions

### Strengths

- **Context-sensitive representations:** attention can combine information from relevant positions in the permitted context.
- **Flexible architecture:** transformer designs can support different objectives and tasks.
- **Strong sequence modeling:** decoder-only and encoder-decoder designs support widely used generation patterns.
- **Multimodal integration:** transformer components can process or combine representations from multiple modalities in suitable systems.

<br/>

### Limitations

- **Resource demand:** long sequences and large models can require substantial memory and computation.
- **Autoregressive latency:** decoder-only and autoregressive decoder outputs are generally generated in dependent steps.
- **Finite context:** the model cannot directly condition on unlimited history in a single context window.
- **Objective matters:** a transformer architecture alone does not specify whether a model is a classifier, representation encoder, or generator.
- **Output reliability:** fluent output may still be incorrect; generation needs suitable evaluation and application-level safeguards.

<br/>

### Common misconceptions

- **Misconception:** “Attention is the whole transformer.”  
  **Correction:** Attention is a central mechanism, but transformer layers also include other neural-network operations.

- **Misconception:** “A transformer always generates text.”  
  **Correction:** Transformers are architectures. The objective, configuration, and generation procedure determine the task.

- **Misconception:** “Causal masking means the model cannot use previous tokens.”  
  **Correction:** It prevents access to future target positions while allowing access to permitted preceding context.

- **Misconception:** “Training and generation must both run one token at a time.”  
  **Correction:** Training can compute predictions for multiple positions in parallel; autoregressive generation has a dependency between successive output tokens.

- **Misconception:** “An encoder-only model is just a decoder-only model with a different name.”  
  **Correction:** Their information-flow patterns and common objectives differ. Encoder-only models are not automatically configured for autoregressive text generation.


<br/>


## 11. Practice: Draw the Generation Flows

Draw two high-level diagrams.

### A. Decoder-only

Include these components in order:

1. Prompt text
2. Tokenization and embeddings
3. Decoder-only transformer with causal masking
4. Next-token distribution
5. Token selection and append
6. Repeat or stop
7. Generated continuation

<br/>

### B. Encoder-decoder

Include these components:

1. Source input
2. Tokenization and embeddings
3. Encoder
4. Contextual source representations
5. Decoder receiving source information and previously generated output tokens
6. Next-output-token distribution
7. Token selection and append
8. Repeat or stop
9. Generated output

<br/>

### Suggested answer

```text
DECODER-ONLY

Prompt
  -> Tokens / embeddings
  -> Causal decoder transformer
  -> Next-token distribution
  -> Select and append token
  -> Repeat until stop
  -> Continuation
```

```text
ENCODER-DECODER

Source input
  -> Tokens / embeddings
  -> Encoder
  -> Source representations
             |
             v
Previous output tokens -> Decoder
                           |
                           v
                  Next-token distribution
                           |
                           v
                  Select and append token
                           |
                      Repeat / stop
                           |
                           v
                     Generated output
```

The critical difference is that an encoder-decoder model explicitly encodes a source sequence that conditions a separate output sequence.


<br/>


## 12. Revision Questions

**1. What is the role of a token embedding?**  
It maps a token or input element to a numerical vector that can be processed by a neural network.

**2. What does attention contribute conceptually?**  
It allows a model to combine information from different permitted positions when building representations.

**3. What is a contextual representation?**  
A representation that incorporates information from other positions in the available context.

**4. Why does a decoder-only autoregressive model use causal masking?**  
To prevent a position from using future target tokens when predicting the next token.

**5. Why can training be parallel while autoregressive generation is sequential?**  
During training, target sequences are known, so predictions for multiple positions can be computed in parallel under the masking constraints. During generation, each selected token affects the context for the next token.

**6. How does an encoder-decoder model generate output?**  
The encoder builds representations of the source input; the decoder uses those representations and previously generated output tokens to predict the next output token.

**7. Why is an encoder-only transformer not automatically a text generator?**  
Its architecture and common objectives focus on contextual representation learning; autoregressive text generation requires a suitable objective and output-generation procedure.

**8. What is a context window?**  
The amount of sequence context a model can consider within its configured processing or generation limit.


<br/>


## 13. Summary and Checkpoint

### Summary

- A transformer processes token or other input representations and learns relationships among positions.
- Embeddings provide numerical representations; attention helps incorporate contextual information.
- Decoder-only transformers commonly support autoregressive continuation, while encoder-decoder transformers use encoded source representations to guide a separate output sequence.
- Causal masking prevents autoregressive predictions from accessing future target tokens.
- Training can compute predictions for many known sequence positions in parallel, while autoregressive generation depends on previously generated tokens.
- Context length, model size, and sequence length affect computational and memory requirements.
- Transformers can be components in language, multimodal, and diffusion systems, but not every system uses them.
- An encoder-only transformer is not automatically a text generator.

<br/>

### Checkpoint

**Explain the transformer's role without deriving attention equations.**

A strong answer should explain that a transformer processes numerical representations of input elements and uses attention and other neural-network operations to build contextual representations. In a generative model, those representations help produce output predictions according to the model's objective. The model configuration and generation procedure determine whether it generates tokens autoregressively or performs another task.


<br/>


## 14. References and Optional Extensions

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — the foundational Transformer paper.
- [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) — an example of an encoder-oriented transformer for language understanding.
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) — an example of decoder-only autoregressive language modeling.
- [Attention Is All You Need — Google Research](https://research.google/pubs/attention-is-all-you-need/) — publication information for the Transformer paper.

**Level 3 depth boundary:** Study attention mathematics, query/key/value details, positional encoding, normalization, and KV caching in the dedicated Level 3 material. This chapter intentionally introduces those topics only at a high level.

**Next chapter:** `05_variational_autoencoders.md`
