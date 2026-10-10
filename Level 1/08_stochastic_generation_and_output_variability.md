# 08. Stochastic Generation and Output Variability

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain probabilistic generation and sampling at an intuitive level.
- Describe why repeated requests may produce different outputs.
- Explain temperature and sampling controls conceptually.
- Distinguish output variation from factual accuracy.
- Identify factors that limit reproducibility, including configuration changes and model updates.
- Explain why reliability testing requires multiple examples and, when appropriate, repeated runs.

<br/>

## 1. Why This Topic Matters

A generative model does not always produce one fixed answer for a given prompt. Depending on the model and its configuration, it may produce different wording, examples, structures, or conclusions across requests.

This variability can be useful when exploring ideas or generating alternative drafts. It can also create challenges when an application needs consistent formatting, stable behavior, or dependable answers.

One successful response demonstrates that the model *can* produce a useful result in that instance. It does not demonstrate that the model will produce a similarly useful result every time.

<br/>

## 2. Probabilistic Generation: An Intuition

Many language models generate text by predicting a probability distribution over possible next tokens. A **token** is a unit of text processing; it may be a word, part of a word, punctuation mark, or another unit.

At each generation step, the model estimates which tokens could come next and assigns them scores or probabilities. A decoding or sampling method then determines which token to select. The selected token becomes part of the context for generating the next token.

This process repeats until the model reaches a stopping condition, such as an end token or a configured output limit.

<br/>

### A simplified example

Suppose a prompt is:

> “For breakfast, I usually drink…”

A model might assign different probabilities to several possible next tokens:

| Possible next token | Illustrative probability |
|---|---:|
| tea | 0.45 |
| coffee | 0.35 |
| water | 0.12 |
| juice | 0.08 |

These values are **illustrative only**. They are not measurements from a real model.

A decoding method might select the most likely token, or a sampling method might select from multiple candidates according to their probabilities. Once a token is selected, later predictions depend on the updated context.

The example demonstrates why the same prompt can allow more than one plausible continuation.

<br/>

## 3. Why Repeated Requests May Differ

Repeated requests can produce different outputs for several reasons.

### Sampling choices

When generation uses sampling, more than one candidate token may be eligible for selection. Different selections can lead to different continuations.

<br/>

### Prompt and context differences

Even small changes in the prompt, conversation history, supplied documents, or formatting instructions can affect the model's response.

<br/>

### Configuration differences

Changes to generation settings—such as temperature, top-p, output limits, or other decoding options—can change the range or selection of possible outputs. The exact controls available depend on the model and API.

<br/>

### Model and service changes

A provider may update a model, its serving stack, or its default configuration. The same application request may therefore behave differently at a later time, even if your code appears unchanged.

<br/>

### Nondeterministic execution

Some inference systems may not guarantee bit-for-bit identical results across repeated executions, hardware, or serving configurations. Whether this matters depends on the model and the implementation.

**Key point:** Different output is not automatically evidence of a defect. The important question is whether the variation stays within the application's quality and safety requirements.

<br/>

## 4. Temperature: A Conceptual Control

**Temperature** is a generation setting used by many language-model APIs to influence how token scores are converted into a sampling distribution.

As a broad intuition:

- **Lower temperature:** tends to concentrate probability on higher-scoring choices, often producing more predictable outputs.
- **Higher temperature:** tends to spread probability more broadly, often allowing more varied outputs.

The exact effect depends on the model, decoding method, and other settings. A low temperature does not guarantee identical outputs, and a high temperature does not guarantee creativity or quality.

<br/>

### When might different settings be useful?

| Task | Desired behavior to evaluate |
|---|---|
| Extracting fields into a fixed schema | Consistency and valid structure |
| Drafting a standard customer response | Predictable wording and policy compliance |
| Brainstorming product names | A useful range of alternatives |
| Writing a creative story | Variety while following the prompt |
| Answering a factual question | Correctness and support from reliable information |

Do not select a temperature solely from a generic rule. Test the setting against the task and evaluate the outputs.

<br/>

## 5. Sampling Controls: Top-p and Related Ideas

Some model APIs expose additional sampling controls. One common example is **top-p sampling**, also called nucleus sampling.

Conceptually, top-p sampling limits the candidate set to tokens whose combined probability reaches a chosen cumulative probability threshold, and then samples from that set. The exact implementation and interaction with other controls depend on the system.

