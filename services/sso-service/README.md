# SSO Service

Service xác thực người dùng cho DemoXV, triển khai Clean Architecture với Go. Hỗ trợ:

- Register
- Login
- JWT Verify
- Postgres persistence

## 1. Cấu hình môi trường

Copy file `.env.example` thành `.env`:

```bash
copy .env.example .env
```

Các biến môi trường mẫu:

```env
PORT=8080
JWT_SECRET=demoxv-sso-secret-key-change-me

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sso_service
DATABASE_URL=postgres://postgres:postgres@localhost:5432/sso_service?sslmode=disable
```

## 2. Chạy service

```bash
go run ./cmd/api
```

Mặc định server chạy tại:

```text
http://localhost:8080
```

## 3. Test API bằng cURL

### Register

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
```

### Verify token

```bash
curl -X POST http://localhost:8080/api/auth/verify \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

## 4. Chạy migration SQL vào Postgres

### Tạo database (nếu chưa có)

```bash
psql -U postgres -h localhost -d postgres -c "CREATE DATABASE sso_service;"
```

### Chạy migration

```bash
psql -U postgres -h localhost -d sso_service -f migrations/000001_create_users_table.up.sql
```

### Rollback migration

```bash
psql -U postgres -h localhost -d sso_service -f migrations/000001_create_users_table.down.sql
```

## 5. Chạy unit test

```bash
go test ./...
```

## 6. Ghi chú

- Password được hash bằng BCrypt.
- JWT sử dụng secret từ biến môi trường `JWT_SECRET`.
- API response tuân theo format chuẩn:
  - Success: `{"success": true, "data": ...}`
  - Error: `{"success": false, "error": {"code": "...", "message": "..."}}`
