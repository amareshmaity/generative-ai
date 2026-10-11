# Chapter 04 — Positional Information and Encoding

**Level 3: Transformer Architecture and Tokenization**  
**Structured GenAI Engineering Notes**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Explain why attention needs information about sequence position.
- Describe sinusoidal and learned absolute position embeddings.
- Explain the basic ideas behind relative-position methods and rotary position embeddings (RoPE).
- Understand that positional information enters transformer computation differently across architectures.
- Explain why context limits exist and why longer-context behavior must be validated.

<br/>

## 2. Why Does a Transformer Need Positional Information?

Self-attention compares token representations and combines information across positions. However, the basic attention operation does not automatically encode the order in which tokens appeared.

Consider these two sentences:

```text
The dog chased the cat.
The cat chased the dog.
```

They contain almost the same words, but the word order changes who chased whom. A model needs information about token positions and relationships to distinguish the two sequences.

<br/>

### A simple intuition

Imagine a set of word cards laid on a table. If the cards contain only the words but the model is not told how they are arranged, it may have difficulty distinguishing different orders. Positional information supplies signals that help the model reason about sequence structure.

For token representations $x_1, x_2, \ldots, x_S$, the index $i$ identifies a token's position in the sequence. A positional method allows the model's computation to use information related to these positions.

**Important:** Positional information is not necessarily added as a separate vector to every token embedding. Different transformer architectures introduce position information in different ways.

<br/>

## 3. Absolute and Relative Position Information

Two broad ways of representing position are **absolute** and **relative** position information.

### 3.1 Absolute position information

Absolute position methods encode a token's position within a sequence. For example, a token may receive position information indicating that it appears at position 1, 2, 3, and so on.

An absolute position representation can help distinguish:

```text
Position 1: The
Position 2: dog
Position 3: chased
Position 4: the
Position 5: cat
```

from a sequence in which the same tokens appear at different positions.

<br/>

### 3.2 Relative position information

Relative position methods represent information about the relationship between token positions, such as how far apart two tokens are or which one comes first.

For example, a method may help the model distinguish a token immediately before another token from one that occurs many positions earlier.

Relative position information is useful because many sequence relationships depend on the distance or ordering between tokens, not only on their absolute indices.

These are broad categories. Specific methods differ in where and how they introduce positional information into the computation.

<br/>

## 4. Sinusoidal Positional Encoding

**Sinusoidal positional encoding** uses fixed sine and cosine functions at different frequencies to create a vector for each position.

In the original Transformer formulation, these position vectors are added to token embeddings before the transformer blocks.

For position $pos$ and feature-pair index $i$, the encoding is defined as:

$$
PE(pos, 2i) =
\sin\left(\frac{pos}{10000^{2i/D}}\right)
$$

$$
PE(pos, 2i+1) =
\cos\left(\frac{pos}{10000^{2i/D}}\right)
$$

Where:

- $pos$ is the token position.
- $i$ indexes pairs of embedding dimensions.
- $D$ is the embedding dimension.
- $PE$ is the positional encoding vector.

Different dimensions use different frequencies. This gives each position a pattern of sine and cosine values.

<br/>

### Why use sine and cosine?

- The encoding is deterministic; it does not need to be learned as a parameter table.
- Different positions receive different patterns.
- Multiple frequencies provide signals at different positional scales.

<br/>

### Conceptual example

```text
Token embeddings:       [e1, e2, e3, ...]
Positional encoding:    [p1, p2, p3, ...]

Original Transformer:
Input representation = token embedding + positional encoding
```

The vectors must have compatible dimensions for element-wise addition.

**Limitation:** Sinusoidal encodings do not guarantee that a model will generalize reliably to arbitrarily long sequences. Performance beyond the training or supported context range must be tested.

<br/>

## 5. Learned Absolute Position Embeddings

A learned absolute position embedding method uses a trainable table of position vectors.

Let the maximum number of supported positions in the table be $P$ and the hidden dimension be $D$. The position embedding table can be represented as:

$$
E_{\text{pos}} \in \mathbb{R}^{P \times D}
$$

For a token at position $i$, the model looks up the corresponding row $E_{\text{pos},i}$.

In a common design, the input representation is:

$$
x_i = E_{\text{token},i} + E_{\text{pos},i}
$$

Where:

- $E_{\text{token},i}$ is the token embedding.
- $E_{\text{pos},i}$ is the learned position vector.
- $x_i$ is the combined representation.

<br/>

### Advantages

- Position vectors are optimized during training.
- The model can learn positional patterns useful for its tasks.

<br/>

### Limitations

- The learned table has a configured number of positions.
- Using positions beyond the trained or supported range may require an extension method or may not be supported.
- The model's ability to handle longer sequences depends on more than the existence of a position table.

Sinusoidal and learned absolute position embeddings are both ways to associate position information with token representations, but one uses fixed functions while the other learns position vectors.

<br/>

## 6. Relative Position Methods

Relative position methods focus on the relationships between positions rather than relying only on a separate vector for each absolute position.

