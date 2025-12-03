# Discovering TargetProcess Entity Types

## Problem Statement

New users don't know what arguments to pass to `tpcli list`. They see:
```bash
$ tpcli list
Error: accepts 1 arg(s), received 0
Usage:
  tpcli list <entity-type> [flags]
```

But they don't know what entity types are available or what they can query.

## Solution: Discovery Commands

There are three ways to discover what you can query:

### 1. Quick List: `tpcli list --help` (Shows Examples)

```bash
$ tpcli list --help
```

This shows common entity types in the examples:
- UserStories
- Bugs
- Tasks
- Features

### 2. Full Discovery: `tpcli discover` (Interactive Discovery)

```bash
$ tpcli discover
```

This connects to your TargetProcess instance and discovers:
- All available entity types
- How many items of each type you have
- What fields/properties exist for each type
- Sample data from each type

**Example output:**
```json
{
  "Projects": {
    "status": "ok",
    "count": 5,
    "fields": ["Id", "Name", "Description", ...],
    "sample": { ... }
  },
  "Teams": {
    "status": "ok",
    "count": 8,
    "fields": ["Id", "Name", "TeamLead", ...],
    "sample": { ... }
  },
  ...
}
```

### 3. Help Text: `tpcli list <ENTITY-TYPE> --help`

```bash
$ tpcli list Features --help
```

Shows what filtering and field options are available for that entity type.

## Common Entity Types

These are the most commonly queried entity types in TargetProcess:

| Entity Type | What It Is | Example Query |
|---|---|---|
| **Projects** | Top-level project containers | `tpcli list Projects` |
| **Teams** | Agile teams within projects | `tpcli list Teams` |
| **Releases** | PI/Release cycles | `tpcli list Releases` |
| **Iterations** | Sprints/iterations | `tpcli list Iterations` |
| **Features** | Epics and features | `tpcli list Features` |
| **UserStories** | User stories and work items | `tpcli list UserStories` |
| **Bugs** | Bug reports | `tpcli list Bugs` |
| **Tasks** | Tasks and work | `tpcli list Tasks` |
| **Epics** | Epic-level features | `tpcli list Epics` |

## Getting Started

### Step 1: Discover Your Data

```bash
$ tpcli discover
```

This tells you what data exists in your TP instance.

### Step 2: Query an Entity Type

```bash
# List all projects
tpcli list Projects

# List all teams
tpcli list Teams --take 50

# List features with specific fields
tpcli list Features --fields Id,Name,Status
```

### Step 3: Filter and Refine

```bash
# List features in specific state
tpcli list Features --where "EntityState.Name eq 'Open'"

# List teams in specific project
tpcli list Teams --where "Project.Id eq 1234"

# Combine filters
tpcli list UserStories --where "Team.Id eq 5678 and EntityState.Name eq 'In Progress'"
```

## Query Syntax

### Basic Filters

```bash
# Equality
tpcli list Features --where "EntityState.Name eq 'Open'"

# Comparison
tpcli list UserStories --where "Effort gt 5"

# Text search
tpcli list Features --where "Name contains 'API'"
```

### Complex Filters

```bash
# AND conditions
tpcli list UserStories --where "Team.Id eq 5 and EntityState.Name eq 'Open'"

# Multiple conditions
tpcli list Features --where "Effort gt 10 and Status eq 'Backlog'"
```

### Field Selection

```bash
# Specific fields only
tpcli list Teams --fields Id,Name,TeamLead

# All fields (default)
tpcli list Teams
```

### Pagination

```bash
# First 50 items
tpcli list Projects --take 50

# Skip first 100, take 50
tpcli list Projects --skip 100 --take 50
```

## Workflow: From Discovery to Query

1. **Start with discovery:**
   ```bash
   tpcli discover
   ```
   Find what entity types exist and what data you have.

2. **List basic entity:**
   ```bash
   tpcli list Features --take 10
   ```
   See what data looks like for an entity type.

3. **Filter by state:**
   ```bash
   tpcli list Features --where "EntityState.Name eq 'Open'" --take 10
   ```
   Find items in a specific state.

4. **Add field selection:**
   ```bash
   tpcli list Features \
     --where "EntityState.Name eq 'Open'" \
     --fields Id,Name,Owner,Effort \
     --take 10
   ```
   Get just the fields you care about.

5. **Export or process:**
   ```bash
   tpcli list Features \
     --where "EntityState.Name eq 'Open'" \
     --fields Id,Name,Owner,Effort | \
     grep -v "^#" | tee my-features.txt
   ```
   Export for further processing.

## Tips

- Start with `tpcli discover` to understand your data
- Use `--take 10` to preview before getting all data
- Use `--fields` to reduce output noise
- Use `--where` to filter to relevant items
- Combine with `tpcli ext` scripts for higher-level analysis

## Related Commands

- `tpcli discover` - Discover entity types and structure
- `tpcli list <entity-type>` - Query entities
- `tpcli ext` - Run analysis scripts (higher-level views)

See [API Reference](../reference/query-syntax.md) for complete query syntax.
