# 10. Model and Use-Case Selection

## Learning Objectives

By the end of this chapter, you should be able to:

- Define the user, problem, and success criteria before selecting a model.
- Identify the task, required modalities, context needs, and output constraints.
- Compare candidates across quality, latency, cost, hardware, privacy, and licensing.
- Choose a suitable model category and access or deployment approach.
- Evaluate candidates using representative examples and a simple rubric.
- Consider a conventional software baseline before choosing a generative model.
- Record assumptions, trade-offs, and situations requiring human review.

<br/>

## 1. Why This Topic Matters

Selecting a model is an engineering decision, not a popularity contest. A widely discussed model may be a poor fit for a particular application if it is too slow, too expensive, difficult to deploy, restricted by its license, or unreliable on the task that matters.

Start with the application requirements. Then identify suitable model categories, shortlist candidates, and evaluate them using representative inputs. The best choice is the one that meets the requirements at an acceptable cost and risk—not necessarily the largest, newest, or most popular model.

A useful selection process is:

**Define the problem → Set success criteria → Identify constraints → Establish a baseline → Compare candidates → Record the decision → Re-evaluate when requirements change**

<br/>

## 2. Define the User and Problem First

Before comparing models, describe the application in plain language.

Answer these questions:

1. **Who is the user?** For example, a customer support agent, analyst, student, or internal employee.
2. **What problem are they trying to solve?** Describe the current difficulty rather than starting with a preferred technology.
3. **What input will the application receive?** Examples include text, documents, images, audio, or structured records.
4. **What output is required?** For example, a summary, category label, JSON object, answer, draft, or generated image.
5. **What happens after the output?** Is it displayed to a person, saved, checked, or used to trigger an action?
6. **What happens when the model is wrong or unavailable?** Define a fallback or escalation path.

<br/>

### Example: support-ticket triage

A vague goal might be: “Use an advanced AI model for support.”

A clearer problem statement is:

> Help the support team assign incoming tickets to the correct queue by suggesting one of four approved categories. The application must validate the category and route uncertain cases for human review.

The clearer statement identifies the user, task, output, constraints, and need for review. Those details make model selection and evaluation more concrete.

<br/>

## 3. Define Success Criteria

Success criteria describe what a suitable solution must achieve. They should be measurable where possible.

Examples include:

- Correctness on a representative test set.
- Valid structured output.
- Acceptable response time.
- Cost per request or per completed task.
- Ability to handle the required input length or modality.
- Compliance with data-handling requirements.
- Sufficient performance on important edge cases.
- A manageable rate of cases requiring human review.

Distinguish **must-have requirements** from **preferences**.

| Type | Example |
|---|---|
| Must-have | Must return a valid category from a fixed set |
| Must-have | Must not send restricted data to an unapproved service |
| Must-have | Must respond within a defined latency limit |
| Preference | Prefer simpler integration |
| Preference | Prefer lower average cost when quality is comparable |
| Preference | Prefer a model with convenient development tooling |

Some requirements are hard constraints: a candidate that violates them should be excluded even if it scores well elsewhere.

<br/>

## 4. Identify the Task and Technical Requirements

A model's suitability depends on what the application actually needs to do.

### Task category

Identify whether the application needs to:

- Summarize or rewrite text.
- Extract fields from documents.
- Classify or route inputs.
- Answer questions using supplied context.
- Draft content or assist with code.
- Generate images, speech, or other media.
- Understand inputs from multiple modalities.

A task may combine several steps. For example, a document assistant may need to extract fields, validate them, and summarize the result. Do not assume one model must handle every step.

<br/>

### Modalities

Identify the input and output modalities separately.

- Text input and text output.
- Image input and text output.
- Text input and image output.
- Audio input and text or audio output.
- Video input and text output.
- Multiple input or output modalities.

Verify that the specific model and service support the exact combination required. “Multimodal” does not guarantee every modality or direction is available.

<br/>

### Context needs

Determine what information the model must use:

- The current user request.
- Conversation history.
- Long documents or multiple documents.
- Retrieved records or policy excerpts.
- Current application data.
- Structured fields supplied by other systems.

If an application needs current or private information, determine how that information will be retrieved, authorized, and passed to the model. Do not assume the model already knows it.

<br/>

### Output constraints

List the requirements for the response:

- Plain text, a fixed schema, JSON, code, or a media file.
- Required fields and allowed values.
- Maximum length or format.
- Required citations or source references.
- Whether the output is a suggestion or may lead to an action.

Output constraints affect both candidate selection and the validation the application must implement.

<br/>

## 5. Consider the Main Selection Factors

### Quality

