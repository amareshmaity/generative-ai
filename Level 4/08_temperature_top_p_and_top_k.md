# 08. Temperature, Top-p, and Top-k

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain how temperature changes the relative sharpness of a next-token probability distribution before sampling.
- Distinguish top-k filtering by candidate rank from top-p filtering by cumulative probability.
- Calculate candidate sets for a small illustrative distribution.
- Explain why parameter order, defaults, and provider-specific implementations matter.
- Recognize that temperature does not directly control truthfulness and that low temperature does not guarantee reproducible output.
- Design a small, controlled experiment comparing supported decoding settings across multiple runs.

<br/>

## 1. Why These Settings Matter

A language model produces scores (logits) for possible next tokens. A decoding pipeline may transform those scores, filter the candidates, and then select a token. Temperature, top-k, and top-p affect this process in different ways.

- **Temperature** changes the relative sharpness of the distribution.
- **Top-k** restricts the eligible candidates to a fixed number of highest-ranked tokens.
- **Top-p** restricts the eligible candidates according to cumulative probability mass.

These settings usually affect how the next token is selected during inference. They do not retrain the model or directly change its learned weights.

<br/>

## 2. Temperature

Temperature rescales logits before a probability distribution is calculated. A common formulation is:

$$
P_i = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)}
$$

where $z_i$ is the logit for candidate $i$, and $T$ is the temperature.

- **Lower temperature** (positive and below the default scale, commonly `1`) generally sharpens the distribution: higher-ranked candidates receive more probability relative to lower-ranked ones.
- **Higher temperature** generally flattens the distribution: lower-ranked candidates receive more probability relative to the highest-ranked candidates.
- **Temperature near 1** leaves logits at their original scale in this formulation.

Temperature does not normally change the ordering of candidates when it is positive; it changes the relative probabilities. The exact valid range, edge-case handling, and defaults are implementation-dependent.

<br/>

### Example

Suppose two tokens have logits $z_A=2$ and $z_B=1$.

- At $T=1$, the logit gap is unchanged.
- At $T=0.5$, the scaled logits are $4$ and $2$, increasing the relative advantage of `A`.
- At $T=2$, the scaled logits are $1$ and $0.5$, reducing the relative advantage of `A`.

This illustrates the effect on relative sharpness. It does not mean that a higher temperature necessarily produces a better or more creative answer.

<br/>

### Important limitation

Temperature is not a truthfulness control. A low temperature does not verify facts or guarantee that the model will choose a correct statement. It can make generation more concentrated around high-probability continuations, but those continuations can still be wrong.

<br/>

## 3. Top-k Filtering

**Top-k** keeps only the `k` highest-ranked candidates according to the scores used by the implementation. Candidates outside that set are excluded from the subsequent selection step. In a common sampling pipeline, the remaining candidates are renormalized to form a distribution and then sampled.

For example, if the ranked candidates are:

1. `A`: 0.40
2. `B`: 0.25
3. `C`: 0.18
4. `D`: 0.10
5. `E`: 0.07

With `top_k = 3`, the eligible set is `{A, B, C}`. `D` and `E` cannot be selected at that step after filtering.

Top-k uses a fixed candidate count, not a fixed amount of probability mass. The probability mass retained can therefore vary from one context to another.

<br/>

## 4. Top-p (Nucleus) Filtering

**Top-p**, also called nucleus sampling, keeps a ranked set of candidates whose cumulative probability reaches a configured threshold `p`, subject to the implementation's precise inclusion rule. The selected set is usually the smallest leading set that reaches or exceeds the threshold.

For example, using the distribution above:

| Candidate | Probability | Cumulative probability |
|---|---:|---:|
| `A` | 0.40 | 0.40 |
| `B` | 0.25 | 0.65 |
| `C` | 0.18 | 0.83 |
| `D` | 0.10 | 0.93 |
| `E` | 0.07 | 1.00 |

With `top_p = 0.80`, the cumulative probability after `B` is only `0.65`, while after `C` it is `0.83`. The candidate set is therefore `{A, B, C}` under the usual smallest-prefix rule.

Unlike top-k, top-p can retain a different number of tokens at different generation steps. A concentrated distribution may reach the threshold with only a few candidates; a flatter distribution may require more.

<br/>

## 5. Numerical Example: Comparing Candidate Sets

Use this illustrative next-token distribution, already sorted from highest to lowest probability:

| Rank | Token | Probability | Cumulative probability |
|---:|---|---:|---:|
| 1 | `A` | 0.40 | 0.40 |
| 2 | `B` | 0.25 | 0.65 |
| 3 | `C` | 0.18 | 0.83 |
| 4 | `D` | 0.10 | 0.93 |
| 5 | `E` | 0.07 | 1.00 |

<br/>

### Top-k result

