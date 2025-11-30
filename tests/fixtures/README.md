# Test Fixtures: Golden Files and API Cassettes

This directory contains pre-recorded API responses (golden files) from TargetProcess. They enable fast, deterministic, offline testing without hitting the real API.

## Directory Structure

```
fixtures/
├── go/              # Go unit test fixtures (JSON)
│   ├── create_objective_success.json
│   ├── create_objective_invalid_json.json
│   └── ...
└── python/          # Python test cassettes (YAML - vcrpy format)
    ├── test_create_objective.yaml
    ├── test_update_objective.yaml
    └── ...
```

## Usage

### Go Tests

Load fixture in test:
```go
func TestCreateObjective(t *testing.T) {
    // Load cassette from tests/fixtures/go/create_success.json
    cassette := loadFixture(t, "create_success")

    // Use in test...
}
```

### Python Tests

Mark test with `@pytest.mark.vcr`:
```python
@pytest.mark.vcr("create_objective_success")
def test_create_team_objective():
    # Automatically uses tests/fixtures/python/create_objective_success.yaml
    objective = client.create_team_objective(...)
    assert objective.id == 12345
```

## Recording New Cassettes

Only record cassettes when:
- API contract changes (new fields, endpoints)
- Updating TargetProcess API version
- Adding new entity types

### Python (vcrpy)

```bash
# Set TP_URL and TP_TOKEN environment variables
export TP_URL="https://company.tpondemand.com"
export TP_TOKEN="your-token-here"

# Run test with record mode
pytest -m record tests/unit/test_api_client.py::test_create_team_objective

# Cassette is auto-saved to tests/fixtures/python/test_create_objective.yaml
```

### Go

Manually create fixture JSON file, or use httptest recording library.

## Sensitive Data

Cassettes are **filtered automatically**:

**Python (vcrpy)**:
- Headers: `Authorization`, `access_token` are masked
- Query params: `access_token` is masked
- URI: API domain preserved, but token removed

**Go**:
- Manually mask sensitive fields in JSON fixtures
- Never commit actual tokens

### Example Masked Cassette

```yaml
# Original
uri: https://company.tpondemand.com/api/v1/TeamPIObjective?access_token=abc123xyz

# Masked
uri: https://company.tpondemand.com/api/v1/TeamPIObjective?access_token=***
```

## CI/CD

### Default: Use Pre-Recorded Cassettes

```bash
# Tests run fast, offline, no credentials needed
make test
```

### Optional: Re-Record Cassettes Weekly

```bash
# Only if TP_TOKEN secret is available (e.g., in secure CI environment)
# Validates cassettes against real API, respects TP rate limits
make test-record-cassettes
```

## Guidelines

✅ **DO**:
- Keep fixtures small and focused (one scenario per file)
- Use realistic TP data (real entity structures, reasonable IDs)
- Filter sensitive data before committing
- Update cassettes when API contract changes
- Document cassette purpose in filename

❌ **DON'T**:
- Commit cassettes with real API tokens
- Hit TP API for every test run
- Share cassettes with real user data
- Record cassettes that are flaky (time-sensitive)

## Examples

### Section 1.2: API Wrapper Testing

Fixture: `tests/fixtures/python/test_create_objective.yaml`
```yaml
interactions:
- request:
    body: '{"name":"API Perf","team_id":1935991,"release_id":1942235}'
    method: POST
    uri: https://company.tpondemand.com/api/v1/TeamPIObjective?access_token=***
  response:
    body: '{"id":12345,"name":"API Perf","team_id":1935991,"release_id":1942235,...}'
    status: {code: 200}
```

Test:
```python
@pytest.mark.vcr("create_objective_success")
def test_create_team_objective_returns_typed_object():
    objective = client.create_team_objective(
        name="API Perf",
        team_id=1935991,
        release_id=1942235
    )
    assert isinstance(objective, TeamPIObjective)
    assert objective.id == 12345
```

### Section 1.3: Markdown Generation

Fixture: `tests/fixtures/python/tp_full_plan_response.yaml`
Contains: Complete TP response with 2 objectives, 4 epics, AC fields, etc.

Used by:
- `test_markdown_generator.py` - verifies markdown structure
- `test_git_sync.py` - tests sync workflows
- BDD scenarios - verify end-to-end workflows

---

See `docs/TESTING_STRATEGY.md` for complete testing strategy and design patterns.
