# Chapter 03 — Embedding Layers

**Level 3: Transformer Architecture and Tokenization**  
**Structured GenAI Engineering Notes**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Trace a token ID lookup in a learned embedding matrix.
- Explain vocabulary size and embedding dimension.
- Follow a sequence from integer token IDs to a matrix of vectors.
- Distinguish input embeddings from contextual hidden states.
- Distinguish token embeddings from document embeddings used for retrieval.
- Explain the purpose of the language-model output projection and the idea of optional weight tying.

<br/>

## 2. What Is an Embedding Layer?

An **embedding layer** maps discrete IDs to dense numerical vectors. In a transformer, the input token IDs are used to look up rows in a learned embedding matrix.

A token ID is an integer identifier, not a vector that directly represents meaning. The embedding layer retrieves the corresponding vector, which becomes a numerical representation used by the model.

A simplified pipeline is:

```text
Text
  |
  v
Tokenizer
  |
  v
Token IDs: [12, 7, 31]
  |
  v
Embedding matrix lookup
  |
  v
Token vectors
  |
  v
Transformer blocks
```

The IDs above are illustrative. Actual IDs depend on the tokenizer.

<br/>

## 3. The Embedding Matrix

Let the vocabulary size be $V$ and the embedding dimension be $D$. A standard token embedding matrix can be represented as:

$$
E \in \mathbb{R}^{V \times D}
$$

Where:

- $V$ is the number of entries in the tokenizer/model vocabulary.
- $D$ is the number of numerical features in each token vector.
- $E$ is a matrix of learned parameters.

Each row corresponds to a vocabulary entry. For a token ID $i$, its embedding is the row $E_i$.

<br/>

### Example

Suppose:

- Vocabulary size $V=6$.
- Embedding dimension $D=4$.

A toy embedding matrix could be:

$$
E =
\begin{bmatrix}
0.1 & 0.2 & 0.3 & 0.4 \\
0.5 & 0.6 & 0.7 & 0.8 \\
0.9 & 1.0 & 1.1 & 1.2 \\
1.3 & 1.4 & 1.5 & 1.6 \\
1.7 & 1.8 & 1.9 & 2.0 \\
2.1 & 2.2 & 2.3 & 2.4
\end{bmatrix}
$$

This matrix is for illustration only. A real model learns its embedding values during training; these values are not manually assigned semantic meanings.

If the input token ID is `2`, using zero-based indexing, the selected vector is the third row:

$$
E_2 = [0.9,\ 1.0,\ 1.1,\ 1.2]
$$

**Important:** Token ID `2` selects a row; the numerical value of the ID does not determine the vector's values.

<br/>

## 4. Vocabulary Size vs. Embedding Dimension

These dimensions describe different things.

| Quantity | Symbol | Meaning | Example |
|---|---|---|---|
| Vocabulary size | $V$ | Number of token entries | 6 |
| Embedding dimension | $D$ | Number of features per token vector | 4 |
| Embedding matrix | $E$ | Matrix containing all token vectors | Shape $(6,4)$ |

A larger vocabulary adds more rows. A larger embedding dimension makes each row wider.

For example, if $V=50{,}000$ and $D=768$, the embedding matrix has shape:

$$
(50{,}000,\ 768)
$$

The matrix contains $50{,}000 \times 768 = 38{,}400{,}000$ scalar parameters.

The vocabulary size is associated with the tokenizer and model vocabulary. The embedding dimension is an architectural configuration of the model. These values should not be assumed to be identical across different models.

<br/>

## 5. From Token IDs to a Sequence of Vectors

A sequence of token IDs is converted by selecting one embedding row for each ID.

Suppose the input IDs are:

```text
[2, 0, 4]
```

With the toy matrix above, the selected rows are:

```text
ID 2 → [0.9, 1.0, 1.1, 1.2]
ID 0 → [0.1, 0.2, 0.3, 0.4]
ID 4 → [1.7, 1.8, 1.9, 2.0]
```

The sequence embedding matrix is:

$$
X =
\begin{bmatrix}
0.9 & 1.0 & 1.1 & 1.2 \\
0.1 & 0.2 & 0.3 & 0.4 \\
1.7 & 1.8 & 1.9 & 2.0
\end{bmatrix}
$$

Its shape is:

$$
(S,D)=(3,4)
$$

where $S=3$ is the sequence length and $D=4$ is the embedding dimension.

For a batch of sequences, the common shape is:

$$
(B,S,D)
$$

where $B$ is the batch size.

<br/>

### Shape walkthrough

If a batch contains 2 sequences, each with 3 token IDs, and the embedding dimension is 4:

```text
Token IDs shape:       (2, 3)
Embedding matrix:      (6, 4)
Sequence embeddings:   (2, 3, 4)
```

The embedding lookup preserves the batch and sequence dimensions while replacing each integer ID with a vector of length $D$.

<br/>

## 6. Are Embeddings Learned?

In a typical neural language model, the input embedding matrix is a trainable parameter matrix.

During training:

1. Token IDs select embedding vectors.
2. The model uses those vectors to compute predictions.
3. A loss function measures prediction error.
4. Backpropagation calculates gradients.
5. An optimizer updates trainable parameters, which may include the embedding matrix.

Over training, the embedding vectors are adjusted to help the model perform its objective.

An embedding vector should not be interpreted as a manually written definition of a word. Its values are learned as part of the full model. Useful patterns may emerge in the geometry of the vectors, but their interpretation is distributed and depends on the model and training process.

Not every system uses trainable embeddings in exactly the same way; frozen embeddings, specialized input representations, or other architecture-specific arrangements are possible.

<br/>

## 7. Input Embeddings vs. Contextual Hidden States

This is one of the most important distinctions in transformer architecture.

### 7.1 Input embeddings

An **input embedding** is the vector retrieved from the embedding matrix for a token ID. By itself, the lookup does not incorporate the surrounding sentence through transformer attention.

For example, the token `bank` receives its initial embedding lookup wherever it appears, assuming the same tokenizer ID and embedding table.

<br/>

### 7.2 Contextual hidden states

A **contextual hidden state** is the representation produced after the token has been processed by transformer layers. Attention and other transformations allow the representation to depend on the surrounding context.

Compare:

```text
Sentence A: She deposited money at the bank.
Sentence B: They sat beside the river bank.
```

The token `bank` may begin with the same input embedding in both sentences. After transformer processing, its contextual hidden state can differ because the surrounding tokens differ.

Conceptually:

```text
Token ID for "bank"
        |
        v
Same input embedding lookup
        |
        +----------------------+
        |                      |
        v                      v
Context A                 Context B
"deposited money"         "river"
        |                      |
        v                      v
Transformer layers       Transformer layers
        |                      |
        v                      v
Contextual state A       Contextual state B
```

The same initial embedding does not imply identical later representations.

<br/>

### Key distinction

| Property | Input embedding | Contextual hidden state |
|---|---|---|
| Source | Embedding matrix lookup | Output of transformer computation |
| Depends directly on surrounding tokens? | Not through contextual attention at lookup time | Yes, generally |
| Shape for one token | $(D,)$ | Typically $(D,)$ at a given layer |
| Main role | Initial learned token representation | Context-sensitive representation used by later computations |

In models with positional information added to input embeddings, the representation entering the first transformer block may already include position-dependent information. The core distinction remains: input lookup vectors are not the same as representations contextualized by transformer layers.

<br/>

## 8. Token Embeddings vs. Document Embeddings for Retrieval

The word *embedding* is used in multiple contexts. Do not confuse the token embedding matrix of a language model with a document embedding used in semantic search.

### 8.1 Token embeddings

- Usually one vector per vocabulary token in a model's embedding table.
- Used as part of the model's input representation.
- Looked up by token ID.
- Typically learned as part of language-model training.

<br/>

### 8.2 Document or text embeddings

A text-embedding model can map a sentence, paragraph, query, or document chunk to a vector intended to represent that piece of text for tasks such as semantic search.

For example:

```text
Document chunk
      |
      v
Embedding model
      |
      v
Document vector
      |
      v
Vector index / semantic search
```

A retrieval system may compare query and document vectors using cosine similarity, dot product, or another supported metric.

A document embedding is not simply the vocabulary row for one token. It is a representation of a larger text input, produced by an embedding model or a pooling procedure designed for that purpose.

<br/>

### Comparison

| Feature | Token embedding | Document embedding |
|---|---|---|
| Represents | A vocabulary token | A text span, chunk, or document |
| Typical use | Input to transformer layers | Retrieval, clustering, semantic similarity |
| How obtained | Lookup by token ID | Run text through an embedding model or pooling pipeline |
| Typical output | One vector per token position after lookup | Often one vector per input text |
| Context | Initial lookup does not itself encode sentence context | Depends on the embedding model and its input |