Temperature and top-p influence token selection in different ways. They should not be treated as interchangeable, and changing several settings simultaneously makes it harder to identify which change affected the output.

Other controls may include output-length limits, stop sequences, penalties, or provider-specific settings. Their availability and behavior are model-dependent; consult the documentation for the model or API being used.

For this chapter, the goal is to understand the concept rather than memorize settings or assume that every model exposes the same controls.

<br/>

## 6. More Variation Does Not Mean More Accuracy

**Variation and factual accuracy are different properties.**

A more varied output may offer new ideas, alternative phrasings, or different examples. It may also contain more unsupported claims or inconsistent details. A more predictable output can still be wrong.

For factual applications, assess correctness directly. Depending on the task, this may include:

- Comparing the answer with a trusted source.
- Checking extracted fields against the original input.
- Verifying calculations with deterministic code.
- Validating required output fields and allowed values.
- Measuring performance against labeled test examples.
- Sending uncertain or high-impact cases for human review.

A response should not be considered accurate simply because it sounds confident, is fluent, or resembles a previous answer.

<br/>

## 7. Reproducibility and Its Limits

**Reproducibility** means being able to repeat an experiment or request and obtain the same, or sufficiently similar, result under defined conditions.

For generative AI, reproducibility can be affected by several factors:

- The exact prompt and conversation context.
- The model identifier and version.
- The decoding method and generation parameters.
- The input data and any retrieved context.
- Provider defaults and API changes.
- Serving infrastructure and implementation details.
- Whether the system supports a seed or deterministic mode, and what guarantees it actually provides.

<br/>

### What should you record?

When evaluating a model or debugging an application, record relevant information such as:

- Exact input and prompt template.
- Model identifier and version, when available.
- Generation settings.
- Timestamp and API or library version, when relevant.
- Input documents or their stable identifiers.
- Output and validation result.
- Evaluation criteria and observed failures.

Avoid storing secrets or unnecessary sensitive data in experiment logs.

A fixed seed, if supported, may improve repeatability in some setups, but it is not a universal guarantee of identical results across model versions, providers, or execution environments.

<br/>

## 8. Why One Successful Output Is Not Enough

A single response is one observation. It cannot reveal the full range of behavior the application may encounter.

For example, a model might correctly classify one support ticket but misclassify tickets with unusual wording, multiple issues, spelling errors, or missing information.

Reliability testing should consider both:

1. **Different examples:** Does the application work across the range of inputs it is expected to handle?
2. **Repeated runs:** For the same input, does output variability affect the application's requirements?

Repeated runs are especially useful when sampling or other sources of nondeterminism may cause materially different results. Testing only one example—or only one run—can miss failure modes.

<br/>

### Test according to risk

- For a low-risk brainstorming tool, useful diversity may be the main goal.
- For structured extraction, track schema validity and field-level correctness.
- For a customer support workflow, test classification and routing across representative cases.
- For high-impact decisions, use stronger evaluation, clear escalation paths, and appropriate human oversight.

<br/>

## 9. Practice: Repeat One Prompt

### Option A — Model access is available

Choose a simple prompt, for example:

> “Suggest three practical ways to reduce food waste at home. Give one sentence for each suggestion.”

1. Use the exact same prompt for several runs.
2. Keep the model and generation settings unchanged.
3. Save the outputs.
4. Compare wording, suggestions, structure, factual claims, and instruction-following.
5. Repeat with a different setting only if the interface allows it, changing one setting at a time.
6. Record whether the differences matter for your intended use.

Do not assume that every response must differ. Some configurations may produce similar or identical outputs.

<br/>

### Option B — Model access is unavailable

Use the prepared outputs below as an illustrative exercise.

**Output A**

1. Plan meals before shopping.
2. Store leftovers in labeled containers.
3. Freeze food that will not be used soon.

**Output B**

1. Make a shopping list based on planned meals.
2. Label leftovers with dates so they are used in time.
3. Freeze extra portions before they spoil.

**Output C**

1. Check what is already in your kitchen before buying more.
2. Keep older food visible and use it first.
3. Freeze suitable ingredients or meals for later.

These are prepared examples, not results from repeated calls to a specific model.

<br/>

### Comparison worksheet

| Criterion | What to record |
|---|---|
| Main ideas | Which suggestions overlap, and which differ? |
| Wording | How does the phrasing change? |
| Format | Does each output follow the requested structure? |
| Factual quality | Are any claims questionable or unsupported? |
| Instruction-following | Does each output satisfy the prompt? |
| Practical usefulness | Would the differences matter to a user? |

