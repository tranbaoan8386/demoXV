package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "demoxv/sso-service/docs"
	"demoxv/sso-service/internal/delivery/http"
	"demoxv/sso-service/internal/repository/postgres"
	"demoxv/sso-service/internal/usecase"
	"demoxv/sso-service/pkg/hasher"
	"demoxv/sso-service/pkg/token"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("no .env file found, using environment variables or defaults")
	}

	port := getEnv("PORT", "8080")
	postgresURL := getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/sso_service?sslmode=disable")
	jwtSecret := token.GetJWTSecret()
	if jwtSecret == "" {
		jwtSecret = "demoxv-sso-secret-key-change-me"
	}

	log.Printf("initializing PostgreSQL connection with URL: %s", sanitizeDSN(postgresURL))
	db, err := sql.Open("postgres", postgresURL)
	if err != nil {
		log.Fatalf("failed to open postgres connection: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("failed to ping postgres: %v", err)
	}
	log.Println("PostgreSQL connected successfully")

	if err := initSchema(db); err != nil {
		log.Fatalf("failed to initialize schema: %v", err)
	}
	log.Println("database schema initialized successfully")

	passwordHasher := hasher.NewBcryptHasher()
	jwtService := token.NewJWTService(jwtSecret)
	userRepo := postgres.NewUserRepository(db)
	authUsecase := usecase.NewAuthUsecase(userRepo, passwordHasher, jwtService)
	router := http.NewRouter(authUsecase)

	address := fmt.Sprintf(":%s", port)
	log.Printf("SSO service is starting on %s", address)
	if err := router.Run(address); err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}

func initSchema(db *sql.DB) error {
	query := `
		CREATE TABLE IF NOT EXISTS users (
		    id            TEXT PRIMARY KEY,
		    email         TEXT NOT NULL UNIQUE,
		    username      TEXT NOT NULL,
		    password_hash TEXT NOT NULL,
		    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
		    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		    last_login_at TIMESTAMPTZ NULL
		);
	`

	_, err := db.Exec(query)
	return err
}

func getEnv(key string, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists && value != "" {
		return value
	}
	return defaultValue
}

func sanitizeDSN(dsn string) string {
	if dsn == "" {
		return ""
	}
	if prefix := "postgres://"; len(dsn) > len(prefix) && dsn[:len(prefix)] == prefix {
		return prefix + "***:***@" + dsn[len(prefix):]
	}
	return dsn
}
