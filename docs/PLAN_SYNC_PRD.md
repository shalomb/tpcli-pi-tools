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

**Proposed Solution**: `tpcli plan` subcommand with git-native workflows

The key insight: **Leverage git's battle-tested merge infrastructure** instead of building custom logic.
- `TP-PI-xxx` branch tracks TargetProcess state (managed by tpcli)
- User works in feature branches with normal git workflows
- `tpcli plan pull/push` handle the TP API ↔ git sync
- Conflicts resolved using git's familiar 3-way merge

### Goals

1. **Reduce friction**: Git-native workflow users already know
2. **Enable collaboration**: Git + markdown for team editing + PR reviews
3. **Prevent data loss**: Leverage git's merge-base algorithm
4. **Maintain source of truth**: TargetProcess remains canonical, git tracks changes
5. **Track changes**: Full git history + commits show who changed what
6. **Scale to ongoing sync**: Support multiple pull/push cycles per PI with conflict detection
7. **Simplify implementation**: Use git tools, not custom merge logic

### Out of Scope (for MVP)

- Capacity planning and resource allocation
- Story and task decomposition (those follow Team Objectives)
- Sprint planning and burndown
- Integration with external tools (Jira, GitHub, etc.)

---

## 2. User Workflows (Git-Native Model)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ TargetProcess API                                       │
│ (source of truth for PI planning)                       │
└──────────────────┬──────────────────────────────────────┘
                   │ tpcli plan pull/push
                   ↓
