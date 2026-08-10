---
name: ai-audit
description: Domain knowledge and implementation guidelines for the Python-based AI Core and Contract Audit Service in `services/ai-audit-service`. Use this skill when working on LLM analysis, RAG pipelines, contract risk detection, vector store integration, or LibreChat tools.
compatibility: Python 3.11+, FastAPI, LlamaIndex/LangChain, Vector DB, Google Gemini API
metadata:
  version: "1.0"
  project: DemoXV
---

# AI Audit & Contract Analysis Service

## Purpose

The `services/ai-audit-service` acts as the core AI engine for the DemoXV platform, specialized in legal contract auditing, compliance checking, and risk extraction.

Its responsibilities include:

- Analyzing legal document text extracted from `doc-processor`.
- Executing Contract Risk Assessment based on legal rules.
- Maintaining RAG (Retrieval-Augmented Generation) pipelines for contract context.
- Exposing REST APIs and Custom Tools/Actions for LibreChat Copilot UI.

---

## Technology Stack

### Language & Framework

- Python 3.11+
- FastAPI (API Framework)
- Pydantic v2 (Validation & Schemas)

### AI / RAG Stack

- Google Gemini API (`google-generativeai`)
- LlamaIndex or LangChain
- Vector Database (ChromaDB / Qdrant / PgVector)

---

## Architecture (Clean Arch + Simple DDD)

```
app/
├── api/ # FastAPI Routers, DTOs
├── usecases/ # RAG Workflows, Audit Services
├── domain/ # Entities, Value Objects, Domain Exceptions
└── infrastructure/ # Gemini API, VectorDB, HTTP Clients (Doc Processor)
Dependencies must point inward toward the Domain layer.

---

## Domain Model

### Aggregates & Entities

**Contract**:

- ID
- DocumentID (references `doc-processor`)
- Clauses (List of `Clause`)
- OverallRiskScore

**Clause** (Value Object):

- Title
- Content
- RiskLevel (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- RiskDescription
- Recommendation

---

## Core Workflows

### Contract Audit Workflow

1. Fetch extracted text from `doc-processor` using `DocumentID`.
2. Segment document text into legal clauses.
3. Query Vector DB for relevant legal compliance guidelines.
4. Call Gemini LLM with structured prompts & JSON Schema output mode.
5. Parse response into `Clause` and `Contract` domain models.
6. Persist audit results and return structured assessment.

---

## API Responsibilities

Primary endpoints:

- POST `/api/v1/audit/contract` - Trigger contract risk evaluation
- GET `/api/v1/audit/contracts/{id}` - Retrieve audit result
- POST `/api/v1/rag/query` - Contextual Q&A over uploaded contracts

Endpoints exposed to LibreChat must provide valid OpenAPI documentation (`/openapi.json`).
```
