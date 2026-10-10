# 03. Training, Inference, and Generation

## 1. Learning Objectives

After completing this chapter, you should be able to:

- Explain training data, learned parameters, and training objectives at a conceptual level.
- Define inference as using a trained model on new input.
- Explain generation as an inference behavior that produces content.
- Distinguish pretraining from later model adaptation.
- Explain why a conversation or retrieved document does not automatically update model weights.
- Distinguish information learned by a model from context supplied by an application.
- Describe the lifecycle from model training to an application request.

<br/>

## 2. The Three Core Concepts

**Training**, **inference**, and **generation** are related, but they refer to different things.

| Concept | Meaning | Example |
|---|---|---|
| Training | The process of adjusting model parameters using data and a training objective | Training a language model on large collections of text |
| Inference | Using an already trained model to process an input and produce a result | Sending a question to a hosted language model |
| Generation | Producing content as part of a model's inference behavior | Generating an answer, email, or image |

Training prepares a model. Inference uses the trained model. Generation is one possible result of inference.

**Important:** Not every inference request generates new content. A model may instead classify an input, produce a score, or return a numerical prediction.

<br/>

## 3. Training: How a Model Learns

Training is the process in which a model's parameters are adjusted using training data and a training objective.

### 3.1 Training Data

**Training data** consists of examples used during training. Its form depends on the model and task.

Examples include:

- Text sequences used to train a language model.
- Images paired with labels or descriptions.
- Audio recordings and their transcripts.
- Structured examples used for prediction.

The training data provides examples from which the model can learn patterns. The quality, coverage, and limitations of the data influence what the model learns.

<br/>

### 3.2 Model Parameters

**Parameters** are learned numerical values inside a model. During training, an optimization process adjusts these values to improve performance according to the training objective.

For a neural network, parameters commonly include weights and biases.

Conceptually:

1. The model processes training examples.
2. It produces predictions.
3. A training objective measures how well those predictions meet the desired target.
4. An optimization process adjusts parameters.
5. The process repeats over many examples and training steps.

The parameters encode learned patterns in a distributed numerical form. They are not simply a human-readable database of every training example.

<br/>

### 3.3 Training Objectives

A **training objective** defines what the model is optimized to do. A **loss function** often measures the difference between a model's predictions and the desired training targets.

For example, a language model may be trained to predict the next token in a sequence. The model's predictions are compared with the actual next tokens, and training adjusts the parameters to improve the predictions.

Different models use different objectives. A classifier may learn to predict class labels, while an image-generation model may use an objective suited to its generation method.

<br/>

### 3.4 What Changes During Training?

The main conceptual change is to the model's **learned parameters**.

Training data is processed, the training objective is evaluated, and the parameters are adjusted. The model is not simply receiving a question and returning a response; it is undergoing an optimization process.

Training can require substantial data, compute, and time, depending on the model and training setup.

<br/>

## 4. Inference: Using a Trained Model

**Inference** is the process of using a trained model to process new input and produce a result.

Examples:

- Sending a question to a language model.
- Asking an image model to describe a photograph.
- Passing a transaction to a fraud classifier.
- Supplying house features to a price-prediction model.

In a typical application request:

1. The application prepares the input.
2. The trained model processes the input using its current parameters.
3. The model returns an output.
4. The application may validate, transform, or display the output.

Ordinary inference does not normally update the model's learned parameters.

<br/>

### 4.1 Inference Is Not the Same as Training

| Aspect | Training | Inference |
|---|---|---|
| Main purpose | Learn or adjust model parameters | Use the trained model |
| Data role | Training examples guide parameter updates | New input is processed by the model |
| Parameters | Updated by the training process | Normally remain fixed during the request |
| Typical activity | Optimization over many examples | A prediction or response for an input |
| Example | Training a spam classifier | Classifying a newly received email |

The exact lifecycle depends on the system, but model training and ordinary application inference are usually separate processes.

<br/>

## 5. Generation: Producing Content During Inference

**Generation** is a model behavior in which the model produces content, such as text, an image, audio, or video.

For an autoregressive language model, generation commonly proceeds by predicting a next token, selecting or sampling a token according to the decoding procedure, and repeating the process until a stopping condition is reached.

For example:

**Prompt:**

```text
Write a two-sentence explanation of photosynthesis.
```

**Possible generated output:**

```text
Photosynthesis is the process by which plants use sunlight
to convert water and carbon dioxide into sugars. Oxygen is
released as a by-product of this process.
```

The model generates the response using its learned parameters and the current request context.

Generation does not automatically mean the model is learning from the response. Producing new content and updating learned parameters are different processes.

<br/>

### 5.1 Is Every Inference Request Generative?

No.

