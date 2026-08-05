---
name: sso-module
description: Knowledge and implementation guidance for the Go-based Single Sign-On (SSO) service located in `services/sso-service`. Use this skill whenever working on authentication, user management, JWT, password hashing, or PostgreSQL persistence for the SSO service.
compatibility: Go 1.20+, PostgreSQL, Gin, bcrypt, JWT
metadata:
  version: "1.1"
  project: DemoXV
---

# SSO Authentication Service

## Purpose

The `services/sso-service` provides centralized authentication and identity management for the DemoXV platform.

Its responsibilities include:

- User registration
- User authentication
- Password hashing
- JWT issuance
- JWT verification
- User persistence
- Authentication APIs

The service is responsible only for authentication and identity management. Business logic unrelated to authentication must remain in other services.

---

## Technology Stack

### Language

- Go

### Web Framework

- Gin

### Database

- PostgreSQL

### Authentication

- JWT (`github.com/golang-jwt/jwt/v5`)

### Password Security

- bcrypt (`golang.org/x/crypto/bcrypt`)

---

## Architecture

The service follows Clean Architecture.

```
Delivery
    ↓
Usecase
    ↓
Domain
    ↓
Repository
```

Dependencies must always point inward.

The Domain layer must remain independent of infrastructure frameworks.

---

## Directory Structure

Typical layout:

```
cmd/
└── api/

internal/
├── domain/
├── usecase/
├── repository/
└── delivery/

scripts/
```

---

## Domain Model

Primary entity:

### User

Typical fields:

- ID
- Username
- Email
- PasswordHash
- CreatedAt
- UpdatedAt

The Domain layer contains only:

- Entities
- Value Objects
- Repository Interfaces

No database models, HTTP models, framework annotations, or infrastructure code belong in this layer.

---

## Authentication Flow

### Register

1. Validate request.
2. Verify the user does not already exist.
3. Hash the password using bcrypt.
4. Persist the new user.
5. Return a success response.

### Login

1. Retrieve the user by identifier.
2. Compare the supplied password using bcrypt.
3. Generate a JWT access token.
4. Return the authentication result.

### Verify

1. Parse the JWT.
2. Validate its signature.
3. Validate expiration and claims.
4. Return the authenticated identity.

---

## Repository Responsibilities

The repository layer is responsible only for persistence.

Typical operations include:

- CreateUser
- GetUserByID
- GetUserByEmail
- UpdateUser
- DeleteUser (if supported)

Business rules must remain in the Usecase layer.

---

## HTTP API Responsibilities

Typical endpoints include:

- POST `/auth/register`
- POST `/auth/login`
- POST `/auth/verify`

HTTP handlers should:

- Validate requests.
- Invoke usecases.
- Convert results into HTTP responses.
- Handle HTTP status codes.

Business logic must never be implemented in HTTP handlers.

---

## Security Guidelines

### Passwords

- Never store plaintext passwords.
- Always hash passwords using bcrypt.
- Never expose password hashes through APIs.

### JWT

- Sign tokens securely.
- Validate signatures before trusting claims.
- Validate expiration.
- Reject malformed or expired tokens.
- Never trust client-provided identity without verification.

---

## Integration Guidelines

The SSO service is the single source of truth for authentication within the DemoXV platform.

Other services should consume authentication through this service instead of implementing their own authentication logic.
