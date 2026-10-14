# 05. Instruction-Tuning Examples and Data Formats

> **Level:** 12 — Fine-Tuning and Model Customization  
> **Purpose:** Convert reviewed examples into the exact input format expected by a model and verify that the intended target responses contribute to the training objective.

<br/>

## Learning objectives

By the end of this chapter, you should be able to:

- Compare instruction/input/output records with conversational message formats.
- Explain why a model's supported chat template and special tokens matter.
- Understand which tokens contribute to training loss and how masking may be configured.
- Handle truncation, padding, sequence length, and example packing carefully.
- Validate schemas, message ordering, and target responses before training.
- Convert reviewed examples into a supported format and inspect tokenized targets.

<br/>

## 1. Why data format matters

A fine-tuning dataset is not just a collection of good answers. Each example must be represented in a form the selected model and training framework understand.

A dataset can contain correct instructions and targets yet train the model incorrectly if:

- The message roles are wrong or out of order.
- The model's expected chat template is not used.
- Special tokens are missing or inserted incorrectly.
- The target response is truncated.
- Loss is applied to the wrong tokens.
- Padding or packing causes unintended training targets.
- A schema conversion silently drops fields or changes meaning.

**Core rule:** Validate the rendered and tokenized training examples—not only the original JSON or CSV records.

<br/>

## 2. Instruction/input/output records

A simple instruction-tuning record separates the task instruction, optional input, and desired output.

```json
{
  "instruction": "Extract the asset identifier from the report. Return null if it is absent.",
  "input": "Pump P-17 stopped during operation.",
  "output": "{\"asset_id\": \"P-17\"}"
}
```

Conceptually:

- `instruction` describes what the model should do.
- `input` contains the instance-specific material.
- `output` is the target response the model should learn to produce.

This representation is easy to inspect, label, and audit. It is not automatically a model-ready training sequence; a preprocessing step must map the fields to the selected model's expected format.

<br/>

### Example with no separate input

```json
{
  "instruction": "Rewrite this sentence in a professional tone: 'send it now'",
  "input": "",
  "output": "Please send it as soon as possible."
}
```

The instruction and input may be combined into a single user message during preprocessing. The exact mapping is a design choice that must be consistent with the model's training and inference template.

<br/>

## 3. Conversation formats

Chat-oriented models commonly represent an example as a sequence of messages with roles, such as `system`, `user`, and `assistant`. Some formats also support tool messages and other metadata.

Illustrative conversation record:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Extract the asset identifier. Do not guess missing values."
    },
    {
      "role": "user",
      "content": "Pump P-17 stopped during operation."
    },
    {
      "role": "assistant",
      "content": "{\"asset_id\": \"P-17\"}"
    }
  ]
}
```

The conversation representation preserves the role and ordering of each message. This is useful when the intended behavior depends on system instructions, multi-turn context, or the distinction between user and assistant content.

Not every provider or framework accepts the same JSON schema. Some expect JSONL with one object per line; others use provider-specific message fields or a framework-specific dataset format. Always verify the supported format for the exact model, trainer, and service.

<br/>

### Comparison

| Feature | Instruction/input/output | Conversation messages |
|---|---|---|
| Main structure | Task instruction, optional input, target output | Ordered messages with roles |
| Simplicity | Easy to inspect for single-turn tasks | More explicit role structure |
| Multi-turn context | Requires an explicit conversion or extension | Naturally represents message sequences |
| System/user/assistant roles | Often implicit in fields | Explicit |
| Model-ready by default? | No; mapping is usually required | Not necessarily; template/rendering may still be required |
| Best fit | Simple instruction-response tasks | Chat models and tasks requiring role-aware context |

Neither representation is universally superior. Choose the format supported by the selected training path and capable of expressing the task without losing important information.

<br/>

## 4. Chat templates and special tokens

### 4.1 What is a chat template?

A chat template converts structured messages into the token sequence expected by a particular model. It determines how message boundaries, roles, content, and end markers are represented.

A conceptual rendered conversation might look like this:

```text
<|system|>
Extract the asset identifier. Do not guess missing values.
<|user|>
Pump P-17 stopped during operation.
<|assistant|>
{"asset_id": "P-17"}
```

**This is illustrative pseudotext, not a universal token format.** Actual templates and special tokens differ by model family and tokenizer. Some use dedicated token IDs for message boundaries, role markers, turn endings, or control flow.

<br/>

### 4.2 Why the exact template matters

The same visible text can produce different token sequences under different tokenizers and templates. A template mismatch can teach the model the wrong message structure or make training and inference behave differently.

Before training, verify:

- The exact base-model identifier and revision.
- The tokenizer associated with that model.
- The model's documented chat template.
- The expected end-of-message and end-of-turn behavior.
- Whether assistant prefixes or generation prompts are added.
- Whether system and tool messages are supported in the chosen fine-tuning path.

Use the model's supported template instead of inventing special-token strings. A string that looks like a special token is not necessarily interpreted as the intended dedicated token ID by every tokenizer.

<br/>

### Hugging Face illustration

The following example inspects a tokenizer's configured template. It requires a compatible model tokenizer and the `transformers` library.

```python
from transformers import AutoTokenizer

