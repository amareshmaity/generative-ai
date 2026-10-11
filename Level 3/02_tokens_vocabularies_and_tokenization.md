# Chapter 02 — Tokens, Vocabularies, and Tokenization

**Level 3: Transformer Architecture and Tokenization**  
**Structured GenAI Engineering Notes**

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Distinguish characters, words, subword tokens, token IDs, and vocabularies.
- Explain the basic ideas behind Byte-Pair Encoding (BPE), WordPiece, and Unigram tokenization.
- Describe encoding, decoding, special tokens, padding, and truncation.
- Explain how whitespace, punctuation, code, numbers, and multilingual text affect tokenization.
- Understand chat templates and message-boundary tokens at a high level.
- Explain why token counts and token IDs depend on the tokenizer.

<br/>

## 2. What Is Tokenization?

**Tokenization** is the process of converting text into smaller units called *tokens* so that a model can process the input numerically.

A language model does not normally receive raw text directly as its main numerical input. A tokenizer first converts the text into tokens, then maps those tokens to integer IDs. The model uses the IDs to look up learned embeddings.

A simplified pipeline is:

```text
Raw text
   |
   v
Tokenizer
   |
   +--> Tokens
   |
   +--> Token IDs
           |
           v
      Embedding lookup
           |
           v
      Transformer
```

Tokenization is an important part of a language model's input pipeline. The exact behavior depends on the tokenizer associated with the model.

<br/>

## 3. Characters, Words, Tokens, Token IDs, and Vocabularies

These terms are related, but they do not mean the same thing.

### 3.1 Characters

Characters are the text symbols that make up a string. Examples include letters, digits, punctuation marks, and spaces.

For example:

```text
Text: cat
Characters: c, a, t
```

Character counts can depend on how Unicode text is represented and counted. For ordinary introductory examples, it is sufficient to think of characters as the visible text units.

<br/>

### 3.2 Words

Words are linguistic units separated by spaces or punctuation in many writing systems. However, word boundaries are not universal: some languages do not use spaces between every word, and code or identifiers may not follow natural-language word boundaries.

For example:

```text
Text: cats are sleeping
Words: cats | are | sleeping
```

Word counts are not a reliable substitute for token counts because tokenizers do not necessarily assign one token to each word.

<br/>

### 3.3 Tokens

A **token** is a unit produced by a particular tokenizer. Depending on the tokenizer and input, a token may represent:

- A whole word.
- Part of a word.
- Punctuation.
- Whitespace together with text.
- A number fragment.
- A piece of code.
- A special control marker.

For example, a tokenizer might split `unhappiness` into multiple subword tokens, while another tokenizer may segment it differently. These examples depend on the vocabulary and tokenizer rules.

<br/>

### 3.4 Token IDs

A **token ID** is an integer assigned to a token in a tokenizer's vocabulary.

Illustrative example:

```text
Tokens:    ["cats", " are", " sleeping"]
Token IDs: [  481,   927,       6421]
```

These IDs are hypothetical. The same visible token may have a different ID in another tokenizer because vocabularies are not universal.

Token IDs are categorical identifiers, not semantic coordinates. For example, token ID 6421 is not inherently more meaningful or more similar to token ID 6422 than to token ID 100.

<br/>

### 3.5 Vocabulary

A tokenizer's **vocabulary** is the collection of token entries it can represent, typically associated with integer IDs. It may contain ordinary text tokens, byte or character-related units, and special tokens.

The vocabulary and tokenization algorithm work together to determine how text is segmented and encoded.

<br/>

### Summary of the distinctions

| Term | Meaning | Example |
|---|---|---|
| Character | A text symbol or character unit | `c` |
| Word | A linguistic unit | `sleeping` |
| Token | A unit produced by a tokenizer | `sleep`, `ing` (illustrative) |
| Token ID | Integer associated with a vocabulary entry | `6421` (hypothetical) |
| Vocabulary | Collection of token entries and their IDs | A model tokenizer's token inventory |

<br/>

## 4. Subword Tokenization

Many modern language-model tokenizers use subword units rather than requiring every word to exist as a single vocabulary entry.

Subword tokenization balances two goals:

1. Represent frequent text efficiently with reusable units.
2. Handle uncommon words by splitting them into smaller pieces.

For example, a tokenizer might represent:

```text
unhappiness
```

as:

```text
["un", "happi", "ness"]
```

This is only an illustration; actual segmentation varies by tokenizer.

