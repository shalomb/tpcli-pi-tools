# Team Planning Scripts - Requirements & Roadmap

## The Team Planning Problem Statement

Teams need to plan hierarchically:
- **Program Objectives** (What is the ART trying to achieve?)
- ↓ **Team Objectives** (What is our team committed to?)
- ↓ **Features/Epics** (How do we implement it?)
- ↓ **Stories** (Day-to-day execution)

But the UI/tools available are fragmented. Teams need **focused, role-based views** that show this hierarchy in context.

---

## Planning Workflow by Role

### 1. Team Lead / Scrum Master
**"I need to understand what my team is accountable for"**

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pi-list` | Find context window | ART (opt) | Current/upcoming PIs |
| `pi-objectives` | Understand program goals | PI (opt) | Objectives + team breakdown |
| `team-dashboard` | **Team snapshot** | Team name | Objectives, features, capacity, risks |
| `team-objectives` | **Our commitments** | Team, PI | List of committed objectives |
| `team-features` | **Our work** | Team, PI | Features implementing objectives |
| `team-risks` | **What could go wrong** | Team, PI | Risk register |
| `team-dependencies` | **Who we need** | Team, PI | Blocking/blocked-by relationships |

### 2. Product Owner / Team Member
**"I need to break down objectives into implementable work"**

| Script | Purpose |
|--------|---------|
| `team-objectives` | What are we committing to? |
| `team-features` | What features implement this? |
| `feature-stories` | What stories make up the feature? |
| `feature-analysis` | Status, blockers, dependencies |

### 3. Team Capacity Planner
**"I need to understand what we can actually commit to"**

| Script | Purpose |
|--------|---------|
| `team-dashboard` | Capacity, allocation, utilization |
| `team-capacity` | **Detailed capacity analysis** |
| `team-allocation` | Who is allocated to what? |
| `team-velocity` | Historical velocity for estimation |

### 4. Program Manager / Release Train Engineer
**"I need to see the whole picture"**

| Script | Purpose |
|--------|---------|
| `pi-list` | All PIs in timeline |
| `pi-status` | ✓ **Progress tracking** |
| `pi-objectives` | **Program objectives by team** |
| `pi-risks` | **Aggregated program risks** |
| `pi-dependencies` | **Critical path & blockers** |

### 5. Executive / Stakeholder
**"I need to know if we're on track"**

| Script | Purpose |
|--------|---------|
| `art-dashboard` | ✓ **ART overview** |
| `pi-list` | Timeline of PIs |
| `pi-status` | ✓ **Current PI progress** |

---

## Script Implementation Roadmap

### TIER 1: FOUNDATIONAL (Weeks 1-2)
**Enable basic planning: context → plan → execute**

- [ ] **`pi-list`** - List all PIs with dates, status, team count
- [ ] **`team-dashboard`** - Team summary: objectives, features, capacity, risks
- [ ] **`team-objectives`** - Team's committed objectives for current PI
- [ ] **`team-features`** - Features/epics assigned to team for current PI

**Effort:** 8-10 hours  
**Why first:** These are the foundational views every team needs to start planning

**Quick implementations:**
```python
# pi-list: Get releases
releases = client.get_releases()

# team-dashboard: Combine existing queries
objectives = client.get_team_pi_objectives(team_id, release_id)
features = client.get_features(team_id, release_id)

# team-objectives: Format objective data
objectives = client.get_team_pi_objectives(team_id, release_id)

# team-features: Link features to objectives
features = client.get_features(team_id, release_id)
objectives = client.get_team_pi_objectives(team_id)
```

### TIER 2: OPERATIONAL (Weeks 2-3)
**Support execution and day-to-day tracking**

- [ ] **`team-capacity`** - Capacity analysis: allocated, available, utilization%
- [ ] **`pi-objectives`** - Program objectives broken down by team allocation
- [ ] **`team-risks`** - Team risks and issues (risk register)
- [ ] **`team-dependencies`** - Cross-team dependencies and critical path

**Effort:** 10-12 hours  
**Why second:** These enable daily standup conversations and capacity planning

**Needs:** Transformation functions for risk aggregation, dependency mapping

### TIER 3: REPORTING (Weeks 3+)
**Aggregate visibility for communication up the chain**

- [ ] **`pi-list` (enhanced)** - Extended with status, health, team count
- [ ] **`pi-risks`** - Aggregated risks across teams with heatmap
- [ ] **`pi-dependencies`** - Program-level critical path and blockers

**Effort:** 8-10 hours  
**Why third:** These are for executive visibility and PI health tracking

**Needs:** Health scoring, risk aggregation, critical path analysis

---

## Script Naming Convention

Organized by scope for natural collation:

```
art-*           ART-level overview
  art-dashboard       ✓ Exists

pi-*            PI/Release-level planning & status
  pi-list             ← NEW (foundational) - Timeline and overview
  pi-status           ✓ Exists - Progress tracking
  pi-objectives       ✓ Exists - Program decomposition
  pi-risks            ← NEW (reporting) - Aggregated risks
  pi-dependencies     ← NEW (reporting) - Critical path

team-*          Team-level planning & execution
  team-analysis       ✓ Exists - Team deep-dive
  team-dashboard      ← NEW (foundational) - Team snapshot
  team-objectives     ← NEW (foundational) - Commitments
  team-features       ← NEW (foundational) - Work items
  team-capacity       ← NEW (operational) - Capacity analysis
  team-risks          ← NEW (operational) - Risk register
  team-dependencies   ← NEW (operational) - Cross-team links

