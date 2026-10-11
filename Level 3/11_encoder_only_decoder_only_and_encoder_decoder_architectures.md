# Chapter 11 — Encoder-Only, Decoder-Only, and Encoder-Decoder Architectures

## Learning Objectives

- Trace bidirectional encoder processing and common task heads.
- Trace causal decoder processing and next-token output.
- Trace encoder-decoder processing, including decoder cross-attention to encoder outputs.
- Compare attention access patterns and input/output flows.
- Distinguish training with known target tokens from autoregressive generation using previous outputs.
- Map architecture families to representation, classification, generation, and sequence-transformation tasks.

<br/>

## 1. Three Common Transformer Architecture Families

Transformer models are often grouped into three broad architecture families:

1. **Encoder-only:** builds contextual representations of an input sequence, commonly using bidirectional self-attention.
2. **Decoder-only:** processes a sequence with causal self-attention and commonly predicts the next token.
3. **Encoder-decoder:** encodes a source sequence, then uses a decoder to produce an output sequence, commonly through causal self-attention and cross-attention to encoder outputs.

These are high-level patterns. Specific models can vary in masks, training objectives, task heads, and implementation details.

<br/>

## 2. Encoder-Only Architecture

### 2.1 Processing flow

An encoder-only model converts input tokens into contextual hidden-state representations. In a common BERT-style encoder, self-attention is bidirectional: each real token can use context from tokens on both its left and right, subject to padding or other masks.

```text
Input text
    |
    v
Tokenizer -> Token IDs
    |
    v
Token + position information
    |
    v
Encoder block(s)
  - Bidirectional self-attention
  - Feed-forward network
  - Residual connections and normalization
    |
    v
Contextual hidden states
    |
    +------> Token-level head (e.g., tagging)
    |
    +------> Sequence-level head (e.g., classification)
    |
    +------> Masked-token prediction head (for MLM-style training)
```

The encoder's output is contextual: a token's vector can incorporate information from other input positions through self-attention and subsequent layers.

<br/>

### 2.2 Common task heads

- **Sequence classification:** predicts a label for the entire input, such as sentiment or topic.
- **Token classification:** predicts a label for each token, such as named-entity tags.
- **Extractive question answering:** predicts answer start and end positions in a supplied passage.
- **Masked-language-model prediction:** predicts selected corrupted or masked token identities during training.

A task head is an additional output component; the encoder architecture itself is not identical to every task head.

<br/>

### 2.3 Typical use cases

Encoder-only models are useful when the goal is to understand, classify, label, or represent an input rather than generate a long output token by token.

Examples include text classification, token labeling, embedding and representation learning, retrieval features, and extractive question answering. These are common applications, not strict limitations.

<br/>

## 3. Decoder-Only Architecture

### 3.1 Processing flow

A decoder-only model commonly uses causal self-attention. Each position can attend to itself and earlier positions but not future positions. The hidden state at a position is used to predict a next-token distribution.

```text
Prompt / available tokens
          |
          v
Tokenizer -> Token IDs
          |
          v
Token + position information
          |
          v
Decoder block(s)
  - Causal self-attention
  - Feed-forward network
  - Residual connections and normalization
          |
          v
Final hidden states
          |
          v
Language-model output projection
          |
          v
Next-token logits / probabilities
          |
          v
Select or sample next token
          |
          +---- append token and continue generation
```

The output projection maps the final hidden representation to vocabulary-sized logits. Softmax can convert logits to probabilities, and a decoding strategy chooses or samples the next token.

<br/>

### 3.2 Next-token prediction

For a token sequence $x_1,x_2,\ldots,x_T$, a causal language model learns to predict a next token from preceding context. Conceptually, it models:

$$
P(x_{t+1}\mid x_1,\ldots,x_t)
$$

Causal masking ensures that a position's representation does not use future target tokens. This lets the model generate one token at a time from a prompt.

<br/>

### 3.3 Typical use cases

Decoder-only models are commonly used for text and code generation, conversational assistants, continuation, completion, and instruction following when trained and configured for it. Decoder-only describes a common architecture and attention pattern; training data and task setup influence behavior.

