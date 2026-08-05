# Python Domain-Driven Design (DDD) Rules

These rules apply to all Python services in the DemoXV platform.

---

## Language & Style

- Use Python 3.11+.
- Use strict type hints throughout the codebase.
- Follow modern Python best practices.
- Keep modules focused on a single responsibility.
- Favor composition over inheritance where appropriate.
- Prefer explicit code over implicit behavior.

---

## Data Models

- Use standard `dataclasses` or plain Python classes for Domain models.
- Use Pydantic v2 only for DTOs and API request/response models.
- Keep domain models independent of framework-specific libraries.

---

## Domain-Driven Design

Use the following architectural layers.

```
API
    ↓
Usecases
    ↓
Domain
    ↓
Infrastructure
```

Dependencies must always point toward the Domain.

Outer layers may depend on inner layers.

The Domain layer must never depend on infrastructure or framework code.

---

## Layer Responsibilities

### Domain

Responsibilities:

- Entities
- Value Objects
- Domain Services
- Domain Events
- Repository Interfaces
- Domain Exceptions

Requirements:

- Pure Python only.
- No FastAPI.
- No Pydantic.
- No SQLAlchemy.
- No LangChain.
- No LlamaIndex.
- No infrastructure dependencies.

Use `abc.ABC` for repository and service interfaces.

---

### Usecases

Responsibilities:

- Application business logic.
- Workflow orchestration.
- Coordination between domain objects and repositories.

Requirements:

- Depend only on Domain abstractions.
- Contain no HTTP handling.
- Contain no persistence implementation.
- Coordinate external services through interfaces.

---

### Infrastructure

Responsibilities:

- Database access.
- Vector database integration.
- LLM adapters.
- RAG adapters.
- External services.
- File storage.

Requirements:

- Implement interfaces defined by the Domain.
- Contain framework-specific integrations.
- Contain no business rules.

---

### API

Responsibilities:

- FastAPI routers.
- Request validation.
- Response serialization.
- Authentication.
- Middleware.
- Exception mapping.

Requirements:

- Use Pydantic v2 models.
- Invoke usecases.
- Convert HTTP requests into usecase inputs.
- Convert usecase outputs into HTTP responses.
- Do not implement business logic.

---

## Interface Design

- Define interfaces using `abc.ABC`.
- Keep interfaces small and cohesive.
- Define abstractions close to the Domain.

---

## Exception Handling

- Define domain-specific exceptions inside the Domain layer.
- Translate domain exceptions into HTTP responses only within the API layer.
- Avoid leaking infrastructure exceptions into business logic.

---

## Dependency Injection

- Inject dependencies through constructors or dependency providers.
- Depend on abstractions rather than concrete implementations.
- Keep object construction outside business logic.

---

## Code Quality

Generated code must be:

- Complete.
- Runnable.
- Production-ready.
- Fully typed.
- Maintainable.
- Consistent with the existing project.

Never generate:

- `pass`
- `TODO`
- Placeholder implementations.
- Incomplete business logic.

---

## Architecture Constraints

Always preserve Domain-Driven Design boundaries.

Never:

- Import FastAPI into the Domain layer.
- Import Pydantic into the Domain layer.
- Import SQLAlchemy into the Domain layer.
- Import LangChain or LlamaIndex into the Domain layer.
- Place business logic inside API routers.
- Place persistence logic inside Usecases.

Business rules belong only in the Domain and Usecase layers.

Infrastructure concerns belong only in the Infrastructure layer.
