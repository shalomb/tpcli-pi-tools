# Product Requirements Document: Bidirectional Plan Sync

**Status**: Draft / Planning Phase
**Last Updated**: 2025-11-30
**Owner**: Engineering Team
**Version**: 1.0

---

## 1. Overview

### Problem Statement

Teams managing Agile Release Trains (ARTs) in TargetProcess need to:
- Export current PI planning (objectives, epics, capacity) to edit locally
- Collaborate on plan refinement using tools they know (markdown + git)
- Push changes back to TargetProcess while detecting/resolving conflicts
- Maintain bidirectional sync across multiple planning cycles

**Current State**: No tooling exists for this workflow. Users must:
1. Manually read data from TargetProcess UI
2. Copy-paste into documents
3. Manually re-enter changes back into TargetProcess
4. Handle conflicts manually when multiple people edit

**Proposed Solution**: `tpcli plan` subcommand with export/import/merge capabilities

### Goals

1. **Reduce friction**: Export → edit → import workflow (not copy-paste)
2. **Enable collaboration**: Git + markdown for team editing
3. **Prevent data loss**: Automatic conflict detection with 3-way merge
4. **Maintain source of truth**: TargetProcess remains canonical, markdown is working copy
5. **Track changes**: Clear audit trail of who changed what
6. **Scale to ongoing sync**: Support multiple pull/edit/push cycles per PI

### Out of Scope (for MVP)

- Capacity planning and resource allocation
- Story and task decomposition (those follow Team Objectives)
- Sprint planning and burndown
- Integration with external tools (Jira, GitHub, etc.)

---

## 2. User Workflows

### 2.1 Initial Export Workflow

**User Goal**: "I want to pull down our team's plan for the upcoming PI so we can refine it together"

```bash
# 1. Export team objectives and program objectives for context
tpcli plan export \
  --release "PI-4/25" \
  --team "Platform Eco" \
  --output objectives.md

# Output: objectives.md with YAML frontmatter + markdown sections
# - Program objectives listed for alignment reference
# - Team objectives with details
# - Epics as subsections under objectives
# - All with TargetProcess IDs preserved
```

**Expected Output**:
- Single markdown file
- YAML frontmatter with metadata (release, team, export timestamp, IDs)
- Structured sections for objectives and epics
- Ready for team editing

### 2.2 Edit Workflow

**User Goal**: "I want to edit this plan collaboratively using markdown and git"

```bash
# 1. User edits objectives.md locally
#    - Changes objective descriptions
#    - Renames epics
#    - Adds new epics (new ### sections)
#    - Changes effort estimates
#    - Uses git to track changes

git add objectives.md
git commit -m "Refine Platform Eco PI-4/25 plan: add observability epic"

# 2. User can preview changes before pushing
tpcli plan import --file objectives.md --dry-run

# Expected: Shows what will be created/updated in TargetProcess
# - New epics: [ Monitoring Integration ]
# - Updated objectives: [ Platform Governance (effort: 21→34) ]
# - No conflicts detected
```

### 2.3 Push with Merge Conflict Resolution

**User Goal**: "I want to push my changes but handle conflicts if others edited the same plan"

```bash
# 1. User attempts import
tpcli plan import --file objectives.md

# 2. System detects conflicts (because TP was updated after export)
# Conflict Example:
#   Objective "Enable Data Transfer using MSK"
#   - Local (your edit): effort 13 → 21, owner changed
#   - Remote (from TP): status changed to "In Progress"
#   - Base (last synced): effort 13, status "Pending"

# 3. System shows git-style conflict markers in file
<<<<<<< local (your edits)
Effort: 21
Owner: Sarah Chen
=======
Status: In Progress
>>>>>>> remote (from TargetProcess)

# 4. User resolves conflicts manually
# - Edit the file to keep desired state
# - Remove conflict markers
# - git add and retry import

tpcli plan import --file objectives.md --no-conflict-check  # Force apply after resolution
```

### 2.4 Ongoing Sync (Multiple Cycles)

