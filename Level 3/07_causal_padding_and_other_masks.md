# Chapter 07 — Causal, Padding, and Other Masks

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain causal masks as preventing attention to future positions.
- Explain padding masks as excluding padding positions from attention.
- Compare bidirectional attention with causal attention.
- Distinguish attention masking from masked-token prediction during training.
- Understand combined masks and common encoder-decoder attention patterns.
- Draw allowed-attention grids and interpret their rows and columns.

<br/>

## 1. What Is an Attention Mask?

An attention mask controls which key positions a query position is allowed to use. It changes which entries participate in the attention calculation; it does not itself supply the content vectors.

A common additive-mask formulation is:

$$
O=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V
$$

Here, disallowed score entries in \(M\) are assigned a very large negative value, conceptually \(-\infty\). After softmax, those entries receive zero attention weight. Implementations may use equivalent boolean masks or other optimized mechanisms.

<br/>

### How to read an allowed-attention grid

In the grids below:

- **Rows** represent query positions — the position doing the attending.
- **Columns** represent key positions — the positions that may be attended to.
- `✓` means attention is allowed.
- `—` means attention is blocked.

The exact implementation convention for `True`/`False` can differ between libraries. Read the documented semantics rather than assuming that `True` always means “allowed.”

<br/>

## 2. Causal Masks

A **causal mask** prevents a position from attending to future positions. At position $i$, the model may attend to positions $j$ where $j \le i$, assuming positions are indexed from left to right.

This is important for autoregressive generation. When predicting the next token, a model must not use future target tokens that would not be available at generation time.

<br/>

### Example: four-token causal sequence

Suppose the sequence is:

`A  B  C  D`

The allowed-attention grid is:

| Query \ Key | A | B | C | D |
|---|---:|---:|---:|---:|
| A | ✓ | — | — | — |
| B | ✓ | ✓ | — | — |
| C | ✓ | ✓ | ✓ | — |
| D | ✓ | ✓ | ✓ | ✓ |

Position A can use only A. Position C can use A, B, and C, but not D. Position D can use all positions up to and including itself.

This lower-triangular pattern is typical of causal self-attention. Some implementations express the mask in terms of blocked entries, while others express allowed entries; the effect is what matters.

<br/>

## 3. Padding Masks

Batches often contain sequences of different lengths. To place them in one rectangular tensor, shorter sequences are padded to a common length. Padding tokens are structural placeholders, not meaningful input content.

A **padding mask** prevents attention from using padding positions as keys/values. Consider a sequence padded to four positions:

`A  B  PAD  PAD`

For a bidirectional attention layer, the two real tokens may attend to each other, while padded key positions are excluded:

| Query \ Key | A | B | PAD | PAD |
|---|---:|---:|---:|---:|
| A | ✓ | ✓ | — | — |
| B | ✓ | ✓ | — | — |
| PAD | ✓ | ✓ | — | — |
| PAD | ✓ | ✓ | — | — |

This grid illustrates masking of padded **key** positions. Whether the model computes outputs for padded query positions is implementation-dependent; those outputs are often ignored or excluded from downstream loss. A padding mask does not automatically mean that every padded query row must be removed from computation.

<br/>

### Why padding masks matter

- Padding should not be treated as meaningful context.
- It prevents real query positions from assigning attention weight to padded key/value positions.
- It supports batching without allowing the padding added for tensor shape to behave like real content.

<br/>

## 4. Bidirectional Attention vs Causal Attention

**Bidirectional attention** allows a position to attend to relevant real tokens on both its left and right, subject to padding or other masks. **Causal attention** blocks future positions and allows only current and earlier positions.

### Visual comparison

Bidirectional attention over four real tokens:

| Query \ Key | A | B | C | D |
|---|---:|---:|---:|---:|
| A | ✓ | ✓ | ✓ | ✓ |
| B | ✓ | ✓ | ✓ | ✓ |
| C | ✓ | ✓ | ✓ | ✓ |
| D | ✓ | ✓ | ✓ | ✓ |

