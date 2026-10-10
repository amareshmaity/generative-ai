# Generative AI Engineering

A structured, project-oriented curriculum for understanding generative models and building, evaluating, and deploying reliable Generative AI applications.

This course focuses on **Generative AI fundamentals and engineering**: model families, LLMs, APIs, retrieval, multimodal capabilities, customization, evaluation, security, and production practices.

> **Scope boundary:** Agentic AI is taught separately. This course teaches basic LLM tool calling through a single application-controlled function call, but excludes agent orchestration, autonomous agents, multi-agent systems, LangGraph workflows, and MCP-based agent integrations.

## Course Goals

By completing this curriculum, you should be able to:

- Explain the main families of generative models and their use cases.
- Understand transformer architectures, LLM training stages, and inference.
- Use hosted and open-weight models through APIs or local inference.
- Design prompts and generate validated structured outputs.
- Build semantic search and retrieval-augmented generation (RAG) applications.
- Understand multimodal models for text, images, audio, and video.
- Customize models using suitable fine-tuning techniques.
- Evaluate output quality, retrieval performance, safety, latency, and cost.
- Build, test, deploy, and monitor production-oriented GenAI applications.
- Present end-to-end projects with clear architecture, evaluation, and documentation.

## How to Use These Notes

Each level will be developed into separate notes. The outline defines scope and sequence; individual chapter files will contain explanations, examples, code, exercises, and projects.

Recommended learning loop:

1. Understand the concept.
2. Implement a small example.
3. Test it on representative inputs.
4. Measure quality, failure cases, latency, or cost where relevant.
5. Document the result and key design decisions.

<br/>

## Level 0: Prerequisites and Development Environment

**Goal:** Prepare the Python and engineering foundations needed to work efficiently with GenAI libraries and services.

### Topics

- Python functions, classes, modules, exceptions, and type hints
- Object-oriented programming fundamentals
- Virtual environments and dependency management
- Package installation and project configuration
- Pydantic models and data validation
- HTTP and REST APIs: methods, status codes, headers, and request/response design
- FastAPI fundamentals: routes, request bodies, validation, and dependencies
- Synchronous versus asynchronous programming, `async`/`await`, and I/O-bound work
- Authentication basics: API keys, tokens, and access control
- Logging, exception handling, and safe error responses
- Unit testing and API testing
- JSON, files, PDFs, CSVs, and basic data handling
- NumPy and Pandas essentials
- SQL fundamentals
- Git and GitHub
- Command-line basics
- Environment variables and secret handling
- Linear algebra essentials: vectors, matrices, dot products, and similarity
- Probability and statistics essentials
- Neural networks, backpropagation, loss functions, and optimization at a conceptual level

### Practice

- Create a reproducible Python project with a virtual environment.
- Validate JSON input with Pydantic.
- Load and inspect a small dataset.
- Use Git to track a project and document setup instructions.
- Build and test a small FastAPI endpoint with validated input, authentication, and logging.

### Existing prerequisite notes

- [REST APIs](<Level 0/1.1_REST_API/README.md>)
- [FastAPI](<Level 0/1.2_FAST_API/README.md>)
- [Request and response design](<Level 0/1.3_REQUEST_RESPONSE_DESIGN/README.md>)
- [Async basics](<Level 0/1.4_Async basics/README.md>)
- [Authentication](<Level 0/1.5_Authentication basics/README.md>)
- [Logging and exception handling](<Level 0/1.6_Logging_and_Exception_Handling/README.md>)
- [Environment variables and configuration](<Level 0/1.7_Environment_Variables_and_Config_Management/README.md>)
- [Unit testing and API testing](<Level 0/1.8_Unit_Testing_and_API_Testing/README.md>)
- [JSON, files, PDFs, and CSVs](<Level 0/1.9_Working_with_JSON_Files_PDFs_and_CSVs/README.md>)

**Scope note:** Treat familiar material as revision. The goal is practical readiness, not repeating an entire data science curriculum.

<br/>

## Level 1: Generative AI Fundamentals

**Goal:** Understand what Generative AI is, what it can produce, and how it differs from other AI approaches.

### Topics

