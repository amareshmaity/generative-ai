# Chapter 11 — Context Selection and Compression

## Learning Objectives

By the end of this chapter, you should be able to:

- Allocate a model's context budget across instructions, the question, retrieved evidence, conversation history, and output.
- Select relevant and diverse evidence while removing duplicate or overlapping passages.
- Compare extractive evidence selection with generated summaries of retrieved evidence.
- Preserve source references, qualifiers, dates, quantities, conditions, and conflicting claims.
- Recognize how compression can lose information or introduce unsupported wording.
- Keep original passages available so compressed material can be verified.
- Assemble a bounded evidence packet for grounded answer generation.

<br/>

## 1. What Is Context Selection?

Retrieval can return more text than the model needs—or more than the model can safely fit into its context window. **Context selection** decides which retrieved passages should be included in the final prompt.

The goal is not to include as much text as possible. It is to provide enough relevant, trustworthy evidence to answer the question while preserving the details and qualifications needed to interpret it correctly.

A useful evidence packet should be:

- **Relevant:** supports the specific question.
- **Sufficient:** includes the facts and conditions required for a complete answer.
- **Non-redundant:** avoids repeated passages that add little information.
- **Traceable:** preserves source IDs, versions, and locators.
- **Authorized:** contains only evidence the caller is permitted to access.
- **Bounded:** fits the context budget with room for instructions and output.

Context selection follows retrieval and any reranking or parent expansion stages. It prepares evidence for answer generation; it does not itself establish that a generated answer is correct.

<br/>

## 2. Reserve Context Capacity Before Selecting Evidence

A model's context window is a shared budget. It must accommodate all input messages and the output the model may generate. Depending on the application, it may also include conversation history, tool results, structured instructions, and formatting constraints.

A simple planning equation is:

$$
B_{\text{evidence}} =
B_{\text{context}} -
B_{\text{instructions}} -
B_{\text{question/history}} -
B_{\text{output reserve}} -
B_{\text{safety margin}}
$$

Where:

- $B_{\text{context}}$ is the usable context capacity for the selected model/configuration.
- $B_{\text{instructions}}$ covers system and developer instructions and output-format requirements.
- $B_{\text{question/history}}$ covers the current question and any conversation history included.
- $B_{\text{output reserve}}$ is space reserved for generated output where the provider's limits require accounting for it.
- $B_{\text{safety margin}}$ allows for tokenization differences, metadata, message formatting, and estimation error.

This is a planning model, not a universal provider formula. Some APIs treat input and output limits separately; others expose a combined context limit. Follow the selected model's documented limits.

<br/>

### Example budget

Suppose a model configuration provides a usable budget of 16,000 tokens. An application estimates:

| Component | Planned tokens |
|---|---:|
| Instructions and output schema | 1,200 |
| Question and relevant history | 800 |
| Output reserve | 2,000 |
| Safety margin | 1,000 |
| Available evidence budget | 11,000 |

These figures are illustrative. Recalculate the budget for the actual model, request format, and output requirements. Do not assume a character count maps directly to a fixed number of tokens.

<br/>

### Practical guidance

- Reserve the output budget before filling the prompt with evidence.
- Count or estimate tokens using the selected model's tokenizer or a provider-supported method.
- Include headings, source labels, citation markers, and metadata in the estimate.
- Avoid filling the entire context window when the provider or prompt format requires additional overhead.
- Recalculate the evidence budget when instructions, conversation history, or output limits change.

<br/>

## 3. Select Evidence for Coverage, Not Just Similarity

A top-ranked passage is not automatically sufficient evidence. Several top results may repeat the same sentence, while a lower-ranked passage may contain an important exception or condition.

A practical selection process considers:

1. **Relevance:** Does the passage answer the question?
2. **Coverage:** Does it supply a distinct fact needed for a complete response?
3. **Authority and applicability:** Is the source appropriate for this question and version?
4. **Diversity:** Does it add a different useful point rather than repeat an existing passage?
5. **Freshness and conflict:** Is the passage current and are there contradictory sources?
6. **Authorization:** Is the caller allowed to see this passage?
7. **Cost:** Does its additional value justify its token cost?

Do not use similarity score as the only selection rule. A passage can be highly similar yet omit the exact condition requested.

<br/>

### Example

Question: “How many unused annual leave days can be carried over, and what approval is required?”

Retrieved candidates:

- Passage A: “Up to five unused days may be carried over.”
- Passage B: “Eligible full-time employees may carry over up to five unused days into the next leave year, subject to manager approval by 15 December.”
- Passage C: “Leave requests must be submitted through the employee portal.”
- Passage D: A duplicate of Passage B from an overlapping chunk.

