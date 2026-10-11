# Level 5: Prompt Engineering and Structured Generation

Produce more reliable model outputs through clear instructions, relevant context, examples, output constraints, and systematic testing. Learn to validate generated data and handle untrusted content without treating prompting as a guarantee of correctness or security.

This README is the plan for creating notes one by one. Keep numbered Markdown notes directly in `Level 5`, following the previous levels. The filenames below are planned files, not existing chapter links.

<br/>

## Prerequisites

- Complete [Level 4: LLM Fundamentals and Inference](<../Level 4/README.md>).
- Understand model messages, token budgets, generation settings, and common model failure modes at a high level.
- Review Python dictionaries, JSON, type hints, and basic Pydantic validation from Level 0.
- Have a way to inspect sample model outputs; paid APIs are not required.

<br/>

## Learning outcomes

After completing this level, you should be able to:

- Organize instructions and input using supported message roles and a conceptual instruction hierarchy.
- Design zero-shot, one-shot, and few-shot prompts with explicit success criteria.
- Provide relevant context, style requirements, and bounded task decomposition.
- Design schemas and validate JSON output with Pydantic.
- Build prompts for extraction, classification, summarization, transformation, and question answering.
- Version prompts and compare variants on representative test cases.
- Apply grounding and abstention techniques while documenting their limitations.
- Recognize prompt injection and separate trusted instructions from untrusted input.

<br/>

## Study order and planned note files

| Order | Planned note filename | Focus |
|---|---|---|
| 1 | `01_prompt_engineering_overview.md` | Prompt components and measurable success |
| 2 | `02_messages_and_instruction_hierarchy.md` | System/user messages, roles, and instruction priority |
| 3 | `03_clear_tasks_and_relevant_context.md` | Task definitions, context selection, and boundaries |
| 4 | `04_zero_one_and_few_shot_prompting.md` | Examples and demonstration design |
| 5 | `05_role_and_style_instructions.md` | Audience, tone, format, and consistency |
| 6 | `06_task_decomposition.md` | Explicit subtasks and bounded workflows |
| 7 | `07_structured_outputs_and_schemas.md` | Output contracts and schema-constrained generation |
| 8 | `08_json_and_pydantic_validation.md` | Parsing, validation, and failure handling |
| 9 | `09_extraction_and_classification.md` | Fields, labels, missing values, and ambiguous inputs |
| 10 | `10_summarization_and_transformation.md` | Faithful summaries and meaning-preserving changes |
| 11 | `11_question_answering_and_grounding.md` | Evidence-based answers and abstention |
| 12 | `12_prompt_iteration_and_versioning.md` | Controlled changes and reproducibility |
| 13 | `13_prompt_testing_and_comparison.md` | Representative datasets and regression checks |
| 14 | `14_hallucination_reduction_and_limits.md` | Verification, grounding, and remaining failures |
| 15 | `15_prompt_injection_and_trust_boundaries.md` | Untrusted content and defensive application design |
| 16 | `16_practice_and_revision.md` | Prompt portfolio and the level deliverable |

<br/>

## Chapter outlines

### 01. Prompt Engineering Overview

- Define prompting as specifying a task at inference time rather than updating weights.
- Identify instructions, input data, context, examples, constraints, and output requirements.
- Distinguish task quality from surface fluency and formatting.
- Introduce a baseline prompt and measurable success criteria.
- Explain why prompt quality must be tested with the selected model and task.

**Practice:** Annotate a prompt and identify missing information or ambiguous requirements.

**Checkpoint:** Describe what a successful output must do before changing the prompt.

<br/>

### 02. Messages and Instruction Hierarchy

- Introduce system, user, and assistant messages and provider-specific roles where supported.
- Distinguish application instructions, user requests, and quoted or retrieved data.
- Explain instruction priority conceptually and conflicts between instructions.
- Discuss message formatting and chat templates for supported models.
- Explain that writing role labels inside user text does not create actual privileged messages.
- Distinguish an intended instruction hierarchy from reliably enforced application authorization.