- Definition and scope of Generative AI
- Generative versus discriminative models
- Training, inference, and generation
- Modalities: text, images, audio, video, and other structured outputs
- Common application patterns and limitations
- Stochastic generation and why outputs may vary
- Hallucinations, bias, uncertainty, and data limitations
- Hosted models versus open-weight models
- Foundation models and task-specific models
- Selecting an appropriate model for a use case

### Practice

- Compare a generative task with a classification task.
- Identify suitable model types for several application scenarios.
- Document limitations and risks for a selected GenAI use case.

<br/>

## Level 2: Generative Model Architectures

**Goal:** Build a high-level understanding of the main model families behind generative systems.

### Topics

- Autoregressive generation
- Transformer-based generation
- Variational Autoencoders (VAEs): latent variables, encoder-decoder structure, and reconstruction
- Generative Adversarial Networks (GANs): generator, discriminator, and adversarial training
- Diffusion models: noise addition, denoising, and iterative generation
- Latent representations and latent spaces
- High-level comparison of model families
- Typical strengths, limitations, and use cases

### Practice

- Compare autoregressive, VAE, GAN, and diffusion approaches.
- Trace the high-level stages of a diffusion generation process.
- Explain why different tasks may require different model families.

**Depth guidance:** Focus on conceptual understanding and practical distinctions. Detailed derivations and training large models from scratch are optional extensions.

**Terminology note:** Autoregression describes a generation approach; transformers describe an architecture. A transformer can generate autoregressively, so these categories are not mutually exclusive.


<br/>


## Level 3: Transformer Architecture and Tokenization

**Goal:** Understand the architecture that underpins most modern LLMs and many multimodal models.

### Topics

- Tokens, token IDs, vocabularies, and tokenization
- Embedding layers
- Positional information and positional encoding
- Self-attention and scaled dot-product attention
- Multi-head attention
- Query, key, and value representations
- Feed-forward networks
- Residual connections and layer normalization
- Encoder-only, decoder-only, and encoder-decoder architectures
- Causal and masked attention
- BERT, GPT-style models, and T5 as architectural examples
- Context windows and token budgets
- High-level inference flow
- KV cache intuition
- Prefill versus autoregressive token generation

### Practice

- Inspect tokenization for different kinds of text.
- Explain how a token sequence moves through a transformer.
- Compare encoder-only, decoder-only, and encoder-decoder use cases.
- Estimate how prompt length affects context usage and inference cost.


<br/>


## Level 4: LLM Fundamentals and Inference

**Goal:** Understand how LLMs are trained, adapted, selected, and used at inference time.

### Topics

- Next-token prediction
- Pretraining and training data at a conceptual level
- Instruction tuning and supervised fine-tuning (SFT)
- Preference optimization and RLHF at a conceptual level
- Alignment and model behavior
- Inference and decoding
- Greedy decoding, beam search, and sampling concepts
- Temperature, top-p, and top-k where supported
- Stop sequences and output limits
- Reasoning-capable models and inference-time computation at a high level
- Quantization concepts
- Open-weight versus hosted models
- Model capability, context length, latency, and cost trade-offs
- Common failure modes and limitations

### Practice

- Compare model outputs under different generation settings.
- Choose a model using quality, cost, latency, and context requirements.
- Explain the difference between model training and inference.
- Load a small open-weight model and its tokenizer, generate text, and record runtime and memory usage on available hardware.


<br/>


## Level 5: Prompt Engineering and Structured Generation

**Goal:** Produce more reliable outputs through clear instructions, examples, output constraints, and systematic testing.

### Topics

- System and user messages
- Instruction hierarchy at a conceptual level
- Zero-shot, one-shot, and few-shot prompting
- Clear task definitions and relevant context
- Role and style instructions
- Decomposition of complex requests into explicit steps
- Structured outputs and schema-constrained generation
- JSON output and validation with Pydantic
- Extraction, classification, summarization, transformation, and question answering
- Prompt iteration and versioning
- Prompt testing with representative examples
- Hallucination reduction techniques and their limitations
- Prompt injection awareness
- Separating trusted instructions from untrusted input

### Practice

