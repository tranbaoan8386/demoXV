# Skill: SSO Authentication Module

## Business Context
Target: services/sso-service
Language: Go
Scope: User Management, Password Hashing, JWT Token Issuance & Verification.

## Deliverables
1. internal/domain/user.go: User entity, RegisterDTO, LoginDTO, and UserRepository interface.
2. internal/usecase/auth_usecase.go: Business logic for Register and Login.
3. internal/repository/postgres_user_repo.go: Database persistence layer.
4. internal/delivery/http/auth_handler.go: Gin HTTP endpoints (/auth/register, /auth/login, /auth/verify).
