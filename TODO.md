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

**Files**: `cmd/plan.go`, `pkg/tpclient/client.go`, `tests/unit/test_tpclient.go`

**BDD Scenarios** (write first):
```gherkin
Feature: Create and Update TargetProcess Entities via CLI

Scenario: Create TeamPIObjective with valid data
  When user runs: tpcli create TeamPIObjective --data '{"name":"API Perf","team_id":1935991,...}'
  Then command succeeds with exit code 0
  And output contains JSON with "id" field
  And returned entity has all provided fields

Scenario: Update TeamPIObjective with valid data
  Given TeamPIObjective 12345 exists in TP
  When user runs: tpcli update TeamPIObjective 12345 --data '{"name":"New Name",...}'
  Then command succeeds with exit code 0
  And output contains updated JSON
  And TP API was called with PUT to /api/v1/TeamPIObjective/12345

Scenario: Create fails with invalid JSON
  When user runs: tpcli create Feature --data 'invalid-json'
  Then command fails with exit code 1
  And error message contains "invalid JSON"

Scenario: Update fails with not found
  When user runs: tpcli update TeamPIObjective 99999 --data '{"name":"x"}'
  Then command fails with exit code 1
  And error message contains "not found" or "404"
```

**Tasks** (BDD-driven):
- [ ] Write BDD scenarios in `tests/bdd/go_cli_create_update.feature`
- [ ] Implement step definitions in `tests/bdd/steps/go_cli_steps.py`

- [ ] Unit tests in `tests/unit/test_tpclient.go`:
  - [ ] Test `Create()` with valid JSON → returns entity with ID
  - [ ] Test `Update()` with valid JSON → returns updated entity
  - [ ] Test `Create()` with invalid JSON → error with message
  - [ ] Test `Update()` with 404 → error with message
  - [ ] Mock TP API responses for all scenarios

- [ ] Implement in `pkg/tpclient/client.go`:
  - [ ] Add `func (c *Client) Create(entityType string, data []byte) ([]byte, error)`
    - Parse JSON data parameter
    - Call TP API: `POST /api/v1/{EntityType}`
    - Return created entity JSON
    - Handle errors (validation, auth, etc.)

  - [ ] Add `func (c *Client) Update(entityType string, id string, data []byte) ([]byte, error)`
    - Parse JSON data parameter
    - Call TP API: `PUT /api/v1/{EntityType}/{id}`
    - Return updated entity JSON
    - Handle errors (not found, validation, etc.)

- [ ] Implement in `cmd/plan.go`:
  - [ ] Add `create` command with `--data` flag
  - [ ] Add `update` command with `--data` flag
  - [ ] Parse and validate JSON input
  - [ ] Call client methods and output JSON response

**Test & Commit Loop**:
```bash
go test ./...                              # RED - tests fail
# ... implement Create/Update methods ...
go test ./...                              # GREEN - all pass
git add . && git commit -m "feat: add tpcli create/update commands..."
```

**Success Criteria** (tests must pass):
- ✅ Unit tests all passing
- ✅ BDD scenarios all passing
- ✅ `tpcli create TeamPIObjective --data '{...}'` works end-to-end
- ✅ `tpcli update TeamPIObjective 12345 --data '{...}'` works end-to-end
- ✅ Both handle errors gracefully with clear messages

---

### 1.2 Python API Client: Wrapper Methods

**Files**: `tpcli_pi/core/api_client.py`, `tests/unit/test_api_client.py`

