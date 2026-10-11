# 05. Role and Style Instructions

## Learning Objectives

By the end of this chapter, you should be able to:

- Specify the intended audience, tone, language, level of detail, and presentation format.
- Distinguish style guidance from factual requirements and task requirements.
- Use role descriptions when they clarify the expected behavior.
- Explain why an expert persona does not create expertise or verify claims.
- Resolve competing style constraints by setting explicit priorities.
- Adapt the same explanation for different audiences while preserving its factual content.

<br/>

## 1. What Are Role and Style Instructions?

**Style instructions** describe how a response should be communicated. They can specify tone, language, detail level, organization, and presentation format.

**Role instructions** describe a perspective or function the model should adopt for a task, such as explaining a concept as a patient tutor or reviewing a design from a software engineer's perspective.

These instructions can make the expected response clearer. They do not change the model's underlying knowledge, guarantee expertise, or establish that a claim is true.

For reliable prompts, specify the task and factual requirements first, then add role and style guidance that helps the model present the result appropriately.

<br/>

## 2. The Main Dimensions of Style

| Dimension | What to specify | Example |
|---|---|---|
| **Audience** | Who will read the response | A beginner learning machine learning |
| **Tone** | The communication style | Neutral, supportive, formal, or conversational |
| **Language** | The desired language or locale | English, using standard technical terminology |
| **Level of detail** | How much explanation is needed | A short overview with one worked example |
| **Presentation format** | How information should be organized | Headings, a table, numbered steps, or bullet points |
| **Terminology** | Whether to use technical language and how to explain it | Define each technical term at first use |
| **Length** | A useful target or limit | 4–6 bullet points, or fewer than 300 words |

Choose dimensions that matter for the task. Adding every possible style instruction to every prompt can make it longer without improving the result.

<br/>

### Example: a general style specification

```text
Audience: Beginner Python developers
Tone: Clear and supportive
Language: English
Detail level: Introductory, with one practical example
Format: Short headings followed by bullet points
Terminology: Explain unfamiliar technical terms on first use
```

This style specification says how to communicate, but it does not define the actual task. The prompt still needs to state what the model should explain, analyze, or produce.

<br/>

## 3. Distinguish Style from Task and Factual Requirements

A prompt often contains three different kinds of requirements:

1. **Task requirements:** What the model must do.
2. **Factual or evidence requirements:** What claims are allowed and what information must be preserved.
3. **Style requirements:** How the response should be presented.

These categories are related, but they should not be confused.

| Requirement type | Example | How to evaluate it |
|---|---|---|
| Task | Explain how an embedding represents text | Does the answer explain the concept requested? |
| Factual/evidence | Do not claim that embeddings understand text exactly like humans | Are the claims accurate and appropriately qualified? |
| Style | Explain for a beginner using a simple analogy | Is the explanation accessible and does it use an appropriate analogy? |
| Format | Use two sections and one example | Does the output follow the requested structure? |

A response can meet the style requirements and still fail the task. For example, a friendly, well-organized explanation may contain a false definition. Conversely, a technically correct answer may be too dense for its intended audience.

Evaluate these dimensions separately.

<br/>

## 4. Role Descriptions: When They Help

A role description can provide a useful perspective or clarify the expected function.

Examples:

```text
Act as a patient tutor. Explain gradient descent to a beginner,
using a small numerical example.
```

```text
Review the following API design from the perspective of a
backend engineer. Identify reliability risks, validation gaps,
and unclear error-handling behavior.
```

The role is useful because it points toward a particular communication or review approach. The task itself remains explicit: explain gradient descent or review an API design.

<br/>

### Avoid role-only prompts

Weak:

```text
You are a world-class AI expert. Help me.
```

The prompt does not identify the problem, input, intended output, or success criteria.

Improved:

```text
Explain the difference between embeddings and one-hot vectors
for a beginner who knows basic Python. Use a comparison table
and one small example. Distinguish what the representation
encodes from what it does not guarantee.
```

The improved prompt defines the task and output requirements. A role could be added if it provides further clarity, but it is not a substitute for a specific request.

<br/>

## 5. An Expert Persona Does Not Create Expertise

Telling a model to act as an expert may influence tone, terminology, structure, or the type of considerations it discusses. It does not:

- Add verified knowledge to the model.
- Guarantee that the response is correct.
- Ensure that the model has current information.
- Replace source checking, calculations, or tests.
- Establish professional credentials or accountability.
- Make unsupported claims reliable merely because they sound confident.

