# TargetProcess API Authentication Investigation

## Current Status

We have successfully:
✅ Built a working Go CLI tool (`tpcli`) with entity listing and discovery commands
✅ Connected to the TargetProcess API (https://takedamain.tpondemand.com)
✅ Identified correct API endpoints and query structure
❌ **Authentication failing with 401 Unauthorized**

## Authentication Error Details

```
Error: API error 401: One or more errors occurred.
(MixedAuthentication was unable to authenticate the user)
```

### What We Tried

1. **Token Format**: Using `$API_TOKEN` as-is in `Authorization: Basic` header
   - Token: `NDUwOkU1UUhmL1pWUm1Ld2RyYlBFbDl6OUtQVXd3OEFhTG54dGxXcEdNMk42RWc9`
   - Decoded: `450:E5QHf/ZVRmKwdrbPEl9z9KPUww8AaLnxtlWpGM2N6Eg=`
   - Format: `userId:apiToken` (already base64-encoded)

2. **HTTP Header Used**:
   ```
   Authorization: Basic NDUwOkU1UUhmL1pWUm1Ld2RyYlBFbDl6OUtQVXd3OEFhTG54dGxXcEdNMk42RWc9
   ```

## Possible Root Causes

1. **API Token Expired or Invalid**
   - The token may have been created for a different purpose
   - The token may have restricted permissions
   - The token may have expired

2. **Wrong Authentication Method**
   - Endpoint may require username/password instead of API token
   - Token format might be different than documented
   - May require Bearer token instead of Basic auth

3. **User Role/Permissions Issue**
   - User account (ID: 450) may not have API access
   - Account may be inactive or restricted

4. **API Key Format Mismatch**
   - The `TP_API_KEY` may expect a different format
   - May need to be `userId:rawToken` (without base64 encoding)

## Next Steps to Resolve

### Option A: Verify Token Format
```bash
# Try raw token (if base64-encoded token is wrong)
curl -H "Authorization: Basic 450:E5QHf/ZVRmKwdrbPEl9z9KPUww8AaLnxtlWpGM2N6Eg=" \
  https://takedamain.tpondemand.com/api/v1/Projects

# Or base64-encode the decoded format
echo -n "450:E5QHf/ZVRmKwdrbPEl9z9KPUww8AaLnxtlWpGM2N6Eg=" | base64
```

### Option B: Test with Username/Password
```bash
# Create new config with username/password
tpcli discover --username=YOUR_USERNAME --password=YOUR_PASSWORD
```

### Option C: Verify Token in TargetProcess UI
1. Go to https://takedamain.tpondemand.com
2. Settings > Access Tokens
3. Create a new API token or verify existing token
4. Ensure token has appropriate permissions
5. Test with fresh token

### Option D: Check Account Permissions
1. Log in as the user (ID 450)
2. Verify account is active
3. Verify API access is enabled for the account
4. Check if account has required permissions

## Related Code

- **CLI Implementation**: `/home/unop/shalomb/tpcli/`
- **MCP Reference**: `/home/unop/projects/aaronsb/apptio-target-process-mcp/`
- **Discovery Document**: `DISCOVERY.md`

## Command to Manually Test

```bash
# Setup
export TP_TOKEN="NDUwOkU1UUhmL1pWUm1Ld2RyYlBFbDl6OUtQVXd3OEFhTG54dGxXcEdNMk42RWc9"
export TP_URL="https://takedamain.tpondemand.com"

# Run discover
cd ~/shalomb/tpcli
./test-discover.sh

# Or use curl to test directly
curl -v -H "Authorization: Basic $TP_TOKEN" \
  "$TP_URL/api/v1/Projects?take=1"
```

## Architecture Notes

The authentication flow in our Go CLI mirrors the MCP server:

```
User Input (CLI flags/env vars)
    ↓
Config Parser (viper)
    ↓
TPClient.NewClient(baseURL, token, verbose)
    ↓
HTTP Request builder:
    req.Header.Set("Authorization", fmt.Sprintf("Basic %s", token))
    ↓
GET https://takedamain.tpondemand.com/api/v1/{EntityType}
```

## API Response Format (When Auth Works)

```json
{
  "Items": [
    {
      "Id": 12345,
      "Name": "Entity Name",
      "EntityState": {"Name": "Open"},
      ...
    }
  ]
}
```

## Files for Testing

- `~/shalomb/tpcli/test-discover.sh` - Test script with env vars
- `~/shalomb/tpcli/tpcli` - Compiled binary
- `~/shalomb/tpcli/cmd/discover.go` - Discovery command implementation