For example, if a query token is at position $i$ and another token is at position $j$, a relative method may use the offset:

$$
\Delta = j-i
$$

The sign and magnitude of this offset can represent direction and distance, depending on the method's convention.

Relative-position information can be introduced into attention scores, attention representations, or other parts of a model's computation. There is no single implementation shared by every relative-position method.

<br/>

### Intuition

Compare the word `not` in these examples:

```text
I do not recommend it.
I do recommend it.
```

The relationship between `not` and nearby words is important. Relative position methods provide ways for a model to represent positional relationships that may be useful for such patterns. The example illustrates the motivation; it does not imply that relative position alone determines meaning.

<br/>

## 7. Rotary Position Embeddings (RoPE)

**Rotary Position Embeddings (RoPE)** introduce positional information by applying position-dependent rotations to query and key representations used in attention.

Unlike the original Transformer design, where positional vectors are added to token embeddings, RoPE changes the query and key vectors used in the attention computation.

At a conceptual level:

1. The transformer produces query and key vectors.
2. A position-dependent transformation is applied to those vectors.
3. Attention scores are calculated using the transformed queries and keys.
4. The resulting attention computation can reflect positional relationships.

The rotation is applied across pairs or groups of vector dimensions according to the implementation.

<br/>

### Why is RoPE important?

- It incorporates position information directly into attention's query-key interaction.
- Its formulation gives attention scores a structured dependence on relative position.
- It is used in many modern decoder-only language-model architectures.

RoPE does not mean that every model can automatically handle unlimited context. Practical context limits and long-context quality depend on training, model configuration, implementation, and any extension or scaling method used.

<br/>

## 8. How Positional Methods Enter the Computation

Do not assume every transformer adds the same positional vector to its token embeddings.

| Method | Where positional information enters | Main idea |
|---|---|---|
| Sinusoidal absolute encoding | Commonly added to token embeddings in the original Transformer design | Fixed sine/cosine vectors represent positions |
| Learned absolute position embeddings | Commonly added to token embeddings | A trainable vector is assigned to each supported position |
| Relative-position methods | May modify attention scores or representations, depending on the method | Encode relationships between positions |
| RoPE | Applied to query and key vectors in attention | Position-dependent rotations make attention position-aware |

This table is a conceptual comparison. Implementations may include variations, combinations, or additional position-handling mechanisms.

<br/>

### Conceptual data-flow diagrams

**Absolute position addition:**

```text
Token IDs
   |
   v
Token embedding lookup ---- Position index
          |                       |
          v                       v
    Token vector             Position vector
          |                       |
          +-----------+-----------+
                      |
                      v
              Element-wise addition
                      |
                      v
             Transformer block
```

**RoPE-style position handling:**

```text
Hidden states
     |
     v
Query and key projections
     |
     +--------------------------+
     |                          |
     v                          v
Position-dependent          Position-dependent
rotation of Q               rotation of K
     |                          |
     +-------------+------------+
                   |
                   v
             Attention scores
                   |
                   v
          Weighted value aggregation
```

These diagrams simplify the real computations. They show where positional information enters, not every operation in a full transformer block.

<br/>

## 9. Position Limits and Context Length

A model's **context window** is the amount of token context it can accept or process under its supported configuration. Positional methods are one factor that affects context handling, but they are not the only factor.

Important distinctions:

- **Configured context limit:** The maximum input/context length supported by a model or service under specified conditions.
- **Training length:** The sequence lengths used during training or adaptation.
- **Position representation:** The method used to encode or incorporate position.
- **Long-context capability:** How well the model uses information across longer sequences.

A model may technically accept a long sequence but still fail to use information from all parts of it reliably.

<br/>

### Why longer context requires validation

Longer sequences can increase:

- Attention computation and memory requirements.
- Prefill latency for language-model inference.
- The amount of irrelevant information competing for the model's attention.
- The risk that relevant information is overlooked or confused with other context.

The behavior depends on the model and inference implementation. Efficient attention methods and positional extensions can change the trade-offs, but do not remove the need to evaluate quality.

<br/>

### Practical validation checklist

When evaluating a model at longer context lengths:

1. Verify the model and provider's documented context limits.
2. Test at several sequence lengths, including realistic maximum-length inputs.
3. Place relevant facts at different positions in the input.
4. Measure answer correctness and whether the model uses the relevant evidence.
5. Measure latency, memory use, and cost where applicable.
6. Record any positional scaling or context-extension settings used.

**Key principle:** A larger advertised context window does not guarantee reliable use of every token in that window.

<br/>

## 10. Code Example: Comparing Reordered Sequences

This small NumPy example demonstrates the central motivation for positional information. It does not implement a complete transformer.

