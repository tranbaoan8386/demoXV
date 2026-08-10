FROM golang:1.26-alpine AS builder
WORKDIR /src

RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags='-s -w' -o /out/sso-service ./cmd/api

FROM alpine:3.20
WORKDIR /app

RUN apk add --no-cache ca-certificates
COPY --from=builder /out/sso-service /app/sso-service

EXPOSE 8080
ENTRYPOINT ["/app/sso-service"]

