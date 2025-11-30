# Architecture Decision Records

This directory contains ADRs (Architecture Decision Records) documenting major technical decisions and their rationale.

## Active ADRs

| # | Title | Status | Date |
|---|-------|--------|------|
| [001](001-python-implementation-language.md) | Python Implementation Language | ✅ Accepted | 2025-11-30 |
| [002](002-tpapiclient-architecture.md) | TPAPIClient Architecture | ✅ Accepted | 2025-11-30 |
| [003](003-risk-scoring-methodology.md) | Risk Scoring Methodology | ✅ Accepted | 2025-11-30 |
| [004](004-mvp-scope-and-feature-deferral.md) | MVP Scope & Feature Deferral | ✅ Accepted | 2025-11-30 |

## ADR Format

Each ADR follows this structure:

```markdown
# ADR NNN: Title

**Date**: YYYY-MM-DD
**Status**: Accepted | Proposed | Deferred | Superseded

## Context
Background and problem statement

## Decision
What decision was made and why

## Consequences
Positive and negative impacts

## Related Decisions
Links to other ADRs

## References
External sources and documentation
```

## Status Definitions

- **Proposed**: Under discussion, not yet decided
- **Accepted**: Decision made and implemented
- **Deferred**: Decision postponed pending more information
- **Superseded**: Replaced by later ADR

## How to Propose New ADRs

1. Copy template: `cp 0NN-template.md NNN-my-decision.md`
2. Fill out all sections
3. Create pull request with proposal
4. Discuss with team
5. Update status to "Accepted"
6. Commit with GPG signature

## Key Design Principles

From these ADRs:

1. **Pragmatism over Perfection**: MVP scope focuses on immediate value
2. **Reuse Existing Code**: Leverage `tpcli` instead of reimplementing
3. **Type Safety**: Python with `mypy --strict` for early error detection
4. **Simple Analysis**: Heuristics and scoring over complex algorithms
5. **Clear Roadmap**: Document deferred features for future prioritization

## Next Decisions Needed

### For Contributors

- ADR 005: CLI Output Format Architecture
- ADR 006: Test Strategy (Unit vs. BDD coverage)
- ADR 007: Error Handling and User Guidance
- ADR 008: Performance and Caching Strategy

### For Product

- Integration with Jira (requires separate API client)
- Historical data collection and analysis
- Team feedback loop on scoring accuracy

## Quick Links

- [Project README](../README.md)
- [TODO Tracking](../TODO.md)
- [Development Guide](../QUICKSTART.md)