**BDD Scenarios** (write first):
```gherkin
Feature: Python API Client Wrapper Methods

Scenario: Create team objective via Python client
  When Python code calls: client.create_team_objective("API Perf", team_id=1935991, release_id=1942235)
  Then subprocess "tpcli create TeamPIObjective --data ..." is called
  And JSON response is parsed
  And TeamPIObjective object is returned
  And object is added to cache with ID

Scenario: Update team objective via Python client
  Given objective 12345 exists in cache
  When Python code calls: client.update_team_objective(12345, name="New Name", effort=40)
  Then subprocess "tpcli update TeamPIObjective 12345 --data ..." is called
  And updated object is returned
  And cache is updated

Scenario: Create feature via Python client
  When Python code calls: client.create_feature("User Auth", parent_epic_id=2018883)
  Then subprocess "tpcli create Feature --data ..." is called
  And Feature object is returned and cached

Scenario: Update feature via Python client
  Given feature 5678 exists in cache
  When Python code calls: client.update_feature(5678, effort=13)
  Then subprocess "tpcli update Feature 5678 --data ..." is called
  And updated object is returned and cached

Scenario: Invalid response from subprocess raises exception
  Given subprocess returns invalid JSON
  When Python code calls: client.create_team_objective(...)
  Then APIClientError is raised with clear message
```

**Tasks** (BDD-driven):
- [ ] Write BDD scenarios in `tests/bdd/python_api_wrapper.feature`
- [ ] Implement step definitions in `tests/bdd/steps/api_steps.py`

- [ ] Unit tests in `tests/unit/test_api_client.py`:
  - [ ] Test `create_team_objective()` with valid args → returns TeamPIObjective
  - [ ] Test `update_team_objective()` with valid args → returns updated object
  - [ ] Test `create_feature()` with valid args → returns Feature
  - [ ] Test `update_feature()` with valid args → returns updated object
  - [ ] Test payload construction (name, team_id, release_id, optional fields)
  - [ ] Test response parsing and object creation
  - [ ] Test cache add/update operations
  - [ ] Test error handling (invalid JSON, subprocess failure)
  - [ ] Mock subprocess responses

- [ ] Implement in `tpcli_pi/core/api_client.py`:
  - [ ] Add `def create_team_objective(self, name: str, team_id: int, release_id: int, **kwargs) -> TeamPIObjective:`
    - Prepare JSON payload
    - Call `self._run_tpcli("create", "TeamPIObjective", payload)`
    - Parse response
    - Add to `self.objectives_cache`
    - Return `TeamPIObjective` object

  - [ ] Add `def update_team_objective(self, objective_id: int, **kwargs) -> TeamPIObjective:`
    - Prepare JSON payload
    - Call `self._run_tpcli("update", "TeamPIObjective", objective_id, payload)`
    - Parse response
    - Update `self.objectives_cache`
    - Return `TeamPIObjective` object

  - [ ] Add `def create_feature(self, name: str, parent_epic_id: int, **kwargs) -> Feature:`
    - Similar pattern to objectives

  - [ ] Add `def update_feature(self, feature_id: int, **kwargs) -> Feature:`
    - Similar pattern to objectives

**Test & Commit Loop**:
```bash
pytest tests/unit/test_api_client.py -v  # RED
# ... implement wrapper methods ...
pytest tests/unit/test_api_client.py -v  # GREEN
git add . && git commit -m "feat: add Python API wrapper methods..."
```

**Success Criteria** (tests must pass):
- ✅ Unit tests all passing
- ✅ BDD scenarios all passing
- ✅ `client.create_team_objective()` works with correct subprocess call
- ✅ `client.update_team_objective()` works with correct subprocess call
- ✅ `client.create_feature()` and `client.update_feature()` work
- ✅ Responses parsed and cached correctly
- ✅ No manual API curl needed

---

### 1.3 Markdown Generation: Export TP to Markdown

**Files**: `tpcli_pi/core/markdown_generator.py` (NEW), `tests/unit/test_markdown_generator.py`

