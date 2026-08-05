# Doc Processor Service

Microservice để trích xuất nội dung text từ file upload PDF/DOCX/TXT.

## Cấu hình

Copy `.env.example` thành `.env` nếu cần.

```bash
PORT=8081
JWT_SECRET=super-secret-key-change-in-production-2026
APP_ENV=development
```

## Chạy service

```bash
go run .
```

Server chạy ở:

```text
http://localhost:8081
```

## Endpoint

```bash
curl -X POST http://localhost:8081/api/v1/docs/extract \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@sample.pdf"
```

## Kết quả mẫu

```json
{
  "success": true,
  "data": {
    "filename": "sample.pdf",
    "content": "Nội dung văn bản...",
    "extracted_by": "user-id"
  }
}
```
