# Chapter 10 — Residual Connections and Layer Normalization

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain residual addition and why the tensors being added must have compatible shapes.
- Describe layer normalization and how it normalizes features for each token position.
- Compare pre-normalization and post-normalization Transformer block layouts.
- Recognize RMSNorm as a related normalization method.
- Explain how residual connections and normalization support information flow and training stability.
- Assemble attention and feed-forward sublayers into a complete Transformer block.

<br/>

## 1. Why Do Transformer Blocks Need Residual Connections and Normalization?

Transformer blocks repeatedly transform hidden-state representations using attention and feed-forward networks. Deep stacks of transformations can make optimization difficult and can alter the scale and distribution of hidden activations.

Two commonly used components help manage this:

- **Residual connections** provide a direct path for the input representation to be added to a sublayer's output.
- **Normalization** controls the scale and distribution of features according to a normalization rule.

They serve different purposes. Residual addition combines an input with a transformed version of that input, while normalization rescales and recenters features (or rescales them in variants such as RMSNorm).

<br/>

## 2. Residual Connections

A residual connection adds a sublayer's input to its output. If the input is $x$ and the sublayer transformation is $F(x)$, a simple residual expression is:

$$
y=x+F(x)
$$

Here, $F$ might be a multi-head attention sublayer or a feed-forward network. The original representation $x$ has a direct path to the result instead of being replaced entirely by $F(x)$.

<br/>

### Residual flow

```text
             +-----------------------------+
             |                             |
Input x -----+----> Sublayer F(x) ----+    |
             |                        |    |
             +------------------------+----+
                                      |
                              Residual addition
                                 y = x + F(x)
```

The diagram represents the identity skip path around the sublayer. Implementations may place normalization before or after the sublayer and addition.

<br/>

### Shape compatibility

Element-wise addition requires compatible shapes. In a typical Transformer block, the sublayer output is designed to have the same shape as its input:

$$
x:(B,T,d_{\text{model}}),\quad F(x):(B,T,d_{\text{model}})
$$

Then:

$$
y=x+F(x):(B,T,d_{\text{model}})
$$

If the dimensions do not match, a direct element-wise residual addition is not valid unless an explicit projection or another compatible transformation is introduced. Standard Transformer sublayers are usually configured to preserve the model width at the residual-addition point.

<br/>

## 3. Residual Addition Is Not Concatenation

Residual addition and concatenation are different operations.

### Addition

$$
y=x+F(x)
$$

- Combines corresponding elements by addition.
- Normally preserves the input shape.
- Does not create a wider feature dimension.

### Concatenation

$$
y=\operatorname{Concat}(x,F(x))
$$

- Places the feature vectors alongside one another.
- Usually increases the feature dimension when concatenating along the feature axis.
- Requires subsequent layers to handle the wider representation if the model width must be restored.

For example, if both $x$ and $F(x)$ have shape $(B,T,8)$, addition produces $(B,T,8)$, while concatenation along the final axis produces $(B,T,16)$

A residual connection preserves a direct additive contribution from the original input. Concatenation preserves both vectors as separate feature sections and changes the shape.

<br/>

## 4. Layer Normalization

Layer normalization (LayerNorm) normalizes features within each token's hidden-state vector. For a hidden vector $x$ with $d$ features, it calculates the mean and variance over those features:

$$
\mu=\frac{1}{d}\sum_{i=1}^{d}x_i
$$

$$
\sigma^2=\frac{1}{d}\sum_{i=1}^{d}(x_i-\mu)^2
$$

It then normalizes each feature and applies learned scale and shift parameters:

