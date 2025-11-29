# Tutorial: Getting Started with tpcli

Learn how to install, configure, and run your first tpcli commands.

**Time needed**: ~10 minutes

## Prerequisites

- Go 1.20 or later (or download the compiled binary)
- TargetProcess account access
- TargetProcess API token (see [Authentication Setup](03-authentication-setup.md))

## Step 1: Get tpcli

### Option A: Use the compiled binary
```bash
cd ~/shalomb/tpcli
./tpcli --help
```

### Option B: Build from source
```bash
cd ~/shalomb/tpcli
go build -o tpcli
./tpcli --help
```

## Step 2: Configure Authentication

Set environment variables:
```bash
export TP_URL="https://takedamain.tpondemand.com"
export TP_TOKEN="your-api-token"
```

(For detailed auth setup, see [Authentication Setup Tutorial](03-authentication-setup.md))

## Step 3: Test the Connection

Run the discover command to test your connection:
```bash
./tpcli discover -v
```

Expected output:
```
Attempting to discover TargetProcess instance...

Discovering Projects... (no errors = good!)
Discovering Epics...
...
```

## Step 4: Run Your First Query

List user stories:
```bash
./tpcli list UserStories --take 5
```

You should see JSON output with user story data.

## Step 5: Explore More

Try these commands:
```bash
# List bugs
./tpcli list Bugs --take 10

# Get details of one entity
./tpcli get UserStory 1938771

# See all available options
./tpcli discover --help
```

## What's Next?

- [Basic Queries Tutorial](02-basic-queries.md) - Learn more query options
- [How to List & Filter](../how-to/list-and-filter.md) - Advanced filtering
- [Entity Types Reference](../reference/entity-types.md) - See what you can query

## Troubleshooting

### Error: "API token is required"
→ Set `TP_TOKEN` environment variable (see Step 2)

### Error: "401 Unauthorized"
→ Your token may be invalid. See [Authentication Setup](03-authentication-setup.md)

### Error: "startIndex cannot be larger than length of string"
→ This is an API error. Check your `--where` filter syntax

### Binary not found
→ Run `go build -o tpcli` in Step 1 (Option B)

---

**Next**: [Basic Queries Tutorial →](02-basic-queries.md)