Subword tokenization helps manage vocabulary size and lets models represent many words, including unfamiliar forms, by combining known pieces. It does not guarantee that every tokenizer handles every language or unusual string equally well.

<br/>

## 5. Common Tokenization Algorithms

BPE, WordPiece, and Unigram are common subword-tokenization approaches. They differ in how their vocabularies or segmentations are learned and selected.

<br/>

### 5.1 Byte-Pair Encoding (BPE)

BPE builds a vocabulary by repeatedly merging frequently occurring adjacent units in training text, starting from smaller units.

Conceptually:

1. Begin with small units, such as characters or bytes, depending on the implementation.
2. Count adjacent pairs in the training corpus.
3. Merge a frequently occurring pair into a new unit.
4. Repeat until the target vocabulary size or another stopping condition is reached.
5. During encoding, segment new text using the learned vocabulary and merge rules.

A simplified illustration:

```text
Initial units:  l o w e r
Possible merge: l + o → lo
Next merge:     lo + w → low
```

The real algorithm uses corpus statistics and a defined sequence of merges. This toy sequence is not a complete BPE training example.

**Key intuition:** Frequently occurring sequences can become single tokens, while less common words may be represented by multiple pieces.

<br/>

### 5.2 WordPiece

WordPiece is a subword-tokenization method associated with models such as BERT.

At a high level, it learns a vocabulary of subword units and segments text into pieces using that vocabulary and its tokenization procedure. Common pieces can be represented directly, while less common words can be split into smaller known units when possible.

Illustrative example:

```text
unwanted → un + ##want + ##ed
```

The `##` notation is commonly used by BERT's WordPiece tokenizer to indicate a continuation piece; it is not literal text from the original word. The exact segmentation is tokenizer-dependent.

**Key intuition:** WordPiece aims to represent words using a reusable vocabulary of subword units. Its vocabulary-learning procedure differs from BPE's simple repeated-pair-merge description.

<br/>

### 5.3 Unigram tokenization

Unigram tokenization starts with a relatively large candidate vocabulary and assigns probabilities or scores to candidate subword units. A tokenizer then selects a segmentation according to its learned model, commonly choosing a high-probability or best-scoring sequence of pieces.

Conceptually:

1. Start with many candidate pieces.
2. Estimate scores for candidate pieces from training data.
3. Remove or reduce the usefulness of pieces that contribute less to the model, according to the training procedure.
4. Select a segmentation using the remaining vocabulary and scoring method.

SentencePiece supports Unigram and BPE tokenization and can operate directly on raw text without requiring conventional whitespace-based pre-tokenization.

**Key intuition:** Unigram tokenization evaluates candidate segmentations using learned piece scores rather than relying only on a fixed sequence of pair merges.

<br/>

### 5.4 High-level comparison

| Method | Core idea | Conceptual distinction |
|---|---|---|
| BPE | Repeatedly merge frequent adjacent units | Builds units through a merge sequence |
| WordPiece | Learn and use a subword vocabulary with its segmentation procedure | Commonly associated with BERT; continuation pieces may use markers such as `##` |
| Unigram | Score candidate pieces and choose a likely segmentation | Uses a probabilistic or score-based vocabulary model |

These descriptions are conceptual. Implementations differ in normalization, pre-tokenization, byte handling, unknown-token behavior, and special-token processing.

<br/>

## 6. Encoding and Decoding

### 6.1 Encoding

**Encoding** converts input text into token IDs.

```text
Text → tokenizer → token IDs
```

For example, using a hypothetical tokenizer:

```text
Input: "Hello!"
Tokens: ["Hello", "!"]
IDs:    [154,  22]
```

The token boundaries and IDs are illustrative.

<br/>

### 6.2 Decoding

**Decoding** converts token IDs back into a text representation.

```text
Token IDs → tokenizer decoder → text
```

For example:

```text
IDs: [154, 22]
Text: "Hello!"
```

Decoding may not always reproduce the original input exactly. Depending on the tokenizer and options, normalization, special-token handling, whitespace conventions, or invalid input representations can affect the result.

<br/>

### 6.3 Encoding and decoding in code

The following example uses Hugging Face Transformers with a pretrained tokenizer. It requires an internet connection the first time the tokenizer files are downloaded, unless the files are already cached.