**BDD Scenarios** (write first):
```gherkin
Feature: Markdown Generation from TargetProcess Data

Scenario: Export team plan generates valid markdown
  Given team "Platform Eco" (id=1935991) exists
  And release "PI-4/25" (id=1942235) exists
  And team has 2 objectives and 4 epics
  When code calls: MarkdownGenerator.export_team_plan(1935991, 1942235)
  Then result is MarkdownPlan with valid markdown content
  And markdown starts with H1 title with team and release name
  And markdown contains H2 sections for each objective
  And markdown contains H3 sections for each epic

Scenario: Frontmatter contains required metadata
  When code calls: MarkdownGenerator.export_team_plan(1935991, 1942235)
  Then frontmatter includes:
    - tp_team_id: 1935991
    - tp_release_id: 1942235
    - tp_release_name: "PI-4/25"
    - tp_last_sync: ISO 8601 timestamp
    - tp_last_sync_hash: SHA256 of data

Scenario: Acceptance criteria cleaned from HTML
  Given epic with AC CustomField containing: "<p>Item 1&#44; Item 2&nbsp;extra</p>"
  When markdown is generated
  Then epic section contains: "- Item 1, Item 2 extra" (cleaned)

Scenario: Jira keys formatted as clickable links
  Given epic with Jira key "DAD-2652"
  When markdown is generated
  Then epic section contains: "[DAD-2652](https://jira.takeda.com/browse/DAD-2652)"

Scenario: Missing optional fields handled gracefully
  Given objective with no owner, no acceptance criteria
  When markdown is generated
  Then objective section renders without those fields (no errors)
```

**Data Model**:
```python
class MarkdownPlan:
    """Generated markdown plan with YAML frontmatter"""
    frontmatter: dict  # {tp_team_id, tp_release_id, tp_release_name, tp_last_sync, tp_last_sync_hash}
    objectives: list[str]  # H2 sections: "## Objective: ..."
    epics: list[str]  # H3 sections: "### Epic: ..."
    content: str  # Full markdown text
```

**Tasks** (BDD-driven):
- [ ] Write BDD scenarios in `tests/bdd/markdown_generation.feature`
- [ ] Implement step definitions in `tests/bdd/steps/markdown_steps.py`

- [ ] Unit tests in `tests/unit/test_markdown_generator.py`:
  - [ ] Test `export_team_plan()` returns MarkdownPlan object
  - [ ] Test frontmatter generation with all required fields
  - [ ] Test H1 title with team and release names
  - [ ] Test H2 objective sections with ID, status, owner, effort
  - [ ] Test H3 epic sections with ID, Jira key, effort, AC
  - [ ] Test HTML cleaning: strip tags, convert entities
  - [ ] Test Jira links formatted correctly
  - [ ] Test edge cases: no AC, missing fields, empty objectives
  - [ ] Mock API client responses

- [ ] Implement `tpcli_pi/core/markdown_generator.py`:
  - [ ] Create `MarkdownGenerator` class

  - [ ] Add `def export_team_plan(team_id: int, release_id: int) -> MarkdownPlan:`
    - Fetch objectives via `api_client.list_team_objectives(team_id, release_id)`
    - Fetch features/epics via `api_client.list_features(parent=objectives)`
    - Generate frontmatter dict with metadata
    - Generate H1 title
    - Generate H2 objective sections
    - Generate H3 epic sections
    - Combine into markdown content
    - Return MarkdownPlan object

  - [ ] Add `def _generate_frontmatter(team_id, release_id, data) -> dict:`
    - Include tp_team_id, tp_release_id, tp_release_name
    - Include tp_last_sync (now in ISO 8601)
    - Include tp_last_sync_hash (SHA256 of serialized data)

  - [ ] Add `def _clean_html(html_str: str) -> str:`
    - Strip HTML tags
    - Convert entities: `&#44;` → `,`, `&nbsp;` → ` `, etc.
    - Return cleaned text

  - [ ] Add `def _format_jira_link(jira_key: str) -> str:`
    - Return `[{key}](https://jira.takeda.com/browse/{key})`

