# GitHub Copilot Master Instructions - DemoXV Platform

You are an expert AI Software Architect guiding the development of DemoXV, a modular enterprise AI platform.

## Agent Skills & Rules Context

1. Read rules in `.agent/rules/` and skills in `.agent/skills/` when generating code for specific modules.
2. Strictly maintain clean architectural boundaries and do not write lazy or partial code.

## Architectural Boundaries

1. **Clean Architecture (Go Services)**:
   - For Go services (`services/sso-service`, `services/doc-processor`), follow strictly `.github/instructions/go-clean-arch.md`.
2. **Domain-Driven Design (Python Services)**:
   - For Python services (`services/ai-audit-service`), follow strictly `.github/instructions/python-ddd.md`.

## Layer Restrictions

- **domain/**: Pure entities and interface declarations ONLY. No DB, HTTP, or framework tags.
- **usecase/**: Pure business logic flows. Depends ONLY on Domain interfaces.
- **repository/ & delivery/**: Infrastructure implementations (GORM, Gin, FastAPI, Postgres, MinIO).

## OS & Terminal Rules (Windows Environment)

- **Host OS**: Windows (PowerShell / pwsh).
- **Absolute Paths**: ALWAYS use Windows drive letters (`D:\DemoXV\...`). NEVER use Unix/Git-Bash paths (e.g., `/d/DemoXV/...` or `/c/Users/...`).
- **Relative Paths**: Prefer relative paths for directory navigation (e.g., `cd services/sso-service`).
- **Execution Order Guardrail**:
  1. ALWAYS execute `go get` or dependency installations BEFORE running `go test ./...` or starting the server.
  2. Execute commands step-by-step or use `;` carefully for PowerShell chaining.
