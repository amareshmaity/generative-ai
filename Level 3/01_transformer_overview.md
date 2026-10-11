# Chapter 01 — Transformer Overview

**Level 3: Transformer Architecture and Tokenization**  
**Structured GenAI Engineering Notes**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Trace how input text becomes tokens, embeddings, contextual representations, and task-specific outputs.
- Explain the roles of attention, feed-forward networks, residual connections, and normalization.
- Distinguish transformer architecture from training objectives and generation procedures.
- Understand the batch, sequence, and hidden dimensions used in transformer computations.
- Recognize which parts of a transformer overview are simplified and which vary across model implementations.

<br/>

## 2. What Is a Transformer?

A **Transformer** is a neural network architecture designed to process sequences using attention mechanisms and learned transformations. It was introduced in the 2017 research paper *Attention Is All You Need*.

Transformers are widely used in:

- Large Language Models (LLMs), such as GPT-style models.
- Language understanding models, such as BERT.
- Text-to-text models, such as T5.
- Vision Transformers and multimodal models that process different types of input.

The key idea is that a transformer can build contextual representations of tokens by allowing them to exchange information through attention, then further transform those representations through feed-forward networks.

A transformer is **not just an attention mechanism**. A typical transformer block combines attention, feed-forward computation, residual connections, and normalization.

<br/>

## 3. The Complete Transformer Data Flow

A transformer-based language model typically processes text through several stages.

```text
Input Text
    |
    v
Tokenization
Text → tokens → integer token IDs
    |
    v
Embedding and Positional Information
Token IDs → vectors with sequence-position information
    |
    v
Transformer Blocks × N
    |
    +--> Self-Attention
    |    Exchange information across allowed token positions
    |
    +--> Residual Connection + Normalization
    |
    +--> Feed-Forward Network
    |    Transform each token's representation
    |
    +--> Residual Connection + Normalization
    |
    v
Final Hidden Representations
Contextual vectors for the processed sequence
    |
    v
Task-Specific Output Layer
Next-token scores, class scores, or another task output
```

> **Note:** This is a conceptual diagram of a common transformer language-model pipeline, not every possible transformer design. Some models use different positional methods, normalization layouts, output heads, or encoder-decoder structures. The exact ordering of normalization and residual operations varies by architecture.

<br/>

### Understanding each stage

| Stage | Purpose |
|---|---|
| Tokenization | Converts text into token IDs that the model can process. |
| Embedding | Maps each token ID to a learned vector. |
| Positional information | Helps the model represent token order or relative position. |
| Attention | Combines information from other permitted positions in the sequence. |
| Feed-forward network | Applies learned nonlinear transformations to token representations. |
| Residual connections | Provide paths for information and gradients to flow through layers. |
| Normalization | Normalizes hidden features to support stable computation and training. |
| Output layer | Converts final representations into predictions appropriate for the task. |

The following chapters examine these components individually.

<br/>

## 4. Tokenization and Embeddings

Before a transformer can process text, the input must be converted into numerical representations.

### 4.1 Tokenization

**Tokenization** divides input text into units called tokens. Depending on the tokenizer, a token may represent a word, part of a word, punctuation, whitespace-related content, or another text unit.

For example, the sentence:

```text
Transformers process text.
```

might be represented as:

```text
["Transform", "ers", " process", "."]
```

This is an illustrative example only; the actual tokens depend on the tokenizer.

The tokenizer then maps these tokens to integer IDs:

```text
Tokens:     ["Transform", "ers", " process", "."]
Token IDs:  [1542, 287, 982, 13]
```

The IDs above are hypothetical, not actual vocabulary IDs.

A transformer processes these numerical IDs rather than directly processing raw text.

<br/>

### 4.2 Embedding layer

An embedding layer maps each token ID to a learned vector.

Suppose the embedding dimension is four. A simplified embedding matrix might look like this:

| Token ID | Embedding vector |
|---:|---|
| 101 | `[0.2, 0.5, -0.1, 0.8]` |
| 102 | `[0.7, -0.3, 0.4, 0.1]` |
| 103 | `[-0.2, 0.6, 0.9, -0.4]` |

These values are illustrative. In a trained model, embedding vectors are learned during training.

If the input contains five tokens and the embedding dimension is four, the embedding output has shape:

$$
(5,4)
$$

Each row represents one token.

<br/>

### 4.3 Positional information

Token embeddings alone do not necessarily identify where each token occurs in a sequence. Transformers therefore use positional information or another position-aware mechanism.

For example:

```text
The dog chased the cat.
The cat chased the dog.
```

These sentences contain similar tokens but express different relationships. The model needs information about token positions and their relationships to understand the sequence.

Different transformer architectures incorporate positional information differently. Some use additive position embeddings, while others use relative-position methods or rotary position embeddings.

**Detailed topics:** Chapters 2, 3, and 4 cover tokenization, embeddings, and positional information, respectively.

<br/>

## 5. Inside a Transformer Block

A transformer typically contains multiple transformer blocks stacked together. Each block transforms the representations produced by the previous block.

Two major computational components are:

1. Attention.
2. Feed-forward networks.

Residual connections and normalization support information flow and stable computation around these components.

<br/>

### 5.1 Attention

Attention allows a token's representation to incorporate information from other permitted token positions.

Consider:

> The animal didn't cross the road because it was tired.

To interpret *it*, the model may need information about earlier words. Attention provides a mechanism for combining information from relevant positions.

In self-attention, queries, keys, and values are derived from the same sequence of hidden representations.

At a high level:

- **Query (Q):** Represents what a position is looking for.
- **Key (K):** Represents features used to calculate how relevant a position is to a query.
- **Value (V):** Supplies the information combined using the attention weights.

A simplified attention equation is:

$$
\operatorname{Attention}(Q,K,V)
=
\operatorname{softmax}
\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

Here, $d_k$ is the dimension of each key vector. Attention masks may also be applied to restrict which positions can be attended to.

This operation produces updated representations for the sequence.

**Important:** Attention does not independently determine the correct meaning of a sentence. It is one component of a learned neural network.

<br/>

### 5.2 Feed-forward network (FFN)

After attention, a transformer block usually applies a feed-forward network to the hidden representation at each token position.

A simplified FFN is:

$$
\operatorname{FFN}(x)
=
W_2\,\sigma(W_1x+b_1)+b_2
$$

Where:

- $x$ is a token's hidden vector.
- $W_1,W_2$ are learned weight matrices.
- $b_1,b_2$ are bias vectors.
- $\sigma$ is a nonlinear activation function, such as GELU.

The intermediate dimension is often larger than the hidden dimension.

For example:

$$
768 \rightarrow 3072 \rightarrow 768
$$

These dimensions are illustrative, not universal.

Attention mixes information across token positions. The FFN then applies learned transformations to each position's representation, typically using the same FFN parameters at every position within that block.

<br/>

### 5.3 Residual connections

A residual connection adds a sublayer's input to its output.

$$
y=x+F(x)
$$

Here, $F(x)$ represents a transformation such as attention or an FFN, and the tensors must have compatible shapes for the addition.

Residual connections help preserve information and support the training of deep neural networks.

They are different from concatenation: addition combines corresponding elements, while concatenation joins dimensions.

<br/>

### 5.4 Layer normalization

Layer normalization normalizes features within a token's hidden representation, using learned scale and shift parameters in the standard formulation.

Conceptually, it helps control the scale of activations and supports stable optimization.

Transformer blocks use different normalization layouts:

- **Pre-norm:** Normalization is applied before the main sublayer.
- **Post-norm:** Normalization is applied after the residual addition.

The exact block arrangement depends on the architecture and implementation. Some models also use alternatives such as RMSNorm.

<br/>