- Build extraction, classification, and summarization prompts.
- Generate schema-validated JSON.
- Compare prompt variants using a fixed set of test cases.
- Record common failure modes and improvements.

**Scope boundary:** Basic tool calling is implemented in Level 6 as an API capability. Agent loops and autonomous orchestration belong to the separate Agentic AI course.


<br/>


## Level 6: LLM APIs and Application Development

**Goal:** Integrate language models into software applications using provider APIs and reliable backend patterns.

### Topics

- Direct model-provider SDKs
- API keys and secret management
- Model initialization and configuration
- Messages and response objects
- Synchronous and asynchronous calls
- Streaming responses
- Batch processing where supported
- Structured output APIs
- Basic tool calling: function schemas, argument validation, allowlisted functions, and returning function results to the model
- Token usage and usage metadata
- Timeouts, retries, rate limits, and error handling
- Provider abstraction and model portability
- FastAPI integration
- Request and response validation
- Basic authentication and access control
- Logging and testing model-backed endpoints

### Practice

- Build a small FastAPI service with model-backed endpoints.
- Implement a streaming response.
- Validate structured model output.
- Add timeouts, retry rules, and safe error handling.
- Implement one application-controlled function call with validated arguments and bounded execution.
- Create a small fixed evaluation dataset and measure output validity, task quality, latency, and cost.

**Prerequisite connection:** Apply the FastAPI, async, authentication, logging, and testing foundations from Level 0 to model-backed services.


<br/>


## Level 7: Embeddings and Semantic Search

**Goal:** Understand how to represent content as vectors and retrieve semantically relevant information.

### Topics

- What embeddings represent
- Text embedding models and their limitations
- Document and query embeddings
- Vector dimensions and normalization
- Cosine similarity, dot product, and distance metrics
- Dense retrieval versus lexical or keyword retrieval
- BM25 as a lexical retrieval baseline
- Sparse retrieval fundamentals
- Approximate nearest-neighbor search
- Vector indexes and index trade-offs
- Metadata filtering
- Access-control-aware retrieval
- Vector indexing libraries such as FAISS versus vector stores/databases such as Chroma, Pinecone, and Weaviate
- Embedding model selection
- Index updates and deletion

### Practice

- Embed a collection of documents.
- Retrieve top-k results for a query.
- Compare semantic search with keyword search.
- Test how chunk size, embedding model, and filters affect retrieval.


<br/>


## Level 8: Retrieval-Augmented Generation (RAG)

**Goal:** Build applications that use retrieved information to ground model responses in a defined knowledge source.

### Topics

- RAG architecture and data flow
- Document ingestion and parsing
- PDF extraction, OCR, tables, and document structure
- Chunking strategies and overlap
- Metadata design and filtering
- Indexing and retrieval
- Dense, sparse, and hybrid retrieval
- Query rewriting and expansion
- Reranking
- Parent-child and multi-stage retrieval concepts
- Context selection and compression
- Grounded answer generation
- Citations and source attribution
- Handling missing evidence and unanswerable questions
- Ingestion updates, re-indexing, and document deletion
- Retrieval permissions and data isolation
- Basic versus advanced RAG patterns
- Common RAG failure modes

### Practice

- Build a PDF question-answering application.
- Build a knowledge-base assistant with source citations.
- Compare retrieval configurations using a fixed evaluation dataset.
- Test unanswerable questions and permission-filtered documents.


<br/>


## Level 9: Multimodal Generative AI

**Goal:** Understand models that process or generate more than one modality, with emphasis on practical applications.

### Topics

- What multimodal models are
- Text-only versus multimodal model capabilities
- Vision-language models (VLMs)
- Image inputs, image understanding, and visual question answering
- Image resolution, crops, patches, and visual token concepts
- Document understanding using text and images
- Audio inputs and outputs
- Speech recognition and text-to-speech concepts
- Audio generation fundamentals
- Video understanding and video generation fundamentals
- Combining text with image, audio, or video inputs
- Multimodal prompting and structured outputs
- Multimodal RAG concepts
- Modality-specific limitations, latency, and cost

### Practice

