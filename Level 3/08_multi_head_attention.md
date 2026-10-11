# Chapter 08 — Multi-Head Attention

## Learning Objectives

- Explain how multiple learned attention heads operate in parallel.
- Track per-head query, key, and value projections and their dimensions.
- Trace attention, concatenation, and the final output projection.
- Compare single-head and multi-head attention conceptually.
- Explain why heads do not have fixed, manually assigned linguistic jobs.
- Describe multi-query attention (MQA) and grouped-query attention (GQA), including their relationship to key-value cache memory.

<br/>

## 1. Why Use Multi-Head Attention?

A single attention head learns one set of query, key, and value projections. Multi-head attention uses several learned attention heads in parallel. Each head performs its own attention computation, and the resulting outputs are combined.

The motivation is to give the model multiple learned representation pathways for attending to information. Heads can learn different patterns, but their roles are not assigned in advance.

```text
Single-head attention
Input hidden states -> Q, K, V -> One attention operation -> One head output

Multi-head attention
Input hidden states
   |----------|----------|
  Head 1     Head 2     Head H
   |----------|----------|
      Concatenate head outputs
                |
         Output projection
                |
       Combined representation
```

Multi-head attention is not simply repeating an identical computation and averaging the results. Each head typically has its own learned projection parameters.

<br/>

## 2. Per-Head Projections

Let the input hidden-state matrix be:

$$
X \in \mathbb{R}^{B \times T \times d_{\text{model}}}
$$

where $B$ is batch size, $T$ is sequence length, and $d_{\text{model}}$ is hidden-state width.

For each head $h$, the model forms its own projections:

$$
Q_h=XW_Q^{(h)},\quad
K_h=XW_K^{(h)},\quad
V_h=XW_V^{(h)}
$$

One common setup uses:

$$
W_Q^{(h)},W_K^{(h)} \in
\mathbb{R}^{d_{\text{model}}\times d_k}
$$

$$
W_V^{(h)} \in
\mathbb{R}^{d_{\text{model}}\times d_v}
$$

The head computes scaled dot-product attention:

$$
\operatorname{head}_h =
\operatorname{softmax}
\left(
\frac{Q_hK_h^\top}{\sqrt{d_k}}+M
\right)V_h
$$

The mask $M$, when needed, restricts which positions can attend to which keys. Exact dimensions vary by architecture. A common design chooses equal-sized heads so that $H d_v=d_{\text{model}}$, but this is not a universal requirement.

<br/>

## 3. Trace the Complete Multi-Head Computation

1. Project hidden states into per-head Q, K, and V representations.
2. Compute attention scores within each head.
3. Scale scores, apply any mask, and use row-wise softmax.
4. Multiply attention weights by that head's V matrix to produce its output.
5. Concatenate head outputs along the feature dimension.
6. Apply a learned output projection.

The standard conceptual formula is:

$$
\operatorname{MultiHead}(Q,K,V)
=
\operatorname{Concat}(\operatorname{head}_1,\ldots,\operatorname{head}_H)W_O
$$

Here, $W_O$ is the learned output-projection matrix. Implementations commonly use efficient tensor operations rather than explicit Python loops over heads.

<br/>

## 4. Worked Shape Example

Suppose batch size $B=2$, sequence length $T=4$, model width $d_{\text{model}}=8$, number of heads $H=2$, and per-head widths $d_k=d_v=4$. In this example, $H d_v=8=d_{\text{model}}$.

### 4.1 Input

$$
X:(B,T,d_{\text{model}})=(2,4,8)
$$

<br/>

### 4.2 Per-head projections

For each head:

$$
Q_h,K_h,V_h:(2,4,4)
$$

<br/>

### 4.3 Scores and weights

For each head:

$$
Q_hK_h^\top:(2,4,4)
$$

The shape is $(B,T,T)$: every query position is scored against every key position. After scaling, masking, and row-wise softmax, the attention weights remain $(2,4,4)$.

<br/>

### 4.4 Head output

$$
\operatorname{head}_h=A_hV_h:(2,4,4)
$$

Each head returns one four-dimensional output vector per position.

<br/>

### 4.5 Concatenate and project

