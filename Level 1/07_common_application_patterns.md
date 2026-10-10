# 07. Common Application Patterns

## Learning Objectives

By the end of this chapter, you should be able to:

- Recognize common ways generative AI is used in applications.
- Distinguish summarization, rewriting, extraction, classification, drafting, coding assistance, and question answering.
- Identify where image, speech, and other media generation fit into an application.
- Describe retrieval-grounded question answering at a conceptual level without implementing a retrieval-augmented generation (RAG) pipeline.
- Explain how validation, business rules, and human review complement a model.
- Recognize when deterministic code or conventional search is sufficient.
- Describe the model's role as one component of a larger application.

<br/>

## 1. Why This Topic Matters

A generative AI model is rarely the whole product. In a real application, it usually performs a defined step within a larger workflow.

For example, an email assistant might collect a message, ask a model to draft a reply, check the draft against basic rules, and let a person review it before sending. The model contributes language understanding and generation, while the application handles permissions, validation, and the final action.

A useful way to think about an application is:

**Input → Model step (when useful) → Validation and rules → Output or human review**

Not every application needs every step, and not every step needs a generative model.

<br/>

## 2. Summarization and Rewriting

### Summarization

**Summarization** reduces a longer piece of content to a shorter version that preserves the most important information for a particular purpose.

Common examples include:

- Summarizing a long report for an executive.
- Producing meeting notes from a transcript.
- Creating a short overview of a support conversation.
- Listing key decisions and action items from a document.

The desired summary depends on the audience and task. A short executive summary may prioritize decisions and risks, while a study summary may preserve definitions and explanations.

**Important limitation:** A summary can omit important details or introduce unsupported statements. For high-impact uses, compare it with the source and validate critical facts.

<br/>

### Rewriting

**Rewriting** changes the expression of existing content while aiming to preserve its intended meaning.

Examples include:

- Making a message more concise.
- Rewriting technical prose for a nontechnical audience.
- Changing the tone of a draft from casual to formal.
- Improving grammar and readability.

A rewriting request should state what may change—such as tone, length, or reading level—and what must remain unchanged, such as facts, names, amounts, or commitments.

<br/>

### Summarization versus rewriting

| Task | Main goal | Example |
|---|---|---|
| Summarization | Reduce content while retaining key information | Turn a 10-page report into five key points |
| Rewriting | Express the same intended message differently | Rewrite a paragraph in plain language |

<br/>

## 3. Extraction, Classification, and Structured Transformation

These patterns turn unstructured content into information that an application can process.

### Extraction

**Extraction** identifies specific pieces of information in an input.

Examples:

- Extracting invoice number, date, and total from an invoice.
- Finding a customer's requested delivery date in an email.
- Extracting names and organizations from a document.

A model can help interpret varied language and formats. However, extracted values should be checked for completeness, type, and consistency. If an invoice total must be numeric, for example, the application should validate that the result is a valid number and within expected constraints.

<br/>

### Classification

**Classification** assigns an input to one or more predefined categories.

Examples:

- Assigning a support ticket to `billing`, `technical`, or `account`.
- Classifying feedback as positive, negative, or neutral.
- Routing a message to a team based on its content.

If categories are well-defined and the input follows stable rules, conventional code may be enough. A model can be useful when classification depends on context, varied wording, or nuanced meaning.

<br/>

### Structured transformation

**Structured transformation** converts content from one representation to another while following a required format.

Examples:

- Turning meeting notes into a list of decisions, owners, and deadlines.
- Converting a natural-language request into a JSON object.
- Transforming a paragraph into a table with specified fields.

A model can propose the structured result, but the application should parse and validate it before relying on it.

<br/>

### Example: extracting a support request

Input:

> “My order A-1042 arrived late. Could you tell me when the replacement will arrive?”

A model might produce:

```json
{
  "order_id": "A-1042",
  "issue_type": "late_delivery",
  "requested_information": "replacement_arrival_date"
}
```

This is an illustrative target format, not a guarantee that a model will always return valid JSON. The application should verify the syntax, required fields, and allowed category values.

<br/>

## 4. Drafting Content and Assisting with Code

### Content drafting

A model can create a first draft based on instructions, source material, and constraints.

Examples:

- Drafting an email response.
- Creating product descriptions.
- Preparing an outline for a report.
- Generating alternative headlines or explanations.

Drafting is useful when a person needs a starting point rather than a final, automatically approved result. The application can provide context, enforce format requirements, and present the draft for review.

<br/>

### Code assistance

A model can assist with software development by:

- Explaining unfamiliar code.
- Suggesting a function or implementation.
- Generating unit-test ideas.
- Helping interpret an error message.
- Refactoring code for readability.
- Drafting documentation.

Generated code may be incorrect, insecure, inefficient, or incompatible with the project. Treat it as a proposal: inspect it, run tests, review security-sensitive logic, and verify behavior before deployment.

For tasks with exact and known behavior, ordinary code is often more reliable than asking a model to generate or execute an answer from scratch.

<br/>

## 5. Question Answering and Knowledge Assistance