- Build an image-question-answering application.
- Extract and summarize information from a document containing text and images.
- Experiment with a speech or audio model API.
- Compare model performance on text-only and multimodal inputs.

**Depth guidance:** This level introduces multimodal model capabilities. Image, audio, and video generation techniques are explored further in Level 10 and Level 11.


<br/>


## Level 10: Image Generation with Diffusion Models

**Goal:** Understand and use modern image-generation systems.

### Topics

- Text-to-image generation
- Diffusion model intuition and denoising
- Latent diffusion and latent spaces
- Noise schedules and sampling steps at a conceptual level
- Text encoders and conditioning
- Image-to-image generation
- Inpainting and outpainting
- Guidance and conditioning concepts
- Image-to-image control and adapter-based methods
- Model checkpoints and model selection
- Image generation APIs and open model ecosystems
- GPU and memory requirements
- Image quality, prompt adherence, and generation trade-offs
- Responsible use, licensing, and provenance considerations

### Practice

- Generate images from text prompts.
- Compare prompt variations and generation settings.
- Experiment with image-to-image or inpainting.
- Document quality, runtime, hardware requirements, and limitations.

**Optional extensions:** Detailed diffusion mathematics, training custom diffusion models, and advanced control techniques.


<br/>


## Level 11: Audio, Speech, and Video Generation

**Goal:** Understand the main tasks and workflows for generative audio and video applications.

### Topics

- Speech-to-text and automatic speech recognition
- Text-to-speech and voice generation
- Audio-to-audio and general audio generation concepts
- Audio tokenization and representation at a high level
- Speaker characteristics and expressive speech
- Text, audio, and speech model interfaces
- Video generation fundamentals
- Text-to-video and image-to-video
- Temporal consistency and motion coherence
- Audio-video synchronization concepts
- Real-time and streaming media workflows
- Quality, latency, and compute trade-offs
- Consent, impersonation risks, provenance, and responsible use

### Practice

- Build a speech transcription and summarization workflow.
- Generate speech from text.
- Explore a video-generation API or model.
- Evaluate output quality, processing time, and limitations.

**Depth guidance:** Focus on understanding model capabilities and building applications. Training large audio or video models from scratch is optional.


<br/>


## Level 12: Fine-Tuning and Model Customization

**Goal:** Determine when a model should be customized and understand practical fine-tuning workflows.

**Prerequisites:** Complete the evaluation fundamentals in Level 13 before running fine-tuning experiments. For local training, first learn basic PyTorch tensors, devices, autograd, datasets, and training loops. Hosted fine-tuning does not require implementing a local training loop.

### Topics

- Prompt engineering versus RAG versus fine-tuning
- When fine-tuning is and is not appropriate
- Dataset curation and quality checks
- Training, validation, and test splits
- Instruction-tuning examples and data formats
- Supervised fine-tuning
- Parameter-efficient fine-tuning (PEFT)
- LoRA and adapter concepts
- Training configuration and hyperparameters
- Overfitting and generalization
- Evaluation before and after fine-tuning
- Quantization concepts and QLoRA at a high level
- Model checkpoints and versioning
- Hosted fine-tuning versus local fine-tuning
- Deployment considerations for customized models

### Practice

- Prepare a small instruction-tuning dataset.
- Run a guided fine-tuning exercise on a suitable small model or supported service.
- Compare the base and customized model on a fixed test set.
- Document improvements, regressions, compute needs, and limitations.

**Scope note:** Training foundation models from scratch is outside the core course.


<br/>


## Level 13: GenAI Evaluation and Optimization

**Goal:** Measure application quality systematically and improve it without relying on subjective impressions alone.

### Topics

- Why GenAI evaluation differs from conventional software testing
- Defining task-specific quality criteria
- Golden datasets and representative test cases
- Human evaluation
- Exact-match and task-specific metrics where appropriate
- LLM-as-a-judge: use cases, calibration, and limitations
- Pairwise comparisons and preference evaluation
- Hallucination, correctness, relevance, and faithfulness
- RAG retrieval metrics: Precision@k, Recall@k, MRR, and nDCG
- RAG answer quality and groundedness
- Prompt and model regression testing
- Evaluating structured outputs
- Latency, throughput, token usage, and cost
- Error categorization and failure analysis
- Experiment tracking and reproducibility
- Evaluation gates in CI/CD
- Online feedback and production evaluation

