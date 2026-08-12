package domain

import "errors"

var (
	ErrInvalidFileType       = errors.New("unsupported file type")
	ErrMissingFile           = errors.New("file is required")
	ErrExtractFailed         = errors.New("failed to extract content")
	ErrStorageFailed         = errors.New("failed to store document")
	ErrDocumentPersistFailed = errors.New("failed to persist document")
	ErrDocumentNotFound      = errors.New("document not found")
	ErrUnauthorized          = errors.New("unauthorized")
)