If `top_k = 2`, keep the two highest-ranked candidates:

$$
S_k = \{A, B\}
$$

The retained probability mass before renormalization is $0.40 + 0.25 = 0.65$.

### Top-p result

If `top_p = 0.80`, keep the smallest ranked prefix whose cumulative probability reaches at least `0.80`:

$$
S_p = \{A, B, C\}
$$

The retained mass before renormalization is \(0.83\).

<br/>

### Combined top-k and top-p

If both filters are supported and applied, the candidate set is constrained by both rules. In this example, `top_k = 4` first allows `{A, B, C, D}`, and `top_p = 0.80` applied to the relevant normalized distribution may retain `{A, B, C}`. However, the exact result depends on whether the implementation applies top-p before or after top-k and whether it recomputes or renormalizes probabilities between steps.

**Do not assume a universal operation order.** Providers can differ in which parameters they support, how they define the filtering order, and how they handle boundary cases.

<br/>

## 6. How the Settings Interact

A decoding pipeline may conceptually perform operations like:

1. Obtain logits from the model.
2. Apply temperature or another score transformation.
3. Convert scores into probabilities.
4. Apply top-k and/or top-p candidate filtering.
5. Renormalize the remaining candidates.
6. Select a token, often by sampling.

This is a useful conceptual sequence, not a universal contract. A runtime may use a different order, define its filtering calculations differently, or support only a subset of these controls. Because temperature can change the probability distribution, it can also change which tokens fall inside a top-p nucleus. Top-k's rank-based candidate count is less directly tied to cumulative mass, although ties and implementation details may affect boundary behavior.

<br/>

### Why operation order matters

Imagine a candidate distribution where `A` and `B` dominate but several other tokens have small probabilities. Temperature changes the distribution's sharpness. If top-p is calculated after temperature, the number of candidates required to reach the cumulative threshold can change. If filtering is performed at a different stage, the resulting set can differ.

Therefore, parameter names alone are not enough to guarantee identical behavior across providers.

<br/>

## 7. Defaults and Provider-Specific Support

Inference APIs do not all expose the same controls. One provider may support temperature and top-p but not top-k; another may impose parameter constraints or use different defaults. A model may also have recommended settings or restrictions that differ from the serving platform's defaults.

Before running a comparison, record:

- Provider and endpoint/runtime.
- Exact model identifier or revision.
- Whether temperature, top-k, and top-p are supported.
- Explicit values for supported settings.
- Any documented default values and parameter constraints.
- Whether settings are ignored, rejected, clamped, or transformed when unsupported or out of range.
- Stop conditions, maximum output tokens, and seed support where available.

Avoid silently comparing a provider's default configuration with another provider's default configuration. If the defaults are unknown, record them as unknown rather than assuming they match.

<br/>

## 8. Temperature Does Not Control Truthfulness

Temperature changes the relative probability of candidate tokens. It does not add evidence, retrieve authoritative facts, validate claims, or guarantee correctness.

A low temperature may make a response more consistent with the model's most likely continuation, but the most likely continuation can still contain a factual error. A higher temperature may produce more varied outputs, but variety is not the same as quality.

Likewise, **low temperature does not guarantee reproducibility**. Other sources of variation include:

- The model or model revision changing.
- Prompt formatting or tokenizer differences.
- Provider/runtime implementation differences.
- Nondeterministic execution or tie-breaking.
- Hidden or unspecified defaults.
- Sampling behavior and random-seed support.

If a task requires factual reliability, use appropriate evidence, retrieval, validation, or evaluation. Do not treat temperature as a substitute for those mechanisms.

<br/>

## 9. Small Generation Experiment

To compare decoding settings fairly, use the same prompt and model version, change one parameter at a time, and run multiple trials where the configuration is stochastic.

### Suggested procedure

1. Choose one short prompt that supports several plausible continuations.
2. Fix the model identifier, system prompt, input, output-token limit, and stop sequences.
3. Record the provider's supported decoding parameters and defaults.
4. Run a baseline with explicit settings where possible.
5. Change only temperature, then compare results across multiple runs.
6. Repeat with top-k or top-p only if the provider supports them.
7. Record output variation, repetition, task adherence, latency, and any factual errors.
8. Repeat trials rather than drawing conclusions from a single response.
9. Keep a clear record of unsupported settings and implementation-specific constraints.

<br/>

### Experiment log template

| Run | Model/version | Temperature | Top-k | Top-p | Seed | Output summary | Variation/repetition | Latency |
|---|---|---:|---:|---:|---|---|---|---|
| 1 | Record value | Record value | Record value or N/A | Record value or N/A | Record value or N/A | Record output | Record observation | Record value |
| 2 | Same as baseline | Change one setting | Same/N/A | Same/N/A | Record value or N/A | Record output | Record observation | Record value |
| 3 | Same as baseline | Same as run 2 | Same/N/A | Change one setting | Record value or N/A | Record output | Record observation | Record value |