<br/>

## 4. Encoder-Decoder Architecture

### 4.1 Processing flow

An encoder-decoder model contains an encoder that builds representations of a source sequence and a decoder that produces an output sequence. In a common design, the decoder uses causal self-attention and cross-attention to encoder outputs.

```text
Source input
    |
    v
Tokenizer / embeddings
    |
    v
Encoder block(s)
  - Usually bidirectional self-attention
    |
    v
Encoder output states ----------------------+
                                            |
Target prefix / previous target tokens      |
    |                                       |
    v                                       |
Decoder embeddings                          |
    |                                       |
    v                                       |
Decoder block(s)                            |
  - Causal self-attention                   |
  - Cross-attention to encoder states <-----+
  - Feed-forward network
    |
    v
Output projection
    |
    v
Next-token distribution
    |
    v
Generated target sequence
```

<br/>

### 4.2 What cross-attention does

In typical encoder-decoder cross-attention:

- **Queries (Q)** come from decoder hidden states.
- **Keys (K)** and **values (V)** come from encoder output states.

This lets the decoder use information from the encoded source while building the output. The decoder's causal self-attention separately controls how it uses the target-side prefix.

<br/>

### 4.3 Typical use cases

Encoder-decoder models are commonly used for machine translation, summarization, text transformation and rewriting, input-conditioned generation, and some question-answering or speech/text transformation pipelines. They are useful when source input and target output have distinct sequence roles.

<br/>

## 5. Compare the Attention Patterns

| Property | Encoder-only | Decoder-only | Encoder-decoder |
|---|---|---|---|
| Main input flow | One input sequence | Prompt / token prefix | Source sequence plus target prefix |
| Common encoder-side attention | Bidirectional self-attention | Not a separate encoder | Usually bidirectional self-attention |
| Common decoder-side self-attention | Not a separate decoder | Causal self-attention | Causal self-attention |
| Cross-attention to a separate encoder | Usually absent in basic design | Usually absent in basic design | Present in standard design |
| Common output | Contextual hidden states and task-head outputs | Next-token logits | Next-token logits for target sequence |
| Common task style | Representation and understanding | Autoregressive generation | Source-conditioned sequence generation |

These are common patterns, not universal rules. Models may introduce other masks, extra components, or hybrid designs.

<br/>

## 6. Training With Known Targets vs Generation

A crucial distinction is between training and inference.

### 6.1 Training with known target tokens

During standard teacher-forced training for an autoregressive model, the correct target sequence is available. The model receives a shifted target prefix and learns to predict the next target token at each position.

For a target sequence:

`<BOS> The cat sat <EOS>`

the model may receive:

`<BOS> The cat sat`

and learn targets:

`The cat sat <EOS>`

The causal mask prevents each position from using target tokens to its right. The model can compute predictions for many target positions in parallel during training because the correct shifted target tokens are already known.

For encoder-decoder training, the encoder processes the source input, while the decoder receives the shifted target sequence and uses cross-attention to the encoder outputs.

<br/>

### 6.2 Autoregressive generation

During generation, future target tokens are not known. The model begins with a prompt or target prefix, predicts the next token, appends the selected token, and repeats.

```text
Current prefix
     |
     v
Model predicts next-token distribution
     |
     v
Select / sample a token
     |
     v
Append token to prefix
     |
     +----> Repeat until stopping condition
```

The next step depends on the token selected. This is why ordinary autoregressive generation proceeds step by step, even though training predictions can often be computed in parallel across known target positions.

<br/>

### 6.3 Encoder-only objectives differ

Encoder-only models are not generally trained as standard left-to-right next-token predictors. A BERT-style model commonly uses a masked-language-model objective: selected input tokens are corrupted and the model learns to predict their original identities using bidirectional context. Other encoder objectives and task heads are possible.

<br/>

## 7. Architecture Selection by Task