```python
import numpy as np

# Toy token embeddings: one 3-dimensional vector per token.
embeddings = {
    "dog": np.array([1.0, 0.0, 0.0]),
    "chased": np.array([0.0, 1.0, 0.0]),
    "cat": np.array([0.0, 0.0, 1.0]),
}

sequence_a = ["dog", "chased", "cat"]
sequence_b = ["cat", "chased", "dog"]

X_a = np.stack([embeddings[token] for token in sequence_a])
X_b = np.stack([embeddings[token] for token in sequence_b])

print("Sequence A:")
print(X_a)

print("Sequence B:")
print(X_b)

print("Same set of token vectors:", np.array_equal(
    np.sort(X_a, axis=0),
    np.sort(X_b, axis=0)
))
```

The sequences contain the same token embeddings in a different order. The order of the rows differs.

Without any position-aware operation, a basic self-attention layer without positional information is permutation-equivariant: permuting the input token representations permutes the outputs correspondingly. It does not independently identify the original sequence order. Positional information gives the model a way to distinguish positions and their relationships.

The final printed comparison is only a simple numerical illustration; the key concept is that the sequence order differs even though the same token vectors are present.

<br/>

## 11. Practice Exercise

Consider these sequences:

```text
A: The teacher praised the student.
B: The student praised the teacher.
```

Answer the following:

1. Why can token order affect the meaning?
2. What limitation would arise if the model had no position-aware information?
3. How does sinusoidal positional encoding introduce position?
4. How does learned absolute position embedding differ from sinusoidal encoding?
5. Where does RoPE apply its position-dependent transformation?
6. Why is a context-window limit not the same as a guarantee of long-context accuracy?

<br/>

### Answers

1. Word order changes the grammatical roles of `teacher` and `student`.
2. Basic attention without positional information does not inherently identify sequence order; it cannot reliably distinguish order-dependent relationships from token content alone.
3. It generates fixed sine and cosine vectors for positions and, in the original Transformer design, adds them to token embeddings.
4. Learned absolute position embeddings use trainable position vectors, while sinusoidal encodings are generated by fixed functions.
5. RoPE applies position-dependent rotations to query and key representations used in attention.
6. A model may accept a long sequence yet fail to use distant or relevant information reliably. Quality must be tested at realistic lengths.

<br/>

## 12. Common Misconceptions

### Misconception 1: Attention automatically understands word order

**Correction:** The basic attention operation needs positional information or another order-aware mechanism to distinguish sequence positions.

<br/>

### Misconception 2: Every transformer adds a positional vector to token embeddings

**Correction:** Some models add absolute position vectors, while relative methods and RoPE introduce positional information elsewhere in the computation.

<br/>

### Misconception 3: Sinusoidal encodings guarantee unlimited context

**Correction:** A fixed positional formula does not guarantee reliable generalization to arbitrary sequence lengths.

<br/>

### Misconception 4: A learned position table can always be extended without consequences

**Correction:** Position limits and extension behavior depend on the model. Extending the table or changing position handling may require additional methods and validation.

<br/>

### Misconception 5: RoPE removes context limits

**Correction:** RoPE is a positional method, not a guarantee of unlimited input length or reliable long-context performance.

<br/>

### Misconception 6: A model's advertised context window tells the whole story

**Correction:** Supported length and effective use of context are different. Accuracy, latency, memory, and cost should be tested at realistic lengths.

<br/>

## 13. Revision Questions and Answers

**Q1. Why does a transformer need positional information?**  
Because basic attention does not by itself encode the original order of tokens. Position-aware mechanisms help the model distinguish sequences and relationships that depend on order.

**Q2. What is sinusoidal positional encoding?**  
A fixed encoding formed from sine and cosine functions at different frequencies, commonly added to token embeddings in the original Transformer design.

**Q3. What is a learned absolute position embedding?**  
A trainable vector associated with each supported absolute sequence position.

**Q4. What is the difference between absolute and relative position information?**  
Absolute methods represent a token's position in a sequence; relative methods represent relationships such as offsets or distances between positions.

**Q5. How does RoPE introduce positional information?**  
It applies position-dependent rotations to query and key vectors in attention.

**Q6. Why should long-context behavior be tested?**  
A model can accept a long sequence without reliably using all its information. Longer inputs can also increase computation, latency, and memory requirements.

<br/>

## 14. Chapter Summary

- Position matters because word order can change meaning.
- Basic attention requires positional information or another order-aware mechanism to distinguish sequence positions.
- Sinusoidal absolute encodings use fixed sine and cosine functions.
- Learned absolute position embeddings use trainable position vectors.
- Relative-position methods represent relationships between positions.
- RoPE applies position-dependent rotations to queries and keys in attention.
- Positional methods enter transformer computation in different ways; not every model adds a position vector to token embeddings.
- Context limits, training length, positional methods, and effective long-context quality are related but distinct.
- Long-context behavior should be evaluated for accuracy, latency, memory, and cost.

**Checkpoint:** Explain positional information without assuming every transformer adds the same positional vector to its embeddings. Compare reordered sequences and describe how absolute, relative, and rotary methods incorporate position differently.

<br/>

**Next chapter:** `05_query_key_and_value_representations.md` — Query, Key, and Value Representations.
