# US-003: Objective Deep Dive - Dependencies & Risks

**Status:** Proposed
**Priority:** High
**Story Points:** 13
**Epic:** PI Planning Tools
**Related BDD Spec:** `scripts/specs/objective-deep-dive.feature`

## User Story

As a **Lead/Principal Engineer**
I want to **drill into an objective's details and relationships**
So that **I can manage dependencies, identify risks, and correlate with Jira**

## Description

A single objective often has complex context that lives across multiple systems:

1. **Rich Description** - Often structured YAML/JSON with decision context
2. **Linked Work** - Features/epics in TargetProcess
3. **Dependencies** - What other teams/work items this depends on
4. **Risks & Mitigations** - Known issues and mitigation strategies
5. **Jira Correlation** - Related epics/issues in Jira
6. **Stakeholders** - Who owns, sponsors, and works on this
7. **History** - Comments, decisions, status changes

## Acceptance Criteria

### AC1: Display Objective Core Info
```gherkin
Given I run: ./scripts/objective-deep-dive.sh --objective 2029314
Then I see objective details:
  - Name, ID, type (Team or Program)
  - Status, owner
  - Release, dates
  - Description (full text)
```

### AC2: Show Linked Features
```gherkin
When I run with --show features
Then I see all linked features:
  - Feature name, ID, status
  - Effort estimate
  - Owner team
  - Parent epic (if any)
```

### AC3: Display Dependencies
```gherkin
When I run with --show dependencies
Then I see:
  - "Blocks" relationships
  - "Blocked by" relationships
  - Related objectives
  - External dependencies (e.g., approvals)
```

### AC4: Show Risk Assessment
```gherkin
When I run with --show risks
Then I see identified risks:
  - Technical risks
  - Schedule risks
  - Resource/skill gaps
  - Dependency risks
  - Mitigation strategies
```

### AC5: Correlate with Jira
```gherkin
When I run with --show jira
Then I see:
  - Matching Jira epics (if linked)
  - Epic status
  - Linked Jira issues
  - Suggested epic name (if not yet linked)
```

### AC6: Show Stakeholders
```gherkin
When I run with --show stakeholders
Then I see:
  - Owner
  - Team responsible
  - Sponsors
  - Collaborators
  - Watchers
```

## Definition of Done

- [x] Core objective details displayed
- [x] Rich description parsing (YAML/structured)
- [x] Linked work items shown
- [x] Dependencies identified and visualized
- [x] Risk assessment included
- [x] Jira correlation
- [x] Stakeholder information
- [x] Export formats (markdown, json)
- [x] BDD spec passes
- [x] Integration tests

## Technical Approach

**Script:** `scripts/objective-deep-dive.sh`

**Query Strategy:**
1. Get objective details: `tpcli get TeamPIObjectives <id>` or `tpcli get ProgramPIObjectives <id>`
2. Get linked features: `tpcli list Features --where "TeamPIObjective.Id eq <id>"`
3. Parse description for structured content (YAML/JSON)
4. Analyze for risks and dependencies
5. Search for related Jira issues

## Data Enrichment

```
Risk Analysis:
  - Missing effort estimates → "Effort estimation risk"
  - Missing features → "No work items linked"
  - External dependencies → "Blocked by external"
  - Stakeholders with [emoji] or custom field → Priority indicator

Jira Correlation:
  - Search Jira for objective name (fuzzy match)
  - Look for epic with matching external ID
  - Suggest epic creation if not found
```

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║  OBJECTIVE: Enable Data Transfer using MSK                 ║
║  ID: 2029314 | Type: TeamPIObjective | Status: Pending     ║
╚════════════════════════════════════════════════════════════╝

📋 DETAILS
  Team:          Example Team (1001)
  Release:       PI-4/25 (Jan 2-13, 2025)
  Status:        Pending (not yet committed)
  Owner:         Shalom Bhooshi
  Created:       Oct 28, 2025 by Shalom Israel Bhooshi
  Committed:     No
  Effort:        Not estimated

📝 DESCRIPTION (structured)
  title: IronMountain → Takeda Databricks S3 transfer
  cloud_request_id: 1750
  status: in_progress
  priority: high

  Objective: Transfer 4+ TB of OCR PDFs from IronMountain to Databricks S3
  Primary approach: S3-S3 replication (cross-account)
  Alternate: SFTP if needed

  Action items:
    - Cancel existing CSE request; inform Alex
    - Share meeting notes/specs/timelines/repos/accounts

📌 LINKED FEATURES
  None found yet (should link to implementation work)

🔗 DEPENDENCIES
  Blocks:        Nothing identified yet
  Blocked by:    AWS Transfer Family approval (not approved for PROD/GxP)
                 GxP compliance review needed
  External deps: IronMountain vendor account access
                 AWS cross-account role setup

⚠️  RISKS (5 identified)
  1. GxP Compliance Risk
     - Status: Likely GxP required
     - Mitigation: Get early GxP review on approach

  2. AWS Transfer Family Constraint
     - Status: NOT approved for PROD/GxP
     - Mitigation: Use S3-S3 replication or validate SFTP controls

  3. Timeline Risk
     - Status: 4TB transfer duration unknown
     - Mitigation: Run POC to estimate transfer time

  4. Technical Complexity
     - Status: Cross-account setup, KMS, versioning
     - Mitigation: Team has infrastructure expertise

  5. Effort Unknown
     - Status: Not estimated
     - Mitigation: Break into features and estimate work

👥 STAKEHOLDERS
  Owner:         Shalom Bhooshi (Example Team)
  Team:          Example Team
  Sponsor:       Stephane Dattenny
  Collaborators: Karol Lacuska, Florian Jantscher, Jan Felix Meyer,
                 Matthias Greinecker, Nivedha Sampath
  External:      Saso Jezernik (requester)

🔀 JIRA CORRELATION
  Matching epic:  EX-2527 (Iron Mountain S3-to-S3 replication)
  Jira status:    Funnel (In Progress)
  Linked issues:  EX-2527, EX-2528, ...

  Correlation:
    ✓ Objective: "Enable Data Transfer using MSK"
    ✓ Jira Epic: "Iron Mountain S3-to-S3 replication pattern"
    Status alignment: Objective is Pending, Epic is Funnel (in progress)

  Note: Jira epic is actively being worked; TP objective is still pending

💬 COMMENTS & HISTORY
  Latest:  Nov 20 - Shalom: "Work to be carried out in GitHub issue #15"
           Link: github.com/Example/.../issues/15

  Key decisions:
    - Nov 20: Chose S3-S3 over SFTP
    - Oct 30: Created as replacement for PROJ-13937

✅ EXECUTIVE SUMMARY
  Status: Objective pending commitment - needs effort estimate
  Risk level: MEDIUM (3 unresolved risks)
  Readiness: 40% (effort unknown, risks identified, Jira epic active)

  Recommendation:
    1. Link this objective to Jira epic EX-2527 (already active)
    2. Create TargetProcess features for:
       - POC: Estimate 4TB S3 transfer duration
       - Setup cross-account access
       - Implement replication
       - Testing and validation
    3. Resolve GxP compliance early
    4. Get effort estimates by end of this week
```

## Related User Stories

- US-001: ART Dashboard
- US-002: Team Deep Dive
- US-004: Release Status Report

## Effort Breakdown

| Activity | Points |
|----------|--------|
| Core functionality | 5 |
| Risk analysis | 3 |
| Jira search/correlation | 3 |
| Description parsing | 2 |
| **Total** | **13** |
