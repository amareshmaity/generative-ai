# Generative AI Roadmap for MNC Placement

This roadmap is optimized for two goals:

1. Learn GenAI properly
2. Become job-ready for MNC roles such as GenAI Engineer, AI/ML Engineer, Applied AI Engineer, or LLM Engineer

The focus is not only theory. It is built around the skills companies actually expect:

* Python engineering
* LLM application development
* RAG systems
* APIs and backend integration
* Deployment, evaluation, and production thinking
* Strong portfolio projects

---

## Level 0: Prerequisites

Goal: Build enough foundation to move fast without getting stuck.

### Learn

* Python: OOP, functions, modules, virtual environments
* NumPy and Pandas basics
* SQL basics
* Git and GitHub
* Linear algebra basics: vectors, matrices, dot product
* Probability basics: Bayes, distributions, conditional probability
* Deep learning basics: neural networks, backpropagation, loss functions

### Placement priority

* High: Python, Git, SQL
* Medium: math basics
* Low: very deep theoretical derivations

---

## Level 1: Software Engineering for GenAI

Goal: Become strong enough to build and ship AI applications, not just notebooks.

### Learn

* REST APIs
* FastAPI
* Request and response design
* Async basics
* Authentication basics
* Logging and exception handling
* Environment variables and config management
* Unit testing and API testing
* Working with JSON, files, PDFs, and CSVs

### Build

* A small FastAPI service with 3 to 5 endpoints
* File upload API for document processing
* Basic authentication and logging

### Why this matters

Most MNC GenAI roles expect application engineering skill along with AI knowledge.

---

## Level 2: Deep Learning Core

Goal: Understand the ideas behind modern GenAI systems.

### Learn

* Forward and backward propagation
* Activation functions
* Optimization basics
* Sequence modeling intuition
* Encoder-decoder architecture
* Limitations of RNN and LSTM systems

### Keep this practical

You do not need to become a research scientist for placement.
Understand concepts well enough to explain them in interviews.

---

## Level 3: Transformers

Goal: Master the architecture behind modern LLMs.

### Learn

* Self-attention
* Multi-head attention
* Positional encoding
* Encoder vs decoder vs encoder-decoder
* BERT vs GPT vs T5
* Masked attention
* Tokenization basics
* Context window concept

### Interview expectation

You should be able to clearly explain:

* Why transformers replaced RNNs
* How attention works at a high level
* Difference between encoder and decoder models

---

## Level 4: LLM Fundamentals

Goal: Understand how GPT-like systems are trained and adapted.

### Learn

* Next-token prediction
* Pretraining intuition
* Instruction tuning
* Supervised fine-tuning
* RLHF at a conceptual level
* Safety, hallucination, bias
* Model limits and failure modes

### Placement note

For most MNC roles, conceptual understanding is more important than training a large model from scratch.

---

## Level 5: Prompt Engineering

Goal: Learn how to control and improve LLM output quality.

### Learn

* Zero-shot, one-shot, few-shot prompting
* System prompts and user prompts
* Role prompting
* Structured outputs
* Function or tool calling basics
* Prompt iteration and testing
* Hallucination reduction techniques

### Practice

* Rewrite prompts for better accuracy
* Build prompts for extraction, summarization, classification, and Q and A

---

## Level 6: Embeddings and Vector Search

Goal: Build semantic search and retrieval systems.

### Learn

* What embeddings are
* Similarity search
* Cosine similarity
* Metadata filtering
* Dense search vs keyword search
* Vector databases such as FAISS, Pinecone, Weaviate, Chroma

### Practice

* Create embeddings for documents
* Retrieve top-k relevant chunks
* Compare naive retrieval vs improved retrieval

---

## Level 7: RAG Systems

Goal: Build the most common GenAI application pattern used in industry.

### Learn

* RAG pipeline design
* Chunking strategies
* Retrieval plus generation flow
* Query rewriting
* Hybrid search
* Re-ranking basics
* Context compression
* Grounded answer generation

### Build

* PDF question-answering app
* Internal knowledge base assistant
* Domain-specific chatbot

### Placement priority

This is one of the highest-value sections in the roadmap.

---

## Level 8: Frameworks and Tooling