For example:

```text
Act as a senior security engineer and explain the risks in this design.
```

This may encourage a security-oriented review. But the resulting analysis still needs to be checked against the design, security requirements, and relevant evidence.

A safer and more testable formulation is:

```text
Review this design for authentication, authorization, input
validation, secret handling, and logging risks. For each finding,
cite the relevant design detail, explain the potential impact,
and mark uncertain conclusions as unverified.
```

The second prompt specifies review criteria and evidence expectations instead of relying on an authoritative persona.

**Practical rule:** Use role descriptions to guide the response's perspective; use explicit requirements and verification to assess its correctness.

<br/>

## 6. Resolve Competing Style Constraints

Style requirements can conflict. Some conflicts are obvious; others arise when the desired audience, detail level, and length do not fit together.

Examples:

- “Explain every implementation detail” and “Use no more than 50 words.”
- “Use only plain language” and “Preserve all formal mathematical notation.”
- “Be highly conversational” and “Write in a strict legal-memorandum format.”
- “Include all edge cases” and “Give only the main conclusion.”

<br/>

### Ways to resolve conflicts

1. **Set priorities:** State which requirement takes precedence.
2. **Narrow the scope:** Explain the core idea rather than every implementation detail.
3. **Use layered output:** Provide a short summary first, followed by technical details if allowed.
4. **Clarify the intended trade-off:** Ask the user when the conflict materially changes the desired result.
5. **Define a fallback:** For example, prioritize factual completeness over a strict word target when omitting information would be misleading.

Example:

```text
Write for a beginner in no more than 250 words.
Priorities:
1. Preserve technical accuracy.
2. Explain essential terminology in plain language.
3. Keep the answer concise.
Omit advanced implementation details rather than oversimplifying
or making unsupported claims.
```

This makes the intended trade-off explicit.

<br/>

## 7. Worked Example: Same Facts, Different Audiences

Suppose the core fact to communicate is:

> An embedding model maps an input, such as text, to a numerical vector. Similarity between vectors can be used to find semantically related items, depending on the model and similarity measure. The representation does not guarantee that the model has understood every nuance of the input.

The audience and style can change while these facts remain intact.

### Version A: Beginner

**Prompt**

```text
Explain embeddings to a beginner who knows basic Python.
Use plain language, one analogy, and no more than three bullet points.
Preserve the limitations in the supplied facts.

Facts:
<<<FACTS
An embedding model maps an input, such as text, to a numerical
vector. Similarity between vectors can be used to find semantically
related items, depending on the model and similarity measure.
The representation does not guarantee that the model has understood
every nuance of the input.
<<<END_FACTS
```

**Illustrative output**

- An **embedding** turns text into a list of numbers called a vector.
- You can compare these vectors to find text that is related in meaning, much like comparing coordinates on a map. The result depends on the model and the comparison method.
- Similar vectors do not prove that the system has understood every detail or nuance of the text.

<br/>

### Version B: Technical reviewer

**Prompt**

```text
Explain embeddings for a technical reviewer familiar with Python
and machine learning. Use precise terminology and three concise
bullet points. Preserve all qualifications in the supplied facts.

Facts:
<<<FACTS
An embedding model maps an input, such as text, to a numerical
vector. Similarity between vectors can be used to find semantically
related items, depending on the model and similarity measure.
The representation does not guarantee that the model has understood
every nuance of the input.
<<<END_FACTS
```

**Illustrative output**

- An embedding model maps an input to a vector in a learned representation space.
- A similarity function, such as cosine similarity or dot product when appropriate, can rank vectors for semantic retrieval; behavior depends on the embedding model and scoring method.
- Vector proximity is a retrieval signal, not proof of complete semantic understanding or preservation of every nuance.

The second version uses more technical vocabulary, but the underlying claims and qualifications remain aligned. The example outputs are illustrative; they are not measured results from a model run.

<br/>

## 8. Evaluate Accuracy Separately from Style

A useful review process asks two independent questions:

**Content review**
- Does the response answer the actual question?
- Are its factual claims supported?
- Does it preserve necessary qualifications?
- Does it distinguish known information from assumptions?
- Does it invent evidence or overstate certainty?

**Style and format review**
- Is the language appropriate for the audience?
- Is the tone suitable?
- Is the detail level appropriate?
- Is the requested structure followed?
- Are terminology and examples understandable?

