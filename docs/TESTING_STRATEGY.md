# Testing Strategy: BDD and TDD Cohesion

## Overview

This project uses a **dual-testing approach** that combines:
- **TDD (Test-Driven Development)**: Unit tests that verify implementation correctness
- **BDD (Behavior-Driven Development)**: Acceptance tests that verify business requirements

Together, they answer two essential questions:
- **TDD**: "Are we building it right?" (implementation is correct)
- **BDD**: "Are we building the right thing?" (requirements are met)

---

## Go Testing Strategy

### TDD: Unit Tests (Low-Level)

**Goal**: Verify implementation correctness of Go functions and methods

**Tools**:
- `testing` package (standard library)
- Table-Driven Tests (Go idiomatic pattern)
- Mocking (via `httptest`, custom stubs)

**Focus**:
- Individual functions/methods
- Edge cases and error handling
- Data structure logic
- API interactions

**Example Pattern** (from `pkg/tpclient/client_test.go`):
```go
func TestClientCreateSuccess(t *testing.T) {
    // Arrange: Mock API server
    server := httptest.NewServer(...)
    client := NewClient(server.URL, "token", false)

    // Act: Call the method
    result, err := client.Create("TeamPIObjective", data)

    // Assert: Verify behavior
    if err != nil {
        t.Fatalf("expected no error, got %v", err)
    }
    // ... more assertions
}
```

**Run Command**:
```bash
make go-test
go test -v ./...
go test -v ./pkg/tpclient  # Single package
```

**Success Criterion**: All unit tests pass (GREEN)

---

### BDD: Gherkin Scenarios (High-Level)

**Goal**: Verify business requirements and user workflows

**Tools**:
- Gherkin syntax (`.feature` files)
- Step definitions in Python (behave framework)
- Mock TP API responses

**Focus**:
- End-to-end user workflows
- Command-line behavior
- Error messages and feedback
- Integration across components

**Example Pattern** (from `tests/features/go_cli_create_update.feature`):
```gherkin
Feature: Create and Update TargetProcess Entities via CLI

Scenario: Create TeamPIObjective with valid data
  When user runs: tpcli create TeamPIObjective --data '{"name":"API Perf",...}'
  Then command succeeds with exit code 0
  And output contains JSON with "id" field
  And returned entity has all provided fields
```

**Run Command**:
```bash
make bdd
```

**Success Criterion**: All BDD scenarios pass (GREEN)

---

## Python Testing Strategy

### TDD: Unit Tests (Low-Level)

**Goal**: Verify implementation correctness of Python classes and methods

**Tools**:
- `pytest` (recommended over `unittest`)
- Fixtures (pytest fixtures for setup/teardown)
- Parameterized Tests (via `pytest.mark.parametrize`)
- Mocking (`pytest-mock`, `unittest.mock`)

**Focus**:
- Individual methods in classes
- Data structure logic and transformations
- API client interactions
- Cache behavior
- Error handling

**Example Pattern** (future for `tpcli_pi/core/api_client.py`):
```python
@pytest.fixture
def api_client():
    """Fixture providing a mocked API client"""
    return APIClient(base_url="http://localhost", token="test-token")

def test_create_team_objective_success(api_client, mocker):
    # Arrange: Mock subprocess
    mocker.patch.object(
        api_client,
        "_run_tpcli",
        return_value='{"id": 12345, "name": "API Perf", ...}'
    )

    # Act: Call the method
    objective = api_client.create_team_objective(
        name="API Perf",
        team_id=1935991,
        release_id=1942235
    )

    # Assert: Verify result
    assert objective.id == 12345
    assert objective.name == "API Perf"
    assert objective in api_client.objectives_cache.values()

@pytest.mark.parametrize("invalid_json", [
    "not-json",
    "{incomplete",
    '{"no": "close}'
])
def test_create_with_invalid_json_raises_error(api_client, invalid_json):
    """Parameterized test for various JSON errors"""
    with pytest.raises(APIClientError, match="invalid JSON"):
        api_client._parse_json(invalid_json)
```

**Run Command**:
```bash
make py-test
pytest -v tests/unit/
pytest -v tests/unit/test_api_client.py  # Single file
pytest -v --cov=tpcli_pi tests/unit/    # With coverage
```

**Success Criterion**: All unit tests pass (GREEN)

---

