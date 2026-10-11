# Level 4: LLM Fundamentals and Inference

Understand how large language models learn, how their behavior is adapted, and how inference settings affect generated outputs. Learn to compare models using quality, context requirements, latency, memory, and cost.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 4`, following the previous levels. The filenames below are planned files, not existing chapter links.

## Prerequisites

- Complete [Level 3: Transformer Architecture and Tokenization](<../Level 3/README.md>).
- Understand tokens, logits, softmax, context windows, prefill, decoding, and KV caching.
- Understand training versus inference and basic probability distributions.
- Basic Python is useful for experiments. Local model exercises may require introductory PyTorch and compatible hardware.

## Learning outcomes

After completing this level, you should be able to:

- Explain next-token prediction and the difference between learning objectives and application capabilities.
- Distinguish pretraining, instruction tuning, preference optimization, and inference.
- Explain alignment goals and their limitations.
- Compare greedy decoding, beam search, and sampling.
- Use temperature, top-p, top-k, stopping rules, and output limits where supported.
- Explain reasoning-oriented inference and quantization trade-offs conceptually.
- Compare hosted and self-managed models using representative test cases.
- Run a small inference experiment and document quality, variability, runtime, and resource requirements.

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_next_token_prediction.md` | Prediction objective, probabilities, and generated sequences |
| 2 | `02_pretraining_and_training_data.md` | Data preparation, learning, and data limitations |
| 3 | `03_instruction_tuning_and_sft.md` | Demonstration-based adaptation and instruction following |
| 4 | `04_preference_optimization_and_rlhf.md` | Preference data, reward-based methods, and direct optimization |
| 5 | `05_alignment_and_model_behavior.md` | Desired behavior, safety, and remaining limitations |
| 6 | `06_inference_and_decoding_overview.md` | From logits to selected tokens |
| 7 | `07_greedy_beam_search_and_sampling.md` | Decoding approaches and their trade-offs |
| 8 | `08_temperature_top_p_and_top_k.md` | Sampling controls and experimental comparisons |
| 9 | `09_stop_sequences_and_output_limits.md` | Completion boundaries, truncation, and termination |
| 10 | `10_reasoning_models_and_inference_time_compute.md` | Additional inference computation and evaluation |
| 11 | `11_quantization_concepts.md` | Numerical precision, memory, and quality trade-offs |
| 12 | `12_open_weight_and_hosted_inference.md` | Access methods, local inference, and deployment choices |
| 13 | `13_model_selection_and_trade_offs.md` | Quality, context, latency, throughput, and cost |
| 14 | `14_failure_modes_and_limitations.md` | Unreliable behavior and practical mitigations |
| 15 | `15_practice_and_revision.md` | Experiments, comparisons, and the level deliverable |

## Chapter outlines

### 01. Next-Token Prediction

- Trace a context to logits, probabilities, and a next-token prediction.
- Explain predicting known target tokens during training versus choosing tokens during generation.
- Introduce cross-entropy loss and perplexity conceptually.
- Explain how repeated prediction produces a sequence.
- Distinguish lower prediction loss from verified factual correctness or application usefulness.

**Practice:** Use a toy probability distribution to trace several possible continuations.

**Checkpoint:** Explain how a prediction objective can support multiple tasks without guaranteeing their correctness.

### 02. Pretraining and Training Data

- Define pretraining and distinguish it from later adaptation.
- Introduce text collection, filtering, deduplication, tokenization, and dataset mixtures.
- Discuss data quality, coverage, contamination, licensing, and sensitive information.
- Introduce training steps, batches, optimization, and checkpoints conceptually.
- Discuss knowledge cutoffs, memorization, and generalization.
- Explain why parameter count or dataset size alone does not determine capability.

**Practice:** Create a conceptual data-preparation checklist for a hypothetical corpus.

**Checkpoint:** Explain why adding text to a prompt is different from updating training data or model weights.

### 03. Instruction Tuning and Supervised Fine-Tuning (SFT)

- Compare base and instruction-tuned language models.
- Explain learning from instruction-response or conversation demonstrations.
- Introduce training examples, chat formatting, and target-response loss masking conceptually.
- Discuss demonstration quality, diversity, overfitting, and behavior changes.
- Distinguish prompting, retrieval, and weight-updating customization.
- Explain why instruction tuning does not guarantee factual accuracy or safe behavior.

**Practice:** Draft a few consistent instruction-response examples and identify poor-quality alternatives.

**Checkpoint:** Explain SFT as a training method rather than an inference setting.

**Depth boundary:** Dataset preparation, LoRA, training configuration, and hands-on fine-tuning belong to Level 12.

### 04. Preference Optimization and RLHF