**User Goal**: "We want to track our planning over multiple PIs and sync bidirectionally"

```bash
# Week 1: Initial planning
tpcli plan export --release "PI-4/25" --team "Platform Eco" > pi-4-25-plan.md
git add pi-4-25-plan.md

# Week 2: Team refines plan
# - Edit pi-4-25-plan.md
# - Commit changes
git commit -m "Add new security epic based on compliance review"

# Week 3: Sync changes back to TP
tpcli plan import --file pi-4-25-plan.md  # Pushes changes back

# Week 4: Someone updated TP directly (bug fix, new constraint)
# Next export detects changes
tpcli plan export --release "PI-4/25" --team "Platform Eco" > pi-4-25-plan.md
# System detects conflicts and marks them in the file

# Week 5: Resolve conflicts and re-sync
git add pi-4-25-plan.md
tpcli plan import --file pi-4-25-plan.md

# This workflow repeats throughout the PI
```

---

## 3. Data Model

### 3.1 Entity Relationships

```
AgileReleaseTrain (ART)
│
├── Release (PI)
│   │
│   ├── ProgramPIObjective
│   │   ├── name, description, status, effort, owner
│   │   ├── release_id → Release
│   │   └── art_id → ART
│   │
│   └── Team (belongs to ART)
│       │
│       └── TeamPIObjective
│           ├── name, description, status, effort, owner
│           ├── team_id → Team
│           ├── release_id → Release
│           ├── program_objective_id → ProgramPIObjective (ONE-TO-ONE link)
│           ├── committed (bool)
│           │
│           └── Epic (as markdown subsection)
│               ├── name (= subsection title)
│               ├── description (markdown body)
│               ├── parent_objective_id → TeamPIObjective
│               └── (stored as Feature with parent_epic_id in TP)
```

### 3.2 Markdown Representation

**Structure**: Team Objectives as H2 sections, Epics as H3 subsections

```markdown
---
# YAML Frontmatter (metadata for sync)
release: "PI-4/25"
team: "Platform Eco"
art: "Data, Analytics and Digital"
exported_at: "2025-11-30T10:30:00Z"
objectives:
  - id: 2019099
    name: "Platform governance for PIC teams"
    synced_at: "2025-11-30T10:30:00Z"
---

# PI-4/25 Plan - Platform Eco

_Sync Status: Last exported 2025-11-30. Last synced 2025-11-25._

## Program Objectives (for reference/alignment)

- **Objective 1**: Some program objective
- **Objective 2**: Another program objective

> These are read-only reference. Team Objectives below align to these.

## Team Objective: Platform governance for PIC teams and process improvements

**TP ID**: 2019099
**Status**: Pending
**Effort**: 21 points
**Owner**: Norbert Borský
**Program Objective**: (links to one of the program objectives above)
**Team**: Platform Eco
**Release**: PI-4/25

### Description

Establish governance frameworks and processes for Platform Infrastructure teams to ensure consistency, compliance, and knowledge sharing across the organization.

### Epic: Governance Framework Definition

Define the core governance model including:
- Decision-making structure
- Change management process
- Architecture review board

**Owner**: John Smith
**Status**: Planned
**Effort**: 8 points

### Epic: Process Documentation

Document all processes:
- Team onboarding
- Incident response
- Change procedures

**Owner**: Jane Doe
**Status**: Planned
**Effort**: 8 points

### Epic: Training and Enablement

Create training materials and run sessions for all teams.

**Owner**: Bob Jones
**Effort**: 5 points

---

## Team Objective: Supporting the DQ initiative

**TP ID**: 2027963
**Status**: In Progress
**Effort**: 34 points
**Owner**: Sarah Chen
**Program Objective**: Data Quality Improvements

(... more sections)
```

### 3.3 Metadata Fields

**Frontmatter** (YAML, preserved across syncs):
- `release` - Release/PI name (e.g., "PI-4/25")
- `team` - Team name
- `art` - ART name
- `exported_at` - Timestamp of last export
- `objectives` - Array of objective metadata for conflict detection:
  - `id` - TargetProcess objective ID
  - `name` - Objective name (for tracking renames)
  - `synced_at` - Last sync timestamp (for conflict detection)

