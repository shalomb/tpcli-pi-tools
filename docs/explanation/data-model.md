# TargetProcess Data Model & Access Patterns

## Entity Hierarchy

TargetProcess uses a hierarchical work item structure:

```
Project (top-level container)
├── Release (version)
│   └── Iteration (sprint/cycle)
│       └── Epic (major initiative)
│           └── Feature (user story)
│               ├── Task (work item)
│               └── Bug (defect)
│
└── Team
    ├── User (team member)
    └── Process definitions
```

## Entity Types Reference

### Work Items (Assignable)

These entities can be assigned to users and have state transitions:

| Type | API Name | Description | Parent | ID Example |
|------|----------|-------------|--------|-----------|
| **Epic** | `Epics` | Major business initiative | Project | 5555673480067962920 |
| **Feature** | `Features` | User story or feature | Epic | 1940304, 1938766 |
| **User Story** | `UserStories` | User-facing functionality | Epic/Feature | 1938771 |
| **Task** | `Tasks` | Unit of work | User Story | - |
| **Bug** | `Bugs` | Defect or issue | Epic/Feature | - |

### Container Entities

| Type | API Name | Description |
|------|----------|-------------|
| **Project** | `Projects` | Top-level organization |
| **Iteration** | `Iterations` | Sprint, cycle, or milestone |
| **Release** | `Releases` | Version release |
| **Team** | `Teams` | Team grouping |
| **User** | `Users` | Person/team member |

### Metadata Entities

| Type | API Name | Description |
|------|----------|-------------|
| **EntityState** | `EntityStates` | Work item status (Open, In Progress, Closed) |
| **Priority** | `Priorities` | Priority levels |
| **Severity** | `Severities` | Bug severity |
| **CustomField** | `CustomFields` | Custom attributes |

## Core Properties

All entities have these base properties:

```json
{
  "Id": 12345,
  "Name": "Entity Name",
  "Description": "Detailed description",
  "CreateDate": "2024-01-15T10:30:00",
  "ModifyDate": "2024-11-29T18:45:00",
  "Owner": {
    "Id": 100,
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john@example.com"
  },
  "Project": {
    "Id": 1000,
    "Name": "Project Name"
  },
  "EntityState": {
    "Name": "Open",
    "Id": 1
  }
}
```

### Work Item Specific Properties

```json
{
  "AssignedUser": {
    "Id": 101,
    "FirstName": "Jane",
    "LastName": "Smith"
  },
  "Priority": {
    "Name": "High",
    "Id": 5
  },
  "Tags": ["bug", "urgent", "backend"],
  "Effort": 8,
  "TimeSpent": 5,
  "TimeRemaining": 3,
  "Parent": {
    "Id": 1938771,
    "Name": "Parent User Story"
  },
  "Children": [
    {
      "Id": 1938772,
      "Name": "Child Task"
    }
  ],
  "CustomFields": {
    "RiskLevel": "Medium",
    "Component": "Authentication"
  }
}
```

## Query Patterns

### List All Items of a Type

```bash
tpcli list UserStories --take 100
```

### Filter by Status

```bash
# Open items
tpcli list Bugs --where "EntityState.Name eq 'Open'"

# Items in specific project
tpcli list Features --where "Project.Id eq 1234"

# Items assigned to user
tpcli list Tasks --where "AssignedUser.Id eq 456"

# High priority
tpcli list Bugs --where "Priority.Name eq 'High'"
```

### Filter by Dates

```bash
# Created in last 7 days
tpcli list UserStories --where "CreateDate gt '2024-11-22'"

# Modified today
tpcli list Tasks --where "ModifyDate ge '2024-11-29' and ModifyDate lt '2024-11-30'"
```

### Complex Filters

```bash
# Open bugs in critical project (chaining with AND)
tpcli list Bugs \
  --where "EntityState.Name eq 'Open' and Project.Id eq 1234 and Priority.Name eq 'High'"

# Items in current sprint
tpcli list UserStories \
  --where "Iteration.IsCurrent eq 'true'"

# Search by text
tpcli list UserStories \
  --where "Name contains 'authentication'"
```