**Practical note:** Some systems derive text embeddings from transformer hidden states using pooling. The distinction is about the representation's role and how it is produced, not a claim that the underlying mathematics can never overlap.

<br/>

## 9. Language-Model Output Projection

For a language model that predicts vocabulary tokens, the final hidden state is transformed into vocabulary-sized scores called **logits**.

Let:

- $h \in \mathbb{R}^{D}$ be a final hidden vector at a prediction position.
- $W_{\text{out}} \in \mathbb{R}^{D \times V}$ be an output projection matrix.
- $b \in \mathbb{R}^{V}$ be an optional bias.

Then:

$$
z = hW_{\text{out}} + b
$$

where:

$$
z \in \mathbb{R}^{V}
$$

Each logit corresponds to a vocabulary entry. A softmax can convert these scores into a probability distribution, after which the generation procedure selects a token.

For a sequence, the output projection can produce logits at each position, often with a shape such as:

$$
(B,S,V)
$$

The exact inference behavior depends on the architecture and implementation. For next-token generation, the model uses the logits associated with the relevant final prompt position or current decoding position.

<br/>

### Input and output matrices

```text
Input token ID
      |
      v
Input embedding matrix E: (V, D)
      |
      v
Transformer layers
      |
      v
Final hidden vector h: (D,)
      |
      v
Output projection W_out: (D, V)
      |
      v
Vocabulary logits: (V,)
```

The input embedding matrix and output projection have related but conceptually distinct roles: one maps token IDs to vectors, while the other maps hidden vectors to vocabulary scores.

<br/>

## 10. Weight Tying

**Weight tying** means sharing the same learned parameters between the input token embedding matrix and the language-model output projection, with the appropriate transpose or orientation.

The input embedding matrix is commonly represented as:

$$
E \in \mathbb{R}^{V \times D}
$$

If the output projection uses tied weights, its matrix can be represented as:

$$
W_{\text{out}} = E^\top
$$

so that:

$$
W_{\text{out}} \in \mathbb{R}^{D \times V}
$$

This lets the model reuse the same parameter values for input token lookup and output vocabulary scoring.

<br/>

### Why tie weights?

Potential benefits include:

- Reducing the number of independent parameters.
- Sharing information between input token representations and output token scoring.
- Potentially improving parameter efficiency.

Weight tying is an implementation choice, not a requirement. Some models tie input and output embeddings; others use separate matrices or more specialized arrangements. The exact dimensions and parameter-sharing behavior should be checked for the model being studied.

<br/>

## 11. Code Example: A Toy Embedding Lookup with NumPy

This example performs a lookup using a small, manually defined matrix so that every value can be inspected.

```python
import numpy as np

# Vocabulary size V = 6
# Embedding dimension D = 4
embedding_matrix = np.array([
    [0.1, 0.2, 0.3, 0.4],  # Token ID 0
    [0.5, 0.6, 0.7, 0.8],  # Token ID 1
    [0.9, 1.0, 1.1, 1.2],  # Token ID 2
    [1.3, 1.4, 1.5, 1.6],  # Token ID 3
    [1.7, 1.8, 1.9, 2.0],  # Token ID 4
    [2.1, 2.2, 2.3, 2.4],  # Token ID 5
])

# Three token IDs in one sequence
token_ids = np.array([2, 0, 4])

# Lookup one row per token ID
sequence_embeddings = embedding_matrix[token_ids]

print("Embedding matrix shape:", embedding_matrix.shape)
print("Token IDs shape:", token_ids.shape)
print("Sequence embeddings shape:", sequence_embeddings.shape)
print(sequence_embeddings)
```

Expected shapes:

```text
Embedding matrix shape: (6, 4)
Token IDs shape: (3,)
Sequence embeddings shape: (3, 4)
```

Expected embedding vectors:

```text
[[0.9 1.  1.1 1.2]
 [0.1 0.2 0.3 0.4]
 [1.7 1.8 1.9 2. ]]
```

<br/>

### How to read the shapes

- `(6, 4)`: six vocabulary entries, each with a four-dimensional vector.
- `(3,)`: three token IDs in the sequence.
- `(3, 4)`: three selected token vectors, each with four features.

The values are illustrative and are not trained semantic embeddings.

<br/>

## 12. Practice Exercise

Use the following embedding matrix:

