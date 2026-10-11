# Chapter 06 — Self-Attention and Scaled Dot-Product Attention

## Learning Objectives

By the end of this chapter, you should be able to:

- Trace the scaled dot-product attention computation:
  $$
  \operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)V
  $$
  where $M$ represents an optional additive attention mask.
- Explain dot-product scores, scaling, row-wise softmax, and weighted aggregation.
- Distinguish the score matrix, attention-weight matrix, and attention output.
- Track tensor dimensions in a small worked example.
- Explain why standard full attention has a quadratic attention-matrix size with respect to sequence length.
- Understand why attention weights alone do not fully explain a model's behavior.

<br/>

## 1. What Is Self-Attention?

Self-attention lets each position in a sequence gather information from other positions in that same sequence. Starting from hidden states $X$, a layer produces queries, keys, and values:

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
$$

The attention operation compares queries with keys, converts the scores into weights, and uses those weights to combine value vectors.

In self-attention, Q, K, and V come from the same sequence's hidden states. A mask may restrict which positions each query is allowed to use.

<br/>

## 2. The Scaled Dot-Product Attention Formula

A common expression is:

$$
O=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V
$$

where:

- $Q$: query matrix.
- $K$: key matrix.
- $K^\top$: transpose of K.
- $d_k$: query/key vector dimension.
- $M$: optional additive mask, with disallowed positions assigned a very large negative value (conceptually $-\infty\$.
- `softmax`: converts each row of scores into a distribution of attention weights.
- $V$: value matrix.
- $O$: output matrix, one output vector per query position.

If no mask is needed, omit $M$. Some implementations apply masks through equivalent mechanisms rather than literally adding a matrix.

<br/>

### Computation pipeline

```text
Queries Q and Keys K
          |
          v
       Q K^T
          |
          v
   Divide by sqrt(d_k)
          |
          v
     Add attention mask
          |
          v
  Row-wise softmax scores
          |
          v
    Attention weights
          |
          +---------- Values V
          |                 |
          +------ weighted sum
                    |
                    v
             Output vectors O
```

<br/>

## 3. Step 1 — Calculate Dot-Product Scores

Each query vector is compared with every key vector by taking a dot product. A larger score generally indicates greater compatibility between that query and key in the learned representation.

If there are $n$ positions, Q and K each have $n$ rows. Their product $QK^\top$ produces an $n\times n$ score matrix.

- Each **row** represents one query position.
- Each **column** represents one key position.
- Entry $(i,j)$ measures the compatibility between query $i$ and key $j$.

The score matrix is not yet a probability distribution. Scores can be positive, negative, or zero, and their row sums need not equal one.

<br/>

## 4. Step 2 — Scale the Scores

The raw dot products are divided by $\sqrt{d_k}$:

$$
S=\frac{QK^\top}{\sqrt{d_k}}
$$

As the query/key dimension grows, dot products can tend to grow in magnitude. Large score magnitudes can make softmax distributions very sharp, producing small gradients in saturated regions. Scaling helps keep score magnitudes more manageable.

The divisor is the square root of the query/key dimension $d_k$, not necessarily the model's full hidden width $d_{\text{model}}$.

<br/>

## 5. Step 3 — Apply the Mask and Row-Wise Softmax

A mask determines which key positions each query may attend to. For an additive mask, disallowed entries are set to a very large negative value, often represented conceptually as $-\infty$, before softmax.

Softmax is applied **separately to each row**:

$$
A_{ij}=\frac{e^{S_{ij}}}{\sum_{t}e^{S_{it}}}
$$

Here, $S$ includes the scaling and any mask. For a row with at least one allowed position, its attention weights sum to one (up to numerical precision):

$$
\sum_j A_{ij}=1
$$

A disallowed position receives zero weight in the idealized formulation. Different masks serve different purposes; causal and padding masks are covered in the masking chapter.

**Do not confuse scores with weights:**

- **Score matrix $S$:** compatibility values before softmax.
- **Attention matrix $A$:** normalized weights after mask and softmax.
- **Output matrix $O$:** weighted combinations of value vectors.

<br/>

## 6. Step 4 — Use the Weights to Aggregate Values

The output is computed as:

$$
O=AV
$$

For query position $i$:

$$
O_i=\sum_j A_{ij}V_j
$$

Each output vector is a weighted sum of the value vectors at allowed key positions. If one weight is large, that value vector contributes more strongly; a small weight contributes less.

The output is not simply the attention-weight row. The weights are coefficients, while the values contain the vectors being combined.

<br/>

## 7. Worked Example With Small Matrices

For clarity, use two query positions and two key/value positions, with $d_k=d_v=2$. Let:

$$
Q=
\begin{bmatrix}
1&0\\
0&1
\end{bmatrix},\quad
K=
\begin{bmatrix}
1&0\\
1&1
\end{bmatrix},\quad
V=
\begin{bmatrix}
2&0\\
0&4
\end{bmatrix}
$$

This is a toy example, not a trained model. No mask is applied.

<br/>

### 7.1 Compute raw scores

$$
QK^\top=
\begin{bmatrix}
1&0\\
0&1
\end{bmatrix}
\begin{bmatrix}
1&1\\
0&1
\end{bmatrix}
=
\begin{bmatrix}
1&1\\
0&1
\end{bmatrix}
$$

The score matrix has shape $2\times2$.

<br/>

### 7.2 Scale scores

Since $d_k=2$:

$$
S=\frac{1}{\sqrt{2}}
\begin{bmatrix}
1&1\\
0&1
\end{bmatrix}
\approx
\begin{bmatrix}
0.707&0.707\\
0&0.707
\end{bmatrix}
$$

<br/>

### 7.3 Apply row-wise softmax

The first row has equal scores, so its weights are $[0.5,0.5]$.

For the second row, the scores are approximately $[0,0.707]$. Softmax gives approximately $[0.330,0.670]$.

Thus:

$$
A\approx
\begin{bmatrix}
0.500&0.500\\
0.330&0.670
\end{bmatrix}
$$

Each row sums to approximately one.

<br/>

### 7.4 Aggregate the values

$$
O=AV\approx
\begin{bmatrix}
0.500&0.500\\
0.330&0.670
\end{bmatrix}
\begin{bmatrix}
2&0\\
0&4
\end{bmatrix}
$$

$$
O\approx
\begin{bmatrix}
1.000&2.000\\
0.660&2.680
\end{bmatrix}
$$

Interpretation:

- Query 1 combines half of each value vector: $0.5[2,0]+0.5[0,4]=[1,2]$.
- Query 2 combines the values with weights approximately 0.330 and 0.670, producing approximately $[0.660,2.680]$.

<br/>

### Dimensions at every step

| Quantity | Shape | Meaning |
|---|---:|---|
| \$Q\$ | $2\times2$ | Two query vectors |
| \$K^\top\$ | $2\times2$ | Transposed key matrix |
| \$QK^\top\$ | $2\times2$ | Pairwise scores |
| \$S\$ | $2\times2$ | Scaled scores |
| \$A\$ | $2\times2$ | Row-wise attention weights |
| \$V\$ | $2\times2$ | Two value vectors |
| \$O=AV\$ | $2\times2$ | One output vector per query |

<br/>

## 8. Verify the Example With NumPy

```python
import numpy as np

Q = np.array([
    [1.0, 0.0],
    [0.0, 1.0],
])

K = np.array([
    [1.0, 0.0],
    [1.0, 1.0],
])

V = np.array([
    [2.0, 0.0],
    [0.0, 4.0],
])

d_k = Q.shape[-1]

# 1. Pairwise dot-product scores
scores = Q @ K.T

# 2. Scale the scores
scaled_scores = scores / np.sqrt(d_k)

# 3. Stable row-wise softmax
shifted = scaled_scores - scaled_scores.max(axis=-1, keepdims=True)
exp_scores = np.exp(shifted)
weights = exp_scores / exp_scores.sum(axis=-1, keepdims=True)

# 4. Weighted aggregation of values
output = weights @ V

print("Scores:\n", scores)
print("Scaled scores:\n", scaled_scores)
print("Attention weights:\n", weights)
print("Row sums:", weights.sum(axis=-1))
print("Output:\n", output)

# Each row's weights should sum to 1 when no row is fully masked.
assert np.allclose(weights.sum(axis=-1), 1.0)
```

The stable softmax subtracts the maximum score in each row before exponentiation. This improves numerical stability without changing the resulting probabilities.

<br/>

## 9. Attention-Matrix Size and Computational Cost

For standard full self-attention over a sequence of length $n$, the score and attention matrices each have shape:

$$
n\times n
$$

That means their number of entries grows as $n^2$. If sequence length doubles, the number of entries in the attention matrix becomes four times as large.

For example:

| Sequence length $n$ | Entries in an $n\times n$ matrix |
|---:|---:|
| 128 | 16,384 |
| 512 | 262,144 |
| 1,024 | 1,048,576 |
| 4,096 | 16,777,216 |

The pairwise attention computation has quadratic scaling with sequence length. The Q/K/V projections and value aggregation also have costs, but the $n\times n$ attention matrix is a key reason standard full attention becomes expensive for long sequences. Memory-efficient implementations can avoid materializing the entire matrix, but they do not make standard full attention's pairwise interaction count cease to be quadratic.

<br/>

## 10. Why Attention Weights Alone Do Not Explain Model Behavior

Attention weights show how a particular attention operation distributes its weights over positions. They can be useful for inspecting that operation, but they are not a complete explanation of a model's decision or generated output.

Reasons include:

- The output depends on the **value vectors**, not only on the weights.
- Value and output projections can transform the information.
- Multi-head attention combines information from multiple heads.
- Residual connections, feed-forward layers, normalization, and later layers also affect the final representation.
- Different internal computations can produce similar outputs; a weight pattern alone does not establish causal importance.

Treat an attention map as a view of one part of the computation, not as a definitive explanation of the model's reasoning.

<br/>

## 11. Common Misconceptions

1. **“The score matrix and attention matrix are the same.”** Scores are computed before softmax; attention weights are normalized scores after applying the mask.
2. **“Softmax is applied across the whole matrix.”** In standard attention, it is applied row-wise, over key positions for each query.
3. **“The output is the attention matrix.”** The output is the attention weights multiplied by V.
4. **“Every position can always attend to every other position.”** Masks may restrict allowed positions.
5. **“Attention is linear in sequence length.”** The pairwise matrix in standard full attention has \(n^2\) entries.
6. **“An attention map fully explains a model's behavior.”** It describes one computational component and must be interpreted in the context of the wider model.

<br/>

## 12. Practice

### Task A — Follow the computation

Using the matrices in Section 7:

1. Calculate \(QK^\top\).
2. Divide the score matrix by \(\sqrt{2}\).
3. Calculate the row-wise softmax weights.
4. Verify that each row sums to one.
5. Multiply the attention weights by V to calculate O.

### Task B — Track dimensions

Suppose Q has shape \(5\times4\), K has shape \(7\times4\), and V has shape \(7\times6\).

1. What is the shape of \(QK^\top\)?
2. What is the shape of the attention-weight matrix?
3. What is the shape of the output after multiplying the weights by V?

### Task C — Explain in words

In three or four sentences, explain how one query position combines information from other allowed positions. Distinguish scores, weights, values, and output.

<br/>

## 13. Practice Answers

### Task B

1. $QK^\top$: $5\times7$
2. Attention weights: $5\times7$
3. Output: $5\times6$

<br/>

### Task C — Example answer

A query is compared with all allowed key vectors to produce scores. The scores are scaled and converted by row-wise softmax into weights that sum to one over the allowed positions. Those weights multiply the corresponding value vectors, and their weighted sum becomes the output vector for that query position.

<br/>

## 14. Chapter Summary

- Scaled dot-product attention follows the pattern $\operatorname{softmax}(QK^\top/\sqrt{d_k}+M)V$.
- Dot products create compatibility scores; scaling moderates their magnitude.
- Row-wise softmax converts scores into attention weights over allowed key positions.
- Multiplying weights by V creates one aggregated output vector per query.
- Standard full attention has an $n\times n$ attention matrix, giving quadratic growth in sequence length.
- Attention weights are informative but do not, by themselves, fully explain model behavior.

<br/>

**Checkpoint:** Explain how one position combines information from other allowed positions. Include the roles of scores, scaling, row-wise softmax, values, and the resulting weighted sum.
