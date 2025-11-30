# US-002: Team Deep Dive - Capacity & Commitments

**Status:** Proposed
**Priority:** High
**Story Points:** 13
**Epic:** PI Planning Tools
**Related BDD Spec:** `scripts/specs/team-deep-dive.feature`

## User Story

As a **Lead/Principal Engineer**
I want to **drill into a team's PI commitments and capacity**
So that **I can identify overcommitment, risks, and coordination needs**

## Description

When a team is part of your ART, you need to understand:

1. **Team Composition** - Who's on the team, how many people
2. **PI Commitments** - What objectives did they commit to
3. **Capacity** - How many points can they take on
4. **Workload** - Are they overcommitted relative to capacity
5. **Risks** - What could block them (dependencies, skills, resources)
6. **History** - Did they complete their objectives last PI

## Acceptance Criteria

### AC1: Show Team Profile
```gherkin
Given I run: ./scripts/team-deep-dive.sh --team "Example Team"
Then I see:
  - Team name, ID, ART assignment
  - Owner, member count
  - Active status
  - Team capacity info
```

### AC2: Display PI Objectives
```gherkin
Given the team deep dive is displayed
Then I see all PI objectives for this team:
  - Objective name and description
  - Status (Pending, Accepted, In Progress)
  - Committed flag
  - Effort estimate (if provided)
  - Start/end dates
```

### AC3: Show Capacity Analysis
```gherkin
When I run with --show capacity
Then I see:
  - Team size: X people
  - Total committed effort: Y points
  - Effort per person: Y/X
  - ⚠️ Overcommitment warning if Y/X > standard
```

### AC4: Display Risks and Blockers
```gherkin
When I run with --show risks
Then I see identified risks:
  - External dependencies ("Waiting on Team X")
  - Skills gaps ("Need Kubernetes expert")
  - Resource constraints ("Key person on vacation")
  - Overcommitment indicators
```

### AC5: Link to Jira
```gherkin
When I run with --show jira-links
Then I see:
  - Matching Jira epics for each objective
  - External issue IDs
  - Status correlation
```

### AC6: Historical Performance
```gherkin
When I run with --show history
Then I see previous PI performance:
  - Last N PIs
  - Completion rates
  - Velocity trend
```

## Definition of Done

- [x] User can invoke with `--team <name>`
- [x] Script shows team profile
- [x] All PI objectives displayed
- [x] Capacity analysis with warnings
- [x] Risk identification
- [x] Jira correlation
- [x] Historical data
- [x] Multiple output formats (json, markdown, text)
- [x] BDD spec fully passes
- [x] Integration tests

## Technical Approach

**Script:** `scripts/team-deep-dive.sh`

**Query Plan:**
1. Find team by name: `tpcli list Teams`
2. Get team PI objectives: `tpcli list TeamPIObjectives --where "Team.Id eq X"`
3. Get linked features: `tpcli list Features --where "TeamPIObjective.Id eq Y"`
4. Analyze for risks (capacity, dependencies, gaps)

## Key Metrics Calculated

```
Team Capacity Metrics:
  - People count (from custom field)
  - Total effort committed (sum of objective efforts)
  - Average effort per person
  - At-risk flag (if > standard allocation)

Risk Indicators:
  - Missing effort estimates
  - Resource constraints
  - External dependencies
  - Skill gaps
  - Overcommitment (>30 pts/person typical for 2-week PI)
```

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║           TEAM: Example Team                ║
╚════════════════════════════════════════════════════════════╝

👥 TEAM PROFILE
  Name:        Example Team
  ID:          1001
  ART:         Data, Analytics and Digital
  Owner:       Shalom Bhooshi
  Members:     2 people
  Status:      Active

🎯 PI-4/25 COMMITMENTS
  Objective:   Enable Data Transfer using MSK
  Status:      Pending (not yet committed)
  Effort:      TBD (not estimated)
  Start:       Jan 2, 2025
  End:         Jan 13, 2025

📊 CAPACITY ANALYSIS
  Team size:        2 people
  Committed effort: TBD points
  Per person:       TBD / 2 = TBD points
  ⚠️ Warning:       No effort estimates yet - get these to assess capacity

⚠️  RISKS IDENTIFIED
  1. Overcommitment: Effort not estimated - can't assess capacity
  2. Dependencies: Waiting on AWS/GxP clearance
  3. Complexity: GxP compliance required (4TB data transfer)
  4. Timeline: Data transfer duration unknown

RECOMMENDATION:
  → Get effort estimate for "Enable Data Transfer" objective
  → Clarify GxP/AWS Transfer Family constraints
  → Assess team capacity before committing
```

## Related User Stories

- US-001: ART Dashboard
- US-003: Objective Deep Dive
- US-004: Release Status Report

## Effort Breakdown

| Activity | Points |
|----------|--------|
| Core implementation | 5 |
| Risk analysis logic | 4 |
| Jira integration | 2 |
| Testing & specs | 2 |
| **Total** | **13** |
