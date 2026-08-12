package postgres

import (
	"context"
	"database/sql"
	"fmt"

	"demoxv/doc-processor/internal/domain"
)

type DocumentRepository struct {
	db *sql.DB
}

func NewDocumentRepository(db *sql.DB) *DocumentRepository {
	return &DocumentRepository{db: db}
}

func (r *DocumentRepository) Save(ctx context.Context, document *domain.Document) error {
	_, err := r.db.ExecContext(ctx, `
		INSERT INTO documents (id, filename, content, storage_path, created_by, created_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`, document.ID, document.Filename, document.Content, document.StoragePath, nilIfEmpty(document.CreatedBy), document.CreatedAt)
	if err != nil {
		return fmt.Errorf("insert document: %w", err)
	}
	return nil
}

func (r *DocumentRepository) FindByID(ctx context.Context, id string) (*domain.Document, error) {
	row := r.db.QueryRowContext(ctx, `
		SELECT id, filename, content, storage_path, created_by, created_at
		FROM documents
		WHERE id = $1
	`, id)

	document := &domain.Document{}
	var createdBy sql.NullString
	err := row.Scan(&document.ID, &document.Filename, &document.Content, &document.StoragePath, &createdBy, &document.CreatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, domain.ErrDocumentNotFound
		}
		return nil, fmt.Errorf("select document: %w", err)
	}
	if createdBy.Valid {
		document.CreatedBy = createdBy.String
	}

	return document, nil
}

func (r *DocumentRepository) List(ctx context.Context, userID string) ([]*domain.Document, error) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT id, filename, content, storage_path, created_by, created_at
		FROM documents
		WHERE ($1 = '' OR created_by::text = $1)
		ORDER BY created_at DESC
	`, userID)
	if err != nil {
		return nil, fmt.Errorf("list documents: %w", err)
	}
	defer rows.Close()

	var documents []*domain.Document
	for rows.Next() {
		document := &domain.Document{}
		var createdBy sql.NullString
		if err := rows.Scan(&document.ID, &document.Filename, &document.Content, &document.StoragePath, &createdBy, &document.CreatedAt); err != nil {
			return nil, fmt.Errorf("scan document: %w", err)
		}
		if createdBy.Valid {
			document.CreatedBy = createdBy.String
		}
		documents = append(documents, document)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate documents: %w", err)
	}

	return documents, nil
}

func nilIfEmpty(value string) interface{} {
	if value == "" {
		return nil
	}
	return value
}