**Practice:** Place application rules, a user request, and source text into appropriate message structures.

**Checkpoint:** Explain why message roles help organize instructions but do not replace access controls.

<br/>

### 03. Clear Tasks and Relevant Context

- Specify the action, intended user, input, output, and acceptance criteria.
- Remove contradictory, vague, and unnecessary instructions.
- Select relevant context and fit it within a stated token budget.
- Identify missing information and define when to ask for clarification or abstain.
- Use consistent delimiters to mark source material and examples.
- Explain that delimiters improve clarity but are not a security barrier.

**Practice:** Rewrite an ambiguous prompt into a testable task specification.

**Checkpoint:** Separate the requested behavior from the data being processed.

<br/>

### 04. Zero-Shot, One-Shot, and Few-Shot Prompting

- Compare instructions without demonstrations, one demonstration, and several demonstrations.
- Choose examples representing expected formats, labels, and difficult cases.
- Keep examples consistent with the task instructions and schema.
- Discuss example order, diversity, token cost, and overfitting to narrow demonstrations.
- Keep evaluation examples separate from examples included in prompts.

**Practice:** Compare zero-shot, one-shot, and few-shot versions on the same held-out cases.

**Checkpoint:** Explain when examples improve performance and when they introduce misleading patterns.

<br/>

### 05. Role and Style Instructions

- Specify audience, tone, language, level of detail, and presentation format.
- Distinguish style guidance from factual or task requirements.
- Use role descriptions only when they make the expected behavior clearer.
- Explain why assigning an expert persona does not create expertise or verify claims.
- Resolve competing style constraints with explicit priorities.

**Practice:** Adapt the same explanation for a beginner and a technical reviewer while preserving its facts.

**Checkpoint:** Evaluate content accuracy separately from whether the output sounds authoritative.

<br/>

### 06. Decomposition of Complex Requests

- Divide a task into explicit, inspectable subtasks with defined inputs and outputs.
- Compare one structured request with a fixed sequence of application-controlled steps.
- Introduce intermediate artifacts such as extracted fields, outlines, or checklists.
- Validate intermediate results and discuss error propagation.
- Request concise justifications or evidence when useful, rather than assuming long reasoning text ensures correctness.
- Bound steps, retries, latency, and token use.

**Practice:** Decompose a document-to-summary task into extraction, organization, and final-output stages.

**Checkpoint:** Explain which intermediate results can be verified and where failure should stop the workflow.

**Scope boundary:** Fixed task decomposition is covered here. Autonomous planning, agent loops, and orchestration frameworks belong to the separate Agentic AI course.

<br/>

### 07. Structured Outputs and Schema-Constrained Generation

- Define an output contract before generating data.
- Compare formatting instructions, JSON syntax constraints, and schema-constrained generation.
- Specify fields, types, required values, allowed labels, and missing-data behavior.
- Introduce nested objects, lists, optional fields, and bounded values.
- Discuss supported schema subsets and model/provider differences.
- Separate schema compliance from semantic correctness.
- Account for refusals, incomplete generation, and unsupported capabilities.

**Practice:** Design a schema for extracting event details with explicit treatment of unknown dates and locations.

**Checkpoint:** Explain why valid structured output can still contain incorrect facts.

<br/>

### 08. JSON Output and Validation with Pydantic

- Distinguish a JSON string, a parsed Python object, and a validated Pydantic model.
- Define field types, enums, optional values, and constraints.
- Discuss strict validation, coercion, extra fields, and custom business-rule checks.
- Inspect malformed JSON, missing fields, incorrect types, and unsupported values.
- Handle errors through bounded retries, rejection, or human review.
- Preserve original inputs and errors for debugging without logging sensitive data.
- Treat generated text and code as untrusted data; never execute it merely to parse it.

**Practice:** Validate prepared outputs containing syntax errors, schema errors, and semantically incorrect values.

**Checkpoint:** Distinguish parsing success, schema validity, and application-level correctness.

**Depth boundary:** Provider SDK calls and structured-output API integration belong to Level 6. Verify the installed Pydantic version when writing code examples.