**Per-Objective Metadata** (YAML in markdown body):
- `TP ID` - TargetProcess ID for matching
- `Status` - Current status (Pending, In Progress, Done, etc.)
- `Effort` - Story points
- `Owner` - Person responsible
- `Program Objective` - Links to program objective (one-to-one)

**Per-Epic Metadata**:
- `Owner` - Person responsible
- `Status` - Epic status
- `Effort` - Total effort estimate

---

## 4. Conflict Detection and 3-Way Merge

### 4.1 Conflict Scenarios

| Scenario | Local | Base | Remote | Resolution |
|----------|-------|------|--------|------------|
| User edits objective name | "New Name" | "Old Name" | "Old Name" | ✓ Accept local (clean change) |
| User edits description | "Updated..." | "Original..." | "Original..." | ✓ Accept local (clean change) |
| TP updates status | "Pending" | "Pending" | "In Progress" | ✓ Accept remote (TP source) |
| Both edit effort | 21 | 13 | 20 | ✗ **CONFLICT**: Show 3-way diff |
| User adds epic | [new] | [none] | [none] | ✓ Accept local (create new) |
| TP adds epic | [none] | [none] | [new] | ✓ Accept remote (add new) |
| Both add same epic | [local] | [none] | [remote] | ✗ Check if names match → merge |

### 4.2 3-Way Merge Algorithm

```
For each Objective:
  IF objective.id exists in local AND remote:
    FOR each field (name, effort, status, owner, description):
      IF local.field == base.field AND base.field != remote.field:
        # Remote only changed
        USE remote.field  (✓ accept)
      ELIF local.field != base.field AND base.field == remote.field:
        # Local only changed
        USE local.field  (✓ accept)
      ELIF local.field == remote.field:
        # Both same (or both unchanged)
        USE local.field  (✓ accept)
      ELIF local.field != remote.field AND base.field != local.field AND base.field != remote.field:
        # Both changed differently
        MARK CONFLICT  (✗ needs manual resolution)

  ELIF objective.id exists only in local:
    # User added new objective
    CREATE new objective  (✓ accept)

  ELIF objective.id exists only in remote:
    # TP added new objective
    ADD to local markdown  (✓ accept)
```

### 4.3 Conflict Markers

When conflicts detected, system injects git-style markers into markdown:

```markdown
## Team Objective: Enable Data Transfer using MSK

**TP ID**: 2019099
**Status**: Pending
<<<<<<< local (your edits)
**Effort**: 21 points
**Owner**: Sarah Chen
=======
**Effort**: 13 points
**Owner**: John Doe
>>>>>>> remote (from TargetProcess)

### Description

(... no conflict in description)

### Epic: MSK Configuration

<<<<<<< local
Implementation details using AWS MSK...
=======
Setup and configuration procedures...
>>>>>>> remote
```

**User Resolution Process**:
1. User manually edits the file to resolve conflicts
2. Removes conflict markers (keep desired version)
3. Commits to git
4. Runs `tpcli plan import --file objectives.md` again
5. If no markers remain, import succeeds

### 4.4 Handling Epics (Features)

**Epics are matched by name** (not ID):
- If H3 section title exists in both local and remote: 3-way merge
- If H3 section title only in local: create new epic
- If H3 section title only in remote: add to local markdown

**Special case - Epic rename**:
- If epic ID stays same but name changes: treated as update
- If epic ID changes: might be detected as delete + create

---

## 5. Implementation Requirements

### 5.1 Go CLI Commands (tpcli foundation)

**Required additions to tpcli**:

```bash
# Create entity
tpcli create <EntityType> --data '<json>'
# Example: tpcli create TeamPIObjectives --data '{"Name":"...","Team":{"Id":123}}'

# Update entity
tpcli update <EntityType> <id> --data '<json>'
# Example: tpcli update TeamPIObjectives 2019099 --data '{"Effort":21}'

# These commands POST to TargetProcess API
# - Return JSON response with created/updated entity
# - Support --verbose flag for debugging
# - Proper error handling for validation failures
```

