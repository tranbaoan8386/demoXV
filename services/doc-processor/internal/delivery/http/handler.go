package http

import (
	"net/http"

	"demoxv/doc-processor/internal/delivery/http/middleware"
	"demoxv/doc-processor/internal/domain"
	"demoxv/doc-processor/internal/usecase"
	"github.com/gin-gonic/gin"
)

type Handler struct {
	documentUsecase *usecase.DocumentUsecase
}

func NewHandler(documentUsecase *usecase.DocumentUsecase) *Handler {
	return &Handler{documentUsecase: documentUsecase}
}

// Extract godoc
// @Summary Trích xuất văn bản từ tài liệu
// @Tags Documents
// @Accept multipart/form-data
// @Produce json
// @Param Authorization header string true "Bearer <token>"
// @Param file formData file true "File PDF, DOCX hoặc TXT"
// @Success 200 {object} map[string]interface{}
// @Failure 400 {object} map[string]interface{}
// @Failure 401 {object} map[string]interface{}
// @Failure 500 {object} map[string]interface{}
// @Router /api/v1/docs/extract [post]
func (h *Handler) Extract(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error": gin.H{
				"code":    "missing_file",
				"message": "file is required",
			},
		})
		return
	}

	userID, _ := c.Get(middleware.ContextUserID)
	result, err := h.documentUsecase.ExtractFile(file, userID.(string))
	if err != nil {
		status := http.StatusBadRequest
		code := "extract_failed"
		message := err.Error()

		switch err {
		case domain.ErrMissingFile:
			status = http.StatusBadRequest
			code = "missing_file"
		case domain.ErrInvalidFileType:
			status = http.StatusUnsupportedMediaType
			code = "invalid_file_type"
		case domain.ErrExtractFailed:
			status = http.StatusInternalServerError
			code = "extract_failed"
		}

		c.JSON(status, gin.H{
			"success": false,
			"error": gin.H{
				"code":    code,
				"message": message,
			},
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"filename":     result.Filename,
			"content":      result.Content,
			"extracted_by": result.ExtractedBy,
		},
	})
}