feature-*       Feature/Epic-level (future expansion)
  feature-stories     ← FUTURE - Story decomposition
  feature-analysis    ← FUTURE - Feature status & risks
```

---

## Data Transformations Needed

### 1. Program Decomposition
Link Program Objectives → Team Objectives → Features

```
Program Objective
  ├─ Team A Objective (effort: 21pts)
  │   ├─ Feature 1 (8pts)
  │   ├─ Feature 2 (13pts)
  ├─ Team B Objective (effort: 13pts)
  │   ├─ Feature 3 (13pts)
```

**Functions needed:**
- `get_teams_for_program_objective(program_obj_id)` → List teams
- `get_team_contribution_to_objective(team_id, program_obj_id)` → Effort split
- `aggregate_feature_effort_by_objective()` → Progress roll-up

### 2. Team Allocation
Show what's committed vs. capacity

```
Team "Cloud Enablement"
├─ Committed Objectives
│   ├─ "Enable MSK" (21pts)
│   ├─ "Prove Observability" (13pts)
│   └─ Total: 34pts
├─ Total Capacity: 40pts (per PI)
└─ Available: 6pts
```

**Functions needed:**
- `calculate_team_committed_effort(team_id, release_id)` → Total effort
- `get_team_capacity(team_id)` → Max capacity
- `calculate_utilization_pct()` → Committed % of capacity

### 3. Risk Aggregation
Roll up team risks to PI level

```
Team Risks:
  ├─ Technical: 2 high, 1 critical
  ├─ Capacity: over-allocated
  └─ Dependency: blocked on Team B

Team Health Score: 45/100 (Red)
```

**Functions needed:**
- `aggregate_team_risks(team_id)` → Risk summary
- `calculate_team_health_score()` → Overall health
- `get_blocking_dependencies()` → Critical blockers

### 4. Dependency Mapping
Find cross-team dependencies

```
Feature: "Kafka Integration" (Team A)
  ├─ depends_on: "Schema Registry" (Team B)
  └─ blocks: "Data Pipeline" (Team C)
```

**Functions needed:**
- `get_feature_dependencies()` → All dependencies
- `find_critical_path()` → Serialization risk
- `detect_circular_deps()` → Impossible sequences

---

## Implementation Notes

### Existing Infrastructure to Leverage

1. **TPAPIClient** - Already has all base queries
   - `get_team_pi_objectives(team_id, release_id)`
   - `get_features(team_id, release_id)`
   - `get_releases()` for timeline
   - Caching already built-in (1 hour TTL)

2. **Analysis Models** - Risk framework exists
   - `RiskAnalyzer` class
   - `CapacityAnalyzer` class
   - `RiskLevel` and `RiskCategory` enums
   - Can be extended for aggregation

3. **CLI Framework** - Click templates
   - 4 existing scripts show patterns
   - Rich library for formatting
   - Config file support for defaults

### Quick Wins (Implement First)

1. **`pi-list`** (30 mins)
   ```python
   releases = client.get_releases()
   # Just format: name, start_date, end_date, status
   ```

2. **`team-objectives`** (1 hour)
   ```python
   objectives = client.get_team_pi_objectives(team_id, release_id)
   # Format with status, effort, owner
   ```

3. **`team-features`** (1.5 hours)
   ```python
   features = client.get_features(team_id, release_id)
   objectives = client.get_team_pi_objectives(team_id)
   # Cross-link and format
   ```

4. **`team-dashboard`** (2 hours)
   ```python
   # Combine above queries + risk/capacity analysis
   # Create summary view
   ```

---

## User Value by Script

| Script | Who Uses | Frequency | Value |
|--------|----------|-----------|-------|
| `pi-list` | Everyone | Weekly | "Are we in planning or execution?" |
| `team-dashboard` | Team Leads | Daily | "Health snapshot" |
| `team-objectives` | POs | Daily | "What are we building?" |
| `team-features` | Team Members | Daily | "My work context" |
| `team-capacity` | Planners | Weekly | "Can we commit to more?" |
| `pi-objectives` | PMs | Weekly | "Program alignment" |
| `team-risks` | Leads | Weekly | "What's at risk?" |
| `pi-risks` | Executives | Weekly | "Program health" |
| `pi-dependencies` | PMs | Weekly | "Critical path" |

---

## Success Criteria

These scripts will be successful when:

1. **Team Leads** can run `team-dashboard` in 10 seconds and see their status
2. **POs** can run `team-features` to understand what's assigned vs. ready
3. **Capacity Planners** can run `team-capacity` to see available bandwidth
4. **PMs** can run `pi-list` and know which PIs to focus on
5. **Executives** can run `pi-risks` to identify program health issues

---

## Next Steps

1. **Validate script list** with actual teams
   - Does this cover their planning workflow?
   - Missing anything critical?
   - Too many? (prioritize)

2. **Design data transformations** (beyond this doc)
   - Specific field mappings
   - Aggregation logic
   - Performance considerations

3. **Build Phase 1** (foundational scripts)
   - Implement pi-list, team-dashboard, team-objectives, team-features
   - Get user feedback
   - Iterate

4. **Build Phase 2** (operational scripts)
   - Add team-capacity, pi-objectives decomposition, team-risks, team-dependencies
   - Build transformation functions
   - Test with real data

5. **Build Phase 3** (reporting scripts)
   - Aggregate views for executives
   - Health scoring
   - Critical path analysis