Does the candidate perform the required task correctly on representative examples? Evaluate the dimensions that matter for the application, such as factual accuracy, classification performance, instruction-following, extraction quality, or output validity.

<br/>

### Latency

How long does the user wait for a result? Measure response time under realistic input sizes and usage patterns. Average latency may hide slow responses, so consider tail latency when it matters.

<br/>

### Cost

Estimate the cost of completing the task, not just the cost of a single model call. Include relevant input and output usage, repeated attempts, supporting services, and human review.

<br/>

### Hardware and operational effort

For self-managed models, assess memory, compute, storage, throughput, deployment complexity, and the team's ability to operate the system. For hosted services, consider integration effort, rate limits, provider dependency, and service constraints.

<br/>

### Privacy and data handling

Determine which data may be sent to a provider, what must remain in a controlled environment, and which logging, retention, access, and contractual requirements apply.

<br/>

### Licensing and permitted use

Verify the actual license and service terms for the intended use. Check commercial-use conditions, redistribution, modification, and any relevant restrictions. Do not infer usage rights from a model's popularity or from the availability of downloadable weights.

<br/>

### Reliability and safety

Consider known limitations, failure modes, uncertainty handling, prompt-injection exposure, and the consequences of an incorrect result. Decide where validation and human review are required.

<br/>

### Practical comparison table

| Factor | Questions to ask |
|---|---|
| Quality | Does it meet the task-specific success criteria? |
| Latency | Is it fast enough under realistic conditions? |
| Cost | What is the estimated total cost per completed task? |
| Hardware | Can the required environment run it reliably? |
| Privacy | Is the data flow acceptable for the application? |
| Licensing | Are the intended uses permitted? |
| Reliability | How does it fail, and how will failures be handled? |
| Integration | Can the team maintain the solution? |

<br/>

## 6. Choose a Model Category and Access Approach

At this stage, choose a category before settling on a specific model name.

### General-purpose language model

Consider this category when the application needs flexible language understanding, drafting, summarization, or multiple related text tasks.

Potential trade-offs include cost, latency, variability, and the need for careful output validation.

<br/>

### Multimodal model

Consider this category when the application must understand or generate a supported combination of text, image, audio, video, or other media. Confirm the exact modality support and output constraints.

<br/>

### Task-specific model

Consider a specialized classifier, extractor, or other task-specific model when the task is narrow, evaluation criteria are clear, and a specialized approach can meet the requirements with less complexity or cost.

A task-specific model may be sufficient for a fixed classification problem where a general-purpose model would add unnecessary flexibility.

<br/>

### Conventional software

Consider deterministic code, database queries, or conventional search when the task follows explicit rules or involves retrieving known records. A model may not add enough value to justify its cost and variability.

<br/>

### Access and deployment approach

After identifying a suitable model category, consider how to access and operate it:

- **Hosted API:** Often convenient for prototypes and applications that benefit from managed inference.
- **Self-managed inference:** May provide greater control over deployment and data flow, but adds operational responsibilities.
- **Local inference:** May suit constrained or offline environments if hardware and model capability are sufficient.

Access method and deployment location should be evaluated against requirements. Also check licensing separately; an open-weight model can be accessed through a hosted service, and downloadable weights may still have usage restrictions.

<br/>

## 7. Establish a Conventional Baseline

Before selecting a generative model, ask whether a simpler solution can solve the problem.

Possible baselines include:

- A database query or exact lookup.
- Keyword or conventional search.
- A set of deterministic rules.
- A conventional machine-learning classifier.
- A fixed template or form.
- A human-only workflow.

<br/>

### Why a baseline matters

A baseline gives you something concrete to compare against. It can show whether the model improves quality, reduces work, or handles cases that the simpler method cannot.

For example, a ticket classifier based on a few stable labels may work adequately with conventional rules or a smaller classification model. If tickets use varied language and require contextual interpretation, a language model may improve performance. The decision should be based on observed results.

A more complex solution is not automatically a better solution.

<br/>

## 8. Compare Candidates Using Representative Examples

Do not select a model based only on demonstrations, general benchmarks, or reputation. Test the candidates on examples that resemble the real application.

### Build a representative test set

Include:

- Common, ordinary inputs.
- Ambiguous or incomplete requests.
- Longer or unusually formatted inputs.
- Relevant edge cases.
- Inputs likely to trigger known failure modes.
- Examples that reflect the intended users, languages, and operating conditions.

Use data that you are permitted to process. Avoid exposing sensitive information unnecessarily, and keep a separate evaluation set where appropriate so repeated tuning does not simply optimize for the same examples.

<br/>

### Use the same evaluation conditions

