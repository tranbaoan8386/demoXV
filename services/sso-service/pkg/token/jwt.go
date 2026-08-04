package token

import (
	"errors"
	"os"
	"time"

	"demoxv/sso-service/internal/domain"
	jwt "github.com/golang-jwt/jwt/v5"
)

type JWTToken interface {
	Generate(user *domain.User) (string, error)
	Verify(tokenString string) (*JWTClaims, error)
}

type JWTClaims struct {
	UserID   string `json:"user_id"`
	Email    string `json:"email"`
	FullName string `json:"full_name"`
	Role     string `json:"role"`
	jwt.RegisteredClaims
}

type JWTService struct {
	secretKey []byte
}

func NewJWTService(secretKey string) *JWTService {
	if secretKey == "" {
		secretKey = "demoxv-sso-secret-key-change-me"
	}

	return &JWTService{secretKey: []byte(secretKey)}
}

func (s *JWTService) Generate(user *domain.User) (string, error) {
	if user == nil {
		return "", errors.New("user is required")
	}

	claims := JWTClaims{
		UserID:   user.ID,
		Email:    user.Email,
		FullName: user.FullName,
		Role:     user.Role,
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   user.ID,
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(s.secretKey)
}

func (s *JWTService) Verify(tokenString string) (*JWTClaims, error) {
	if tokenString == "" {
		return nil, errors.New("token is required")
	}

	claims := &JWTClaims{}
	parsedToken, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		return s.secretKey, nil
	})
	if err != nil {
		return nil, err
	}
	if !parsedToken.Valid {
		return nil, errors.New("invalid token")
	}
	if claims.UserID == "" {
		return nil, errors.New("token missing user id")
	}

	return claims, nil
}

func GetJWTSecret() string {
	return os.Getenv("JWT_SECRET")
}
