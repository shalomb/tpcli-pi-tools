# Plan Sync Feature - Phase 1 Implementation

## Development Protocol

**See**: `docs/PLAN_SYNC_PRD.md` for complete design, architecture decisions, and detailed rationale.

**Quick Reference**:
- PRD Section 10: Jira Integration strategy (read-only links in MVP)
- PRD Section 11: State Management (Model 1: git-native 3-way merge APPROVED)
- PRD Section 9: Phase 1-4 breakdown

**Key Decision**: TargetProcess is source of truth. Pull from TP only (TP ↔ Jira syncs automatically, order of seconds).

## Phase 1 Scope (18-24 hours)

Implement core bidirectional sync: pull objectives/epics from TP, edit in markdown+git, push changes back.

```
Phase 1 Goal: tpcli plan pull → edit markdown → tpcli plan push workflow
```

### 1.1 Go CLI: Create/Update Operations

**Files**: `cmd/plan.go`, `pkg/tpclient/client.go`

**Tasks**:
- [ ] Add `tpcli create <EntityType> --data '<json>'` command
  - Parse JSON data parameter
  - Call TP API: `POST /api/v1/{EntityType}`
  - Return created entity with ID
  - Handle errors (validation, auth, etc.)

- [ ] Add `tpcli update <EntityType> <id> --data '<json>'` command
  - Parse JSON data parameter
  - Call TP API: `PUT /api/v1/{EntityType}/{id}`
  - Return updated entity
  - Handle errors (not found, validation, etc.)

- [ ] Add tests for create/update operations
  - Mock TP API responses
  - Test error handling
  - Test JSON parsing

**Reference**: Leverage existing `List()` method in `pkg/tpclient/client.go` as pattern

**Success Criteria**:
- ✅ `tpcli create TeamPIObjective --data '{...}'` creates objective in TP
- ✅ `tpcli update TeamPIObjective 12345 --data '{...}'` updates objective
- ✅ Both return JSON response with updated entity data
- ✅ Errors handled gracefully with clear messages

---

### 1.2 Python API Client: Wrapper Methods

**Files**: `tpcli_pi/core/api_client.py`

**Tasks**:
- [ ] Add `create_team_objective(name, team_id, release_id, **kwargs)` method
  - Prepare JSON payload (name, team_id, release_id, and any optional fields)
  - Call subprocess: `tpcli create TeamPIObjective --data '...'`
  - Parse JSON response
  - Return typed `TeamPIObjective` object
  - Add to cache

- [ ] Add `update_team_objective(objective_id, **kwargs)` method
  - Prepare JSON payload with updated fields
  - Call subprocess: `tpcli update TeamPIObjective {id} --data '...'`
  - Parse JSON response
  - Return typed `TeamPIObjective` object
  - Update cache

- [ ] Add `create_feature(name, parent_epic_id, **kwargs)` method
  - Similar pattern to objectives
  - Call `tpcli create Feature --data '...'`
  - Return typed `Feature` object

- [ ] Add `update_feature(feature_id, **kwargs)` method
  - Similar pattern to objectives
  - Call `tpcli update Feature {id} --data '...'`
  - Return typed `Feature` object

- [ ] Unit tests for wrapper methods
  - Mock subprocess responses
  - Test payload construction
  - Test response parsing
  - Test cache updates

**Reference**: Study existing `_run_tpcli()` and `_parse_*()` methods for pattern

**Success Criteria**:
- ✅ Python client can create objectives via TP API
- ✅ Python client can update objectives via TP API
- ✅ Responses parsed and cached correctly
- ✅ No manual API curl needed (all via Python client)

---

### 1.3 Markdown Generation: Export TP to Markdown

**Files**: `tpcli_pi/core/markdown_generator.py` (NEW)

**Data Model**:
```python
class MarkdownPlan:
    """Generated markdown plan with YAML frontmatter"""
    frontmatter: dict  # {tp_id, release, team, last_sync, ...}
    objectives: list[str]  # H2 sections: "## Objective: ..."
    epics: list[str]  # H3 sections: "### Epic: ..."
    content: str  # Full markdown text
```

