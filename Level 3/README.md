# Level 3: Transformer Architecture and Tokenization

Understand how text becomes tokens, how transformer blocks process those tokens, and how a model produces outputs during inference. Connect architectural concepts to context usage, latency, and memory requirements.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 3`, following Levels 1 and 2. The filenames below are planned files, not existing chapter links.

<br/>

## Prerequisites

- Complete [Level 2: Generative Model Architectures](<../Level 2/README.md>).
- Understand autoregressive generation, training versus inference, and the high-level role of transformers.
- Review vectors, matrix multiplication, dot products, probability distributions, and softmax.
- Understand neural-network layers and learned parameters conceptually.
- Basic Python and NumPy are sufficient for small exercises; PyTorch is optional.

<br/>

## Learning outcomes

After completing this level, you should be able to:

- Inspect tokens, token IDs, vocabularies, and tokenizer behavior.
- Distinguish token embeddings, positional information, and contextual hidden states.
- Trace query, key, and value projections through scaled dot-product and multi-head attention.
- Explain attention masks, feed-forward layers, residual connections, and normalization.
- Compare encoder-only, decoder-only, and encoder-decoder architectures using BERT, GPT-style models, and T5.
- Trace a decoder-only model from prompt tokenization to next-token generation.
- Estimate context usage and explain prefill, decoding, and KV-cache trade-offs.

<br/>

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_transformer_overview.md` | Components and overall data flow |
| 2 | `02_tokens_vocabularies_and_tokenization.md` | Tokens, IDs, subwords, and special tokens |
| 3 | `03_embedding_layers.md` | Embedding lookup and representation shapes |
| 4 | `04_positional_information_and_encoding.md` | Sequence order and positional methods |
| 5 | `05_query_key_and_value_representations.md` | Learned projections and their roles |
| 6 | `06_self_attention_and_scaled_dot_product.md` | Scores, scaling, softmax, and weighted values |
| 7 | `07_causal_padding_and_other_masks.md` | Allowed attention positions and masking distinctions |
| 8 | `08_multi_head_attention.md` | Multiple heads, concatenation, and output projection |
| 9 | `09_feed_forward_networks.md` | Position-wise transformations and activations |
| 10 | `10_residual_connections_and_layer_normalization.md` | Stable information flow and block organization |
| 11 | `11_encoder_decoder_architectures.md` | Encoder-only, decoder-only, and encoder-decoder designs |
| 12 | `12_bert_gpt_and_t5_examples.md` | Architecture and training-objective comparisons |
| 13 | `13_context_windows_and_token_budgets.md` | Input/output budgeting and long-context limitations |
| 14 | `14_inference_flow_prefill_and_decoding.md` | Prompt processing, logits, and autoregressive generation |
| 15 | `15_kv_cache_intuition.md` | Reusing attention state and memory trade-offs |
| 16 | `16_practice_and_revision.md` | Worked examples, diagrams, and the level deliverable |

<br/>

## Chapter outlines

### 01. Transformer Overview

- Trace tokenization, embeddings, transformer blocks, and task-specific output layers.
- Identify attention, feed-forward networks, residual connections, and normalization.
- Distinguish model architecture from training objective and generation procedure.
- Introduce batch, sequence, and hidden dimensions.
- Explain what the overview simplifies and what varies between model implementations.

**Practice:** Annotate a transformer diagram with component roles and data shapes.

**Checkpoint:** Describe the complete flow without treating a transformer as only an attention layer.

<br/>

### 02. Tokens, Vocabularies, and Tokenization

- Distinguish characters, words, subword tokens, token IDs, and vocabularies.
- Introduce byte-pair encoding, WordPiece, and Unigram tokenization conceptually.
- Explain encoding, decoding, special tokens, padding, and truncation.
- Examine whitespace, punctuation, code, numbers, and multilingual text.
- Introduce chat templates and message-boundary tokens at a high level.
- Explain why token counts and token IDs depend on the tokenizer.

**Practice:** Inspect tokens and IDs for several strings using one tokenizer; optionally compare a second tokenizer.

**Checkpoint:** Explain why word count is not a reliable token count and why token IDs are not meaning vectors.

<br/>

### 03. Embedding Layers

- Trace a token ID lookup in a learned embedding matrix.
- Introduce vocabulary size and embedding dimension.
- Follow a sequence from integer IDs to a matrix of vectors.
- Distinguish input embeddings from contextual hidden states.
- Distinguish token embeddings from document embeddings used for retrieval.
- Preview the language-model output projection and optional weight tying.

**Practice:** Perform a small embedding lookup with a toy matrix and label its dimensions.

**Checkpoint:** Explain what is learned and why the same token's later hidden state can vary with context.

<br/>

### 04. Positional Information and Encoding

- Explain why attention needs information about sequence position.
- Introduce sinusoidal and learned absolute position embeddings.
- Preview relative position methods and rotary position embeddings conceptually.
- Explain that positional methods enter computation differently across architectures.
- Discuss position limits and why longer-context behavior requires validation.