### Practice

- Create an evaluation dataset for a GenAI application.
- Compare two prompts or models using the same dataset.
- Evaluate retrieval separately from answer generation.
- Add automated regression tests and document known failure modes.


<br/>

## Level 14: GenAI Security and Responsible AI

**Goal:** Design GenAI applications that handle untrusted input, sensitive information, and model-generated output safely.

### Topics

- Security risks specific to GenAI systems
- Direct and indirect prompt injection
- Sensitive-data exposure and privacy
- Data leakage through prompts, logs, and model responses
- Untrusted documents and retrieved content
- Input validation and output validation
- Schema validation and safe parsing
- Insecure output handling
- Authentication, authorization, and least privilege
- Retrieval access controls and tenant isolation
- Secrets management
- Content moderation and policy enforcement
- Human review for consequential decisions
- Abuse prevention and rate limiting
- Threat modeling and adversarial testing
- Model and dependency supply-chain risks, artifact provenance, and safe model loading
- Training-data, fine-tuning-data, and retrieval-corpus poisoning
- Resource-exhaustion risks and request, token, concurrency, and budget limits
- Model limitations, bias, fairness, and transparency
- Data retention, licensing, and provenance considerations

### Practice

- Test an application against prompt-injection examples.
- Verify that users cannot retrieve unauthorized documents.
- Check whether logs expose secrets or sensitive content.
- Document threats, mitigations, and remaining risks.

<br/>


## Level 15: Production GenAI Engineering and Portfolio

**Goal:** Deploy and maintain reliable GenAI applications with measurable quality, performance, and cost.

### Application architecture

- Separating API, business logic, model integration, and data access
- Configuration and environment management
- Background jobs and asynchronous processing
- Database and storage integration
- Streaming API design

### Model serving and inference

- Hosted inference APIs versus local inference
- Model serving fundamentals
- Quantization and quality/performance trade-offs
- GPU and memory considerations
- Batching and concurrency
- Throughput and latency optimization
- Model routing and fallback strategies

### Reliability and operations

- Docker and containerization
- CI/CD and automated testing
- Timeouts, retries, rate limits, and circuit-breaking concepts
- Caching and idempotency
- Logging, metrics, and distributed tracing
- LLM observability and request-level traces
- Token usage, cost monitoring, and budget controls
- Load testing and scaling fundamentals
- Secrets management and access controls
- Cloud deployment on AWS, Azure, or GCP
- Incident analysis and production feedback

### Portfolio projects

Build and document at least three substantial projects:

1. **RAG Knowledge Assistant:** Document ingestion, hybrid retrieval, citations, evaluation, and access controls.
2. **Production GenAI API:** FastAPI, structured outputs, streaming, tests, Docker, deployment, and observability.
3. **Specialized Generative AI Application:** Choose a multimodal, image-generation, audio, or fine-tuned-model use case.

Each project should include:

- Clear problem statement and target user
- Architecture and data-flow diagram
- Reproducible setup instructions
- Well-organized source code
- Tests and evaluation methodology
- Evaluation results and known limitations
- Latency and cost measurements where relevant
- Security and privacy considerations
- Deployment instructions or a working demo
- Meaningful Git history and a clear README
- Future improvements

### Practice

- Deploy a GenAI backend.
- Containerize the application.
- Add evaluation and regression tests.
- Measure latency, token usage, and cost.
- Document failures and operational trade-offs.


<br/>


## Recommended Learning Order

```text
Prerequisites
    ↓
Generative AI Fundamentals
    ↓
Generative Model Architectures
    ↓
Transformers and Tokenization
    ↓
LLM Fundamentals and Inference
    ↓
Prompt Engineering and Structured Generation
    ↓
LLM APIs and Application Development
    ↓
Embeddings and Semantic Search
    ↓
RAG Systems
    ↓
Evaluation and Optimization
    ↓
Security and Responsible AI
    ↓
Production Engineering and Portfolio
    ↓
Multimodal Generative AI Overview
    ↓
Selected Specialization: Image, Audio/Video, or Fine-Tuning
```

