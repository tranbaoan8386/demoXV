package usecase

import (
	"context"
	"errors"
	"strings"
	"time"

	"demoxv/sso-service/internal/domain"
	"demoxv/sso-service/pkg/hasher"
	"demoxv/sso-service/pkg/token"

	"github.com/google/uuid"
)

type AuthUsecase struct {
	userRepo       domain.UserRepository
	passwordHasher hasher.PasswordHasher
	jwtService     *token.JWTService
}

func NewAuthUsecase(repo domain.UserRepository, passwordHasher hasher.PasswordHasher, jwtService *token.JWTService) *AuthUsecase {
	return &AuthUsecase{
		userRepo:       repo,
		passwordHasher: passwordHasher,
		jwtService:     jwtService,
	}
}

func (u *AuthUsecase) TokenHelper() token.JWTToken {
	return u.jwtService
}

func (u *AuthUsecase) Register(ctx context.Context, dto domain.RegisterDTO) (*domain.User, string, error) {
	if err := dto.Validate(); err != nil {
		return nil, "", err
	}

	email := strings.TrimSpace(dto.Email)
	if _, err := u.userRepo.GetByEmail(ctx, email); err == nil {
		return nil, "", domain.ErrUserAlreadyExists
	} else if !errors.Is(err, domain.ErrUserNotFound) {
		return nil, "", err
	}

	hashedPassword, err := u.passwordHasher.Hash(dto.Password)
	if err != nil {
		return nil, "", err
	}

	now := time.Now()
	user := &domain.User{
		ID:           uuid.NewString(),
		Email:        email,
		Username:     strings.TrimSpace(dto.Username),
		FullName:     strings.TrimSpace(dto.FullName),
		PasswordHash: hashedPassword,
		Role:         "user",
		Status:       "active",
		IsActive:     true,
		CreatedAt:    now,
		UpdatedAt:    now,
	}
	if err := user.Validate(); err != nil {
		return nil, "", err
	}

	if err := u.userRepo.Create(ctx, user); err != nil {
		return nil, "", err
	}

	jwtToken, err := u.jwtService.Generate(user)
	if err != nil {
		return nil, "", err
	}

	return user, jwtToken, nil
}

func (u *AuthUsecase) Login(ctx context.Context, dto domain.LoginDTO) (*domain.User, string, error) {
	if err := dto.Validate(); err != nil {
		return nil, "", err
	}

	user, err := u.userRepo.GetByEmail(ctx, strings.TrimSpace(dto.Email))
	if err != nil {
		if errors.Is(err, domain.ErrUserNotFound) {
			return nil, "", domain.ErrInvalidCredentials
		}
		return nil, "", err
	}

	if err := u.passwordHasher.Compare(user.PasswordHash, dto.Password); err != nil {
		return nil, "", domain.ErrInvalidCredentials
	}

	if !user.IsActive {
		return nil, "", domain.ErrInvalidCredentials
	}

	user.UpdatedAt = time.Now()

	jwtToken, err := u.jwtService.Generate(user)
	if err != nil {
		return nil, "", err
	}

	return user, jwtToken, nil
}

func (u *AuthUsecase) Verify(ctx context.Context, tokenString string) (*domain.User, error) {
	claims, err := u.jwtService.Verify(tokenString)
	if err != nil {
		return nil, err
	}

	user, err := u.userRepo.GetByID(ctx, claims.UserID)
	if err != nil {
		return nil, err
	}

	return user, nil
}
