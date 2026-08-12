package http

import (
	"errors"
	"log"
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

	createdBy := ""
	if value, exists := c.Get(middleware.ContextUserID); exists {
		if userID, ok := value.(string); ok {
			createdBy = userID
		}
	}

	result, err := h.documentUsecase.ExtractFile(c.Request.Context(), file, createdBy)
	if err != nil {
		status := http.StatusInternalServerError
		code := "extract_failed"
		message := err.Error()

		switch {
		case errors.Is(err, domain.ErrMissingFile):
			status = http.StatusBadRequest
			code = "missing_file"
		case errors.Is(err, domain.ErrInvalidFileType):
			status = http.StatusUnsupportedMediaType
			code = "invalid_file_type"
		case errors.Is(err, domain.ErrStorageFailed), errors.Is(err, domain.ErrDocumentPersistFailed):
			status = http.StatusInternalServerError
			code = "storage_error"
		case errors.Is(err, domain.ErrExtractFailed):
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
			"document_id":  result.DocumentID,
			"filename":     result.Filename,
			"content":      result.Content,
			"storage_path": result.StoragePath,
			"created_by":   result.CreatedBy,
		},
	})
}

// GetDocument godoc
// @Summary Lấy thông tin tài liệu theo ID
// @Tags Documents
// @Accept json
// @Produce json
// @Param Authorization header string true "Bearer <token>"
// @Param document_id path string true "Document ID"
// @Success 200 {object} map[string]interface{}
// @Failure 404 {object} map[string]interface{}
// @Failure 500 {object} map[string]interface{}
// @Router /api/v1/docs/{document_id} [get]
func (h *Handler) GetDocument(c *gin.Context) {
	documentID := c.Param("document_id")
	log.Printf("GetDocument request document_id=%s", documentID)
	if documentID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error": gin.H{
				"code":    "missing_document_id",
				"message": "document_id is required",
			},
		})
		return
	}

	document, err := h.documentUsecase.GetDocument(c.Request.Context(), documentID)
	if err != nil {
		log.Printf("GetDocument error for id=%s: %v", documentID, err)
		if errors.Is(err, domain.ErrDocumentNotFound) {
			log.Printf("document %s not found in DB", documentID)
			c.JSON(http.StatusNotFound, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "document_not_found",
					"message": "document not found",
				},
			})
			return
		}

		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error": gin.H{
				"code":    "internal_error",
				"message": err.Error(),
			},
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"document_id":  document.ID,
			"filename":     document.Filename,
			"content":      document.Content,
			"storage_path": document.StoragePath,
			"created_by":   document.CreatedBy,
			"created_at":   document.CreatedAt,
		},
	})
}

// ListDocuments godoc
// @Summary Lấy danh sách tài liệu của người dùng đang đăng nhập
// @Tags Documents
// @Accept json
// @Produce json
// @Param Authorization header string true "Bearer <token>"
// @Success 200 {object} map[string]interface{}
// @Failure 401 {object} map[string]interface{}
// @Failure 500 {object} map[string]interface{}
// @Router /api/v1/docs [get]
func (h *Handler) ListDocuments(c *gin.Context) {
	userID := ""
	if value, exists := c.Get(middleware.ContextUserID); exists {
		if storedUserID, ok := value.(string); ok {
			userID = storedUserID
		}
	}

	documents, err := h.documentUsecase.ListDocuments(c.Request.Context(), userID)
	if err != nil {
		log.Printf("ListDocuments error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error": gin.H{
				"code":    "internal_error",
				"message": err.Error(),
			},
		})
		return
	}

	items := make([]gin.H, 0, len(documents))
	for _, document := range documents {
		items = append(items, gin.H{
			"document_id":  document.ID,
			"filename":     document.Filename,
			"content":      document.Content,
			"storage_path": document.StoragePath,
			"created_by":   document.CreatedBy,
			"created_at":   document.CreatedAt,
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"documents": items,
		},
	})
}
