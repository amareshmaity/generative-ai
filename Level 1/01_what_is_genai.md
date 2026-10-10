Level 1: Generative AI Fundamentals · Chapter 01

# 01. What Is Generative AI?

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Define Artificial Intelligence (AI), Machine Learning (ML), Deep Learning (DL), and Generative AI.
- Explain how Generative AI produces content based on patterns learned during training.
- Understand the roles of inputs, prompts, models, and outputs.
- Distinguish an AI model from a complete AI application.
- Explain why fluent or realistic AI-generated content may still be incorrect.
- Identify the inputs and outputs of common generative applications.

<br/>

## 2. What Is Artificial Intelligence?

Artificial Intelligence (AI) is a field of computer science focused on building systems that perform tasks commonly associated with human intelligence.

These tasks include learning, reasoning, recognizing patterns, understanding language, solving problems, and making predictions.

Examples of AI applications include:

- Spam detection in email.
- Face recognition in photographs.
- Voice assistants that respond to spoken commands.
- Recommendation systems that suggest products.
- Chatbots that generate human-like responses.

AI is the broad field that includes several approaches, such as rule-based systems, machine learning, and deep learning.

<br/>

## 3. AI vs Machine Learning vs Deep Learning vs Generative AI

These terms are related, but they do not mean the same thing.

### Artificial Intelligence (AI)

The broad field of creating systems that perform tasks associated with intelligence.

Example: A rule-based system that recommends an action.

<br/>

### Machine Learning (ML)

A subset of AI in which systems learn patterns from data instead of relying entirely on explicitly programmed rules.

Example: A model trained to predict house prices.

<br/>

### Deep Learning (DL)

A subset of ML that uses neural networks with multiple layers to learn complex patterns.

Example: A neural network that recognizes objects in images.

<br/>

### Generative AI

A category of AI systems designed to generate new content, often using deep learning models.

Example: A language model that drafts an email.

Conceptual relationship: Generative AI commonly uses deep learning, but not every AI system is based on ML, and not every ML or DL model is generative.

<br/>

### 3.1 Machine Learning

Machine Learning enables computers to learn patterns from examples and use those patterns to make predictions or decisions.

For example, a house-price prediction model learns relationships between features such as area, location, and number of rooms and the corresponding prices.

Its output might be a numerical prediction:

`Predicted house price: ₹45,00,000`

<br/>

### 3.2 Deep Learning

Deep Learning uses neural networks containing multiple layers. These networks can learn increasingly complex representations from data.

Deep learning is widely used in:

- Image recognition.
- Speech recognition.
- Natural language processing.
- Large language models.
- Image, audio, and video generation.

<br/>

### 3.3 Generative AI

Generative AI focuses on producing content rather than only assigning labels or predicting values.

It can generate:

- Text: explanations, summaries, emails, and stories.
- Images: illustrations, designs, and synthetic photographs.
- Audio: speech, music, and sound effects.
- Video: generated scenes and animations.
- Structured outputs: JSON objects, extracted fields, and code.

The generated content is based on patterns and representations learned during training, together with the input and context supplied when the model is used.

<br/>

## 4. How Does Generative AI Work?

At a high level, a generative application follows a simple process:

**1\. Input:** A user provides a request, prompt, image, audio clip, or other data.

**2\. Model processing:** The trained model processes the input using learned parameters and available context.

**3\. Generation:** The model produces content according to its learned patterns and generation procedure.

**4\. Output**: The application returns text, an image, audio, structured data, or another supported result.

<br/>

For example, a user enters:

> Explain photosynthesis to a 10-year-old student.

A language model processes the request and generates an explanation appropriate to the specified audience.

The model does not simply retrieve a prewritten answer in every case. It generates a response using its learned parameters, the current input, and any additional context provided to it.

<br/>

### 4.1 What does “learning patterns during training” mean?

During training, a model processes training examples and adjusts its parameters according to a training objective.

For a language model, one important training objective is predicting the next token in a sequence.

Through training, the model can learn statistical and semantic patterns involving grammar, word relationships, concepts, and other regularities present in the data.

When the model is later given a prompt, it uses its learned parameters to produce an output.

Important: Learning patterns does not mean the model automatically stores every training example as a searchable record or understands every concept in the same way a human does.

<br/>

## 5. Understanding Inputs, Prompts, Models, and Outputs

These are fundamental components of a Generative AI system.

| Component | Meaning                                                                                            | Example                                            |
| --------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Input     | Information supplied to the system                                                                 | A paragraph to summarize                           |
| Prompt    | Instructions or context guiding the model's response                                               | “Summarize this paragraph in three bullet points.” |
| Model     | A trained computational system that processes inputs and produces predictions or generated content | A large language model                             |
| Output    | The result produced by the model or returned by the application                                    | A three-bullet summary                             |

A prompt can include the task instructions, source content, desired format, and other relevant context. A prompt is not necessarily just a question.

<br/>

### Example

Input content:

`Generative AI can produce text, images, audio, and other forms of content.`

