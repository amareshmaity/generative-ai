# Chapter 09 — Feed-Forward Networks

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain the position-wise feed-forward network (FFN) applied to each token's hidden state.
- Describe expansion, activation, and projection back to the model's hidden dimension.
- Compare the FFN's role with attention's mixing of information across sequence positions.
- Recognize GELU and gated feed-forward variants such as SwiGLU.
- Explain why the same FFN parameters are shared across sequence positions within a Transformer block.

<br/>

## 1. What Is a Feed-Forward Network?

A Transformer block commonly contains an attention sublayer and a feed-forward network (FFN). The FFN applies a learned transformation to each position's hidden-state vector.

If the input hidden states are:

$$
X \in \mathbb{R}^{B\times T\times d_{\text{model}}}
$$

then the FFN transforms the final feature dimension while preserving the batch size $B$ and sequence length $T$. Here, $d_{\text{model}}$ is the model's hidden-state width.

The network is called **position-wise** because it processes each token position independently of the other positions at this sublayer. It does not directly mix information between token positions; attention provides that cross-position mixing.

<br/>

## 2. The Standard Expansion–Activation–Projection Pattern

A common two-layer FFN is:

$$
\operatorname{FFN}(x)=\phi(xW_1+b_1)W_2+b_2
$$

where:

- $x$: one token's hidden-state vector.
- $W_1,b_1$: first learned linear layer and bias.
- $\phi$: nonlinear activation function.
- $W_2,b_2$: second learned linear layer and bias.
- $d_{\text{model}}$: input and output width.
- $d_{\text{ff}}$: intermediate feed-forward width, often larger than $d_{\text{model}}$.

Typical matrix shapes are:

$$
W_1\in\mathbb{R}^{d_{\text{model}}\times d_{\text{ff}}}
$$

$$
W_2\in\mathbb{R}^{d_{\text{ff}}\times d_{\text{model}}}
$$

The first layer expands the representation from $d_{\text{model}}$ to $d_{\text{ff}}$. The activation introduces nonlinearity. The second layer projects the intermediate representation back to $d_{\text{model}}$.

<br/>

### Flow diagram

```text
Token hidden state
   (d_model)
       |
       v
Linear projection W1
       |
       v
Expanded representation
   (d_ff)
       |
       v
Activation function φ
       |
       v
Nonlinear intermediate features
   (d_ff)
       |
       v
Linear projection W2
       |
       v
Output hidden state
   (d_model)
```

The intermediate width and activation depend on the model configuration; not every Transformer uses identical dimensions or an identical FFN design.

<br/>

## 3. Track the Tensor Shapes

For a batch of sequences, let:

$$
X:(B,T,d_{\text{model}})
$$

The FFN applies the same learned linear layers to the last dimension at every position.

| Stage | Shape |
|---|---|
| Input hidden states | $(B,T,d_{\text{model}})$ |
| First linear layer | $(B,T,d_{\text{ff}})$ |
| Activation | $(B,T,d_{\text{ff}})$ |
| Second linear layer | $(B,T,d_{\text{model}})$ |
| Output hidden states | $(B,T,d_{\text{model}})$ |

For example, if $B=2$, $T=5$, $d_{\text{model}}=8$, and $d_{\text{ff}}=32$:

```text
Input:       (2, 5, 8)
Expansion:   (2, 5, 32)
Activation:  (2, 5, 32)
Projection:  (2, 5, 8)
```

The sequence length does not change in the FFN. The intermediate feature width expands and then returns to the model width.

<br/>

## 4. Why Use an Expanded Intermediate Representation?

The expansion creates a wider feature space in which the network can apply a nonlinear transformation. The second projection then combines those intermediate features into a vector of the original hidden width.

This is not the same as adding more token positions. The FFN expands the **feature dimension**, not the sequence dimension.

The activation function matters because two linear layers without a nonlinear operation between them can be represented as a single linear transformation (ignoring certain implementation details such as separately applied constraints). A nonlinear activation allows the FFN to model richer transformations.

