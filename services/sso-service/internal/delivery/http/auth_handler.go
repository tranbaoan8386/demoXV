package http

import (
	"errors"
	"net/http"
	"strings"

	"demoxv/sso-service/internal/domain"
	"demoxv/sso-service/internal/usecase"
	"github.com/gin-gonic/gin"
)

type AuthHandler struct {
	authUsecase *usecase.AuthUsecase
}

func NewAuthHandler(authUsecase *usecase.AuthUsecase) *AuthHandler {
	return &AuthHandler{authUsecase: authUsecase}
}

// Register godoc
// @Summary Register a new user
// @Tags Auth
// @Accept json
// @Produce json
// @Param request body domain.RegisterDTO true "User registration payload"
// @Success 201 {object} map[string]interface{} "User created successfully"
// @Failure 400 {object} map[string]interface{} "Bad request"
// @Failure 409 {object} map[string]interface{} "User already exists"
// @Router /api/auth/register [post]
// Example payload:
// {
//   "email": "alice@example.com",
//   "full_name": "Alice Nguyen",
//   "password": "password123"
// }
func (h *AuthHandler) Register(c *gin.Context) {
	var req domain.RegisterDTO
	if err := c.ShouldBindJSON(&req); err != nil {
		responseError(c, http.StatusBadRequest, "invalid_request", "invalid request body")
		return
	}

	user, token, err := h.authUsecase.Register(c.Request.Context(), req)
	if err != nil {
		mapDomainError(c, err)
		return
	}

	responseSuccess(c, http.StatusCreated, gin.H{
		"user":  user,
		"token": token,
	})
}

// Login godoc
// @Summary Login a user
// @Tags Auth
// @Accept json
// @Produce json
// @Param request body domain.LoginDTO true "User login payload"
// @Success 200 {object} map[string]interface{} "Login successful"
// @Failure 400 {object} map[string]interface{} "Bad request"
// @Failure 401 {object} map[string]interface{} "Unauthorized"
// @Router /api/auth/login [post]
func (h *AuthHandler) Login(c *gin.Context) {
	var req domain.LoginDTO
	if err := c.ShouldBindJSON(&req); err != nil {
		responseError(c, http.StatusBadRequest, "invalid_request", "invalid request body")
		return
	}

	user, token, err := h.authUsecase.Login(c.Request.Context(), req)
	if err != nil {
		mapDomainError(c, err)
		return
	}

	responseSuccess(c, http.StatusOK, gin.H{
		"user":  user,
		"token": token,
	})
}

// Verify godoc
// @Summary Verify a JWT token
// @Tags Auth
// @Accept json
// @Produce json
// @Param Authorization header string true "Bearer token"
// @Success 200 {object} map[string]interface{} "Token is valid"
// @Failure 401 {object} map[string]interface{} "Unauthorized"
// @Router /api/auth/verify [post]
func (h *AuthHandler) Verify(c *gin.Context) {
	authorizationHeader := c.GetHeader("Authorization")
	if authorizationHeader == "" {
		responseError(c, http.StatusUnauthorized, "missing_authorization", "missing authorization header")
		return
	}

	parts := strings.SplitN(authorizationHeader, " ", 2)
	if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
		responseError(c, http.StatusUnauthorized, "invalid_authorization", "invalid authorization header")
		return
	}

	user, err := h.authUsecase.Verify(c.Request.Context(), parts[1])
	if err != nil {
		mapDomainError(c, err)
		return
	}

	responseSuccess(c, http.StatusOK, gin.H{"user": user})
}

func responseSuccess(c *gin.Context, statusCode int, payload interface{}) {
	c.JSON(statusCode, gin.H{
		"success": true,
		"data":    payload,
	})
}

func responseError(c *gin.Context, statusCode int, code string, message string) {
	c.JSON(statusCode, gin.H{
		"success": false,
		"error": gin.H{
			"code":    code,
			"message": message,
		},
	})
}

func mapDomainError(c *gin.Context, err error) {
	switch {
	case errors.Is(err, domain.ErrInvalidEmail):
		responseError(c, http.StatusBadRequest, "invalid_email", domain.ErrInvalidEmail.Error())
	case errors.Is(err, domain.ErrInvalidFullName):
		responseError(c, http.StatusBadRequest, "invalid_full_name", domain.ErrInvalidFullName.Error())
	case errors.Is(err, domain.ErrWeakPassword):
		responseError(c, http.StatusBadRequest, "weak_password", domain.ErrWeakPassword.Error())
	case errors.Is(err, domain.ErrUserAlreadyExists):
		responseError(c, http.StatusConflict, "user_exists", domain.ErrUserAlreadyExists.Error())
	case errors.Is(err, domain.ErrUserNotFound):
		responseError(c, http.StatusUnauthorized, "user_not_found", domain.ErrInvalidCredentials.Error())
	case errors.Is(err, domain.ErrInvalidCredentials):
		responseError(c, http.StatusUnauthorized, "invalid_credentials", domain.ErrInvalidCredentials.Error())
	default:
		responseError(c, http.StatusInternalServerError, "internal_error", "internal server error")
	}
}
