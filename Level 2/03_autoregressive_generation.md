# Chapter 03 — Autoregressive Generation

## 1. Learning Objectives and Prerequisites

By the end of this chapter, you should be able to:

- Explain next-element prediction conditioned on previous elements.
- Describe sequence probability factorization conceptually.
- Trace text generation from an initial context through successive tokens.
- Distinguish training on known sequences from sequential generation at inference time.
- Explain the roles of sampling and stopping conditions.
- Identify sequential latency, error accumulation, and conditioning limits.
- Recognize autoregressive generation in modalities beyond text.

**Prerequisites:** Understand the difference between training and inference, and the basic idea of tokens as units of text processed by a language model. A detailed understanding of transformer layers or decoding algorithms is not required here.

<br/>

## 2. Intuition: Predict One Element at a Time

An autoregressive model generates a sequence by predicting the next element using the elements that came before it.

For text, the elements are often tokens. A token may be a whole word, part of a word, punctuation, or another unit defined by the tokenizer.

Suppose the prompt is:

> The sun rises in the

The model estimates what token could come next. It might select `east`. The updated context becomes:

> The sun rises in the east

The model then predicts another token using this longer context. It might produce a period and stop, or continue with more text.

The central idea is that **each new element is conditioned on the preceding context**. The model does not normally generate the entire sequence independently in one step.

<br/>

### A simple analogy

Imagine writing a sentence one word at a time. At each step, you consider what you have already written and choose a plausible continuation. An autoregressive model follows a similar sequence-based process, except that it uses learned statistical patterns rather than human reasoning.


<br/>


## 3. Sequence Probability Factorization

A sequence contains multiple elements, and an autoregressive model represents its probability through a chain of conditional probabilities.

For a sequence of tokens $x_1, x_2, \ldots, x_T$:

$$
P(x_1, x_2, \ldots, x_T)
= \prod_{t=1}^{T} P(x_t \mid x_1, \ldots, x_{t-1})
$$

In plain language:

- Estimate the probability of the first token.
- Estimate the second token given the first.
- Estimate the third token given the first two.
- Continue until the sequence is complete.
- Multiply these conditional probabilities to express the probability of the complete sequence.

For the first token, there is no preceding token in the sequence, so the model uses an initial or otherwise supplied context.

<br/>

### Why this matters

The factorization provides a way to model a joint sequence probability through a series of next-element predictions. It does **not** mean that the elements are independent. Each conditional distribution can depend on the preceding elements.

For example, the likely next token after `peanut butter and` differs from the likely next token after `salt and`. The preceding context changes the distribution over possible continuations.

This equation describes the sequence model conceptually. You do not need to calculate the product by hand to understand generation.


<br/>


## 4. Tracing Text Generation Step by Step

Consider the prompt:

> A small bird sat on the

The following is an illustrative trace, not a claim that every model will produce these exact tokens.

| Step | Context available to the model | Illustrative next token | Updated sequence |
|---|---|---|---|
| 1 | `A small bird sat on the` | `branch` | `A small bird sat on the branch` |
| 2 | `A small bird sat on the branch` | `.` | `A small bird sat on the branch.` |
| 3 | Complete sentence and stop condition | — | Generation ends |

At each generation step, the model uses the current context to produce a distribution over possible next tokens. A selection rule chooses one token from that distribution. The selected token is appended to the sequence, making it part of the context for the next step.

<br/>

### Conceptual flow

```text
Initial prompt
     |
     v
Predict next-token distribution
     |
     v
Select one token
     |
     v
Append token to context
     |
     +------> Stop condition met? -- Yes --> Return generated sequence
     |
     No
     |
     +------> Predict the next token using the updated context
```

The process repeats until a stopping condition is reached.

<br/>

### Important distinction

The model predicts a distribution over possible next tokens; the final token depends on the selection method. The most probable token is not necessarily selected on every run.


<br/>


## 5. Training Flow vs. Inference Flow

Autoregressive models use the same basic next-element relationship during training and generation, but the way the sequence is supplied differs.

### Training on known sequences

During training, the sequence is already available. The model is trained to predict each target token from the preceding context.

For example, given the known sequence:

> Birds can fly

Training examples conceptually include:

