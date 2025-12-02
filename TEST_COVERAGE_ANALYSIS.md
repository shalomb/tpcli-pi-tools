# tpcli_pi Module Test Coverage Analysis

## Executive Summary

Out of 9 core modules totaling **3,941 lines of code**, tests have been written for 8 modules with **379 total test functions**. 

**Coverage Status:**
- **Well Tested (>80%)**: 2 modules (config, markdown_generator)
- **Moderately Tested (60-80%)**: 2 modules (jira_api_client, api_client)
- **Poorly Tested (<60%)**: 5 modules (resilience, analysis, git_integration, monitoring, change_tracker)

---

## Module Breakdown: Lines of Code vs Tests

| Module | LOC | Tests | Tests/100LOC | Est. Coverage | Status |
|--------|-----|-------|--------------|---------------|--------|
| config.py | 144 | 43 | 29.9% | ~100% | ✓ Complete |
| markdown_generator.py | 412 | 97 | 23.5% | ~85% | ✓ Good |
| jira_api_client.py | 301 | 27 | 8.97% | ~70% | ⚠ Moderate |
| api_client.py | 1,009 | 74 | 7.3% | ~65% | ⚠ Low |
| resilience.py | 338 | 25 | 7.4% | ~65% | ⚠ Low |
| analysis.py | 406 | 26 | 6.4% | ~60% | ⚠ Low |
| git_integration.py | 350 | 23 | 6.6% | ~50% | ✗ Very Low |
| change_tracker.py | 528 | 35 | 6.6% | ~50% | ✗ Very Low |
| monitoring.py | 448 | 21 | 4.7% | ~55% | ✗ Very Low |

---

## Detailed Gap Analysis

### 1. CONFIG.PY (144 LOC) - 43 Tests - ~100% Coverage ✓

**Status**: COMPLETE - Well tested

**What's Tested:**
- All 6 getter functions (jira_url, jira_token, tp_url, tp_token, default_art, default_team)
- All configuration precedence orders (config file > env var > default)
- YAML loading and parsing
- Missing file handling
- Environment variable overrides

**Gaps**: None significant


### 2. MARKDOWN_GENERATOR.PY (412 LOC) - 97 Tests - ~85% Coverage ✓

**Status**: GOOD - Well tested

**What's Tested:**
- Markdown generation (generate method)
- Frontmatter creation and YAML serialization
- Objective sections with metadata
- Epic sections with Jira links
- Story sections (Phase 2B) with status, assignee, story points
- Acceptance criteria rendering and HTML cleaning
- Filename generation and normalization
- Section ordering

**Known Gaps:**
- No tests for _clean_html() with various edge cases:
  - Multiple consecutive newlines
  - Nested HTML tags
  - Malformed HTML entities
  - Very long text without HTML
- No tests for boundary conditions:
  - Empty objectives list
  - Missing required fields in data dict
  - Very long objective/epic/story names
  - Special characters in names
- Limited tests for story rendering:
  - Only 5-6 tests for _story_section
  - Missing: stories with missing fields, malformed description, null descriptions
- YAML dump function (_yaml_dump) has no explicit tests:
  - Complex nested structures
  - Special characters in values
  - List items with dicts


### 3. JIRA_API_CLIENT.PY (301 LOC) - 27 Tests - ~70% Coverage

**Status**: MODERATE - Needs more tests

**What's Tested:**
- Client initialization with credentials (token from env, config, constructor)
- fetch_stories_by_epic() basic flow
- Story parsing and field extraction
- Status extraction
- Cache management
- Rate limiting handling
- Error handling (timeout, API errors, malformed responses)
- Missing token error message

**Significant Gaps:**
1. **Search Method (_search_jira) - 35 LOC, UNTESTED**
   - Retry logic with exponential backoff
   - Rate limit (429) handling
   - Timeout handling
   - JSON parsing failures
   - HTTP status codes other than 429

2. **Story Field Extraction - INCOMPLETE**
   - Story points extraction heuristic (searches for "story" or "point" in field names)
   - Missing test cases:
     - Custom field IDs other than customfield_10001
     - Story points as float vs int
     - Null/missing story points
     - Multiple fields matching "story" pattern