```python
from transformers import AutoTokenizer

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

text = "Transformers process text."

# Convert text to token IDs
encoded = tokenizer(
    text,
    add_special_tokens=True
)

print("Input text:", text)
print("Token IDs:", encoded["input_ids"])
print("Tokens:", tokenizer.convert_ids_to_tokens(encoded["input_ids"]))

# Convert IDs back to readable text
decoded = tokenizer.decode(
    encoded["input_ids"],
    skip_special_tokens=True
)

print("Decoded text:", decoded)
```

Install the required library if needed:

```bash
pip install transformers
```

BERT's uncased tokenizer lowercases text as part of its processing, so decoded text may not preserve the original capitalization. Special tokens may also be included in the encoded sequence and omitted during decoding when `skip_special_tokens=True`.

<br/>

## 7. Special Tokens

**Special tokens** are dedicated vocabulary entries used to mark structure, boundaries, or specific control information. Their meanings depend on the model and tokenizer.

Examples in some tokenization systems include:

| Special token | Common role |
|---|---|
| `[CLS]` | Classification-related sequence marker in BERT-style inputs |
| `[SEP]` | Separator or sequence-boundary marker in BERT-style inputs |
| `[PAD]` | Padding position |
| `[UNK]` | Unknown-token marker in tokenizers that use one |
| `[MASK]` | Masking marker used in BERT-style masked-language-model workflows |

These are examples, not a universal set. GPT-style and other model families may use different special tokens, and not every model uses every token shown here.

Special tokens are not ordinary words, even when their readable spelling looks like text in a dump. Tokenizers often recognize them as dedicated vocabulary entries.

<br/>

### Chat message-boundary tokens

Chat-oriented models may use special tokens to mark message boundaries, identify the speaker, separate headers from message bodies, or indicate that an assistant turn has ended or control is being handed off.

A conceptual message structure may look like:

```text
[message start] [speaker / metadata] [message body] [ending marker]
```

Actual token spellings and semantics vary by model. A visible string such as `...` or a token-like spelling should not be assumed to be a special token unless the tokenizer or model format defines it as one.

<br/>

## 8. Chat Templates and Message Boundaries

A chat model often expects messages to be serialized into a model-specific format. A **chat template** converts structured messages—such as system, user, and assistant messages—into the token sequence expected by the model.

Conceptual conversation:

```text
User: Hi.
Assistant: Hello!
```

A chat template may turn the messages into a structured sequence containing:

- A message-start marker.
- A speaker label.
- Optional header metadata.
- The message content.
- An end-of-message, end-of-turn, or handoff marker.

These markers are important because the model may interpret them as structural or control information rather than ordinary prose.

With Hugging Face tokenizers that support chat templates, a conversation can be formatted using code such as:

```python
messages = [
    {"role": "user", "content": "Explain tokenization briefly."}
]

formatted_text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

print(formatted_text)
```

**Important:** Not every tokenizer has a chat template. Use the template associated with the target model rather than inventing a format. Some APIs accept structured messages directly and apply formatting internally. Avoid accidentally applying a template twice.

Detailed tool-calling control flow is outside this chapter; the focus here is recognizing that message structure can be encoded in the input sequence.

<br/>

## 9. Padding and Truncation

Models commonly process batches of sequences. Different input sequences may contain different numbers of tokens, but a batch tensor often needs a consistent sequence length.

### 9.1 Padding

**Padding** adds designated padding tokens so sequences in a batch have a common length.

Suppose the encoded sequences are:

```text
Sequence A: [12, 25, 31]
Sequence B: [19, 44]
```

If the padding ID is `0`, they may be padded to length three:

```text
Sequence A: [12, 25, 31]
Sequence B: [19, 44,  0]
```

The padding ID `0` is illustrative; actual token IDs vary.

Attention masks or related mechanisms are commonly used so the model can distinguish real tokens from padding positions where appropriate. The exact handling depends on the model and task.

<br/>

### 9.2 Truncation

**Truncation** removes tokens when a sequence exceeds a configured maximum length.

For example, truncating this sequence to four tokens:

```text
Original:   [10, 20, 30, 40, 50, 60]
Truncated:  [10, 20, 30, 40]
```

This is an illustration. Real tokenizers may support different truncation sides and strategies, and paired inputs may have additional rules.

Truncation can remove important information. Choose the maximum length based on model limits and task requirements rather than assuming that cutting the sequence is harmless.

<br/>

### 9.3 Padding and truncation with a tokenizer