┌─────────────────────────────────────────────────────────┐
│ Git Remote (origin)                                     │
│ ├── TP-PI-4-25-platform-eco (tracking branch)          │
│ ├── TP-PI-4-25-cloud-enablement (tracking branch)      │
│ └── feature/* (user feature branches)                  │
└──────────────────┬──────────────────────────────────────┘
                   │ git fetch/push
                   ↓
┌─────────────────────────────────────────────────────────┐
│ Local Git Repository                                    │
│ ├── TP-PI-4-25-platform-eco (local tracking)           │
│ │   └── objectives.md (fresh from TP)                  │
│ └── feature/plan-refinement (user working branch)      │
│     └── objectives.md (with user edits)                │
└─────────────────────────────────────────────────────────┘
        User edits here ↑         User commits here ↑
```

### 2.1 Initialization Workflow

**User Goal**: "I want to set up a tracking branch for our team's PI plan"

```bash
# Initialize plan tracking for a specific release and team
tpcli plan init --release "PI-4/25" --team "Platform Eco"

# tpcli actions (hidden from user):
#   1. Fetch current state from TargetProcess API
#   2. Create local branch: TP-PI-4-25-platform-eco
#   3. Commit objectives.md with export from TP
#   4. Push to origin/TP-PI-4-25-platform-eco
#   5. Create feature branch: feature/plan-pi-4-25
#   6. Check out feature branch (user is here now)

# User sees:
# ✓ Initialized plan tracking for PI-4/25 Platform Eco
# ✓ Created tracking branch: TP-PI-4-25-platform-eco
# ✓ Checked out feature branch: feature/plan-pi-4-25
#
# You can now:
#   git add objectives.md
#   git commit -m "Add observability epic"
#   tpcli plan push    (when ready to sync to TP)
#   tpcli plan pull    (if TP was updated by others)
```

### 2.2 Edit Workflow

**User Goal**: "I want to edit our plan collaboratively using git"

```bash
# Normal git workflow - user is on feature/plan-pi-4-25
# Edit objectives.md locally
vim objectives.md

# Review what changed
git diff objectives.md

# Commit changes
git add objectives.md
git commit -m "Refine Platform Governance objective: increase effort 21→34"

# Make another change
git commit -m "Add observability epic for monitoring"

# View all commits since tracking branch
git log TP-PI-4-25-platform-eco..HEAD
#   * Add observability epic for monitoring
#   * Refine Platform Governance objective: increase effort 21→34

# All standard git workflows work:
# - Revert: git revert <commit>
# - Amend: git commit --amend
# - Squash: git rebase -i TP-PI-4-25-platform-eco
# - Branch: git checkout -b feature/alternative-plan
```

### 2.3 Pull from TargetProcess

**User Goal**: "Someone else updated the plan in TP, I want the latest changes"

```bash
# Pull latest from TargetProcess (may have changes from other team members)
tpcli plan pull

# tpcli actions (under the hood):
#   1. Switch to TP-PI-4-25-platform-eco branch
#   2. Fetch fresh state from TargetProcess API
#   3. Commit fresh export to TP-PI-4-25-platform-eco
#   4. Push to origin/TP-PI-4-25-platform-eco
#   5. Switch back to original branch (feature/plan-pi-4-25)
#   6. Rebase current branch onto updated tracking branch
#      (git might pause for conflict resolution if needed)

# Possible outcomes:

# Case 1: No conflicts (clean rebase)
# ✓ Rebased feature/plan-pi-4-25 onto TP-PI-4-25-platform-eco
# Your 2 commits replayed cleanly

# Case 2: Conflicts detected (both sides edited same objective)
# ✗ Conflict in objectives.md
# Fix conflicts in file and run: git rebase --continue

# View conflicts
cat objectives.md
# Shows standard git conflict markers:
# <<<<<<< HEAD (TP-PI-4-25-platform-eco - from TP)
# Effort: 20
# =======
# Effort: 34 (feature/plan-pi-4-25 - your edit)
# >>>>>>> your-commit-message

# Resolve manually, keep what you want
# Then mark resolved:
git add objectives.md
git rebase --continue

# Result: Your commits now based on latest TP state
```

### 2.4 Push to TargetProcess

**User Goal**: "Our planning is complete, push changes back to TargetProcess"

```bash
# Push changes to TargetProcess
tpcli plan push

# tpcli actions (under the hood):
#   1. Identify tracking branch: TP-PI-4-25-platform-eco
#   2. Calculate diff: what changed since last sync
#      git diff TP-PI-4-25-platform-eco..HEAD
#   3. For each change:
#      - Parse markdown to extract objective/epic updates
#      - Call TargetProcess API to create/update entities
#   4. Fetch fresh state from TP (others may have pushed too)
#   5. Update TP-PI-4-25-platform-eco with latest export
#   6. Push to origin/TP-PI-4-25-platform-eco
#   7. Notify user of sync status

# Possible outcomes:

# Case 1: Clean push (no changes in TP since last pull)
# ✓ Pushed 2 objectives updated, 1 epic created
# ✓ Updated tracking branch TP-PI-4-25-platform-eco
# ✓ Pushed to origin/TP-PI-4-25-platform-eco

# Your feature branch is still ahead with same commits:
# git log TP-PI-4-25-platform-eco..HEAD
#   * Add observability epic for monitoring
#   * Refine Platform Governance objective

# Case 2: Changes in TP since last pull
# ✗ Conflict: TP changed while you were pushing
# Run: tpcli plan pull
# Then: tpcli plan push
# (This retriggers the pull→merge→push cycle)
```

### 2.5 Ongoing Sync Across Multiple Cycles

**User Goal**: "We sync our plan regularly throughout the PI"

```bash
# Week 1: Initial setup
tpcli plan init --release "PI-4/25" --team "Platform Eco"
git commit -m "Initial plan for PI-4/25"
tpcli plan push

# Week 2: Refinement cycle
# - Edit objectives/epics
# - Several commits
# - Sync back to TP
git commit -m "Add new security epic"
git commit -m "Increase effort estimates based on risks"
tpcli plan pull          # Check for changes from others
# (resolve conflicts if any)
tpcli plan push          # Push our changes

# Week 3: More refinement
# - Someone else updated TP directly (compliance requirement)
tpcli plan pull          # Get latest
# (conflicts possible - resolve with git)
git commit -m "Merge compliance requirements with team plan"
tpcli plan push          # Sync back

# Week 4: Final push
# - All commits reviewed
# - Ready for execution
git log TP-PI-4-25-platform-eco..HEAD  # See all changes
tpcli plan pull          # Final sync
tpcli plan push          # Final push to TP

# Result: Full git history of all planning changes
# All reflected in TargetProcess as source of truth
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

## 4. Git-Native Merge Strategy

We leverage **git's built-in 3-way merge** rather than building custom logic. This provides:
- Battle-tested merge algorithm (`git merge-base`)
- Standard conflict markers that developers know
- Integration with existing tools (editors, `git mergetool`, etc.)
- Full merge history preserved in git

### 4.1 Merge Bases: The Three Versions

```
        TP-PI-4-25-platform-eco               (base)
              ↓
              ├─→ Feature Branch (local)       (yours)
              │      └─ Your edits & commits
              │
              └─→ Fresh TP State (remote)      (others' changes)
                     └─ TP API updated by others
```

Git's 3-way merge compares:
1. **Base** (TP-PI-4-25-platform-eco): Last known state when you started
2. **Local** (feature/plan-pi-4-25): Your commits and edits
3. **Remote** (TP-PI-4-25-platform-eco after `tpcli plan pull`): Latest from TP API

### 4.2 Conflict Scenarios and Git Behavior

| Scenario | Base | Local | Remote | Git Result |
|----------|------|-------|--------|-----------|
| User edits name only | "Old Name" | "New Name" | "Old Name" | ✓ Accept local (clean) |
| TP updates name only | "Old Name" | "Old Name" | "New Name" | ✓ Accept remote (clean) |
| Both edit name diff | "Old Name" | "New Name" | "Name v2" | ✗ **CONFLICT** |
| User edits effort | Effort: 13 | Effort: 21 | Effort: 13 | ✓ Accept local (clean) |
| TP updates status | Status: Pending | Status: Pending | Status: In Progress | ✓ Accept remote (clean) |
| Both change effort | Effort: 13 | Effort: 21 | Effort: 20 | ✗ **CONFLICT** |
| User adds epic | [no epic] | [epic A] | [no epic] | ✓ Create epic A (clean) |
| TP adds epic | [no epic] | [no epic] | [epic B] | ✓ Add epic B to markdown (clean) |
| Both add epics | [no epic] | [epic A] | [epic B] | ✓ Both added (clean, non-overlapping) |

### 4.3 Git Conflict Markers

When git detects a conflict during rebase, it injects standard markers:

```markdown
## Team Objective: Enable Data Transfer using MSK

**TP ID**: 2019099
**Status**: Pending
<<<<<<< HEAD (TP-PI-4-25-platform-eco - base/remote state from TP)
**Effort**: 20 points
**Owner**: John Doe
=======
**Effort**: 34 points
**Owner**: Sarah Chen
>>>>>>> feature/plan-pi-4-25 (your commits - local state)

### Description

(... no conflict in this field, clean merge)

### Epic: MSK Configuration

(... no conflict here either)

### Epic: New Observability Framework

(... user added this, TP doesn't have it, clean add)
```

**What the markers mean**:
- `<<<<<<< HEAD` = Base state from TP (what's on TP-PI-4-25-platform-eco)
- `=======` = Divider
- `>>>>>>> feature/plan-pi-4-25` = Your state (what you committed)

### 4.4 User Resolution Process

When `tpcli plan pull` encounters conflicts:

```bash
tpcli plan pull
# ✗ Conflict in objectives.md during rebase
# Fix manually and run: git rebase --continue

# User opens objectives.md and sees conflict markers
# Option 1: Keep local version (your edits)
# Option 2: Keep remote version (from TP)
# Option 3: Merge both (edit manually)

# Example: Keep your higher effort estimate
**Effort**: 34 points  # Keep this (your edit)
**Owner**: Sarah Chen

# Remove conflict markers
# Then continue rebase:
git add objectives.md
git rebase --continue

# Result: Your commits replayed on top of latest TP state
```

### 4.5 Epic (Feature) Handling

**Epics are matched by section title** (name-based, not ID):

| Scenario | Base | Local | Remote | Result |
|----------|------|-------|--------|--------|
| Both have "Epic: Monitoring" | [same] | [same] | [modified] | Merge fields using 3-way merge |
| User adds "Epic: Security" | [none] | [added] | [none] | ✓ Clean add |
| TP adds "Epic: Compliance" | [none] | [none] | [added] | ✓ Clean add |
| Both add different epics | [none] | [Epic A] | [Epic B] | ✓ Both exist, clean |
| User renames epic | "Old Name" | "New Name" | "Old Name" | ✓ Accept local |

**Edge case - Epic recreation**:
- If epic deleted from TP but you still have it: Treated as new epic (recreate)
- If epic deleted locally but exists in TP: Treated as remove (not added back)

### 4.6 What Git Does Automatically (No User Action Needed)

Git's merge-base algorithm automatically resolves:

1. **Non-overlapping changes**
   ```
   Base:  Effort: 13, Owner: John
   Local: Effort: 21, Owner: John     (you changed effort)
   Remote: Effort: 13, Owner: Sarah   (TP changed owner)

   Result: Effort: 21, Owner: Sarah   ✓ (both changes applied, no conflict)
   ```

2. **Same change on both sides**
   ```
   Base: Status: Pending
   Local: Status: In Progress
   Remote: Status: In Progress

   Result: Status: In Progress  ✓ (same result, no conflict)
   ```

3. **One side unchanged**
   ```
   Base: Description: "Old"
   Local: Description: "Old"           (you didn't change)
   Remote: Description: "New"          (TP changed it)

   Result: Description: "New"  ✓ (accept remote change, no conflict)
   ```

### 4.7 When Conflicts Occur

Conflicts only occur when **both sides changed the same field differently**:

```
Base: Effort: 13
Local: Effort: 21      (you estimate higher)
Remote: Effort: 20     (TP estimated 20)

Result: ✗ CONFLICT - Git can't decide which is right
        User must manually choose or merge
```

No custom conflict detection needed - git handles it!

---

## 5. Implementation Requirements

### 5.1 Go CLI Commands (tpcli foundation)

**Required additions to tpcli** (pkg/tpclient/client.go + cmd/):

```bash
# Create entity
tpcli create <EntityType> --data '<json>'
# Example: tpcli create TeamPIObjectives --data '{"Name":"...","Team":{"Id":123}}'

# Update entity
tpcli update <EntityType> <id> --data '<json>'
# Example: tpcli update TeamPIObjectives 2019099 --data '{"Effort":21}'

# Implementation notes:
# - Use existing pkg/tpclient/client.go doRequest() for POST
# - Return JSON response with created/updated entity
# - Support --verbose flag for debugging
# - Proper error handling for validation failures
# - No custom merge logic needed (git handles it)
```

### 5.2 Python API Client Extensions

**New methods in `tpcli_pi/core/api_client.py`**:

```python
# Create operations (write to TP API)
def create_team_objective(name, team_id, release_id, **kwargs) -> TeamPIObjective
def create_feature(name, team_id, release_id, **kwargs) -> Feature
def create_program_objective(name, art_id, release_id, **kwargs) -> ProgramPIObjective

# Update operations (write to TP API)
def update_team_objective(objective_id, **kwargs) -> TeamPIObjective
def update_feature(feature_id, **kwargs) -> Feature
def update_program_objective(objective_id, **kwargs) -> ProgramPIObjective

# Helpers for detecting what changed
def get_team_pi_objectives_at_timestamp(team_id, release_id) -> list[TeamPIObjective]
  # Fetches current state from TP for merge base detection
```

**Subprocess wrappers** (using tpcli create/update):
```python
def _run_tpcli_create(entity_type: str, data: dict) -> dict
def _run_tpcli_update(entity_type: str, entity_id: int, data: dict) -> dict
```

### 5.3 Plan Sync Module

**New module**: `tpcli_pi/sync/`

**Key components**:
- `markdown_parser.py` - Parse/generate markdown with YAML frontmatter
  - `parse_frontmatter(content)` - Extract YAML metadata
  - `generate_markdown(objectives, program_objectives)` - Create markdown from TP data
  - `extract_objectives_from_markdown(content)` - Parse user edits

- `markdown_diff.py` - Detect changes between versions
  - `parse_markdown_diff(diff)` - Parse `git diff` output
  - `extract_changes(old_md, new_md)` - What was created/updated/deleted

- `validator.py` - Validate before API calls
  - `validate_objective(data)` - Check required fields
  - `validate_epic(data)` - Check epic fields

**New CLI**: `tpcli_pi/cli/plan.py`

```bash
tpcli plan init --release <name> --team <name>
  # Create TP-PI-xxx-xxx tracking branch, feature branch, initial export

tpcli plan pull
  # Fetch latest from TP, update tracking branch, rebase current branch

tpcli plan push
  # Parse changes, apply to TP API, update tracking branch

tpcli plan status
  # Show tracking branch status, commits ahead, etc.

tpcli plan validate --file <path>
  # Check markdown structure and required fields
```

### 5.4 Git Integration (subprocess calls)

**tpcli will call git under the hood**:

```python
# Key git operations tpcli will execute:
git checkout -b <branch>
git switch <branch>
git add <file>
git commit -m <message>
git push origin <branch>
git diff <base>..<head>
git log <base>..<head>
git rebase <branch>
git status
git reset --hard

# tpcli handles all git operations internally
# User never needs to run git commands except:
# - git commit (for their edits)
# - git add (before commit)
# - git rebase --continue (if conflicts during pull)
```

### 5.5 No Custom Merge Logic Needed

**What we're NOT building**:
- ✗ Custom 3-way merge algorithm (git provides this)
- ✗ Conflict detection (git provides this via rebase)
- ✗ Conflict marker generation (git provides this)
- ✗ Custom conflict resolution UI (use git's standard markers)

**What git handles automatically**:
- ✓ Merge-base calculation
- ✓ Non-conflicting change detection
- ✓ Automatic merge of non-overlapping changes
- ✓ Conflict marker injection
- ✓ Rebase orchestration

This simplifies the codebase significantly!

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

## 7. Implementation Phases (Simplified via Git-Native)

### Phase 1: Go CLI Foundation (3-4 days)
- [ ] Implement `tpcli create <EntityType> --data '<json>'`
  - Post to TargetProcess API
  - Return created entity JSON
  - Error handling for validation
- [ ] Implement `tpcli update <EntityType> <id> --data '<json>'`
  - Post to TargetProcess API
  - Return updated entity JSON
  - Error handling
- [ ] Manual testing with curl equivalents
- [ ] Verify against real TargetProcess API

### Phase 2: Python Wrapper (2-3 days)
- [ ] Add `_run_tpcli_create()` subprocess wrapper
- [ ] Add `_run_tpcli_update()` subprocess wrapper
- [ ] Implement high-level create methods:
  - `create_team_objective(name, team_id, release_id, **kwargs)`
  - `create_feature(name, team_id, release_id, **kwargs)`
  - `create_program_objective(name, art_id, release_id, **kwargs)`
- [ ] Implement high-level update methods
  - `update_team_objective(objective_id, **kwargs)`
  - `update_feature(feature_id, **kwargs)`
  - `update_program_objective(objective_id, **kwargs)`
- [ ] Unit tests for API wrappers

### Phase 3: Markdown Parsing & Generation (3-4 days)
- [ ] YAML frontmatter parsing (using existing pyyaml)
- [ ] Objective/epic extraction from markdown
  - Parse H2 sections as objectives
  - Parse H3 subsections as epics
  - Extract metadata fields
- [ ] Markdown generation from TP data
  - Format objectives with metadata
  - Format epics as subsections
  - Include program objectives for reference
- [ ] Test with various markdown formats

### Phase 4: Git Integration & Plan Commands (4-5 days)
- [ ] Implement `tpcli plan init --release <name> --team <name>`
  - Export from TP
  - Create tracking branch
  - Create feature branch
  - Git operations under the hood
- [ ] Implement `tpcli plan pull`
  - Fetch from TP API
  - Update tracking branch
  - Git rebase (conflicts handled by user + git)
  - Proactive fetch before any operation
- [ ] Implement `tpcli plan push`
  - Parse `git diff` against tracking branch
  - Apply changes to TP API
  - Update tracking branch with fresh export
  - Push to origin
- [ ] Implement `tpcli plan status`
  - Show branch status
  - Show commits ahead
- [ ] Implement `tpcli plan validate`
  - Check markdown structure

### Phase 5: Testing (4-5 days)
- [ ] BDD tests with behave:
  - Init workflow
  - Edit and push
  - Pull and conflict resolution
  - Multiple cycles
- [ ] Unit tests:
  - Markdown parser
  - Markdown diff parser
  - Validator
  - API client wrappers
- [ ] Integration tests:
  - Full export → edit → import cycle
  - Conflict scenarios
  - Concurrent edits

### Phase 6: Documentation & UX Polish (2-3 days)
- [ ] User guide for plan sync workflow
- [ ] Example markdown files
- [ ] Troubleshooting guide (especially conflicts)
- [ ] API documentation
- [ ] Help text in `tpcli help` (see Section 9 for UX refinement note)
- [ ] Architecture documentation

**Total Estimated Effort**: 18-24 days (3-4 weeks)

**Key Simplification**: No custom merge engine → saves ~5-7 days of development

---

## 8. Success Criteria

### MVP (Minimal Viable Product)

**Commands working**:
- [ ] `tpcli plan init --release <name> --team <name>` creates tracking + feature branches
- [ ] `tpcli plan pull` fetches latest from TP and rebases (with conflict handling)
- [ ] `tpcli plan push` applies changes to TP and updates tracking branch
- [ ] `tpcli plan status` shows branch and commit status
- [ ] `tpcli plan validate --file <path>` checks markdown structure

**Data handling**:
- [ ] Objectives exported to markdown with H2 sections
- [ ] Epics exported as H3 subsections
- [ ] YAML frontmatter preserves TP IDs and metadata
- [ ] All TargetProcess IDs preserved for round-trip sync
- [ ] Program objectives shown for reference/alignment
- [ ] Team objectives linked to Program objectives (one-to-one)

**Conflict handling**:
- [ ] Git's native merge handles non-conflicting changes automatically
- [ ] Standard git conflict markers appear on conflicting fields
- [ ] User resolves via normal git workflow (`git add`, `git rebase --continue`)
- [ ] No custom conflict detection needed (git provides this)

**Sync integrity**:
- [ ] No data loss or corruption in export → edit → push cycle
- [ ] Multiple sync cycles preserve all changes
- [ ] Git history shows all planning changes
- [ ] TargetProcess remains source of truth

**Error handling**:
- [ ] Helpful error messages for missing fields
- [ ] Clear guidance on conflicts (e.g., "Fix conflicts in objectives.md and run: git rebase --continue")
- [ ] Validation before API calls

### Tested & Verified

- [ ] Full export → edit → push cycle works end-to-end
- [ ] Pull detects TP changes and rebases correctly
- [ ] Git conflicts resolved using standard git tools
- [ ] Multiple sync cycles don't cause data loss
- [ ] All BDD scenarios passing
- [ ] Manual testing with real TargetProcess data

### Documented

- [ ] User guide for init → edit → push workflow
- [ ] Example markdown files showing expected format
- [ ] Troubleshooting guide (especially for conflicts)
- [ ] Branch naming conventions documented
- [ ] How to resolve git conflicts in the plan file
- [ ] Help text in `tpcli help` (polish tracked separately, see Section 9)
- [ ] Architecture decisions recorded (this document)

---

## 9. Open Questions & Future Considerations

### Design Decisions (Finalized)

1. **Commands**: Use `tpcli plan` as subcommand (not separate tool) ✓
2. **Merge strategy**: Git-native (leverage git's 3-way merge) ✓
3. **Conflict resolution**: Git-style markers + manual file editing ✓
4. **Base version**: Always fetch fresh from TP (not stored in file) ✓
5. **File versioning**: Single file per team+release (git manages history) ✓
6. **Remote**: Real git remote (team-shareable, not local-only) ✓
7. **Pull strategy**: Proactive (detect changes automatically) ✓
8. **Permissions**: Lenient (let TP API validate) ✓

### Help Text & UX Polish (Tracked Separately)

**Note**: Help text design for `tpcli help` will be polished after feature is complete and working.

Current approach: Minimal help text in Phase 6
Future work (post-MVP):
- [ ] Add workflow diagrams to `tpcli help`
- [ ] Add examples to `tpcli plan --help`
- [ ] Create quick-start guide
- [ ] Polish help text for discoverability

This ensures we focus on core functionality first, then refine UX based on actual usage patterns.

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

## 10. Jira Integration Considerations

### Current State of Jira Integration in TargetProcess

**Investigation Results** (Epic #2018883 "PI-4/25 DevOps Enhancements"):

TargetProcess maintains bidirectional sync with Jira at the Feature level:

1. **Jira Link Mechanism**:
   - Features in TP have Jira Key field (e.g., `DAD-2652`)
   - Also maintains: Jira Project, Jira Priority, Jira Issue Type
   - Bidirectional sync already exists (TP ↔ Jira)

2. **What TP Exposes from Jira**:
   - Feature metadata: Jira Key, Jira Project, Priority, Issue Type
   - Acceptance Criteria: Stored as CustomField (RichText/HTML)
   - Status synchronization: TP EntityState synced with Jira Issue status
   - Dates: Jira Start Date, Jira Due Date (CustomFields)
   - Link: TemplatedURL pointing back to Jira

3. **What TP Does NOT Expose**:
   - **Story decomposition**: No API field for linked Jira stories/sub-tasks
   - **Story details**: Can't fetch Jira story acceptance criteria from TP API
   - **Full decomposition**: Jira has Epic → Stories → Tasks tree, TP only shows top-level Feature
   - **Story status tracking**: Individual story status not reflected in TP
   - **Cross-Epic dependencies**: Jira cross-issue links not exposed in TP API

### Design Implications for Plan Sync

#### Problem: Missing Story Decomposition

Users want to see full Jira decomposition in the markdown plan for context:
- Stories under an epic
- Story acceptance criteria
- Story status and owner
- Dependencies between stories

But TargetProcess API doesn't expose this information.

#### Options Considered

**Option A: Include Jira Stories (Requires Direct Jira API Access)**
- Pros:
  - Full context for planning
  - Shows realistic scope
  - Easy to understand story relationships
- Cons:
  - Requires Jira API credentials (separate from TP)
  - Adds complexity: sync 3 systems (Git ← TP ← Jira)
  - Conflict resolution becomes harder (which system wins if Jira and TP disagree?)
  - Implementation effort: ~3-5 days
  - Maintenance burden: More integrations = more failure points

**Option B: Read-Only Jira Links in Markdown (MVP Approach)**
- Pros:
  - Works with existing TP API
  - Clear signal that story data is external
  - Minimal implementation effort (~2 hours)
  - Users can click link to view stories in Jira
  - Doesn't introduce new system dependencies
- Cons:
  - Users must switch to Jira to view story decomposition
  - No decomposition visible in markdown plan
  - Less convenient for planning
  - Users still have to manually connect stories to epics

**Option C: Deferred - Phase B Enhancement**
- Pros:
  - Get MVP out faster (no Jira API complexity)
  - Gather user feedback on what story data is actually needed
  - Can be added later without breaking existing workflows
- Cons:
  - MVP doesn't show story decomposition
  - Users will ask for this feature immediately

#### Recommendation

**For MVP (Phase A)**: Use **Option B** - Read-Only Jira Links
- Display Feature Jira Key in markdown as clickable link
- Include acceptance criteria from TP CustomField
- Include note in Plan markdown: "View detailed story decomposition in [Jira DAD-2652](https://jira.takeda.com/...)"

**Example Markdown Structure**:
```markdown
### Epic: Semantic Versioning & CI/CD
- **TP ID**: 2018883
- **Jira Epic**: [DAD-2652](https://jira.takeda.com/browse/DAD-2652)
- **Owner**: Venkatesh Ravi
- **Status**: Analyzing
- **Effort**: 21 pts
- **Acceptance Criteria**:
  - CPU and memory limits configured at pod level
  - Alerting implemented for backend pods
  - Semantic versioning for Docker images
  - Unified branching strategy established

For detailed story decomposition, see [Jira Epic DAD-2652](link)
```

**For Phase B (Post-MVP)**: Direct Jira API Integration
- Fetch stories directly from Jira API
- Add H4 subsections for read-only stories
- Track story status and sync back to TP if needed
- Handle credential management (Jira token in tpcli config)

### Implementation Notes for MVP

1. **No Code Changes Required** for Jira link inclusion:
   - TP API already provides Jira Key in CustomFields
   - Markdown rendering just adds hyperlinks

2. **Accept Criteria Display**:
   - Parse HTML from CustomField → plain text markdown
   - Strip HTML tags, convert entities to Unicode
   - Keep formatting (lists, paragraphs)

3. **Future Consideration**:
   - If users frequently ask "where are the stories?", implement Phase B
   - Gather metrics on how often users click Jira links
   - Survey teams on what story info they need most

### Handling Changes on Pull

When `tpcli plan pull` fetches updated data from TP:

1. **Detected Changes**:
   - New Jira stories (query TP, not Jira directly)
   - Story status changed in Jira (reflected in TP)
   - Acceptance criteria updated (from CustomFields)

2. **Conflict Handling**:
   - If user edited story section, git 3-way merge handles it
   - If Jira story removed, TP data won't include it
   - If new story added in Jira, won't appear in plan unless user manually updates

3. **User Workflow**:
   - Team edits and refines epics in markdown
   - Stories stay in Jira (users edit there directly)
   - `tpcli plan pull` updates acceptance criteria from TP
   - `tpcli plan push` only updates epics/objectives in TP

### Success Criteria for MVP

- ✅ Jira Epic Key links are displayed in markdown
- ✅ Acceptance criteria from TP are shown
- ✅ Users can click Jira link to view decomposition
- ✅ No dependency on Jira API credentials
- ✅ Pull/push works without Jira integration
- ✅ Plan remains readable and manageable in markdown

---

## 11. State Management: Handling TP-Jira Bidirectional Sync

### The Core Issue

When creating an Epic in TargetProcess:
1. TP automatically creates corresponding Jira Epic
2. TP monitors Jira Epic for all changes (stories, AC, status, etc.)
3. TP syncs those changes back to TP state

**This means: TargetProcess state is NOT stable** - it's being mutated by Jira activity in the background.

#### Timeline Example
```
T0:    tpcli plan pull
       TP State: Epic "Platform Governance" [AC: "Configure limits"]
       Git: TP-PI-xxx branch @ T0
       Feature branch: User ready to edit

T0+X:  Meanwhile in Jira:
       Team adds Story D, updates Story A AC
       ↓
       TP syncs changes
       ↓
       TP State: Epic "Platform Governance" [AC: "Set Pod limits for performance"]

T0+2X: User edits markdown locally

T0+3X: tpcli plan push
       Now must reconcile:
       - Base: TP @ T0 (our anchor point)
       - User edits: Feature branch changes
       - Current: TP @ T0+3X (includes Jira updates)
```

### State Management Models

#### **Model 1: Git-Native 3-Way Merge (RECOMMENDED for MVP)**

```
TP-PI-xxx (tracking branch) ← Fresh TP state on each pull
         ↓ (merge-base)
feature/plan-xxx (user working branch)
         ↓ (3-way merge)
Resolved markdown (conflicts marked if both sides changed AC)
         ↓ (push)
Apply changes to TP
```

**How conflicts are handled:**
- If only Jira updated AC: Accept Jira's version (no conflict)
- If only user updated AC: Accept user's version (no conflict)
- If both Jira AND user updated AC: CONFLICT (user resolves)

**Examples:**

Case 1 - No conflict (Jira only):
```
Base:    Epic AC: "Configure limits"
User:    Epic AC: "Configure limits" (unchanged), adds Epic C
Current: Epic AC: "Configure limits and monitoring" (Jira updated)

Result: Merged ✅ (accept Jira's AC, add user's Epic C)
```

Case 2 - Conflict (both touched AC):
```
Base:    Epic AC: "Configure limits"
User:    Epic AC: "Configure limits and monitor" (user edited)
Current: Epic AC: "Set Pod-level constraints" (Jira updated)

Result: CONFLICT ❌ (need human decision)
```

**Pros:**
- Leverages git's battle-tested algorithm
- Clear audit trail (git commits show who did what)
- Handles accidental conflicts correctly
- No new system dependencies

**Cons:**
- Frequent conflicts if teams actively using both Jira and plan
- Users need to understand git conflict resolution
- Doesn't show "reason for change" (Jira vs user vs tpcli push)

**Success depends on:**
- How chatty is TP↔Jira sync? (Real-time? Batch? Polling?)
- Do teams edit same sections in both Jira and plan? (If yes, conflicts; if no, clean)
- User comfort with conflict markers

---

#### **Model 2: Hybrid (TP Epics + Jira Stories Direct)**

Query Jira directly in addition to TP:

```
Pull sequence:
1. Fetch Epic/Objective from TP (source of truth)
2. Fetch Stories directly from Jira (fresher data)
3. Build markdown with stories as read-only H4 sections
4. Apply 3-way merge against base (TP state @ last pull)
```

**Pros:**
- Stories always real-time from Jira
- Clear separation: editable (H2-H3) vs read-only (H4)
- Users see true scope in one markdown file

**Cons:**
- Requires Jira API credentials (separate from TP)
- More complex implementation
- Risk of TP/Jira disagreement on story status
- ~3-5 additional days implementation

**When to use:**
- MVP shows too many conflicts from Jira sync
- Users want full decomposition in markdown
- Team actively editing both systems simultaneously

---

#### **Model 3: Batch/Scheduled Sync**

If TP sync latency is known and batched, we could:
- Pull, get fresh TP state
- Extract "last change timestamp" from TP
- Detect if TP was updated due to Jira or user push
- Warn user: "TP changed due to Jira activity since your last pull"

**Pros:**
- Can explain "why TP changed"
- Users can make informed decision to rebase

**Cons:**
- Requires TP to expose "change reason" or timestamps
- Might need custom TP query

---

### Recommendation for MVP

**Use Model 1 (Git-Native 3-Way Merge)** with explicit assumptions:

#### MVP Assumptions
1. **Jira sync is relatively infrequent** - teams don't constantly add stories
2. **User awareness** - teams understand markdown plan ↔ Jira are linked
3. **Conflict resolution acceptable** - git conflict markers are fine
4. **Clear workflow** - document that teams can:
   - Edit epics/objectives in plan (git)
   - Edit stories in Jira (git doesn't know about this)
   - `tpcli plan pull` frequently to stay in sync
   - Resolve conflicts when they appear

#### MVP Workflow Documentation
```markdown
## Plan Editing Workflow with Active Jira Decomposition

### Your Responsibilities
- **Edit Plan**: Markdown files (epics, objectives, effort)
- **Edit Stories**: Jira (stories, tasks, AC) - NOT in markdown

### Jira Team's Responsibilities
- Edit stories in Jira (add, remove, update)
- This will be visible in TP and might cause merge conflicts

### When to Pull
- Before starting your edit session: `tpcli plan pull`
- After team finishes Jira updates: `tpcli plan pull`
- When you see unexpected changes: `tpcli plan pull`

### Conflict Resolution
When you see `<<<<<<< HEAD ... ======= ... >>>>>>>` markers:
1. Identify the section (usually Acceptance Criteria or epic changes)
2. Understand: Your changes OR Jira team's updates?
3. Decide: Keep both, keep one, or merge
4. Remove conflict markers
5. Commit: `git add . && git commit -m "Resolve merge conflict"`

This is NORMAL - it means nothing was lost, just needs human decision.
```

### Decision: Model 1 APPROVED for MVP

**Sync Behavior Confirmed**:
- TP ↔ Jira sync latency: **Order of seconds** (effectively real-time)
- Sync scope: **Fast enough** that we don't need to query Jira directly
- Source of truth: **TargetProcess** (not Jira)

**Implication**: When we pull from TP, we get the latest state including any Jira syncs that happened in the background. No need to query Jira directly or worry about disagreement between systems.

**Design Decision**:
- Use Model 1 (Git-Native 3-Way Merge) as planned
- Pull from TP only (TP is canonical)
- Accept that merge conflicts may occur when Jira + user both edit, but they'll be correct conflicts
- Document the workflow clearly (edit epics in plan, stories in Jira)

**This unblocks Phase 1 implementation** - no additional validation needed.

### Phase B Consideration

If MVP shows that conflicts are too frequent or confusing, Phase B should:
1. Implement Model 2 (Hybrid - Jira stories direct)
2. Query Jira API in addition to TP
3. Show stories as read-only H4 sections
4. Reduce conflicts by having fresher baseline

---

## 12. Architecture Decisions

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

## 13. Glossary

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

## 14. Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-30 | 1.0 | Initial PRD with all design decisions | Engineering |
| 2025-11-30 | 1.1 | Add Jira Integration Considerations section (Epic #2018883 analysis) | Engineering |
| 2025-11-30 | 1.2 | Add State Management section addressing TP-Jira bidirectional sync | Engineering |
| TBD | 1.3 | Add implementation notes from Phase 1 | TBD |
| TBD | 2.0 | Post-MVP refinements based on real usage | TBD |

---

**Next Steps**:
1. Review PRD for clarity and completeness
2. Identify any missing details or ambiguities
3. Iterate on design based on feedback
4. When approved, begin Phase 1 implementation
