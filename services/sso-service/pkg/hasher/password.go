package hasher

import (
	"errors"
	"strings"

	"golang.org/x/crypto/bcrypt"
)

type PasswordHasher interface {
	Hash(password string) (string, error)
	Compare(hashedPassword string, password string) error
}

type BcryptHasher struct{}

func NewBcryptHasher() *BcryptHasher {
	return &BcryptHasher{}
}

func (h *BcryptHasher) Hash(password string) (string, error) {
	trimmed := strings.TrimSpace(password)
	if trimmed == "" {
		return "", errors.New("password cannot be empty")
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(trimmed), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}

	return string(hash), nil
}

func (h *BcryptHasher) Compare(hashedPassword string, password string) error {
	trimmedHash := strings.TrimSpace(hashedPassword)
	trimmedPassword := strings.TrimSpace(password)
	if trimmedHash == "" {
		return errors.New("password hash is empty")
	}
	if trimmedPassword == "" {
		return errors.New("password cannot be empty")
	}

	return bcrypt.CompareHashAndPassword([]byte(trimmedHash), []byte(trimmedPassword))
}
