# Chapter 05 — Query, Key, and Value Representations

## Learning Objectives

By the end of this chapter, you should be able to:

- Define queries (Q), keys (K), and values (V) as learned projections of hidden-state vectors.
- Trace `Q = XW_Q`, `K = XW_K`, and `V = XW_V` using small matrices.
- Explain how queries and keys determine attention scores, while values provide the content that attention aggregates.
- Distinguish self-attention from cross-attention by identifying the source of Q, K, and V.
- Understand projection dimensions without assuming that every Transformer uses the same configuration.

<br/>

## 1. Why Are Q, K, and V Needed?

A Transformer processes a sequence as a collection of hidden-state vectors. Let

$$
X \in \mathbb{R}^{n \times d_{\text{model}}}
$$

where `n` is the number of sequence positions and `d_model` is the hidden-state width. Each row of `X` represents one position's current vector representation.

Attention lets each position gather information from other positions. The model learns three linear projections:

- **Query (Q):** represents what each position is looking for when deciding where to attend.
- **Key (K):** represents features other positions can match against their queries.
- **Value (V):** represents the content that can be weighted and combined after attention scores are calculated.

These are useful intuitions, not literal hand-written questions or labels. Q, K, and V are numerical representations learned through training.

<br/>

## 2. The Three Learned Projections

The hidden states are projected using three learned weight matrices:

$$
Q = XW_Q,\qquad K = XW_K,\qquad V = XW_V
$$

For a simple single-head example, the projection matrices may have shapes:

$$
W_Q \in \mathbb{R}^{d_{\text{model}} \times d_k}
$$
$$
W_K \in \mathbb{R}^{d_{\text{model}} \times d_k}
$$
$$
W_V \in \mathbb{R}^{d_{\text{model}} \times d_v}
$$

Therefore:

$$
Q \in \mathbb{R}^{n \times d_k},\quad
K \in \mathbb{R}^{n \times d_k},\quad
V \in \mathbb{R}^{n \times d_v}
$$

Query and key dimensions must match for their dot products to be computed. The value width $d_v$ is specified separately. Real implementations may combine projections into one matrix operation, and multi-head attention introduces per-head dimensions. Exact sizes vary by model.

<br/>

### Projection flow

```text
Hidden states X
     |
     +---- multiply by W_Q ----> Queries Q
     |
     +---- multiply by W_K ----> Keys K
     |
     +---- multiply by W_V ----> Values V
```

The three matrices are learned parameters. During training, optimization adjusts them so that attention supports the model's objective.

<br/>

## 3. Trace Q, K, and V With Small Matrices

Use a deliberately tiny example. Suppose there are two positions and each hidden state has two features:

$$
X =
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
$$

Choose small projection matrices for illustration:

$$
W_Q =
\begin{bmatrix}
1 & 1\\
0 & 1
\end{bmatrix},\quad
W_K =
\begin{bmatrix}
1 & 0\\
1 & 1
\end{bmatrix},\quad
W_V =
\begin{bmatrix}
2 & 0\\
0 & 3
\end{bmatrix}
$$

These values are illustrative, not trained parameters from a real model.

<br/>

### 3.1 Compute the query matrix

$$
Q = XW_Q =
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 1\\
0 & 1
\end{bmatrix}
=
\begin{bmatrix}
1 & 1\\
0 & 1
\end{bmatrix}
$$

The first position's query is \([1,1]\); the second position's query is \([0,1]\).

<br/>

### 3.2 Compute the key matrix

$$
K = XW_K =
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0\\
1 & 1
\end{bmatrix}
=
\begin{bmatrix}
1 & 0\\
1 & 1
\end{bmatrix}
$$

The two key vectors are $[1,0]$ and $[1,1]$.

<br/>

### 3.3 Compute the value matrix

$$
V = XW_V =
\begin{bmatrix}
1 & 0\\
0 & 1
\end{bmatrix}
\begin{bmatrix}
2 & 0\\
0 & 3
\end{bmatrix}
=
\begin{bmatrix}
2 & 0\\
0 & 3
\end{bmatrix}
$$

