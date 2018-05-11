package main

import (
	"encoding/json"
	"net/http"
	"os"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/rs/zerolog"
)

type UploadResponse struct {
	Location  string
	UploadID  string
	VersionID *string
}

func main() {
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
	logger := zerolog.New(os.Stdout).With().Str("App", "s3proxy").Logger()

	sess := session.Must(session.NewSession(&aws.Config{
		Region:      aws.String("us-east-1"),
		Endpoint:    aws.String("http://localhost:9000"),
		Credentials: credentials.NewStaticCredentials("minio_key", "minio_key", ""),
	}))
	uploader := s3manager.NewUploader(sess)

	handler := func(w http.ResponseWriter, r *http.Request) {
		defer r.Body.Close()

		rlog := logger.
			With().
			Str("TaskID", r.Header.Get("TaskID")).
			Str("URL", r.URL.Path).
			Str("Method", r.Method).
			Logger()
		rlog.Debug().Msg("Handling request")
		result, err := uploader.Upload(&s3manager.UploadInput{
			Bucket: aws.String("bucketname"),
			Key:    aws.String(r.URL.Path[1:]),
			Body:   r.Body,
		})
		if err != nil {
			rlog.Error().Err(err).Msg("")
			err = json.NewEncoder(w).Encode(err)
			if err != nil {
				rlog.Error().Err(err).Msg("")
				json.NewEncoder(w).Encode(err)
			}
			return
		}
		err = json.NewEncoder(w).Encode(&UploadResponse{
			Location:  result.Location,
			UploadID:  result.UploadID,
			VersionID: result.VersionID,
		})
		if err != nil {
			rlog.Error().Err(err).Msg("")
		}
	}
	server := &http.Server{
		Addr:              ":8080",
		Handler:           http.HandlerFunc(handler),
		ReadHeaderTimeout: 10 * time.Second,
	}
	err := server.ListenAndServe()
	if err != nil {
		logger.Fatal().Err(err).Msg("")
	}
}