Prompt:

`Summarize the following text in one sentence: Generative AI can produce text, images, audio, and other forms of content.`

Expected output:

`Generative AI creates content in multiple formats, including text, images, and audio.`

The output is a generated response to the prompt. Its quality depends on the model's capabilities, the input, the instructions, and other generation settings.

<br/>

## 6. Code Example: A Simple Generative AI Application

The following example demonstrates the basic structure of a model-backed application using Python.

It uses a hosted language model through the OpenAI Python SDK. You need a valid API key and an available model to execute it.

### 6.1 Install the SDK

```
pip install openai
```

Set your API key through an environment variable named `OPENAI_API_KEY`. Avoid placing secret keys directly in source code.

### 6.2 Generate text from a prompt

```python
import os
from openai import OpenAI

# Read the API key from an environment variable
api_key = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

# Input and prompt
prompt = """
Explain Generative AI to a beginner in three bullet points.
"""

# Send the prompt to the model
response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

# Display the generated output
print(response.output_text)
```

The model identifier is an example; use a currently available model supported by your account and API.

<br/>

### 6.3 Understanding the code

1. `OpenAI()` creates a client for communicating with the provider's API.
2. `prompt` contains the instruction supplied to the model.
3. `client.responses.create()` sends a request to the hosted model.
4. The model processes the request and generates a response.
5. `response.output_text` extracts the text returned by the API.

The actual wording of the output may vary between requests.

<br/>

### 6.4 What happens in this example?

Input / prompt

Explain Generative AI to a beginner in three bullet points.

Model

A hosted language model processes the prompt and generates text.

Output

A generated explanation containing three bullet points, if the model follows the instruction.

This example demonstrates inference and generation. It does not train the model.

Also, asking for three bullet points does not guarantee exactly three bullet points. If that requirement is important, validate the output or use a suitable structured-output mechanism.

<br/>

## 7. A Model Is Not the Same as a Complete Application

A model is the trained component that processes inputs and produces outputs. A Generative AI application combines the model with software components that make it useful for a particular task.

For example, consider an AI-powered PDF question-answering application.

<br/>

### Example: PDF Question-Answering Application

**User interface**

The user uploads a PDF and asks a question.

**Application logic**

Extracts relevant text, prepares context, and builds the model request.

**Generative AI model**

Generates an answer using the supplied question and context.

**Validation and response handling**

Checks the response as needed and returns it to the user.

A complete application may include:

- Frontend: The user interface.
- Backend: Application logic and API endpoints.
- Model integration: Code that communicates with the model.
- Data processing: File parsing, cleaning, or context preparation.
- Validation: Checks for required fields, formats, and business rules.
- Security: Authentication, authorization, and secret management.
- Monitoring: Logging, error tracking, latency measurements, and cost tracking.

Not every application needs all these components. Their requirements depend on the use case.

**Key distinction:** The model generates content; the surrounding application determines how inputs are collected, what context is supplied, what actions are allowed, and how outputs are handled.

<br/>

## 8. Why Fluent or Realistic Output Does Not Guarantee Correctness

Generative AI can produce responses that are clear, grammatically correct, persuasive, and realistic while still containing incorrect information.

This is because fluency and factual correctness are different properties.

<br/>

### 8.1 Common reasons

1\. Learned patterns are not a guarantee of truth

A model learns patterns from training data. Those patterns can support useful responses, but they do not guarantee that every generated statement is factually correct.

2\. Missing or outdated information

A model may lack current information or relevant details about a particular situation.

3\. Ambiguous prompts

A vague question can lead to an answer based on assumptions that do not match the user's intention.

4\. Fabricated details

A model may generate plausible but unsupported facts, references, quotations, or citations. This type of failure is commonly called a hallucination.

5\. Plausible answers can conceal errors

A well-written answer may be accepted too quickly because it sounds authoritative.

<br/>

### 8.2 Example

Suppose a user asks:

> What is the publication year of a book whose title I have provided, but no author or edition?

The model might return a specific year even when the available information is insufficient to identify the book reliably.

The answer may sound confident, but it could be wrong.

<br/>

### 8.3 How should applications handle this?

- Verify important factual claims against reliable sources.
- Supply relevant context when the model needs it.
- Use deterministic code for calculations and rules that can be handled reliably with conventional software.
- Validate structured outputs against schemas.
- Test representative examples, including ambiguous and unsupported requests.
- Allow the application to request clarification or abstain when evidence is insufficient.
- Require human review for consequential decisions.

No single prompt or validation technique eliminates every possible failure.

<br/>

## 9. Practice: Identify Inputs and Outputs

Consider these three generative applications.

