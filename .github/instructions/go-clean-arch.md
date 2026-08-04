# Go Clean Architecture Rules - DemoXV Platform

## General Conventions

- Use Go 1.22+ standard idioms.
- Avoid global state. Inject dependencies explicitly via constructors (`New...`).
- Explicit error handling: always return `error` as the last return parameter.
- Check Agent Skills in `.agent/skills/` and rules in `.agent/rules/` for context before generating code.

## Structure Rules (`services/sso-service` & `services/doc-processor`)

1. **`internal/domain/`**: Defines Domain Model structs & Repository Interfaces. Pure Go standard library ONLY.
2. **`internal/usecase/`**: Business logic execution. Receives interfaces from `domain/`.
3. **`internal/repository/`**: Implements `domain/` repository interfaces with Postgres/SQL/GORM.
4. **`internal/delivery/http/`**: Handles REST API requests, routes, and middleware using Gin or standard `net/http`.
5. **`cmd/api/main.go`**: Entry point for manual Dependency Injection and HTTP server initialization.

## Strict Clean Arch Guardrails

- **Domain Layer Isolation**: Pure Go code only. No imports of `gin-gonic`, `lib/pq`, `gorm`, or external framework packages inside `internal/domain/`.
- **Interface Definitions**: Define interfaces where they are consumed or inside `domain/repository/`, never inside the implementation layer.
- **Dependency Injection**: Assemble and wire all dependencies manually inside `cmd/api/main.go`.
- **Complete Code**: Write full, runnable, production-ready Go code. Never use `// TODO`, `/* implement here */`, or placeholder logic.