**Practice:** Compare two reordered token sequences and identify the information needed to distinguish them.

**Checkpoint:** Explain positional information without assuming every model adds the same positional vector to its embeddings.

<br/>

### 05. Query, Key, and Value Representations

- Define queries, keys, and values as learned projections of hidden states.
- Trace `Q = XW_Q`, `K = XW_K`, and `V = XW_V` with small matrices.
- Explain queries and keys as determining attention scores and values as supplying aggregated content.
- Distinguish self-attention from cross-attention by the source of these representations.
- Introduce projection dimensions without imposing one model's configuration on all transformers.

**Practice:** Label Q, K, and V sources for self-attention and encoder-decoder cross-attention.

**Checkpoint:** Explain why Q, K, and V are not separate input documents or hand-written search queries.

<br/>

### 06. Self-Attention and Scaled Dot-Product Attention

- Trace `softmax(QK^T / sqrt(d_k) + mask)V`.
- Explain dot-product scores, scaling, row-wise softmax, and weighted aggregation.
- Distinguish score matrices, attention weights, and output vectors.
- Track dimensions in a small worked example.
- Introduce the quadratic attention-matrix size of standard full attention.
- Discuss why attention weights alone are insufficient explanations of model behavior.

**Practice:** Calculate a tiny attention example by hand or with NumPy and verify that each allowed row's weights sum to one.

**Checkpoint:** Explain how one position combines information from other allowed positions.

<br/>

### 07. Causal, Padding, and Other Masks

- Explain causal masks as preventing attention to future positions.
- Explain padding masks as excluding padding positions.
- Compare bidirectional attention with causal attention.
- Distinguish attention masking from masked-token prediction during training.
- Introduce combined masks and encoder-decoder attention patterns.

**Practice:** Draw allowed-attention grids for a short causal sequence and a padded bidirectional sequence.

**Checkpoint:** Distinguish a causal attention mask from BERT's masked-language-model objective.

<br/>

### 08. Multi-Head Attention

- Explain parallel learned attention heads and head dimensions.
- Trace per-head projections, attention, concatenation, and output projection.
- Compare single-head and multi-head computation conceptually.
- Explain that head roles are learned rather than assigned fixed linguistic jobs.
- Preview multi-query and grouped-query attention as variants relevant to cache memory.

**Practice:** Track shapes through a toy multi-head attention layer.

**Checkpoint:** Explain how heads are combined and why more heads do not automatically imply better performance.

<br/>

### 09. Feed-Forward Networks

- Explain the position-wise network applied to each token's hidden state.
- Introduce expansion, activation, and projection back to the hidden dimension.
- Compare its role with attention's mixing across positions.
- Preview GELU and gated variants such as SwiGLU.
- Explain shared network parameters across positions within a block.

**Practice:** Draw the input, expanded intermediate representation, and output shapes.

**Checkpoint:** Explain how attention and feed-forward layers contribute different transformations.

<br/>

### 10. Residual Connections and Layer Normalization

- Explain residual addition and shape compatibility.
- Introduce layer normalization and its per-token feature normalization.
- Compare pre-normalization and post-normalization block layouts conceptually.
- Preview RMSNorm as a related normalization variant.
- Discuss information flow and training stability without deriving gradients.
- Assemble attention and feed-forward sublayers into a complete block.

**Practice:** Annotate a block diagram with residual branches and normalization placement.

**Checkpoint:** Explain why adding a residual connection differs from concatenating outputs.

<br/>

### 11. Encoder-Only, Decoder-Only, and Encoder-Decoder Architectures

- Trace bidirectional encoder processing and common task heads.
- Trace causal decoder processing and next-token output.
- Trace encoder-decoder processing with decoder cross-attention to encoder outputs.
- Compare attention access patterns and input/output flows.
- Introduce training with known target tokens versus generation using previous outputs.
- Map designs to representation, classification, generation, and sequence transformation tasks.

**Practice:** Draw all three architectures and label self-attention, causal attention, and cross-attention where applicable.

**Checkpoint:** Explain how the decoder in an encoder-decoder model differs from a decoder-only model.

<br/>

### 12. BERT, GPT-Style Models, and T5 as Examples

- Use BERT as an encoder-only example with masked-language-model training.
- Use GPT-style models as decoder-only examples with next-token prediction.
- Use T5 as an encoder-decoder example with text-to-text tasks and span-corruption pretraining.
- Compare tokenization, attention access, training objectives, and typical uses.
- Distinguish architectural examples from product-specific features.
- Explain why architecture alone does not establish instruction-following capability.

**Practice:** Build a BERT/GPT/T5 comparison table and select suitable designs for three tasks.

**Checkpoint:** Keep architectural differences separate from pretraining and later adaptation.

<br/>

