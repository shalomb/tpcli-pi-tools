# US-004: Release Status Report - PI Progress Tracking

**Status:** Proposed
**Priority:** High
**Story Points:** 13
**Epic:** PI Planning Tools
**Related BDD Spec:** `scripts/specs/release-status.feature`

## User Story

As a **Lead/Principal Engineer**
I want to **track the status and progress of a program increment**
So that **I can identify blockers early and manage the PI to completion**

## Description

During a PI execution, leadership needs to monitor progress across all teams:

1. **Release Info** - What PI, when does it run, status
2. **Team Participation** - Which teams involved, how many objectives each
3. **Progress Tracking** - How many objectives completed vs. pending
4. **Risk Dashboard** - What's at risk, what's blocked
5. **Cross-Team Issues** - Who's blocking whom
6. **Trending** - Is velocity up or down
7. **Reporting** - Summary for executives and stakeholders

## Acceptance Criteria

### AC1: Display Release Information
```gherkin
Given I run: ./scripts/release-status.sh --release "PI-4/25"
Then I see:
  - Release name, ID, dates
  - ART assignment
  - Status (Current, Upcoming, Past)
  - Days remaining (if in progress)
```

### AC2: Show Team Summary
```gherkin
When the report displays
Then I see all teams:
  - Team name
  - Number of objectives
  - Status breakdown (Pending, Accepted, Done)
  - Total effort committed
```

### AC3: Display Progress Metrics
```gherkin
When I view progress section
Then I see for current/past PI:
  - Total objectives
  - Objectives completed (%)
  - Objectives in progress (%)
  - Objectives pending (%)
  - At-risk count
```

### AC4: Show Blockers & Risks
```gherkin
When I run with --show risks
Then I see:
  - At-risk objectives (and why)
  - Cross-team blockers ("Team A waiting on Team B")
  - Dependency risks
  - Resource constraints
  - Schedule risks (holidays, etc)
```

### AC5: Display Dependencies
```gherkin
When I run with --show dependencies
Then I see dependency matrix:
  - From team → To team
  - Type (Blocks, Depends on)
  - Objective affected
```

### AC6: Comparison with Previous PI
```gherkin
When I run: --compare-with "PI-3/25"
Then I see comparison:
  - Number of teams (PI-3 vs PI-4)
  - Number of objectives
  - Effort estimates
  - Average effort per objective
  - Completion % (at midpoint)
```

## Definition of Done

- [x] Release information displayed
- [x] Team summary with objectives
- [x] Progress metrics (for in-progress PI)
- [x] Risk identification and assessment
- [x] Cross-team dependency tracking
- [x] Comparison with previous PI
- [x] Multiple output formats (summary, json, html)
- [x] Executive summary generation
- [x] BDD spec fully passes
- [x] Integration tests

## Technical Approach

**Script:** `scripts/release-status.sh`

**Query Plan:**
1. Get release by name: `tpcli get Releases <id>`
2. Get team objectives: `tpcli list TeamPIObjectives --where "Release.Id eq X"`
3. Get program objectives: `tpcli list ProgramPIObjectives --where "Release.Id eq X"`
4. Get linked features (for progress): `tpcli list Features --where "Release.Id eq X"`
5. Analyze and calculate metrics

**Risk Detection:**
```
At-Risk Indicators:
  - Effort unknown (not estimated)
  - Multiple blockers identified
  - Key person unavailable
  - External approvals pending
  - Overcommitted team

Blocker Detection:
  - Feature status = "Blocked"
  - Comment contains "blocked", "waiting", "blocker"
  - Dependency to other team's feature
```

## Example Output (Current PI)

