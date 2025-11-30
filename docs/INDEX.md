# tpcli Project Index

## 📋 Documentation

Start here based on your role:

### For API Users (Using tpcli)
1. **[README.md](README.md)** - Quick start and command reference
2. **[DATA-MODEL.md](DATA-MODEL.md)** - Entity types and query patterns
3. **[API-AUTH-INVESTIGATION.md](API-AUTH-INVESTIGATION.md)** - Authentication troubleshooting

### For Developers (Extending tpcli)
1. **[PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)** - Architecture and structure
2. **[DISCOVERY.md](DISCOVERY.md)** - API endpoint reference
3. Source code:
   - `main.go` - Entry point
   - `cmd/` - CLI command implementations
   - `pkg/tpclient/` - API client library

### For TargetProcess API Learning
1. **[DISCOVERY.md](DISCOVERY.md)** - TP entity types and API basics
2. **[DATA-MODEL.md](DATA-MODEL.md)** - Entity relationships and state
3. **[API-AUTH-INVESTIGATION.md](API-AUTH-INVESTIGATION.md)** - Auth details

## 🗂️ Project Structure

```
~/shalomb/tpcli/
│
├── Source Code
│   ├── main.go                    Entry point
│   ├── cmd/
│   │   ├── root.go               Global config & authentication
│   │   ├── discover.go           Entity discovery command
│   │   ├── list.go               List/filter entities command
│   │   └── get.go                Get single entity command
│   └── pkg/
│       └── tpclient/
│           └── client.go         TargetProcess API client
│
├── Documentation
│   ├── INDEX.md                  📍 You are here
│   ├── README.md                 Quick start guide
│   ├── PROJECT-SUMMARY.md        High-level overview
│   ├── DISCOVERY.md              API reference
│   ├── DATA-MODEL.md             Entity model & queries
│   └── API-AUTH-INVESTIGATION.md Auth troubleshooting
│
├── Configuration Files
│   ├── go.mod / go.sum           Go dependencies
│   ├── .tpcli.yaml.example       Config file template
│   ├── .gitignore                Git ignore rules
│
├── Tools & Scripts
│   ├── tpcli                     Compiled binary
│   ├── test-discover.sh          Test script
│
└── Reference
    └── ../projects/aaronsb/apptio-target-process-mcp/  MCP server reference
```

## 🚀 Quick Commands

### Build
```bash
cd ~/shalomb/tpcli
go build -o tpcli
```

### Test
```bash
./test-discover.sh    # Test connectivity
./tpcli discover -v   # Discover entities
./tpcli list Projects # List items
./tpcli get UserStory 1938771  # Get one item
```

### Develop
```bash
./tpcli discover --help         # See options
go run main.go discover         # Run without building
```

## 📚 Document Guide

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **README.md** | Usage instructions | First time using tpcli |
| **PROJECT-SUMMARY.md** | Architecture overview | Understanding structure |
| **DISCOVERY.md** | TP API reference | Learning TP API |
| **DATA-MODEL.md** | Entity relationships | Building queries |
| **API-AUTH-INVESTIGATION.md** | Auth debugging | When auth fails |
| **INDEX.md** (this) | Navigation | Orienting yourself |

## 🔍 Finding Things

### How do I...?

**Run a command?**
→ See [README.md](README.md) - Command Reference section

**Understand entity types?**
→ See [DISCOVERY.md](DISCOVERY.md) - Entity Model section

**Write a query filter?**
→ See [DATA-MODEL.md](DATA-MODEL.md) - Query Patterns section

**Fix authentication error?**
→ See [API-AUTH-INVESTIGATION.md](API-AUTH-INVESTIGATION.md)

**Add a new command?**
→ See [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md) - Development section

**Understand code structure?**
→ See [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md) - Architecture section

## 🔗 Key Links

- **Project Root**: `~/shalomb/tpcli/`
- **TP Instance**: https://example.tpondemand.com
- **TP API Docs**: https://dev.targetprocess.com/docs
- **MCP Reference**: `~/projects/aaronsb/apptio-target-process-mcp/`

## 📊 Current Status

✅ **Completed**
- CLI framework (Cobra)
- Configuration system
- API client
- Commands: discover, list, get
- Documentation

❌ **Blocked**
- API authentication (401 error)
- See: API-AUTH-INVESTIGATION.md

⏳ **Future**
- Create/Update operations
- Comment management
- Time logging

## 🤔 Help & Support

### Common Issues

**Can't find `tpcli` command?**
```bash
cd ~/shalomb/tpcli && go build -o tpcli
./tpcli discover
```

**Getting 401 Unauthorized?**
→ Check [API-AUTH-INVESTIGATION.md](API-AUTH-INVESTIGATION.md)

**Don't know which command to use?**
```bash
./tpcli --help
./tpcli discover --help
./tpcli list --help
```

**Want to understand the code?**
→ Start with [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)

## 📝 Last Updated

November 29, 2025

## 🎓 Learning Path

### Beginner (Just using tpcli)
1. [README.md](README.md)
2. Run `./test-discover.sh`
3. Try basic commands

### Intermediate (Understanding TP API)
1. [DISCOVERY.md](DISCOVERY.md)
2. [DATA-MODEL.md](DATA-MODEL.md)
3. Write custom queries

### Advanced (Extending tpcli)
1. [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)
2. Study source code
3. Add new commands

---

**Next Step**: Read [README.md](README.md) to get started!
