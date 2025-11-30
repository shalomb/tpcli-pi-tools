# PI Planning Sync Developer Guide

## Overview

This guide covers architecture, development workflows, testing, and deployment for the PI Planning Sync tool.

## Architecture

### Components

```
tpcli (Go CLI)
├── cmd/
│   └── plan.go          # Plan sync commands (init, pull, push)
│
tpcli_pi (Python Core)
├── core/
│   ├── api_client.py    # TargetProcess API wrapper
│   ├── git_integration.py # Git operations
│   ├── markdown_generator.py # Markdown export/import
│   └── config.py        # Configuration management
│
├── models/
│   └── entities.py      # Data models
│
└── cli/
    └── (Future analysis commands)

tests/
├── unit/                # Unit tests (pytest)
├── features/            # BDD scenarios (behave)
└── fixtures/            # Test data and VCR cassettes
```

### Data Flow

1. **Initialize**: Create tracking and feature branches
2. **Export**: Fetch objectives from TP → Generate markdown
3. **Edit**: User edits markdown files locally
4. **Pull**: Fetch latest from TP → Rebase feature branch
5. **Push**: Parse changes → Call API → Update tracking branch

### Key Design Decisions

- **Git-Native**: Use git's built-in 3-way merge for conflict resolution
- **Markdown-Based**: Human-readable editable format
- **YAML Metadata**: Preserves sync state in frontmatter
- **TTL Caching**: Automatic cache expiration to prevent stale data
- **Atomic Operations**: All-or-nothing for data consistency

## Development Setup

### Prerequisites

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Go dependencies
go mod download
```

### Build

```bash
# Build Go CLI
make build

# Run tests
make test

# Run with coverage
make test-cov
```

## Testing Strategy

### BDD Approach

All features follow Behavior-Driven Development:

```gherkin
Feature: Plan Sync
  Scenario: Initialize tracking
    When user initializes plan tracking
    Then tracking branch is created
    And feature branch is created
```

Scenarios → Unit Tests → Implementation

### Test Organization

```
tests/
├── unit/
│   ├── test_api_client.py        # 120+ tests
│   ├── test_git_integration.py   # 110+ tests
│   └── test_markdown_generator.py # 87+ tests
│
└── features/
    ├── go_cli_create_update.feature
    ├── plan_sync_cli.feature
    ├── git_integration.feature
    ├── markdown_generation.feature
    └── performance_optimization.feature
```

### Running Tests

```bash
# All tests
make test

# Only unit tests
make py-test

# Only BDD tests
make bdd

# With coverage
make test-cov
```

### Test Fixtures

VCR cassettes record API responses:

```
tests/fixtures/cassettes/
├── test_create_objective.json
├── test_update_objective.json
└── test_bulk_operations.json
```

This ensures:
- Respectful API usage (no unnecessary calls)
- Fast test execution (no network calls)
- Deterministic results (consistent responses)

## Code Style

### Python

```bash
# Format code
make format

# Check style
make lint

# Type checking
make type-check
```

### Go

```bash
# Format
gofmt -w .

# Lint
golangci-lint run ./...
```

## Adding New Features

### 1. Write BDD Scenario

Create `tests/features/feature_name.feature`:

```gherkin
Feature: New Feature
  Scenario: Do something
    Given initial state
    When user performs action
    Then expected result
```

### 2. Write Step Definitions

Create `tests/features/steps/feature_name_steps.py`:

```python
from behave import given, when, then

@given("initial state")
def step_initial(context):
    context.state = "ready"

@when("user performs action")
def step_action(context):
    context.result = perform_action()

@then("expected result")
def step_verify(context):
    assert context.result == "expected"
```

### 3. Write Unit Tests

Create `tests/unit/test_feature.py`:

```python
def test_feature_works(mocker):
    """Test that feature works correctly."""
    result = perform_action()
    assert result == "expected"
```

### 4. Implement Feature

Modify code in `tpcli_pi/core/` or `cmd/`:

```python
def perform_action():
    """Implementation goes here."""
    return "expected"
```

### 5. Run Tests (TCR)

```bash
make test
# If all pass: commit
# If fail: revert changes
```

## API Client Development

### Adding Query Methods

```python
def get_custom_entities(self, filter_id: int) -> list[CustomEntity]:
    """
    Get custom entities, optionally filtered.

    Uses caching with TTL to minimize API calls.
    """
    args = ["--where", f"Filter.Id eq {filter_id}"]

    cached = self._get_cached("CustomEntities", args)
    if cached is None:
        cached = self._run_tpcli("CustomEntities", args)
        self._set_cached("CustomEntities", cached, args)

    return [self._parse_custom_entity(item) for item in cached]
