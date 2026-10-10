# Level 1: Generative AI Fundamentals

Understand what Generative AI is, what it can produce, how it differs from other AI approaches, and when it is suitable for an application.

This README is the plan for creating notes one by one. The filenames below are planned files, not existing chapter links.

<br/>

## Prerequisites

- Basic understanding of software applications, inputs, and outputs.
- Familiarity with the practical foundations in Level 0.
- Basic Python is useful for optional experiments; the conceptual chapters do not require model training or advanced mathematics.

<br/>

## Learning outcomes

After completing this level, you should be able to:

- Explain Generative AI and distinguish it from classification and other predictive tasks.
- Distinguish training, inference, and generation.
- Identify text, image, audio, video, and structured-output tasks.
- Explain why generated outputs can vary and fail.
- Distinguish foundation models from task-specific models and hosted access from open-weight deployment.
- Select a suitable model category and access approach for a use case.
- Write a use-case brief covering requirements, limitations, and risks.

<br/>

## Study order and planned note files

Create the notes in this order. Each row represents one chapter folder and one main note.

| Order | Chapter folder | Main note filename | Focus |
|---|---|---|---|
| 1 | `01_What_Is_Generative_AI` | `01_what_is_generative_ai.md` | Definition, scope, and relationship to AI, ML, and deep learning |
| 2 | `02_Generative_vs_Discriminative` | `01_generative_vs_discriminative.md` | Generating content versus predicting labels or values |
| 3 | `03_Training_Inference_and_Generation` | `01_training_inference_and_generation.md` | How models learn and how applications use them |
| 4 | `04_Modalities_and_Outputs` | `01_modalities_and_outputs.md` | Text, images, audio, video, and structured outputs |
| 5 | `05_Foundation_and_Task_Specific_Models` | `01_foundation_and_task_specific_models.md` | Broad capabilities, specialization, and model adaptation |
| 6 | `06_Hosted_and_Open_Weight_Models` | `01_hosted_and_open_weight_models.md` | Access, deployment, control, and operational trade-offs |
| 7 | `07_Application_Patterns` | `01_application_patterns.md` | Common uses and the model's role inside an application |
| 8 | `08_Output_Variability` | `01_output_variability.md` | Stochastic generation and reproducibility |
| 9 | `09_Limitations_and_Responsible_Use` | `01_limitations_and_responsible_use.md` | Hallucinations, bias, uncertainty, privacy, and data limitations |
| 10 | `10_Model_and_Use_Case_Selection` | `01_model_and_use_case_selection.md` | Requirements and evidence-based selection |
| 11 | `11_Practice_and_Revision` | `01_practice_and_revision.md` | Scenarios, revision questions, and the level deliverable |

<br/>

## Chapter outlines

### 01. What Is Generative AI?

- Define AI, machine learning, deep learning, and Generative AI at a high level.
- Explain generation as producing content from patterns learned during training.
- Introduce inputs, prompts, models, and outputs.
- Distinguish a model from a complete application.
- Explain why fluent or realistic output does not guarantee correctness.

**Practice:** Describe three generative applications and identify their inputs and outputs.

**Checkpoint:** Explain Generative AI in your own words using one concrete example.

<br/>

### 02. Generative versus Discriminative Models

- Introduce generative and discriminative modeling conceptually.
- Compare generating an email with classifying an email as spam.
- Compare image generation with image classification.
- Distinguish generation, classification, and regression as tasks.
- Explain that a generative model can also perform classification through suitable instructions.

**Practice:** Categorize six tasks and explain whether generation is needed.

**Checkpoint:** Distinguish a model's learning approach from the task an application asks it to perform.

<br/>

### 03. Training, Inference, and Generation

- Explain training data, learned parameters, and training objectives conceptually.
- Define inference as using a trained model on new input.
- Explain generation as an inference behavior that produces content.
- Introduce pretraining and adaptation without implementation details.
- Explain why a conversation or retrieved document does not automatically update model weights.
- Separate model knowledge from context supplied by an application.

**Practice:** Annotate a simple training-to-application lifecycle diagram.

**Checkpoint:** Explain what changes during training and what happens during an ordinary model request.

<br/>

### 04. Modalities and Outputs

- Define a modality and distinguish input modalities from output modalities.
- Introduce text generation, image generation, speech generation, and video generation.
- Introduce image understanding, speech recognition, and video understanding as related capabilities.
- Explain multimodal inputs and outputs with simple examples.
- Introduce structured text outputs such as JSON, extracted fields, and code.
- Distinguish understanding existing content from generating new content.

**Practice:** Map five application scenarios to their required input and output modalities.

**Checkpoint:** Recognize that understanding an image does not imply a model can generate images.

<br/>

### 05. Foundation Models and Task-Specific Models

- Define foundation models and task-specific models.
- Introduce language models, LLMs, and multimodal foundation models.
- Compare broad capabilities with narrow task requirements.
- Introduce base and instruction-tuned models conceptually.
- Preview prompting, retrieval, and fine-tuning as different ways to adapt application behavior.
- Explain why model size alone does not determine suitability.

**Practice:** Compare a broad language model with a specialized classifier for a clearly defined task.

**Checkpoint:** Explain when a smaller specialized model may be sufficient.

<br/>

### 06. Hosted and Open-Weight Models