Where possible, compare candidates using the same inputs, success criteria, and realistic constraints. Record relevant model identifiers, settings, timestamps, and costs. If a candidate requires different configuration, document the difference rather than hiding it.

<br/>

### A simple evaluation rubric

Score each dimension from 1 to 5, where 1 means poor and 5 means excellent. Define the scoring rules before evaluating candidates.

| Dimension | What to assess |
|---|---|
| Task quality | Correctness and usefulness on the test set |
| Instruction-following | Compliance with required behavior and constraints |
| Output validity | Correct structure and required fields |
| Latency | Response time under the intended workload |
| Cost | Estimated cost per completed task |
| Integration effort | Work needed to build and maintain the solution |
| Risk fit | Ability to meet privacy, safety, and review requirements |

Not every dimension should have equal weight. For example, a privacy requirement may be a hard constraint rather than a score to trade against quality.

<br/>

### Example scorecard

The following values are **illustrative only**, not benchmark results for actual models.

| Dimension | Candidate A | Candidate B |
|---|---:|---:|
| Task quality | 4 | 5 |
| Instruction-following | 4 | 4 |
| Output validity | 5 | 4 |
| Latency | 5 | 3 |
| Cost | 5 | 3 |
| Integration effort | 5 | 3 |
| Risk fit | Pass | Pass |

Candidate B has a higher illustrative task-quality score, while Candidate A has lower latency, cost, and integration effort. Which is better depends on the requirements. If Candidate A already meets the required quality threshold, Candidate B's additional quality may not justify its trade-offs. If the task-quality threshold is higher than Candidate A can meet, Candidate B may be the more suitable choice.

The point is not to pick the candidate with the highest total. It is to make trade-offs explicit and respect hard constraints.

<br/>

## 9. Practice: Recommend a Model Category for Three Scenarios

For each scenario, recommend a model category, an access approach, and a verification plan. These are example recommendations to guide your reasoning; the final choice should depend on observed results and actual constraints.

### Scenario A — Summarizing non-sensitive meeting notes

**Requirements:** The team wants readable summaries and action-item drafts. Traffic is low and unpredictable. The goal is to validate a prototype quickly.

**Reasonable starting point:**
- **Model category:** General-purpose language model.
- **Access approach:** Hosted API.
- **Why:** It can handle flexible summarization and drafting without requiring the team to operate model-serving hardware.
- **Checks:** Compare summaries with source notes, validate action-item structure, estimate cost and latency, and keep a human review step before publishing important decisions.
- **Reconsider if:** Usage becomes high and predictable, provider terms are unsuitable, or a smaller specialized approach meets the requirements more efficiently.

<br/>

### Scenario B — Routing support tickets into fixed categories

**Requirements:** Each ticket must be assigned one of five allowed categories. The system needs predictable output and low operating cost.

**Reasonable starting point:**
- **Model category:** Begin with a conventional rules-based or task-specific classification baseline; evaluate a general-purpose language model if context and varied wording make the baseline insufficient.
- **Access approach:** Choose hosted or self-managed inference based on measured traffic, latency, data-handling requirements, and operating capacity.
- **Why:** The task has a constrained output, so a simpler classifier may be enough. A more flexible model should justify its extra cost and complexity through better measured performance.
- **Checks:** Evaluate classification metrics on representative tickets, inspect errors by category, validate labels, and send ambiguous cases to a fallback queue or human reviewer.
- **Reconsider if:** The task expands to nuanced summaries or complex multi-step interpretation.

<br/>

### Scenario C — Answering questions about sensitive internal policies

**Requirements:** Employees ask questions about internal policies. Answers must use current approved documents, and access to confidential material must be controlled.

**Reasonable starting point:**
- **Model category:** A language model paired with retrieval of authorized policy passages.
- **Access approach:** Compare approved hosted services with self-managed deployment according to the organization's data-handling and contractual requirements.
- **Why:** The model can phrase an answer, while the retrieval step supplies current source material. The application must enforce document permissions and validate the relevance of retrieved passages.
- **Checks:** Test whether answers are supported by the cited policy, verify source freshness, enforce authorization outside the prompt, and abstain or escalate when evidence is missing.
- **Reconsider if:** Retrieval quality is poor, the model misrepresents policy, or the required data controls cannot be met.

<br/>

### Practice worksheet

| Scenario | Model category | Access approach | Main reason | Evaluation and safeguards |
|---|---|---|---|---|
| A — Meeting summaries |  |  |  |  |
| B — Ticket routing |  |  |  |  |
| C — Sensitive policy Q&A |  |  |  |  |

For each recommendation, write down at least one assumption and one trade-off.

<br/>

## 10. Record the Decision

A short decision record makes the reasoning clear and helps the team revisit the choice when requirements change.

