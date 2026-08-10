package storage

import (
	"bytes"
	"context"
	"fmt"
	"io"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

func NewMinioClient(endpoint, accessKey, secretKey string, useSSL bool) (*minio.Client, error) {
	client, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: useSSL,
	})
	if err != nil {
		return nil, fmt.Errorf("create minio client: %w", err)
	}
	return client, nil
}

func EnsureBucket(ctx context.Context, client *minio.Client, bucket string) error {
	exists, err := client.BucketExists(ctx, bucket)
	if err != nil {
		return fmt.Errorf("check bucket existence: %w", err)
	}
	if exists {
		return nil
	}

	if err := client.MakeBucket(ctx, bucket, minio.MakeBucketOptions{}); err != nil {
		return fmt.Errorf("create bucket: %w", err)
	}
	return nil
}

type MinioStorage struct {
	client *minio.Client
}

func NewMinioStorage(client *minio.Client) *MinioStorage {
	return &MinioStorage{client: client}
}

func (s *MinioStorage) Upload(ctx context.Context, bucket, objectName string, data []byte, contentType string) error {
	reader := bytes.NewReader(data)
	_, err := s.client.PutObject(ctx, bucket, objectName, reader, int64(len(data)), minio.PutObjectOptions{ContentType: contentType})
	if err != nil {
		return fmt.Errorf("upload object to minio: %w", err)
	}
	return nil
}

func (s *MinioStorage) Download(ctx context.Context, bucket, objectName string) ([]byte, error) {
	object, err := s.client.GetObject(ctx, bucket, objectName, minio.GetObjectOptions{})
	if err != nil {
		return nil, fmt.Errorf("download object from minio: %w", err)
	}
	defer object.Close()

	data, err := io.ReadAll(object)
	if err != nil {
		return nil, fmt.Errorf("read minio object body: %w", err)
	}
	return data, nil
}