$$
E =
\begin{bmatrix}
1 & 0 & 2 \\
3 & 4 & 5 \\
6 & 7 & 8 \\
9 & 10 & 11
\end{bmatrix}
$$

Assume zero-based token IDs and the input sequence:

```text
[2, 0, 3]
```

Answer these questions:

1. What are the vocabulary size $V$ and embedding dimension $D$?
2. What vector is selected for token ID `0`?
3. Write the sequence embedding matrix for `[2, 0, 3]`.
4. What is the shape of the sequence embedding matrix?
5. If a transformer processes the sequence, why might the contextual hidden state for the token at position 0 differ from its initial embedding?

<br/>

### Answers

1. $V=4$, $D=3$.
2. Token ID `0` selects the first row: $[1,0,2]$.
3. The selected rows are:

   $$
   X =
   \begin{bmatrix}
   6 & 7 & 8 \\
   1 & 0 & 2 \\
   9 & 10 & 11
   \end{bmatrix}
   $$

4. The shape is $(3,3)$: three token positions and three features per token.
5. Transformer layers apply attention and other learned transformations. The resulting hidden state can incorporate context from other permitted positions and therefore differs from the initial lookup vector.

<br/>

## 13. Common Misconceptions

### Misconception 1: Token IDs are embeddings

**Correction:** Token IDs are integer indices. The embedding layer uses them to retrieve learned vectors.

<br/>

### Misconception 2: An input embedding fully captures a token's meaning in context

**Correction:** An input embedding is a learned initial representation. Contextual hidden states are formed through transformer computation and can vary with context.

<br/>

### Misconception 3: Vocabulary size and embedding dimension mean the same thing

**Correction:** Vocabulary size determines the number of rows in the embedding matrix; embedding dimension determines the number of features per row.

<br/>

### Misconception 4: Token embeddings and document embeddings are interchangeable

**Correction:** Token embeddings represent vocabulary entries for model input. Document embeddings represent larger text units for tasks such as retrieval, often using a separate embedding model or pooling method.

<br/>

### Misconception 5: Every model ties its input and output embeddings

**Correction:** Weight tying is optional and architecture-dependent.

<br/>

### Misconception 6: Embedding vector coordinates have manually assigned meanings

**Correction:** Embedding parameters are learned through training. Individual coordinates do not generally correspond to simple, predefined human-readable properties.

<br/>

## 14. Revision Questions and Answers

**Q1. What does an embedding layer do?**  
It maps token IDs to learned dense vectors by selecting rows from an embedding matrix.

**Q2. What do $V$ and $D$ represent?**  
$V$ is vocabulary size; $D$ is embedding dimension. The input embedding matrix has shape $(V,D)$.

**Q3. What is the shape of the embedded sequence if there are $S$ tokens and embedding dimension $D$?**  
$(S,D)$ for one sequence, or commonly $(B,S,D)$ for a batch.

**Q4. Why can the same token have different contextual hidden states?**  
The same token can have the same initial embedding lookup, but attention and other transformer operations incorporate surrounding context.

**Q5. How does a document embedding differ from a token embedding?**  
A token embedding is a vector associated with a vocabulary entry. A document embedding represents a larger text input for uses such as semantic retrieval.

**Q6. What does the language-model output projection produce?**  
Vocabulary-sized logits from a hidden representation, which can be converted into probabilities for token prediction.

**Q7. What is weight tying?**  
Sharing the input embedding parameters with the output vocabulary projection, typically using a transpose to match matrix dimensions.

<br/>

## 15. Chapter Summary

- An embedding layer maps token IDs to learned dense vectors.
- The embedding matrix has shape $(V,D)$, where $V$ is vocabulary size and $D$ is embedding dimension.
- A sequence of $S$ token IDs becomes an embedding matrix of shape $(S,D)$; batched inputs commonly have shape $(B,S,D)$.
- Input embeddings are initial lookup vectors; contextual hidden states are produced by transformer computation and can depend on surrounding tokens.
- Token embeddings and document embeddings have different roles, even though both are vectors.
- A language-model output projection maps hidden states to vocabulary logits.
- Weight tying optionally shares parameters between input embeddings and output token scoring.

**Checkpoint:** Explain what is learned in the embedding matrix, trace a token ID lookup with correct dimensions, and describe why the same token's contextual hidden state can vary with context.

<br/>

**Next chapter:** `04_positional_information_and_encoding.md` — Positional Information and Encoding.
