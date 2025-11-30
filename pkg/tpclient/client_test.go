package tpclient

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

// TestClientCreateSuccess tests successful creation of an entity
func TestClientCreateSuccess(t *testing.T) {
	// Mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Verify request
		if r.Method != "POST" {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if r.URL.Path != "/api/v1/TeamPIObjective" {
			t.Errorf("expected /api/v1/TeamPIObjective, got %s", r.URL.Path)
		}

		// Verify JSON body can be parsed
		var body map[string]interface{}
		err := json.NewDecoder(r.Body).Decode(&body)
		if err != nil {
			t.Fatalf("failed to decode request body: %v", err)
		}

		// Return successful response
		response := map[string]interface{}{
			"id":         12345,
			"name":       "API Perf",
			"team_id":    1935991,
			"release_id": 1942235,
			"effort":     34,
			"create_date": "2025-11-30T10:00:00.000Z",
			"modify_date": "2025-11-30T10:00:00.000Z",
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"name":"API Perf","team_id":1935991,"release_id":1942235,"effort":34}`)
	result, err := client.Create("TeamPIObjective", data)

	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	// Verify result
	var entity map[string]interface{}
	err = json.Unmarshal(result, &entity)
	if err != nil {
		t.Fatalf("failed to unmarshal result: %v", err)
	}

	if entity["id"] != float64(12345) {
		t.Errorf("expected id 12345, got %v", entity["id"])
	}
	if entity["name"] != "API Perf" {
		t.Errorf("expected name 'API Perf', got %v", entity["name"])
	}
}

// TestClientCreateInvalidJSON tests creation with invalid JSON input
func TestClientCreateInvalidJSON(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Fatal("server should not be called with invalid JSON")
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`invalid-json`)
	_, err := client.Create("TeamPIObjective", data)

	if err == nil {
		t.Fatal("expected error for invalid JSON, got none")
	}
	if err.Error() != "invalid JSON in data parameter" {
		t.Errorf("expected 'invalid JSON in data parameter', got %v", err)
	}
}

// TestClientCreateAPIError tests creation when API returns error
func TestClientCreateAPIError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadRequest)
		response := map[string]interface{}{
			"Status":  "BadRequest",
			"Message": "Missing required field: name",
			"Type":    "ValidationException",
			"ErrorId": "123456",
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"team_id":1935991}`)
	_, err := client.Create("TeamPIObjective", data)

	if err == nil {
		t.Fatal("expected error from API, got none")
	}
	if err.Error() != "API error 400: BadRequest: Missing required field: name (ValidationException)" {
		t.Errorf("unexpected error message: %v", err)
	}
}

// TestClientUpdateSuccess tests successful update of an entity
func TestClientUpdateSuccess(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Verify request
		if r.Method != "PUT" {
			t.Errorf("expected PUT, got %s", r.Method)
		}
		if r.URL.Path != "/api/v1/TeamPIObjective/12345" {
			t.Errorf("expected /api/v1/TeamPIObjective/12345, got %s", r.URL.Path)
		}

		// Verify JSON body
		var body map[string]interface{}
		err := json.NewDecoder(r.Body).Decode(&body)
		if err != nil {
			t.Fatalf("failed to decode request body: %v", err)
		}

		// Return successful response
		response := map[string]interface{}{
			"id":         12345,
			"name":       "New Name",
			"team_id":    1935991,
			"release_id": 1942235,
			"effort":     40,
			"create_date": "2025-11-30T09:00:00.000Z",
			"modify_date": "2025-11-30T10:30:00.000Z",
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"name":"New Name","effort":40}`)
	result, err := client.Update("TeamPIObjective", "12345", data)

	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	// Verify result
	var entity map[string]interface{}
	err = json.Unmarshal(result, &entity)
	if err != nil {
		t.Fatalf("failed to unmarshal result: %v", err)
	}

	if entity["id"] != float64(12345) {
		t.Errorf("expected id 12345, got %v", entity["id"])
	}
	if entity["name"] != "New Name" {
		t.Errorf("expected name 'New Name', got %v", entity["name"])
	}
	if entity["effort"] != float64(40) {
		t.Errorf("expected effort 40, got %v", entity["effort"])
	}
}

// TestClientUpdateNotFound tests update when entity doesn't exist
func TestClientUpdateNotFound(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
		response := map[string]interface{}{
			"Status":  "NotFound",
			"Message": "Entity not found",
			"Type":    "EntityNotFoundException",
			"ErrorId": "789",
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"name":"x"}`)
	_, err := client.Update("TeamPIObjective", "99999", data)

	if err == nil {
		t.Fatal("expected error for not found, got none")
	}
}