| Task | Common starting point | Why it fits |
|---|---|---|
| Sentiment or topic classification | Encoder-only | Contextual representations feed a sequence-classification head |
| Token labeling / entity recognition | Encoder-only | Produces contextual representations at each token |
| Text or code continuation | Decoder-only | Next-token prediction supports autoregressive generation |
| Conversational text generation | Decoder-only is common | Generates responses token by token from a prompt |
| Machine translation | Encoder-decoder is common | Encodes source and generates a separate target sequence |
| Summarization | Encoder-decoder or decoder-only | Can be framed as source-to-target transformation or prompt-conditioned generation |
| Text embeddings / retrieval representations | Encoder-based or other embedding model | Learns representations intended for similarity or retrieval |
| Masked-token prediction | Encoder-only is common in BERT-style setups | Predicts selected corrupted tokens using surrounding context |

These are starting points, not absolute rules. Task formulation, latency, model availability, data, and quality requirements also influence the choice.

<br/>

## 8. Common Misconceptions

1. **“Every Transformer decoder has cross-attention.”** A decoder-only language model commonly has causal self-attention without a separate encoder or encoder-decoder cross-attention.
2. **“Encoder-only models cannot produce predictions.”** They produce outputs through task heads, including classification, token labeling, and masked-token prediction.
3. **“Decoder-only models can see future tokens during generation.”** Causal attention prevents future-token information from entering a position's representation.
4. **“Encoder-decoder and decoder-only models generate in the same way internally.”** Both may generate autoregressively, but the encoder-decoder decoder also uses cross-attention to encoded source states.
5. **“Training and generation use exactly the same available information.”** Training often has known shifted targets; generation must use previously available tokens and the model's own selected outputs.
6. **“One architecture is always best for every task.”** Choice depends on input/output structure and practical constraints.

<br/>

## 9. Practice

### Task A — Draw the three architectures

Draw a separate diagram for each architecture and label the applicable components:

1. **Encoder-only:** bidirectional self-attention, encoder outputs, task head.
2. **Decoder-only:** causal self-attention, output projection, next-token prediction.
3. **Encoder-decoder:** encoder self-attention, decoder causal self-attention, cross-attention, output projection.

Indicate which sequence supplies Q, K, and V for encoder-decoder cross-attention.

<br/>

### Task B — Match architecture to task

Choose a common starting point for each task and explain why:

- Classify a review as positive or negative.
- Continue a code snippet.
- Translate a source sentence into another language.
- Predict a masked word using context from both sides.

<br/>

### Task C — Explain training and generation

Why can an autoregressive model compute predictions for many target positions in parallel during teacher-forced training, but usually generates the target sequence one token at a time during inference?

<br/>

## 10. Practice Answers

### Task B — Example answers

- **Review classification:** encoder-only is a common starting point because its contextual representation can feed a sequence-classification head.
- **Code continuation:** decoder-only is a common starting point because causal next-token prediction supports token-by-token continuation.
- **Translation:** encoder-decoder is a common starting point because the encoder represents the source and the decoder generates a separate target sequence.
- **Masked-word prediction with both-side context:** an encoder-only, BERT-style setup is a common starting point because bidirectional attention can use context on both sides of the selected token.

<br/>

### Task C — Example answer

During teacher-forced training, the correct shifted target tokens are already available, so the model can calculate predictions at multiple positions in one forward pass while the causal mask prevents future-token leakage. During generation, the next target token is not known in advance; the model must select or sample a token, append it to the prefix, and then predict the following token.

<br/>

## 11. Chapter Summary

- Encoder-only architectures commonly use bidirectional self-attention to create contextual representations for task heads.
- Decoder-only architectures commonly use causal self-attention and a vocabulary projection for next-token prediction.
- Encoder-decoder architectures encode a source sequence and use a decoder with causal self-attention and cross-attention to encoder outputs.
- In standard encoder-decoder cross-attention, Q comes from decoder states while K and V come from encoder states.
- Teacher-forced training uses known shifted target tokens; autoregressive inference generates tokens incrementally.
- Architecture choice depends on whether the task is primarily representation/classification, continuation/generation, or source-to-target sequence transformation.

<br/>

**Checkpoint:** Explain how the decoder in an encoder-decoder model differs from a decoder-only model. A strong answer should mention that both commonly use causal self-attention, but the encoder-decoder decoder additionally uses cross-attention to the encoder's source representations.
