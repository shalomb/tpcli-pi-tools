# Critical Test Gaps in API Client - Code Examples

## Overview
**File:** `tpcli_pi/core/api_client.py`  
**Priority:** These are the 27 CRITICAL paths affecting core functionality  
**Implementation Time:** 22 hours (8-10 hours per week for 3 weeks)

---

## CRITICAL GAP #1: Error Handling Not Tested (Lines 153-164)

### Current Code
```python
def _run_tpcli(
    self, entity_type: str, args: list[str] | None = None
) -> list[dict[str, Any]]:
    # ... build cmd ...
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        # ... extract JSON ...
    
    except subprocess.TimeoutExpired as e:  # <-- LINE 153-156: NOT TESTED
        raise TPAPIError(f"tpcli command timed out: {' '.join(cmd)}") from e
    
    except subprocess.CalledProcessError as e:  # <-- LINE 157-160: NOT TESTED
        raise TPAPIError(f"tpcli command failed: {' '.join(cmd)}\nstderr: {e.stderr}") from e
    
    except json.JSONDecodeError as e:  # <-- LINE 161-164: TESTED
        raise TPAPIError(f"Failed to parse tpcli JSON response: {e}\nRaw output: {output}") from e
```

### What's NOT Tested
1. **subprocess.TimeoutExpired** (line 153)
   - No test for 30-second timeout scenario
   - Recovery behavior undefined
   
2. **subprocess.CalledProcessError** (line 157)
   - stderr content handling not validated
   - Different error types (401, permission denied, invalid args) not distinguished

### Test Needed
```python
def test_run_tpcli_timeout_raises_error(self, client, mocker):
    """Test _run_tpcli raises TPAPIError on subprocess timeout."""
    import subprocess
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired("tpcli list Teams", timeout=30),
    )
    
    with pytest.raises(TPAPIError, match="timed out"):
        client._run_tpcli("Teams")

def test_run_tpcli_command_error_with_stderr(self, client, mocker):
    """Test _run_tpcli preserves stderr in error message."""
    import subprocess
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd="tpcli list Teams",
        stderr="Authentication failed: Invalid token"
    )
    mocker.patch("subprocess.run", side_effect=error)
    
    with pytest.raises(TPAPIError) as exc_info:
        client._run_tpcli("Teams")
    
    assert "Invalid token" in str(exc_info.value)
```

**Impact:** HIGH - Network timeouts and permission errors are production scenarios

---

## CRITICAL GAP #2: Query Filter Combinations (Lines 281-287)

### Current Code - get_program_pi_objectives()
```python
def get_program_pi_objectives(
    self, art_id: int | None = None, release_id: int | None = None
) -> list[ProgramPIObjective]:
    args: list[str] | None = None
    
    if art_id is not None:
        args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]
    
    if release_id is not None:
        where = f"Release.Id eq {release_id}"
        if args:  # <-- CRITICAL: When both filters provided
            where = f"AgileReleaseTrain.Id eq {art_id} and {where}"
            args = ["--where", where]
        else:
            args = ["--where", where]
    
    # ... rest of method ...
```

### What's NOT Tested
1. **Both art_id AND release_id provided**
   - WHERE clause: `"AgileReleaseTrain.Id eq X and Release.Id eq Y"`
   - Test exists but doesn't validate actual WHERE string
   - Does tpcli accept AND syntax? Never verified
   
2. **Line 284 builds WHERE clause twice**
   - First assignment at line 280
   - Second assignment at line 285 (overwrites if release_id provided)
   - Logic is correct but untested combinations

### Test Needed
```python
def test_get_program_pi_objectives_with_both_filters(self, client, mocker):
    """Test WHERE clause when both art_id AND release_id provided."""
    mock_data = [{"Id": 1, "Name": "Objective"}]
    mock_run = mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
    
    objs = client.get_program_pi_objectives(art_id=100, release_id=10)
    
    # Verify WHERE clause built correctly
    called_args = mock_run.call_args
    where_clause = called_args[1][1][1]  # Extract args list's where clause
    assert "AgileReleaseTrain.Id eq 100" in where_clause
    assert "Release.Id eq 10" in where_clause
    assert " and " in where_clause
    assert objs == [client._parse_program_objective(mock_data[0])]
```

