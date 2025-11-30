# ADR 001: Python Implementation Language for PI Planning Tools

**Date:** 2025-11-30
**Status:** Accepted

## Context

After initial proof-of-concept with Bash scripts (`map-pi-structure.sh`, etc.), the PI planning tools evolved beyond simple CLI wrappers. The feature set included:

- Type-safe data modeling with multiple entity types
- Complex analysis engines (capacity analysis, risk assessment)
- Multiple output formats (text/JSON/Markdown/HTML)
- Terminal formatting with rich colors and tables
- Caching and performance optimization

Bash became inadequate for:
- Type safety and compile-time validation
- Large codebases (500+ lines per module)
- Dependency management and tool configuration
- Testing frameworks (unit + BDD)

## Decision

Implement the PI planning tools in **Python 3.11+** with modern tooling.

### Tooling Stack

| Tool | Purpose | Rationale |
|------|---------|-----------|
| **uv** | Package management | Fast, reliable Python package management |
| **mypy** | Type checking | `--strict` mode catches errors early |
| **ruff** | Linting & formatting | Single tool for code quality |
| **pytest** | Unit testing | Comprehensive test framework with coverage |
| **behave** | BDD testing | Gherkin specs tied to step implementations |
| **click** | CLI framework | Mature, well-documented CLI library |
| **rich** | Terminal formatting | Beautiful tables, colors, progress bars |

## Consequences

### Positive

✓ **Type Safety**: `mypy --strict` enables compile-time error detection
✓ **Code Quality**: Mature ecosystem with excellent linting tools
✓ **Testing**: Strong frameworks (pytest, behave) for unit and BDD tests
✓ **Readability**: Cleaner, more maintainable code than Bash
✓ **Dependency Management**: `pyproject.toml` handles all tool config
✓ **Performance**: Native Python faster than subprocess-heavy Bash
✓ **Extensibility**: Easy to add new analysis features and integrations

### Negative

✗ **Runtime Dependency**: Requires Python 3.11+ runtime
✗ **Import Performance**: Small startup overhead vs. Bash
✗ **Subprocess Overhead**: Still uses subprocess for `tpcli` calls (mitigation: caching)
✗ **Learning Curve**: Requires Python knowledge to extend

## Implementation Details

### Package Structure

```
tpcli_pi/
├── models/       # Type-safe dataclasses
│   ├── entities.py     # TargetProcess entity models
│   └── analysis.py     # Analysis result models
├── core/         # Business logic
│   ├── api_client.py   # TPAPIClient wrapper
│   └── analysis.py     # Analysis engines
└── cli/          # CLI commands
    ├── art_dashboard.py
    ├── team_deep_dive.py
    ├── objective_deep_dive.py
    └── release_status.py
```

### Type Hints

- All function arguments have type hints
- All return types explicitly declared
- `Optional[T]` used for nullable fields
- Dataclasses use modern type syntax (`field(default_factory=...)`)

### Caching Strategy

Since we wrap subprocess calls to `tpcli`, caching is critical:
- Simple dict-based cache in `TPAPIClient`
- Cache key: `"EntityType:--where condition"`
- Cache cleared between independent analysis runs
- Future: Consider LRU cache with TTL

## Related Decisions

- **ADR 002**: TPAPIClient architecture (subprocess wrapper + caching)
- **ADR 003**: Risk scoring methodology
- **ADR 004**: Feature deferral and MVP scope

## References

- [Python Type Hints](https://peps.python.org/pep-0484/)
- [mypy strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [uv package manager](https://github.com/astral-sh/uv)
- [Ruff linter](https://docs.astral.sh/ruff/)