A good evidence packet would usually prioritize B because it includes the amount and approval condition. A may be useful if it comes from a separate authoritative source or helps verify a conflict, but its wording is less complete. C may not answer the carryover question unless the procedure is also requested. D should generally be removed as redundant while preserving its provenance if it has a distinct source/version that matters.

<br/>

## 4. Deduplicate Overlapping Passages

Chunk overlap helps retrieval preserve context at chunk boundaries, but it can cause repeated text to appear in the retrieved set.

Deduplication can use several levels:

- **Exact duplicate:** identical chunk IDs or identical canonical text.
- **Near duplicate:** overlapping chunks that repeat most of the same content.
- **Semantic duplicate:** different wording that contributes essentially the same fact.
- **Repeated source evidence:** multiple passages from the same section that support the same claim.

Prefer stable IDs and source relationships when identifying exact duplicates. Text similarity can help detect overlap, but avoid merging passages merely because they discuss the same topic: one may contain an exception, date, or contradictory statement.

<br/>

### Safe deduplication rules

- Keep one canonical copy of exact duplicate text in the evidence packet.
- Preserve all relevant source references if the duplicates represent distinct sources or versions.
- Do not merge contradictory claims into a single statement.
- Keep nearby qualifiers, headings, and table labels when they affect meaning.
- Re-check source versions and authorization before selecting a canonical copy.

<br/>

## 5. Extractive Selection vs. Generated Compression

Two common approaches reduce evidence to a manageable size.

### Extractive selection

Select original sentences, passages, table rows, or spans without rewriting their substantive wording.

**Advantages**
- Preserves source wording.
- Easier to verify against the original.
- Lower risk of introducing new facts through paraphrase.
- Can preserve exact values, terminology, and qualifications.

**Limitations**
- May be less concise than a summary.
- Selected spans can lose context if headings or neighboring conditions are omitted.
- Requires careful source-span and citation tracking.

<br/>

### Generated compression

Ask a model to summarize or compress retrieved evidence into a shorter representation.

**Advantages**
- Can reduce token usage.
- Can combine related information into a more compact explanation.
- May be useful when evidence is long or repetitive.

**Limitations**
- May omit exceptions, dates, numbers, qualifiers, or disagreements.
- May introduce wording that is not directly supported by any source.
- Can collapse distinct claims from different versions or sources.
- May make uncertain evidence sound more definitive than it is.
- Requires validation against the original passages.

<br/>

### Comparison

| Dimension | Extractive selection | Generated compression |
|---|---|---|
| Source wording | Retains selected original spans | Rephrases or combines information |
| Information-loss risk | Can lose context through selection | Can lose context and details during summarization |
| Unsupported additions | Lower risk when text is copied faithfully | Higher risk; must be checked |
| Token efficiency | Depends on selected spans | Often more compact |
| Traceability | Straightforward with span-level references | Requires claim-to-source mapping |
| Best initial baseline | Usually simpler to audit | Useful after extractive selection is understood |

A practical starting point is to establish an extractive baseline first. Introduce generated compression only if the token savings or usability benefit justifies the additional validation burden.

<br/>

## 6. Preserve Qualifiers, Numbers, and Conflicting Claims

Compression is especially risky when it removes details that change a claim's meaning.

Preserve:

- **Quantities and units:** “five days” is not “five weeks.”
- **Dates and deadlines:** “by 15 December” is not the same as “in December.”
- **Eligibility:** “eligible full-time employees” is not “all employees.”
- **Conditions:** “subject to manager approval” is not optional background.
- **Negation:** “not permitted” must not become “permitted.”
- **Scope:** “for version 2.4.1” must not become “for the latest version.”
- **Uncertainty:** “may,” “typically,” and “not confirmed” must not be converted into certainty.
- **Source distinctions:** two sources may apply to different regions, versions, or user groups.
- **Conflicts:** contradictory claims should remain visibly contradictory until resolved using a defined source-priority policy.

<br/>

### Example of harmful compression

Original evidence A:

> “Eligible full-time employees may carry over up to five unused days, subject to manager approval by 15 December.”

Original evidence B:

> “Part-time employees must request exceptions through Human Resources. Approval is not automatic.”

Unsafe compressed version:

> “Employees can carry over five days with approval.”

What was lost or distorted?

- The eligibility restriction to full-time employees.
- The deadline.
- The special procedure for part-time employees.
- The fact that approval is not automatic.