<br/>

### 09. Extraction and Classification

- Define extraction fields and whether exact source text or normalized values are required.
- Preserve evidence spans where helpful.
- Define a label set with inclusion criteria and ambiguous-case handling.
- Specify unknown, missing, or not-applicable values without inventing data.
- Handle multiple entities, conflicting statements, and mixed-category inputs.
- Evaluate field accuracy and label accuracy separately from output validity.

**Practice:** Create extraction and classification prompts for synthetic support messages, including incomplete examples.

**Checkpoint:** Explain how the prompt and schema prevent forced guesses without guaranteeing perfect extraction.

<br/>

### 10. Summarization and Transformation

- Define summary audience, scope, length, and required coverage.
- Preserve important facts, qualifications, disagreements, and source uncertainty.
- Compare summarization with rewriting, translation, reformatting, and other transformations.
- Specify information that must remain unchanged, such as identifiers and numbers.
- Handle content exceeding the available context using a bounded staged approach.
- Check omissions, unsupported additions, and changed meaning.

**Practice:** Produce a summary and a style transformation of the same source using separate rubrics.

**Checkpoint:** Distinguish concision from fidelity to the original content.

<br/>

### 11. Question Answering and Grounding

- Compare general-knowledge answers with answers restricted to supplied evidence.
- Define allowed sources and how to cite available source identifiers.
- Handle missing, conflicting, outdated, or irrelevant evidence.
- Require abstention or clarification when the evidence is insufficient.
- Verify whether a citation supports the associated claim.
- Preview retrieval-grounded prompting without implementing a RAG pipeline.

**Practice:** Answer questions from a short source packet, including unanswerable questions and conflicting sources.

**Checkpoint:** Separate having a citation from having evidence that supports the answer.

<br/>

### 12. Prompt Iteration and Versioning

- Start with a baseline and categorize observed failures.
- Change a defined aspect of the prompt and record the hypothesis.
- Store prompt templates, schemas, examples, and model settings together.
- Record version identifiers, dates, model identifiers, and relevant environment details.
- Compare improvements and regressions before accepting a new version.
- Avoid tuning repeatedly on the final held-out test set.

**Practice:** Create a prompt changelog explaining one revision and its measured effects.

**Checkpoint:** Reproduce a prior comparison from recorded prompts, settings, and test cases.

<br/>

### 13. Prompt Testing with Representative Examples

- Build a small dataset with typical, edge, ambiguous, missing-data, and adversarial inputs.
- Define expected fields, labels, facts, or evaluation rubrics.
- Measure schema validity separately from task-specific quality.
- Repeat selected cases to inspect output variability.
- Compare token usage, latency, and cost where available.
- Use regression checks to retain previously successful behavior.
- Introduce human review and limitations of automated model-based judgments.

**Practice:** Compare two prompt variants on the same held-out examples and document failure categories.

**Checkpoint:** Explain why a few selected successful outputs are insufficient evidence of improvement.

**Depth boundary:** Larger evaluation suites, judge calibration, statistical comparisons, and CI/CD gates are developed systematically in Level 13.

<br/>

### 14. Hallucination Reduction and Its Limitations

- Improve input completeness and clarify what evidence may be used.
- Ground answers in relevant material and require supported attribution.
- Allow unknown values, abstention, and clarification.
- Verify facts, calculations, identifiers, and output constraints with independent checks where possible.
- Discuss why lower temperature, expert personas, and self-review alone do not guarantee truthfulness.
- Recognize that grounding can fail when sources are incorrect or the model misuses them.
- Document residual risk and human-review requirements.

**Practice:** Compare an unconstrained answer with an evidence-restricted answer, then verify both against the source.

**Checkpoint:** Match each proposed mitigation to a specific failure rather than claiming to eliminate hallucinations.

<br/>

### 15. Prompt Injection and Trust Boundaries

