# ADR 003: Risk Scoring Methodology

**Date:** 2025-11-30
**Status:** Accepted

## Context

The PI planning tools need to assess risk levels for objectives and teams. Users need:

- Quick visual health status (red/yellow/green)
- Numerical health score (0-100)
- Categorized risks (Technical, Schedule, Resource, etc.)
- Actionable recommendations

The challenge: Create a simple, intuitive scoring system that aligns with user mental models.

## Decision

Implement **penalty-based health scoring** with **category-specific risk detection**.

### Health Score Calculation

**Formula**: `Health = 100 - (sum of risk penalties)`

**Risk Penalties** (deducted from 100):
- **Critical risk**: -25 points each
- **High risk**: -15 points each
- **Medium risk**: -5 points each
- **Low risk**: -2 points each
- **Floor**: Score cannot go below 0

**Color Mapping**:
- 80-100: 🟢 Green (Healthy)
- 60-79: 🟡 Yellow (Caution)
- 40-59: 🟠 Orange (At Risk)
- 0-39: 🔴 Red (Critical)

### Risk Categories

| Category | Detection | Penalty |
|----------|-----------|---------|
| **Estimation** | Missing effort, low estimates | HIGH |
| **Capacity** | Overcommitted team/person | HIGH |
| **Schedule** | Unstarted work late in PI | HIGH |
| **Resource** | Missing owners, skills gaps | MEDIUM |
| **Dependency** | Blocking dependencies | MEDIUM |
| **Compliance** | Unmet requirements | HIGH |
| **Skills** | Team lacks required skills | MEDIUM |
| **Technical** | Technical debt, architecture issues | MEDIUM |

### Risk Detection Rules

#### Estimation Risks

```python
if objective.effort == 0:
    risk("Missing effort estimation", HIGH)
elif objective.effort < 5:
    risk("Unusually low estimate", MEDIUM)
```

**Rationale**: Story points < 5 suggest incomplete breakdown

#### Capacity Risks

```python
utilized = committed_effort / available_effort
if utilized > 1.0:
    risk("Team overcommitted", HIGH)
elif utilized > 0.9:
    risk("High capacity (>90%)", MEDIUM)
```

**Rationale**: >90% utilization leaves no buffer for uncertainty

#### Feature/Work Item Risks

```python
unstarted_pct = unstarted_features / total_features
if unstarted_pct > 0.7:
    risk("High proportion of unstarted work", HIGH)

if missing_owners > 0:
    risk(f"{missing_owners} features without owners", MEDIUM)

if missing_estimates > 0:
    risk(f"{missing_estimates} features without estimates", HIGH)
```

**Rationale**: Late-stage unstarted work signals planning issues

#### Dependency Risks

```python
if blocking_dependencies > 0:
    risk(f"{n} blocking dependencies", HIGH)

if cross_team_deps > expected:
    risk("High cross-team coupling", MEDIUM)
```

**Rationale**: Dependencies are schedule blockers

### Escalation Rules

**Escalation Required** if:
- Any CRITICAL risks exist, OR
- More than 2 HIGH risks, OR
- Health score < 30

When escalated, recommendations include:
- "Escalate immediately" for critical
- "Create mitigation plans" for high risks
- "Consider deferring lower-priority work"

## Example

**Scenario**: Team with 80 story point capacity, 100 committed

```
Risk: Missing effort on 3 objectives     → HIGH
Risk: 2 features without owners          → MEDIUM
Risk: 1 blocking dependency              → MEDIUM

Penalties:
  1 HIGH risk: -15
  2 MEDIUM risks: -10

Health = 100 - 25 = 75 (Yellow/Caution)

Recommendations:
- Estimate missing objectives
- Assign owners to features
- Coordinate with dependent team
```

## Consequences

### Positive

✓ **Intuitive**: Users understand 0-100 scale
✓ **Contextual**: Colors and numbers work together
✓ **Actionable**: Specific risk types → specific mitigations
✓ **Adjustable**: Penalty weights can be tuned based on feedback
✓ **Composite**: Combines multiple risk signals into one metric

### Negative

✗ **Arbitrary Weights**: Penalty values based on experience, not science
✗ **False Negatives**: May miss risks not explicitly checked
✗ **Domain Specific**: Weights may not apply to all organizations
✗ **Static Thresholds**: Doesn't learn from historical data

## Calibration

Penalties were chosen based on:

1. **SAFe PI Planning Guidance**
   - "Planning confidence" concept
   - Risk categories from SAFe PI Risk Board

2. **Agile Estimation Theory**
   - Unestimated work = high uncertainty
   - Late unstarted work = schedule risk

3. **Capacity Planning**
   - 70% utilization = safe
   - 80-90% = caution
   - >100% = critical

## Future Improvements

### Feedback-Based Tuning

Track actual PI outcomes:
- How often did 75-health PIs complete on time?
- Which risk types most affected outcomes?
- Should weights be adjusted?

### Historical Comparison

Compare current objective against similar historical objectives:
- "This is similar risk to PI-4/24 Objective X"
- "That objective had 3 escalations"

### Risk Correlation Analysis

Detect which risk combinations are most dangerous:
- Capacity + Dependency risks together?
- Estimation + Skills risks?

## Related Decisions

- **ADR 004**: Feature scope and MVP (why dependency analysis is deferred)
- **ADR 005**: CLI output format decisions

## References

- [SAFe Program Increment](https://scaledagileframework.com/program-increment/)
- [SAFe PI Risk Board](https://scaledagileframework.com/pi-risk-board/)
- [Story Point Estimation](https://www.mountaingoatsoftware.com/blog/how-to-estimate)