**Test & Commit Loop**:
```bash
pytest tests/unit/test_markdown_generator.py -v  # RED
# ... implement MarkdownGenerator ...
pytest tests/unit/test_markdown_generator.py -v  # GREEN
git add . && git commit -m "feat: add markdown generation from TP data..."
```

**Success Criteria** (tests must pass):
- ✅ Unit tests all passing
- ✅ BDD scenarios all passing
- ✅ `MarkdownGenerator.export_team_plan()` returns valid markdown
- ✅ Frontmatter complete with all metadata
- ✅ Objectives/epics formatted clearly
- ✅ Acceptance criteria cleaned and formatted
- ✅ Jira keys as clickable links

---

### 1.4 Git Integration: Pull/Push with 3-Way Merge

**Files**: `tpcli_pi/core/git_sync.py` (NEW), `tpcli_pi/cli/plan.py` (NEW), `tests/unit/test_git_sync.py`

**BDD Scenarios** (write first):
```gherkin
Feature: Git-based Plan Sync with 3-Way Merge

Scenario: Initialize plan creates branches and markdown
  Given team "Platform Eco" and release "PI-4/25"
  When user runs: tpcli plan init --team "Platform Eco" --release "PI-4/25"
  Then branch "TP-PI-4-25-platform-eco" is created (tracking)
  And branch "feature/plan-pi-4-25" is created (working)
  And user is on "feature/plan-pi-4-25"
  And file "objectives.md" exists with frontmatter and content
  And commit "TP-PI-4-25-platform-eco" shows initial markdown

Scenario: Pull merges fresh TP state without conflicts
  Given user is on "feature/plan-pi-4-25" with no local changes
  And TP has 2 objectives (effort 34, 21)
  When user runs: tpcli plan pull
  Then "TP-PI-4-25-platform-eco" branch updated with fresh TP data
  And objectives.md merged into working branch
  And no merge conflicts
  And git log shows merge commit

Scenario: Pull detects merge conflicts
  Given user is on "feature/plan-pi-4-25" with local edit to "API Perf" objective
  And TP was updated by another user (same objective changed)
  When user runs: tpcli plan pull
  Then git merge initiated with 3-way merge
  And objectives.md contains merge conflict markers (<<<<<<, ======, >>>>>>)
  And git status shows "both modified: objectives.md"
  And user can manually resolve

Scenario: Push applies markdown changes to TP
  Given user is on "feature/plan-pi-4-25" with local commits
  And objectives.md has changed: "API Perf" effort 34 → 40
  When user runs: tpcli plan push
  Then TP API called to update objective 12345 with effort 40
  And "TP-PI-4-25-platform-eco" tracking branch updated
  And git log shows push commit with changes summary

Scenario: Push with new epic creates in TP
  Given objectives.md adds new H3 section "### Epic: Auth Flow"
  When user runs: tpcli plan push
  Then TP API called to create Feature with parent objective
  And new epic gets TP ID added to markdown
  And markdown committed to tracking branch

Scenario: List shows available plans
  Given multiple team/release combinations with tracking branches
  When user runs: tpcli plan list
  Then shows all available plans
  And indicates which have active working branches checked out
```

**Tasks** (BDD-driven):
- [ ] Write BDD scenarios in `tests/bdd/git_integration.feature`
- [ ] Implement step definitions in `tests/bdd/steps/git_steps.py`
  - [ ] Temp git repo setup/teardown
  - [ ] Mock TP API responses
  - [ ] Git branch assertions

- [ ] Unit tests in `tests/unit/test_git_sync.py`:
  - [ ] Test `init_plan()` creates branches and markdown file
  - [ ] Test `pull_plan()` fetches and merges without conflicts
  - [ ] Test `pull_plan()` detects merge conflicts
  - [ ] Test `push_plan()` updates objectives via API
  - [ ] Test `push_plan()` creates new features via API
  - [ ] Test branch name generation
  - [ ] Test markdown parsing for diffs
  - [ ] Test error handling (not on working branch, etc.)

