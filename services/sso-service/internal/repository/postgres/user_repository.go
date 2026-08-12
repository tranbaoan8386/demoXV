package postgres

import (
	"context"
	"database/sql"
	"errors"

	"demoxv/sso-service/internal/domain"
)

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) Create(ctx context.Context, user *domain.User) error {
	if r.db == nil {
		return errors.New("database connection is nil")
	}

	if user == nil {
		return errors.New("user is nil")
	}

	query := `
		INSERT INTO users (
			id,
			email,
			username,
			password_hash,
			full_name,
			role,
			status,
			is_active,
			created_at,
			updated_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
	`

	_, err := r.db.ExecContext(
		ctx,
		query,
		user.ID,
		user.Email,
		user.Username,
		user.PasswordHash,
		user.FullName,
		defaultString(user.Role, "user"),
		defaultString(user.Status, "active"),
		user.IsActive,
		user.CreatedAt,
		user.UpdatedAt,
	)
	if err != nil {
		return err
	}

	return nil
}

func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
	if r.db == nil {
		return nil, errors.New("database connection is nil")
	}

	query := `
		SELECT id, email, username, password_hash, full_name, role, status, is_active, created_at, updated_at
		FROM users
		WHERE email = $1
		LIMIT 1
	`

	row := r.db.QueryRowContext(ctx, query, email)
	return scanUser(row)
}

func (r *UserRepository) GetByID(ctx context.Context, id string) (*domain.User, error) {
	if r.db == nil {
		return nil, errors.New("database connection is nil")
	}

	query := `
		SELECT id, email, username, password_hash, full_name, role, status, is_active, created_at, updated_at
		FROM users
		WHERE id = $1
		LIMIT 1
	`

	row := r.db.QueryRowContext(ctx, query, id)
	return scanUser(row)
}

func scanUser(row *sql.Row) (*domain.User, error) {
	var user domain.User

	err := row.Scan(
		&user.ID,
		&user.Email,
		&user.Username,
		&user.PasswordHash,
		&user.FullName,
		&user.Role,
		&user.Status,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domain.ErrUserNotFound
		}
		return nil, err
	}

	return &user, nil
}

func defaultString(value string, fallback string) string {
	if value == "" {
		return fallback
	}
	return value
}
