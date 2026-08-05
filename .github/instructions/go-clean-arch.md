# Go Clean Architecture Rules

These rules apply to all Go services in the DemoXV platform.

---

## Language & Style

- Use Go 1.22+ idioms and best practices.
- Prefer simplicity and readability over unnecessary abstractions.
- Keep packages cohesive and focused on a single responsibility.
- Avoid global state.
- Inject dependencies explicitly through constructors (`New...`).
- Always return `error` as the final return value when applicable.
- Handle errors explicitly. Never ignore returned errors.

---

## Dependency Policy

### Standard Library First

Prefer the Go standard library whenever it provides a suitable solution.

Examples include:

- `os`
- `io`
- `context`
- `net/http`
- `encoding/json`
- `fmt`
- `errors`
- `time`
- `sync`

---

### Approved Third-Party Libraries

Use external libraries only when they provide clear value.

Approved libraries include:

- `github.com/gin-gonic/gin`
- `github.com/golang-jwt/jwt/v5`
- `github.com/ledongthuc/pdf`
- `github.com/nguyenthenguyen/docx`

Avoid introducing additional dependencies unless explicitly requested.

---

### Dependency Management

- Never invent package versions.
- Never guess module names.
- Keep dependencies minimal.
- Run `go mod tidy` after dependency changes.
- Prefer replacing unnecessary dependencies with standard library implementations.

---

## Clean Architecture

Use the following architectural layers.

```
Delivery
    ↓
Usecase
    ↓
Domain
    ↓
Repository
```

Dependencies must always point toward the domain.

Outer layers may depend on inner layers.

Inner layers must never depend on outer layers.

---

## Layer Responsibilities

### Domain

Responsibilities:

- Entities
- Value Objects
- Domain Interfaces
- Domain Rules

Requirements:

- Pure Go.
- No HTTP.
- No SQL.
- No ORM.
- No framework imports.
- No infrastructure code.

---

### Usecase

Responsibilities:

- Business logic.
- Application workflows.
- Coordination between domain objects.

Requirements:

- Depends only on domain abstractions.
- No HTTP handling.
- No database implementation.
- No framework-specific logic.

---

### Repository

Responsibilities:

- Persistence.
- Database access.
- External storage integration.

Requirements:

- Implements domain repository interfaces.
- Contains SQL, GORM, or database-specific code.
- Must not contain business rules.

---

### Delivery

Responsibilities:

- HTTP handlers.
- Request validation.
- Response formatting.
- Routing.
- Middleware.

Requirements:

- Invoke usecases.
- Convert HTTP requests into usecase inputs.
- Convert usecase outputs into HTTP responses.
- Must not contain business logic.

---

### Application Entry Point

The application entry point is responsible for:

- Loading configuration.
- Constructing dependencies.
- Performing dependency injection.
- Registering routes.
- Starting the HTTP server.

---

## Dependency Injection

- Perform dependency injection manually.
- Construct dependencies at the application entry point.
- Pass interfaces instead of concrete implementations whenever possible.

---

## Interface Design

- Define interfaces close to where they are consumed.
- Keep interfaces small and focused.
- Avoid unnecessary abstractions.

---

## Code Quality

Generated code must be:

- Complete.
- Runnable.
- Production-ready.
- Maintainable.
- Consistent with the existing project.

Never generate:

- TODO comments.
- Placeholder implementations.
- Stub methods.
- Dummy business logic.

---

## Architecture Constraints

Always preserve Clean Architecture boundaries.

Never:

- Import infrastructure packages into the Domain layer.
- Place business logic inside HTTP handlers.
- Place SQL inside the Usecase layer.
- Place framework-specific code inside the Domain layer.

Business rules belong only in the Usecase and Domain layers.

Infrastructure concerns belong only in the outer layers.