### BDD: Gherkin Scenarios (High-Level)

**Goal**: Verify business requirements and user workflows

**Tools**:
- Gherkin syntax (`.feature` files)
- Step definitions in Python (pytest-bdd or behave)
- Mock TP API responses
- Integration with subprocess calls

**Focus**:
- End-to-end API client workflows
- Data transformation and formatting
- Markdown generation and git sync
- Error handling from user perspective

**Example Pattern** (future for `tests/features/python_api_wrapper.feature`):
```gherkin
Feature: Python API Client Wrapper Methods

Scenario: Create team objective via Python client
  When Python code calls: client.create_team_objective("API Perf", team_id=1935991, release_id=1942235)
  Then subprocess "tpcli create TeamPIObjective --data ..." is called
  And JSON response is parsed
  And TeamPIObjective object is returned
  And object is added to cache with ID

Scenario: Update fails gracefully with API error
  Given subprocess returns 404 Not Found
  When Python code calls: client.update_team_objective(99999, name="x")
  Then APIClientError is raised with clear message
  And error message contains "not found"
```

**Run Command**:
```bash
make bdd
```

**Success Criterion**: All BDD scenarios pass (GREEN)

---

## Cohesion: How TDD and BDD Work Together

### The Pyramid Model

```
        ┌─────────────────┐
        │   E2E Tests     │  Few, expensive
        │  (BDD Scenarios)│  High-level requirements
        ├─────────────────┤
        │  Integration    │  Some, moderate cost
        │  Unit Tests     │  Medium-level components
        ├─────────────────┤
        │  Unit Tests     │  Many, fast, cheap
        │  (TDD)          │  Low-level functions
        └─────────────────┘
```

### Test Execution Flow

**For each feature (Section 1.1 - 1.5)**:

```
1. Write BDD scenarios (.feature file)
   └─ Defines WHAT users need (business value)

2. Write unit tests (test_*.py, *_test.go)
   └─ Defines HOW implementation should work

3. Run tests → RED
   make test
   # TDD: Unit tests fail (methods don't exist)
   # BDD: Scenarios fail (workflows incomplete)

4. Implement feature
   └─ Write production code to satisfy tests

5. Run tests → GREEN
   make test
   # TDD: Unit tests pass (all methods work correctly)
   # BDD: Scenarios pass (workflows deliver value)

6. Commit atomically
   git commit -m "feat: implement feature X

   - All unit tests passing
   - All BDD scenarios passing
   - Ref: TODO.md Section Y"
```

### Example: Section 1.1 (Go CLI Create/Update)

**BDD defined the requirement**:
```gherkin
Scenario: Create TeamPIObjective with valid data
  When user runs: tpcli create TeamPIObjective --data '{...}'
  Then command succeeds with exit code 0
```

**TDD verified the implementation**:
```go
func TestClientCreateSuccess(t *testing.T) {
    // Ensures client.Create() method works correctly
    result, err := client.Create("TeamPIObjective", data)
    // ... assertions on the result
}
```

**Result**: Both BDD scenario and unit test pass → Feature complete ✓

---

## Go-Specific Patterns

### Table-Driven Tests

Go idiom for parameterized tests:

```go
func TestClientCreateErrors(t *testing.T) {
    tests := []struct {
        name       string
        data       []byte
        wantErr    string
    }{
        {"invalid JSON", []byte("invalid"), "invalid JSON in data parameter"},
        {"not found", []byte("{}"), "API error 404"},
        {"empty ID", []byte("{}"), "ID cannot be empty"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            _, err := client.Update("Entity", "", tt.data)
            if !strings.Contains(err.Error(), tt.wantErr) {
                t.Errorf("got %v, want %v", err, tt.wantErr)
            }
        })
    }
}
```

### Run Specific Tests

```bash
# Single test
go test -run TestClientCreateSuccess ./pkg/tpclient

# All tests matching pattern
go test -run TestClient ./pkg/tpclient

# With verbose output
go test -v ./pkg/tpclient

# Show coverage
go test -cover ./...
```

---

## Python-Specific Patterns

### Pytest Fixtures

```python
@pytest.fixture
def mock_api_client(mocker):
    """Fixture providing a pre-configured mock client"""
    client = APIClient(base_url="http://test", token="test")
    mocker.patch.object(client, "_run_tpcli")
    return client

def test_create_objective(mock_api_client):
    # Fixture is auto-injected
    objective = mock_api_client.create_team_objective(...)
    assert objective.id > 0
```