- A text-generation request produces text.
- An image-generation request produces an image.
- A classification request produces a label or score.
- A regression request produces a numerical prediction.

All can involve inference, but not all involve content generation in the usual sense of creating new content.

<br/>

## 6. Pretraining and Adaptation

Models may go through multiple stages before being used in an application.

### 6.1 Pretraining

**Pretraining** is an initial, large-scale training stage used to learn broad patterns from a large dataset.

For a language model, pretraining may teach statistical and semantic regularities in language, including relationships between tokens and common structures in text.

Pretraining provides a general starting point, but it does not guarantee that a model will follow every user instruction or perform every task reliably.

<br/>

### 6.2 Adaptation

**Adaptation** refers to methods used to make a pretrained model more suitable for a particular behavior or application.

Common approaches include:

- **Instruction tuning:** Further training on examples that demonstrate how to respond to instructions.
- **Fine-tuning:** Additional training on a selected dataset to change model behavior or improve performance on a target task.
- **Preference optimization:** Training methods that encourage outputs preferred under a defined preference process.

These approaches can change model parameters. They differ from simply supplying a prompt or a document at inference time.

Prompting and retrieval can also adapt an application's behavior without necessarily changing the underlying model weights. These methods provide instructions or additional context rather than updating parameters.

<br/>

### 6.3 High-Level Comparison

| Method | Changes model weights? | How it affects behavior |
|---|---|---|
| Pretraining | Yes | Learns broad patterns from training data |
| Fine-tuning or instruction tuning | Yes | Further adjusts behavior through training |
| Prompting | Not by itself | Supplies instructions and context for a request |
| Retrieval-augmented context | Not by itself | Supplies relevant external information to the request |

This table describes the typical behavior of these methods. Some systems may use additional training, memory, or update mechanisms beyond an ordinary request.

<br/>

## 7. Model Knowledge vs. Application Context

A model request can use both information encoded in the model's learned parameters and information supplied at request time.

### 7.1 Model Knowledge

In this context, **model knowledge** means patterns and information reflected in the model's learned parameters from training and any subsequent training or adaptation.

It is not necessarily a complete, current, or perfectly retrievable record of the training data.

<br/>

### 7.2 Application Context

**Application context** is information supplied to the model when processing a particular request.

It may include:

- The current user message.
- Earlier messages included in the conversation history.
- System or developer instructions.
- Retrieved passages from documents.
- Data supplied by an application.

For example, an application may retrieve a paragraph from a company's policy document and include it with a user's question. The model can use that paragraph to answer the question, even if the document was not part of the model's original training data.

<br/>

### 7.3 Why a Conversation Does Not Automatically Update Model Weights

Consider a conversation:

```text
User: Our product is called Atlas, and its warranty lasts three years.
Assistant: Understood. I will use that information in this conversation.
```

The assistant may use the supplied information in later turns if the relevant conversation history remains available in its context.

However, merely adding this message to the conversation does not normally perform a training step or modify the model's learned parameters.

The same principle applies to a retrieved document. Retrieving and inserting text into a request supplies context; it does not, by itself, retrain the model.

Some applications implement separate memory systems, logging, feedback pipelines, or later training processes. Those are additional system mechanisms, not automatic consequences of ordinary inference.

<br/>

### 7.4 Context Is Not the Same as Permanent Learning

| Situation | What happens |
|---|---|
| A user supplies a fact in the current prompt | The model can use it while processing that request |
| Earlier messages are included in the next request | The model can use the included conversation history |
| An application retrieves a document and adds it to the prompt | The model can use the retrieved content as context |
| A model undergoes a training or fine-tuning process | Its parameters may be updated |
| A conversation ends and is not included in a later request | The model cannot rely on that conversation being present in its context |

A product may provide persistent memory or retrieve past conversations through a separate mechanism. That still does not necessarily mean its underlying model weights have changed.

<br/>

## 8. A Simple Training-to-Application Lifecycle

The following diagram shows a typical high-level lifecycle.

```text
Training data
     |
     v
Training objective + optimization
     |
     v
Learned model parameters
     |
     v
Trained model available for use
     |
     v
Application prepares a request
(prompt + relevant context)
     |
     v
Inference
     |
     v
Model output
(generated content or prediction)
     |
     v
Application validation and response
```

<br/>

### How to Read the Diagram

1. **Training data:** Examples are provided to the training process.
2. **Training objective and optimization:** The model's parameters are adjusted to improve the defined objective.
3. **Learned parameters:** The trained parameters encode patterns learned during training.
4. **Application request:** The application supplies the current prompt and any relevant context.
5. **Inference:** The model processes the request using its trained parameters.
6. **Output:** The model returns generated content, a classification, a score, or another result.
7. **Application handling:** The application may validate, format, store, or display the result.