- Explain preference comparisons and chosen/rejected responses.
- Trace a conceptual RLHF pipeline: demonstrations, preference data, reward modeling, and policy optimization.
- Introduce direct preference optimization (DPO) as an alternative that does not require a separately trained reward model in its standard form.
- Compare supervised demonstrations with preference feedback.
- Discuss annotator disagreement, proxy objectives, reward exploitation, and evaluation needs.
- Explain that training pipelines vary and need not include every stage in this order.

**Practice:** Rank response pairs with an explicit rubric and discuss ambiguous preferences.

**Checkpoint:** Distinguish SFT, reward-model-based optimization, and direct preference optimization.

### 05. Alignment and Model Behavior

- Define desired behavior in terms of helpfulness, honesty, safety, and task requirements.
- Explain how data, training objectives, instructions, and application controls influence behavior.
- Discuss refusals, over-refusal, sycophancy, bias, and instruction-following failures.
- Distinguish model-level adaptation from runtime validation and policy enforcement.
- Explain why alignment is not a guarantee of correctness or security.

**Practice:** Define acceptable behavior for a use case and evaluate sample responses against it.

**Checkpoint:** Identify both model behavior requirements and application checks needed to enforce them.

### 06. Inference and Decoding Overview

- Review tokenization, prefill, logits, token selection, and repeated decoding.
- Distinguish model weights from request-time generation configuration.
- Explain output-token probabilities and the role of decoding algorithms.
- Separate context limits, generation limits, and stopping behavior.
- Discuss configuration reproducibility and implementation-dependent defaults.

**Practice:** Annotate an inference flow with the points where decoding settings are applied.

**Checkpoint:** Explain why changing sampling settings does not retrain the model.

### 07. Greedy Decoding, Beam Search, and Sampling

- Explain greedy selection of the highest-probability next token.
- Trace beam search as retaining multiple candidate sequences.
- Introduce sequence scoring, length effects, and search costs conceptually.
- Explain sampling from a next-token distribution.
- Compare determinism, diversity, repetition, runtime, and suitability for different tasks.
- Explain that beam search is not universally available or preferable for conversational generation.

**Practice:** Compare greedy selection, a small beam search, and sampling on a toy sequence tree.

**Checkpoint:** Distinguish local token choice from searching across multiple candidate sequences.

### 08. Temperature, Top-p, and Top-k

- Explain temperature as adjusting the relative sharpness of the distribution before sampling.
- Explain top-k as limiting candidates by rank and top-p as limiting them by cumulative probability.
- Show a small numerical example of candidate filtering.
- Discuss interactions, operation order, defaults, and provider-specific support.
- Explain that temperature does not control truthfulness and low-temperature output is not always reproducible.
- Compare settings using the same prompts and multiple runs.

**Practice:** Calculate candidate sets for a toy distribution, then compare supported settings in a small generation experiment.

**Checkpoint:** Explain which controls change candidate selection and why their effects depend on the implementation.

### 09. Stop Sequences and Output Limits

- Distinguish end-of-sequence tokens, configured stop strings, and maximum generated-token limits.
- Explain termination metadata and detecting incomplete output.
- Discuss accidental stopping, truncation, and broken structured output.
- Introduce context-dependent output budgets and model-specific accounting rules.
- Explain how internal reasoning tokens may affect limits where documented by a provider.
- Discuss bounded continuation and validation rather than unlimited retries.

**Practice:** Review examples ending normally, hitting a limit, and matching a stop string; identify what the application should check.

**Checkpoint:** Distinguish an intentionally completed answer from one cut off by an output limit.

### 10. Reasoning-Capable Models and Inference-Time Computation

- Introduce models and inference methods designed to spend additional computation on a response.
- Discuss internal reasoning, candidate generation, checking, and selection at a conceptual level.
- Distinguish model-native reasoning behavior from application-controlled multi-call methods.
- Compare potential quality improvements with latency and cost.
- Discuss task suitability, unsupported settings, and provider-specific budget controls.
- Explain why a visible rationale is not proof of correct reasoning or a faithful account of internal computation.
- Evaluate final answers against known outcomes rather than explanation length.

**Practice:** Design a comparison between a fast baseline and a reasoning-oriented option using verifiable tasks.

**Checkpoint:** Explain when additional inference computation might help and how to measure whether it does.

**Scope boundary:** Autonomous agent loops and orchestration remain in the separate Agentic AI course.

### 11. Quantization Concepts

- Compare floating-point precision and lower-bit representations conceptually.
- Distinguish weight, activation, and KV-cache quantization.
- Introduce scales, rounding, and quantization error through a toy example.
- Compare model-weight memory with total runtime memory, including caches and overhead.
- Discuss hardware support, compatibility, quality regressions, and possible speed trade-offs.
- Distinguish post-training quantization from quantization-aware training at a high level.
- Explain why lower precision does not automatically produce faster inference.

**Practice:** Estimate weight storage for a hypothetical parameter count and several bit widths, explicitly excluding runtime overhead.

**Checkpoint:** Explain why a model's weight-file size is not its full inference memory requirement.

### 12. Open-Weight and Hosted Inference