The two value vectors are $[2,0]$ and $[0,3]$.

<br/>

### Results at a glance

| Position | Query | Key | Value |
|---|---|---|---|
| 1 | $[1,1]$ | $[1,0]$ | $[2,0]$ |
| 2 | $[0,1]$ | $[1,1]$ | $[0,3]$ |

Q, K, and V are three different projections of the same hidden states, not three separate input sequences.

<br/>

## 4. How Q and K Produce Attention Scores

Queries and keys are compared using dot products. For scaled dot-product attention:

$$
S = \frac{QK^\top}{\sqrt{d_k}}
$$

For the toy example:

$$
QK^\top =
\begin{bmatrix}
1 & 1\\
0 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 1\\
0 & 1
\end{bmatrix}
=
\begin{bmatrix}
2 & 2\\
1 & 1
\end{bmatrix}
$$

Here \(d_k=2\), so:

$$
S = \frac{1}{\sqrt{2}}
\begin{bmatrix}
2 & 2\\
1 & 1
\end{bmatrix}
$$

Each row corresponds to a query position, and each column corresponds to a key position. A score indicates compatibility between that query and key. Softmax is applied across each row (subject to any attention mask) to obtain attention weights.

**Important:** the scores are not the final output. They determine how strongly each query uses each available value vector.

<br/>

## 5. How V Supplies the Aggregated Content

Once attention weights are calculated, they form weighted sums of the value vectors:

$$
\operatorname{Attention}(Q,K,V)
= \operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

Conceptually:

```text
Q and K
   |
   v
Compatibility scores
   |
   v
Softmax (plus any applicable mask)
   |
   v
Attention weights -----------+
                              |
V ----------------------------+--> Weighted sum of value vectors
                                      |
                                      v
                               Attention output
```

- **Q and K determine the weighting pattern.**
- **V supplies the vectors being weighted and combined.**

A position can use its query to assign different weights to values associated with available key positions. The output is generally a weighted combination, not simply a copy of one input vector.

<br/>

## 6. Self-Attention vs Cross-Attention

The key distinction is the source of the hidden states used to construct Q, K, and V.

### Self-attention

In self-attention, Q, K, and V are all projected from the same sequence's hidden states:

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V
$$

```text
Sequence hidden states X
       |          |          |
      W_Q        W_K        W_V
       |          |          |
       Q          K          V
```

This lets positions in a sequence gather information from other positions in that same sequence, subject to the attention mask.

<br/>

### Encoder-decoder cross-attention

In a typical encoder-decoder Transformer, decoder hidden states supply queries, while encoder output states supply keys and values:

$$
Q=X_{\text{decoder}}W_Q
$$
$$
K=X_{\text{encoder}}W_K,\quad
V=X_{\text{encoder}}W_V
$$

```text
Decoder hidden states ----------------> W_Q ---> Q
                                                   \
                                                    > Attention output
                                                   /
Encoder output states -------------> W_K ---> K --+
                              \----> W_V ---> V --+
```

This lets decoder positions select and combine information from the encoded input sequence. The encoder and decoder sequence lengths may differ, so Q can have a different number of rows from K and V.

| Property | Self-attention | Encoder-decoder cross-attention |
|---|---|---|
| Query source | Current sequence states | Decoder states |
| Key source | Same sequence states | Encoder output states |
| Value source | Same sequence states | Encoder output states |
| Main role | Mix information within a sequence | Let decoder states use encoded input information |

These are common patterns; implementations can vary. Identify which hidden-state sequence is projected into each of Q, K, and V.

<br/>

## 7. Projection Dimensions: What Is Fixed and What Varies?

Use the symbols carefully:

- $d_{\text{model}}$: width of the model's hidden states.
- $d_k$: width of each query and key vector in the attention operation.
- $d_v$: width of each value vector.