**Impact:** HIGH - Incorrect filters return wrong data

---

## CRITICAL GAP #3: Cache Poisoning (Lines 187-191)

### Current Code - _get_cached()
```python
def _get_cached(self, entity_type: str, args: list[str] | None = None) -> list[dict[str, Any]] | None:
    key = self._cache_key(entity_type, args)
    
    if key not in self._cache:
        self._cache_stats["misses"] += 1
        return None
    
    # Check if cache has expired
    cache_time = self._cache_timestamps.get(key, 0)  # <-- LINE 187: POISONING VECTOR
    if time() - cache_time > self.cache_ttl:
        # Cache expired, remove it
        del self._cache[key]  # <-- What if next line fails?
        del self._cache_timestamps[key]  # <-- Then key in _cache but not timestamps!
        self._cache_stats["evictions"] += 1
        self._cache_stats["misses"] += 1
        return None
    
    # Cache hit
    self._cache_stats["hits"] += 1
    return self._cache[key]
```

### What's NOT Tested
1. **Cache poisoning scenario:**
   - Key exists in `_cache` but NOT in `_cache_timestamps`
   - Line 187: `cache_time = self._cache_timestamps.get(key, 0)` returns 0
   - Line 188: `time() - 0 > cache_ttl` is ALWAYS true
   - Entry deleted on next access
   - **Data loss without error**

2. **Race condition in eviction:**
   - If first `del` succeeds, second fails
   - _cache[key] remains, _cache_timestamps[key] gone
   - Next access hits poisoning scenario

### Test Needed
```python
def test_cache_poisoning_scenario(self, client):
    """Test cache entry without timestamp is treated as expired."""
    # Manually create poisoned cache state
    key = "Teams:--where"
    client._cache[key] = [{"Id": 1}]
    # Intentionally missing: client._cache_timestamps[key]
    
    # get_cached should return None (expired), not the cached data
    result = client._get_cached("Teams", ["--where"])
    assert result is None
    
    # Cache should be cleaned up
    assert key not in client._cache
    assert client._cache_stats["evictions"] == 1

def test_cache_eviction_del_race_condition(self, client, mocker):
    """Test cache consistency if del fails during eviction."""
    key = "Teams:"
    client._cache[key] = [{"Id": 1}]
    client._cache_timestamps[key] = time.time() - 100  # Expired
    
    # Mock the first del to succeed, second to fail
    original_del = dict.__delitem__
    call_count = [0]
    
    def mock_del(d, k):
        call_count[0] += 1
        if call_count[0] == 2:  # Second del fails
            raise RuntimeError("Simulated del failure")
        original_del(d, k)
    
    with patch.object(dict, "__delitem__", mock_del):
        # Should handle the error gracefully
        with pytest.raises(RuntimeError):
            client._get_cached("Teams")
        
        # State should be consistent
        assert key not in client._cache or key not in client._cache_timestamps
```

**Impact:** CRITICAL - Silent data loss in cached reads

---

## CRITICAL GAP #4: Dangerous Date Defaults (Lines 398-399)

### Current Code - _parse_release()
```python
def _parse_release(self, data: dict[str, Any]) -> Release:
    start_date = self._parse_tp_date(data.get("StartDate"))  # Could be None
    end_date = self._parse_tp_date(data.get("EndDate"))      # Could be None
    
    return Release(
        id=data.get("Id", 0),
        name=data.get("Name", ""),
        start_date=start_date or datetime.now(),  # <-- LINE 398: DANGEROUS DEFAULT
        end_date=end_date or datetime.now(),      # <-- LINE 399: DANGEROUS DEFAULT
        # ... other fields ...
    )
```

