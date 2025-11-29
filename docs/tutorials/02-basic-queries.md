# Tutorial: Basic Queries with tpcli

Learn how to query different entity types and use basic options.

**Time needed**: ~15 minutes
**Prerequisites**: Complete [Getting Started](01-getting-started.md)

## List Different Entity Types

TargetProcess has many entity types you can query:

### Work Items
```bash
# User Stories
./tpcli list UserStories --take 10

# Bugs
./tpcli list Bugs --take 10

# Tasks
./tpcli list Tasks --take 10

# Features
./tpcli list Features --take 10

# Epics
./tpcli list Epics --take 10
```

### Containers
```bash
# Projects
./tpcli list Projects --take 10

# Iterations (sprints)
./tpcli list Iterations --take 10

# Releases
./tpcli list Releases --take 10
```

### People
```bash
# Users/team members
./tpcli list Users --take 10

# Teams
./tpcli list Teams --take 10
```

## Query with Pagination

Control how many results you get:

```bash
# Get 50 items instead of default 25
./tpcli list UserStories --take 50

# Skip first 25, get next 25 (page 2)
./tpcli list UserStories --take 25 --skip 25

# Get all first page items
./tpcli list UserStories --take 1000
```

## Select Specific Fields

Reduce data transfer by requesting only needed fields:

```bash
# Get only Id and Name
./tpcli list UserStories --fields "Id,Name" --take 10

# Get more detailed information
./tpcli list UserStories \
  --fields "Id,Name,Owner,Project,EntityState" \
  --take 10
```

## View Single Entity Details

Get all information about one item:

```bash
./tpcli get UserStory 1938771
./tpcli get Bug 12345
./tpcli get Project 9876
```

## Basic Filtering

Filter results by status:

```bash
# Open bugs only
./tpcli list Bugs \
  --where "EntityState.Name eq 'Open'" \
  --take 25

# Done stories only
./tpcli list UserStories \
  --where "EntityState.Name eq 'Done'" \
  --take 25
```

## Combine Options

Use multiple options together:

```bash
# Open bugs in specific project, show selected fields, limit results
./tpcli list Bugs \
  --where "Project.Id eq 1234" \
  --fields "Id,Name,Priority,EntityState" \
  --take 50
```

## Discover Available Entities

Find out what you can query:

```bash
./tpcli discover
```

This shows all available entity types and sample fields.

## Output Formats

Results are always JSON. Pretty-printed for readability:

```json
{
  "Items": [
    {
      "Id": 12345,
      "Name": "Entity Name",
      "Description": "...",
      ...
    }
  ]
}
```

You can pipe to tools like `jq` for further processing:
```bash
./tpcli list UserStories --take 5 | jq '.Items[].Name'
```

## Common Entity Fields

Most entities have these fields:

| Field | Meaning |
|-------|---------|
| `Id` | Unique identifier |
| `Name` | Entity name/title |
| `Description` | Detailed text |
| `CreateDate` | When created |
| `ModifyDate` | Last modification |
| `Owner` | Creator user |
| `Project` | Parent project |
| `EntityState` | Current status (Open, In Progress, etc) |

Work items (UserStories, Bugs, Tasks) also have:

| Field | Meaning |
|-------|---------|
| `AssignedUser` | Who it's assigned to |
| `Priority` | Work item priority |
| `Effort` | Estimated work |
| `TimeSpent` | Hours worked |
| `Parent` | Parent item |

## What's Next?

- [Advanced Filtering](../how-to/list-and-filter.md) - Complex queries
- [Work with Related Data](../how-to/work-with-nested-entities.md) - Include related entities
- [Query Syntax Reference](../reference/query-syntax.md) - All operators

---

**Continue**: [Advanced Filtering →](../how-to/list-and-filter.md)
