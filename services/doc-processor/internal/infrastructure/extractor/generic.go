package extractor

import (
	"bytes"
	"io"
	"path/filepath"
	"strings"

	"demoxv/doc-processor/internal/domain"
	"github.com/ledongthuc/pdf"
	"github.com/nguyenthenguyen/docx"
)

type GenericExtractor struct{}

func NewGenericExtractor() *GenericExtractor {
	return &GenericExtractor{}
}

func (e *GenericExtractor) Supports(ext string) bool {
	switch strings.ToLower(ext) {
	case domain.FileTypePDF, domain.FileTypeDOCX, domain.FileTypeTXT:
		return true
	default:
		return false
	}
}

func (e *GenericExtractor) Extract(file io.Reader, filename string) (string, error) {
	ext := strings.TrimPrefix(strings.ToLower(filepath.Ext(filename)), ".")

	if !e.Supports(ext) {
		return "", domain.ErrInvalidFileType
	}

	data, err := io.ReadAll(file)
	if err != nil {
		return "", err
	}

	switch ext {
	case domain.FileTypeTXT:
		return normalizeExtractedText(string(data)), nil
	case domain.FileTypePDF:
		return extractPDFText(data)
	case domain.FileTypeDOCX:
		return extractDOCXText(data)
	default:
		return "", domain.ErrInvalidFileType
	}
}

func extractPDFText(data []byte) (string, error) {
	reader, err := pdf.NewReader(bytes.NewReader(data), int64(len(data)))
	if err != nil {
		return "", err
	}

	plainTextReader, err := reader.GetPlainText()
	if err != nil {
		return "", err
	}

	content, err := io.ReadAll(plainTextReader)
	if err != nil {
		return "", err
	}

	return normalizeExtractedText(string(content)), nil
}

func extractDOCXText(data []byte) (string, error) {
	doc, err := docx.ReadDocxFromMemory(bytes.NewReader(data), int64(len(data)))
	if err != nil {
		return "", err
	}
	defer doc.Close()

	text := doc.Editable().GetContent()
	return normalizeExtractedText(text), nil
}

func normalizeExtractedText(value string) string {
	if value == "" {
		return ""
	}
	return strings.Join(strings.Fields(value), " ")
}