### Parameterized Tests

```python
@pytest.mark.parametrize("entity_type,entity_id", [
    ("TeamPIObjective", 12345),
    ("Feature", 5678),
    ("Epic", 999),
])
def test_update_different_entity_types(api_client, entity_type, entity_id):
    """Test update works with various entity types"""
    result = api_client.update(entity_type, entity_id, {"name": "updated"})
    assert result.id == entity_id
```

### Run Specific Tests

```bash
# Single test
pytest tests/unit/test_api_client.py::test_create_objective

# All tests in file
pytest tests/unit/test_api_client.py -v

# Tests matching pattern
pytest -k "test_create" -v

# With coverage
pytest --cov=tpcli_pi tests/unit/

# Stop on first failure
pytest -x tests/
```

---

## Makefile Targets

| Target | Purpose | Tools |
|--------|---------|-------|
| `make go-test` | Run Go unit tests | `go test -v ./...` |
| `make py-test` | Run Python unit tests | `pytest -v tests/` |
| `make bdd` | Run BDD scenarios | `behave` |
| `make test` | Run all tests | Calls all three above |
| `make test-cov` | Coverage report | `pytest --cov` |
| `make check` | Lint + type-check | `ruff`, `mypy` |

---

## When to Use TDD vs BDD

### Use TDD (Unit Tests) When:
- Testing a single method or function
- Verifying error handling logic
- Testing data transformations
- Checking edge cases and boundaries
- Validating cache behavior

**Examples**:
- "Does `Create()` reject invalid JSON?"
- "Does `Update()` validate numeric IDs?"
- "Does the parser handle empty lists?"

### Use BDD (Gherkin Scenarios) When:
- Testing complete workflows
- Describing user interactions
- Validating end-to-end behavior
- Documenting business requirements
- Testing command-line usage

**Examples**:
- "When user runs `tpcli plan create`, does it succeed and return valid JSON?"
- "When user edits markdown and runs `tpcli plan push`, are changes persisted to TP?"
- "When a merge conflict occurs, are git markers shown correctly?"

---

## Test && Commit Cycle

**The workflow for Sections 1.1 - 1.5**:

```bash
# 1. Write BDD scenarios and unit tests (RED)
# (edit .feature files and test_*.py / *_test.go)

# 2. Run tests
make test

# 3a. If GREEN → commit
git commit -m "feat: implement feature X
Implements Section Y.Z with all tests passing.
- BDD scenarios cover user workflows
- Unit tests verify implementation
- Ref: TODO.md Section Y.Z, PRD Section N"

# 3b. If RED → implement and repeat
# (edit production code)
make test
# (repeat until GREEN)
```

---

## Success Criteria

A feature is **complete** when:

✅ **All TDD tests pass** (unit tests GREEN)
- Implementation is correct
- Edge cases are handled
- Errors are caught

✅ **All BDD scenarios pass** (acceptance tests GREEN)
- Business requirements met
- User workflows validated
- End-to-end behavior verified

✅ **Atomic commit** with clear message
- References which section(s) completed
- Lists what was tested
- Links to PRD/TODO

---

## References

- **Go Testing**: https://golang.org/pkg/testing/
- **Pytest**: https://docs.pytest.org/
- **Behave (BDD)**: https://behave.readthedocs.io/
- **Table-Driven Tests**: https://github.com/golang/go/wiki/TableDrivenTests
- **Gherkin**: https://cucumber.io/docs/gherkin/

---

## Next Steps

As we implement Sections 1.2 - 1.5, follow this strategy:

1. **Section 1.2** (Python API Wrapper)
   - BDD: `tests/features/python_api_wrapper.feature`
   - TDD: `tpcli_pi/core/test_api_client.py`

2. **Section 1.3** (Markdown Generation)
   - BDD: `tests/features/markdown_generation.feature`
   - TDD: `tpcli_pi/core/test_markdown_generator.py`

3. **Section 1.4** (Git Integration)
   - BDD: `tests/features/git_integration.feature`
   - TDD: `tpcli_pi/core/test_git_sync.py`

4. **Section 1.5** (Integration Testing)
   - BDD: `tests/features/core_workflow.feature`
   - Integration of all sections