3. **Cache Logic - GAPS**
   - Cache TTL expiration (only tests basic _is_cached)
   - Cache invalidation behavior
   - Cache statistics/metrics
   - Multiple epics in cache
   - Cache memory usage

4. **Error Paths - MISSING**
   - Missing jira_key in epic (currently silent)
   - Invalid epic_key formats (not caught by isinstance check)
   - Network errors (socket timeout, connection refused)
   - Invalid JSON responses
   - Partial responses (missing required fields)

5. **Edge Cases**
   - Empty epic (no stories returned)
   - Very large epic (>500 stories, hits maxResults limit)
   - Special characters in Jira keys
   - Assignee data in unexpected formats


### 4. API_CLIENT.PY (1,009 LOC) - 74 Tests - ~65% Coverage

**Status**: LOW - Large module needs more coverage

**What's Tested:**
- Basic CRUD operations (create, update objectives)
- Feature operations
- Bulk operations (bulk_create, bulk_update)
- Cache management and TTL
- Date parsing (TP format and ISO)
- Querying teams, releases, objectives
- Parsing of all entity types (User, Team, ART, Release, ProgramPIObjective, TeamPIObjective, Feature)
- Error handling (invalid JSON, timeouts, command errors)

**Critical Gaps:**
1. **_run_tpcli Method (100+ LOC) - PARTIAL COVERAGE**
   - JSON extraction logic with various output formats
   - Error messages aren't fully tested:
     - stderr parsing
     - Different error types
   - Subprocess timeout handling (has test but no actual timeout scenario)
   - Missing JSON in output (has test)
   - Single object vs array response (both tested)

2. **Query Filters - INCOMPLETE**
   - Tested: basic filters (art, release, team, parent_epic)
   - NOT tested:
     - Multiple filter combinations beyond basic pairs
     - Invalid filter values
     - SQL injection attempts in where clauses
     - Empty filter results handling
     - Large result sets (>1000 items)

3. **Entity Parsing - GAPS**
   - User parsing: only 2 tests (complete + missing fields)
   - Team parsing: 3 tests (missing edge cases like invalid member count)
   - Feature parsing: 2 tests (missing owner scenario not fully tested)
   - ProgramPIObjective: 2 tests
   - Release: 2 tests (missing dates partially tested)
   - No tests for:
     - Null/empty field handling in all entities
     - Invalid data types (string instead of int for IDs)
     - Very long strings
     - Unicode/special characters

4. **Caching - PARTIAL**
   - TTL expiration tested
   - Cache statistics tested
   - NOT tested:
     - Multiple queries with same key
     - Cache eviction under memory pressure
     - Cache consistency across multiple client instances
     - Cache poisoning (bad data cached)

5. **Missing Error Scenarios**
   - Network errors (not just timeout):
     - Connection refused
     - DNS resolution failure
     - SSL/TLS errors
   - Partial failures (some data parsed successfully, some fails)
   - Rate limiting from TargetProcess API
   - Token expiration/authentication failures


### 5. RESILIENCE.PY (338 LOC) - 25 Tests - ~65% Coverage

**Status**: LOW - Core resilience features undertested

**What's Tested:**
- Retry strategies (exponential, linear, fixed)
- Max delay enforcement
- RetryableOperation basic flow (success, failure, retry exhaustion)
- Recoverable vs non-recoverable errors
- Rate limit error handling
- Partial failure tracking (success/failure counting, rates)
- API rate limit detection and tracking

**Critical Gaps:**
1. **Retry Timing - NOT TESTED**
   - Actual sleep behavior (tests mock it, no time verification)
   - Exponential backoff with large attempt numbers
   - backoff_multiplier != 2.0
   - Delay cap behavior at boundaries
   - Time.sleep accuracy

2. **RateLimitError Specifics - INCOMPLETE**
   - Custom retry_after values (only tested with default 60)
   - retry_after < base_delay
   - retry_after > max_delay