### What's NOT Tested
1. **Both dates None:**
   - `start_date = datetime.now()`
   - `end_date = datetime.now()` (same second)
   - Release duration = 0 seconds (invalid)
   - No validation that end_date > start_date

2. **StartDate invalid, EndDate valid:**
   - `start_date = None` → defaults to `now()`
   - `end_date = datetime(2025, 1, 1)`
   - If called at future time, `start_date > end_date` (backwards!)

3. **Clock skew:**
   - System clock is wrong
   - `now()` is past the release's real end_date
   - Calculations based on these dates are invalid

### Test Needed
```python
def test_parse_release_with_both_dates_missing(self, client, mocker):
    """Test release with both dates None gets same fallback (0 duration)."""
    data = {
        "Id": 10,
        "Name": "PI-4/25",
        # StartDate and EndDate missing
    }
    
    # Mock now() to return fixed time
    mock_now = datetime(2025, 6, 15, 12, 0, 0)
    with patch("tpcli_pi.core.api_client.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        
        release = client._parse_release(data)
        
        # Both dates should be now()
        assert release.start_date == mock_now
        assert release.end_date == mock_now
        assert (release.end_date - release.start_date).total_seconds() == 0

def test_parse_release_start_date_after_end_date(self, client, mocker):
    """Test release where start_date > end_date (invalid state)."""
    data = {
        "Id": 10,
        "Name": "PI-4/25",
        "StartDate": None,  # Will default to now()
        "EndDate": "/Date(1609459200000-0500)/",  # Jan 1, 2021 (past)
    }
    
    release = client._parse_release(data)
    
    # CRITICAL: start_date (now) > end_date (past)
    assert release.start_date > release.end_date
    # This should be caught and handled, or raise error
    # Currently silently accepted (BUG)
```

**Impact:** CRITICAL - Invalid date relationships cause logic errors downstream

---

## CRITICAL GAP #5: Bulk Operation Partial Failures (Lines 914-916)

### Current Code - bulk_create_team_objectives()
```python
def bulk_create_team_objectives(self, objectives: list[dict[str, Any]]) -> list[TeamPIObjective]:
    # Documentation says: "Raises TPAPIError: If any creation fails (atomic - none are created)"
    
    # ... build payloads ...
    
    created = []
    for payload in payloads:
        response_list = self._run_tpcli_create("TeamPIObjective", payload)  # <-- LINE 915
        created.append(response_list[0])  # If this fails on iteration 2:
    # created = [obj1] (not rolled back)
    
    # Update cache with all new items
    cached = self._get_cached("TeamPIObjectives")
    if cached is None:
        cached = []
    cached.extend(created)  # <-- LINE 922: Partial data committed to cache!
    self._set_cached("TeamPIObjectives", cached)
    
    return [self._parse_team_objective(item) for item in created]
```

### What's NOT Tested
1. **Partial failure on iteration 2:**
   - Objective 1 created successfully: `created = [obj1]`
   - Objective 2 fails with TPAPIError
   - Exception propagates
   - Cache now has partial data, but error says "none were created"
   - **Atomicity violated**

2. **No input validation:**
   - Loop assumes `obj["name"]` exists
   - If missing: `KeyError` not caught
   - No try/except around payload building

### Test Needed
```python
def test_bulk_create_partial_failure_is_not_atomic(self, client, mocker):
    """Test that bulk create is NOT actually atomic (partial failure allowed)."""
    # Mock: First create succeeds, second fails
    responses = [
        [{"Id": 100, "Name": "Obj1"}],  # First succeeds
    ]
    
    def mock_create(entity_type, payload):
        if len(responses) == 1:
            return responses[0]
        # Second call raises error
        raise TPAPIError("API error: invalid effort")
    
    mocker.patch.object(client, "_run_tpcli_create", side_effect=mock_create)
    
    objectives_to_create = [
        {"name": "Obj1", "team_id": 1, "release_id": 10},
        {"name": "Obj2", "team_id": 1, "release_id": 10},
    ]
    
    with pytest.raises(TPAPIError):
        client.bulk_create_team_objectives(objectives_to_create)
    
    # PROBLEM: Cache has partial data
    cached = client._get_cached("TeamPIObjectives")
    assert cached is not None and len(cached) == 1
    # Documentation says "atomic - none are created" but cache has 1!
    # This is a DATA CONSISTENCY BUG
```

