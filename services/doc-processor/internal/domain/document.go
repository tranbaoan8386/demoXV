package domain

import (
	"mime/multipart"
	"path/filepath"
	"strings"
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
	Filename    string `json:"filename"`
	Content     string `json:"content"`
	ExtractedBy string `json:"extracted_by"`
}

type DocumentExtractor interface {
	Extract(file multipart.File, filename string) (string, error)
	Supports(ext string) bool
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
