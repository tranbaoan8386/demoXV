package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

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
	db, err := connectPostgresWithRetry(postgresURL, 10, 2*time.Second)
	if err != nil {
		log.Fatalf("failed to establish postgres connection: %v", err)
	}
	defer db.Close()
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

func connectPostgresWithRetry(dsn string, attempts int, delay time.Duration) (*sql.DB, error) {
	if dsn == "" {
		return nil, fmt.Errorf("database url is required")
	}

	var db *sql.DB
	var err error
	for i := 1; i <= attempts; i++ {
		db, err = sql.Open("postgres", dsn)
		if err != nil {
			log.Printf("postgres open attempt %d/%d failed: %v", i, attempts, err)
		} else if pingErr := db.Ping(); pingErr != nil {
			log.Printf("postgres ping attempt %d/%d failed: %v", i, attempts, pingErr)
			err = pingErr
		}

		if err == nil {
			return db, nil
		}

		if db != nil {
			_ = db.Close()
		}

		if i < attempts {
			time.Sleep(delay)
		}
	}

	return nil, fmt.Errorf("postgres connection failed after %d attempts: %w", attempts, err)
}

func initSchema(db *sql.DB) error {
	query := `
		CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
		CREATE TABLE IF NOT EXISTS users (
		    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
		    email VARCHAR(255) NOT NULL UNIQUE,
		    username VARCHAR(100) NOT NULL,
		    full_name VARCHAR(255) NOT NULL,
		    password_hash VARCHAR(255) NOT NULL,
		    role VARCHAR(50) NOT NULL DEFAULT 'user',
		    status VARCHAR(50) NOT NULL DEFAULT 'active',
		    is_active BOOLEAN NOT NULL DEFAULT TRUE,
		    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		    last_login_at TIMESTAMPTZ NULL
		);
		CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
		CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
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
