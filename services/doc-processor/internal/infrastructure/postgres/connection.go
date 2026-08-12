package postgres

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

func NewConnection(databaseURL string) (*sql.DB, error) {
	if databaseURL == "" {
		return nil, fmt.Errorf("database url is required")
	}

	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("open postgres connection: %w", err)
	}

	if err := db.Ping(); err != nil {
		db.Close()
		return nil, fmt.Errorf("ping postgres: %w", err)
	}

	return db, nil
}

func EnsureDocumentsTable(db *sql.DB) error {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS documents (
			id UUID PRIMARY KEY,
			filename VARCHAR(255) NOT NULL,
			content TEXT NOT NULL,
			storage_path VARCHAR(500) NOT NULL,
			created_by UUID NULL,
			created_at TIMESTAMP NOT NULL
		)
	`)
	return err
}