<br/>

## 5. GELU and Other Activation Functions

An activation function is applied element-wise to the intermediate representation.

### GELU

The Gaussian Error Linear Unit (GELU) is used in many Transformer FFNs. Informally, it smoothly scales input values rather than using a hard on/off threshold.

A common exact definition is:

$$
\operatorname{GELU}(x)=x\Phi(x)
$$

where $\Phi(x)$ is the cumulative distribution function of the standard normal distribution. Implementations may use a computationally efficient approximation.

<br/>

### ReLU

The Rectified Linear Unit is:

$$
\operatorname{ReLU}(x)=\max(0,x)
$$

It sets negative inputs to zero and leaves positive inputs unchanged.

The activation choice is an architectural decision. Do not assume every Transformer uses GELU or ReLU.

<br/>

## 6. Gated Feed-Forward Variants: SwiGLU

Some modern Transformer architectures use gated feed-forward networks rather than the simple expansion–activation–projection pattern.

A simplified SwiGLU-style expression is:

$$
\operatorname{SwiGLU}(x)
=
\left(\operatorname{Swish}(xW_{\text{gate}})
\odot xW_{\text{value}}\right)W_{\text{out}}
$$

where:

- $W_{\text{gate}}$ and $W_{\text{value}}$ are learned projections.
- $\operatorname{Swish}(z)=z\,\sigma(z)$, with $\sigma\$the sigmoid function.
- $\odot$ denotes element-wise multiplication.
- $W_{\text{out}}$ projects the gated intermediate representation back to the model width.

This formula is a simplified description; specific implementations may use different names, bias settings, and dimensions. The central idea is that one projected branch gates another branch element-wise, providing a different nonlinear transformation from a conventional single-activation FFN.

Gated FFNs often use different intermediate-width settings from conventional FFNs. Therefore, compare architectures using their actual configurations rather than assuming identical parameter counts.

<br/>

## 7. Parameter Sharing Across Positions

Within a Transformer block, the FFN's learned weights are shared across all token positions. The network does not ordinarily learn a separate $W_1$ and $W_2$ for each position.

For a sequence with positions $x_1,x_2,\ldots,x_T$:

$$
y_i=\operatorname{FFN}(x_i)
$$

The same function and parameters are used for each position $i$:

```text
x1 ----\
x2 -----\        Shared FFN parameters
x3 ------> [same learned FFN] ---> y1, y2, y3, ...
... -----/
xT ----/
```

The input vectors differ by position, so their outputs can differ even though the parameters are shared. This parameter sharing makes the FFN position-wise and allows the same learned feature transformation to be applied throughout the sequence.

<br/>

## 8. Attention vs Feed-Forward Network

Attention and the FFN transform hidden states in different ways.

| Aspect | Attention sublayer | Feed-forward network |
|---|---|---|
| Main role | Mix information across positions | Transform features at each position |
| Uses other positions' representations directly? | Yes, through attention over keys and values | No, not within the FFN operation itself |
| Core operation | Attention weights combine value vectors | Linear projections with nonlinear transformation |
| Typical sequence length effect | Can mix information between positions | Preserves the number of positions |
| Parameter sharing | Projection parameters are used across positions; attention weights depend on input | Same FFN parameters are applied at each position |

A typical Transformer block uses both: attention enables context-dependent information exchange, while the FFN transforms the resulting feature representations independently at each position. Residual connections and normalization are additional parts of the block and are covered in a separate chapter.

<br/>

## 9. A Small NumPy Example

This example illustrates a standard two-layer FFN using a simple ReLU activation. It uses toy weights and does not represent a trained model.