// TestClientUpdateInvalidJSON tests update with invalid JSON
func TestClientUpdateInvalidJSON(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Fatal("server should not be called with invalid JSON")
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`invalid-json`)
	_, err := client.Update("TeamPIObjective", "12345", data)

	if err == nil {
		t.Fatal("expected error for invalid JSON, got none")
	}
	if err.Error() != "invalid JSON in data parameter" {
		t.Errorf("expected 'invalid JSON in data parameter', got %v", err)
	}
}

// TestClientUpdateInvalidID tests update with non-numeric ID
func TestClientUpdateInvalidID(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Fatal("server should not be called with invalid ID")
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"name":"x"}`)
	_, err := client.Update("TeamPIObjective", "invalid-id", data)

	if err == nil {
		t.Fatal("expected error for invalid ID format, got none")
	}
}

// TestClientCreateFeature tests creating a Feature entity
func TestClientCreateFeature(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/Feature" {
			t.Errorf("expected /api/v1/Feature, got %s", r.URL.Path)
		}

		response := map[string]interface{}{
			"id":        5678,
			"name":      "User Auth",
			"parent_id": 2018883,
			"effort":    21,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"name":"User Auth","parent_id":2018883,"effort":21}`)
	result, err := client.Create("Feature", data)

	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	var entity map[string]interface{}
	json.Unmarshal(result, &entity)
	if entity["id"] != float64(5678) {
		t.Errorf("expected id 5678, got %v", entity["id"])
	}
}

// TestClientCreateReturnsRawJSON tests that Create returns raw JSON bytes
func TestClientCreateReturnsRawJSON(t *testing.T) {
	expectedJSON := []byte(`{"id":999,"name":"test","status":"pending"}`)

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write(expectedJSON)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	data := []byte(`{"name":"test"}`)
	result, err := client.Create("TestEntity", data)

	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	// Verify result is valid JSON
	var parsed map[string]interface{}
	err = json.Unmarshal(result, &parsed)
	if err != nil {
		t.Fatalf("result is not valid JSON: %v", err)
	}

	if parsed["id"] != float64(999) {
		t.Errorf("expected id 999, got %v", parsed["id"])
	}
}

// TestClientDoRequestAddsToken verifies that requests include the token
func TestClientDoRequestAddsToken(t *testing.T) {
	tokenSeen := false
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := r.URL.Query().Get("access_token")
		if token == "test-secret-token" {
			tokenSeen = true
		}
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{}`))
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-secret-token", false)
	client.Create("TestEntity", []byte(`{}`))

	if !tokenSeen {
		t.Error("token was not passed in request")
	}
}

// TestClientCreateWithLargePayload tests handling of large JSON payloads
func TestClientCreateWithLargePayload(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Read and verify we got the payload
		body, err := io.ReadAll(r.Body)
		if err != nil {
			t.Fatalf("failed to read body: %v", err)
		}

		var data map[string]interface{}
		err = json.Unmarshal(body, &data)
		if err != nil {
			t.Fatalf("invalid JSON in request: %v", err)
		}

		response := map[string]interface{}{
			"id":          12345,
			"description": data["description"],
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewClient(server.URL, "test-token", false)

	// Create a payload with a long description
	longDesc := bytes.Repeat([]byte("a"), 5000)
	payload := map[string]interface{}{
		"name":        "Test",
		"description": string(longDesc),
	}
	data, _ := json.Marshal(payload)

	result, err := client.Create("TestEntity", data)

	if err != nil {
		t.Fatalf("expected no error with large payload, got %v", err)
	}

	var entity map[string]interface{}
	json.Unmarshal(result, &entity)
	if entity["id"] != float64(12345) {
		t.Errorf("expected id 12345, got %v", entity["id"])
	}
}
