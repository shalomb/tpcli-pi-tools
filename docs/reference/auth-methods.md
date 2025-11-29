# Reference: Authentication Methods

Complete reference for all TargetProcess authentication methods.

**Source**: [IBM TargetProcess API Authentication](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-authentication)

## Overview

TargetProcess supports three authentication methods:

| Method | Format | Recommended | Best For |
|--------|--------|-------------|----------|
| **Token** (Access Token) | `?access_token=token` | ✅ YES | Applications, automation, tpcli |
| **Basic Auth** | `Authorization: Basic base64(user:pass)` | ⚠️ Conditional | Scripts, testing |
| **Cookie** | Browser session | ⚠️ Limited | Browser mashups |

## Token Authentication (Recommended)

### Access Tokens (Personal Tokens)

**Supported Since**: TargetProcess v3.8.2+

**Characteristics**:
- User creates in UI
- Multiple tokens per user
- Password-independent
- Can be deleted anytime
- Displays creation date and last use

**How to Get**:
1. Log in to TargetProcess
2. My Profile > Access Tokens
3. Create New Token
4. Copy token immediately (shown once)

**How to Use**:

With tpcli:
```bash
export TP_TOKEN="your-access-token"
./tpcli list UserStories
```

With curl:
```bash
curl "https://instance.tpondemand.com/api/v1/UserStories?access_token=YOUR_TOKEN"
```

With HTTP header:
```
GET /api/v1/UserStories HTTP/1.1
Authorization: Bearer YOUR_TOKEN
```

### Legacy Service Tokens

**Characteristics**:
- Generated via `/api/v1/Authentication` endpoint
- Single token per user
- Expires when password changes
- Deprecated but still supported

**How to Get**:
```bash
curl -u username:password https://instance.tpondemand.com/api/v1/Authentication
```

Response:
```xml
<Authentication Token="YWRtaW46OTRDRDg2Qzg1Njg..."/>
```

**How to Use**:
```bash
curl "https://instance.tpondemand.com/api/v1/UserStories?token=YOUR_TOKEN"
```

## Basic Authentication

### Overview

Authentication via username:password in Authorization header.

**Format**:
```
Authorization: Basic base64(username:password)
```

**Example**:
```bash
# username: admin, password: admin
Authorization: Basic YWRtaW46YWRtaW4=
```

### Generate Base64

PowerShell:
```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('admin:admin'))
```

Bash:
```bash
echo -n "admin:admin" | base64
```

Online: Use any base64 encoder

### Usage

With curl (automatic encoding):
```bash
curl --user admin:admin https://instance.tpondemand.com/api/v1/UserStories/
```

With HTTP header:
```
GET /api/v1/UserStories HTTP/1.1
Authorization: Basic YWRtaW46YWRtaW4=
```

### Important Notes

⚠️ **Security**: Only use over HTTPS. Basic Auth sends base64-encoded credentials (not encrypted).

❌ **Not recommended** for:
- Single Sign-On (SSO) enabled instances
- Frontdoor authentication
- Production use without HTTPS

## Cookie Authentication

### Overview

Uses browser cookies from logged-in session.

**How It Works**:
1. User logs in via browser
2. Browser stores session cookie
3. JavaScript mashups automatically use cookie
4. API calls are authenticated

### Usage

**JavaScript Mashup** (same origin):
```javascript
$.getJSON('/api/v1/UserStories?include=[Id,Name]')
  .then(data => console.log(data.Items));
```

**Limitations**:
- Same-origin only (CORS restrictions)
- Not suitable for third-party applications
- Requires user to be logged in

## Authentication Errors

### Error: 401 Unauthorized

**Causes**:
1. Missing or invalid token
2. Expired credentials
3. User account inactive
4. Insufficient permissions

**Solution**:
```bash
# Check token is set
echo $TP_TOKEN

# Verify token is still valid in TP UI
# Settings > Access Tokens

# Create new token if needed
```

### Error: 401 for System User

**Cause**: System User doesn't have password set

**Solution**:
1. Go to TargetProcess Settings
2. System Settings > General Settings
3. Set System User Credentials password
4. Save changes

### Error: Windows Authentication Required

**Cause**: On-premises installation with NTLM authentication

**Solution**:
1. Enable Anonymous Authentication for `/api/` directory
2. Use NTLM instead of Basic Auth
3. Or use token-based authentication

## Comparison

### Credentials vs Passwords

| Aspect | Tokens | Passwords |
|--------|--------|-----------|
| Created by | User in UI | Set during registration |
| Multiple per user | ✅ Yes | ❌ No |
| Can disable without logout | ✅ Yes | ❌ No |
| Expires when password changes | ❌ No | N/A |
| Recommended | ✅ YES | ⚠️ Legacy |

### tpcli Support

With tpcli, you can use:
```bash
# Access Token (recommended)
export TP_TOKEN="access-token"

# Basic Auth (decode needed)
export TP_TOKEN="base64(username:password)"
```

## Best Practices

### For tpcli and Scripts

```bash
# Use access tokens
export TP_TOKEN="your-access-token"
export TP_URL="https://instance.tpondemand.com"
./tpcli list UserStories
```

### For Production

```bash
# Use environment variables, never hardcode
# In deployment script:
export TP_TOKEN="${TARGETPROCESS_TOKEN}"
# where TARGETPROCESS_TOKEN comes from secrets manager
```

### For CI/CD Pipelines

```bash
# Use dedicated CI token
# Store in: GitHub Secrets, GitLab CI Variables, Jenkins credentials, etc.
# Access in pipeline:
./tpcli list UserStories --token $CI_TP_TOKEN
```

### Security Checklist

- [ ] Using access tokens, not passwords
- [ ] Token stored in environment variable (not hardcoded)
- [ ] Token not committed to version control
- [ ] Regular token rotation policy
- [ ] Unused tokens deleted
- [ ] Using HTTPS (not HTTP)
- [ ] Minimal required permissions for token

## Related

- [tpcli Authentication Setup Tutorial](../tutorials/03-authentication-setup.md)
- [TargetProcess API Documentation](https://dev.targetprocess.com/docs)
- [API v1 Reference](api-v1-reference.md)
