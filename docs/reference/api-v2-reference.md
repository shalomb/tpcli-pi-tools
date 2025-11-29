# Reference: API v2 - Advanced Query API

Complete reference for TargetProcess REST API v2.

**Source**: [IBM TargetProcess API v2](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v2-overview)

**Version**: v2
**Type**: Read-Only
**Formats**: JSON only

## Overview

API v2 is a **read-only** API with advanced filtering, querying, and projection capabilities.

**When to use**:
- ✅ Complex data queries
- ✅ Advanced filtering (OR, complex expressions)
- ✅ Custom projections and aggregations
- ❌ Creating or modifying entities (use v1 instead)

## Endpoint Format

```
GET /api/v2/{entity}/{id}?where={where}&select={select}&orderBy={order}&take={N}&skip={N}
```

## URL Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `where` | string | Filter expression | Advanced .NET expressions |
| `select` | string | Custom projection | `{id,name,project:{name}}` |
| `result` | string | Aggregation expression | `sum(effort)` |
| `orderBy` | string | Sort order | `effort desc,name` |
| `take` | int | Items per page | `take=50` |
| `skip` | int | Items to skip | `skip=25` |
| `filter` | string | DSL or simple filter | Board filter syntax |
| `prettify` | flag | Pretty JSON output | `prettify=true` |
| `isoDate` | flag | ISO 8601 dates | `isoDate=true` |
| `callback` | string | JSONP callback | `callback=myFunc` |

## Entity Names (Singular)

API v2 uses **singular** entity names:

| Type | API v1 | API v2 |
|------|--------|--------|
| User Stories | `/api/v1/UserStories` | `/api/v2/userstory` |
| Bugs | `/api/v1/Bugs` | `/api/v2/bug` |
| Tasks | `/api/v1/Tasks` | `/api/v2/task` |
| Features | `/api/v1/Features` | `/api/v2/feature` |
| Epics | `/api/v1/Epics` | `/api/v2/epic` |
| Projects | `/api/v1/Projects` | `/api/v2/project` |
| Users | `/api/v1/Users` | `/api/v2/user` |

## Select (Projection)

### Simple Projection

Get only specific fields:

```
/api/v2/userstory?select={id,name}

// Response
{
  "items": [
    {"id": 12345, "name": "Story Name"},
    ...
  ]
}
```

### Nested Projection

Get related entity fields:

```
/api/v2/userstory?select={
  id,
  name,
  project:{name,id},
  assignedUser:{firstName,lastName}
}

// Response
{
  "items": [
    {
      "id": 12345,
      "name": "Story Name",
      "project": {"name": "Project", "id": 100},
      "assignedUser": {"firstName": "John", "lastName": "Doe"}
    }
  ]
}
```

### Aliased Projection

Rename fields:

```
/api/v2/userstory?select={
  id,
  title:name,
  owner:owner.firstName,
  projectName:project.name
}
```

### Collection Projection

Get nested collections with custom fields:

```
/api/v2/project?select={
  id,
  name,
  stories:userstories.select({id,name,effort})
}
```

### Aggregation on Collections

Count, sum, average:

```
/api/v2/project?select={
  id,
  name,
  storyCount:userstories.count(),
  totalEffort:userstories.sum(effort),
  avgEffort:userstories.average(effort)
}
```

## Where (Advanced Filtering)

### Basic Comparison

```
/api/v2/bug?where=it.id > 1000

/api/v2/userstory?where=it.name == "Title"
```

**Note**: Use `==` or `=` for equality (different from v1 `eq`)

### Nested Property Access

```
/api/v2/userstory?where=it.project.id == 123

/api/v2/task?where=it.assignedUser.firstName == "John"
```

### Collection Filtering

```
// Items with bugs
/api/v2/userstory?where=it.bugs.any()

// Items with specific bug
/api/v2/userstory?where=it.bugs.any(x => x.id == 456)

// Items with opened bugs
/api/v2/userstory?where=it.bugs.any(x => x.entityState.name == "Open")
```

### Logical Operators

```
// AND
/api/v2/bug?where=it.id > 1000 AND it.name.contains("auth")

// OR
/api/v2/bug?where=it.priority.id == 1 OR it.priority.id == 2
```

### String Operations

```
// Contains
/api/v2/userstory?where=it.name.contains("login")

// Starts with
/api/v2/userstory?where=it.name.startsWith("Bug")

// Ends with
/api/v2/userstory?where=it.name.endsWith("done")

// Equals (case-sensitive)
/api/v2/userstory?where=it.name == "Exact Name"

// Not equals
/api/v2/userstory?where=it.name != "Exclude"
```

### Numeric Operations

```
// Greater than
/api/v2/userstory?where=it.effort > 5

// Less than or equal
/api/v2/task?where=it.timeRemain <= 0

// In range
/api/v2/task?where=it.effort >= 5 AND it.effort <= 10
```

### Null Checks

```
// Has value
/api/v2/userstory?where=it.description != null

// Is null
/api/v2/userstory?where=it.assignedUser == null
```

## OrderBy (Sorting)

### Single Field

```
// Ascending (default)
/api/v2/userstory?orderBy=name

// Descending
/api/v2/userstory?orderBy=createDate desc
```

### Multiple Fields

```
/api/v2/userstory?orderBy=priority.id desc,name
```

### Collection Sorting

```
/api/v2/project?select={
  id,
  name,
  stories:userstories.orderBy(effort).select({id,effort})
}
```

## Response Format

```json
{
  "next": "/api/v2/userstory?skip=25&take=25",
  "prev": "/api/v2/userstory?skip=0&take=25",
  "items": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
  ]
}
```

## Complex Example

Get projects with all user stories, showing:
- Project id, name
- Stories with id, name, effort
- Total effort for project
- Story count

```
/api/v2/project?select={
  id,
  name,
  totalEffort:userstories.sum(effort),
  storyCount:userstories.count(),
  stories:userstories
    .orderByDescending(effort)
    .select({id,name,effort})
}
```

## Key Differences from v1

| Aspect | v1 | v2 |
|--------|----|----|
| Read/Write | CRUD | Read-only |
| Entity names | Plural | Singular |
| Filtering | Simple | Advanced .NET |
| OR operator | ❌ No | ✅ Yes |
| Aggregations | Basic | Advanced |
| Projections | Limited | Flexible |
| Collection filters | ❌ No | ✅ Yes |
| Performance | Good | Better for complex queries |

## When to Use v1 vs v2

**Use v1 when**:
- Creating/updating entities
- Simple queries
- Familiar with TP API

**Use v2 when**:
- Read-only data extraction
- Complex filtering (OR, collection filters)
- Custom projections needed
- Aggregations (sum, count, etc)

## Examples

### Get all projects with their teams

```
/api/v2/project?select={id,name,teams:{id,name}}
```

### Count bugs by priority

```
/api/v2/project?select={
  id,
  name,
  critical:bugs.count(x => x.priority.name == "Critical"),
  high:bugs.count(x => x.priority.name == "High"),
  normal:bugs.count(x => x.priority.name == "Normal")
}
```

### Stories with no assignee

```
/api/v2/userstory?where=it.assignedUser == null
```

### Overdue tasks

```
/api/v2/task?where=
  it.entityState.name != "Done" AND
  it.endDate != null AND
  it.endDate < today()
```

## Related

- [API v1 Reference](api-v1-reference.md)
- [Query Syntax Reference](query-syntax.md)
- [TargetProcess Official v2 Docs](https://dev.targetprocess.com/docs/rest-api-v2)