For a useful comparison, evaluate both **variation** and **task quality**. Different wording is not automatically better, and identical outputs are not proof of factual correctness.

<br/>

## 10. Common Misconceptions

- **“Temperature directly makes a model truthful or creative.”** It changes the probability distribution used for selection; it does not verify truth or guarantee creativity.
- **“Top-k and top-p are the same.”** Top-k limits the number of eligible candidates by rank; top-p limits the set by cumulative probability mass.
- **“Top-p always keeps the same number of candidates.”** No. The candidate count can change with the distribution.
- **“Combining top-k and top-p has a universal result.”** No. The result can depend on operation order, probability handling, and provider implementation.
- **“A low temperature guarantees the same answer every time.”** No. Reproducibility depends on the complete model and serving setup, not temperature alone.
- **“Every API supports every decoding parameter.”** No. Parameter availability, defaults, valid ranges, and semantics are provider-specific.
- **“A single run is enough to compare settings.”** Usually not when generation is stochastic. Multiple controlled runs are more informative.

<br/>

## 11. Practice

### Exercise 1 — Candidate filtering

Use the distribution:

| Token | Probability |
|---|---:|
| `A` | 0.40 |
| `B` | 0.25 |
| `C` | 0.18 |
| `D` | 0.10 |
| `E` | 0.07 |

Assume the probabilities are sorted and use the usual smallest-prefix rule for top-p.

1. What is the candidate set for `top_k = 3`?
2. What is the candidate set for `top_p = 0.70`?
3. What is the candidate set for `top_p = 0.90`?
4. What is the retained probability mass for `top_k = 2` before renormalization?

<br/>

### Exercise 2 — Temperature

In a common softmax formulation, what happens to the relative sharpness of the distribution when positive temperature decreases? Why does this not mean that the model becomes more truthful?

<br/>

### Exercise 3 — Operation order

Explain why applying top-p after temperature scaling may produce a different candidate set from applying top-p before temperature scaling.

<br/>

### Exercise 4 — Provider comparison

You compare two APIs, both with a parameter named `temperature = 0.7`, but the outputs differ. List at least four things to verify before attributing the difference to the model itself.

<br/>

### Exercise 5 — Experimental design

Design a small experiment to compare two temperature settings. Identify the variables to hold constant, what to record, and why multiple runs may be needed.

<br/>

## 12. Answers and Checkpoint Review

### Exercise 1 — Suggested answers

1. `top_k = 3`: `{A, B, C}`.
2. `top_p = 0.70`: cumulative mass after `A` and `B` is `0.65`; adding `C` reaches `0.83`. Set: `{A, B, C}`.
3. `top_p = 0.90`: cumulative mass reaches `0.93` after `D`. Set: `{A, B, C, D}`.
4. `top_k = 2`: retained mass is \(0.40 + 0.25 = 0.65\).

<br/>

### Exercise 2 — Suggested answer

Decreasing a positive temperature generally sharpens the distribution, giving relatively more probability to higher-scoring candidates. It does not introduce new evidence or check factual claims, so the most likely continuation can still be wrong.

<br/>

### Exercise 3 — Suggested answer

Temperature changes the probability distribution. Top-p selects a candidate prefix based on cumulative probability, so changing the distribution before filtering can change how many candidates are needed to reach the threshold. Exact behavior depends on the implementation's operation order and filtering semantics.

<br/>

### Exercise 4 — Suggested answer

Check the exact model version, prompt and chat template, supported parameters and defaults, top-k/top-p values, output limits and stop sequences, seed behavior, provider/runtime version, and any documented transformations or restrictions. The same parameter name does not guarantee identical implementation semantics.

<br/>

### Exercise 5 — Suggested answer

Use the same model version, prompt, template, output-token limit, stop conditions, and all other decoding settings. Run multiple trials at each temperature, record the actual settings and outputs, and compare variation, repetition, task adherence, factual errors, and latency. Multiple runs help reveal variability that a single output cannot show.

<br/>

### Checkpoint

**Which controls change candidate selection, and why do effects depend on the implementation?** Temperature changes relative probabilities by rescaling logits; top-k restricts the candidate set by rank; top-p restricts it by cumulative probability. Their combined effect depends on operation order, probability normalization, boundary rules, parameter support, and provider-specific defaults.

<br/>

## Summary

Temperature adjusts the relative sharpness of the next-token distribution. Top-k keeps a fixed number of highest-ranked candidates, while top-p keeps a ranked set based on cumulative probability. These controls can interact, and their precise behavior depends on the serving implementation. Temperature is not a truthfulness control, low temperature does not guarantee reproducibility, and comparisons should use the same prompts and model setup across multiple runs.
