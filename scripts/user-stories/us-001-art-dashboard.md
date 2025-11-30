# US-001: ART Dashboard for Lead/Principal Engineers

**Status:** Proposed
**Priority:** High
**Story Points:** 13
**Epic:** PI Planning Tools
**Related BDD Spec:** `scripts/specs/art-dashboard.feature`

## User Story

As a **Lead/Principal Engineer on an ART**
I want to **see a dashboard of all my releases, teams, and objectives at a glance**
So that **I can understand the overall state of my program and make strategic decisions**

## Description

When managing an ART through a Program Increment planning cycle, the Lead/Principal Engineer needs to quickly understand:

1. **Release Timeline** - What PIs are coming, when do they start/end
2. **Team Participation** - Which teams are participating and how many objectives they've committed to
3. **Program Objectives** - What are the ART-level strategic goals
4. **Health Metrics** - How many objectives are pending, accepted, completed, at-risk
5. **Quick Assessment** - Can I identify obvious gaps or overcommitment at a glance

## Acceptance Criteria

### AC1: Display Release Information
```gherkin
Given I'm an ART lead for "Data, Analytics and Digital"
When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital"
Then I see:
  - Current PI (PI-3/25 with [CURRENT] badge)
  - Next PI (PI-4/25)
  - Upcoming PIs with dates
```

### AC2: Show Team Participation
```gherkin
Given the dashboard is displayed
Then I see a "Teams" section showing:
  - All teams in the ART (27 teams for DAD)
  - Number of objectives per team
  - Status breakdown (Pending, Accepted, etc.)
```

### AC3: Display Program Objectives
```gherkin
Given the dashboard is displayed
Then I see "Program PI Objectives" section showing:
  - One objective per PI
  - Status of each (Draft, Accepted, etc.)
  - Grouped by release
```

### AC4: Show Health Metrics
```gherkin
Given the dashboard is displayed
Then I see metrics including:
  - Total teams: 27
  - Total objectives: 47
  - By status: Pending (45), Accepted (2)
  - At-risk count
```

### AC5: Support Filtering
```gherkin
When I run: ./scripts/art-dashboard.sh --art "DAD" --pi current
Then I only see information about the current PI

When I run: ./scripts/art-dashboard.sh --art "DAD" --pi upcoming
Then I only see information about the next PI
```

### AC6: Multiple Output Formats
```gherkin
When I run with --format json
Then I get valid JSON suitable for piping to jq

When I run with --format csv
Then I get CSV output suitable for Excel
```

## Definition of Done

- [x] User can invoke script with `--art <name>`
- [x] Script correctly identifies ART by name
- [x] All sections display (Releases, Teams, Program Objectives)
- [x] Filtering works (--pi current, --pi upcoming)
- [x] Output formats work (json, csv, markdown)
- [x] Error handling for ART not found
- [x] Help/usage documentation included
- [x] BDD spec fully passes
- [x] Integration test written
- [x] Documentation in docs/how-to/

## Technical Approach

**Script:** `scripts/art-dashboard.sh`

**Dependencies:**
- `./tpcli` CLI tool (for querying TP API)
- `jq` (for JSON processing)
- Bash (color output, formatting)

**Query Plan:**
1. Find ART ID by name: `tpcli list AgileReleaseTrains`
2. Get releases for ART: `tpcli list Releases --where "AgileReleaseTrain.Id eq X"`
3. Get program objectives: `tpcli list ProgramPIObjectives --where "AgileReleaseTrain.Id eq X"`
4. Get team objectives: `tpcli list TeamPIObjectives --where "AgileReleaseTrain.Id eq X"`
5. Count and group by status

**Architecture:**
```
Helper functions:
  - find_art_by_name()
  - fetch_releases()
  - fetch_objectives()
  - format_output()

Main flow:
  1. Validate/find ART
  2. Query releases
  3. Query objectives (program & team)
  4. Count metrics
  5. Format output based on --format flag
```

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║              ART DASHBOARD: Data, Analytics & Digital      ║
╚════════════════════════════════════════════════════════════╝

📋 RELEASES
  Current:  PI-3/25 (Oct 28 - Nov 12) [CURRENT]
  Next:     PI-4/25 (Jan 2 - Jan 13)
  Upcoming: PI-5/25 (TBD)

📊 PARTICIPATION
  Teams:       27
  Objectives:  47 total
    - Pending:   45
    - Accepted:  2
    - Done:      0

👥 PROGRAM OBJECTIVES
  PI-3/25: (in progress)
    - Objective 1 [Draft]
  PI-4/25: (upcoming)
    - Objective 1 [Draft]

⚠️  HEALTH CHECK
  At-risk:     3 objectives
  Blockers:    2 cross-team dependencies
  Overcommit:  4 teams exceed capacity

Recommendation: Get effort estimates for remaining objectives
```

## Risks

- **Discovery Time:** If there are many objectives, API queries might take time
- **Stale Data:** Dashboard shows point-in-time snapshot; refresh needed for updates
- **Name Conflicts:** If multiple ARTs have similar names, need exact match

## Future Enhancements

- Real-time auto-refresh mode
- Slack/Teams integration for notifications
- Trend tracking (week-over-week burndown)
- Resource utilization visualization
- Risk heat map by team

## Related User Stories

- US-002: Team Deep Dive
- US-003: Objective Deep Dive
- US-004: Release Status Report

## Acceptance Tests

See `scripts/specs/art-dashboard.feature` for full BDD specifications.

## Effort Breakdown

| Activity | Points | Notes |
|----------|--------|-------|
| Script implementation | 5 | Query + formatting |
| Output formatting | 3 | Colors, tables, etc |
| Testing & specs | 3 | BDD + integration |
| Documentation | 2 | How-to guide |
| **Total** | **13** | One sprint |