### 5.2 Python API Client Extensions

**New methods in `TPAPIClient`**:

```python
# Create operations
create_team_objective(name, team_id, release_id, ...)
create_feature(name, team_id, release_id, ...)
create_program_objective(name, art_id, release_id, ...)

# Update operations
update_team_objective(objective_id, **kwargs)
update_feature(feature_id, **kwargs)
update_program_objective(objective_id, **kwargs)

# Helpers
fetch_full_state(release_id, team_id)  # Get base for merge
```

### 5.3 Plan Sync Module

**New module**: `tpcli_pi/sync/`

**Components**:
- `markdown_parser.py` - Parse/generate markdown with frontmatter
- `merger.py` - 3-way merge with conflict detection
- `validator.py` - Validate required fields before API calls

**New CLI**: `tpcli_pi/cli/plan.py`

```bash
tpcli plan export --release <name> --team <name> [--output file]
tpcli plan import --file <path> [--dry-run] [--no-conflict-check]
tpcli plan validate --file <path>
```

---

## 6. BDD Test Scenarios

### 6.1 Export Workflow

```gherkin
Feature: Export Team Plan for Editing

  Scenario: Export team objectives with program objectives
    Given I have team "Platform Eco" with 3 Team Objectives
    And these objectives link to Program Objectives
    When I run: tpcli plan export --release "PI-4/25" --team "Platform Eco"
    Then I should see markdown file with:
      | Section | Content |
      | Frontmatter | release: PI-4/25, team: Platform Eco, exported_at |
      | Program Objectives | List of program objectives for reference |
      | Objective 1 | Name, Status, Effort, Owner, ID |
      | Epic 1.1 | Name, Owner, Effort (as H3 section) |
      | Epic 1.2 | Another epic under same objective |
      | Objective 2 | Next objective with its epics |
    And all TargetProcess IDs are preserved in metadata
    And timestamps show when exported

  Scenario: Export uses correct API calls
    When I export with verbose flag
    Then I should see:
      | API Call | Purpose |
      | GET /TeamPIObjectives | Fetch team objectives |
      | GET /ProgramPIObjectives | Fetch program objectives |
      | GET /Features | Fetch epics linked to objectives |
```

### 6.2 Edit and Import Workflow

```gherkin
Feature: Edit Plan and Import Changes

  Scenario: Import modified objectives
    Given I have exported objectives.md
    And I edited objective effort from 13 to 21
    When I run: tpcli plan import --file objectives.md
    Then objective should be updated in TargetProcess with effort 21
    And I should see "Updated 1 objective"

  Scenario: Detect new epics as additions
    Given I have markdown file with 2 epics
    And I added a new H3 section "Epic: New Observability Framework"
    When I run: tpcli plan import --file objectives.md --dry-run
    Then I should see "Create 1 new epic"
    And no changes should be made to TargetProcess

  Scenario: Reject invalid markdown format
    Given I have malformed markdown (missing required metadata)
    When I run: tpcli plan import --file invalid.md
    Then I should see error "Missing objective ID in frontmatter"
    And import should fail
```

### 6.3 Conflict Resolution