## 6. Understanding Tensor Dimensions

Transformer implementations commonly work with three important dimensions.

| Dimension | Symbol | Meaning |
|---|---|---|
| Batch | $B$ | Number of sequences processed together |
| Sequence | $S$ | Number of token positions in each sequence |
| Hidden | $D$ | Number of features in each token representation |

For example, suppose a batch contains eight sequences, each containing 128 tokens, and the model uses a hidden dimension of 768.

The hidden-state tensor has shape:

$$
(B,S,D)=(8,128,768)
$$

The tensor contains:

$$
8 \times 128 \times 768 = 786{,}432
$$

scalar values, assuming every sequence position is represented.

### Why these dimensions matter

- Increasing \(B\) processes more sequences together and increases activation memory requirements.
- Increasing \(S\) increases the amount of sequence information processed. Standard full self-attention has a score matrix whose size grows quadratically with \(S\).
- Increasing \(D\) increases the size of token representations and often increases computation and parameter requirements.

These dimensions help engineers reason about memory usage, throughput, and latency.

The shape generally remains \((B,S,D)\) across standard transformer blocks, although intermediate operations can use different shapes. Attention introduces head dimensions, and an FFN may temporarily expand the hidden dimension.

<br/>

## 7. Output Layers and Task-Specific Predictions

After transformer processing, a model uses its final hidden representations to produce the output required by its task.

The output layer is not necessarily the same for every transformer.

### 7.1 Language generation

For a decoder-only language model, the final hidden representation at a position is projected into a vector of vocabulary scores called **logits**.

$$
\text{Logits}=hW_{\text{out}}+b
$$

Where:

- $h$ is a final hidden vector.
- $W_{\text{out}}$ is the output projection matrix.
- $b$ is an optional bias.
- The resulting logits contain one score per vocabulary token.

A probability distribution can be obtained by applying softmax to the logits. A decoding procedure then selects the next token according to its configured strategy.

For example:

```text
Input:  "The capital of France is"
Output: " Paris"
```

The model generates a continuation based on its learned parameters, input context, and generation procedure.

<br/>

### 7.2 Classification

A classification model may use a task-specific classification head to produce class scores.

For example:

```text
Input:  "The movie was excellent."
Output: Positive
```

An encoder-only architecture such as BERT can be adapted for classification using a suitable output head.

<br/>

### 7.3 Other tasks

Transformer representations can also support:

- Token classification, such as named-entity recognition.
- Text-to-text transformations.
- Question answering.
- Encoder-decoder sequence generation.

The appropriate output layer depends on the task and model design.

<br/>

## 8. Architecture vs. Training Objective vs. Generation Procedure

These three concepts are related but distinct.

| Concept | What it describes | Example |
|---|---|---|
| Architecture | How the neural network is organized | Decoder-only transformer |
| Training objective | What the model is optimized to learn | Next-token prediction |
| Generation procedure | How output tokens are selected and produced during inference | Greedy decoding or sampling |

<br/>

### Example: GPT-style language model

- **Architecture:** A decoder-only transformer with causal self-attention.
- **Training objective:** Typically learns to predict the next token from preceding tokens.
- **Generation procedure:** Processes a prompt and repeatedly selects or samples the next token until a stopping condition is met.

A decoder-only transformer is therefore not itself a decoding algorithm, and next-token prediction is not an architectural component.

Similarly, BERT uses an encoder-only transformer and is commonly associated with masked-language-model pretraining. Its architecture and training objective are separate design choices.

Detailed comparisons of BERT, GPT-style models, and T5 are covered in Chapter 12.

<br/>

## 9. What This Overview Simplifies

This chapter provides a high-level view. Real implementations can differ in several ways.

