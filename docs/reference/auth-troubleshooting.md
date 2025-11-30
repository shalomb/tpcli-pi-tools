# TargetProcess API Authentication Investigation

## Current Status

✅ **All systems operational!**

We have successfully:
✅ Built a working Go CLI tool (`tpcli`) with entity listing and discovery commands
✅ Connected to the TargetProcess API (https://example.tpondemand.com)
✅ Identified correct API endpoints and query structure
✅ **FIXED: Authentication now working via query parameter method**

All commands (discover, list, get) are returning 200 OK and retrieving data.

## Solution: Query Parameter Authentication

### The Fix

The original implementation used Basic Authentication header:
```go
// BEFORE (Failed with 401)
req.Header.Set("Authorization", fmt.Sprintf("Basic %s", c.Token))
```

The fix uses query parameter authentication as documented in [IBM TargetProcess API v1 Authentication](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-authentication):

```go
// AFTER (Working - 200 OK)
q := req.URL.Query()
q.Add("access_token", c.Token)
req.URL.RawQuery = q.Encode()
```

### Why This Works

IBM TargetProcess API v1 supports multiple authentication methods:
1. **Query Parameter** (used by tpcli): `GET /api/v1/UserStories/?access_token={token}`
2. **Basic Auth Header** (also supported): `Authorization: Basic {base64(userId:token)}`
3. **Cookie Auth** (requires login session)

The query parameter method is simpler and doesn't require special encoding.

### What Changed in Code

File: `pkg/tpclient/client.go` - `doRequest()` method (lines 46-50)

```diff
  // Add authentication token as query parameter
- // Token is already base64 encoded in format expected by TargetProcess
- req.Header.Set("Authorization", fmt.Sprintf("Basic %s", c.Token))
+ // This is the recommended method per IBM TargetProcess documentation
+ q := req.URL.Query()
+ q.Add("access_token", c.Token)
+ req.URL.RawQuery = q.Encode()
```

### Test Results

All commands now work with 200 OK responses:

```bash
# Test discover - identifies all entity types
$ ./tpcli discover
✓ Projects: 1 item
✓ Epics: 1 item
✓ Features: 1 item
✓ UserStories: 1 item
✓ Bugs: 1 item

# Test list - returns filtered results
$ ./tpcli list UserStories --take 5
[{id: 2028653, name: "..."}, ...]

# Test get - retrieves individual entity
$ ./tpcli get Projects 222402
{id: 222402, name: "GDDT", effort: 72310.62, ...}
```

## How to Use Authentication

### Token Format

Your access token should be obtained from TargetProcess UI:
1. Log in to your TargetProcess instance
2. Go to Settings > Personal > Access Tokens
3. Create or copy an existing token
4. Use the raw token value (no base64 encoding needed)

### Configuration Methods

**1. Environment Variable** (Recommended for local development)
```bash
export TP_TOKEN="your_access_token_here"
export TP_URL="https://your-instance.tpondemand.com"
./tpcli discover
```

**2. Configuration File** (~/.tpcli.yaml)
```yaml
token: your_access_token_here
url: https://your-instance.tpondemand.com
```

**3. Command Line Flags**
```bash
./tpcli discover --token="your_access_token" --url="https://your-instance.tpondemand.com"
```

## Related Documentation

- [API v1 Reference](api-v1-reference.md) - Complete API documentation
- [Auth Methods Reference](auth-methods.md) - All authentication approaches
- [Query Syntax](query-syntax.md) - How to filter and query data

## Architecture Notes

The authentication flow in tpcli:

```
User Input (CLI flags/env vars/config file)
    ↓
Config Parser (viper)
    ↓
TPClient.NewClient(baseURL, token, verbose)
    ↓
HTTP Request builder:
    q.Add("access_token", token)
    req.URL.RawQuery = q.Encode()
    ↓
GET https://instance.tpondemand.com/api/v1/{EntityType}?access_token={token}
```

## API Response Format

```json
{
  "Items": [
    {
      "Id": 12345,
      "Name": "Entity Name",
      "EntityState": {"Name": "Open"},
      "CreateDate": "/Date(1764342238000-0500)/",
      ...
    }
  ],
  "Next": "/api/v1/UserStories?take=25&skip=25",
  "Prev": "/api/v1/UserStories?take=25&skip=0"
}
```

## Testing Authentication

Test your connection with the discover command:

```bash
./tpcli discover

# Expected output:
# Discovering Projects... ✓ Found 1 items
# Discovering Epics... ✓ Found 1 items
# ...
```

If you get 401 errors:
1. Verify token is valid in TargetProcess UI
2. Ensure token hasn't expired
3. Check that your user account has API access permissions
4. Try with a fresh token if issues persist
