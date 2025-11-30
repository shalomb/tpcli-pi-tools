# ADR 002: TPAPIClient Architecture (Subprocess Wrapper with Caching)

**Date:** 2025-11-30
**Status:** Accepted

## Context

The Python tools need to access TargetProcess APIs. Two main approaches exist:

1. **Direct HTTP Client**: Use `requests` library to call API directly
2. **Subprocess Wrapper**: Call existing `tpcli` Go CLI via subprocess

### Why Not Direct HTTP?

The existing `tpcli` Go CLI already:
- Handles authentication (token management, config precedence)
- Parses TargetProcess API responses
- Manages URL construction and query parameters
- Supports both v1 and v2 APIs
- Has been tested against the real API

Reimplementing this in Python would:
- Duplicate code and maintenance burden
- Reinvent authentication wheel
- Add another dependency to manage

## Decision

**Create TPAPIClient as a subprocess wrapper** around the existing `tpcli` CLI.

### Architecture

```python
class TPAPIClient:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._cache = {}  # Simple dict-based cache

    def _run_tpcli(self, entity_type: str, args: List[str]) -> List[Dict]:
        """Execute tpcli and parse JSON response"""
        cmd = ["tpcli", "list", entity_type, "--take", "1000"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # Extract JSON from output (skip request/response metadata)
        # Return parsed JSON array

    def get_teams(self, art_id: Optional[int]) -> List[Team]:
        """Query teams with caching"""
        cache_hit = self._get_cached("Teams", args)
        if cache_hit:
            return [self._parse_team(t) for t in cache_hit]
        # Fetch, parse, cache, return
```

### Parser Methods

Each entity type has a dedicated parser:
- `_parse_user()` → `User` dataclass
- `_parse_team()` → `Team` dataclass
- `_parse_release()` → `Release` dataclass
- etc.

Parsers handle:
- Nested object extraction (e.g., `Team.Owner` → `User`)
- Date parsing (ISO 8601 with timezone)
- Type conversion (string IDs to integers)
- Missing fields (use defaults)

### Caching Strategy

**Cache Key**: `"EntityType:--where clause"`

Example:
```python
cache_key("Teams", ["--where", "AgileReleaseTrain.Id eq 123"])
# → "Teams:--where AgileReleaseTrain.Id eq 123"
```

**When to Cache**:
- ✓ Large entity lists (Teams, Releases)
- ✓ Repeated queries within same analysis
- ✓ Static entity relationships

**When NOT to Cache**:
- ✗ User-triggered reports (always fresh)
- ✗ Real-time status dashboards
- ✗ Between different commands (clear cache)

## Consequences

### Positive

✓ **Reuse Existing Code**: Leverage battle-tested `tpcli` implementation
✓ **Simplified Auth**: No need to manage tokens in Python
✓ **Type Safety**: Subprocess handling is isolated in one class
✓ **Testability**: Easy to mock subprocess calls in unit tests
✓ **Flexibility**: Can upgrade `tpcli` without changing Python code
✓ **Separation of Concerns**: CLI is separate from API client

### Negative

✗ **Subprocess Overhead**: ~100ms per call (mitigated by caching)
✗ **JSON Parsing Twice**: First by `tpcli`, then by Python
✗ **String-based Commands**: No type-safe CLI argument building
✗ **Error Messages**: Must parse `tpcli` error output
✗ **Dependency**: Requires `tpcli` binary in PATH

## Trade-offs Made

### Synchronous vs Async

**Decision**: Synchronous (blocking calls)

The subprocess overhead is acceptable because:
- Most queries are cached
- API is fast (~100ms)
- Users tolerate CLI latency
- Async adds complexity

**Future**: Can add async via `asyncio.run_in_executor()` if needed

### Entity Parsing vs Raw JSON

**Decision**: Parse to typed dataclasses

Alternatives:
1. Return raw `Dict[str, Any]` (untyped, error-prone)
2. Use `pydantic` models (strict, slower parsing)
3. Use `dataclasses` with custom parsing (chosen)

Dataclasses are ideal because:
- Python standard library (no extra dependency)
- Type hints for all fields
- Easy `__post_init__` for computed properties
- Good balance of safety vs. simplicity

## Implementation Notes

### Error Handling

```python
class TPAPIError(Exception):
    """Raised when tpcli subprocess fails"""
    pass
```

Subprocess failures should:
1. Capture stderr
2. Include command in error message
3. Suggest remediation (e.g., "Run `tpcli discover`")

### Timeout Protection

All subprocess calls have `timeout=30` to prevent hanging.

### JSON Extraction

`tpcli` outputs request/response metadata before JSON. Parser must:
1. Find first `{` or `[` in output
2. Extract from that point to end
3. Parse as JSON

## Related Decisions

- **ADR 001**: Why Python over Bash/Go
- **ADR 005**: CLI command architecture and integration

## References

- [Python subprocess module](https://docs.python.org/3/library/subprocess.html)
- [dataclasses module](https://docs.python.org/3/library/dataclasses.html)
- [Type hints](https://peps.python.org/pep-0484/)