$$
\operatorname{LayerNorm}(x)_i
=
\gamma_i\frac{x_i-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta_i
$$

where:

- $\mu$: mean across the normalized features for that token.
- $\sigma^2$: variance across those features.
- $\epsilon$: small constant for numerical stability.
- $\gamma_i$: learned scale parameter.
- $\beta_i$: learned shift parameter.

In the usual Transformer use, the normalization is performed over the hidden-feature dimension for each token independently. It does not calculate one mean across all tokens in the sequence.

<br/>

### Shape behavior

For input $X:(B,T,d_{\text{model}})$, LayerNorm typically returns the same shape:

$$
\operatorname{LayerNorm}(X):(B,T,d_{\text{model}})
$$

It changes feature values, not batch size, sequence length, or hidden width.

<br/>

## 5. Pre-Norm and Post-Norm Layouts

Transformer blocks can differ in where LayerNorm is placed relative to the sublayer and residual addition.

### Post-normalization (Post-LN)

A simplified post-norm layout applies the sublayer to $x$, adds the residual, then normalizes:

$$
y=\operatorname{LayerNorm}(x+F(x))
$$

```text
Input x --------------------------+
   |                              |
   v                              |
 Sublayer F(x)                    |
   |                              |
   +----------> Add <-------------+
                  |
                  v
              LayerNorm
                  |
                  v
                Output
```

<br/>

### Pre-normalization (Pre-LN)

A simplified pre-norm layout normalizes the input before the sublayer, then adds the sublayer result to the residual path:

$$
y=x+F(\operatorname{LayerNorm}(x))
$$

```text
Input x --------------------------+
   |                              |
   v                              |
 LayerNorm                        |
   |                              |
   v                              |
 Sublayer F                       |
   |                              |
   +----------> Add <-------------+
                  |
                  v
                Output
```

These formulas illustrate the placement distinction for one sublayer. Real blocks commonly contain both an attention sublayer and an FFN sublayer, each with its own residual path and normalization placement. Some models also apply a final normalization after the stack.

<br/>

### Conceptual comparison

- **Post-LN:** normalization follows the residual addition.
- **Pre-LN:** normalization is applied before the sublayer transformation, while the residual path carries the unnormalized input to the addition.
- Pre-LN designs are often used to make optimization of deep Transformer stacks easier, though stability and performance depend on the full architecture, initialization, optimizer, and training setup.

Do not assume all Transformer implementations use the same normalization layout.

<br/>

## 6. RMSNorm: A Related Variant

Root Mean Square Layer Normalization (RMSNorm) is a related normalization method. In its common form, it scales a hidden vector using its root-mean-square magnitude and a learned scale parameter. Unlike standard LayerNorm, RMSNorm does not subtract the feature mean and typically does not use a learned bias.

A simplified expression is:

$$
\operatorname{RMSNorm}(x)_i
=
\gamma_i\frac{x_i}{\sqrt{\frac{1}{d}\sum_{j=1}^{d}x_j^2+\epsilon}}
$$

where $\gamma_i$ is a learned scale parameter.

This is a simplified formula; exact implementation details can vary. RMSNorm preserves the hidden-state shape, like LayerNorm. It is used in some modern Transformer architectures as an alternative normalization design.

| Property                  | LayerNorm                         | RMSNorm                       |
| ------------------------- | --------------------------------- | ----------------------------- |
| Subtracts feature mean    | Yes                               | No, in the common form        |
| Uses variance / RMS scale | Centers and scales using variance | Scales using root mean square |
| Learned scale             | Commonly yes                      | Commonly yes                  |
| Learned shift/bias        | Commonly yes                      | Commonly omitted              |
| Output shape              | Same as input                     | Same as input                 |

<br/>

## 7. Assemble a Transformer Block

A standard Transformer block typically includes an attention sublayer and a feed-forward sublayer. Each is commonly paired with a residual connection and normalization.

The exact order depends on whether the architecture uses pre-norm or post-norm.

### Simplified pre-norm block

$$
x' = x+\operatorname{Attention}(\operatorname{Norm}(x))
$$

$$
y = x'+\operatorname{FFN}(\operatorname{Norm}(x'))
$$

```text
                 +-------------------------------------+
                 |                                     |
Input x ----------+--> Norm --> Multi-Head Attention ---+--> Add --> x'
                                                               |
                 +---------------------------------------------+
                 |
                 +--> Norm --> Feed-Forward Network -----------+--> Add --> Output y
                                                               |
                 +---------------------------------------------+
```

The diagram emphasizes the residual paths. It is a conceptual view; implementations can differ in dropout placement, normalization choice, and other details.

<br/>

### Simplified post-norm block

$$
x'=\operatorname{Norm}(x+\operatorname{Attention}(x))
$$

$$
y=\operatorname{Norm}(x'+\operatorname{FFN}(x'))
$$

In both cases, attention mixes information across positions, the FFN transforms features at each position, residual connections add the incoming representation, and normalization follows the chosen layout.

<br/>

## 8. Information Flow and Training Stability

Residual connections create a direct path for the incoming hidden state to reach the output of a sublayer. The model can learn a transformation that modifies the representation while retaining an additive contribution from the input.

Normalization helps control activation scales and distributions, which can support optimization in deep networks. Pre-norm layouts are often selected for deep Transformer stacks because the residual path can remain direct across sublayers.

These components help with information flow and training behavior, but they do not guarantee stable training by themselves. Architecture depth, initialization, learning rate, precision, data, and optimizer settings also matter.