A shorter statement can be less accurate even when each individual word sounds plausible.

<br/>

## 7. Keep Original Passages as the Source of Truth

A compressed evidence representation should never replace the original records.

Store the relationship between compressed claims and the source passages that support them. For example:

```json
{
  "evidence_item_id": "evidence-001",
  "compressed_text": "Eligible full-time employees may carry over up to five unused days with manager approval by 15 December.",
  "source_passages": [
    {
      "chunk_id": "leave-policy:v2026-03:section-2:c03",
      "source_id": "leave-policy",
      "document_version": "2026-03",
      "section_path": ["Annual Leave", "Carryover"],
      "page_number": 12
    }
  ],
  "compression_method": "extractive_or_validated_summary"
}
```

The values are illustrative. `compression_method` should reflect what the system actually did; do not label generated paraphrase as extractive.

Maintain access to the original passage text so that the application can:

- verify every compressed claim;
- restore omitted context;
- display citations or source excerpts;
- inspect contradictory evidence;
- debug hallucinations or incorrect summaries;
- reprocess evidence when a source is updated or deleted.

A source citation should point to the underlying source record and locator, not only to the temporary compressed text.

<br/>

## 8. Ordering and Long-Context Limitations

Even when all selected evidence fits within the context window, ordering can affect how well a model uses it. Long prompts may contain repeated material, distractors, and evidence distributed across distant positions. Model behavior varies by architecture and task, so do not assume every model attends equally to every token.

Practical controls:

- Put the most directly relevant evidence in a clear, predictable location.
- Group related passages and label source boundaries.
- Keep each claim close to its source reference.
- Place critical exceptions alongside the claims they qualify.
- Avoid burying decisive evidence in a large block of low-value text.
- Use a stable ordering rule, such as relevance first followed by complementary evidence.
- Evaluate ordering changes on the selected model rather than relying on a universal rule.

A possible evidence order is:

1. Direct answer-bearing passage.
2. Conditions, definitions, and exceptions.
3. Independent corroborating evidence.
4. Relevant conflicting evidence, clearly labeled.
5. Additional background only if it helps answer the question.

This is a starting policy, not a guarantee that every model performs best with this exact order.

<br/>

## 9. Assemble a Bounded Evidence Packet

An evidence packet is the structured collection of selected passages sent to answer generation.

A useful packet includes:

- the user's original question;
- selected evidence text;
- stable source and chunk IDs;
- document versions and page/section locators;
- relevant metadata such as effective date or category;
- explicit labels for conflicting or uncertain claims;
- the selected evidence order;
- a record of whether text was extracted or compressed.

Example:

```text
QUESTION
How many unused annual leave days can be carried over, and what approval is required?

EVIDENCE 1
Text: Eligible full-time employees may carry over up to five unused days into the next leave year, subject to manager approval by 15 December.
Source: leave-policy
Version: 2026-03
Location: Annual Leave > Carryover, page 12
Chunk ID: leave-policy:v2026-03:section-2:c03

EVIDENCE 2
Text: Part-time employees must request exceptions through Human Resources; approval is not automatic.
Source: leave-policy
Version: 2026-03
Location: Annual Leave > Exceptions, page 13
Chunk ID: leave-policy:v2026-03:section-3:c01

NOTES
- Keep the eligibility condition and approval deadline.
- Do not generalize the full-time rule to all employees.
- Original passages remain available for verification.
```

The content is illustrative. In an actual system, include only evidence that was retrieved, validated, and authorized for the current request.

<br/>

## 10. Python Example: Bounded Extractive Evidence Selection

The following minimal example selects candidates under a character budget, removes exact duplicate text, and preserves metadata. Character count is used only to make the example easy to read; production systems should estimate or count tokens with the target model's tokenizer.

```python
def select_evidence(
    candidates: list[dict],
    max_chars: int,
    max_items: int = 6,
) -> list[dict]:
    """
    Candidates should already be retrieved, ranked, and authorized.
    This simple baseline preserves original text and metadata.
    """
    if max_chars < 1 or max_items < 1:
        raise ValueError("Budgets must be positive")

    selected = []
    seen_text = set()
    used_chars = 0

    for item in candidates:
        text = item.get("content", "").strip()
        if not text:
            continue

        key = " ".join(text.split()).casefold()
        if key in seen_text:
            continue

        # Account for text length only in this illustrative implementation.
        if used_chars + len(text) > max_chars:
            continue

        selected.append({
            "chunk_id": item["chunk_id"],
            "source_id": item["source_id"],
            "document_version": item["document_version"],
            "section_path": item.get("section_path", []),
            "content": text,
        })
        seen_text.add(key)
        used_chars += len(text)

        if len(selected) >= max_items:
            break

    return selected
```