model_id = "HuggingFaceTB/SmolLM2-135M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

messages = [
    {"role": "system", "content": "Return concise, factual answers."},
    {"role": "user", "content": "Extract the asset ID from: Pump P-17 stopped."},
    {"role": "assistant", "content": '{"asset_id": "P-17"}'},
]

print("Configured chat template exists:", bool(tokenizer.chat_template))

rendered = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=False,
)
print(rendered)
```

This is an inspection example, not a training run. Confirm the selected model's current tokenizer and template documentation before using it. For supervised fine-tuning, the training example normally includes the desired assistant target; inference prompts may instead end with a generation prefix.

<br/>

## 5. Which tokens contribute to the training loss?

In supervised fine-tuning, the model produces token predictions and the training procedure computes a loss against target token IDs. The precise objective and masking behavior depend on the model and implementation.

For many instruction-tuning workflows, the intended behavior is to train on assistant target tokens while not directly supervising the model to reproduce the user prompt. However, **this is not universal**: some training recipes apply loss to a broader sequence, while others use completion-only or assistant-only loss.

<br/>

### Conceptual example

```text
System:    Extract the asset identifier.
User:      Pump P-17 stopped.
Assistant: {"asset_id": "P-17"}
```

A simplified assistant-only loss mask could be:

| Sequence segment | Included in loss? |
|---|---|
| System instruction tokens | No |
| User input tokens | No |
| Assistant target tokens | Yes |
| Padding tokens | No |

This table illustrates one common objective, not a rule for every trainer. End-of-turn tokens may also be part of the supervised target, depending on the training recipe.

<br/>

### Why loss masking matters

If the intended assistant response is accidentally masked out, the model may receive little or no direct learning signal for the desired answer. If loss is applied to tokens that should be context only, the model may be trained to reproduce prompt text unnecessarily.

Verify:
- Which positions have non-ignored labels.
- Whether assistant targets are included.
- Whether expected end markers are supervised as intended.
- Whether padding positions are excluded from loss.
- Whether packed examples preserve the intended boundaries and masks.

In many Hugging Face causal language-modeling pipelines, the label value `-100` is used to ignore positions in common loss implementations. This convention is framework-dependent; inspect the actual trainer and collator behavior.

<br/>

## 6. Inspect tokenized targets and labels

The following small example illustrates how to inspect a rendered sequence and the labels used by a completion-only setup. It intentionally demonstrates masking rather than a complete trainer. Actual label construction depends on the selected model's template and training library.

```python
from transformers import AutoTokenizer

model_id = "HuggingFaceTB/SmolLM2-135M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

messages = [
    {"role": "user", "content": "Extract the asset ID: Pump P-17 stopped."},
    {"role": "assistant", "content": '{"asset_id": "P-17"}'},
]

# Render the complete example with the model's template.
rendered = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=False,
)

encoded = tokenizer(
    rendered,
    add_special_tokens=False,
    return_tensors="pt",
)

print("Rendered example:\n", rendered)
print("Token count:", encoded["input_ids"].shape[1])
print("Token IDs:", encoded["input_ids"][0].tolist())
print("Decoded tokens:")
for token_id in encoded["input_ids"][0].tolist():
    print(token_id, repr(tokenizer.decode([token_id])))