A response should not receive a high correctness score merely because it sounds authoritative. Likewise, awkward wording does not necessarily make a factually correct response wrong, although it can reduce usability.

For important tasks, use separate criteria or scores for content accuracy, completeness, style, and format compliance.

<br/>

## 9. Practice: Adapt an Explanation for Two Audiences

### Source facts

Use the following facts as the fixed content:

> A vector database stores vector representations and supports similarity search. Applications may attach metadata to vectors and filter results using that metadata. Retrieval quality depends on factors such as the embedding model, indexed content, similarity method, and search configuration.

<br/>

### Task A: Beginner

Write a prompt that requests:
- A beginner-friendly explanation.
- Plain language and one analogy.
- No more than three bullet points.
- All source facts preserved, including the limitations.

<br/>

### Task B: Technical reviewer

Write a prompt that requests:
- A technically precise explanation for a software engineer.
- Three concise bullet points.
- Explicit mention of metadata filtering and retrieval-quality dependencies.
- No unsupported claims about guaranteed relevance.

<br/>

### Review checklist

Compare the two outputs and verify:

- [ ] Both explain the same core function of a vector database.
- [ ] Both preserve the role of metadata filtering.
- [ ] Both retain the stated retrieval-quality dependencies.
- [ ] Neither claims that similarity search guarantees correct or relevant results.
- [ ] Vocabulary and explanation depth differ appropriately for the audience.
- [ ] Each output follows its requested format.

The wording should change to suit the audience; the facts should not change merely to sound more impressive.

<br/>

## 10. Common Mistakes

| Mistake | Why it matters | Better practice |
|---|---|---|
| Giving a persona but no task | The requested action remains unclear | State the task, input, and output explicitly |
| Assuming an expert persona guarantees accuracy | Authority in the wording can hide errors | Verify claims independently |
| Mixing style and factual requirements | A polished response may be mistaken for a correct one | Evaluate content and style separately |
| Asking for incompatible styles | The model must guess which requirement matters more | Set priorities or narrow the scope |
| Using vague style words alone | “Detailed” or “professional” can mean different things | Define length, structure, audience, and terminology |
| Changing facts to simplify an explanation | The output may become misleading | Simplify wording without removing essential qualifications |
| Overloading every prompt with style rules | Extra instructions can add noise | Include only style requirements that improve usability |


<br/>


## 11. Revision Questions

### Q1. What are common dimensions of style instructions?

**Answer:** Audience, tone, language, detail level, presentation format, terminology, and length.

### Q2. How do style requirements differ from task requirements?

**Answer:** Task requirements specify what the model must do. Style requirements specify how the result should be communicated.

### Q3. Does asking a model to act as an expert make its answer correct?

**Answer:** No. It may influence perspective or presentation, but correctness still depends on the task, available information, model behavior, and verification.

### Q4. Why should content accuracy and style be evaluated separately?

**Answer:** A response can be clear and authoritative while factually wrong, or factually correct while poorly suited to the audience. Separate evaluation identifies these different failure types.

### Q5. How can competing style constraints be resolved?

**Answer:** Set explicit priorities, narrow the scope, use a layered response, define a fallback, or ask for clarification when the trade-off materially affects the result.

### Q6. How can you simplify an explanation without changing its facts?

**Answer:** Change vocabulary, examples, organization, and assumed background knowledge while preserving the original claims, qualifications, and limitations.


<br/>


## 12. Chapter Checkpoint

**Question:** How should you evaluate content accuracy separately from whether an output sounds authoritative?

**Answer:** Check factual claims against reliable evidence or the supplied source, verify that the response answers the task, and confirm that qualifications and uncertainty are preserved. Separately evaluate tone, terminology, audience fit, and format. An expert persona or confident style is not evidence of correctness.


<br/>


## Key Takeaways

- Specify audience, tone, language, detail level, and format when they matter.
- Keep task requirements, factual constraints, and style guidance distinct.
- Role descriptions are useful when they clarify the desired perspective or function.
- An expert persona does not create expertise or verify claims.
- Resolve competing style constraints by defining priorities.
- Adapt wording and detail to the audience while preserving facts and qualifications.
- Evaluate content correctness independently from tone and presentation.

<br/>

## References and Further Reading

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) — guidance on communicating desired model behavior.
- [OpenAI Model Spec](https://model-spec.openai.com/) — broader context for intended assistant behavior and instruction handling.
- [Level 5 course outline](README.md) — chapter scope, practice, and checkpoint.