Concatenating two head outputs along the final dimension gives:

$$
\operatorname{Concat}(\operatorname{head}_1,\operatorname{head}_2):(2,4,8)
$$

A typical output projection has \(W_O\in\mathbb{R}^{8\times8}\), producing:

$$
Y:(2,4,8)
$$

<br/>

### Shape summary

| Stage | Shape |
|---|---|
| Input hidden states $X$ | $(2,4,8)$ |
| Q, K, V for each head | $(2,4,4)$ each |
| Scores/weights for each head | $(2,4,4)$ |
| Output for each head | $(2,4,4)$ |
| Concatenated heads | $(2,4,8)$ |
| Output projection result | $(2,4,8)$ |

This is one common design, not a universal configuration. The output projection must match the actual concatenated width.

<br/>

## 5. A Tiny NumPy Shape Demonstration

This example uses random toy arrays, not trained parameters. It omits dropout, residual connections, normalization, and framework-specific optimizations.

```python
import numpy as np

rng = np.random.default_rng(7)

batch_size, seq_len = 2, 4
d_model, num_heads = 8, 2
d_k = d_v = 4

X = rng.normal(size=(batch_size, seq_len, d_model))

WQ = [rng.normal(size=(d_model, d_k)) for _ in range(num_heads)]
WK = [rng.normal(size=(d_model, d_k)) for _ in range(num_heads)]
WV = [rng.normal(size=(d_model, d_v)) for _ in range(num_heads)]

head_outputs = []

for h in range(num_heads):
    Q = X @ WQ[h]  # (B, T, d_k)
    K = X @ WK[h]  # (B, T, d_k)
    V = X @ WV[h]  # (B, T, d_v)

    scores = (Q @ K.transpose(0, 2, 1)) / np.sqrt(d_k)  # (B, T, T)

    # Stable softmax over key positions.
    scores = scores - scores.max(axis=-1, keepdims=True)
    exp_scores = np.exp(scores)
    weights = exp_scores / exp_scores.sum(axis=-1, keepdims=True)

    head_outputs.append(weights @ V)  # (B, T, d_v)

concatenated = np.concatenate(head_outputs, axis=-1)  # (B, T, H*d_v)
W_O = rng.normal(size=(num_heads * d_v, d_model))
output = concatenated @ W_O  # (B, T, d_model)

print("Input:", X.shape)
print("Each head output:", head_outputs[0].shape)
print("Concatenated:", concatenated.shape)
print("Final output:", output.shape)

assert X.shape == (2, 4, 8)
assert concatenated.shape == (2, 4, 8)
assert output.shape == (2, 4, 8)
```

<br/>

## 6. Single-Head vs Multi-Head Attention

| Aspect | Single-head attention | Multi-head attention |
|---|---|---|
| Attention computations | One | Several in parallel |
| Learned Q/K/V projections | One set | A set per head, conceptually |
| Output before final projection | One head representation | Concatenated head representations |
| Potential benefit | Simpler representation pathway | Multiple learned attention pathways |
| Performance guarantee | No guarantee of best performance | More heads do not guarantee better performance |

Multi-head attention offers representational flexibility, but it also changes parameterization and computation. Its benefit depends on model size, training data, optimization, architecture, and task.

<br/>

## 7. Do Heads Have Fixed Linguistic Roles?

It is common to describe a head as focusing on nearby tokens, syntax, coreference, or other patterns. Such patterns may emerge in trained models, but they are observations rather than predefined roles.

- Head 1 is not manually assigned the job of finding nouns.
- Head 2 is not automatically the punctuation head.
- A head's behavior can vary by layer, model, input, and context.
- Some heads may be redundant or difficult to interpret.

Projection parameters are learned through training. A head may exhibit a recognizable pattern, but that does not mean its function was explicitly programmed or that the pattern fully explains its contribution.

<br/>

## 8. Multi-Query Attention and Grouped-Query Attention

Multi-head attention often uses separate key and value projections for every query head. During autoregressive generation, previously computed keys and values may be stored and reused instead of recomputed for every new token. These tensors form the **key-value (KV) cache**.

For long sequences or large batches, KV-cache memory can be a significant inference cost. Two variants reduce the number of key/value heads.