- [ ] Implement `tpcli_pi/core/git_sync.py`:
  - [ ] Create `GitSync` class with constructor `__init__(repo_path)`

  - [ ] Add `def init_plan(self, team: str, release: str) -> str:`
    - Generate branch names: `TP-{release}-{team_slug}`, `feature/plan-{release}`
    - Run: `git branch TP-...` (tracking branch)
    - Run: `git branch feature/...` (working branch)
    - Generate markdown via `MarkdownGenerator.export_team_plan()`
    - Commit to tracking branch
    - Checkout working branch
    - Return working branch name

  - [ ] Add `def pull_plan(self) -> (bool, list[str]):`
    - Verify on working branch (error if on tracking)
    - Get tracking branch name from current branch
    - Fetch latest TP data
    - Update tracking branch with fresh markdown
    - Run: `git merge {tracking_branch}` (3-way merge)
    - Parse `git status` for conflicts
    - Return (success, list of conflicting files)

  - [ ] Add `def push_plan(self) -> dict:`
    - Parse current markdown (objectives and epics)
    - Get last-known state from tracking branch
    - Diff to find changes (new/updated objectives, epics)
    - Call API client methods to apply changes
    - Update tracking branch markdown
    - Commit to tracking branch
    - Return summary dict: {created: [...], updated: [...], errors: [...]}

  - [ ] Add `def list_plans(self) -> list[dict]:`
    - Find all `TP-*` tracking branches
    - Extract team/release from branch names
    - Check which have active working branches
    - Return list of plan dicts

- [ ] Implement `tpcli_pi/cli/plan.py`:
  - [ ] Add `@click.group()` for plan commands

  - [ ] Add `@plan.command('init')` with `--team`, `--release` options:
    - Create `GitSync` instance
    - Call `init_plan()`
    - Print success message

  - [ ] Add `@plan.command('pull')` (no args):
    - Create `GitSync` instance
    - Call `pull_plan()`
    - If conflicts: print "Merge in progress. Resolve conflicts and git commit."
    - Otherwise: print summary

  - [ ] Add `@plan.command('push')` (no args):
    - Create `GitSync` instance
    - Call `push_plan()`
    - Print summary of applied changes

  - [ ] Add `@plan.command('list')` (no args):
    - Create `GitSync` instance
    - Call `list_plans()`
    - Print formatted table

**Test & Commit Loop**:
```bash
pytest tests/unit/test_git_sync.py -v        # RED
# ... implement GitSync class ...
pytest tests/unit/test_git_sync.py -v        # GREEN
git add . && git commit -m "feat: implement git sync with 3-way merge..."

pytest tests/unit/ -v                         # RED
# ... implement CLI commands ...
pytest tests/unit/ -v                         # GREEN
git add . && git commit -m "feat: add tpcli plan init/pull/push commands..."
```

**Success Criteria** (tests must pass):
- ✅ Unit tests all passing
- ✅ BDD scenarios all passing
- ✅ `tpcli plan init` creates branches and initial markdown
- ✅ `tpcli plan pull` merges fresh TP state (3-way)
- ✅ `tpcli plan push` applies changes to TP
- ✅ Conflicts shown as git merge markers
- ✅ `tpcli plan list` shows available plans

---

### 1.5 Integration Testing: Core Workflow BDD

**Files**: `tests/bdd/core_workflow.feature`, `tests/bdd/steps/workflow_steps.py`