```python
batch_texts = [
    "Short example.",
    "This is a somewhat longer example sentence."
]

batch = tokenizer(
    batch_texts,
    padding=True,
    truncation=True,
    max_length=12,
    return_tensors="pt"
)

print("Input IDs shape:", batch["input_ids"].shape)
print("Attention mask shape:", batch["attention_mask"].shape)
```

This example produces PyTorch tensors. The sequence length is constrained by the configured maximum, but the precise output depends on tokenization and the selected tokenizer.

- `padding=True` pads sequences in the batch to a common length.
- `truncation=True` enables truncation when necessary.
- `max_length=12` sets the configured maximum length for this encoding call.
- `attention_mask` commonly marks real token positions and padded positions, often with `1` and `0` respectively.

<br/>

## 10. Why Text Types Tokenize Differently

Tokenization depends on the exact string and the tokenizer's vocabulary and rules. Whitespace, punctuation, code, numbers, and writing systems can all affect the resulting token sequence.

### 10.1 Whitespace

Whitespace may be attached to a token or represented through tokenizer-specific conventions.

For example, some tokenizers distinguish a word at the beginning of a string from the same word preceded by a space. Consequently, these inputs may tokenize differently:

```text
"hello"
" hello"
```

Do not assume that spaces are always discarded or always become separate tokens.

<br/>

### 10.2 Punctuation

Punctuation may be represented as separate tokens or combined with adjacent text.

```text
"hello, world!"
```

A tokenizer might separate commas and exclamation marks, but exact segmentation depends on its rules and vocabulary.

<br/>

### 10.3 Code

Programming-language syntax contains identifiers, operators, brackets, indentation-related whitespace, and punctuation. A tokenizer may split these in ways that do not correspond to programming-language concepts.

```python
def add(a, b):
    return a + b
```

The function name, variable names, parentheses, commas, colon, indentation, and operators can all affect tokenization. Token boundaries are determined by the tokenizer, not by Python's parser.

<br/>

### 10.4 Numbers

Numbers may be represented as one token or multiple pieces.

For example:

```text
20261011
3.14159265
123456789012345
```

A tokenizer may split a long number into multiple tokens. Different number formats, decimal points, signs, separators, and whitespace may also change segmentation.

Do not assume one numeric value equals one token.

<br/>

### 10.5 Multilingual text

Different languages and scripts can have very different tokenization behavior. Languages with clear whitespace boundaries, languages that commonly omit spaces between words, mixed-script text, accented characters, and emoji may all be segmented differently.

A tokenizer's training data, vocabulary, normalization rules, and underlying encoding approach affect how efficiently it represents different languages.

**Practical implication:** Compare tokenization using representative inputs from the languages and data formats your application will actually process.

<br/>

## 11. Why Token Counts Depend on the Tokenizer

A token count is the number of tokens produced by a specific tokenizer for a specific input representation.

Token counts can vary because tokenizers differ in:

- Vocabulary entries.
- Subword segmentation rules.
- Pre-tokenization and normalization.
- Handling of whitespace and punctuation.
- Handling of Unicode, bytes, and multilingual text.
- Special-token insertion.
- Chat-template formatting.

Therefore, a word count is not a dependable way to estimate token count.

For example, the same sentence might be represented by different numbers of tokens under two model tokenizers. Neither count is universally correct: each count is correct for its own tokenizer and input settings.

Token count matters for context-window budgeting, maximum input and output limits, latency, and usage-based cost. For accurate estimates, use the tokenizer and accounting rules associated with the model or API being used.

<br/>

## 12. Practice: Inspect Tokens and IDs

This exercise uses one tokenizer to inspect prose, punctuation, code, numbers, and multilingual text. The examples are designed to reveal tokenizer behavior, not to prescribe a universal segmentation.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

examples = {
    "prose": "Transformers process natural language.",
    "whitespace": "hello",
    "leading_space": " hello",
    "punctuation": "Hello, world!",
    "code": "def add(a, b): return a + b",
    "number": "Price: 123456.78",
    "multilingual": "Hello नमस्ते café"
}

for label, text in examples.items():
    encoded = tokenizer(
        text,
        add_special_tokens=False
    )
    tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])

    print(f"\n[{label}]")
    print("Text:", repr(text))
    print("Tokens:", tokens)
    print("Token IDs:", encoded["input_ids"])
    print("Token count:", len(encoded["input_ids"]))
