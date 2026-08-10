package main

import (
	"bufio"
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"demoxv/doc-processor/internal/delivery/http"
	"demoxv/doc-processor/internal/infrastructure/extractor"
	"demoxv/doc-processor/internal/infrastructure/postgres"
	"demoxv/doc-processor/internal/infrastructure/storage"
	"demoxv/doc-processor/internal/usecase"
	"demoxv/doc-processor/pkg/token"
	_ "demoxv/doc-processor/docs"
	_ "github.com/lib/pq"
	"github.com/minio/minio-go/v7"
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

	databaseURL := getEnv("DATABASE_URL", "postgres://demoxv_admin:demoxv_secret_pass@localhost:5432/doc_db?sslmode=disable")
	minioEndpoint := getEnv("MINIO_ENDPOINT", "localhost:9000")
	minioAccessKey := getEnv("MINIO_ROOT_USER", "minio_admin")
	minioSecretKey := getEnv("MINIO_ROOT_PASSWORD", "minio_secret_pass")
	minioBucket := getEnv("MINIO_BUCKET", "contracts")
	minioUseSSL := getEnv("MINIO_USE_SSL", "false") == "true"

	jwtService := token.NewJWTService(jwtSecret)
	documentExtractor := extractor.NewGenericExtractor()

	db, err := connectPostgresWithRetry(databaseURL, 10, 2*time.Second)
	if err != nil {
		log.Fatalf("failed to connect to postgres: %v", err)
	}
	defer db.Close()

	if err := postgres.EnsureDocumentsTable(db); err != nil {
		log.Fatalf("failed to initialize documents table: %v", err)
	}

	minioClient, err := connectMinioWithRetry(minioEndpoint, minioAccessKey, minioSecretKey, minioUseSSL, 10, 2*time.Second)
	if err != nil {
		log.Fatalf("failed to initialize MinIO client: %v", err)
	}

	ctx := context.Background()
	if err := storage.EnsureBucket(ctx, minioClient, minioBucket); err != nil {
		log.Fatalf("failed to ensure MinIO bucket: %v", err)
	}

	documentRepo := postgres.NewDocumentRepository(db)
	objectStorage := storage.NewMinioStorage(minioClient)
	documentUsecase := usecase.NewDocumentUsecase(documentExtractor, documentRepo, objectStorage, minioBucket)
	router := http.NewRouter(jwtService, documentUsecase)

	address := fmt.Sprintf(":%s", port)
	log.Printf("doc-processor service is starting on %s", address)
	if err := router.Run(address); err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}

func connectPostgresWithRetry(databaseURL string, attempts int, delay time.Duration) (*sql.DB, error) {
	if databaseURL == "" {
		return nil, fmt.Errorf("database url is required")
	}

	var db *sql.DB
	var err error
	for i := 1; i <= attempts; i++ {
		db, err = postgres.NewConnection(databaseURL)
		if err == nil {
			return db, nil
		}

		log.Printf("postgres connection attempt %d/%d failed: %v", i, attempts, err)
		if db != nil {
			_ = db.Close()
		}
		if i < attempts {
			time.Sleep(delay)
		}
	}

	return nil, fmt.Errorf("postgres connection failed after %d attempts: %w", attempts, err)
}

func connectMinioWithRetry(endpoint, accessKey, secretKey string, useSSL bool, attempts int, delay time.Duration) (*minio.Client, error) {
	var client *minio.Client
	var err error
	for i := 1; i <= attempts; i++ {
		client, err = storage.NewMinioClient(endpoint, accessKey, secretKey, useSSL)
		if err == nil {
			return client, nil
		}

		log.Printf("minio connection attempt %d/%d failed: %v", i, attempts, err)
		if i < attempts {
			time.Sleep(delay)
		}
	}

	return nil, fmt.Errorf("minio connection failed after %d attempts: %w", attempts, err)
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