**Impact:** CRITICAL - Data consistency violation, cache gets corrupted

---

## CRITICAL GAP #6: Null/Empty Field Handling (Lines 363-365, 398-399)

### Current Code - _parse_team()
```python
def _parse_team(self, data: dict[str, Any]) -> Team:
    owner = None
    if "Owner" in data and data["Owner"]:  # <-- UNTESTED: data["Owner"] = None
        owner = self._parse_user(data["Owner"])
    
    return Team(
        id=data.get("Id", 0),
        name=data.get("Name", ""),
        owner=owner,
        member_count=data.get("Members", {}).get("length", 0)
            if isinstance(data.get("Members"), dict)
            else 0,
        # ... other fields ...
    )
```

### What's NOT Tested
1. **Owner = None** (key exists, value is None)
   - `"Owner" in data` is True
   - `data["Owner"]` is None (falsy)
   - Condition passes first check but fails second
   - Result: `owner = None` (correct, but not tested)

2. **Owner = {}** (empty dict)
   - Both conditions pass
   - Calls `_parse_user({})`
   - Result: User with all empty fields
   - Never tested this path

3. **Members = {}** (empty dict)
   - Line `isinstance(data.get("Members"), dict)` is True
   - `.get("length", 0)` returns 0 (missing key)
   - But what if `Members = {"length": "5"}` (string)?
   - Result: `member_count = "5"` (string, not int!)

### Test Needed
```python
def test_parse_team_with_owner_null(self, client):
    """Test parsing team where Owner key exists but value is None."""
    data = {
        "Id": 1,
        "Name": "Team A",
        "Owner": None,  # <-- Key exists, value is None
    }
    
    team = client._parse_team(data)
    
    assert team.owner is None  # Should be None
    assert team.id == 1

def test_parse_team_with_empty_owner(self, client):
    """Test parsing team with empty Owner dict."""
    data = {
        "Id": 1,
        "Name": "Team A",
        "Owner": {},  # <-- Empty dict
    }
    
    team = client._parse_team(data)
    
    assert team.owner is not None  # Parsed to User object
    assert team.owner.id == 0
    assert team.owner.first_name == ""

def test_parse_team_with_invalid_members_type(self, client):
    """Test parsing team with invalid Members value type."""
    data = {
        "Id": 1,
        "Name": "Team A",
        "Members": {"length": "5"},  # <-- String, not int
    }
    
    team = client._parse_team(data)
    
    # PROBLEM: member_count is "5" (string) not 5 (int)
    assert isinstance(team.member_count, int)
    assert team.member_count == 5  # Should coerce to int
```

**Impact:** HIGH - Type inconsistencies cause downstream errors

---

## Summary: Most Critical Gaps to Fix First

| Gap | Lines | Impact | Effort | Fix Priority |
|-----|-------|--------|--------|--------------|
| Error handling timeouts | 153-156 | HIGH | 1 hour | 1 |
| Query filter combinations | 281-287 | HIGH | 2 hours | 2 |
| Cache poisoning | 187-191 | CRITICAL | 2 hours | 1 |
| Date logic errors | 398-399 | CRITICAL | 1.5 hours | 1 |
| Bulk partial failures | 914-916 | CRITICAL | 2 hours | 1 |
| Null field handling | 363-365 | HIGH | 3 hours | 2 |

**Total for Critical Path:** 11.5 hours (4 days)

---

Generated: 2025-12-02