Causal attention over the same four tokens:

| Query \ Key | A | B | C | D |
|---|---:|---:|---:|---:|
| A | ✓ | — | — | — |
| B | ✓ | ✓ | — | — |
| C | ✓ | ✓ | ✓ | — |
| D | ✓ | ✓ | ✓ | ✓ |

Bidirectional attention is useful when the representation of a token can use the full input context, such as in common BERT-style encoder layers. Causal attention is used when the model must preserve left-to-right prediction constraints, as in GPT-style autoregressive decoding.

These are common architecture patterns, not definitions of every possible model. An architecture may use other masks or combine multiple constraints.

<br/>

## 5. Attention Masking Is Not Masked-Token Prediction

The word *mask* appears in two related but different ideas.

### Attention masking

An **attention mask** controls information flow inside the attention calculation. It determines which query-key pairs are permitted to exchange information.

Examples:
- A causal mask blocks future positions.
- A padding mask blocks padded key positions.

<br/>

### Masked-language-model (MLM) objective

**Masked-language-model training** is a training objective in which selected input tokens are replaced or corrupted (often with a special mask token, depending on the procedure), and the model is trained to predict the original token identities.

A BERT-style model commonly uses bidirectional self-attention while learning a masked-language-model objective. Its attention mask does **not** have to block every position whose token is hidden by the MLM corruption procedure. In fact, the model usually uses surrounding left and right context to predict the masked token.

| Concept | What is masked? | Purpose |
|---|---|---|
| Causal attention mask | Future attention connections | Prevent future-token information leakage |
| Padding attention mask | Padding positions as keys/values | Exclude structural padding from context |
| MLM corruption / prediction objective | Selected input-token content | Train the model to recover original token identities |

**Checkpoint distinction:** a causal attention mask restricts which positions can be attended to. BERT's masked-language-model objective changes selected input tokens and trains the model to predict them; it is not the same operation as a causal mask.

<br/>

## 6. Combining Masks

More than one constraint can apply at once. For example, a batched causal language-model input may need both:

1. A causal restriction so a token cannot attend to future positions.
2. A padding restriction so tokens cannot attend to padded positions.

Conceptually, a key position is allowed only if it satisfies every relevant constraint. In an additive-mask implementation, blocked entries are made sufficiently negative before softmax. In a boolean-mask implementation, the constraints are combined according to the library's mask semantics.

<br/>

### Example: causal sequence with padding

Consider:

`A  B  C  PAD`

A causal constraint blocks future keys, and a padding constraint blocks the padded key. The combined grid for the real query positions is:

| Query \ Key | A | B | C | PAD |
|---|---:|---:|---:|---:|
| A | ✓ | — | — | — |
| B | ✓ | ✓ | — | — |
| C | ✓ | ✓ | ✓ | — |
| PAD | ✓* | ✓* | ✓* | — |

`✓*` illustrates a possible implementation that still computes padded query rows. Those rows are generally not meaningful outputs and may be ignored. The important requirement is that real queries do not attend to the PAD key.

In practice, attention APIs differ in mask shapes, broadcasting rules, and whether a boolean value means “keep” or “block.” Always check the relevant framework's documentation.

<br/>

## 7. Common Encoder-Decoder Attention Patterns

Encoder-decoder Transformers commonly use different attention patterns in their components.

### Encoder self-attention

In a standard bidirectional encoder, each input token can attend to other real input tokens in both directions. Padding positions are excluded where needed.

```text
Encoder input
     |
     v
Bidirectional self-attention
     |
     v
Encoder representations
```

<br/>

### Decoder causal self-attention

A standard autoregressive decoder uses causal self-attention so that each target position can use only earlier target tokens and itself.

```text
Previously available target tokens
     |
     v
Causal self-attention
     |
     v
Decoder hidden states
```

<br/>

### Encoder-decoder cross-attention