This baseline is intentionally simple. It does not optimize evidence diversity, detect semantic duplicates, resolve conflicting claims, count actual tokens, or implement authorization. It assumes candidate ranking and authorization have already been performed. Improve it incrementally and evaluate each change.

<br/>

## 11. Validate Generated Compression

If you use a model to compress evidence, treat its summary as a derived artifact that needs checking.

A practical validation workflow:

1. Keep the exact original passages and their metadata.
2. Ask the compression model to retain numbers, dates, qualifiers, negations, and source distinctions.
3. Require the output to identify which source passages support each claim.
4. Validate that source IDs and locators refer to actual retrieved records.
5. Compare key entities, quantities, dates, and qualifiers with the original evidence.
6. Check that no unsupported claims were added.
7. Flag contradictions rather than blending them into a single answer.
8. Reject or fall back to extractive evidence when validation fails.
9. Log the compression configuration and validation outcome without exposing sensitive content unnecessarily.

Automatic checks can catch many errors, but they cannot guarantee semantic equivalence. Human review or task-specific tests may be necessary for high-impact use cases.

<br/>

## 12. Practice — Build and Verify a Bounded Evidence Packet

Choose a labeled set of questions and retrieved passages. Include some overlapping chunks, a passage with an important qualifier, and at least one case with conflicting claims.

For each question:

1. Reserve space for instructions, the question/history, output, and safety margin.
2. Calculate the evidence budget using the target model's tokenization method.
3. Select evidence for relevance and coverage, not score alone.
4. Remove exact duplicates and inspect near-duplicate passages.
5. Build an extractive evidence packet with source IDs, versions, and locators.
6. If testing generated compression, create a separate compressed packet and retain the originals.
7. Compare numbers, dates, names, negations, qualifiers, and conflicts before and after compression.
8. Check whether each compressed claim can be traced to source passages.
9. Record token use, evidence coverage, irrelevant material, and any information loss.
10. Confirm that all evidence was authorized and that source permissions remain valid.

<br/>

### Suggested audit table

| Fact to preserve | Present in original? | Present in selected packet? | Present in compressed version? | Source verified? |
|---|---|---|---|---|
| Quantity and unit | — | — | — | — |
| Eligibility condition | — | — | — | — |
| Deadline or effective date | — | — | — | — |
| Exception or negation | — | — | — | — |
| Source/version distinction | — | — | — | — |

Fill the table using the actual source text. Do not mark a fact as preserved merely because the compressed wording sounds similar.

<br/>

## 13. Checkpoint — Model Answer

**Question:** Why must compressed text not be treated as more authoritative than its sources?

**Answer:**

Compressed text is a derived representation. Selection may omit surrounding context, and generated compression may lose qualifiers, dates, numbers, exceptions, uncertainty, or conflicts. A summary can also introduce unsupported wording or combine claims that apply to different source versions.

The original passages remain the authoritative evidence for verification. Preserve their source IDs, versions, and locators; map compressed claims back to those passages; and check key facts before using the compressed representation. If compression cannot be validated, use the original extractive passages or retrieve additional context. Never let a summary override the underlying source records.

<br/>

## Key Takeaways

1. Reserve context capacity for instructions, the question, history, output, and safety margin before selecting evidence.
2. Choose passages for relevance, coverage, diversity, provenance, and authorization—not similarity score alone.
3. Remove redundant overlap without erasing distinct sources, exceptions, or conflicts.
4. Extractive selection is generally easier to audit; generated compression can save tokens but requires validation.
5. Preserve numbers, dates, qualifiers, negation, uncertainty, source versions, and conflicting claims.
6. Keep original passages available and trace every compressed claim back to its sources.
7. Evaluate context quality, token cost, information loss, and downstream grounding rather than assuming shorter context is better.

<br/>

## References

- [OpenAI — Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic — Context Windows](https://docs.anthropic.com/en/docs/build-with-claude/context-windows)
- [LangChain — Contextual Compression](https://python.langchain.com/docs/how_to/contextual_compression/)
- [Sentence Transformers — Semantic Search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)
- [W3C — PROV-O: The PROV Ontology](https://www.w3.org/TR/prov-o/)

<br/>

## Next Chapter

**Chapter 12 — Grounded Answer Generation**

Next, use a carefully selected evidence packet to generate answers that distinguish supported facts from missing evidence, preserve citations, and avoid claims that the sources do not justify.
