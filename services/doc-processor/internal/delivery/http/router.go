package http

import (
	"demoxv/doc-processor/internal/delivery/http/middleware"
	"demoxv/doc-processor/internal/usecase"
	"demoxv/doc-processor/pkg/token"
	ginSwagger "github.com/swaggo/gin-swagger"
	swaggerFiles "github.com/swaggo/files"
	"github.com/gin-gonic/gin"
	"net/http"
)

func NewRouter(jwtService token.JWTToken, documentUsecase *usecase.DocumentUsecase) *gin.Engine {
	r := gin.Default()
	r.GET("/docs", func(c *gin.Context) {
		c.Redirect(http.StatusMovedPermanently, "/swagger/index.html")
	})
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	api := r.Group("/api")
	{
		handler := NewHandler(documentUsecase)
		v1 := api.Group("/v1")
		{
			docs := v1.Group("/docs")
			docs.Use(middleware.AuthMiddleware(jwtService))
			docs.POST("/extract", handler.Extract)
			docs.GET("/:document_id", handler.GetDocument)
		}
	}

	return r
}