# Important:
# This script prints tokens but does NOT reliably infer the assistant span.
# Construct assistant/completion masks using the chosen trainer's documented
# chat-template and masking support. Do not guess the target boundary by
# searching for a visible string that might also occur in the input.
```

This example is deliberately cautious: the rendered string alone is not a robust universal way to derive target masks. Use the selected training framework's supported assistant-mask or completion-only mechanism, then inspect the resulting labels and decoded supervised positions.

<br/>

### What a target inspection should show

For every sample or a carefully selected audit batch, confirm that:
1. The intended assistant response is present.
2. It has not been truncated.
3. The labels cover the intended target tokens.
4. Context-only tokens are masked if the chosen objective requires it.
5. Padding is ignored by the loss.
6. End markers and message boundaries are correct.

<br/>

## 7. Truncation and sequence length

The model and training configuration impose a maximum sequence length. Long examples may be truncated to fit.

Truncation can remove:
- The end of a user input.
- A key piece of context.
- The end of the assistant target.
- A required closing delimiter in structured output.

For instruction tuning, silently cutting off the desired response is especially damaging because the target no longer represents a complete answer.

<br/>

### Recommended checks

- Measure token-length distributions before training.
- Define a maximum sequence length based on model and hardware limits.
- Inspect examples near or beyond the limit.
- Choose a documented truncation policy.
- Reject, shorten, or restructure examples when important content would be lost.
- Confirm that truncation does not disproportionately remove rare classes or target endings.

Do not assume that a maximum character count is equivalent to a token limit. Tokenization depends on the model's vocabulary and the content.

<br/>

## 8. Padding and attention masks

Batches often contain examples of different lengths. Padding makes them fit a common tensor shape, while attention masks indicate which positions correspond to real tokens rather than padding.

Padding and loss masking are related but different:

- **Attention mask:** controls which positions are treated as valid input tokens in supported attention implementations.
- **Loss mask/labels:** controls which target positions contribute to the training objective.

Padding tokens should not accidentally become supervised target content. The exact padding side and token configuration depend on the model and trainer. Some causal language-modeling setups reuse an end-of-sequence token as padding, which makes the collator's masking behavior particularly important.

Validate a batch after collation, not only the individual examples before batching.

<br/>

## 9. Packing multiple examples into one sequence

Packing combines shorter examples into a longer sequence to improve training efficiency. It can reduce wasted padding, but it introduces boundary and attention considerations.

Potential risks:
- One example's target is joined incorrectly to the next example.
- The model attends across examples when the training design intended independence.
- Position IDs or attention masks are incorrect for the packed format.
- A response is cut at a packing boundary.
- Loss is applied across a boundary in an unintended way.

Correct behavior depends on the trainer and packing strategy. Some implementations explicitly manage boundaries or attention; others may allow interactions between packed examples. Do not assume packing preserves independent-example semantics automatically.

For an initial small experiment, a simple non-packed setup can make inspection easier. Add packing only after the data pipeline is correct and the framework's behavior is understood.

<br/>

## 10. Validate schemas, message ordering, and targets

Perform structural validation before tokenization.

Example validator for a simple conversation schema:

```python
ALLOWED_ROLES = {"system", "user", "assistant"}

def validate_conversation(record: dict) -> None:
    if not isinstance(record, dict):
        raise TypeError("Record must be a dictionary.")

    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list.")

    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise TypeError(f"Message {index} must be a dictionary.")

        if message.get("role") not in ALLOWED_ROLES:
            raise ValueError(f"Unsupported role at message {index}.")

        if not isinstance(message.get("content"), str):
            raise ValueError(f"Message {index} content must be a string.")

        if not message["content"].strip():
            raise ValueError(f"Message {index} content is empty.")

    if messages[-1]["role"] != "assistant":
        raise ValueError("Expected a target assistant response at the end.")

# Example:
example = {
    "messages": [
        {"role": "user", "content": "Extract the asset ID from Pump P-17."},
        {"role": "assistant", "content": '{"asset_id": "P-17"}'},
    ]
}
validate_conversation(example)
print("Basic schema validation passed.")
```

This validator is intentionally minimal. Extend it for the selected provider/framework and task. For example, multi-turn conversations may contain multiple assistant messages, tool messages may be required by some tasks, and some valid targets may intentionally be empty or represent refusals. Do not enforce a simplified schema that conflicts with the chosen training format.

<br/>

### Validate structured target outputs separately

If the target is intended to be JSON, parse it and validate its schema rather than checking only whether it looks like JSON.

```python
import json

target = '{"asset_id": "P-17"}'
parsed = json.loads(target)

if set(parsed) != {"asset_id"}:
    raise ValueError("Unexpected output fields.")

if parsed["asset_id"] is not None and not isinstance(parsed["asset_id"], str):
    raise TypeError("asset_id must be a string or null.")

print("Target JSON passed the example contract.")
```

In a real project, prefer a versioned schema or a Pydantic model for richer validation. The schema must match the application contract.

<br/>

## 11. Practice: convert and inspect a reviewed example

### Source record

```json
{
  "example_id": "INC-104",
  "instruction": "Extract the asset ID. Return null if it is absent.",
  "input": "Pump P-17 stopped during operation.",
  "output": "{\"asset_id\": \"P-17\"}"
}
```

<br/>


### Convert to conversation format

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Extract the asset ID. Return null if it is absent.\n\nReport:\nPump P-17 stopped during operation."
    },
    {
      "role": "assistant",
      "content": "{\"asset_id\": \"P-17\"}"
    }
  ]
}
```

