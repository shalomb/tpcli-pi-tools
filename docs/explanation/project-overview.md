# tpcli - TargetProcess CLI Project Summary

**Status**: ✅ MVP Complete (Authentication debugging required)

## What is tpcli?

A lightweight command-line interface for interacting with the TargetProcess (Apptio) REST API built in Go. Enables scripting, automation, and programmatic access to TP work items, projects, and related entities.

## What We've Built

```
tpcli/
├── src code/
│   ├── cmd/          (CLI commands)
│   │   ├── discover.go   (Discover entities and structure)
│   │   ├── get.go        (Fetch single entity)
│   │   ├── list.go       (Query & filter entities)
│   │   └── root.go       (Config & auth management)
│   └── pkg/          (Libraries)
│       └── tpclient/ (TP API client)
│
├── Documentation/
│   ├── README.md                      (Quick start)
│   ├── DISCOVERY.md                   (Entity types & API basics)
│   ├── DATA-MODEL.md                  (Entity relationships & queries)
│   ├── API-AUTH-INVESTIGATION.md      (Auth debugging guide)
│   └── PROJECT-SUMMARY.md             (This file)
│
├── Tools/
│   ├── tpcli                         (Compiled binary)
│   └── test-discover.sh              (Test script)
│
└── Config/
    ├── .tpcli.yaml.example
    ├── .gitignore
    ├── go.mod
    └── go.sum
```

## Quick Start

### Build

```bash
cd ~/shalomb/tpcli
go build -o tpcli
```

### Configure

**Option A: Environment Variables** (Recommended)
```bash
export TP_URL="https://example.tpondemand.com"
export TP_TOKEN="your-api-token"
```

**Option B: Config File**
```bash
cp .tpcli.yaml.example ~/.tpcli.yaml
# Edit ~/.tpcli.yaml with credentials
```

**Option C: Command Line**
```bash
tpcli discover --url https://example.tpondemand.com --token YOUR_TOKEN
```

### Basic Commands

```bash
# Discover available entities
./tpcli discover

# List user stories
./tpcli list UserStories --take 10

# Get specific entity
./tpcli get UserStory 1938771

# Filter items
./tpcli list Bugs --where "EntityState.Name eq 'Open'" --take 25

# Include related data
./tpcli list Features --fields "Id,Name,Owner,Project,AssignedUser" --take 50
```

## Current Status

### ✅ Completed

- [x] Go CLI framework with Cobra
- [x] Configuration management (flags, env vars, config file)
- [x] TargetProcess API client with proper HTTP handling
- [x] Entity listing with filtering and pagination
- [x] Entity details (get by ID)
- [x] Entity discovery/introspection
- [x] Comprehensive documentation
- [x] Test connectivity script
- [x] Error handling and logging

### 🔴 Blocking Issue: Authentication

The API returns `401 Unauthorized: MixedAuthentication was unable to authenticate the user`

**See `API-AUTH-INVESTIGATION.md` for debugging steps**

Possible causes:
- API token format mismatch
- Token invalid or expired
- Account permissions issue
- Wrong endpoint or API version

### ⏳ Future Features (Blocked on Auth)

- [ ] Create/Update entity operations
- [ ] Comment management
- [ ] Time logging
- [ ] Bulk operations
- [ ] Export to CSV/JSON files
- [ ] Template-based creation
- [ ] Integration with CI/CD

## Key Files

| File | Purpose |
|------|---------|
| `main.go` | Entry point |
| `cmd/root.go` | Global config & auth |
| `cmd/discover.go` | Entity discovery command |
| `cmd/list.go` | List/filter command |
| `cmd/get.go` | Fetch single entity |
| `pkg/tpclient/client.go` | API client library |
| `README.md` | User guide |
| `DISCOVERY.md` | API reference |
| `DATA-MODEL.md` | Entity relationships |
| `API-AUTH-INVESTIGATION.md` | Troubleshooting |
| `test-discover.sh` | Test script |

## Architecture

```
User Input (CLI flags/env vars)
    ↓
Root Command (config & auth setup)
    ↓
Subcommand (discover/list/get)
    ↓
tpclient.Client (HTTP layer)
    ↓
TargetProcess API
    ↓
JSON Response Parsing
    ↓
User Output (formatted JSON/errors)
```

## Knowledge Transfer

### For TP API Understanding
- Start with: `DISCOVERY.md`
- Reference: `DATA-MODEL.md`
- Troubleshooting: `API-AUTH-INVESTIGATION.md`

### For Code Understanding
- Start with: `main.go` → `cmd/root.go`
- Commands: `cmd/*.go`
- API Client: `pkg/tpclient/client.go`

### For Development
- Build: `go build -o tpcli`
- Test: `./test-discover.sh`
- Add new command: `cmd/newcommand.go`

## Lessons Learned

1. **TargetProcess API is RESTful** but requires:
   - Proper Base64-encoded authentication
   - Specific `Authorization: Basic` header format
   - Correct entity type names (UserStories, not UserStory plural)

2. **Entity Model**:
   - Hierarchical (Epic → Feature → Task/Bug)
   - Supports filtering with rich query syntax
   - Includes related entities via `include` parameter

3. **Auth Format**:
   - Takes form: `Authorization: Basic {token}`
   - Token is `base64(userId:apiToken)`
   - Each TP instance has different API tokens

## MCP Server Reference

The project in `/home/unop/projects/aaronsb/apptio-target-process-mcp/` provides:
- Comprehensive API auth/client implementation
- Entity type definitions
- Semantic operations (business logic)
- Error handling patterns
- Test suite examples

Our Go implementation draws architectural patterns from this project.

## Next Steps

To get tpcli working:

1. **Verify API Token**
   - Check TP instance Settings → Access Tokens
   - Create new token if needed
   - Confirm token has API permissions

2. **Test Authentication**
   - Run: `./test-discover.sh`
   - Check error response from server
   - Try with different token formats

3. **Debug & Fix**
   - Check `API-AUTH-INVESTIGATION.md`
   - Run curl tests manually
   - Compare with MCP server approach

4. **Enable Full Operations**
   - Once auth works, add Create/Update tools
   - Implement time logging
   - Add comment management

## Support & Resources

- **Project Location**: `~/shalomb/tpcli/`
- **MCP Reference**: `~/projects/aaronsb/apptio-target-process-mcp/`
- **TP Documentation**: https://dev.targetprocess.com/docs
- **Go Cobra Docs**: https://cobra.dev/

## Technical Stack

- **Language**: Go 1.20+
- **CLI Framework**: Cobra
- **Configuration**: Viper
- **HTTP Client**: net/http (standard library)
- **JSON Parsing**: encoding/json (standard library)
- **Build**: Go build system

## License & Attribution

Inspired by the Apptio TargetProcess MCP Server project:
https://github.com/aaronsb/apptio-target-process-mcp

Licensed under MIT (see LICENSE file if present)
