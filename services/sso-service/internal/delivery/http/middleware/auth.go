package middleware

import (
	"net/http"
	"strings"

	"demoxv/sso-service/pkg/token"
	"github.com/gin-gonic/gin"
)

const (
	ContextUserID    = "user_id"
	ContextUserEmail = "user_email"
	ContextUserRole  = "user_role"
)

func AuthMiddleware(tokenHelper token.JWTToken) gin.HandlerFunc {
	return func(c *gin.Context) {
		authorizationHeader := c.GetHeader("Authorization")
		if authorizationHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "unauthorized",
					"message": "missing authorization header",
				},
			})
			return
		}

		parts := strings.SplitN(authorizationHeader, " ", 2)
		if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "unauthorized",
					"message": "invalid authorization header",
				},
			})
			return
		}

		claims, err := tokenHelper.Verify(parts[1])
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "unauthorized",
					"message": "invalid or expired token",
				},
			})
			return
		}

		c.Set(ContextUserID, claims.UserID)
		c.Set(ContextUserEmail, claims.Email)
		c.Set(ContextUserRole, claims.Role)
		c.Next()
	}
}