Goal: Speed up development without becoming framework-dependent.

### Learn

* Hugging Face Transformers
* LangChain
* LlamaIndex
* LangGraph or agent workflow basics

### Rule

Learn the underlying concepts first, then use frameworks to build faster.
Do not become someone who knows only LangChain syntax.

---

## Level 9: Evaluation and Optimization

Goal: Learn how to measure whether your GenAI system is actually good.

### Learn

* Offline evaluation basics
* Human evaluation
* Retrieval quality evaluation
* Response quality evaluation
* Latency vs cost vs quality trade-offs
* Regression testing for prompts and RAG pipelines
* Hallucination analysis

### Important note

This is often missed by learners, but companies care about it a lot.

---

## Level 10: Deployment and Production

Goal: Become industry-ready.

### Learn

* Model APIs such as OpenAI, Hugging Face, Azure OpenAI, AWS Bedrock
* Docker
* CI/CD
* Monitoring and logging
* Rate limits and retries
* Caching
* Cost tracking
* Scaling basics
* Secrets management
* Cloud basics: AWS, Azure, or GCP

### Build

* Deploy one GenAI backend
* Containerize one project
* Add logging, retries, and monitoring

### Placement priority

Very high for MNC roles.

---

## Level 11: Fine-Tuning and Customization

Goal: Know when and how to customize models.

### Learn

* When prompt engineering is enough
* When RAG is enough
* When fine-tuning is needed
* LoRA and PEFT
* Dataset curation
* Fine-tuning workflow at a high level

### Placement note

This is useful, but for many entry-level or early-career GenAI roles, RAG plus application development is more important.

---

## Level 12: Agents and Advanced Workflows

Goal: Build multi-step AI systems that can plan, retrieve, and use tools.

### Learn

* Tool calling
* Function calling
* Multi-step reasoning pipelines
* Agent orchestration basics
* Memory concepts
* Guardrails and safety checks

### Build

* Research assistant
* Multi-tool document workflow
* Agent that uses search, retrieval, and structured outputs

---

## Level 13: Portfolio Projects

Goal: Build proof that you can do real work.

### Minimum project set for placement

* RAG chatbot with FastAPI and deployment
* Document Q and A system with evaluation
* AI content or email generator with structured outputs
* Agentic workflow project with tool calling

### Each project should include

* Clean README
* Architecture diagram
* Screenshots or demo video
* Deployed API or app
* GitHub repo with meaningful commits
* Problem statement
* Tech stack explanation
* Challenges and improvements section

---

## Recommended Learning Order

```text
Python + FastAPI + SQL
-> Transformer basics
-> LLM basics
-> Prompt engineering
-> Embeddings
-> RAG
-> Evaluation
-> Deployment
-> Agents
-> Portfolio projects
```

---

## What to Skip or Keep Light

If your goal is placement, do not spend too much time on:

* Very deep math proofs
* Training large models from scratch
* Too much time on old sequence models
* Too much framework hopping
* Too much tutorial watching without building

---

## What MNCs Usually Look For

A strong candidate for a GenAI role usually has:

* Python and backend development skill
* Good understanding of transformers, LLMs, prompt engineering, and RAG
* Experience with APIs, deployment, Docker, and cloud
* Ability to build end-to-end projects
* Good communication and explanation skill
* Basic DSA, SQL, OOP, and system design for interviews

---

## Placement Strategy

Use this roadmap in this order:

1. Learn the concept
2. Build a small project
3. Deploy it
4. Write about it in GitHub and LinkedIn
5. Prepare interview answers from what you built

The fastest way to get job-ready is project-first learning with enough theory to explain your decisions.

---

## Final Verdict

If your goal is only learning GenAI, this roadmap is strong.

If your goal is MNC placement, focus most on:

* Python backend plus FastAPI
* RAG systems
* Evaluation
* Deployment and cloud
* 3 strong portfolio projects

That combination gives you much better placement value than studying every topic equally.

---

## Next Step

Possible next actions:

1. Create a 45-day placement-focused study plan
2. Make detailed notes for Level 1
3. Design 3 job-ready portfolio projects
4. Turn this roadmap into OneNote-style structured notes