The diagram separates the training process from an ordinary application request. In a typical deployment, the request does not repeat the training process.

<br/>

## 9. Conceptual Python Example

This example illustrates inference using a simple, already trained model API. It does not train or fine-tune the model.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

prompt = "Explain the difference between training and inference."

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt,
)

print(response.output_text)
```

<br/>

### What the code does

1. Reads the API key from an environment variable.
2. Creates a client for a hosted model API.
3. Sends a prompt to the model.
4. Receives the model's response.
5. Prints the generated text.

This is an inference request. The code does not supply training data, calculate a training loss, run an optimizer, or update the model parameters.

The model identifier is an example; use a currently available model supported by your account and API.

<br/>

## 10. Common Misconceptions

| Misconception | Correct understanding |
|---|---|
| Inference and training are the same process. | Training adjusts parameters; inference uses the trained model to process input. |
| Every inference request generates content. | Inference can also produce labels, scores, or numerical predictions. |
| Generating an answer means the model learned from that answer. | Generation does not automatically update the model's parameters. |
| A retrieved document permanently becomes part of the model. | Retrieval supplies context to a request unless a separate update or training mechanism is used. |
| A model's learned information is always complete and current. | Model knowledge can be incomplete, outdated, or incorrect. |
| Prompting is the same as fine-tuning. | Prompting supplies instructions or context; fine-tuning uses an additional training process to adjust parameters. |
| Conversation history is always available forever. | A later request can use only the history or memory made available to it by the application. |

<br/>

## 11. Practice: Annotate the Lifecycle

Use the lifecycle diagram in Section 8. For each stage, explain what happens.

1. **Training data:** What examples are used?
2. **Optimization:** What is adjusted during training?
3. **Trained model:** What is available after training?
4. **Application request:** What information does the application send?
5. **Inference:** What does the model do with the request?
6. **Output:** What can the model return?
7. **Application handling:** Why might the result need validation?

<br/>

### Practice Scenario

A company has a support chatbot. Its language model was trained earlier. At request time, the application retrieves a current warranty policy and includes the policy text alongside the customer's question.

Answer these questions:

- Which information comes from the model's learned parameters?
- Which information is supplied as request-time context?
- Does retrieving the policy automatically update the model's weights?
- What could the application do if the model's answer conflicts with the policy?

**Suggested answers:**

- The model uses patterns encoded in its learned parameters.
- The retrieved warranty policy and customer question are supplied as request-time context.
- No. Retrieval alone does not automatically update model weights.
- The application can validate the answer against the source policy, provide a citation, request a corrected response, or escalate the question for human review.

<br/>

## 12. Revision Questions and Answers

**Q1. What is training?**

Training is the process of adjusting model parameters using data and a training objective.

**Q2. What are model parameters?**

They are learned numerical values, such as neural-network weights and biases, that are adjusted during training.

**Q3. What is inference?**

Inference is the use of a trained model to process an input and produce a result.

**Q4. How is generation related to inference?**

Generation is an inference behavior in which the model produces content, such as text, images, audio, or video.

**Q5. What is pretraining?**

Pretraining is an initial training stage in which a model learns broad patterns from a large dataset.

**Q6. How does fine-tuning differ from prompting?**

Fine-tuning uses an additional training process that can update model parameters. Prompting supplies instructions or context without itself updating those parameters.

**Q7. Does supplying a document in a prompt update the model's learned parameters?**

No. It provides request-time context. Updating parameters requires a separate training or update mechanism.

**Q8. What is the difference between model knowledge and application context?**

Model knowledge refers to information and patterns reflected in learned parameters. Application context is information supplied for a particular request, such as a prompt, conversation history, or retrieved document.

<br/>

## 13. Chapter Summary

- Training uses data and a defined objective to adjust model parameters.
- Parameters encode learned patterns but do not guarantee complete or correct knowledge.
- Inference uses a trained model to process new input.
- Generation is one possible inference behavior that produces content.
- Pretraining establishes broad capabilities; adaptation methods such as fine-tuning can further adjust model behavior.
- Prompting and retrieval supply instructions or context without automatically changing model weights.
- Conversation history is useful only when the application makes the relevant history available to the model.
- Applications often need validation and other controls around model outputs.

<br/>

## 14. Checkpoint

**Question:** What changes during training, and what happens during an ordinary model request?

**Answer:** During training, the model's learned parameters are adjusted using training data, a training objective, and an optimization process. During an ordinary request, the application supplies input and relevant context, and the trained model performs inference using its current parameters. It may generate content or return another kind of prediction, but the request does not normally update the model's weights.

**Next chapter:** 04. Modalities and Outputs.