```gherkin
Feature: Detect and Resolve Conflicts

  Scenario: Detect conflict when both sides changed same field
    Given I exported objectives.md on 2025-11-25
    And I edited objective effort locally (13 → 21)
    And TargetProcess was updated (effort 13 → 20, by someone else)
    When I run: tpcli plan import --file objectives.md
    Then I should see conflict marker in output:
      """
      <<<<<<< local
      Effort: 21
      =======
      Effort: 20
      >>>>>>> remote
      """
    And import should pause, waiting for manual resolution

  Scenario: Resolve conflict by keeping remote (TargetProcess version)
    Given conflict markers exist in objectives.md
    When I remove conflict marker and keep remote version
    And I run: tpcli plan import --file objectives.md
    Then objective should be updated with remote value (20)
    And import should succeed

  Scenario: Accept non-conflicting changes
    Given I edited objective A effort and owner changed
    And TargetProcess updated objective B status (unrelated)
    When I run: tpcli plan import --file objectives.md
    Then objective A should be updated (no conflict)
    And objective B should be updated (no conflict)
    And import should succeed without prompts

  Scenario: Handle concurrent epic additions
    Given local markdown has new epic "Epic: Monitoring"
    And TargetProcess has new epic "Epic: Observability" (same objective)
    When I run: tpcli plan import --file objectives.md
    Then local epic "Monitoring" should be created
    And remote epic "Observability" should be added to markdown
    And no conflict (both new, non-overlapping)
```

### 6.4 Ongoing Sync Scenarios

```gherkin
Feature: Bidirectional Sync Across Multiple Cycles

  Scenario: Multiple export-edit-import cycles
    Given I exported objectives.md in week 1
    And edited it and imported changes in week 2
    When I export again in week 3
    And TargetProcess was updated (new epic added)
    Then exported markdown should include the new epic
    And previous edits should be preserved
    And no data loss

  Scenario: Track editing history via git
    Given objectives.md in git repository
    When I edit and commit multiple times
    Then git log should show all changes
    And git diff should show what changed
    And I can rollback to any previous version
```

---

## 7. Implementation Phases

### Phase 1: Go CLI Foundation (Week 1)
- [ ] Implement `tpcli create` command
- [ ] Implement `tpcli update` command
- [ ] Test with manual API calls
- [ ] Verify TargetProcess API responses

### Phase 2: Python Wrapper (Week 1)
- [ ] Extend TPAPIClient with create/update methods
- [ ] Add validation before API calls
- [ ] Test with unit tests
- [ ] Handle errors gracefully

### Phase 3: Markdown Parsing (Week 2)
- [ ] YAML frontmatter parsing
- [ ] Objective/epic extraction from markdown
- [ ] Markdown generation from TP data
- [ ] Test with various markdown formats

### Phase 4: 3-Way Merge Engine (Week 2)
- [ ] Base version fetching from TP
- [ ] 3-way merge algorithm
- [ ] Conflict detection
- [ ] Conflict marker injection

### Phase 5: CLI Commands (Week 2-3)
- [ ] `tpcli plan export` command
- [ ] `tpcli plan import` command
- [ ] `tpcli plan validate` command
- [ ] Help text and usage examples

### Phase 6: Testing & Docs (Week 3)
- [ ] BDD tests with behave
- [ ] Unit tests
- [ ] Integration tests
- [ ] User documentation

---

## 8. Success Criteria

### MVP (Minimal Viable Product)

- [ ] `tpcli plan export` exports objectives to markdown with correct metadata
- [ ] `tpcli plan import --dry-run` shows preview without changes
- [ ] `tpcli plan import` pushes changes back to TargetProcess
- [ ] Basic conflict detection (shows when both sides changed same field)
- [ ] Git-style conflict markers injected for manual resolution
- [ ] All TargetProcess IDs preserved for round-trip sync
- [ ] Program objectives shown for reference/alignment
- [ ] Team objectives linked to Program objectives (one-to-one)
- [ ] Epics (Features) sync as subsections
- [ ] No data loss or corruption in sync cycle
- [ ] Helpful error messages for common issues

### Tested

- [ ] Export + edit + import cycle works end-to-end
- [ ] Conflicts detected and resolved correctly
- [ ] Multiple sync cycles don't cause data loss
- [ ] Git workflow supported (commit-before-sync recommended)
- [ ] All BDD scenarios passing

### Documented

- [ ] User guide for export/edit/import workflow
- [ ] Example markdown files showing expected format
- [ ] Troubleshooting guide for conflicts
- [ ] API requirements documented
- [ ] Architecture decisions recorded (this document)

---

## 9. Open Questions & Future Considerations