### Include Related Data

```bash
# Get items with related owners and projects
tpcli list UserStories \
  --fields "Id,Name,Owner,Project,EntityState,AssignedUser,Tags"

# For deeper nesting
--fields "Id,Name,Owner[FirstName,LastName],Project[Name]"
```

## Common Query Examples

### Dashboard Use Case: Show My Open Tasks

```bash
# Get user ID first
tpcli list Users --where "Email eq 'john@example.com'" --take 1

# Then list their tasks
tpcli list Tasks \
  --where "AssignedUser.Id eq {userId} and EntityState.Name eq 'Open'" \
  --fields "Id,Name,Priority,TimeRemaining,Project"
```

### Backlog Use Case: Epic with All Descendants

```bash
# Get epic
tpcli get Epics 5555673480067962920 \
  --fields "Id,Name,Description,Owner,Children"

# Get all features in epic
tpcli list Features \
  --where "Parent.Id eq 5555673480067962920" \
  --take 200
```

### Release Planning Use Case: Iteration Burndown

```bash
# Get iteration tasks
tpcli list Tasks \
  --where "Iteration.Id eq {iterationId}" \
  --fields "Id,Name,EntityState,Effort,TimeSpent,AssignedUser" \
  --take 500
```

### Status Tracking Use Case: Open Issues by Project

```bash
tpcli list Bugs \
  --where "EntityState.Name eq 'Open'" \
  --fields "Id,Name,Project,Priority,AssignedUser,CreateDate" \
  --take 1000
```

## State Transitions

### Typical Work Item States

```
Open → In Progress → Testing → Closed
  ↓_____________________↑__________|
        (blocked)
```

Common state names:
- `Open` - Not started
- `In Progress` - Actively being worked
- `Testing` - Under QA review
- `In Review` - Code/design review
- `Blocked` - Waiting on dependency
- `Done` / `Closed` - Completed

## Entity Type Discovery

### List Available Entity Types

```bash
tpcli discover
```

This will show:
- Which entity types are available
- Sample properties for each
- Response format

### Get Details about Entity Type

```bash
tpcli inspect {EntityType}
```

Example:
```bash
tpcli inspect UserStories
```

Shows:
- All possible fields
- Field types and constraints
- Relationships
- Available actions

## Relationships & Includes

### Parent-Child Relationships

```
Epic
  ├── Feature
  │   ├── Task
  │   └── Bug
  └── Feature
```

Query with includes:
```bash
tpcli list Epics \
  --fields "Id,Name,Children[Id,Name,EntityState]"
```

### User Relationships

```json
{
  "Owner": {...},           // Original creator
  "AssignedUser": {...},    // Currently assigned
  "ModifiedBy": {...}       // Last modifier
}
```

## Pagination

Default: `take=25`, `skip=0`

```bash
# First page
tpcli list Features --take 50 --skip 0

# Second page
tpcli list Features --take 50 --skip 50

# All items (caution with large result sets)
tpcli list Features --take 1000 --skip 0
```

## Performance Tips

1. **Use `take` parameter** - Don't fetch all items unnecessarily
2. **Filter early** - Use `--where` to reduce result set
3. **Select fields** - Use `--fields` to get only needed data
4. **Avoid deep includes** - Nested includes can slow queries
5. **Check pagination** - Handle large result sets in batches

## Common Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid token | Verify API token in TP Settings |
| 400 Bad Request | Malformed query | Check `--where` clause syntax |
| 404 Not Found | Entity doesn't exist | Verify entity ID |
| 429 Too Many Requests | Rate limited | Add delays between requests |
| 500 Server Error | Server issue | Retry after delay |

## Links & References

- **TargetProcess Instance**: https://takedamain.tpondemand.com
- **API Documentation**: https://dev.targetprocess.com/docs
- **API v1 Reference**: https://dev.targetprocess.com/docs/rest-getting-started
- **Query Syntax**: https://dev.targetprocess.com/docs/rest-filtering
- **Entity Reference**: https://dev.targetprocess.com/docs/entities
