# API Client Untested Code Paths and Edge Cases Analysis

**File:** `/home/unop/shalomb/tpcli/tpcli_pi/core/api_client.py`

**Current Test Coverage:** 74 tests covering ~65% of the module (7.3% ratio)

**Total Identified Gaps:** 79+ untested code paths and edge cases

---

## PRIORITY 1: HIGHEST IMPACT (Critical to test immediately)

### 1. Error Handling in Core subprocess Methods

#### A. `_run_tpcli()` - Lines 100-165
**Status:** Partial error handling exists but many paths untested

**Untested Exception Paths:**
- **Lines 153-156:** `subprocess.TimeoutExpired` - 30-second timeout scenario
  - When subprocess.run() exceeds 30 seconds
  - No test simulates actual timeout behavior
  - Recovery/fallback behavior undefined

- **Lines 157-160:** `subprocess.CalledProcessError` - when tpcli command fails
  - stderr content parsing not tested
  - Complex error messages with newlines not handled
  - Example: permission denied, missing credentials, invalid command

- **Lines 161-164:** `json.JSONDecodeError` - malformed JSON response
  - Valid JSON start found but incomplete JSON string
  - Invalid characters in JSON after array marker
  - Mixed text and JSON (incomplete extraction)

**Untested Data Extraction (Lines 136-145):**
- Output with `[` found at position 50+, then `{` - which takes precedence?
- Output with neither `[` nor `{` - error at line 143 is tested
- Edge case: output is whitespace + `[` with only whitespace inside brackets
- Metadata with brackets: e.g., "Querying [Resource 1]" before actual JSON

**Recommendation:** Add 8-10 tests covering:
1. Actual TimeoutExpired exception
2. CalledProcessError with various stderr formats
3. JSONDecodeError at different positions in JSON
4. Mixed bracket types (`[` and `{`)
5. Malformed JSON (missing closing bracket)

---

#### B. `_run_tpcli_create()` - Lines 513-573
**Status:** Same error handling as _run_tpcli

**Untested Exception Paths (identical to _run_tpcli):**
- Lines 561-564: TimeoutExpired timeout handling
- Lines 565-568: CalledProcessError - validation errors from API
- Lines 569-572: JSONDecodeError - malformed response JSON

**Key Difference from _run_tpcli:**
- Only expects single object response (line 559)
- No array handling
- Error when response is array instead of object - NOT TESTED

**Recommendation:** Add 8-10 tests for create-specific scenarios

---

#### C. `_run_tpcli_update()` - Lines 574-643
**Status:** Identical to _run_tpcli_create

**Untested Exception Paths:**
- Lines 631-634: TimeoutExpired
- Lines 635-638: CalledProcessError
- Lines 639-642: JSONDecodeError

**Additional Untested:**
- Invalid entity_id handling (does API return 404? tested at line 300 but not in update itself)
- What if entity_id is 0 or negative? (edge case parameter validation)

---

### 2. Query Filter Combinations (Complex WHERE clause building)

#### A. `get_program_pi_objectives()` - Lines 274-294
**Current Tests:** Lines 922-947 cover individual filters

**UNTESTED Combinations:**
1. **Both art_id AND release_id provided** (Lines 281-287)
   ```python
   if art_id is not None:
       args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]
   if release_id is not None:
       where = f"Release.Id eq {release_id}"
       if args:  # <-- This logic: combines with AND
           where = f"AgileReleaseTrain.Id eq {art_id} and {where}"
           args = ["--where", where]
       else:
           args = ["--where", where]
   ```
   
   **BUG POTENTIAL:** When both are provided:
   - Does the WHERE clause build correctly? Test shows assumption but no actual verification
   - Order matters: "A eq X and B eq Y" vs "B eq Y and A eq X"
   - Does tpcli accept AND syntax?

2. **Boundary case:** release_id with art_id=None (line 281 condition)
   - Should only check `if release_id is not None`
   - Does it correctly build single-filter query?

3. **Zero/negative IDs** (edge case, not explicit)
   - What if art_id=-1, release_id=0?
   - API behavior undefined, but should handle gracefully

