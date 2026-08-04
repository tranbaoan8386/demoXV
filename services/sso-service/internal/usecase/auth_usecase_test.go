package usecase

import (
	"context"
	"testing"

	"demoxv/sso-service/internal/domain"
	"demoxv/sso-service/pkg/hasher"
	"demoxv/sso-service/pkg/token"
)

type inMemoryUserRepository struct {
	users map[string]*domain.User
}

func newInMemoryUserRepository() *inMemoryUserRepository {
	return &inMemoryUserRepository{users: make(map[string]*domain.User)}
}

func (r *inMemoryUserRepository) Create(_ context.Context, user *domain.User) error {
	r.users[user.Email] = user
	return nil
}

func (r *inMemoryUserRepository) GetByEmail(_ context.Context, email string) (*domain.User, error) {
	user, ok := r.users[email]
	if !ok {
		return nil, domain.ErrUserNotFound
	}
	return user, nil
}

func (r *inMemoryUserRepository) GetByID(_ context.Context, id string) (*domain.User, error) {
	for _, user := range r.users {
		if user.ID == id {
			return user, nil
		}
	}
	return nil, domain.ErrUserNotFound
}

func TestAuthUsecase_Register_Success(t *testing.T) {
	repo := newInMemoryUserRepository()
	uc := NewAuthUsecase(repo, hasher.NewBcryptHasher(), token.NewJWTService("test-secret"))

	user, token, err := uc.Register(context.Background(), domain.RegisterDTO{
		Email:    "alice@example.com",
		FullName: "Alice Nguyen",
		Password: "password123",
	})
	if err != nil {
		t.Fatalf("Register() unexpected error: %v", err)
	}
	if user == nil {
		t.Fatal("Register() returned nil user")
	}
	if token == "" {
		t.Fatal("Register() returned empty token")
	}
	if user.PasswordHash == "" {
		t.Fatal("Register() did not hash password")
	}
	if got, err := repo.GetByEmail(context.Background(), "alice@example.com"); err != nil || got == nil {
		t.Fatalf("saved user lookup failed: %v, %v", err, got)
	}
}

func TestAuthUsecase_Register_DuplicateEmail(t *testing.T) {
	repo := newInMemoryUserRepository()
	uc := NewAuthUsecase(repo, hasher.NewBcryptHasher(), token.NewJWTService("test-secret"))

	_, _, err := uc.Register(context.Background(), domain.RegisterDTO{
		Email:    "dup@example.com",
		FullName: "Duplicate User",
		Password: "password123",
	})
	if err != nil {
		t.Fatalf("first Register() unexpected error: %v", err)
	}

	_, _, err = uc.Register(context.Background(), domain.RegisterDTO{
		Email:    "dup@example.com",
		FullName: "Duplicate User 2",
		Password: "password456",
	})
	if err == nil {
		t.Fatal("Register() expected duplicate email error")
	}
	if err != domain.ErrUserAlreadyExists {
		t.Fatalf("Register() error = %v, want %v", err, domain.ErrUserAlreadyExists)
	}
}

func TestAuthUsecase_Login_WrongPassword(t *testing.T) {
	repo := newInMemoryUserRepository()
	uc := NewAuthUsecase(repo, hasher.NewBcryptHasher(), token.NewJWTService("test-secret"))

	_, _, err := uc.Register(context.Background(), domain.RegisterDTO{
		Email:    "bob@example.com",
		FullName: "Bob Nguyen",
		Password: "correctpass",
	})
	if err != nil {
		t.Fatalf("Register() unexpected error: %v", err)
	}

	_, _, err = uc.Login(context.Background(), domain.LoginDTO{
		Email:    "bob@example.com",
		Password: "wrongpass",
	})
	if err == nil {
		t.Fatal("Login() expected invalid credentials error")
	}
	if err != domain.ErrInvalidCredentials {
		t.Fatalf("Login() error = %v, want %v", err, domain.ErrInvalidCredentials)
	}
}