3. **PartialFailureHandler - GAPS**
   - Error type aggregation (get_summary includes errors_by_type):
     - Only tested with ValueError
     - Not tested: multiple error types, inheritance hierarchy
   - Empty state edge cases:
     - success_rate when total_count == 0 (returns 100.0, correct but untested)
   - Failed operations tracking:
     - get_summary only partially tested
     - Not tested: retrieval of original exceptions

4. **APIRateLimitHandler - SIGNIFICANT GAPS**
   - Window duration hardcoded to 60.0, no tests for:
     - Requests arriving at window boundary
     - Clock skew (time goes backwards)
     - Very precise timing scenarios
   - check_rate_limit() calculation (LOC 308-309):
     - Not directly tested, inferred from exception raised
     - Edge case: wait_time calculation when oldest_request is very old

5. **Monitoring Integration - NOT TESTED**
   - record_retry() calls monitoring service
   - Monitoring service failures shouldn't block retry (try/except at LOC 184-192)
   - No tests for:
     - Monitoring service unavailable
     - Monitoring service exceptions

6. **Error Scenarios - MISSING**
   - Operation function raises different exception types each retry
   - Operation function modifies state on failure
   - Operation function raises SystemExit or KeyboardInterrupt
   - Custom is_recoverable function with side effects


### 6. ANALYSIS.PY (406 LOC) - 26 Tests - ~60% Coverage

**Status**: LOW - Many untested methods

**What's Tested:**
- CapacityAnalyzer:
  - Total effort calculation
  - Per-person effort estimation
  - Overcommitment detection
  - Empty team and no-objectives scenarios
- RiskAnalyzer:
  - Objective assessment with various risk conditions
  - Team assessment with aggregation
  - Risk recommendations generation
- MetricsCalculator:
  - Burndown rate calculation (with 5 tests covering 0%, partial, 100%, empty)

**Major Gaps:**
1. **DependencyAnalyzer - UNTESTED** (40 LOC)
   - map_dependencies(): placeholder returns empty, no tests
   - find_critical_path(): placeholder returns first 3 items, no tests
   - Comments indicate incomplete implementation

2. **RiskAnalyzer._check_dependency_risks() - MINIMAL**
   - Heuristic similarity detection untested
   - Only creates DependencyMapping with "Related" type
   - No tests for:
     - Objectives with no name overlap
     - Multiple similar objectives (>3)
     - Same objective checked against itself

