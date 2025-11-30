# Scripts - PI Planning Tools for ART Leadership

This directory contains scripts and specifications for Lead/Principal Engineers managing Agile Release Trains (ARTs) through Program Increment planning cycles.

## Overview

These tools help ART leadership:
- View dashboards of releases, teams, and objectives
- Drill down into team commitments and capacity
- Understand objective dependencies and risks
- Track PI progress and identify blockers
- Correlate TargetProcess objectives with Jira epics

## Directory Structure

```
scripts/
├── README.md                    # This file
├── map-pi-structure.sh          # Discovery script (working)
├── specs/                       # BDD specifications
│   ├── art-dashboard.feature
│   ├── team-deep-dive.feature
│   ├── objective-deep-dive.feature
│   └── release-status.feature
├── user-stories/                # Product requirements
│   ├── us-001-art-dashboard.md
│   ├── us-002-team-deep-dive.md
│   ├── us-003-objective-deep-dive.md
│   └── us-004-release-status.md
└── [To implement]
    ├── art-dashboard.sh
    ├── team-deep-dive.sh
    ├── objective-deep-dive.sh
    └── release-status.sh
```

## Implemented Scripts

### `map-pi-structure.sh` ✅
**Status:** Working
**Purpose:** Discover PI hierarchy starting from ART, team, or release anchor

```bash
./scripts/map-pi-structure.sh --art "Data, Analytics and Digital"
./scripts/map-pi-structure.sh --team "Example Team"
./scripts/map-pi-structure.sh --release "PI-4/25"
```

See: `docs/how-to/discover-pi-structure.md`

## Planned Scripts

### 1. `art-dashboard.sh` 📋
**User Story:** US-001
**Purpose:** High-level dashboard of releases, teams, and objectives for an ART
**Effort:** 13 points

```bash
./scripts/art-dashboard.sh --art "Data, Analytics and Digital"
```

**Deliverables:**
- Release timeline view
- Team participation summary
- Program objectives status
- Health metrics (objective counts by status)
- Filtering: --pi current/upcoming
- Formats: text (default), json, csv

**BDD Spec:** `specs/art-dashboard.feature`

### 2. `team-deep-dive.sh` 👥
**User Story:** US-002
**Purpose:** Drill into a team's PI commitments, capacity, and risks
**Effort:** 13 points

```bash
./scripts/team-deep-dive.sh --team "Example Team"
./scripts/team-deep-dive.sh --team "Example Team" --show capacity
./scripts/team-deep-dive.sh --team "Example Team" --show risks
```

**Deliverables:**
- Team profile (members, capacity)
- PI objectives with status
- Capacity analysis (effort per person)
- Risk identification (overcommitment, dependencies, skills gaps)
- Jira correlation
- Historical PI performance

**BDD Spec:** `specs/team-deep-dive.feature`

### 3. `objective-deep-dive.sh` 🎯
**User Story:** US-003
**Purpose:** Comprehensive view of an objective with dependencies, risks, and Jira correlation
**Effort:** 13 points

```bash
./scripts/objective-deep-dive.sh --objective 2029314
./scripts/objective-deep-dive.sh --objective 2029314 --show dependencies
./scripts/objective-deep-dive.sh --objective 2029314 --show risks
./scripts/objective-deep-dive.sh --objective 2029314 --show jira
```

**Deliverables:**
- Full objective details (description, stakeholders, dates)
- Linked features
- Dependencies (blocks, blocked by, related)
- Risk assessment (technical, schedule, resource, compliance)
- Jira correlation (matching epic, linked issues)
- Decision history and comments

**BDD Spec:** `specs/objective-deep-dive.feature`

### 4. `release-status.sh` 📊
**User Story:** US-004
**Purpose:** PI progress tracking and blocker identification
**Effort:** 13 points

```bash
./scripts/release-status.sh --release "PI-4/25"
./scripts/release-status.sh --release "PI-3/25" --show risks
./scripts/release-status.sh --release "PI-4/25" --compare-with "PI-3/25"
```

**Deliverables:**
- Release information and timeline
- Team participation summary
- Progress metrics (completion %, effort tracking)
- Blocker identification
- Cross-team dependency map
- PI comparison (velocity, trends)
- Executive summary for reporting

**BDD Spec:** `specs/release-status.feature`

## User Stories