```

### Bulk Operations

```python
def bulk_create_custom(self, items: list[dict]) -> list[CustomEntity]:
    """Create multiple items atomically."""
    created = []
    for item in items:
        response = self._run_tpcli_create("Custom", item)
        created.append(response[0])

    # Update cache
    cached = self._get_cached("CustomEntities")
    if cached is None:
        cached = []
    cached.extend(created)
    self._set_cached("CustomEntities", cached)

    return [self._parse_custom_entity(item) for item in created]
```

### Performance Optimization

- Use TTL caching for frequently accessed data
- Implement bulk operations for multiple items
- Cache statistics: `get_cache_stats()`

## Git Integration Development

### Adding Sync Operations

```python
def custom_sync(self, params: dict) -> SyncResult:
    """
    Perform custom sync operation.

    Returns:
        SyncResult with success/failure and details
    """
    try:
        # Perform operation
        result = self._perform_operation(params)

        return SyncResult(
            success=True,
            message="Operation successful",
            api_calls=result.api_calls,
        )
    except Exception as e:
        return SyncResult(success=False, message=str(e))
```

### Error Handling

```python
class GitPlanSyncError(Exception):
    """Raised when git sync operation fails."""
    pass

try:
    result = sync_manager.pull(...)
    if not result.success:
        raise GitPlanSyncError(result.message)
except GitPlanSyncError as e:
    print(f"Sync failed: {e}")
```

## Performance Considerations

### Caching Strategy

- **Read-Heavy**: Bulk query results cached for 1 hour
- **Write Operations**: Cache invalidated on mutations
- **Statistics**: Track hits/misses for optimization

### Benchmarking

```bash
# Performance tests
python -m pytest tests/unit/ -k "performance" -v

# Coverage analysis
make test-cov  # Check htmlcov/index.html
```

### Optimization Checklist

- [ ] Queries use caching
- [ ] Bulk operations minimize API calls
- [ ] No N+1 query patterns
- [ ] Performance tests added
- [ ] Metrics tracked

## Debugging

### Enable Verbose Output

```bash
# Python
client = TPAPIClient(verbose=True)

# CLI
tpcli plan init --verbose
```

### Git Debugging

```bash
# See all git operations
GIT_TRACE=1 tpcli plan pull

# Inspect branches
git branch -a
git log --oneline --all

# Check rebase state
git rebase --status
```

### Inspect Cache

```python
client = TPAPIClient()
stats = client.get_cache_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

## Documentation

### Code Comments

```python
def sync_data(self, team_id: int) -> SyncResult:
    """
    Sync planning data for a team.

    This method:
    1. Fetches latest from TargetProcess
    2. Updates tracking branch
    3. Rebases feature branch

    Args:
        team_id: ID of the team to sync

    Returns:
        SyncResult indicating success/failure

    Raises:
        GitPlanSyncError: If git operations fail
    """
```

### README Updates

When adding features, update:
- User Guide: User-facing documentation
- This Developer Guide: Technical documentation
- Code docstrings: Implementation details

## Release Process

### Version Numbering

Semantic versioning: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Release Checklist

- [ ] Update version in code
- [ ] Update CHANGELOG
- [ ] Run full test suite
- [ ] Build binaries
- [ ] Create git tag
- [ ] Deploy to PyPI/npm

## Troubleshooting

### Test Failures

```bash
# Run specific test with verbose output
make py-test -- -xvs tests/unit/test_api_client.py::test_name

# Run with pdb debugger
python -m pytest tests/unit/test_api_client.py -xvs --pdb
```

### Performance Issues

```bash
# Profile code
python -m cProfile -s cumtime script.py

# Memory profiling
pip install memory_profiler
python -m memory_profiler script.py
```

### Cache Issues

```python
# Clear cache if stale
client.clear_cache()

# Check cache status
stats = client.get_cache_stats()
if stats['size'] > 1000:
    print("Cache growing large, consider TTL adjustment")
```

## Contributing

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Write tests and implementation (BDD-first)
4. Run full test suite: `make test`
5. Update documentation
6. Submit PR with description

### Code Review

- All code must have tests
- Tests must pass
- Code style must match project
- Documentation must be updated

## Resources

- [TargetProcess API Docs](https://tp.example.com/api)
- [Behave (BDD Framework)](https://behave.readthedocs.io/)
- [Pytest](https://docs.pytest.org/)
- [Git Documentation](https://git-scm.com/doc)

---

Last Updated: 2025-11-30
