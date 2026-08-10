package http

import (
	"demoxv/sso-service/internal/delivery/http/middleware"
	"demoxv/sso-service/internal/usecase"
	ginSwagger "github.com/swaggo/gin-swagger"
	swaggerFiles "github.com/swaggo/files"
	"github.com/gin-gonic/gin"
	"net/http"
)

func NewRouter(authUsecase *usecase.AuthUsecase) *gin.Engine {
	r := gin.Default()
	r.GET("/docs", func(c *gin.Context) {
		c.Redirect(http.StatusMovedPermanently, "/swagger/index.html")
	})
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	api := r.Group("/api")
	{
		handler := NewAuthHandler(authUsecase)
		api.POST("/auth/register", handler.Register)
		api.POST("/auth/login", handler.Login)
		api.POST("/auth/verify", handler.Verify)
	}

	v1 := r.Group("/api/v1")
	{
		authGroup := v1.Group("/auth")
		authGroup.Use(middleware.AuthMiddleware(authUsecase.TokenHelper()))
		authGroup.GET("/me", func(c *gin.Context) {
			payload := gin.H{
				"user_id": c.MustGet(middleware.ContextUserID),
				"email":   c.MustGet(middleware.ContextUserEmail),
				"role":    c.MustGet(middleware.ContextUserRole),
			}
			c.JSON(200, gin.H{"success": true, "data": payload})
		})
	}

	return r
}