```

Install the library if necessary:

```bash
pip install transformers
```

<br/>

### What to inspect

1. Compare the token count with the number of words.
2. Check whether punctuation is separate from adjacent words.
3. Compare the strings `"hello"` and `" hello"`.
4. Observe how the number is segmented.
5. Inspect how the selected tokenizer handles the multilingual string.
6. Remember that BERT's uncased tokenizer normalizes text, including lowercasing; other tokenizers may behave differently.

<br/>

### Optional comparison with a second tokenizer

Try another compatible tokenizer, for example:

```python
other_tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "Transformers process natural language."

for name, tok in [
    ("BERT", tokenizer),
    ("GPT-2", other_tokenizer)
]:
    ids = tok(text, add_special_tokens=False)["input_ids"]
    tokens = tok.convert_ids_to_tokens(ids)

    print(f"\n{name}")
    print("Tokens:", tokens)
    print("Token count:", len(ids))
```

This comparison illustrates that tokenizer vocabularies and segmentation rules differ. It does not imply that one tokenizer is universally better. Also note that GPT-2 and BERT have different tokenization conventions and model-specific special-token behavior.

<br/>

## 13. Common Misconceptions

### Misconception 1: One word always equals one token

**Correction:** A word can be one token or several subword tokens. Punctuation, whitespace, code, and numbers also affect token counts.

<br/>

### Misconception 2: Token IDs represent meaning directly

**Correction:** Token IDs are categorical vocabulary indices. The model learns vector representations through embedding parameters; the numerical size of an ID does not indicate semantic similarity.

<br/>

### Misconception 3: All models use the same tokenizer

**Correction:** Tokenizers differ in vocabulary, segmentation, normalization, and special-token conventions. Use the tokenizer associated with the model.

<br/>

### Misconception 4: Decoding always recreates the original string exactly

**Correction:** Normalization, special-token handling, whitespace conventions, and decoding options can affect the resulting text.

<br/>

### Misconception 5: Padding and truncation are interchangeable

**Correction:** Padding adds positions to align sequence lengths; truncation removes positions to meet a length limit.

<br/>

### Misconception 6: Chat messages are always plain text separated by role labels

**Correction:** Chat templates can encode message boundaries, roles, metadata, and turn-ending or control markers using model-specific conventions.

<br/>

## 14. Revision Questions and Answers

**Q1. What is the difference between a token and a token ID?**  
A token is a unit produced by a tokenizer; its token ID is the integer assigned to the corresponding vocabulary entry.

**Q2. Why do modern tokenizers often use subwords?**  
Subwords allow frequent sequences to be represented efficiently while letting uncommon words be assembled from reusable pieces.

**Q3. How do BPE and Unigram differ conceptually?**  
BPE builds units through repeated adjacent-pair merges. Unigram uses a scored vocabulary and selects a likely segmentation according to its learned model.

**Q4. What is a special token?**  
A dedicated vocabulary entry used for a structural or control purpose, such as marking a sequence boundary or padding position.

**Q5. What is the difference between padding and truncation?**  
Padding adds tokens to align lengths; truncation removes tokens to fit a configured limit.

**Q6. Why might two tokenizers assign different IDs to the same text?**  
They may use different vocabularies and tokenization rules, so both segmentation and the associated integer IDs can differ.

**Q7. Why is word count not a reliable token-count estimate?**  
Tokenizers may split words into subwords, attach whitespace or punctuation to tokens, and segment code, numbers, and multilingual text differently.

**Q8. Why are token IDs not meaning vectors?**  
They are categorical identifiers. Semantic and contextual representations are learned in the embedding and transformer computations, not encoded by the magnitude of the integer IDs.

<br/>

## 15. Chapter Summary

- Tokenization converts text into tokens and token IDs that a model can process.
- Characters, words, tokens, token IDs, and vocabularies are distinct concepts.
- Subword approaches such as BPE, WordPiece, and Unigram use different methods to build or select token segmentations.
- Encoding converts text to IDs; decoding converts IDs back to a text representation.
- Special tokens and chat templates can encode structure beyond ordinary prose.
- Padding aligns sequence lengths; truncation removes tokens to fit a length limit.
- Whitespace, punctuation, code, numbers, and multilingual text can tokenize differently.
- Token counts and token IDs depend on the tokenizer, vocabulary, settings, and input formatting.
- Token IDs are categorical indices, not semantic vectors.

<br/>

**Checkpoint:** Explain why word count is not a reliable token-count estimate, why token IDs are not meaning vectors, and why tokenization should be inspected using the tokenizer associated with the target model.

<br/>

**Next chapter:** `03_embedding_layers.md` — Embedding Layers.
