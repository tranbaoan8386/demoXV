FROM golang:1.26-alpine AS builder
WORKDIR /src

RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags='-s -w' -o /out/doc-processor .

FROM alpine:3.20
WORKDIR /app

RUN apk add --no-cache ca-certificates
COPY --from=builder /out/doc-processor /app/doc-processor

EXPOSE 8081
ENTRYPOINT ["/app/doc-processor"]

