package http

import (
	"net/http"

	"demoxv/doc-processor/internal/delivery/http/middleware"
	"demoxv/doc-processor/internal/usecase"
	"demoxv/doc-processor/pkg/token"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
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
			docs.GET("", handler.ListDocuments)
			docs.POST("/extract", handler.Extract)
			docs.GET("/:document_id", handler.GetDocument)
		}
	}

	return r
}
