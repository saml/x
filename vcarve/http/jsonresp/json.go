package jsonresp

import (
	"encoding/json"
	"net/http"

	"github.com/rs/zerolog/log"
)

// JSONResponse is http response in JSON format.
type JSONResponse struct {
	StatusCode int
	Payload    map[string]interface{}
}

// New creates new json response.
func New(statusCode int) *JSONResponse {
	return &JSONResponse{
		StatusCode: statusCode,
		Payload: map[string]interface{}{
			"Status": statusCode,
		},
	}
}

// Err adds an error to response.
func (j *JSONResponse) Err(err error) *JSONResponse {
	j.Payload["Error"] = err
	return j
}

// Msg adds a message to response.
func (j *JSONResponse) Msg(msg string) *JSONResponse {
	j.Payload["Message"] = msg
	return j
}

// Set adds arbitrary context to response.
func (j *JSONResponse) Set(key string, val interface{}) *JSONResponse {
	j.Payload[key] = val
	return j
}

// Write sends the response.
func (j *JSONResponse) Write(w http.ResponseWriter) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(j.StatusCode)
	err := json.NewEncoder(w).Encode(j.Payload)
	if err != nil {
		log.Print(err)
	}
	return err
}