<br/>

### Multi-query attention (MQA)

- Uses multiple query heads.
- Shares one key head and one value head across query heads.
- Reduces the amount of key/value state that must be cached compared with a design with separate K/V heads for every query head.

<br/>

### Grouped-query attention (GQA)

- Uses multiple query heads grouped around a smaller number of key/value heads.
- Each group of query heads shares its group's K/V representation.
- Provides a design between one shared K/V head and fully separate K/V heads.

```text
Multi-head attention:
Q1  Q2  Q3  Q4
|   |   |   |
K1  K2  K3  K4
V1  V2  V3  V4

Multi-query attention:
Q1  Q2  Q3  Q4
 \   |   |   /
      K1
      V1

Grouped-query attention:
Q1  Q2  Q3  Q4
 \  /     \  /
 K1       K2
 V1       V2
```

The diagrams are conceptual. The number and size of groups depend on the model configuration. MQA and GQA do not eliminate attention; they change how query heads share keys and values. They are especially relevant to inference memory and throughput, though actual performance depends on implementation and hardware.

<br/>

## 9. Common Misconceptions

1. **“Each head is assigned a fixed linguistic job.”** Head behavior is learned; observed roles are not guaranteed or manually prescribed.
2. **“Head outputs are averaged by default.”** Standard multi-head attention typically concatenates head outputs and applies an output projection.
3. **“The number of heads must equal the hidden width.”** Head count and per-head dimensions are configuration choices.
4. **“More heads always improve performance.”** Benefits depend on the model and training conditions.
5. **“MQA and GQA remove the query heads.”** They retain multiple query heads while reducing the number of K/V heads.
6. **“The KV cache stores attention weights.”** The usual KV cache stores key and value representations for reuse during autoregressive inference.

<br/>

## 10. Practice

### Task A — Track shapes

A model has $B=1$, $T=3$, $d_{\text{model}}=12$, $H=3$, and $d_k=d_v=4$. Fill in the shapes:

1. Input $X$: ____________________
2. Q, K, and V for one head: ____________________
3. Score matrix for one head: ____________________
4. Output for one head: ____________________
5. Concatenated heads: ____________________
6. Final output if $W_O$ maps the concatenated width back to $d_{\text{model}}$: ____________________

<br/>

### Task B — Explain the architecture

Explain why head outputs are concatenated and passed through an output projection rather than treating each head as a separate final answer.

<br/>

### Task C — Compare attention variants

Explain how MQA and GQA differ from the common multi-head arrangement in their treatment of key and value heads. Why can this matter for inference memory?

<br/>

## 11. Practice Answers

### Task A

1. $X:(1,3,12)$
2. Q, K, V for one head: $(1,3,4)$ each
3. Score matrix: $(1,3,3)$
4. Output for one head: $(1,3,4)$
5. Concatenated heads: $(1,3,12)$
6. Final output: $(1,3,12)$

<br/>

### Task B — Example answer

Each head produces a representation based on its learned projections and attention pattern. Concatenation preserves the feature outputs from all heads, and the output projection learns how to mix those features into the model's output width. This lets the model combine information from parallel heads rather than treating them as independent final predictions.

<br/>

### Task C — Example answer

In a common multi-head arrangement, each query head has its own K/V head. MQA shares one K/V head across query heads, while GQA shares K/V heads within groups of query heads. Fewer K/V heads mean fewer key and value tensors need to be stored in the KV cache, which can reduce inference memory requirements.

<br/>

## 12. Chapter Summary

- Multi-head attention performs several learned attention computations in parallel.
- Each head projects hidden states into Q, K, and V, computes attention, and produces an output.
- Head outputs are typically concatenated and passed through a learned output projection.
- Head roles emerge through training; they are not assigned fixed linguistic jobs.
- Increasing the number of heads does not automatically improve performance.
- MQA and GQA reduce the number of K/V heads relative to query heads, which can reduce KV-cache memory during inference.

<br/>

**Checkpoint:** Explain how heads are combined and why more heads do not automatically imply better performance. Include per-head attention, concatenation, the output projection, and the role of learned parameters.
