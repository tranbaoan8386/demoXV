package domain

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"time"
)

var (
	ErrUserNotFound       = errors.New("user not found")
	ErrUserAlreadyExists  = errors.New("user already exists")
	ErrInvalidEmail       = errors.New("invalid email")
	ErrInvalidUsername    = errors.New("invalid username")
	ErrInvalidFullName    = errors.New("invalid full name")
	ErrWeakPassword       = errors.New("password is too weak")
	ErrInvalidCredentials = errors.New("invalid credentials")
)

type User struct {
	ID           string    `json:"id"`
	Email        string    `json:"email"`
	Username     string    `json:"username"`
	FullName     string    `json:"full_name"`
	PasswordHash string    `json:"-"`
	Role         string    `json:"role"`
	Status       string    `json:"status"`
	IsActive     bool      `json:"is_active"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

type RegisterDTO struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	FullName string `json:"full_name"`
	Password string `json:"password"`
}

type LoginDTO struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type UserRepository interface {
	Create(ctx context.Context, user *User) error
	GetByEmail(ctx context.Context, email string) (*User, error)
	GetByID(ctx context.Context, id string) (*User, error)
}

func (dto *RegisterDTO) Validate() error {
	if strings.TrimSpace(dto.Email) == "" {
		return ErrInvalidEmail
	}
	if !isValidEmail(dto.Email) {
		return ErrInvalidEmail
	}
	if strings.TrimSpace(dto.Username) == "" {
		return ErrInvalidUsername
	}
	if len(strings.TrimSpace(dto.Username)) < 3 {
		return ErrInvalidUsername
	}
	if strings.TrimSpace(dto.FullName) == "" {
		return ErrInvalidFullName
	}
	if len(strings.TrimSpace(dto.FullName)) < 3 {
		return ErrInvalidFullName
	}
	if len(dto.Password) < 8 {
		return ErrWeakPassword
	}
	return nil
}

func (dto *LoginDTO) Validate() error {
	if strings.TrimSpace(dto.Email) == "" || !isValidEmail(dto.Email) {
		return ErrInvalidEmail
	}
	if len(strings.TrimSpace(dto.Password)) == 0 {
		return ErrInvalidCredentials
	}
	return nil
}

func (u *User) Validate() error {
	if strings.TrimSpace(u.Email) == "" || !isValidEmail(u.Email) {
		return ErrInvalidEmail
	}
	if strings.TrimSpace(u.Username) == "" || len(strings.TrimSpace(u.Username)) < 3 {
		return ErrInvalidUsername
	}
	if strings.TrimSpace(u.FullName) == "" || len(strings.TrimSpace(u.FullName)) < 3 {
		return ErrInvalidFullName
	}
	if strings.TrimSpace(u.PasswordHash) == "" {
		return ErrWeakPassword
	}
	if strings.TrimSpace(u.ID) == "" {
		return fmt.Errorf("user id is required")
	}
	if strings.TrimSpace(u.Role) == "" {
		u.Role = "user"
	}
	return nil
}

func isValidEmail(email string) bool {
	trimmed := strings.TrimSpace(email)
	if trimmed == "" {
		return false
	}
	at := strings.Index(trimmed, "@")
	if at <= 0 || at == len(trimmed)-1 {
		return false
	}
	dot := strings.LastIndex(trimmed, ".")
	if dot <= at+1 || dot == len(trimmed)-1 {
		return false
	}
	return true
}