- Define hosted inference, downloadable model weights, and local or self-managed inference.
- Explain that open-weight models can also be accessed through hosted services.
- Distinguish open weights from open-source licensing and verify usage rights separately.
- Compare setup effort, hardware, privacy, control, latency, and operational cost.
- Introduce model documentation, licenses, and deployment constraints.
- Discuss why self-hosting alone does not guarantee privacy or lower cost.

**Practice:** Create a deployment comparison for a prototype and an application handling sensitive data.

**Checkpoint:** Treat access method, licensing, and deployment location as separate decisions.

<br/>

### 07. Common Application Patterns

- Summarization and rewriting.
- Extraction, classification, and structured transformation.
- Drafting content and assisting with code.
- Question answering and knowledge assistance.
- Image, speech, and media creation.
- Preview retrieval-grounded answers without implementing a RAG pipeline.
- Identify where validation, business rules, and human review fit around a model.
- Recognize situations where deterministic code or conventional search is sufficient.

**Practice:** Sketch the input, model step, validation, and output for one application.

**Checkpoint:** Describe the model's role without treating it as the entire system.

<br/>

### 08. Stochastic Generation and Output Variability

- Introduce probabilistic generation and sampling intuition.
- Explain why repeated requests may produce different outputs.
- Preview temperature and sampling controls at a conceptual level.
- Explain that more variation does not imply more factual accuracy.
- Discuss reproducibility limits, configuration changes, and model updates.
- Introduce testing multiple examples and repeated runs.

**Practice:** If model access is available, repeat one prompt several times and record differences. Otherwise, compare a prepared set of outputs.

**Checkpoint:** Explain why one successful output is insufficient evidence of reliability.

<br/>

### 09. Limitations and Responsible Use

- Hallucinations: unsupported facts, fabricated citations, and plausible errors.
- Bias, uneven performance, and training-data limitations.
- Knowledge freshness and missing application context.
- Ambiguity and limitations of self-reported confidence.
- Privacy, sensitive inputs, licensing, and provenance awareness.
- Prompt injection awareness and the need to separate instructions from untrusted content.
- Verification, appropriate abstention, and human review for consequential uses.

**Practice:** Review sample outputs, identify failure modes, and propose checks or mitigations.

**Checkpoint:** Document remaining risks without claiming that prompting eliminates them.

<br/>

### 10. Model and Use-Case Selection

- Define the user, problem, and success criteria before selecting a model.
- Identify task, modalities, context needs, and output constraints.
- Consider quality, latency, cost, hardware, privacy, and licensing requirements.
- Choose a model category and deployment approach.
- Compare candidates using representative examples and a simple evaluation rubric.
- Consider a conventional software baseline.
- Record assumptions, trade-offs, and when human review is required.

**Practice:** Recommend a model category and access approach for three scenarios, with reasons.

**Checkpoint:** Support the recommendation with requirements and observed results rather than popularity.

<br/>

### 11. Practice and Revision

- Compare a generative task with a classification task.
- Identify suitable model categories for text, document, image, and speech scenarios.
- Review the distinction between training, inference, context, and generation.
- Compare hosted and self-managed deployment choices.
- Analyze unreliable outputs and propose validation steps.
- Complete the use-case brief below.

**Checkpoint:** Explain your decisions clearly enough for another learner to review them.

<br/>

## Level deliverable: GenAI use-case brief

Create `11_Practice_and_Revision/use_case_brief.md` for one application idea. Include:

1. Problem statement and target user.
2. Example inputs and expected outputs.
3. Why Generative AI is appropriate and a conventional alternative.
4. Required model capabilities and modalities.
5. Proposed model category and deployment approach.
6. Quality, latency, cost, privacy, and licensing requirements.
7. At least five representative test cases, including ambiguous or unsupported requests.
8. A simple rubric for acceptable output.
9. Expected limitations, risks, validation, and human-review needs.
10. Assumptions and open questions to investigate in later levels.

A working application is optional at this stage. If you run experiments, record the model identifier, date, prompt, available settings, and observed results; use synthetic or public inputs.

<br/>

## Suggested structure for each future note

Use a consistent format when writing the planned chapters:

1. Learning objectives.
2. Why the topic matters.
3. Definitions and explanation.
4. Concrete examples or a comparison table.
5. Common misconceptions and limitations.
6. A short exercise.
7. Revision questions and answers.
8. References used for technical claims.

Add code or notebooks when they help demonstrate the concept. Date any provider-specific examples and verify their capabilities when writing the notes.

<br/>

## Completion checklist

- [ ] Explain Generative AI with concrete examples.
- [ ] Compare generative and discriminative modeling and distinguish their application tasks.
- [ ] Distinguish training, inference, and generation.
- [ ] Identify required input and output modalities.
- [ ] Explain foundation models and task-specific models.
- [ ] Compare hosted access, open weights, licensing, and self-managed deployment.
- [ ] Explain output variability and common failure modes.
- [ ] Select an approach using requirements and representative test cases.
- [ ] Complete and review the use-case brief.

<br/>

## Scope and next step

This level introduces concepts and decision-making. Model architecture details belong to Levels 2–4; prompt implementation and APIs to Levels 5–6; embeddings and RAG to Levels 7–8; deeper multimodal work to Levels 9–11; fine-tuning to Level 12; systematic evaluation and security to Levels 13–14; and production engineering to Level 15.

Agent orchestration, autonomous agents, multi-agent systems, and MCP-based agent integrations remain part of the separate Agentic AI course.

Next: **Level 2 — Generative Model Architectures** in the [main course outline](../README.md).