- Distinguish access to model weights from hosted service access.
- Explain that an open-weight model may also be offered through a hosted provider.
- Review licensing, model documentation, chat templates, and tokenizer compatibility.
- Outline loading a tokenizer and small pretrained model, placing it on a device, and generating output.
- Compare setup effort, control, privacy, hardware, maintenance, and service reliability.
- Discuss secure artifact loading and dependency provenance.

**Practice:** Load a suitable small open-weight model and tokenizer, generate text, and record runtime and memory on available hardware. If hardware is insufficient, document a hosted alternative and its limitations.

**Checkpoint:** Choose an access approach independently of the model's licensing and architecture.

### 13. Model Selection and Trade-offs

- Define task-specific success criteria before selecting models.
- Compare quality, instruction following, structured-output needs, modalities, and context requirements.
- Measure time to first token, total latency, throughput, and output length where available.
- Compare hosted usage cost with self-managed infrastructure and operating effort.
- Consider supported controls, versioning, privacy, and deployment constraints.
- Evaluate representative, difficult, and unanswerable requests using a fixed rubric.
- Record uncertainty and avoid treating a public benchmark as sufficient evidence for your application.

**Practice:** Build a decision matrix for two candidate models or configurations using the same test set.

**Checkpoint:** Justify a selection with measured results and explicit requirements.

### 14. Common Failure Modes and Limitations

- Hallucinated facts, fabricated references, and unsupported certainty.
- Repetition, incoherence, instruction failures, and format errors.
- Weak performance on ambiguous, unfamiliar, multilingual, or numerical tasks.
- Context omission, truncation, and failure to use relevant supplied information.
- Bias, sensitive-data exposure, and susceptibility to untrusted instructions.
- Model or service changes that cause behavioral regressions.
- Match mitigations to failure types: verification, retrieval, validation, suitable tools, abstention, and human review.
- Explain remaining limitations rather than promising complete elimination of failures.

**Practice:** Categorize observed failures and propose a check or mitigation for each.

**Checkpoint:** Separate generation-setting problems from model-capability, data, and application-design problems.

### 15. Practice and Revision

- Compare training stages and their effects on behavior.
- Trace greedy decoding, beam search, and sampling with toy examples.
- Compare supported generation settings on fixed prompts.
- Detect stopping and truncation failures.
- Estimate weight storage and record inference resource requirements.
- Compare model quality, latency, cost, and limitations.
- Complete the inference comparison report below.

**Checkpoint:** Defend a model/configuration recommendation and state when you would reconsider it.

## Level deliverable: Inference comparison report

Create `inference_comparison_report.md` in this folder with:

1. A training-to-inference diagram distinguishing pretraining, SFT, preference optimization, and generation.
2. A fixed set of at least ten prompts covering extraction, summarization, verifiable questions, ambiguous requests, and unsupported requests.
3. A simple rubric for correctness, relevance, output validity, and handling missing information.
4. A comparison of two models or two configurations of one model using the same test cases.
5. Repeated runs on selected prompts to inspect output variability.
6. The model identifier, tokenizer or service, date, environment, prompts, supported settings, and stopping rules.
7. Quality results, failure categories, runtime, token usage, cost, and memory measurements where available.
8. A recommendation explaining trade-offs, measurement limitations, and known regressions.

Use synthetic or public inputs. Small local models and toy probability exercises are sufficient; paid services and model training are not required. Mark unavailable measurements explicitly, and distinguish calculated estimates from observations.

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Intuition and a concrete example.
3. Definitions and a diagram or small worked calculation.
4. Training-time versus inference-time implications.
5. Practical settings, supported variations, and trade-offs.
6. Common misconceptions and failure modes.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify current model capabilities, settings, licenses, and pricing when writing provider-specific notes. Define the assumptions behind every numerical estimate.

## Completion checklist

- [ ] Explain next-token prediction and its limitations.
- [ ] Distinguish pretraining, SFT, preference optimization, and inference.
- [ ] Explain alignment goals without treating them as guarantees.
- [ ] Compare greedy decoding, beam search, and sampling.
- [ ] Explain temperature, top-p, and top-k where supported.
- [ ] Recognize stop conditions and truncated output.
- [ ] Explain inference-time computation and its quality/latency/cost trade-offs.
- [ ] Explain quantization and estimate weight storage with explicit assumptions.
- [ ] Run or document a small open-weight inference exercise.
- [ ] Compare candidate models or configurations using fixed test cases.
- [ ] Categorize failure modes and document remaining risks.
- [ ] Complete and review the inference comparison report.

## Scope and next step

This level focuses on understanding training stages and using models at inference time. Foundation-model training, hands-on fine-tuning, advanced quantization implementations, distributed serving, and systematic evaluation frameworks are studied in later levels or optional extensions.

Next: **Level 5 — Prompt Engineering and Structured Generation** in the [main course outline](../README.md).