**Reflection:** If all three outputs are useful, what have you learned? If one output is poor, what additional tests would you run before deciding whether the model is reliable?

<br/>

## 10. A Simple Evaluation Plan

For an application that depends on consistent model behavior, define a small evaluation plan before changing generation settings.

1. **Define success:** Specify what a correct and acceptable output looks like.
2. **Select representative inputs:** Include ordinary cases, edge cases, and ambiguous examples.
3. **Fix the test configuration:** Record the prompt, model, and settings.
4. **Run the test set:** Evaluate multiple different inputs.
5. **Repeat selected inputs:** Measure variability where it could affect outcomes.
6. **Score outputs:** Use task-appropriate measures, such as correctness, schema validity, instruction-following, or human ratings.
7. **Inspect failures:** Group errors by type rather than relying only on an average score.
8. **Change one factor at a time:** This makes comparisons easier to interpret.
9. **Re-test after changes:** Repeat evaluation when prompts, settings, dependencies, or models change.

The number of examples and repetitions should reflect the risk and expected usage. A small exercise is useful for learning, but it is not enough to establish production reliability.

<br/>

## 11. Common Misconceptions

- **“The same prompt must always produce the same response.”** Not necessarily. Sampling, context, settings, and service changes can affect outputs.
- **“Higher temperature means a better answer.”** No. It generally affects variation, not factual correctness.
- **“Lower temperature guarantees determinism.”** No. It may make output more predictable, but does not guarantee identical results in every system.
- **“A fluent answer is an accurate answer.”** Fluency and factual correctness are separate.
- **“One successful test proves reliability.”** One result cannot represent the range of expected inputs and repeated-run behavior.
- **“A fixed seed guarantees reproducibility everywhere.”** Seed support and guarantees vary by system and environment.
- **“If outputs differ, the model is broken.”** Variation may be expected; evaluate whether it violates the application's requirements.
- **“Testing many runs of one prompt is enough.”** Different inputs and edge cases are also necessary.

<br/>

## 12. Revision Questions and Answers

**Q1. What does probabilistic generation mean in a language model?**  
The model estimates probabilities for possible next tokens, and a decoding method determines which token is selected at each step.

**Q2. Why might repeated requests produce different outputs?**  
Sampling, prompt or context differences, configuration changes, model updates, and nondeterministic execution can all contribute.

**Q3. What is temperature used for?**  
It influences how token scores are converted into a sampling distribution, often affecting how predictable or varied the output is.

**Q4. Does a higher temperature improve factual accuracy?**  
No. Temperature affects generation behavior, not a guarantee of truth.

**Q5. What is top-p sampling?**  
It restricts the candidate tokens to a set whose cumulative probability reaches a chosen threshold, then samples from that set.

**Q6. What does reproducibility mean in this context?**  
Repeating a request or experiment under defined conditions and obtaining the same or sufficiently similar result.

**Q7. What information is useful to record during evaluation?**  
The prompt, model identifier, settings, relevant input context, output, timestamp or version details, and evaluation result.

**Q8. Why is one successful output insufficient evidence of reliability?**  
It is only one observation and does not reveal behavior across varied inputs, edge cases, or repeated runs.

**Q9. Why test multiple examples as well as repeated runs?**  
Multiple examples test general behavior across inputs; repeated runs help reveal output variability for the same input.

**Q10. What should you do after changing the model or its configuration?**  
Re-run appropriate evaluations and compare the results against defined success criteria.

<br/>

## 13. Chapter Summary

- Many generative models predict distributions over possible next tokens and use a decoding method to select tokens.
- Sampling and other system differences can make repeated outputs vary.
- Temperature and top-p are conceptual controls that influence token selection; exact behavior depends on the model and implementation.
- More variation does not imply more factual accuracy.
- Reproducibility depends on prompts, context, model versions, settings, and serving behavior.
- Useful evaluation covers different examples and repeated runs where variability matters.
- Record the configuration and evaluate outputs against task-specific criteria.
- One successful output is evidence of possibility, not proof of reliability.

<br/>

### Final Checkpoint

Explain why a model may answer the same prompt differently, describe what temperature changes conceptually, and state why **one successful output is insufficient evidence of reliability**. Your answer should include both testing across different examples and repeated runs where appropriate.
