package domain

import (
	"context"
	"io"
	"mime/multipart"
	"path/filepath"
	"strings"
	"time"
)

const (
	FileTypePDF  = "pdf"
	FileTypeDOCX = "docx"
	FileTypeTXT  = "txt"
)

type ExtractRequest struct {
	File   *multipart.FileHeader
	UserID string
}

type ExtractResult struct {
	DocumentID  string `json:"document_id"`
	Filename    string `json:"filename"`
	Content     string `json:"content"`
	StoragePath string `json:"storage_path"`
	CreatedBy   string `json:"created_by,omitempty"`
}

type Document struct {
	ID          string    `json:"id"`
	Filename    string    `json:"filename"`
	Content     string    `json:"content"`
	StoragePath string    `json:"storage_path"`
	CreatedBy   string    `json:"created_by,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
}

type DocumentExtractor interface {
	Extract(file io.Reader, filename string) (string, error)
	Supports(ext string) bool
}

type DocumentRepository interface {
	Save(ctx context.Context, document *Document) error
	FindByID(ctx context.Context, id string) (*Document, error)
}

type ObjectStorage interface {
	Upload(ctx context.Context, bucket, objectName string, data []byte, contentType string) error
}

func DetectFileType(filename string) string {
	ext := strings.TrimSpace(strings.ToLower(filepath.Ext(filename)))
	ext = strings.TrimPrefix(ext, ".")

	switch ext {
	case FileTypePDF:
		return FileTypePDF
	case FileTypeDOCX:
		return FileTypeDOCX
	case FileTypeTXT:
		return FileTypeTXT
	default:
		return ""
	}
}