For $n_q$ query positions and $n_k$ key/value positions:

$$
Q \in \mathbb{R}^{n_q\times d_k},\quad
K \in \mathbb{R}^{n_k\times d_k},\quad
V \in \mathbb{R}^{n_k\times d_v}
$$

Then $QK^\top$ has shape $n_q \times n_k$, and multiplying attention weights by V produces an output of shape $n_q \times d_v$.

Do not assume every Transformer uses the same hidden width, head count, or projection size. In multi-head attention, the model projects into several head-specific Q/K/V representations. Implementations may use separate matrices or a combined projection matrix. Exact dimensions depend on the architecture and configuration.

<br/>

## 8. Common Misconceptions

1. **“Q, K, and V are three input documents.”** No. They are learned projections of hidden-state vectors.
2. **“A query is a natural-language search question.”** Not in this context. “Query” is an analogy for a learned vector used to compute compatibility scores.
3. **“Keys contain the answer and values contain the question.”** This is not a reliable literal interpretation. Keys participate in scoring; values supply the content aggregated by attention weights.
4. **“Q, K, and V are manually designed.”** Normally, their projection weights are learned during training rather than written as hand-crafted search rules.
5. **“Every Transformer has identical Q/K/V dimensions.”** No. Dimensions depend on architecture and implementation.
6. **“Cross-attention is just another name for self-attention.”** No. In the standard encoder-decoder pattern, Q comes from decoder states, while K and V come from encoder outputs.

<br/>

## 9. Practice

### Task A — Label the sources

For each case, identify where Q, K, and V come from.

**Case 1: Self-attention over a paragraph**

A sequence of paragraph hidden states is passed to an attention layer.

- Q source: ____________________
- K source: ____________________
- V source: ____________________

**Case 2: Encoder-decoder cross-attention**

The decoder is generating an output sequence from an encoded input.

- Q source: ____________________
- K source: ____________________
- V source: ____________________

<br/>

### Task B — Explain the roles

In two or three sentences, explain why the model needs separate Q, K, and V projections instead of treating the hidden states as one undifferentiated representation.

<br/>

### Task C — Check dimensions

Suppose there are 4 query positions, 6 key/value positions, $d_k=3$, and $d_v=5$.

1. What is the shape of Q?
2. What is the shape of K?
3. What is the shape of V?
4. What is the shape of $QK^\top$?
5. What is the shape of the attention output after multiplying the attention weights by V?

<br/>

## 10. Practice Answers

### Task A

**Case 1 — Self-attention**

- Q source: paragraph hidden states.
- K source: the same paragraph hidden states.
- V source: the same paragraph hidden states.

Each source is passed through its own learned projection matrix.

**Case 2 — Encoder-decoder cross-attention**

- Q source: decoder hidden states.
- K source: encoder output states.
- V source: encoder output states.

<br/>

### Task B — Example answer

Q and K provide learned representations used to calculate compatibility scores between positions. Those scores become attention weights, which determine how the model combines V vectors. Separate projections let the model learn different representations for matching information and supplying the content to be aggregated.

<br/>

### Task C

1. $Q$: $4\times3$
2. $K$: $6\times3$
3. $V$: $6\times5$
4. $QK^\top$: $4\times6$
5. Attention output: $4\times5$

<br/>

## 11. Chapter Summary

- Q, K, and V are learned linear projections of hidden-state vectors.
- Queries and keys determine attention compatibility scores.
- Attention weights form weighted combinations of value vectors.
- Self-attention projects Q, K, and V from the same sequence's hidden states.
- In standard encoder-decoder cross-attention, Q comes from decoder states, while K and V come from encoder outputs.
- Projection dimensions vary across architectures; track matrix shapes rather than assuming one universal configuration.

<br/>

**Checkpoint:** Explain why Q, K, and V are not separate input documents or hand-written search queries. A strong answer should mention learned projections, their different roles in the attention computation, and the source of the hidden states in self-attention versus cross-attention.