A question-answering application accepts a question and returns an answer. Its reliability depends partly on what information the model can access and how the application constrains the response.

### General question answering

The model responds using its learned capabilities and the context provided in the request. This can work for explanations, brainstorming, and many general questions.

However, a model may provide an answer that sounds plausible but is incorrect, incomplete, or out of date. Do not assume that fluency proves correctness.

<br/>

### Knowledge assistance using supplied information

An application can provide relevant documents or excerpts alongside a user's question. The model then answers using that supplied context.

For example:

1. The user asks, “What is our refund window?”
2. The application finds a relevant passage in the current policy document.
3. The model drafts an answer based on that passage.
4. The application presents the answer and may show the source passage.

This is a conceptual preview of **retrieval-grounded answering**. A retrieval-augmented generation (RAG) system commonly retrieves relevant information and supplies it to a model so the response can be grounded in that information. The details of building a RAG pipeline are outside this chapter's scope.

<br/>

### Why grounding matters

- It can provide information that was not included in the model's original training.
- It gives the application a specific source to check.
- It can help users inspect why an answer was produced.

Grounding does not guarantee correctness. The retrieved information may be irrelevant, incomplete, outdated, or misinterpreted. A robust application should check source relevance and make uncertainty visible when appropriate.

<br/>

## 6. Image, Speech, and Media Creation

Generative AI can work with different modalities, depending on the model's capabilities.

### Image creation

A user describes a scene or supplies other supported inputs, and an image-generation model produces an image.

Examples:

- Creating a concept image for a product.
- Producing illustrations for a presentation.
- Generating visual variations for design exploration.

Applications may need to check content requirements, output dimensions, file formats, and whether the result is suitable for the intended use.

<br/>

### Speech and audio

Audio-related applications may generate speech from text, transform audio, or work with spoken language, depending on the model.

Examples:

- Turning written text into spoken narration.
- Producing a voice response in a conversational application.
- Creating a spoken version of an explanation.

Audio applications may need checks for duration, format, intelligibility, and appropriate use.

<br/>

### Video and other media

Some models can generate or transform video and other media. Capabilities vary by model, and outputs may require processing or validation before they are usable in a product.

<br/>

### Important distinction

A model that **understands** an input modality is not necessarily able to **generate** that modality. Check the capabilities of the specific model and endpoint rather than assuming that all multimodal models support every input and output type.

<br/>

## 7. Validation, Business Rules, and Human Review

A model's response should not automatically be treated as a valid or authorized application result.

### Validation

Validation checks whether an output meets technical or content requirements.

Examples:

- Is the JSON syntactically valid?
- Are all required fields present?
- Is a date in the expected format?
- Is a category one of the allowed values?
- Does a generated file use the required format?

Validation can reject an invalid result, request a correction, or route the case for review. Valid structure does not prove that the content is factually correct.

<br/>

### Business rules

Business rules encode requirements that the application must enforce consistently.

Examples:

- A refund cannot exceed the eligible purchase amount.
- A user cannot access another customer's records.
- An order can be cancelled only while it is in an eligible state.
- A required approval must be recorded before a payment is released.

Do not rely on a model's text response to enforce authorization, financial limits, or other exact constraints. Enforce such rules in application code or the relevant authoritative system.

<br/>

### Human review

Human review is useful when a result has meaningful consequences, requires judgment, or cannot be verified reliably through automatic checks.

Examples:

- Reviewing a customer-facing response before sending it.
- Approving a legal or financial document.
- Checking a generated image before publication.
- Escalating an ambiguous or high-risk classification.

Review should be proportionate to the risk. A low-risk brainstorming draft may need little review, while a decision affecting a person's rights or finances requires much stronger controls.

<br/>

## 8. When Deterministic Code or Conventional Search Is Enough

Generative AI is not the default solution for every problem.

### Deterministic code

Use ordinary code when the task has explicit rules and requires consistent results.

Examples:

- Adding two numbers.
- Checking whether a field is empty.
- Validating an email's required fields.
- Applying a fixed discount formula.
- Enforcing access permissions.
- Sorting records by a specified column.

For these tasks, deterministic code is usually easier to test and more predictable than a generative model.

<br/>

### Conventional search

Use conventional search when the goal is to find known documents, records, or pages using exact terms, filters, or established ranking.

Examples:

- Finding an order by its unique ID.
- Filtering products by price and category.
- Searching a document repository for an exact phrase.
- Retrieving a record from a database using a key.

A generative model may be useful after retrieval—for example, to summarize several relevant documents—but it is not necessarily needed to locate a record.

<br/>

### A practical decision rule

Ask:

1. Is the task defined by exact rules?
2. Can a database query, search index, or ordinary function solve it reliably?
3. Does the task require interpreting varied language, synthesizing information, or producing flexible content?
4. What is the cost of a wrong answer?
5. How will the result be checked?

Use a model when its flexibility adds value. Use deterministic methods for exact operations, and combine the two when each has a clear role.

<br/>

## 9. A General Application Pattern

Many applications can be described using the following workflow:

