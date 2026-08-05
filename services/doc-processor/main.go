package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"

	"demoxv/doc-processor/internal/delivery/http"
	"demoxv/doc-processor/internal/infrastructure/extractor"
	"demoxv/doc-processor/internal/usecase"
	"demoxv/doc-processor/pkg/token"
	_ "demoxv/doc-processor/docs"
)

// @title Doc Processor API
// @version 1.0
// @host localhost:8081
// @BasePath /
func main() {
	loadEnvFile(".env")

	port := getEnv("PORT", "8081")
	jwtSecret := token.GetJWTSecret()
	if jwtSecret == "" {
		jwtSecret = "demoxv-sso-secret-key-change-me"
	}

	jwtService := token.NewJWTService(jwtSecret)
	documentExtractor := extractor.NewGenericExtractor()
	documentUsecase := usecase.NewDocumentUsecase(documentExtractor)
	router := http.NewRouter(jwtService, documentUsecase)

	address := fmt.Sprintf(":%s", port)
	log.Printf("doc-processor service is starting on %s", address)
	if err := router.Run(address); err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}

func getEnv(key string, fallback string) string {
	if value, exists := os.LookupEnv(key); exists && value != "" {
		return value
	}
	return fallback
}

func loadEnvFile(path string) {
	file, err := os.Open(path)
	if err != nil {
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])
		if _, exists := os.LookupEnv(key); !exists {
			_ = os.Setenv(key, value)
		}
	}
}