### Design Questions (Ready to Answer)

1. **Help text**: How should `tpcli help` guide users to the plan commands?
   - Show in main help? Add to workflow section?

2. **File naming**: Should we suggest `{release}-{team}-plan.md` convention?
   - Or let users choose?

3. **Dry-run output**: What should `--dry-run` show exactly?
   - Unified diff? JSON? Structured table?

4. **Conflict resolution UI**: Should we prompt interactively, or expect manual editing?
   - Current: Manual (edit file, remove markers, re-run)
   - Alternative: Interactive TUI prompts

### Future Enhancements (Post-MVP)

1. **Story decomposition**: Break Team Objectives → Epics → Stories → Tasks
2. **Capacity planning**: Track team capacity and utilization
3. **Sprint planning**: Map objectives to sprints and iterations
4. **Integration**: Sync with external tools (Jira, GitHub)
5. **Diff visualization**: Web UI to show changes before applying
6. **Notification**: Alert team when objectives change
7. **Permissions**: Enforce TargetProcess permissions on sync
8. **Audit trail**: Track who made what changes and when
9. **Rollback**: Revert to previous sync point if needed

---

## 10. Architecture Decisions

### Why Git-Style Conflict Markers?

**Chosen**: Manual conflict marker resolution (like git merge conflicts)

**Alternatives considered**:
- Interactive TUI: More user-friendly but more complex to build
- Auto-merge: Risky, users might lose changes silently
- Separate base file: Harder to manage multiple files

**Rationale**:
- Users already know git merge conflicts
- Markdown files are standard, no hidden state
- Users can use any text editor to resolve
- Enables auditing via git commits

### Why Fetch Base from TP (not store in file)?

**Chosen**: Always fetch current state from TP as "base" for merge

**Alternatives considered**:
- Store base in frontmatter: File grows large, harder to diff
- Separate .base file: More files to manage
- Git history: Works but requires git, not always available

**Rationale**:
- TargetProcess is source of truth
- Fresh import always gets accurate base
- Simpler for users (one file to manage)
- Handles case where multiple people exported at different times

### Why One-to-One (Team Objective ↔ Program Objective)?

**Chosen**: Each Team Objective links to exactly one Program Objective

**Alternative**: Many-to-many linking

**Rationale**:
- Simpler data model
- Aligns with SAFe philosophy (each team focused on specific program goals)
- Reduces complexity of conflict resolution
- Can evolve later if needed

### Why Not Version the Export File?

**Chosen**: Single file per team+release (no auto-versioning)

**Alternatives considered**:
- Auto-increment: objectives-v1, objectives-v2, etc.
- Backup old versions

**Rationale**:
- Git already versions files
- Users control naming convention
- Single source of truth in git history
- Simpler implementation

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **ART** | Agile Release Train - collection of teams (e.g., "Data, Analytics and Digital") |
| **PI** | Program Increment / Release - planning period (e.g., "PI-4/25") |
| **Program Objective** | Organization-level goal for a PI (aligns multiple teams) |
| **Team Objective** | Team-level goal for a PI (supports one Program Objective) |
| **Epic** | Set of features delivering one Team Objective |
| **Feature** | User-facing deliverable (stored as Feature in TP, shown as epic in markdown) |
| **3-way Merge** | Comparing three versions: local, remote, and last-known-good (base) |
| **Source of Truth** | TargetProcess is the system of record; markdown is working copy |
| **Dry-run** | Preview changes without applying them |
| **Conflict Marker** | Git-style markers showing conflicting versions (<<<<<<, ======, >>>>>>>) |

---

## 12. Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-30 | 1.0 | Initial PRD with all design decisions | Engineering |
| TBD | 1.1 | Add implementation notes from Phase 1 | TBD |
| TBD | 2.0 | Post-MVP refinements | TBD |

---

**Next Steps**:
1. Review PRD for clarity and completeness
2. Identify any missing details or ambiguities
3. Iterate on design based on feedback
4. When approved, begin Phase 1 implementation
