# Test Fixtures: Builders, Golden Files, and API Cassettes

This directory contains:
1. **Fixture Builders** - Reusable builders to generate test data (no company data exposure)
2. **Golden Files** - Pre-recorded API responses for deterministic testing
3. **API Cassettes** - VCR cassettes for offline testing without hitting real APIs

All fixture data is anonymized with generic names and sequential IDs.

## Directory Structure

```
fixtures/
├── builders.py                      # Fixture builders (TPFeatureBuilder, etc.)
├── mock_data.py                     # Pytest fixtures for common scenarios
├── go/                              # Go unit test fixtures (JSON)
│   ├── create_objective_success.json
│   ├── create_objective_invalid_json.json
│   └── ...
└── python/                          # Python test cassettes (YAML - vcrpy format)
    ├── test_create_objective.yaml
    ├── test_update_objective.yaml
    └── ...
```

## Usage

### Fixture Builders (Recommended for Unit Tests)

The fixture builders enable creating realistic test data with zero risk of exposing company information. Use them when:
- Testing API clients with mock data
- Creating parameterized tests with multiple scenarios
- Building composite scenarios with related entities

#### Quick Example

```python
from tests.fixtures.builders import TPFeatureBuilder, JiraStoryBuilder

# Create a single feature
feature = (TPFeatureBuilder()
    .with_id(1234)
    .with_name("My Feature")
    .with_team(999, "Platform Eco")
    .with_jira_mapping("DAD-100", "Data Project")
    .with_effort(21)
    .build())

# Create a Jira story
story = (JiraStoryBuilder()
    .with_key("DAD-100")
    .with_summary("Implement feature")
    .with_status("In Progress")
    .with_story_points(13)
    .with_assignee("Alice Chen")
    .build())
```

#### Available Builders

- **TPTeamBuilder** - TargetProcess teams with ARTs, owners, members
- **TPFeatureBuilder** - TargetProcess features with teams, effort, Jira mapping
- **TPTeamObjectiveBuilder** - TargetProcess PI objectives with releases, status
- **JiraStoryBuilder** - Jira stories with status, points, assignee, epic links

Each builder provides:
- Fluent API (method chaining)
- Sensible defaults matching real TP/Jira structures
- Realistic timestamp generation
- Custom field support

#### Pytest Fixtures

Pre-built fixtures available in `tests.fixtures.mock_data`:

```python
def test_something(tp_tech_debt_feature, tp_platform_team):
    """Fixtures automatically injected."""
    assert tp_tech_debt_feature["Id"] == 1937700
    assert tp_platform_team["Name"] == "Platform Eco"
```

Available fixtures:
- `tp_tech_debt_feature` - Real-world tech debt scenario
- `tp_platform_team` - Platform team with 12 members
- `tp_platform_objective` - Committed PI objective
- `tp_multiple_teams` - Several teams with different ARTs
- `tp_multiple_objectives` - Objectives in different statuses
- `jira_story_basic` - Single Jira story
- `jira_stories_under_epic` - Multiple stories under epic
- Parameterized fixtures for status variations

#### Why Not Real Data?

✅ **Builders are better because:**
- No sensitive company information
- Can't accidentally commit credentials
- Tests run instantly (no API calls)
- Deterministic (no timing issues)
- Can customize for any scenario
- Perfect for CI/CD pipelines
- Can be version controlled safely

❌ **Real data risks:**
- Accidentally commit customer data
- Tight coupling to specific TP/Jira instances
- Slower tests (real API calls)
- Credential management complexity
- Can't run tests in public CI without secrets

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