**Test Gap:** No single test with BOTH art_id and release_id parameters set

---

#### B. `get_team_pi_objectives()` - Lines 296-321
**Current Tests:** Lines 949-965 cover individual and multiple filters

**UNTESTED Filter Combinations:**
1. **All three filters together:** team_id, art_id, release_id (3-way)
   - Test at line 964 checks "all three" but with missing data checks - real WHERE clause not validated
   
2. **Two-filter combinations:**
   - team_id + art_id (no release_id)
   - team_id + release_id (no art_id)
   - art_id + release_id (no team_id)
   - None of these 3 combinations explicitly tested

3. **WHERE clause building** (Lines 313-314):
   ```python
   if where_clauses:
       args = ["--where", " and ".join(where_clauses)]
   ```
   - String joining with " and " is straightforward but:
   - What if one where_clause is empty? (shouldn't happen but defensive programming)
   - What if where_clause contains " and " itself? (injection concern)

---

#### C. `get_features()` - Lines 323-348
**Current Tests:** Lines 967-1001 cover individual filters

**UNTESTED Combinations:**
1. **All three filters:** team_id + release_id + parent_epic_id
   - Test at line 1000 checks two, not three together
   
2. **Parent epic with team:** Can same feature belong to multiple teams?
   - Filter interaction not tested
   
3. **Release + epic:** Do epics span releases?
   - Expected behavior undefined in tests

---

### 3. Network Error Scenarios

#### `_run_tpcli()` and create/update variants
**CURRENTLY TESTED:** TimeoutExpired, CalledProcessError, JSONDecodeError

**NOT TESTED:**
1. **Connection refused** (subprocess returns specific error code)
   - CalledProcessError exists but specific scenarios differ
   
2. **Authentication failures**
   - stderr contains "401 Unauthorized" or "Invalid token"
   - How is this distinguished from other errors?
   - No separate handling - all wrapped in TPAPIError

3. **DNS resolution failures**
   - tpcli might fail before even attempting connection
   
4. **SSL/TLS certificate errors**
   - HTTPS requests might fail with cert validation error
   - tpcli delegates to underlying HTTP client

5. **Partial responses** (subprocess outputs partial JSON before failing)
   - Lines 136-145 extract first `[` or `{`
   - If response is `[partial, {` - which marker wins?
   - Leads to JSONDecodeError, but scenario not explicitly tested

**Recommendation:** Add 6-8 tests for realistic network scenarios

---

## PRIORITY 2: HIGH IMPACT (Important edge cases)

### 4. Null/Empty Field Handling in Parse Methods

#### A. `_parse_team()` - Lines 361-381
**Current Tests:** Lines 1034-1071 cover most cases

**UNTESTED Edge Cases:**
1. **Owner = None** (line 363-365)
   - Explicitly tested: `"Owner" in data and data["Owner"]`
   - NOT tested: `data["Owner"] = None` (key exists but value is None)
   
2. **Owner = {} (empty dict)**
   - Parses to User but with all empty fields
   - Semantically different from None but same handling

3. **Members field variations:**
   - `Members = None` (tested at line 1068)
   - `Members = {}` (empty dict - get() returns None from missing "length")
   - `Members = {"length": null}` (null value)
   - `Members = {"length": "5"}` (string instead of int)

4. **AgileReleaseTrain = None** (line 375)
   - Key exists but value is None
   - Returns None from get() but isinstance check fails gracefully
   - Test doesn't cover this exact case

5. **Empty string fields:**
   - `Name = ""` (valid but semantically wrong)
   - `IsActive = ""` (falsy) vs `IsActive = null` vs missing

---

#### B. `_parse_release()` - Lines 390-407
**CRITICAL ISSUE: Dangerous date defaults** (Lines 398-399)
```python
start_date=start_date or datetime.now(),
end_date=end_date or datetime.now(),
```

**Current Tests:** Lines 1080-1104 cover some cases

**UNTESTED Danger Scenarios:**
1. **Both dates None:**
   - start_date and end_date both default to `now()`
   - Results in 0-second duration release
   - No validation that end_date > start_date
   
2. **StartDate invalid, EndDate valid:**
   - start_date falls back to now() - might be AFTER end_date!
   - Test line 1103 assumes this is acceptable but doesn't verify ordering

3. **Clock skew/time travel:**
   - If system clock is wrong, now() can be past/future of real dates
   - No safeguard

4. **AgileReleaseTrain missing/None:**
   - Gracefully returns None for art_id and "" for art_name
   - NOT tested: AgileReleaseTrain = {} vs None vs missing

**Recommendation:** Add 5-6 tests including:
- Date ordering validation
- Null/empty ART handling
- Type validation for numeric fields

---

#### C. `_parse_program_objective()` - Lines 409-441
**Current Tests:** Lines 1106-1137

**UNTESTED Edge Cases:**
1. **Owner with partial data:**
   - `Owner = {"Id": 123}` (missing FirstName, LastName, Email)
   - Test doesn't set incomplete owner data
   
2. **Release = None vs Release = {}:**
   - Test doesn't distinguish

3. **Effort = 0 or negative:**
   - No validation, just stored
   - Semantically wrong but accepted

4. **All date fields missing:**
   - start_date, end_date, created_date all None
   - Result has 3 None date fields
   - Workable but untested combination

5. **Description = None** (explicitly untested)

---

#### D. `_parse_team_objective()` - Lines 443-474
**Current Tests:** Lines 1138-1157

**UNTESTED Edge Cases:**
1. **Team = None vs Team = {}:**
   - Both cases not explicitly tested together

2. **Committed field variations:**
   - `Committed = null` (None)
   - `Committed = 0` (falsy)
   - `Committed = false` (vs default True)

3. **Missing Status field:**
   - Defaults to "Pending" (line 456)
   - Test doesn't verify missing field handling

---

#### E. `_parse_feature()` - Lines 476-509
**Current Tests:** Lines 1159-1187

**UNTESTED Edge Cases:**
1. **Team nested parsing:**
   - `Team = {}` (empty dict) - would pass isinstance check
   - Calls `_parse_team({})` - recursively parses empty team
   - Not tested: what happens with deeply nested empty objects?

2. **Parent epic with null ID:**
   - `Parent = {"Id": null}` vs `Parent = {"Name": "Epic"}` (missing Id)

3. **Status, Effort defaults:**
   - Missing fields tested but combinations not

---

### 5. Caching Edge Cases

#### A. `_get_cached()` - Lines 171-198
**Current Tests:** Lines 711-797 cover basic TTL

**UNTESTED Edge Cases:**
1. **Cache poisoning:**
   - Key exists in `_cache` but NOT in `_cache_timestamps`
   - Line 187 does `get()` with default 0
   - Entry is considered "expired" immediately (time() - 0 > TTL always true)
   - Data loss but no error!

2. **Cache eviction race condition:**
   - Line 190-191: del both keys
   - What if deletion of _cache_timestamps fails? (del statement)
   - _cache key remains, causing inconsistency

3. **Boundary timing:**
   - Entry at exactly TTL seconds old
   - Entry at TTL - 1ms (should hit)
   - Entry at TTL + 1ms (should evict)
   - Current test uses `time.sleep(1.1)` with 1-second TTL (line 730)
   - Timing can be flaky on slow systems

4. **Large cache performance:**
   - Test doesn't stress 1000+ cached entries
   - get() still O(1) but stats increment is O(1) - fine
   - But hit_rate calculation (line 989-990) could overflow with large counts

5. **Concurrent access:**
   - Multiple threads calling get_cached simultaneously
   - Not tested - no thread locks

---

#### B. Cache Updates in Create/Update Methods

**create_team_objective() - Lines 690-695:**
```python
objectives = self._get_cached("TeamPIObjectives")
if objectives is None:
    objectives = []
objectives.append(response)
self._set_cached("TeamPIObjectives", objectives)
```

**UNTESTED Scenarios:**
1. **Cache was fetched with filter, now updating with unfiltered key:**
   - `_get_cached("TeamPIObjectives", None)` returns None
   - Creates new list with 1 item
   - But what if cache had "TeamPIObjectives:--where Team.Id eq 1"?
   - Unfiltered cache created, filtered cache stays out of sync!

2. **Multiple concurrent creates:**
   - Thread 1: gets cached = [obj1]
   - Thread 2: gets cached = [obj1]
   - Thread 1: appends obj2, sets cache
   - Thread 2: appends obj3, sets cache → obj2 lost!

3. **Append to immutable list:**
   - If response was empty list [], append([obj]) works
   - But if somehow immutable, append raises error

---

### 6. Bulk Operations Error Handling

#### `bulk_create_team_objectives()` - Lines 867-925
**Current Tests:** Lines 553-663 cover success path

**UNTESTED Error Scenarios:**
1. **Partial failure:**
   ```python
   for payload in payloads:
       response_list = self._run_tpcli_create(...)  # Line 915
       created.append(response_list[0])
   ```
   - If 2nd iteration fails with TPAPIError
   - `created = [obj1]` is not rolled back
   - Cache now has partial data: `cached.extend(created)` (line 922)
   - Documentation says "atomic - none are created" but code doesn't guarantee this!

2. **Empty payloads list:**
   - Lines 889-890 tested
   - But test doesn't verify cache is untouched

3. **Payload validation:**
   - Loops assume each obj has required fields
   - If `obj["name"]` missing → KeyError
   - No exception handling

---

#### `bulk_update_team_objectives()` - Lines 927-974
**UNTESTED Error Scenarios:**
1. **Same partial failure as bulk_create**

2. **Update ID set generation (line 968):**
   ```python
   updated_ids = {u.get("Id") for u in updated}
   ```
   - If u.get("Id") returns None, set contains None
   - Later filter: `if c.get("Id") not in updated_ids`
   - If cache has {"Id": None}, it's incorrectly removed!

3. **Cache consistency after filter:**
   - Line 969: removes old versions BEFORE adding new
   - If add fails, cache loses data without replacement

---

## PRIORITY 3: MEDIUM IMPACT (Important but less critical)

### 7. Rate Limiting (NOT IMPLEMENTED)

**Critical Issue:** api_client.py has NO rate limiting logic at all

**Current Behavior:**
- All rate limiting delegated to subprocess (tpcli)
- No detection of rate limit responses from API (429 status, etc.)
- No backoff/retry logic in Python layer
- No tracking of API call frequency

**Test Gap:** 
- Cannot test rate limiting in api_client since none exists
- Should document dependency on tpcli for rate limit handling
- Or implement rate limiting in Python layer (recommended)

---

### 8. _parse_tp_date() Edge Cases - Lines 72-98

**Current Tests:** Lines 807-844 cover main cases

**UNTESTED Edge Cases:**
1. **Timezone offset edge cases:**
   - `/Date(0+0000)/` (epoch, UTC)
   - `/Date(1000000000000+1400)/` (Line Islands, +14:00)
   - `/Date(1000000000000-1200)/` (Baker Island, -12:00)

2. **Millisecond precision:**
   - `/Date(1738450043001-0500)/` vs `/Date(1738450043000-0500)/`
   - Difference of 1ms - test doesn't validate this

3. **ISO format edge cases:**
   - `2025-12-31T23:59:59Z` (end of year)
   - `2025-01-01T00:00:00+00:00` vs `2025-01-01T00:00:00Z` (different representation)
   - Both should parse to same datetime

4. **Malformed but partially valid:**
   - `/Date(notanumber-0500)/` - regex matches but int() fails
   - Not caught by current regex but would cause ValueError

5. **Very large millisecond values:**
   - `/Date(9999999999999-0500)/` - year 5138
   - `datetime.fromtimestamp()` might overflow

---

### 9. Query Filter Parameter Validation

**Missing validation (implicit test gap):**

All query methods accept any integer for ID parameters:
```python
def get_teams(self, art_id: int | None = None) -> list[Team]:
```

**UNTESTED Parameter Validation:**
1. **Negative IDs:** `get_teams(art_id=-1)`
   - WHERE clause becomes `AgileReleaseTrain.Id eq -1`
   - Probably returns no results, but never tested

2. **Zero IDs:** `get_teams(art_id=0)`
   - Same as above

3. **Very large IDs:** `get_teams(art_id=999999999999999)`
   - WHERE clause builds but API returns nothing
   - Untested edge case

4. **Type coercion:**
   - Type hints say `int | None` but Python doesn't enforce at runtime
   - Could pass float `get_teams(art_id=1.5)` → WHERE clause has `1.5` (invalid)

---

## PRIORITY 4: LOWER IMPACT (Nice to have)

### 10. get_*_by_name() Methods

#### `get_team_by_name()` - Lines 245-251
#### `get_art_by_name()` - Lines 224-230
#### `get_release_by_name()` - Lines 266-272

**Current Tests:** Lines 877-897 partially cover

**UNTESTED Cases:**
1. **Case sensitivity:**
   - Test doesn't try different cases: "Team A" vs "team a"
   - Comparison is exact (`art.name == name`)
   - API might return different case than expected

2. **Whitespace handling:**
   - `get_team_by_name("Team A ")` (trailing space)
   - Test doesn't strip whitespace

3. **Multiple matches:**
   - What if API returns duplicate names?
   - Returns first match only (implicit behavior)
   - Not tested that duplicates return first

4. **Unicode/special characters:**
   - `get_team_by_name("Équipe Élite")`
   - Not tested

---

### 11. Initialization and Configuration

#### `__init__()` - Lines 34-70

**UNTESTED Scenarios:**
1. **Credential priority:**
   - Documentation says: constructor params > config file > env vars
   - Test doesn't verify priority order
   - Only tests with defaults

2. **tp_url validation:**
   - Accepts any string: `tp_url="not-a-url"`
   - No validation of URL format
   - Only validated at runtime when tpcli uses it

3. **tp_token validation:**
   - Accepts any string: `tp_token=""`
   - No validation of base64 encoding
   - No validation of token format

4. **Cache TTL bounds:**
   - Accepts any integer: `cache_ttl=-1` or `cache_ttl=0`
   - No validation
   - Negative TTL means entries always expired
   - Zero TTL means entries always expired

---

## Summary Table: Untested Code Paths by Severity

| Severity | Category | Methods | Gap Count | Test Effort |
|----------|----------|---------|-----------|------------|
| **Critical** | Error handling (try/except) | _run_tpcli, _run_tpcli_create, _run_tpcli_update | 8-12 | 4-5 hours |
| **Critical** | Query filter combinations | get_program_pi_objectives, get_team_pi_objectives, get_features | 8-10 | 3-4 hours |
| **Critical** | Cache edge cases | _get_cached, create/update cache logic | 10-12 | 4-5 hours |
| **High** | Null/empty field handling | All _parse_* methods | 15-18 | 4-5 hours |
| **High** | Bulk operation errors | bulk_create/bulk_update | 6-8 | 2-3 hours |
| **High** | Network error scenarios | All subprocess methods | 6-8 | 2-3 hours |
| **Medium** | Date parsing edge cases | _parse_tp_date | 5-6 | 1-2 hours |
| **Medium** | Parameter validation | All query methods | 4-6 | 1-2 hours |
| **Low** | get_*_by_name methods | get_team_by_name, etc. | 4-6 | 1-2 hours |
| **Not Applicable** | Rate limiting | (not implemented) | 0 | N/A |

**TOTAL IDENTIFIED GAPS:** 79 untested code paths and edge cases
**ESTIMATED TEST EFFORT:** 22-35 hours (60-100 new tests)
**RECOMMENDED EXECUTION:** Weeks 1-2 of development cycle

---

## Recommended Test Implementation Order

1. **Week 1 - Critical paths (20-25 tests):**
   - Error handling in _run_tpcli, _run_tpcli_create, _run_tpcli_update
   - Query filter combinations
   - Cache TTL boundary conditions

2. **Week 2 - High-impact edge cases (20-25 tests):**
   - Null/empty field parsing
   - Bulk operation error handling
   - Network error scenarios

3. **Week 2-3 - Medium-priority (15-20 tests):**
   - Date parsing edge cases
   - Parameter validation
   - get_*_by_name edge cases