| Context | Target to predict |
|---|---|
| Beginning of sequence | `Birds` |
| `Birds` | `can` |
| `Birds can` | `fly` |

Real training pipelines may process many positions and sequences in parallel. Therefore, the conceptual next-token objective does **not** imply that training must run one token at a time in a slow loop.

The model's predictions are compared with the known target tokens, and the training objective adjusts the model's parameters to improve those predictions.

<br/>

### Inference: generating a new sequence

During generation, the next target token is not already known. The model predicts a distribution, a selection rule chooses a token, and that generated token is added to the context. The process repeats.

| Aspect | Training | Inference / generation |
|---|---|---|
| Sequence | Known training examples | Prompt plus tokens generated so far |
| Target token | Available from the training sequence | Not known in advance |
| Main operation | Learn to predict the next token | Predict and select the next token repeatedly |
| Context | Preceding tokens from the known sequence | Prompt and previously generated tokens |
| Main purpose | Adjust model parameters | Produce a continuation |

**Key takeaway:** Training teaches the model how to predict next elements. Inference uses those predictions to construct a sequence.


<br/>


## 6. Sampling and Stopping Conditions

### 6.1 Selecting a token

At each step, the model assigns scores or probabilities to possible next tokens. A generation procedure then selects a token.

Common high-level choices include:

- **Greedy selection:** choose the highest-probability next token.
- **Sampling:** select a token probabilistically from the model's distribution.

Sampling can produce different continuations from the same prompt. The result depends on the distribution and the sampling settings. Detailed decoding methods and their mathematical behavior can be studied separately.

Generation is not guaranteed to be factually correct just because the model assigns a high probability to a continuation.

<br/>

### 6.2 Stopping generation

A model needs a rule for deciding when to stop. Common stopping conditions include:

- The model emits a designated end-of-sequence token.
- A configured maximum number of new tokens is reached.
- An application-specific stop sequence is detected.
- An external application rule ends the generation.

A maximum-token limit is a safeguard, not a guarantee that the answer is complete. Conversely, a model may emit an end-of-sequence token before reaching the maximum.


<br/>


## 7. Strengths, Limitations, and Common Misconceptions

### Strengths

- **Flexible continuation:** can continue a prompt in a context-sensitive way.
- **Sequence modeling:** represents dependencies between earlier and later elements.
- **Broad applicability:** the sequence elements need not be ordinary text tokens.
- **Incremental output:** an application can display generated tokens as they arrive, rather than waiting for the entire response.

<br/>

### Limitations

**Sequential generation latency:** In a conventional autoregressive decoding loop, the next token depends on the tokens already generated. The model therefore usually performs repeated generation steps. Long outputs can take time, although systems may optimize inference and process multiple requests efficiently.

**Error accumulation:** An incorrect, irrelevant, or unhelpful generated token becomes part of the context. Later predictions may continue from that token, causing the initial problem to influence the rest of the sequence.

**Conditioning limits:** The model can only condition on the context available to it. Context-window limits, truncation, and the model's learned behavior can prevent relevant earlier information from influencing a later prediction.

**Probabilistic uncertainty:** Multiple continuations may be plausible. A fluent continuation is not necessarily true, safe, or appropriate.

<br/>

### Common misconceptions

- **Misconception:** “The model generates the whole response independently in one step.”  
  **Correction:** In autoregressive generation, tokens are selected successively, with each new token conditioned on the available preceding context.

- **Misconception:** “Autoregressive training must be sequential token by token.”  
  **Correction:** The prediction objective is autoregressive, but training implementations can compute predictions for many positions in parallel.

- **Misconception:** “The next token is always the most probable token.”  
  **Correction:** Greedy selection does this, but sampling-based methods may choose another token.

- **Misconception:** “Autoregression is the same thing as a transformer.”  
  **Correction:** Autoregression describes a sequence factorization/generation approach. A transformer is a neural-network architecture that can implement autoregressive generation, but the terms are not interchangeable.

- **Misconception:** “Autoregressive models only generate text.”  
  **Correction:** They can model sequences of other elements, including audio tokens, image patches or codes, and other learned representations.


<br/>


## 8. Autoregression Beyond Text

The sequence elements depend on the representation used by a system. Autoregressive modeling can apply wherever data is represented as an ordered sequence.