- Define direct and indirect prompt injection through user input, documents, and retrieved content.
- Identify content that attempts to override instructions, reveal sensitive information, or redirect the task.
- Separate trusted instructions from untrusted text using message structure and clear data boundaries.
- Keep authorization, secret handling, and permitted actions in application logic.
- Validate outputs before downstream use and limit privileges and capabilities.
- Explain why delimiters, warning prompts, and schema constraints are incomplete defenses.
- Test malicious source text while preserving legitimate task behavior.

**Practice:** Create synthetic documents containing injection attempts and evaluate whether a summarization or extraction prompt remains on task.

**Checkpoint:** Explain which protections require application controls beyond the prompt.

**Depth boundary:** Threat modeling, tenant isolation, access-control testing, and broader security controls belong to Level 14. Basic application-controlled tool calling is covered in Level 6.

<br/>

### 16. Practice and Revision

- Build extraction, classification, summarization, transformation, and evidence-based question-answering prompts.
- Compare prompting with and without examples.
- Validate JSON outputs with Pydantic and independent business rules.
- Review decomposition, versioning, hallucination mitigation, and trust boundaries.
- Compare prompt variants with fixed test cases.
- Complete the prompt portfolio below.

**Checkpoint:** Explain why each prompt is structured as it is and support improvements with results.

<br/>

## Level deliverable: Tested prompt portfolio

Create `prompt_portfolio.md` in this folder, with supporting schemas and example data as needed. Include:

1. Five task prompts: extraction, classification, summarization, transformation, and evidence-based question answering.
2. Input assumptions, message roles, output requirements, and success criteria for each task.
3. A structured-output schema and Pydantic validation example for at least one task.
4. At least five held-out cases per task, including a relevant edge or missing-information case.
5. Separate synthetic injection tests for tasks that process untrusted source text.
6. A baseline-versus-revised prompt comparison on the same cases, with repeated runs for selected inputs.
7. Task-quality results, schema-validity results, and latency/token/cost measurements where available.
8. A version log recording prompts, examples, schemas, model identifiers, settings, and dates.
9. Observed failures, mitigations, remaining risks, and a recommendation for the preferred variants.

Use public or synthetic data. A small local model or an available hosted service is sufficient; paid APIs are not required. Prepared outputs may be used to practice validation, but label them clearly and do not present them as measured model performance.

<br/>

## Suggested format for each note

1. Learning objectives and prerequisite concepts.
2. Why the technique matters and when to use it.
3. A baseline prompt and a worked improvement.
4. Expected outputs, schema, or evaluation rubric.
5. Representative successes and failure examples.
6. Trade-offs, misconceptions, and remaining limitations.
7. Exercise and revision questions with answers.
8. References and optional extensions.

Verify supported message roles, schema features, SDK behavior, and Pydantic syntax when writing implementation notes. Keep test inputs separate from demonstrations embedded in prompts.

<br/>

## Completion checklist

- [ ] Organize messages and explain instruction priority conceptually.
- [ ] Define clear tasks and separate instructions from input data.
- [ ] Compare zero-shot, one-shot, and few-shot prompts.
- [ ] Specify role, audience, and style without confusing authority with accuracy.
- [ ] Decompose a complex request into bounded, inspectable steps.
- [ ] Design a structured-output schema with explicit missing-data behavior.
- [ ] Parse and validate JSON with Pydantic and business-rule checks.
- [ ] Build prompts for all five application task types.
- [ ] Version prompts and compare variants using representative held-out cases.
- [ ] Apply grounding and abstention while documenting remaining failures.
- [ ] Recognize prompt injection and explain application-level trust controls.
- [ ] Complete and review the tested prompt portfolio.

<br/>

## Scope and next step

This level develops prompt design, structured generation, validation, and small-scale testing. Provider API implementation belongs to Level 6; full RAG systems to Level 8; fine-tuning to Level 12; systematic evaluation to Level 13; and comprehensive security engineering to Level 14.

Autonomous agents, multi-agent systems, and agent orchestration remain part of the separate Agentic AI course.

Next: **Level 6 — LLM APIs and Application Development** in the [main course outline](../README.md).
