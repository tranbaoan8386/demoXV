# Python Domain-Driven Design (DDD) Rules - DemoXV Platform

## General Conventions

- Use Python 3.11+ strict type hints everywhere.
- Use Pydantic v2 exclusively for Data Transfer Objects (DTOs) and Request/Response validation in API/UseCase layers.
- Check Agent Skills in `.agent/skills/ai-audit/` and rules in `.agent/rules/` for context before generating code.

## Layer Architecture (`services/ai-audit-service`)

1. **`services/ai-audit-service/app/domain/`**: Pure Python dataclasses, Value Objects, Domain Exceptions, and Abstract Base Classes (`abc.ABC`) for Interfaces.
2. **`services/ai-audit-service/app/usecases/`**: Application business logic orchestrating domain models, RAG flows, and repository interfaces.
3. **`services/ai-audit-service/app/infrastructure/`**: Technical adapters (Postgres DB, Qdrant/Vector DB, LLM & RAG Adapters).
4. **`services/ai-audit-service/app/api/`**: FastAPI routers, middlewares, and Pydantic request/response schemas.

## Strict Domain & Code Guardrails

- **Pure Domain Boundary**: Use standard Python `dataclasses` or pure classes only in `domain/`. Strictly DO NOT import `pydantic`, `SQLAlchemy`, `FastAPI`, `langchain`, or `llama_index` inside `domain/`.
- **Interface Definitions**: Define all Repositories, Vector Stores, and LLM Adapters as `abc.ABC` abstract classes inside `domain/`.
- **Error Handling**: Define custom domain exceptions in `domain/exceptions.py`. Map them directly to standard HTTP status codes in `api/`.
- **Complete Code**: Write full, runnable, production-ready code. Never use `# pass`, `# TODO`, or incomplete placeholder logic.