- **Positional methods:** Not every model adds an absolute positional vector to token embeddings.
- **Attention patterns:** Some models use bidirectional attention, while others use causal attention. Other attention patterns are possible.
- **Block organization:** The placement of residual connections and normalization varies.
- **Attention variants:** Multi-head attention, multi-query attention, and grouped-query attention have different configurations.
- **Output heads:** Some models predict vocabulary tokens; others produce class scores or task-specific outputs.
- **Inference optimization:** KV caching, batching, quantization, and optimized attention kernels affect deployment behavior without necessarily changing the high-level architecture.
- **Multimodal inputs:** Models may process image patches, audio tokens, or other non-text representations rather than only text token IDs.

A transformer should therefore be understood as a family of related architectures, not one fixed implementation.

<br/>

## 10. Code Example: Inspecting the Data Flow

The following small NumPy example illustrates token embeddings and the three tensor dimensions. It does not implement a complete transformer or train a model.

```python
import numpy as np

# Three sequences, each containing four token IDs.
token_ids = np.array([
    [1, 2, 3, 4],
    [2, 5, 6, 7],
    [1, 8, 9, 4],
])

# Toy embedding matrix:
# vocabulary size = 10, embedding dimension = 6
rng = np.random.default_rng(42)
embedding_matrix = rng.normal(size=(10, 6))

# Embedding lookup
embeddings = embedding_matrix[token_ids]

print("Token IDs shape:", token_ids.shape)
print("Embedding matrix shape:", embedding_matrix.shape)
print("Embeddings shape:", embeddings.shape)
```

Expected shapes:

```text
Token IDs shape: (3, 4)
Embedding matrix shape: (10, 6)
Embeddings shape: (3, 4, 6)
```

Interpretation:

- $B=3$: three sequences.
- $S=4$: four token positions per sequence.
- $D=6$: six features per token in this toy example.

The embedding lookup selects a vector for every token ID. A complete transformer would then process these vectors through position-aware computation and multiple transformer blocks before producing task-specific outputs.

**Limitation:** The example uses randomly initialized embeddings and contains no attention, positional encoding, residual connections, normalization, or output layer.

<br/>

## 11. Practice Exercise: Annotate the Transformer

Annotate the following pipeline with each component's role and tensor shape.

```text
Input text
    |
    v
Tokenizer
    |
    v
Token IDs: (B, S)
    |
    v
Embedding + positional information
    |
    v
Hidden states: (B, S, D)
    |
    v
Transformer Block 1
    |
    v
Transformer Block 2
    |
    v
Final hidden states: (B, S, D)
    |
    v
Task-specific output layer
    |
    v
Predictions
```

Assume $B=2$, $S=5$, and $D=8$.

Questions:

1. What is the shape of the token-ID tensor?
2. What is the shape of the hidden-state tensor?
3. Which component mixes information across token positions?
4. Which component applies a learned nonlinear transformation at each position?
5. Why is the output layer task-dependent?

### Answers

1. Token IDs: $(2,5)$.
2. Hidden states: $(2,5,8)$.
3. Attention mixes information across permitted token positions.
4. The feed-forward network applies a learned nonlinear transformation at each position.
5. Different tasks require different predictions, such as vocabulary logits for language generation or class scores for classification.

<br/>

## 12. Chapter Summary

- A transformer processes numerical representations of input tokens.
- The typical flow is tokenization → embeddings and positional information → transformer blocks → task-specific output.
- Attention mixes information across positions, while feed-forward networks transform token representations.
- Residual connections and normalization support information flow and stable computation.
- Batch, sequence, and hidden dimensions describe the shape of the main hidden-state tensor.
- Architecture, training objective, and generation procedure describe different aspects of a model.
- Actual implementations vary in attention patterns, positional methods, normalization layouts, output heads, and inference optimizations.

<br/>

**Checkpoint:** You should now be able to describe the complete transformer pipeline, identify the role of each major component, and explain why a transformer is more than just an attention layer.

<br/>

**Next chapter:** `02_tokens_vocabularies_and_tokenization.md` — Tokens, Vocabularies, and Tokenization.