3. **CapacityAnalyzer - GAPS**
   - effort_per_person_estimate calculation:
     - Only 1 test explicitly checks per-person distribution
     - Not tested: rounding/truncation to int
   - Hardcoded 80 points per person:
     - No tests for configurable capacity
     - No tests for teams with different skill levels
   - team.member_count edge cases:
     - Tested with 0, not with negative (shouldn't happen)
     - Not tested: very large team (1000+ members)

4. **RiskAnalyzer Risk Detection - INCOMPLETE**
   - _check_estimation_risks(): 
     - Tests: zero effort, low effort (<5)
     - Missing: negative effort, very large effort (>1000)
   - _check_feature_risks():
     - Tests: unstarted features, unassigned, no effort
     - Missing: combinations of these conditions
     - Status check hardcodes ["In Progress", "Done"], untested:
       - Different status values
       - null status
   - _check_dependency_risks():
     - Heuristic only (no real TP API calls)
     - No tests for circular dependencies

5. **RiskAssessment Health Score - NOT TESTED**
   - health_score calculated in __post_init__ (not shown in module)
   - No tests verify health_score changes with different risk counts

6. **MetricsCalculator - INCOMPLETE**
   - calculate_team_velocity(): returns 0.0, placeholder
   - No tests for actual velocity calculations
   - calculate_burndown_rate():
     - Tested with valid inputs
     - Missing: current_progress_pct > 100, < 0
     - Missing: very large effort values


### 7. GIT_INTEGRATION.PY (350 LOC) - 23 Tests - ~50% Coverage ✗

**Status**: VERY LOW - Critical functions barely tested

**What's Tested:**
- Initialization (branch name generation, tracking/feature branch creation)
- Branch naming conventions
- SyncResult structure
- Basic subprocess mocking

**Critical Gaps:**
1. **GitPlanSync.init() - PARTIAL** (60 LOC)
   - Tested: branch name generation, file operations are mocked
   - NOT TESTED:
     - Actual markdown file writing
     - Markdown generation integration
     - Git commit messages
     - Push to remote origin
     - Handling when branches already exist
     - Handling when repo doesn't exist
     - Failed git operations

2. **GitPlanSync.pull() - UNTESTED** (50 LOC)
   - Reads markdown from TP
   - Commits to tracking branch
   - Rebases feature branch
   - Detects conflicts
   - NOT TESTED:
     - Rebase success path
     - Rebase conflict scenarios
     - Switching between branches
     - Git fetch behavior
     - Markdown generation
     - Conflict marker parsing

3. **GitPlanSync.push() - UNTESTED** (60 LOC)
   - Calculates diff between tracking and current branch
   - Parses changes from diff
   - Executes API calls
   - Updates tracking branch
   - NOT TESTED:
     - Diff calculation
     - Change parsing (_parse_changes)
     - API call execution (_execute_api_call)
     - Empty diff handling (tested to return no changes)
     - Multiple file changes

4. **_parse_changes() - STUB** (20 LOC)
   - Returns empty list, placeholder implementation
   - No tests (would be multiple scenarios of objective/epic changes)

5. **_execute_api_call() - STUB** (5 LOC)
   - Empty implementation
   - No tests

6. **_run_git() Error Handling - INCOMPLETE**
   - CalledProcessError caught and wrapped
   - NOT TESTED:
     - Actual command failures
     - stderr output parsing
     - Different error exit codes
     - Command timeout (no timeout parameter)

7. **Edge Cases - NOT TESTED**
   - Repo not initialized
   - Permission denied errors
   - Branch name conflicts (branch already exists)
   - File path conflicts (file already exists)
   - Very long file names
   - Special characters in branch/file names
   - Large markdown files
   - Network timeouts on git push


### 8. CHANGE_TRACKER.PY (528 LOC) - 35 Tests - ~50% Coverage ✗

**Status**: VERY LOW - Many methods untested

**Module Content:**
- FieldChange: dataclass (5 LOC) - basic
- ChangeSource: dataclass (12 LOC) - basic
- AuditLogEntry: dataclass (16 LOC) - basic
- AuditLog: class (85 LOC)
- ChangeTracker: CLASS NOT SHOWN IN TESTS (implied to exist from test imports)

**What's Tested:**
- AuditLog operations:
  - log_pull(), log_push(), log_conflict()
  - get_entries(), get_last_pull()
  - get_conflicts_count()
  - export_to_dict()

**Critical Gaps:**
1. **ChangeTracker Class - MOSTLY MISSING**
   - Tests import and use ChangeTracker:
     - detect_changes_in_diff()
     - detect_user_edits()
     - detect_jira_updates()
     - get_change_summary()
     - generate_conflict_hints()
   - But these methods NOT found in read module (256 LOC shown, ChangeTracker not included)
   - Tests written but implementation may be incomplete
   - NO STUB implementations visible

2. **AuditLog - PARTIAL TESTS**
   - get_entries() tested but not fully integrated
   - export_to_dict() tested with basic scenarios only
   - Missing edge cases:
     - Very long operation chains (1000+ entries)
     - Querying by date range
     - Filtering operations
     - Performance with large logs

3. **Test File Has Empty Stubs** (lines 415-512)
   - TestMetadataEnhancement: all pass (no implementation)
   - TestConflictDetectionLogic: all pass (no implementation)
   - TestChangeTrackingIntegration: all pass (no implementation)
   - TestPhase2CErrorHandling: all pass (no implementation)
   - ~100 LOC of skeleton tests that do nothing

4. **Missing Error Handling Tests**
   - Invalid timestamp formats
   - Concurrent edits
   - Clock skew scenarios
   - Malformed diffs


### 9. MONITORING.PY (448 LOC) - 21 Tests - ~55% Coverage ✗

**Status**: VERY LOW - Large module with limited testing

**What's Tested:**
- OperationMetrics:
  - Creation and finalization
  - Duration calculation
  - Serialization to dict
- HealthCheckResult:
  - Creation and dict conversion
- MonitoringService:
  - Operation start/end tracking
  - Health check registration and status
  - Metrics summary (24-hour window)
  - Conflict analysis
  - JSON export
  - Retry recording
  - Error logging
  - Singleton pattern
- Integration test: complete operation workflow

**Critical Gaps:**
1. **MonitoringService._setup_logger() - NOT TESTED** (25 LOC)
   - File handler creation
   - Console handler setup
   - Formatter configuration
   - NO TESTS for:
     - Log file writing
     - Rotation behavior
     - Handler configuration
     - Logger level settings

2. **Metrics Filtering - INCOMPLETE**
   - get_metrics_summary():
     - Tested: hours parameter, operation type filter
     - Missing:
       - Metrics across multiple hour ranges (1h, 7d, 30d)
       - Empty metrics handling (only one test, message checked)
       - Duration statistics (avg/min/max tested, std dev missing)
   - get_conflicts_analysis():
     - Basic stats tested
     - Missing:
         - Conflict trends over time
         - Conflict patterns by team
         - Conflict patterns by operation type

3. **Health Check Behavior - GAPS**
   - register_health_check():
     - Tested: success, failure, exception
     - Missing:
       - Health check that returns non-boolean
       - Health check that takes too long (timeout)
       - Multiple checks with same name (overwrites?)
       - Large number of checks (100+)
   - get_health_status():
     - Returns overall status correctly
     - Not tested: performance with many checks

4. **Metrics Recording - INCOMPLETE**
   - record_metrics() sets fields on existing metrics
   - NOT TESTED:
     - Recording with zero values
     - Recording with negative values (shouldn't happen)
     - Recording after operation already ended
     - Multiple record_metrics calls (overwrites or accumulates?)

5. **Thread Safety - NOT TESTED**
   - _metrics_lock used for concurrent access
   - No tests with actual threads:
     - Multiple threads starting operations simultaneously
     - Multiple threads recording metrics
     - Race conditions in health check registration

6. **Export and Persistence - GAPS**
   - export_metrics_json():
     - Tested: JSON structure, file creation
     - Missing:
       - Export to non-existent directory (should create)
       - Export with disk full error
       - Corrupted metrics in JSON export
       - Export file permissions
   - Metrics not persisted on shutdown (only if explicitly exported)
   - No tests for reading/loading exported metrics

7. **Edge Cases - MISSING**
   - Metrics with very long operation names
   - Metrics with special characters in team/release names
   - Operation that takes extremely long (days)
   - Operation with very large change counts (millions)
   - get_metrics_summary with hours=0 or negative
   - Very old operations (outside available metrics)


---

## Coverage Prioritization: Modules Needing Most Tests

### Priority 1: CRITICAL (Use these modules heavily)
1. **GIT_INTEGRATION.PY** - 350 LOC, 23 tests (~6.6 tests/100 LOC)
   - Core sync functionality barely tested
   - Error paths untested
   - Should add: ~40 more tests
   
2. **API_CLIENT.PY** - 1009 LOC, 74 tests (~7.3 tests/100 LOC)
   - Largest module, moderate coverage
   - Query filters incomplete
   - Should add: ~60 more tests

### Priority 2: HIGH (Important functionality gaps)
3. **CHANGE_TRACKER.PY** - 528 LOC, 35 tests (~6.6 tests/100 LOC)
   - ChangeTracker class implementation missing/untested
   - 100+ LOC of skeleton tests (no-ops)
   - Should add: ~50 more tests

4. **MONITORING.PY** - 448 LOC, 21 tests (~4.7 tests/100 LOC)
   - Lowest test ratio
   - Logger setup not tested
   - Thread safety not tested
   - Should add: ~35 more tests

### Priority 3: MEDIUM (Moderate functionality gaps)
5. **ANALYSIS.PY** - 406 LOC, 26 tests (~6.4 tests/100 LOC)
   - DependencyAnalyzer not tested
   - Risk detection incomplete
   - Should add: ~30 more tests

6. **RESILIENCE.PY** - 338 LOC, 25 tests (~7.4 tests/100 LOC)
   - Retry timing not actually tested (mocked)
   - Window boundary conditions missing
   - Should add: ~25 more tests

### Priority 4: LOWER (Moderate-good coverage)
7. **JIRA_API_CLIENT.PY** - 301 LOC, 27 tests (~8.97 tests/100 LOC)
   - Search method and retry logic untested
   - Cache edge cases missing
   - Should add: ~15 more tests

8. **MARKDOWN_GENERATOR.PY** - 412 LOC, 97 tests (~23.5 tests/100 LOC)
   - Already well tested
   - Should add: ~10 more tests for edge cases

---

## Recommended Test Additions by Module

### 1. GIT_INTEGRATION.PY - Add ~40 tests

**Error Path Testing:**
- [ ] Test when repo doesn't exist
- [ ] Test when branch already exists (error handling)
- [ ] Test when file already exists
- [ ] Test git commands fail (CalledProcessError scenarios)
- [ ] Test permission denied errors

**Pull Operations:**
- [ ] Test successful rebase
- [ ] Test rebase with conflicts
- [ ] Test conflict detection and reporting
- [ ] Test markdown file reading/writing
- [ ] Test branch switching on existing branches

**Push Operations:**
- [ ] Test diff calculation with multiple files
- [ ] Test parsing changes from diff (when implemented)
- [ ] Test API call execution (when implemented)
- [ ] Test no changes scenario
- [ ] Test large number of changes

**Edge Cases:**
- [ ] Branch names with special characters
- [ ] File names with special characters
- [ ] Very long file names
- [ ] Large markdown files
- [ ] Simultaneous git operations

### 2. API_CLIENT.PY - Add ~60 tests

**Query Filters:**
- [ ] Test complex filter combinations (3+ filters)
- [ ] Test invalid filter values
- [ ] Test empty result sets
- [ ] Test large result sets (1000+ items)
- [ ] Test all filter types in combination

**Entity Parsing:**
- [ ] Test null/empty fields in all entity types
- [ ] Test invalid data types (string for ID fields)
- [ ] Test unicode/special characters
- [ ] Test very long strings
- [ ] Test missing optional fields across all entities

**Error Scenarios:**
- [ ] Test network errors (connection refused, DNS failure)
- [ ] Test SSL/TLS errors
- [ ] Test partial failures (some data parses, some fails)
- [ ] Test rate limiting from TP API
- [ ] Test authentication failures

**Caching:**
- [ ] Test cache poisoning
- [ ] Test cache consistency across instances
- [ ] Test cache memory usage
- [ ] Test concurrent cache access

### 3. CHANGE_TRACKER.PY - Add ~50 tests

**ChangeTracker Implementation** (needs tests for actual implementation):
- [ ] detect_changes_in_diff() - parse various diff formats
- [ ] detect_user_edits() - identify same-timestamp changes
- [ ] detect_jira_updates() - identify changed-timestamp changes
- [ ] get_change_summary() - aggregation and conflict detection
- [ ] generate_conflict_hints() - smart resolution suggestions

**AuditLog Enhancements:**
- [ ] Query by date range
- [ ] Filter by operation type
- [ ] Performance with 1000+ entries
- [ ] Edge cases: very long team/release names

**Error Handling:**
- [ ] Invalid timestamp formats
- [ ] Malformed diffs
- [ ] Concurrent edits
- [ ] Clock skew scenarios
- [ ] Missing fields in diffs

### 4. MONITORING.PY - Add ~35 tests

**Logger Setup:**
- [ ] File handler creation and writing
- [ ] Log rotation (if configured)
- [ ] Handler configuration verification
- [ ] Logger level settings

**Metrics Filtering:**
- [ ] Test various hour ranges (1, 7, 24, 168 for week)
- [ ] Test std dev calculation for durations
- [ ] Test metrics across operation types

**Health Checks:**
- [ ] Health check timeout scenarios
- [ ] Multiple checks with same name
- [ ] Large number of checks (100+)
- [ ] Non-boolean return values

**Thread Safety:**
- [ ] Concurrent operation registration
- [ ] Concurrent metrics recording
- [ ] Concurrent health check updates
- [ ] Data race detection

**Persistence:**
- [ ] Export to non-existent directory
- [ ] Disk full error handling
- [ ] File permission errors
- [ ] Reading/loading exported metrics

### 5. ANALYSIS.PY - Add ~30 tests

**DependencyAnalyzer:**
- [ ] map_dependencies() - basic dependency detection
- [ ] find_critical_path() - path through dependencies
- [ ] Circular dependency detection (when implemented)

**Risk Detection Edge Cases:**
- [ ] Negative effort values
- [ ] Very large effort values (>10000)
- [ ] Multiple risk conditions together
- [ ] Different status values

**MetricsCalculator:**
- [ ] Team velocity actual calculation
- [ ] Burndown with progress > 100%
- [ ] Burndown with progress < 0%
- [ ] Very large effort values

### 6. RESILIENCE.PY - Add ~25 tests

**Retry Timing:**
- [ ] Actual sleep verification (not just mocked)
- [ ] Exponential backoff with large attempts
- [ ] Custom backoff_multiplier values

**Rate Limiting:**
- [ ] Window boundary timing
- [ ] Clock skew handling
- [ ] Very short windows
- [ ] Very long retry_after values

**Error Handling:**
- [ ] Exception state modification
- [ ] Different exception types per retry
- [ ] SystemExit/KeyboardInterrupt handling

**Monitoring Integration:**
- [ ] Monitoring service unavailable
- [ ] Monitoring service exceptions
- [ ] Monitoring calls verify with actual service

### 7. JIRA_API_CLIENT.PY - Add ~15 tests

**Search Method:**
- [ ] Retry logic with exponential backoff
- [ ] Rate limit (429) handling verification
- [ ] Various HTTP status codes
- [ ] JSON parsing failures

**Story Fields:**
- [ ] Custom field ID extraction
- [ ] Story points as float/int
- [ ] Null/missing story points
- [ ] Multiple matching "story" fields

**Edge Cases:**
- [ ] Empty epic (no stories)
- [ ] Epic with 500+ stories (maxResults limit)
- [ ] Special characters in Jira keys
- [ ] Unexpected assignee formats

### 8. MARKDOWN_GENERATOR.PY - Add ~10 tests

**HTML Cleaning Edge Cases:**
- [ ] Multiple consecutive newlines
- [ ] Nested HTML tags
- [ ] Malformed HTML entities
- [ ] Very long text without HTML
- [ ] Mixed content types

**Boundary Conditions:**
- [ ] Empty objectives list
- [ ] Missing required fields
- [ ] Very long names (1000+ chars)
- [ ] Only special characters


---

## Summary of Effort Estimate

| Priority | Module | Current | Target | Add |
|----------|--------|---------|--------|-----|
| P1 | git_integration.py | 23 | 63 | +40 |
| P1 | api_client.py | 74 | 134 | +60 |
| P2 | change_tracker.py | 35 | 85 | +50 |
| P2 | monitoring.py | 21 | 56 | +35 |
| P3 | analysis.py | 26 | 56 | +30 |
| P3 | resilience.py | 25 | 50 | +25 |
| P4 | jira_api_client.py | 27 | 42 | +15 |
| P4 | markdown_generator.py | 97 | 107 | +10 |
| **TOTAL** | | **379** | **603** | **+224** |

**Total Test Addition Effort**: ~224 new tests
- P1 (Critical): 100 tests - 2-3 weeks
- P2 (High): 85 tests - 2 weeks
- P3 (Medium): 55 tests - 1-2 weeks
- P4 (Lower): 25 tests - 3-5 days