### 13. Context Windows and Token Budgets

- Define context length, input length, and output limits.
- Budget instructions, chat history, retrieved text, formatting, and generated output.
- Explain that provider-specific limits and accounting must be checked separately.
- Compare padding, truncation, and selecting relevant context.
- Discuss memory, latency, and attention-computation implications of longer sequences.
- Distinguish nominal context capacity from reliable use of all supplied information.
- Estimate usage-based cost only with documented model pricing and accounting rules.

**Practice:** Allocate a hypothetical token budget across instructions, user input, retrieved content, and output; state the assumed limit rules.

**Checkpoint:** Explain why fitting within a context window does not guarantee a correct answer.

<br/>

### 14. Inference Flow, Prefill, and Autoregressive Decoding

- Trace prompt formatting, tokenization, embeddings, blocks, output projection, logits, and token selection.
- Explain prefill as processing the supplied prompt and producing state for continuation.
- Trace iterative decoding as generating and appending successive tokens.
- Compare parallel work within prefill with sequential dependencies across generated tokens.
- Introduce time to first token and time per output token.
- Explain stopping conditions and streaming at a high level.
- Contrast this generation flow with encoder-only inference.

**Practice:** Trace three generated tokens and identify prefill, decoding, and the growing sequence at each stage.

**Checkpoint:** Distinguish prefill latency from the latency of generating the remaining output.

**Depth boundary:** Detailed decoding strategies, temperature, top-p, and top-k belong to Level 4; provider streaming implementation belongs to Level 6.

<br/>

### 15. KV Cache Intuition

- Explain reusing past key and value tensors during causal decoding.
- Identify the per-layer cache and how it grows with sequence length.
- Explain why current queries still attend to earlier keys and values.
- Compare recomputing past representations with storing reusable state.
- Discuss sequence length, batch size, layers, KV heads, precision, and memory usage.
- Distinguish the KV cache from model weights, persistent conversation memory, and response caching.
- Preview cache limits, prefix reuse, and implementation-dependent optimizations.

**Practice:** Compare cached and uncached decoding diagrams. Optionally estimate cache size from a stated toy configuration.

**Checkpoint:** Explain what the cache saves and why it does not eliminate all work associated with long context.

<br/>

### 16. Practice and Revision

- Inspect tokenization and compare token counts across inputs.
- Calculate a small attention example and apply a causal mask.
- Track shapes through embeddings, attention, and a feed-forward network.
- Compare BERT, GPT-style models, and T5.
- Trace inference from prompt to generated tokens.
- Explain context budgeting and KV-cache trade-offs.
- Complete the transformer walkthrough below.

**Checkpoint:** Explain the full pipeline using both a diagram and a worked example.

<br/>

## Level deliverable: Transformer walkthrough

Create `transformer_walkthrough.md` in this folder with:

1. Tokenization examples for prose, code, and multilingual text, identifying the tokenizer used.
2. An annotated decoder-only inference diagram from text input to generated output.
3. A worked attention example showing Q, K, V, scores, a mask, weights, and output dimensions.
4. A complete transformer-block diagram with residual connections and normalization placement.
5. A comparison of BERT, GPT-style, and T5 architectures and objectives.
6. A hypothetical context budget with explicit assumptions about input and output limits.
7. A step-by-step explanation of prefill, three decoding steps, and KV-cache reuse.
8. References and any simplifications made in the explanation.

Small NumPy examples and conceptual diagrams are sufficient. Loading a small pretrained model is optional; training a transformer or using a paid API is not required.

<br/>

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Intuition and a concrete example.
3. Definitions, notation, and tensor shapes.
4. A diagram or small worked computation.
5. Connection to the overall transformer flow.
6. Common misconceptions and implementation variations.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Define symbols before using equations. Keep toy examples small enough to inspect, and verify model-specific configurations when writing the notes.

<br/>

## Completion checklist

- [ ] Inspect tokenization and distinguish tokens, IDs, and embeddings.
- [ ] Explain positional information and common approaches.
- [ ] Trace Q, K, V and scaled dot-product attention with shapes.
- [ ] Apply causal and padding masks and distinguish them from masked-token prediction.
- [ ] Explain multi-head attention, feed-forward layers, residual connections, and normalization.
- [ ] Compare encoder-only, decoder-only, and encoder-decoder designs.
- [ ] Explain BERT, GPT-style models, and T5 as architectural examples.
- [ ] Plan a context budget with stated assumptions.
- [ ] Trace prefill and autoregressive decoding.
- [ ] Explain KV-cache reuse and memory trade-offs.
- [ ] Complete and review the transformer walkthrough.

<br/>

## Scope and next step

This level develops architectural understanding through small computations and diagrams. Full transformer training, distributed inference, optimized attention kernels, and advanced serving are optional extensions or later production topics.

Next: **Level 4 — LLM Fundamentals and Inference** in the [main course outline](../README.md).
