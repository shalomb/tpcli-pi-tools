# Tutorial: Setting Up Authentication

Learn how to properly authenticate with the TargetProcess API.

**Time needed**: ~5 minutes
**Prerequisites**: TargetProcess account access

## Overview

tpcli supports three authentication methods:

1. **API Token** (Recommended) - Secure, user-specific
2. **Environment Variables** - Convenient for scripts
3. **Config File** - Convenient for permanent setup

## Get Your API Token

### Step 1: Log in to TargetProcess

Go to your instance:
```
https://takedamain.tpondemand.com
```

### Step 2: Access Token Settings

1. Click your profile (top right)
2. Select "My Profile" or "Settings"
3. Go to "Access Tokens" tab
4. Click "Create New Token"

### Step 3: Copy the Token

The token appears once after creation. Copy it immediately (you can't see it again).

**Format**: The token is base64-encoded and looks like:
```
NDUwOkU1UUhmL1pWUm1Ld2RyYlBFbDl6OUtQVXd3OEFhTG54dGxXcEdNMk42RWc9
```

## Configuration Methods

### Method 1: Environment Variables (Recommended for Scripts)

```bash
export TP_URL="https://takedamain.tpondemand.com"
export TP_TOKEN="your-api-token-here"

# Test
./tpcli discover
```

**Pros**: Secure, easy to manage in scripts, session-scoped
**Cons**: Need to set each terminal session

### Method 2: Config File (Recommended for Personal Use)

Create `~/.tpcli.yaml`:

```yaml
url: https://takedamain.tpondemand.com
token: your-api-token-here
verbose: false
```

Then use normally:
```bash
./tpcli list UserStories
```

**Pros**: Automatic, persistent
**Cons**: Credentials stored on disk

### Method 3: Command Line Flags (For One-Off Commands)

```bash
./tpcli list UserStories \
  --url https://takedamain.tpondemand.com \
  --token "your-api-token-here"
```

**Pros**: Explicit, good for temporary use
**Cons**: Credentials in shell history

## Priority Order

Config is loaded in this order (first found wins):

1. Command-line `--token` and `--url` flags
2. Environment variables `TP_TOKEN` and `TP_URL`
3. Config file `~/.tpcli.yaml`
4. Error if none found

## Test Your Setup

```bash
# Test discovery (shows available entities)
./tpcli discover -v

# List some items
./tpcli list Projects --take 1

# If you get JSON back, you're authenticated!
```

## Troubleshooting

### Error: "API token is required"

Means no auth config was found. Check:

```bash
# Check environment variables
echo $TP_TOKEN
echo $TP_URL

# Check config file
cat ~/.tpcli.yaml

# Try command-line approach
./tpcli list Projects --token "your-token" --url "https://takedamain.tpondemand.com"
```

### Error: "401 Unauthorized"

Token is recognized but rejected. Check:

1. Token is valid (hasn't been deleted in TP settings)
2. User account is active
3. You're using the right instance URL

**Solution**: Create a new token in TargetProcess UI

### Error: "MixedAuthentication was unable to authenticate"

This is currently blocking tpcli. See [API-AUTH-INVESTIGATION.md](../../API-AUTH-INVESTIGATION.md) for debugging.

## Security Best Practices

### DO:
- ✅ Keep tokens private like passwords
- ✅ Use environment variables for scripts
- ✅ Use config file for personal machines
- ✅ Regenerate tokens if compromised
- ✅ Use different tokens for different applications

### DON'T:
- ❌ Commit tokens to version control
- ❌ Share tokens with others
- ❌ Use in URLs visible in shell history
- ❌ Hardcode in production code
- ❌ Store in public repositories

## Advanced: Token Best Practices

### One Token Per Application

Create different tokens for:
- Local development (`dev-token`)
- CI/CD pipeline (`ci-token`)
- Third-party integrations (`integration-token`)

This way you can revoke one without affecting others.

### Rotate Tokens Periodically

1. Create new token in TP Settings
2. Update your config/scripts
3. Delete old token in TP Settings

### Monitor Token Usage

TargetProcess shows:
- When each token was created
- When it was last used
- You can delete unused tokens

---

**Next**: [Basic Queries Tutorial →](02-basic-queries.md)