**Tasks**:
- [ ] Create `MarkdownGenerator` class with export method:
  ```python
  def export_team_plan(team_id: int, release_id: int) -> MarkdownPlan:
      # Fetch from TP API via client
      # Generate markdown structure
      # Return MarkdownPlan object
  ```

- [ ] Generate YAML frontmatter with metadata:
  ```yaml
  ---
  tp_team_id: 1935991
  tp_release_id: 1942235
  tp_release_name: "PI-4/25"
  tp_last_sync: 2025-11-30T10:00:00Z
  tp_last_sync_hash: "abc123def456"
  ---
  ```

- [ ] Generate markdown structure:
  ```markdown
  # Team PI Plan: [Team Name] / [Release Name]

  ## Objective: [Objective Name]
  - **TP ID**: 12345
  - **Status**: Pending/In Progress/Done
  - **Owner**: Name
  - **Effort**: 34 pts

  ### Epic: [Feature Name]
  - **TP ID**: 2018883
  - **Jira Key**: [DAD-2652](https://jira.takeda.com/browse/DAD-2652)
  - **Effort**: 21 pts
  - **Acceptance Criteria**:
    - Item 1
    - Item 2
  ```

- [ ] Parse and clean Jira AC from HTML CustomField:
  - Extract "Acceptance Criteria" CustomField from TP response
  - Strip HTML tags
  - Convert entities (&#44; → ,, &nbsp; → space)
  - Format as markdown list

- [ ] Unit tests for markdown generation:
  - Test frontmatter generation
  - Test objective/epic section generation
  - Test HTML cleanup of AC
  - Test edge cases (no AC, missing fields, etc.)

**Reference**: See PRD Section 10 (Jira Integration) for AC field structure

**Success Criteria**:
- ✅ `MarkdownGenerator.export_team_plan()` returns valid markdown
- ✅ Frontmatter includes all required metadata
- ✅ Objectives and epics formatted clearly
- ✅ Acceptance criteria properly cleaned/formatted
- ✅ Jira keys as clickable links [DAD-2652](...)

---

### 1.4 Git Integration: Pull/Push with 3-Way Merge

**Files**: `tpcli_pi/core/git_sync.py` (NEW), `tpcli_pi/cli/plan.py` (NEW)

**Commands**:
```bash
tpcli plan init --team "Platform Eco" --release "PI-4/25"
  # Creates TP-PI-4-25-platform-eco tracking branch
  # Creates feature/plan-pi-4-25 working branch
  # Checks out feature branch for user

tpcli plan pull
  # Fetches latest from TP
  # Updates TP-PI-4-25-platform-eco branch
  # Merges into feature branch (3-way merge)
  # Handles conflicts with git merge markers

tpcli plan push
  # Validates markdown syntax
  # Parses changes (new epics, updated objectives, etc.)
  # Applies changes to TP via create/update API
  # Commits to TP-PI-4-25-platform-eco tracking branch
```

**Tasks**:
- [ ] Create `GitSync` class:
  ```python
  class GitSync:
      def init_plan(team: str, release: str) -> str:
          # Create TP-PI-4-25-platform-eco branch
          # Create feature/plan-pi-4-25 branch
          # Checkout feature branch
          # Return branch name

      def pull_plan() -> (bool, list[str]):
          # Fetch latest from TP
          # Update TP-PI-4-25-xxx tracking branch
          # Merge into current branch (3-way)
          # Return (success, conflicts list if any)

      def push_plan() -> bool:
          # Parse markdown changes
          # Apply to TP (create/update operations)
          # Commit to tracking branch
          # Return success
  ```

- [ ] Implement `plan init` command:
  - Read config for current team/release (if available)
  - Create local git branches
  - Generate initial markdown via MarkdownGenerator
  - Commit to tracking branch

- [ ] Implement `plan pull` command:
  - Fetch fresh TP state
  - Check current git branch
  - Verify we're on feature branch (error if on tracking branch)
  - Run: `git merge TP-PI-4-25-xxx` (3-way merge)
  - Handle conflicts (show merge markers)

- [ ] Implement `plan push` command:
  - Parse markdown (extract objectives/epics)
  - Diff against last-known state (from tracking branch)
  - Generate create/update payloads
  - Call Python API client methods (Section 1.2)
  - Commit to tracking branch with clear message
  - Show summary of applied changes

- [ ] Git-native conflict handling:
  - Use git's built-in merge conflict markers
  - User edits markdown to resolve
  - `git add .` + `git commit` to complete merge
  - No custom merge UI (rely on existing tools)

- [ ] Unit tests:
  - Mock TP API responses
  - Test branch creation/management
  - Test markdown parsing
  - Test conflict detection
  - Test change application

**Reference**:
- PRD Section 2: User workflows
- PRD Section 11: State management (Model 1 git-native)

**Success Criteria**:
- ✅ `tpcli plan init` creates branches and initial markdown
- ✅ `tpcli plan pull` merges fresh TP state (3-way)
- ✅ `tpcli plan push` applies changes to TP
- ✅ Conflicts shown as git merge markers
- ✅ Clear error messages for edge cases

---

### 1.5 Testing: BDD Scenarios for Core Workflow

**Files**: `tests/bdd/plan_sync.feature`, `tests/bdd/steps/plan_steps.py`

**Scenario 1: Initialize Plan**
```gherkin
Given a team "Platform Eco" exists in TargetProcess
And a release "PI-4/25" exists
When user runs: tpcli plan init --team "Platform Eco" --release "PI-4/25"
Then branch "TP-PI-4-25-platform-eco" is created
And branch "feature/plan-pi-4-25" is created
And user is on branch "feature/plan-pi-4-25"
And file "objectives.md" exists with frontmatter
```

**Scenario 2: Pull Changes from TP**
```gherkin
Given user is on branch "feature/plan-pi-4-25"
And TP has 2 objectives (effort 34, 21)
When user runs: tpcli plan pull
Then "TP-PI-4-25-platform-eco" branch updated
And objectives.md merged (no conflicts)
And git log shows merge commit
```

**Scenario 3: Edit and Push Changes**
```gherkin
Given user has fresh objectives.md
When user edits: change "API Performance" effort 34 → 40
And user commits: git add . && git commit -m "..."
And user runs: tpcli plan push
Then TP objective updated with effort 40
And TP-PI-4-25-platform-eco branch updated
And git log shows push commit
```

**Scenario 4: Handle Merge Conflict**
```gherkin
Given user is on branch "feature/plan-pi-4-25" with local edits
And TP was updated by another user (different objective)
When user runs: tpcli plan pull
Then merge attempt includes both changes
And git status shows merge in progress
And objectives.md shows conflict markers if both edited same objective
When user resolves conflict manually
And user commits: git add . && git commit -m "Resolve merge..."
Then merge completes successfully
```

**Scenario 5: List Available Plans**
```gherkin
When user runs: tpcli plan list
Then shows available team/release combinations
And indicates which have active tracking branches
```

**Tasks**:
- [ ] Write BDD feature file with 5+ scenarios
- [ ] Implement step definitions (Given/When/Then)
- [ ] Mock TP API for testing
- [ ] Test with actual git operations (temp repo)
- [ ] Validate end-to-end workflow

**Reference**:
- PRD Section 2: User workflows (init → edit → pull → push)
- PRD Section 11: State management (merge conflicts expected)

**Success Criteria**:
- ✅ All 5+ BDD scenarios passing
- ✅ Tests validate core workflow end-to-end
- ✅ Conflict scenarios handled correctly
- ✅ Clear error messages in edge cases

---

## Implementation Order

**Week 1: Foundation** (Days 1-3)
1. Go CLI create/update (1.1)
2. Python API wrapper (1.2)
3. Markdown generation (1.3)

**Week 2: Integration** (Days 4-5)
4. Git integration (1.4)
5. BDD tests (1.5)

**Validation**: All tests green, core workflow (init → edit → pull → push) works end-to-end

---

## Key Files & References

### Core Implementation
- `pkg/tpclient/client.go` - Add Create/Update methods
- `tpcli_pi/core/api_client.py` - Add Python wrapper methods
- `tpcli_pi/core/markdown_generator.py` (NEW) - Generate markdown from TP
- `tpcli_pi/core/git_sync.py` (NEW) - Git integration
- `tpcli_pi/cli/plan.py` (NEW) - CLI commands

### Testing
- `tests/unit/test_api_client.py` - Unit tests for Python wrapper
- `tests/unit/test_markdown_generator.py` - Unit tests for markdown gen
- `tests/unit/test_git_sync.py` - Unit tests for git ops
- `tests/bdd/plan_sync.feature` - BDD scenarios
- `tests/bdd/steps/plan_steps.py` - BDD step definitions

### Data Models
- `tpcli_pi/models/entities.py` - Already has TeamPIObjective, Feature, etc.
- Add to markdown_generator.py: `MarkdownPlan` class

### Configuration
- `~/.config/tpcli/config.yaml` - Already supports default-team, default-art
- Could add: `default-release` for convenience

### Documentation
- `docs/PLAN_SYNC_PRD.md` - Complete design (see sections 1-12)
- `docs/DEVELOPMENT.md` (optional) - Development workflow during Phase 1

---

## Phase 2 Indicators (Deferred)

These are NOT in Phase 1 scope. Implement only if MVP feedback shows need.

**Phase 2A: Jira Direct API Querying**
- If MVP shows merge conflicts too frequent/noisy
- Implement Jira API integration to fetch stories directly
- Display stories as read-only H4 sections in markdown
- Reduce false conflicts by having fresher baseline
- See PRD Section 10 (Option A) and Section 11 (Model 2)

**Phase 2B: Story Decomposition in Markdown**
- Display full story hierarchy in markdown (read-only)
- Stories as H4 sections under epics (H3)
- Users click to Jira for editing (not in markdown)
- See PRD Section 10 for structure

**Phase 2C: Metadata & Change Attribution**
- Track when TP last synced with Jira
- Detect if change came from Jira or user push
- Help users understand "why did this change?"
- See PRD Section 11 (Model 3) and Section 11 ("Change Attribution")

---

## Atomic Commit Pattern

Each task follows:
1. Write test/BDD scenario (RED)
2. Implement feature (GREEN)
3. Verify no regressions
4. Commit atomically with clear message

Example:
```bash
git commit -m "feat: add tpcli create command

Implements Create operation for TargetProcess API.
Supports any entity type via --data JSON parameter.
Tests cover successful creation and error handling.
Ref: TODO.md 1.1, PRD Section 9 (Phase 1)"
```

---

## Success Criteria for Phase 1 COMPLETE

**Go CLI**:
- ✅ `tpcli create <EntityType> --data '...'` works
- ✅ `tpcli update <EntityType> <id> --data '...'` works
- ✅ Both handle errors gracefully

**Python Client**:
- ✅ create_team_objective() method works
- ✅ update_team_objective() method works
- ✅ create_feature() / update_feature() methods work
- ✅ All cached correctly

**Markdown Generation**:
- ✅ export_team_plan() generates valid markdown
- ✅ Frontmatter complete
- ✅ Objectives/epics formatted clearly
- ✅ Acceptance criteria cleaned and linked to Jira

**Git Integration**:
- ✅ `tpcli plan init` creates branches
- ✅ `tpcli plan pull` merges with 3-way merge
- ✅ `tpcli plan push` applies changes
- ✅ Conflicts shown as git merge markers

**Testing**:
- ✅ All BDD scenarios passing
- ✅ Core workflow (init → edit → pull → push) validated
- ✅ Edge cases covered (conflicts, errors, etc.)

**Overall**:
- ✅ User can pull PI plan, edit in markdown, push back to TP
- ✅ Changes tracked in git commits
- ✅ Conflicts resolved with git merge markers
- ✅ Clear error messages and documentation
- ✅ Ready for team feedback and Phase 2

---

**When Phase 1 Complete**: Freeze scope and gather team feedback before Phase 2 decisions.
