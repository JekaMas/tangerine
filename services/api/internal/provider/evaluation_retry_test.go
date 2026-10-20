package provider

import (
	"testing"
	"time"
)

func TestEvaluationRetryTransientPositive(t *testing.T) {
	for _, code := range []int{408, 429, 502, 503, 504} {
		if !retryableTransport(Response{HTTPStatus: &code}, true) {
			t.Fatal(code)
		}
	}
	if !retryableTransport(Response{}, true) {
		t.Fatal("connection")
	}
}
func TestEvaluationRetryDelayPositive(t *testing.T) {
	if transportRetryDelay("2", time.Time{}) != 2*time.Second || transportRetryDelay("invalid", time.Time{}) != time.Second {
		t.Fatal("delay policy")
	}
}
func TestEvaluationRetryServerNegative(t *testing.T) {
	for _, code := range []int{400, 401, 403, 500, 501} {
		if retryableTransport(Response{HTTPStatus: &code}, true) {
			t.Fatal(code)
		}
	}
}
func TestEvaluationRetryPartialNegative(t *testing.T) {
	if retryableTransport(Response{Raw: []byte("partial")}, true) {
		t.Fatal("partial connection")
	}
	if transportRetryDelay("-1", time.Time{}) != time.Second {
		t.Fatal("negative delay")
	}
}