```
╔════════════════════════════════════════════════════════════╗
║          RELEASE STATUS: PI-3/25 (Data, Analytics & Digital)║
║                     Week 2 of 2 - 50% Complete              ║
╚════════════════════════════════════════════════════════════╝

📋 RELEASE INFORMATION
  Name:          PI-3/25
  ART:           Data, Analytics and Digital
  Timeline:      Oct 28 - Nov 12, 2025
  Duration:      2 weeks (14 days)
  Status:        IN PROGRESS [CURRENT]
  Days elapsed:  7 days
  Days remaining: 7 days

👥 TEAM PARTICIPATION (27 teams)
  Total teams:   27
  With objectives: 27
  Total objectives: 48

  Teams summary:
  ├─ Example Team: 1 objective
  ├─ Team Superman (DQH): 4 objectives
  ├─ PIC - Thanos: 4 objectives
  ├─ DG & MDM POD: 5 objectives
  └─ ... 23 more teams

📊 PI PROGRESS
  Total objectives:        48
    Completed:             8 (17%)
    In Progress:          15 (31%)
    Pending/Not Started:  24 (50%)
    At-Risk:               3 (6%)

  Effort status:
    Estimated:           426 points
    Completed:            89 points (21%)
    Remaining:           337 points (79%)

  Velocity trend: 🔄 Stable (on pace)

🚨 BLOCKERS & AT-RISK ITEMS (3 issues)
  1. EX-2527: Iron Mountain S3 Transfer
     Risk: GxP compliance decision pending
     Impact: Example Team team
     Mitigation: AWS will decide by end of week

  2. PIC-Stan-Lee-001: Master Data Discovery
     Risk: Waiting on Team X infrastructure
     Impact: 2 features blocked
     Mitigation: Team X completing setup Nov 8

  3. DQH-003: Smart Search Refactoring
     Risk: Estimated 40 points, team at capacity (45 pts)
     Impact: Quality risk if not deferred
     Mitigation: Consider deferring to PI-4/25

🔗 CROSS-TEAM DEPENDENCIES (2 blockers)
  Team A → Team B: "Infrastructure setup" (blocks 3 objectives)
  Team C → External AWS: "Service quota increase" (blocks 1 objective)

  Recommendation: Escalate Team C's blocker to AWS account team

📈 COMPARISON WITH PI-2/25
  Metric                 | PI-2/25 | PI-3/25 | Change
  Teams                  | 28      | 27      | -1
  Total objectives       | 48      | 48      | Same
  Completion % (at day 7)| 19%     | 17%     | -2% (slightly slower)
  At-risk items          | 1       | 3       | +2
  Average effort/obj     | 8.9     | 8.9     | Same

  Analysis: Slightly slower velocity, 2 more at-risk items
  Recommendation: Identify new blockers, consider scope adjustment

⚠️  HEALTH CHECK
  On Track: YES (slight slowdown, but recoverable)
  Risks: MEDIUM (3 blockers, manageable with attention)
  Escalation needed: 2 items need decision/escalation

📋 EXECUTIVE SUMMARY
  PI-3/25 is on track with 17% completion at the 50% point.

  Status:
    ✓ 48 objectives in flight
    ✓ 8 completed, 15 in progress
    ⚠️ 3 at-risk items with mitigations in progress

  Key Actions:
    1. AWS to decide on GxP compliance for S3 transfer by Friday
    2. Escalate Team C's service quota request
    3. Evaluate deferring DQH-003 to next PI

  Forecast: 90% complete by end of PI (8 days remaining)
            4 objectives may slip to next PI

UPCOMING EVENTS (next 7 days):
  Nov 8:  Team X completes infrastructure setup
  Nov 9:  PI-3/25 Mid-Point Check-In (recommend escalation)
  Nov 10: AWS GxP compliance decision expected
  Nov 12: PI-3/25 Closes / PI-4/25 Planning begins
```

## Related User Stories

- US-001: ART Dashboard
- US-002: Team Deep Dive
- US-003: Objective Deep Dive

## Effort Breakdown

| Activity | Points |
|----------|--------|
| Core status report | 4 |
| Progress tracking | 3 |
| Risk/blocker identification | 3 |
| Comparison logic | 2 |
| Formatting & export | 1 |
| **Total** | **13** |

## Acceptance Tests

See `scripts/specs/release-status.feature` for full BDD specifications.