| Domain | Possible sequence elements | What is generated |
|---|---|---|
| Text | Text tokens | A sentence, answer, or document |
| Audio | Audio tokens or learned acoustic units | Speech or other audio |
| Images | Image tokens, patches, or discrete codes | An image representation that can be decoded into an image |
| Video | Ordered frame or video tokens | A sequence of video content |
| Structured data | Symbols or fields in a defined order | A structured sequence, subject to the model and output format |

These are examples of possible designs, not a claim that every image, audio, or video model is autoregressive. Other generation approaches—such as diffusion—use different generation procedures.


<br/>


## 9. Practice: Trace a Short Generation

Suppose the prompt is:

> Machine learning helps computers

For this exercise, imagine the model selects the following tokens in order:

1. `identify`
2. `patterns`
3. `.`

Complete the trace:

| Step | Context before prediction | Selected token | Context after selection |
|---|---|---|---|
| 1 | `Machine learning helps computers` | `identify` | `Machine learning helps computers identify` |
| 2 | `Machine learning helps computers identify` | `patterns` | `Machine learning helps computers identify patterns` |
| 3 | `Machine learning helps computers identify patterns` | `.` | `Machine learning helps computers identify patterns.` |

<br/>

### Questions

1. Why does the context change after each selected token?
2. What information is available when predicting `patterns`?
3. If the model selects a poor token at step 1, how could that affect step 2?
4. During training, is the target token already known?
5. Name one stopping condition that could end generation.
6. Does the autoregressive approach require the sequence elements to be words?

<br/>

### Suggested answers

1. The selected token is appended to the sequence and becomes part of the context for the next prediction.
2. The original prompt plus the generated token `identify`.
3. The poor token becomes part of the context and may steer later predictions toward an unsuitable continuation.
4. Yes. The training sequence supplies the target token for each position.
5. An end-of-sequence token, a maximum-token limit, or an application-specific stop sequence.
6. No. The elements can be audio tokens, image codes, or other ordered representations.


<br/>


## 10. Revision Questions

**1. What is autoregressive generation?**  
A process in which a sequence is generated by predicting each next element conditioned on the preceding context.

**2. What does sequence probability factorization express?**  
It expresses the probability of a sequence as a product of conditional probabilities for its elements, each conditioned on preceding elements.

**3. What is the key difference between training and inference?**  
During training, the target tokens are available in known sequences. During inference, the model must generate and append each next token before predicting subsequent tokens.

**4. Why can autoregressive generation have latency?**  
Each next token generally depends on the tokens generated earlier, so generation requires repeated dependent steps.

**5. What is error accumulation?**  
A generated mistake becomes part of the subsequent context and can influence later predictions.

**6. How is autoregression different from a transformer?**  
Autoregression describes how sequence probabilities are factorized and elements are generated; a transformer is an architecture that may be used to implement that process.


<br/>


## 11. Summary and Checkpoint

### Summary

- Autoregressive generation predicts one sequence element at a time using preceding context.
- Sequence probability can be expressed as a product of conditional probabilities.
- During training, known sequences provide the target elements; during inference, selected predictions are appended and used as context.
- Sampling determines how a next element is selected from possible continuations.
- Generation ends when a stopping condition is met.
- Sequential dependence can introduce latency, while early mistakes and limited context can affect later output.
- Autoregression applies to sequences beyond text and is not synonymous with transformer architecture.

<br/>

### Checkpoint

**Explain why later generated elements depend on the earlier sequence.**

A strong answer should mention that the model conditions each next-element distribution on the preceding context. Once an element is selected, it is appended to that context and can change the probabilities of later elements. Consequently, an early selection can influence the continuation, and a mistake can propagate.

<br/>


## 12. References and Optional Extensions

- [Language Models are Few-Shot Learners (GPT-3)](https://arxiv.org/abs/2005.14165) — an example of large-scale autoregressive language modeling.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — introduces the Transformer architecture; useful for understanding one architecture commonly used for autoregressive language models.
- [Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — an example of sequence generation in neural machine translation.

**Optional extension:** Later, study how tokenization, context windows, attention, and decoding strategies affect autoregressive generation. These topics are useful but are not required to understand the core process in this chapter.

**Next chapter:** `04_transformer_based_generation.md`