**Important:** Start evaluation, security, and testing as soon as you build your first model-backed application. Study Levels 13 and 14 systematically after Level 8, then use Level 15 to deploy a core project. Continue with Level 9 and a selected specialization before completing the full portfolio. Level numbers identify chapters; they do not require a strictly numerical study order.

### Level deliverables

Use these deliverables to check readiness before moving on. Add chapter links as notes become available; Level 0's existing notes are linked above.

| Level | Deliverable |
|---|---|
| 0 | A reproducible, tested FastAPI project with validated inputs and safe configuration |
| 1 | A use-case brief explaining suitable models, limitations, and risks |
| 2 | A comparison of generative approaches and architectures |
| 3 | A tokenization experiment and annotated transformer data-flow diagram |
| 4 | An inference comparison with generation settings, runtime, and memory measurements |
| 5 | Versioned prompts producing validated outputs on fixed test cases |
| 6 | A model-backed API with streaming, controlled tool calling, and baseline evaluation |
| 7 | A semantic-search prototype compared with a BM25 baseline |
| 8 | A RAG application with citations, permission checks, and unanswerable-question tests |
| 9 | A multimodal prototype with documented input limitations and evaluation results |
| 10 | An image-generation experiment comparing prompt adherence, settings, and runtime |
| 11 | A speech/audio or video workflow with quality and latency measurements |
| 12 | A base-versus-customized-model report using a held-out test set |
| 13 | A reproducible evaluation suite covering quality, retrieval, latency, and cost |
| 14 | A threat model and adversarial test report with mitigations and remaining risks |
| 15 | Deployed, documented portfolio projects with tests, evaluation, and operational measurements |


<br/>


## What to Prioritize for GenAI Engineering Roles

### Core skills

- Python and backend development
- Transformer and LLM fundamentals
- Model APIs, structured outputs, and prompt engineering
- Embeddings, vector search, and RAG
- Evaluation, testing, and debugging
- Deployment, Docker, monitoring, and cost control
- Security and responsible handling of data

### Specialization skills

- Diffusion-based image generation
- Audio and speech applications
- Video generation
- Fine-tuning and PEFT
- Local inference, quantization, and model serving

Build strong core skills first, then deepen the specializations that fit your target roles.

## What This Course Does Not Cover

To avoid duplication with other courses, the following are intentionally excluded:

- Autonomous AI agents
- Agent planning and multi-step orchestration
- LangChain agent execution loops
- LangGraph stateful agent workflows
- Multi-agent systems
- Agent memory and autonomous decision-making
- MCP-based agent integrations

Basic LLM tool calling, including a single application-controlled function call, is covered in Level 6. Autonomous tool-selection loops, agent orchestration, and agent-framework implementation belong to the separate **Agentic AI** course.


<br/>


## Course Completion Criteria

You should consider the core curriculum complete when you can:

- Explain the major generative model families and their trade-offs.
- Build applications using hosted or open-weight models.
- Design and evaluate a RAG pipeline.
- Explain multimodal capabilities and their limitations.
- Explain when to choose prompting, RAG, or fine-tuning.
- Evaluate quality, retrieval, latency, cost, and failure modes.
- Apply security controls to a model-backed application.
- Deploy and document reliable projects with reproducible tests.

### Specialization and portfolio completion

After completing the core engineering path:

- Complete the Level 9 multimodal overview and build a small multimodal prototype.
- Complete at least one hands-on specialization: image generation (Level 10), audio/speech/video (Level 11), or fine-tuning (Level 12).
- For the fine-tuning specialization, prepare a dataset, run a guided training exercise, and evaluate improvements and regressions on held-out examples.
- Finish the three portfolio projects in Level 15, including the specialized application.

Hands-on media generation and fine-tuning are specialization requirements. Learners do not need to complete every specialization to finish the course portfolio.

The objective is not to memorize every framework or model. It is to understand the principles well enough to select suitable tools, build useful applications, measure their performance, and explain the engineering decisions behind them.