**Comprehensive BDD Scenarios** (test all sections together):
```gherkin
Feature: Plan Sync Core Workflow (End-to-End)

Scenario: Complete init-edit-pull-push workflow
  Given TargetProcess has team "Platform Eco" and release "PI-4/25"
  And TP has 2 objectives with 4 epics total

  When user runs: tpcli plan init --team "Platform Eco" --release "PI-4/25"
  Then initial markdown created and committed
  And user is ready to edit

  When user edits objectives.md: "API Perf" effort 34 → 40
  And user commits: git add . && git commit -m "Update API effort"
  Then working branch has 1 new commit

  When TP is updated externally (different objective changed)
  And user runs: tpcli plan pull
  Then merge completes without conflicts
  And objectives.md includes both local and remote changes

  When user runs: tpcli plan push
  Then TP objective updated with effort 40
  And tracking branch updated
  And all changes persisted to TP

Scenario: Conflict resolution workflow
  Given initialized plan on working branch
  And local edit to objective "API Perf"
  And TP also updated "API Perf" (different field)

  When user runs: tpcli plan pull
  Then merge conflict detected for "API Perf" section
  And objectives.md shows <<<<<<, ======, >>>>>> markers
  And git status shows merge in progress

  When user manually edits to resolve (chooses both changes)
  And user commits: git add . && git commit
  Then merge completes
  And both changes preserved

  When user runs: tpcli plan push
  Then TP receives merged state
  And no data loss

Scenario: Multiple users collaborating
  Given team-shared tracking branch "TP-PI-4-25-platform-eco"
  And two users pull to separate working branches

  When User A edits objective 1, commits, pushes
  And User B edits objective 2, commits
  Then User B's pull should merge cleanly
  And both users' changes in TP after their push
  And no conflicts since they edited different objectives
```

**Tasks**:
- [ ] Write comprehensive BDD scenarios in `tests/bdd/core_workflow.feature`
- [ ] Implement full step definitions in `tests/bdd/steps/workflow_steps.py`:
  - [ ] Setup: create temp git repo, mock TP API
  - [ ] Steps for running all tpcli plan commands
  - [ ] Git assertions (branches exist, commits present, etc.)
  - [ ] Markdown assertions (content, frontmatter, etc.)
  - [ ] TP API assertions (calls made, data updated)
  - [ ] Teardown: clean temp repo

- [ ] Run full BDD test suite:
  ```bash
  pytest tests/bdd/ -v --tb=short
  ```

**Test & Commit Loop**:
```bash
pytest tests/bdd/core_workflow.feature -v     # RED (integration tests)
# All sections 1.1-1.4 already implemented
pytest tests/bdd/ -v                          # GREEN
git add . && git commit -m "test: add integration BDD scenarios for core workflow"
```

**Success Criteria** (tests must pass):
- ✅ All integration BDD scenarios passing
- ✅ Core workflow (init → edit → pull → push) validates end-to-end
- ✅ Conflict scenarios handled correctly
- ✅ Multi-user collaboration scenarios work
- ✅ Clear error messages in edge cases
- ✅ All data persisted correctly to TP and git

---

## Implementation Order

**Workflow for Each Section**:
For sections 1.1 through 1.4, follow this pattern for each:

```
1. Write BDD scenarios (.feature file)
2. Write unit tests (.py or .go file)
3. Run tests → RED
4. Implement feature code
5. Run tests → GREEN
6. Commit atomically
```

**Week 1: Foundation** (Days 1-3)
- **Section 1.1**: Go CLI create/update
  - Write BDD + unit tests → RED
  - Implement → GREEN
  - Commit

- **Section 1.2**: Python API wrapper
  - Write BDD + unit tests → RED
  - Implement → GREEN
  - Commit

- **Section 1.3**: Markdown generation
  - Write BDD + unit tests → RED
  - Implement → GREEN
  - Commit

**Week 2: Integration** (Days 4-5)
- **Section 1.4**: Git integration
  - Write BDD + unit tests → RED
  - Implement → GREEN
  - Commit

- **Section 1.5**: Integration testing
  - Write comprehensive BDD scenarios
  - Run against fully-implemented 1.1-1.4
  - All tests GREEN

**Validation**: All BDD scenarios and unit tests green, core workflow (init → edit → pull → push) works end-to-end

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
