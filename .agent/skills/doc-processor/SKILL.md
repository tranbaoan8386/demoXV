---
name: doc-processor
description: Knowledge and implementation guidance for the Go-based Document Processor service located in `services/doc-processor`. Use this skill whenever working on document ingestion, storage, metadata management, text extraction, or document processing workflows.
compatibility: Go 1.22+, PostgreSQL, MinIO, PDF, DOCX, Excel, TXT
metadata:
  version: "1.1"
  project: DemoXV
---

# Document Processor Service

## Purpose

The `services/doc-processor` service is responsible for document ingestion, storage, metadata management, and text extraction across the DemoXV platform.

Its responsibilities include:

- Document upload
- Object storage
- Metadata persistence
- Text extraction
- Processing status management
- Document retrieval

The service is responsible only for document processing. AI analysis, embedding generation, and business-specific workflows should remain in downstream services.

---

## Technology Stack

### Language

- Go

### Database

- PostgreSQL

### Object Storage

- MinIO

### Supported Extractors

- PDF (`github.com/ledongthuc/pdf`)
- DOCX (`github.com/nguyenthenguyen/docx`)
- Excel (`github.com/xuri/excelize/v2`)
- TXT (Go standard library)

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

pkg/
└── extractor/

scripts/
```

---

## Domain Model

Primary entity:

### Document

Typical fields:

- ID
- FileName
- FileType
- FileSize
- StorageKey
- Status
- ExtractedText
- CreatedAt
- UpdatedAt

The Domain layer contains only:

- Entities
- Value Objects
- Repository Interfaces

No database models, HTTP models, framework annotations, or infrastructure code belong in this layer.

---

## Document Processing Flow

### Upload

1. Validate the uploaded file.
2. Store the original file in MinIO.
3. Persist document metadata in PostgreSQL.
4. Create the initial processing status.
5. Return the document identifier.

### Extraction

1. Load the stored document.
2. Select the appropriate extractor based on file type.
3. Extract textual content.
4. Update extracted content and processing status.
5. Persist the result.

### Retrieval

1. Retrieve metadata from PostgreSQL.
2. Retrieve file content from MinIO if required.
3. Return document information.

---

## Repository Responsibilities

The repository layer is responsible only for persistence.

Typical operations include:

### Metadata Repository

- CreateDocument
- GetDocumentByID
- ListDocuments
- UpdateDocument
- DeleteDocument

### Object Storage Repository

- UploadObject
- DownloadObject
- DeleteObject

Business rules must remain in the Usecase layer.

---

## Extractor Responsibilities

Each extractor is responsible only for converting supported document formats into plain text.

Supported formats include:

- PDF
- DOCX
- Excel
- TXT

Extractors should not contain business logic or persistence logic.

---

## HTTP API Responsibilities

Typical endpoints include:

- POST `/documents`
- GET `/documents`
- GET `/documents/{id}`
- DELETE `/documents/{id}`

HTTP handlers should:

- Validate requests.
- Invoke usecases.
- Convert results into HTTP responses.
- Handle HTTP status codes.

Business logic must never be implemented in HTTP handlers.

---

## Storage Guidelines

### PostgreSQL

Store structured metadata such as:

- Document identifiers
- File information
- Processing status
- Timestamps

### MinIO

Store original document files.

Object storage should never contain application metadata.

---

## Integration Guidelines

The Document Processor is the single source of truth for document storage and text extraction within the DemoXV platform.

Downstream services should consume extracted text and metadata from this service instead of implementing their own document parsing logic.
