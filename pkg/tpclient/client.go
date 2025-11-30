package tpclient

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// Client represents a TargetProcess API client
type Client struct {
	BaseURL    string
	Token      string
	HTTPClient *http.Client
	Verbose    bool
}

// NewClient creates a new TargetProcess API client
func NewClient(baseURL, token string, verbose bool) *Client {
	return &Client{
		BaseURL: strings.TrimRight(baseURL, "/"),
		Token:   token,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		Verbose: verbose,
	}
}

// doRequest executes an HTTP request with authentication
func (c *Client) doRequest(method, path string, body io.Reader) (*http.Response, error) {
	fullURL := fmt.Sprintf("%s%s", c.BaseURL, path)

	if c.Verbose {
		fmt.Printf("Request: %s %s\n", method, fullURL)
	}

	req, err := http.NewRequest(method, fullURL, body)
	if err != nil {
		return nil, fmt.Errorf("creating request: %w", err)
	}

	// Add authentication token as query parameter
	// This is the recommended method per IBM TargetProcess documentation
	q := req.URL.Query()
	q.Add("access_token", c.Token)
	req.URL.RawQuery = q.Encode()

	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/json")

	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("executing request: %w", err)
	}

	if c.Verbose {
		fmt.Printf("Response: %d %s\n", resp.StatusCode, resp.Status)
	}

	return resp, nil
}

// Get retrieves a single entity by ID
func (c *Client) Get(entityType string, id int, fields []string) (map[string]interface{}, error) {
	path := fmt.Sprintf("/api/v1/%s/%d", entityType, id)

	if len(fields) > 0 {
		params := url.Values{}
		params.Set("include", fmt.Sprintf("[%s]", strings.Join(fields, ",")))
		path = fmt.Sprintf("%s?%s", path, params.Encode())
	}

	resp, err := c.doRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		var apiErr struct {
			Status  string `json:"Status"`
			Message string `json:"Message"`
			Type    string `json:"Type"`
			ErrorId string `json:"ErrorId"`
		}
		msg := string(body)
		if err := json.Unmarshal(body, &apiErr); err == nil && apiErr.Message != "" {
			msg = fmt.Sprintf("%s: %s (%s)", apiErr.Status, apiErr.Message, apiErr.Type)
		}
		if resp.StatusCode == http.StatusNotFound {
			return nil, fmt.Errorf("API error %d: %s; resource '%s' may not exist. Try 'tpcli discover' to find available entity types", resp.StatusCode, msg, entityType)
		}
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, msg)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decoding response: %w", err)
	}

	return result, nil
}

// List retrieves multiple entities with optional filtering
func (c *Client) List(entityType string, where string, fields []string, take, skip int) ([]map[string]interface{}, error) {
	params := url.Values{}

	if where != "" {
		params.Set("where", where)
	}

	if len(fields) > 0 {
		params.Set("include", fmt.Sprintf("[%s]", strings.Join(fields, ",")))
	}

	if take > 0 {
		params.Set("take", fmt.Sprintf("%d", take))
	}

	if skip > 0 {
		params.Set("skip", fmt.Sprintf("%d", skip))
	}

	path := fmt.Sprintf("/api/v1/%s", entityType)
	if len(params) > 0 {
		path = fmt.Sprintf("%s?%s", path, params.Encode())
	}

	resp, err := c.doRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		var apiErr struct {
			Status  string `json:"Status"`
			Message string `json:"Message"`
			Type    string `json:"Type"`
			ErrorId string `json:"ErrorId"`
		}
		msg := string(body)
		if err := json.Unmarshal(body, &apiErr); err == nil && apiErr.Message != "" {
			msg = fmt.Sprintf("%s: %s (%s)", apiErr.Status, apiErr.Message, apiErr.Type)
		}
		if resp.StatusCode == http.StatusNotFound {
			return nil, fmt.Errorf("API error %d: %s; resource '%s' may not exist. Try 'tpcli discover' to find available entity types", resp.StatusCode, msg, entityType)
		}
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, msg)
	}

	var response struct {
		Items []map[string]interface{} `json:"Items"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("decoding response: %w", err)
	}

	return response.Items, nil
}

// Query executes a custom query against the API v2 endpoint
func (c *Client) QueryV2(entityType, query string) ([]map[string]interface{}, error) {
	path := fmt.Sprintf("/api/v2/%s?%s", entityType, query)

	resp, err := c.doRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		var apiErr struct {
			Status  string `json:"Status"`
			Message string `json:"Message"`
			Type    string `json:"Type"`
			ErrorId string `json:"ErrorId"`
		}
		msg := string(body)
		if err := json.Unmarshal(body, &apiErr); err == nil && apiErr.Message != "" {
			msg = fmt.Sprintf("%s: %s (%s)", apiErr.Status, apiErr.Message, apiErr.Type)
		}
		if resp.StatusCode == http.StatusNotFound {
			return nil, fmt.Errorf("API error %d: %s; resource '%s' may not exist. Try 'tpcli discover' to find available entity types", resp.StatusCode, msg, entityType)
		}
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, msg)
	}

	var response struct {
		Items []map[string]interface{} `json:"items"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("decoding response: %w", err)
	}

	return response.Items, nil
}