In a common encoder-decoder design, decoder hidden states provide queries, and encoder outputs provide keys and values. The decoder can use the encoded source sequence while generating output tokens. Padding in the encoder source is masked so it does not contribute as valid context.

```text
Decoder states ---> Queries Q -----------+
                                          |
Encoder outputs ---> Keys K, Values V ----+--> Cross-attention output
```

Cross-attention does not, by itself, mean “causal” or “bidirectional.” Its mask depends on the architecture and task. The usual encoder-decoder pattern allows decoder positions to access the relevant encoder input positions, while the decoder's own self-attention remains causal during autoregressive generation.

<br/>

## 8. Common Misconceptions

1. **“A causal mask hides the current token too.”** In the usual lower-triangular convention, a position can attend to itself and earlier positions; it cannot attend to later positions.
2. **“Padding tokens are ordinary words.”** Padding is structural and should not contribute as meaningful context.
3. **“Bidirectional attention means no masks are used.”** Padding masks and other constraints may still apply.
4. **“BERT uses a causal mask because it predicts masked tokens.”** Its common MLM objective is different from an attention mask; BERT-style encoder attention is generally bidirectional.
5. **“A padding mask necessarily deletes padded query rows.”** It commonly prevents attention to padded keys; treatment of padded queries depends on the implementation.
6. **“All libraries use the same boolean-mask convention.”** Mask polarity and shape conventions can differ.

<br/>

## 9. Practice

### Task A — Draw a causal grid

For the sequence `A B C`, draw a \(3\times3\) allowed-attention grid. Use `✓` for allowed and `—` for blocked.

| Query \ Key | A | B | C |
|---|---:|---:|---:|
| A | ___ | ___ | ___ |
| B | ___ | ___ | ___ |
| C | ___ | ___ | ___ |

<br/>

### Task B — Draw a padded bidirectional grid

For the sequence `A B PAD`, show bidirectional attention among real tokens while blocking the PAD key.

| Query \ Key | A | B | PAD |
|---|---:|---:|---:|
| A | ___ | ___ | ___ |
| B | ___ | ___ | ___ |
| PAD | ___ | ___ | ___ |

For the PAD query row, indicate one reasonable implementation choice and explain that the row may be ignored.

<br/>

### Task C — Explain the difference

In your own words, explain why a causal attention mask is not the same as BERT's masked-language-model objective.

<br/>

## 10. Practice Answers

### Task A — Causal grid

| Query \ Key | A | B | C |
|---|---:|---:|---:|
| A | ✓ | — | — |
| B | ✓ | ✓ | — |
| C | ✓ | ✓ | ✓ |

<br/>

### Task B — Padded bidirectional grid

One illustrative choice is:

| Query \ Key | A | B | PAD |
|---|---:|---:|---:|
| A | ✓ | ✓ | — |
| B | ✓ | ✓ | — |
| PAD | ✓* | ✓* | — |

The padded query row may be computed but ignored. The core requirement is that valid queries cannot attend to the PAD key.

<br/>

### Task C — Example answer

A causal attention mask blocks future key positions so that each position can use only itself and earlier positions. BERT's masked-language-model objective instead corrupts selected input tokens and trains the model to predict their original identities. BERT commonly uses bidirectional attention so the prediction can use context from both sides of a masked token.

<br/>

## 11. Chapter Summary

- Attention masks constrain which query-key connections are allowed.
- Causal masks block future positions; padding masks exclude padded key/value positions.
- Bidirectional attention can use left and right context, while causal attention preserves left-to-right information flow.
- Attention masking is different from masked-language-model corruption and prediction.
- Multiple constraints can be combined, and encoder-decoder architectures often use bidirectional encoder attention, causal decoder self-attention, and cross-attention to encoder outputs.
- Frameworks differ in mask shape and boolean semantics, so verify the API conventions.

<br/>

**Checkpoint:** Distinguish a causal attention mask from BERT's masked-language-model objective. Explain both the information-flow restriction of the attention mask and the token-prediction task used during MLM training.