<br/>

## 9. Small NumPy Demonstration

This toy example illustrates shape-preserving residual addition and per-token feature normalization. It is for learning purposes, not a replacement for a framework's optimized LayerNorm implementation.

```python
import numpy as np

# Two sequences, three token positions, four features per token.
X = np.array([
    [[1.0, 2.0, 3.0, 4.0],
     [2.0, 0.0, 1.0, 3.0],
     [0.0, 1.0, 0.0, 1.0]],
    [[3.0, 2.0, 1.0, 0.0],
     [1.0, 1.0, 1.0, 1.0],
     [4.0, 1.0, 2.0, 3.0]]
])

# Pretend this is the output of a sublayer with compatible shape.
F_X = 0.1 * X

# Residual addition: shape remains unchanged.
residual = X + F_X

# LayerNorm over the final (feature) dimension, independently per token.
eps = 1e-5
mean = residual.mean(axis=-1, keepdims=True)
var = residual.var(axis=-1, keepdims=True)
normalized = (residual - mean) / np.sqrt(var + eps)

# Illustrative learned affine parameters (scale=1, shift=0).
gamma = np.ones((X.shape[-1],))
beta = np.zeros((X.shape[-1],))
layer_norm_output = normalized * gamma + beta

print("Input shape:", X.shape)
print("Residual shape:", residual.shape)
print("LayerNorm output shape:", layer_norm_output.shape)

assert residual.shape == X.shape
assert layer_norm_output.shape == X.shape
```

The example normalizes over the last axis, so each token's feature vector is normalized independently. It uses scale and shift values of one and zero only to keep the example simple.

## 10. Common Misconceptions

1. **“A residual connection concatenates the input and output.”** Standard residual addition adds corresponding elements and usually preserves shape.
2. **“LayerNorm normalizes across all tokens in a sequence.”** In typical Transformer use, it normalizes the feature dimension independently for each token.
3. **“Pre-LN and Post-LN are identical.”** They differ in the placement of normalization relative to the sublayer and residual addition.
4. **“RMSNorm subtracts the mean like LayerNorm.”** The common RMSNorm form scales by root mean square without mean subtraction.
5. **“Residuals and normalization are interchangeable.”** Residuals provide an additive information path; normalization rescales feature values.
6. **“Pre-LN guarantees stable training.”** It can support optimization, but stability depends on the complete training setup.

<br/>

## 11. Practice

### Task A — Annotate the block

For a pre-norm block, label the following components in order:

- Input hidden states
- LayerNorm
- Multi-head attention
- Residual addition
- LayerNorm
- Feed-forward network
- Residual addition
- Output hidden states

Draw the skip path around each sublayer and indicate which tensors are added.

<br/>

### Task B — Addition vs concatenation

Suppose $x$ and $F(x)$ both have shape $(2,5,8)$.

1. What is the shape after residual addition?
2. What is the shape after concatenation along the feature dimension?
3. Why does the usual Transformer residual path use addition rather than feature concatenation?

<br/>

### Task C — LayerNorm vs RMSNorm

State one key difference between LayerNorm and RMSNorm and explain what dimension is normalized in the usual Transformer setting.

## 12. Practice Answers

### Task B

1. Residual addition: \((2,5,8)\)
2. Feature concatenation: \((2,5,16)\)
3. Addition preserves the model width and supplies a direct additive path for the incoming representation. Concatenation doubles the feature width in this example and would require downstream layers to handle that wider representation.

<br/>

### Task C — Example answer

LayerNorm commonly subtracts the feature mean and scales by the feature variance, while RMSNorm commonly scales by root mean square without subtracting the mean. In a typical Transformer, normalization is applied over the hidden-feature dimension separately for each token position.

<br/>

## 13. Chapter Summary

- Residual connections add a sublayer's input to its output and require compatible shapes.
- Residual addition usually preserves the model width; concatenation usually increases the feature dimension.
- LayerNorm normalizes features within each token's hidden-state vector and usually preserves shape.
- Pre-LN normalizes before the sublayer; Post-LN normalizes after residual addition.
- RMSNorm is a related variant that commonly uses root-mean-square scaling without mean subtraction.
- Attention and FFN sublayers are commonly assembled with residual paths and normalization into a Transformer block.
- Residual connections support information flow, while normalization can support training stability; neither alone guarantees successful optimization.

<br/>

**Checkpoint:** Explain why adding a residual connection differs from concatenating outputs. Mention element-wise addition, shape compatibility, and the preservation of the hidden-state width.