```python
import numpy as np

# Shape: (batch=2, sequence_length=3, d_model=4)
X = np.array([
    [[1.0, 0.0, 2.0, -1.0],
     [0.5, 1.0, 0.0,  2.0],
     [1.0, 1.0, 1.0,  1.0]],
    [[0.0, 2.0, 1.0,  0.0],
     [1.0, 0.0, 0.0,  1.0],
     [2.0, 1.0, 0.0, -1.0]]
])

d_model = 4
d_ff = 6

rng = np.random.default_rng(3)
W1 = rng.normal(size=(d_model, d_ff))
b1 = np.zeros(d_ff)
W2 = rng.normal(size=(d_ff, d_model))
b2 = np.zeros(d_model)

# The matrix multiplication operates on the last dimension.
expanded = X @ W1 + b1             # (2, 3, 6)
activated = np.maximum(expanded, 0)  # ReLU, (2, 3, 6)
output = activated @ W2 + b2       # (2, 3, 4)

print("Input:", X.shape)
print("Expanded:", expanded.shape)
print("Activated:", activated.shape)
print("Output:", output.shape)

assert expanded.shape == (2, 3, 6)
assert output.shape == X.shape
```

The example shows that the FFN changes the feature width from 4 to 6 and back to 4 while preserving batch size and sequence length.

<br/>

## 10. Common Misconceptions

1. **“The FFN mixes information between token positions.”** The position-wise FFN transforms each position separately; attention is the mechanism that directly mixes information across positions.
2. **“Expansion increases the number of tokens.”** It increases the intermediate feature width, not the sequence length.
3. **“Every token has its own FFN weights.”** The same FFN parameters are shared across positions within the block.
4. **“Every Transformer uses the same activation.”** GELU, ReLU, SwiGLU-style gated functions, and other designs may be used depending on the architecture.
5. **“Gated FFNs are identical to ordinary two-layer FFNs.”** Gated variants combine projected branches, often through element-wise gating, and may have different dimensions and parameter counts.
6. **“Attention makes the FFN unnecessary.”** They perform complementary transformations: attention mixes context across positions, while the FFN transforms features at each position.

<br/>

## 11. Practice

### Task A — Draw and label the shapes

Suppose $B=1$, $T=4$, $d_{\text{model}}=6$, and $d_{\text{ff}}=24$.

Fill in the shape at each stage:

1. Input: ____________________
2. After expansion: ____________________
3. After activation: ____________________
4. After projection back: ____________________

<br/>

### Task B — Compare the operations

Explain in two or three sentences how attention differs from the FFN in the way it uses information from sequence positions.

<br/>

### Task C — Parameter sharing

If the input sequence has 20 token positions, how many separate copies of the FFN's learned weights are normally required within one block? Explain briefly.

<br/>

## 12. Practice Answers

### Task A

1. Input: $(1,4,6)$
2. After expansion: $(1,4,24)$
3. After activation: $(1,4,24)$
4. After projection back: $(1,4,6)$

<br/>

### Task B — Example answer

Attention calculates how positions should combine information from other allowed positions and uses those weights to aggregate value vectors. The FFN then applies learned linear projections and a nonlinear transformation independently to each position, using the same parameters at every position.

<br/>

### Task C

Normally, one shared set of FFN parameters is used across all 20 positions in that Transformer block. The input vector changes by position, but the learned transformation is shared.

<br/>

## 13. Chapter Summary

- The FFN is a position-wise learned transformation applied to each token's hidden state.
- A conventional FFN expands from $d_{\text{model}}$ to $d_{\text{ff}}$, applies a nonlinear activation, and projects back to $d_{\text{model}}$.
- The FFN preserves batch size and sequence length while transforming the feature dimension.
- GELU and ReLU are common activation choices; gated variants such as SwiGLU use a different structure.
- FFN parameters are shared across token positions within a block.
- Attention mixes information across positions; the FFN transforms features at each position. Both contribute complementary computations to a Transformer block.

<br/>

**Checkpoint:** Explain how attention and feed-forward layers contribute different transformations. A strong answer should distinguish cross-position information mixing from position-wise feature transformation and mention the FFN's expansion, activation, and projection steps.