Include:

- **Problem and users:** What is the application for, and who relies on it?
- **Requirements:** Which quality, latency, cost, privacy, licensing, and output constraints are mandatory?
- **Candidates considered:** Which model categories, specific models, and non-model baselines were evaluated?
- **Evaluation evidence:** What representative examples, metrics, and observed errors informed the choice?
- **Trade-offs:** What was gained and what was sacrificed?
- **Assumptions:** Which estimates or conditions have not yet been verified?
- **Human review:** Which outputs require approval, and what triggers escalation?
- **Residual risks:** What could still go wrong?
- **Reassessment triggers:** Which changes—such as model updates, new users, increased traffic, or new data types—require re-evaluation?

<br/>

### Example decision statement

> We selected a hosted general-purpose language model for the prototype because it met the required summary-quality threshold on our test set, was quick to integrate, and avoided operating model-serving infrastructure. The application validates the requested output format and requires review before summaries are used as official meeting records. We have not yet tested peak traffic or long-term cost, so we will reassess the choice before broad deployment.

This statement links the recommendation to requirements and evidence while making assumptions and limitations explicit.

<br/>

## 11. Common Misconceptions

- **“The most popular model is the best choice.”** Popularity does not establish suitability for your task.
- **“The largest model always performs best for the application.”** A smaller or specialized solution may meet the requirements with less cost and complexity.
- **“A public benchmark settles the decision.”** General benchmarks may not represent your users, data, or constraints.
- **“Quality is the only selection factor.”** Latency, cost, privacy, licensing, hardware, and operational capacity also matter.
- **“A hosted API is always cheaper.”** Cost depends on usage, pricing, integration, and the alternative's total operating cost.
- **“Self-hosting is always more private.”** Privacy depends on the full data flow, controls, and operational practices.
- **“A high rubric total overrides a hard constraint.”** Candidates that violate mandatory requirements should be excluded.
- **“A generative model is required for every AI-related task.”** Rules, search, databases, and conventional classifiers may be sufficient.
- **“One successful example proves the candidate is suitable.”** Selection requires representative evaluation and attention to failure modes.
- **“The decision is permanent.”** Reassess when models, requirements, data, usage, or operating conditions change.

<br/>

## 12. Revision Questions and Answers

**Q1. What should be defined before selecting a model?**  
The user, problem, required input and output, success criteria, constraints, and what happens when the result is wrong or unavailable.

**Q2. Why define success criteria in advance?**  
They make comparisons measurable and reduce the risk of selecting a model based on impressive but irrelevant demonstrations.

**Q3. Which factors should be considered besides quality?**  
Latency, cost, hardware, privacy, licensing, reliability, integration effort, and operational requirements.

**Q4. Why identify input and output modalities separately?**  
A model may support one modality as input without supporting it as output. The exact capability must match the application.

**Q5. What is a conventional baseline?**  
A simpler alternative, such as deterministic rules, a database query, conventional search, a fixed template, or a task-specific classifier, used for comparison.

**Q6. Why use representative examples?**  
They help reveal whether a candidate works for the intended users, common cases, edge cases, and realistic conditions.

**Q7. How should a simple evaluation rubric be used?**  
Define criteria and scoring rules, evaluate candidates under comparable conditions, and respect mandatory constraints instead of blindly selecting the highest total.

**Q8. When might a task-specific model be preferable?**  
When the task is narrow, the output is constrained, and the specialized solution meets the required quality with acceptable cost and complexity.

**Q9. What should a model-selection decision record include?**  
Requirements, candidates, evaluation evidence, assumptions, trade-offs, safeguards, residual risks, and triggers for reassessment.

**Q10. What should support the final recommendation?**  
The application requirements and observed evaluation results—not popularity, model size, or a single successful example.

<br/>

## 13. Chapter Summary

- Start with the user, problem, and measurable success criteria.
- Identify the task, modalities, context requirements, output constraints, and downstream actions.
- Evaluate quality alongside latency, cost, hardware, privacy, licensing, reliability, and operational effort.
- Choose a suitable model category and access approach; check licensing and deployment constraints separately.
- Establish a conventional baseline before adding model complexity.
- Compare candidates on representative examples using a defined rubric and consistent conditions.
- Treat mandatory constraints as gates, not merely weighted preferences.
- Document assumptions, trade-offs, evidence, human-review requirements, and residual risks.
- Reassess the decision when the application or its operating conditions change.

<br/>

### Final Checkpoint

Recommend a model category and access approach for a specific application. Support the recommendation with **requirements and observed evaluation results**, explain the trade-offs, identify a conventional baseline, and state when human review is needed.