1. **Input:** Receive a user request, document, image, audio clip, or record.
2. **Preparation:** Check the input, authenticate the user, and gather relevant context.
3. **Model step:** Ask the model to summarize, extract, classify, answer, draft, or generate.
4. **Validation:** Check structure, required fields, supported values, and relevant constraints.
5. **Business rules:** Apply authoritative application logic, permissions, and policy requirements.
6. **Review or escalation:** Ask a person to review the result when needed.
7. **Output or action:** Return the result, save it, or perform an authorized operation.
8. **Monitoring:** Record appropriate operational signals and track failures without exposing unnecessary sensitive data.

This is a conceptual pattern, not a mandatory sequence. A simple drafting tool may only need input, generation, and review. A higher-risk workflow may need more checks and approvals.

<br/>

## 10. Practice: Sketch One Application

Choose one application idea:

- Summarize meeting transcripts.
- Extract fields from invoices.
- Classify support tickets.
- Draft replies to customer emails.
- Answer questions using a policy document.
- Generate a product concept image.

Complete this worksheet.

| Component | Your design |
|---|---|
| User goal | What problem should the application solve? |
| Input | What information does the user provide? |
| Model role | What specific task does the model perform? |
| Validation | What technical or content checks are needed? |
| Business rules | What must be enforced by ordinary application logic? |
| Human review | When should a person approve or correct the result? |
| Output | What does the user receive, or what authorized action occurs? |
| Failure handling | What happens if the model is wrong, incomplete, or unavailable? |

<br/>

### Worked example: support-ticket classification

- **Input:** A customer's support message.
- **Model step:** Suggest a category such as `billing`, `technical`, or `account`.
- **Validation:** Confirm that the category is one of the allowed values.
- **Business rules:** Check which team is permitted to receive the ticket and apply routing rules.
- **Human review:** Escalate ambiguous or high-impact cases.
- **Output:** Assign the ticket to the appropriate queue.
- **Failure handling:** Use a safe fallback queue or request manual classification.

The model proposes a category; the application validates it and controls the routing action.

<br/>

## 11. Common Misconceptions

- **“The model is the whole application.”** Usually not. Inputs, permissions, validation, business logic, user experience, and monitoring also matter.
- **“Valid JSON means the answer is correct.”** No. Syntax and factual correctness are different checks.
- **“A model should handle every classification task.”** Stable, well-defined rules may be easier to implement with conventional code.
- **“Question answering always uses only reliable facts.”** A model can produce unsupported or incorrect answers, so important claims need suitable grounding and verification.
- **“Retrieval-grounded answers cannot be wrong.”** Retrieved sources can be poor or misinterpreted.
- **“Generated code is ready to deploy.”** It must be reviewed and tested.
- **“Every application needs a human approval step.”** Review should match the risk and purpose of the application.
- **“Multimodal means every modality is supported in both directions.”** Input and output capabilities vary by model.

<br/>

## 12. Revision Questions and Answers

**Q1. What is the difference between summarization and rewriting?**  
Summarization reduces content while preserving key information; rewriting changes how the content is expressed while aiming to preserve its intended meaning.

**Q2. What is extraction?**  
Extraction identifies specific information, such as dates, names, IDs, or amounts, in an input.

**Q3. What is classification?**  
Classification assigns an input to one or more defined categories.

**Q4. Why validate structured model output?**  
The output may be malformed, incomplete, or contain values that do not match the application's schema or constraints.

**Q5. What is retrieval-grounded question answering?**  
It supplies relevant retrieved information to a model so that the answer can be based on specific source material.

**Q6. Does retrieval guarantee a correct answer?**  
No. The source may be irrelevant or incomplete, and the model may misinterpret it.

**Q7. Why should business rules be implemented outside the model?**  
Application code and authoritative systems can enforce exact constraints and permissions consistently rather than relying on generated text.

**Q8. When is conventional search sufficient?**  
When the goal is to locate known records, documents, or pages using terms, filters, IDs, or established search methods.

**Q9. When is deterministic code preferable?**  
When a task follows explicit rules and needs predictable, testable behavior, such as arithmetic, schema checks, or permission enforcement.

**Q10. What role does the model play in a larger application?**  
It performs a defined task—such as interpreting, transforming, or generating content—while the application manages context, validation, rules, review, and outputs.

<br/>

## 13. Chapter Summary

- Common application patterns include summarization, rewriting, extraction, classification, structured transformation, drafting, coding assistance, question answering, and media creation.
- Retrieval-grounded answers use relevant source material as context, but still need appropriate source and answer checks.
- Validation checks whether an output meets technical or content constraints.
- Business rules and authorization should be enforced by application logic or authoritative systems.
- Human review is valuable when the risk, ambiguity, or need for judgment warrants it.
- Deterministic code and conventional search are often sufficient for exact, rule-based, or lookup tasks.
- The model is one component in a system—not a substitute for the entire application.

<br/>

### Final Checkpoint

For one application, describe the **input, model step, validation, business rules, human review, and output**. Explain what the model contributes and what the surrounding application must control.
