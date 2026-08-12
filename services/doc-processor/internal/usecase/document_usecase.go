package usecase

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"path/filepath"
	"strings"
	"time"

	"demoxv/doc-processor/internal/domain"

	"github.com/google/uuid"
)

type DocumentUsecase struct {
	extractor domain.DocumentExtractor
	repo      domain.DocumentRepository
	storage   domain.ObjectStorage
	bucket    string
}

func NewDocumentUsecase(extractor domain.DocumentExtractor, repo domain.DocumentRepository, storage domain.ObjectStorage, bucket string) *DocumentUsecase {
	return &DocumentUsecase{extractor: extractor, repo: repo, storage: storage, bucket: bucket}
}

func (u *DocumentUsecase) ExtractFile(ctx context.Context, file *multipart.FileHeader, userID string) (*domain.ExtractResult, error) {
	if file == nil {
		return nil, domain.ErrMissingFile
	}

	fileType := domain.DetectFileType(file.Filename)
	if !u.extractor.Supports(fileType) {
		return nil, domain.ErrInvalidFileType
	}

	openedFile, err := file.Open()
	if err != nil {
		return nil, fmt.Errorf("open uploaded file: %w", err)
	}
	defer openedFile.Close()

	data, err := io.ReadAll(openedFile)
	if err != nil {
		return nil, fmt.Errorf("read uploaded file: %w", err)
	}

	content, err := u.extractor.Extract(bytes.NewReader(data), file.Filename)
	if err != nil {
		if errors.Is(err, domain.ErrInvalidFileType) {
			return nil, err
		}
		return nil, fmt.Errorf("%w: %v", domain.ErrExtractFailed, err)
	}

	storagePath := buildStoragePath(file.Filename)
	if err := u.storage.Upload(ctx, u.bucket, storagePath, data, detectContentType(file.Filename, data)); err != nil {
		return nil, fmt.Errorf("%w: %v", domain.ErrStorageFailed, err)
	}

	document := &domain.Document{
		ID:          uuid.NewString(),
		Filename:    file.Filename,
		Content:     content,
		StoragePath: storagePath,
		CreatedBy:   userID,
		CreatedAt:   time.Now().UTC(),
	}

	if err := u.repo.Save(ctx, document); err != nil {
		return nil, fmt.Errorf("%w: %v", domain.ErrDocumentPersistFailed, err)
	}

	return &domain.ExtractResult{
		DocumentID:  document.ID,
		Filename:    document.Filename,
		Content:     document.Content,
		StoragePath: document.StoragePath,
		CreatedBy:   document.CreatedBy,
	}, nil
}

func (u *DocumentUsecase) GetDocument(ctx context.Context, documentID string) (*domain.Document, error) {
	return u.repo.FindByID(ctx, documentID)
}

func (u *DocumentUsecase) ListDocuments(ctx context.Context, userID string) ([]*domain.Document, error) {
	return u.repo.List(ctx, userID)
}

func buildStoragePath(filename string) string {
	now := time.Now().UTC()
	safeName := strings.NewReplacer(" ", "_", "/", "_", "\\", "_", ":", "_").Replace(filename)
	return fmt.Sprintf("%d/%02d/%02d/%s_%s", now.Year(), now.Month(), now.Day(), uuid.NewString(), safeName)
}

func detectContentType(filename string, data []byte) string {
	ext := strings.TrimPrefix(strings.ToLower(filepath.Ext(filename)), ".")
	switch ext {
	case domain.FileTypePDF:
		return "application/pdf"
	case domain.FileTypeDOCX:
		return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
	case domain.FileTypeTXT:
		return "text/plain; charset=utf-8"
	default:
		return http.DetectContentType(data)
	}
}