### [US-001: ART Dashboard](user-stories/us-001-art-dashboard.md)
**Priority:** High | **Points:** 13

As a Lead/Principal Engineer, I want to see a dashboard of releases, teams, and objectives
so that I can understand the overall state of my program.

### [US-002: Team Deep Dive](user-stories/us-002-team-deep-dive.md)
**Priority:** High | **Points:** 13

As a Lead/Principal Engineer, I want to drill into a team's commitments and capacity
so that I can identify overcommitment and risks.

### [US-003: Objective Deep Dive](user-stories/us-003-objective-deep-dive.md)
**Priority:** High | **Points:** 13

As a Lead/Principal Engineer, I want to understand an objective's dependencies and risks
so that I can manage cross-team coordination and escalate early.

### [US-004: Release Status](user-stories/us-004-release-status.md)
**Priority:** High | **Points:** 13

As a Lead/Principal Engineer, I want to track PI progress and identify blockers
so that I can manage the program to completion.

## BDD Specifications

All scripts are specified using Gherkin BDD format in the `specs/` directory.
These serve as:
1. **Requirements** - Clear specification of expected behavior
2. **Tests** - Can be executed with BDD testing framework
3. **Documentation** - Examples of script usage

### Running Specs

When scripts are implemented, specs can be validated with:
```bash
# Using Behat (PHP) or similar Gherkin executor
behat scripts/specs/

# Or manually verify each scenario
./scripts/art-dashboard.sh --art "Data, Analytics and Digital" | grep "RELEASES"
```

## Development Workflow

1. **Review Requirements** - Read the user story and BDD spec
2. **Implement Script** - Create the bash script with all features
3. **Test Manually** - Run script and verify BDD scenarios pass
4. **Automate Tests** - If using BDD framework, validate all scenarios
5. **Document** - Add to how-to guides and update this README

## Architecture Patterns

All scripts follow these patterns:

### 1. Configuration Discovery
```bash
find_entity_by_name() {
  local entity=$1 field=$2 name=$3
  ./tpcli list "$entity" --take 1000 2>&1 | \
    awk '/^[{\[]/{flag=1} flag' | \
    jq -r ".[] | select(.${field} == \"${name}\") | .Id"
}
```

### 2. JSON Processing
```bash
extract_json() {
  awk '/^[{\[]/{flag=1} flag'  # Skip Request/Response lines
}
```

### 3. Output Formatting
```bash
# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}✓${NC} Completed"
```

### 4. Multiple Output Formats
```bash
case "$format" in
  json)
    echo "$data" | jq .
    ;;
  csv)
    echo "$data" | jq -r '@csv'
    ;;
  markdown)
    generate_markdown "$data"
    ;;
  *)
    display_pretty_text "$data"
    ;;
esac
```

## Related Documentation

- **How-To Guide:** `docs/how-to/discover-pi-structure.md`
- **Tutorial:** `docs/tutorials/04-team-analysis.md`
- **API Reference:** `docs/reference/entity-types.md`
- **Ideas:** `docs/ideas/entity-discovery-helpers.md`

## Dependencies

All scripts require:
- **tpcli** - The TargetProcess CLI tool (core to this repo)
- **jq** - JSON processor
- **bash** - Shell scripting
- **Optional:** Jira CLI for correlation features

## Common Patterns

### Help Text
Every script includes:
```bash
./scripts/art-dashboard.sh --help
```

### Error Handling
Scripts handle:
- Entity not found (with suggestions)
- Empty results
- API errors with helpful messages

### Caching
Consider adding for performance:
```bash
CACHE_DIR=~/.cache/tpcli
# Cache results with TTL for repeated queries
```

## Future Enhancements

- Real-time auto-refresh modes
- Slack/Teams bot integration
- Risk heat maps and trend analysis
- Team capacity utilization charts
- Automated dependency detection
- Custom report generation

## Testing

For now, BDD specs serve as manual test cases.
Future: Implement automated test runner using:
- Behat (PHP)
- Behave (Python)
- Cucumber (Ruby/Node)

## Contributing

When adding new scripts:
1. Create BDD spec first (test-driven)
2. Implement script
3. Add user story documentation
4. Update this README
5. Add to how-to guides

---

**Status:** In planning phase (US-001 through US-004)
**Total Effort:** 52 points (4 user stories)
**Target:** Sprint 2-3 of this initiative