This conversion places the instruction and report in the user message and the expected JSON in the assistant message. A system message could instead hold stable task instructions if that matches the intended serving design and the supported training format. Keep training and inference templates consistent.

<br/>

### Inspection checklist

- [ ] The instruction and source report are both present.
- [ ] The target JSON is valid and follows the output schema.
- [ ] The selected tokenizer's chat template is used.
- [ ] The rendered message order is correct.
- [ ] The sequence length is within the configured limit.
- [ ] The full target response is present after tokenization.
- [ ] The loss mask supervises the intended target tokens.
- [ ] Padding and packing do not introduce unintended targets.
- [ ] The example's source and review metadata remain traceable.

<br/>

## 12. Common mistakes

- **Assuming all chat formats are interchangeable:** role markers and special tokens vary by model.
- **Training on raw JSON without a conversion plan:** the model may not receive the intended message structure.
- **Using a different template at training and inference:** behavior can degrade due to a format mismatch.
- **Masking the target by mistake:** the model receives no direct learning signal for the desired response.
- **Supervising prompt tokens unintentionally:** the loss may optimize an unintended objective.
- **Ignoring truncation:** critical target tokens may disappear silently.
- **Confusing attention masks with loss masks:** they serve different functions.
- **Packing without boundary checks:** examples may influence each other or be labeled incorrectly.
- **Validating only JSON syntax:** valid JSON can still violate the application's schema or contain incorrect values.
- **Trusting a preprocessing script without inspecting outputs:** transformation bugs can affect the entire dataset.

<br/>

## 13. Exercises with answers

### Q1. What is the difference between an instruction/input/output record and a conversation record?

**Answer:** The first stores the task, optional input, and target in separate fields. A conversation record represents an ordered sequence of role-labeled messages. The former often needs conversion; the latter may still require the selected model's chat template.

<br/>

### Q2. Why should you use the selected model's supported chat template?

**Answer:** The template defines the token-level representation of roles, message boundaries, and turn endings. A mismatch can produce an input sequence different from what the model and training path expect.

<br/>

### Q3. What happens if the assistant target is accidentally masked from the loss?

**Answer:** The intended response may receive little or no direct supervision, so training cannot optimize that response in the intended way.

<br/>

### Q4. Are attention masks and loss masks the same?

**Answer:** No. Attention masks identify valid input positions for the attention implementation; loss labels or masks identify target positions that contribute to the objective.

<br/>

### Q5. Why is truncation of the target dangerous?

**Answer:** It can remove the answer ending, closing JSON delimiters, or required fields. The model may then be trained on incomplete or malformed targets.

<br/>

### Q6. Is packing always safe?

**Answer:** No. The implementation must handle example boundaries, attention behavior, positions, and loss correctly. Verify the selected trainer's packing semantics before using it.

<br/>

## 14. Checkpoint

Before a fine-tuning run, verify that:

1. The dataset schema matches the selected training path.
2. Instructions, inputs, roles, and targets are mapped correctly.
3. The exact supported chat template and tokenizer are used.
4. Special tokens and message endings are correct.
5. The intended assistant response appears in the tokenized sequence.
6. The intended target tokens contribute to the loss under the chosen masking policy.
7. Truncation, padding, and packing preserve the target and sequence boundaries.
8. Structured targets pass schema validation.
9. The preprocessing configuration and dataset version are recorded.

**Final checkpoint:** The presence of a correct response in the source JSON does not prove the model will learn from it. Verify the rendered sequence, token IDs, target boundaries, and loss labels to confirm that the intended response is actually included in the learning objective.

<br/>

## References

- [Hugging Face Transformers — Chat templates](https://huggingface.co/docs/transformers/chat_templating)
- [Hugging Face TRL — SFT Trainer](https://huggingface.co/docs/trl/sft_trainer)
- [Hugging Face Datasets — Main documentation](https://huggingface.co/docs/datasets/index)
- [Hugging Face Tokenizers — Encoding and padding](https://huggingface.co/docs/tokenizers/index)
- [PyTorch — Tensor documentation](https://pytorch.org/docs/stable/tensors.html)

> **Implementation note:** Dataset schemas, chat templates, masking options, packing behavior, and supported trainer features vary by model and library version. Check the current documentation for the exact training stack and inspect a real batch before launching a full run.
