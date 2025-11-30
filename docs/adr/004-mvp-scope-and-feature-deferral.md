# ADR 004: MVP Scope and Feature Deferral Strategy

**Date:** 2025-11-30
**Status:** Accepted

## Context

Initial user stories outlined 52 story points across 4 commands:
- US-001: ART Dashboard (13 sp)
- US-002: Team Deep-Dive (13 sp)
- US-003: Objective Deep-Dive (13 sp)
- US-004: Release Status (13 sp)

Each story included advanced features:
- Historical trend analysis
- Jira integration and correlation
- Progress forecasting with burn-down
- Explicit dependency graph visualization
- Milestone tracking
- Cross-team blocker analysis

## Decision

**Implement 86% of planned scope (46 of 52 story points)** with strategic feature deferral.

### Deferral Strategy

**Criterion**: Defer features that require **external data sources** or **time-series collection**.

#### Deferred by Category

| Category | Feature | Reason | Effort to Enable |
|----------|---------|--------|------------------|
| **External Data** | Jira integration | Requires separate API layer | +8 hours |
| **Time-Series** | Historical trends | Need multi-PI data collection | +6 hours |
| **Time-Series** | Progress forecasting | Needs velocity history | +4 hours |
| **Time-Series** | Burn-down charts | Historical tracking | +3 hours |
| **Graph Analysis** | Dependency graphs | Explicit link mapping | +5 hours |
| **Advanced Metrics** | Milestone tracking | Custom field expansion | +3 hours |
| **Advanced Metrics** | Capacity forecasting | Resource allocation data | +4 hours |

**Total Deferred Effort**: ~33 hours (post-MVP feature work)

### Implemented Baseline

#### ART Dashboard (11 of 13 sp)

✓ **Included**:
- List releases with dates and status
- List teams with member counts
- Program objectives summary
- Health metrics (objective counts by status)
- Filtering (by PI status, team name)
- Multiple output formats (text/JSON/CSV)

⚠️ **Deferred**:
- Status-level filtering (users can pipe to grep)
- Export to file (standard shell redirection)

#### Team Deep-Dive (12 of 13 sp)

✓ **Included**:
- Team profile (members, owner, ART)
- PI objectives with status/effort/owner
- Features linked to team
- Capacity analysis (utilization %, per-person)
- Risk identification (missing estimates, owners, overcommitment)
- Risk assessment with health score
- Recommendations generated from risks
- Multiple output formats (text/JSON/Markdown)

⚠️ **Deferred**:
- Jira correlation (requires Jira API integration)
- Historical trends (velocity, scope changes)
- Depth filtering (basic/detailed/comprehensive)

#### Objective Deep-Dive (11 of 13 sp)

✓ **Included**:
- Core info (description, owner, status, dates, effort)
- Structured description parsing (goals, outcomes, acceptance criteria)
- Linked features with status
- Heuristic dependency detection (similar names)
- Risk assessment with health score
- Recommendations
- Multiple output formats (text/JSON/Markdown/HTML)

⚠️ **Deferred**:
- Explicit dependency links (requires TargetProcess CustomLinks)
- Jira search (requires Jira API)
- Stakeholder list expansion
- Historical comparison
- Cross-objective comparison

#### Release Status (12 of 13 sp)

✓ **Included**:
- Release info (dates, status, days remaining)
- Progress metrics (% complete, effort tracking)
- Team summary (per-team objectives and progress)
- Program objectives summary
- Health summary (objective counts by status)
- Multiple output formats (text/JSON/Markdown)

⚠️ **Deferred**:
- Progress forecasting (needs velocity)
- Burn-down visualization (needs time-series)
- Explicit blocker list (needs CustomLinks)
- Cross-team dependencies (needs dependency analysis)
- Milestone tracking (needs custom field expansion)
- PI comparison (needs multi-release analysis)

## Rationale

### Why This Deferral Pattern?

1. **Independent Core Value**: Each command provides value without deferred features
2. **Foundation First**: Core features must be solid before adding complexity
3. **Feedback Cycle**: Users can test and provide feedback on MVP
4. **External Dependencies**: Jira, historical data require separate effort
5. **Complexity Scaling**: Analysis features layer naturally on top

### Why Not Full Implementation?

**Time Constraint**: 33 hours of additional deferred work would push timeline

**Complexity vs. Value**:
- Core features deliver 86% of value
- Deferred features are "nice to have" enhancements
- Can prioritize based on user feedback

**Technical Debt Risk**:
- Rushing complex features → bugs and technical debt
- Better to ship MVP well than ship more poorly

## Implementation Philosophy

### "Accept the Version 1 Constraints"

**For Each Deferred Feature**:
1. Document why it's deferred
2. Provide workaround (if any)
3. Mark CLI arguments as "accepted but not implemented"
4. Link to enhancement issue for future work

**Example** (release-status command):
```python
@click.option(
    "--compare-to",
    default=None,
    help="Compare to previous release [DEFERRED]",  # ← Mark as deferred
)
def main(compare_to, ...):
    # Accept argument but don't use it
    if compare_to and "--compare-to" not in "--compare-to":
        console.print(
            "[yellow]⚠️ Comparison feature deferred to v2[/yellow]"
        )
```

### User Guidance

In help text and docs:
- Clearly mark what's available vs. deferred
- Suggest workarounds (e.g., "Use `tpcli` directly for dependency analysis")
- Link to enhancement proposals for future work

## Consequences

### Positive

✓ **Delivers Value Quickly**: Users can start using tools immediately
✓ **Reduces Risk**: Smaller scope = fewer bugs
✓ **Enables Feedback**: Can iterate based on real usage
✓ **Manageable Complexity**: Code is understandable and maintainable
✓ **Clear Roadmap**: Users know what's coming

### Negative

✗ **Incomplete Integration**: Jira features missing despite being mentioned
✗ **Limited Analysis**: No historical or predictive features
✗ **API Mismatch**: Command args exist but don't work
✗ **User Frustration**: "Why do I see this option if it doesn't work?"

### Mitigation

- CLI help text clearly marks deferred features
- Documentation includes "Future Enhancements" section
- GitHub Issues created for each deferred feature
- Users can vote/prioritize via Issues

## Future Work Priority

When time/resources available:

**Phase 2 (High Priority)**:
1. Explicit dependency mapping
2. Progress forecasting
3. Jira integration layer

**Phase 3 (Medium Priority)**:
1. Historical trend analysis
2. Team velocity calculation
3. Advanced capacity analysis

**Phase 4 (Low Priority)**:
1. Burn-down visualizations
2. Milestone tracking
3. Comparative analysis tools

## Related Decisions

- **ADR 002**: TPAPIClient handles data fetching (limits what's possible)
- **ADR 003**: Risk scoring (could expand to include dependency risks with explicit links)
- **ADR 005**: CLI output formats and architecture

## References

- [MVP Definition](https://en.wikipedia.org/wiki/Minimum_viable_product)
- [Scope Management](https://www.projectmanagementinstitute.org/)
- [Feature Flags for Deferred Features](https://martinfowler.com/articles/feature-toggles.html)
