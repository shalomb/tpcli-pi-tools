# How-To: Discover PI Planning Structure

Learn how to explore Program Increment (PI) planning context in TargetProcess using entity names instead of IDs.

## Overview

The `map-pi-structure.sh` script helps you quickly understand PI planning hierarchies by providing a tree view of:
- **Agile Release Trains (ARTs)** and their releases
- **Program PI Objectives** (ART-level strategic goals)
- **Team PI Objectives** (team-level commitments)
- **Features** linked to objectives
- **Relationships** between planning elements

## Basic Usage

### Discover by Agile Release Train (ART)

View all releases and objectives for an ART:

```bash
./scripts/map-pi-structure.sh --art "Data, Analytics and Digital"
```

Output:
```
📦 AGILE RELEASE TRAIN
  ✓ Data, Analytics and Digital (ID: 1936122)

📋 RELEASES/PROGRAM INCREMENTS
  ├─ PI-4/25 (ID: 1942235)
  │  🎯 PROGRAM PI OBJECTIVES
  │  ├─ Objective 1 [Draft]
  │  👥 TEAM PI OBJECTIVES
  │  ├─ Team Superman (DQH): UI Enablement [Pending]
  │  ├─ PIC - Thanos: Improve release stability [Pending]
  │  └─ Example Team: Enable Data Transfer [Pending]
  │
  └─ PI-3/25 [CURRENT]
     👥 TEAM PI OBJECTIVES
     ├─ DAD Cloud-DevSecOps: Establish Platform Architecture [Pending]
     └─ ... (more objectives)
```

### Discover by Team

View all PI objectives assigned to a team:

```bash
./scripts/map-pi-structure.sh --team "Example Team"
```

Output:
```
👥 TEAM
  ✓ Example Team (ID: 1001)

🎯 PI OBJECTIVES
  ├─ Enable Data Transfer using MSK [Pending] (ID: 2029314)
  │  Release: PI-4/25
  │  Features:
  │  └─ (none found)
```

### Discover by Release/PI

View all objectives in a specific program increment:

```bash
./scripts/map-pi-structure.sh --release "PI-4/25"
```

Output:
```
📋 RELEASE/PROGRAM INCREMENT
  ✓ PI-4/25 (ID: 1942235)
  ART: Data, Analytics and Digital

🎯 PROGRAM PI OBJECTIVES
  ├─ Objective 1 [Draft]

👥 TEAM PI OBJECTIVES
  ├─ Team Superman (DQH): UI Enablement [Pending]
  ├─ PIC - Stan Lee: Accelerate Master Data Discovery [Pending]
  └─ ... (more team objectives)
```

## Practical Workflows

### PI Planning Context

Before a PI Planning event, understand what's planned:

```bash
# View the current/upcoming PI structure
./scripts/map-pi-structure.sh --release "PI-4/25"

# See all team objectives in one PI
# Use this to understand capacity and cross-team dependencies
```

### Team Workload Analysis

Check what your team committed to:

```bash
# See all your team's PI objectives
./scripts/map-pi-structure.sh --team "Your Team Name"

# Look for:
# - Status (Pending, Accepted, etc.)
# - Related features (planned work)
# - Release dates
```

### Cross-Team Dependency Mapping

Understand who depends on you:

```bash
# View the full ART structure
./scripts/map-pi-structure.sh --art "Your ART Name"

# Scan for objectives mentioning your team or area
# Look for "BLOCKS" relationships
```

### Integration with Jira

After getting objectives from TargetProcess:

```bash
# Get the PI structure
PI_STRUCT=$(./scripts/map-pi-structure.sh --release "PI-4/25")

# Extract objective names
echo "$PI_STRUCT" | grep "├─\|└─"

# Use objective names to search Jira
OBJECTIVE_NAME="Enable Data Transfer using MSK"
jira issue list --jql "text ~ '$OBJECTIVE_NAME'"
```

## Understanding the Output

### Status Indicators

- **[Pending]** - Not yet committed/accepted
- **[Draft]** - Being prepared, not finalized
- **[Accepted]** - Committed to the PI
- **[In Progress]** - Currently being worked on
- **[Done]** - Completed

### Hierarchy Symbols

```
├─ Regular item
└─ Last item in group
│  Continuation line (relationship)
```

### IDs

Each entity shows its TargetProcess ID:
```
Enable Data Transfer using MSK [Pending] (ID: 2029314)
                                            └─ Use this for direct tpcli queries
```

## Finding Entities

The script automatically looks up entities by name. If not found:

```bash
# List all ARTs
./tpcli list AgileReleaseTrains --take 100

# List all teams
./tpcli list Teams --take 100

# List all releases
./tpcli list Releases --take 100
```

Copy the exact name and use it with the script.

## Troubleshooting

### "Entity not found"

**Problem:** Script says the team/ART/release doesn't exist.

**Solution:** Check the exact name:
```bash
# See all teams
./tpcli list Teams --take 1000 | grep -i "name"

# Use the exact name from the output
./scripts/map-pi-structure.sh --team "Exact Name Here"
```

### No objectives appear

**Problem:** Objectives list is empty.

**Reasons:**
- No objectives created yet for this team/ART
- Objectives are in a different release
- The team isn't assigned to any objectives

**Solution:** Check the TargetProcess UI or list raw data:
```bash
./tpcli list TeamPIObjectives --where "Team.Id eq 1001" --take 100
```

### Verbose output interferes

**Problem:** Seeing "Request:" and "Response:" lines mixed in output.

**Solution:** The script filters these automatically. If you see them in output, check your tpcli config:
```bash
cat ~/.config/tpcli/config.yaml | grep verbose
```

Set `verbose: false` if not needed for debugging.

## Next Steps

Once you understand the PI structure:

1. **Link Objectives to Epics** - Create Jira epics that correspond to TP objectives
2. **Track Progress** - Monitor feature completion relative to objective deadlines
3. **Manage Dependencies** - Use the hierarchy to identify cross-team work
4. **Update Capacities** - Track team availability vs. committed work

## Related

- [How-To: Team Analysis & Workload Management](./team-analysis.md)
- [How-To: List and Filter Entities](./list-and-filter.md)
- [Tutorial: Team Analysis & Workload Management](../tutorials/04-team-analysis.md)
- [Idea: Entity Discovery Helpers](../ideas/entity-discovery-helpers.md)