[Context-Aware Writing Tips for Professionals | Revise AI](https://images.openai.com/static-rsc-4/nhJ0fuctnX377BJ8nEJe2XgcV5ki9b1uSFIXsagR_gM97QD-0QzLqJyOWnDVDd6xIvKouQdw7V3rWdjjEUJRfvDyhyInWkRr4hqtb71yuwSYDbpeFtPFnK1Vgq-aZOjuwtxeicPAeyH6Bw4ni5HaQVT0Ce5YfUEOvEalxu914EM?purpose=inline)

### Application 1: Email Drafting Assistant

- Input: User instructions, recipient details, and relevant message context.
- Model task: Generate a suitable email draft.
- Output: Email subject and body.
- Validation: Check tone, factual details, and recipient information before sending.

[AI Image Generator from Text Free: Create Stunning Images at No Cost](https://images.openai.com/static-rsc-4/deQDX--uOOrmhpmkHqj1oAEzlTu_tRnRgbzSwDZg-8gIcUTiR5bOJHV6FVgjZhrNlMd_aHmSgwKAf9F3qpg0g0Pxa2jJcdi7bHANFyjjpX8E3m4fgj30oMrZWGoXhPfFmOearf3oXHfrC5l3RXdX6hNe2YvTu56rvf3-H0giznk?purpose=inline)

### Application 2: Image Generation

- Input: A text prompt describing the desired image.
- Model task: Generate an image that reflects the prompt.
- Output: A generated image.
- Validation: Check visual quality, prompt adherence, and applicable usage rights.

[WhisperAI](https://images.openai.com/static-rsc-4/xatt0szD_wDWVf-xShCKDVrk-uvI4QUFnjVw3MwkNVQlIOpha3Op8rxb8EpywqnpzJkEzRP9Q07Kr6yhsaf17mXKm9o7jB4rEhv5fAjG4bJSDY1XwVZHDRYA9OQ56xfdJ-RBwCZj8Ie4RnhafP5IFpFoVKX4bj85qFP4o_AMm8M?purpose=inline)

### Application 3: Text-to-Speech

- Input: Written text and optional voice or speaking-style settings.
- Model task: Generate speech from the text.
- Output: An audio file or audio stream.
- Validation: Check pronunciation, intelligibility, and whether the spoken content matches the input.

### Exercise

Try identifying the components for a fourth application: a tool that converts a long report into a short executive summary.

Input

Prompt

Summarize the report for an executive in 5 bullet points.

Expected output

A concise executive summary

Copy my answer

<br/>

## 10. Common Misconceptions

| Misconception                                         | Correct understanding                                                                                                  |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Every AI system is Generative AI.                     | Many AI systems classify, predict, rank, or make decisions without generating new content.                             |
| Generative AI always retrieves a stored answer.       | It can generate new sequences or content using learned parameters and current context.                                 |
| A larger model is always better.                      | Suitability depends on task quality, cost, latency, deployment constraints, and other requirements.                    |
| Fluent output is always correct.                      | Fluency does not establish factual accuracy.                                                                           |
| The model and application are the same thing.         | The model is one component of a potentially larger software system.                                                    |
| Providing information in a prompt retrains the model. | Ordinary inference generally uses the existing model parameters; supplying context does not automatically update them. |

<br/>

## 11. Chapter Summary

- AI is the broad field of building systems that perform tasks associated with intelligence.
- ML learns patterns from data, while DL uses multilayer neural networks.
- Generative AI produces content such as text, images, audio, video, and structured outputs.
- A generative workflow involves inputs, prompts, a trained model, and outputs.
- Training adjusts model parameters; inference uses the trained model to process new inputs; generation produces content during inference.
- A complete application includes the model and any surrounding software needed to deliver a useful result.
- Fluent, realistic output can still contain factual errors, so validation and verification matter.

<br/>

## 12. Revision Questions and Answers

Q1. What is Generative AI?

Generative AI is a category of AI that produces new content based on patterns learned during training and the input and context provided during use.

Q2. How does ML differ from DL?

ML is the broader category of learning from data. DL is a subset of ML that uses neural networks with multiple layers.

Q3. What is the difference between a prompt and a model?

A prompt supplies instructions or context. A model is the trained computational system that processes the prompt and produces a response.

Q4. Does calling a model API train the model?

No. An ordinary API request performs inference using an existing model. It does not automatically update the model's learned parameters.

Q5. Why can Generative AI produce incorrect answers?

Its learned patterns do not guarantee factual truth. Missing context, ambiguity, outdated knowledge, and unsupported generation can lead to errors.

Q6. What is the difference between a model and an application?

A model processes inputs and produces outputs. An application integrates the model with user interfaces, data handling, business logic, validation, security, and other required components.

Q7. Give one example of a Generative AI application.

An email drafting assistant takes user instructions and message context as input and generates an email draft as output.

<br/>

## 13. Checkpoint

You should now be able to explain Generative AI in your own words using one concrete example. For example:

> Generative AI is a type of AI that can create content based on patterns learned during training. An email drafting assistant is one example: it takes a user's instructions and relevant context, processes them with a trained language model, and generates an email draft. The surrounding application can validate the result, but the draft should still be reviewed because a fluent response is not necessarily correct.

Next chapter: 02. Generative versus Discriminative Models.