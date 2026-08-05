package domain

import "errors"

var (
	ErrInvalidFileType = errors.New("unsupported file type")
	ErrMissingFile     = errors.New("file is required")
	ErrExtractFailed   = errors.New("failed to extract content")
	ErrUnauthorized    = errors.New("unauthorized")
)
