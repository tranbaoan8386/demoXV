package usecase

import (
	"errors"
	"fmt"
	"mime/multipart"

	"demoxv/doc-processor/internal/domain"
)

type DocumentUsecase struct {
	extractor domain.DocumentExtractor
}

func NewDocumentUsecase(extractor domain.DocumentExtractor) *DocumentUsecase {
	return &DocumentUsecase{extractor: extractor}
}

func (u *DocumentUsecase) ExtractFile(file *multipart.FileHeader, userID string) (*domain.ExtractResult, error) {
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

	content, err := u.extractor.Extract(openedFile, file.Filename)
	if err != nil {
		if errors.Is(err, domain.ErrInvalidFileType) {
			return nil, err
		}
		return nil, fmt.Errorf("%w: %v", domain.ErrExtractFailed, err)
	}

	return &domain.ExtractResult{
		Filename:    file.Filename,
		Content:     content,
		ExtractedBy: userID,
	}, nil
}
