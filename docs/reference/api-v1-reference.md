# Reference: API v1 - REST API

Complete reference for TargetProcess REST API v1.

**Source**: [IBM TargetProcess REST API v1](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-getting-started)

**Version**: v1
**Type**: Read/Write (CRUD)
**Formats**: XML, JSON

## Endpoint Format

```
GET /api/v1/{EntityType}/[Id]?where={where}&include=[Fields]&format=json&take={N}&skip={N}
```

## URL Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `where` | string | Filter expression | `EntityState.Name eq 'Open'` |
| `include` | string | Fields to retrieve | `[Id,Name,Description]` |
| `exclude` | string | Fields to exclude | `[Description,Tags]` |
| `append` | string | Calculated fields | `[Bugs-Count,Tasks-Count]` |
| `take` | int | Items per page (max 1000, default 25) | `take=50` |
| `skip` | int | Items to skip | `skip=25` |
| `orderBy` | string | Sort ascending | `orderBy=CreateDate` |
| `orderByDesc` | string | Sort descending | `orderByDesc=CreateDate` |
| `format` | string | Response format | `format=json` or `format=xml` |

## Examples

### List all user stories
```
GET /api/v1/UserStories/
```

### List with filters
```
GET /api/v1/Bugs?where=EntityState.Name eq 'Open'
```

### List with field selection
```
GET /api/v1/UserStories?include=[Id,Name,Owner[FirstName,LastName]]
```

### List with pagination
```
GET /api/v1/Tasks?take=50&skip=25
```

### Get single entity
```
GET /api/v1/UserStories/12345
```

### Create entity
```
POST /api/v1/UserStories
Content-Type: application/json

{"Name":"New Story", "Project":{"Id":2}, "Description":"..."}
```

### Update entity
```
POST /api/v1/UserStories/12345
Content-Type: application/json

{"EntityState":{"Id":6}, "Description":"Updated"}
```

## Response Format

### JSON Response (Default)

```json
{
  "Next": "/api/v1/UserStories?take=25&skip=25",
  "Prev": "/api/v1/UserStories?take=25&skip=0",
  "Items": [
    {
      "Id": 12345,
      "Name": "Entity Name",
      "Description": null,
      "CreateDate": "/Date(1314890435000+0300)/",
      ...
    }
  ]
}
```

### Date Format

JSON dates use Microsoft format: `/Date(milliseconds+timezone)/`

Example: `/Date(1314890435000+0300)/` = September 1, 2011, 3:20:35 UTC+3

### XML Response

```xml
<UserStories Next="/api/v1/UserStories?take=25&skip=25"
             Prev="/api/v1/UserStories?take=25&skip=0">
  <UserStory Id="12345" Name="Entity Name">
    <Description nil="true"/>
    <CreateDate>2016-10-16T04:27:10</CreateDate>
    ...
  </UserStory>
</UserStories>
```

## Entity Types

### Work Items (Assignable)

| Type | Singular | Plural |
|------|----------|--------|
| Epic | Epic | Epics |
| Feature | Feature | Features |
| User Story | UserStory | UserStories |
| Task | Task | Tasks |
| Bug | Bug | Bugs |
| Test Plan | TestPlan | TestPlans |
| Test Plan Run | TestPlanRun | TestPlanRuns |
| Request | Request | Requests |

### Containers

| Type | Singular | Plural |
|------|----------|--------|
| Project | Project | Projects |
| Program | Program | Programs |
| Release | Release | Releases |
| Iteration | Iteration | Iterations |
| Team Iteration | TeamIteration | TeamIterations |
| Team | Team | Teams |

### Other

| Type | Singular | Plural |
|------|----------|--------|
| User | User | Users |
| TestCase | TestCase | TestCases |
| CustomField | CustomField | CustomFields |
| Comment | Comment | Comments |
| Time | Time | Times |

## Common Fields

All entities have:

```json
{
  "Id": 12345,
  "Name": "Entity Name",
  "Description": "...",
  "CreateDate": "...",
  "ModifyDate": "...",
  "Owner": { "Id": 100, "FirstName": "John", "LastName": "Doe" },
  "Project": { "Id": 200, "Name": "Project Name" },
  "EntityState": { "Id": 1, "Name": "Open" },
  "EntityType": { "Id": 4, "Name": "UserStory" }
}
```

Work items (UserStory, Bug, Task) additionally have:

```json
{
  "AssignedUser": { "Id": 101, "FirstName": "Jane" },
  "Priority": { "Id": 5, "Name": "High" },
  "Effort": 8.0,
  "TimeSpent": 3.5,
  "TimeRemain": 4.5,
  "Parent": { "Id": 11111, "Name": "Parent Item" },
  "Tags": ["tag1", "tag2"]
}
```

## Filtering Operators

| Operator | Format | Example |
|----------|--------|---------|
| Equals | `field eq value` | `Name eq 'Bug'` |
| Not equals | `field ne value` | `Status ne 'Closed'` |
| Greater than | `field gt value` | `Id gt 1000` |
| Greater or equal | `field gte value` | `Id gte 1000` |
| Less than | `field lt value` | `CreateDate lt '2024-01-01'` |
| Less or equal | `field lte value` | `CreateDate lte '2024-01-01'` |
| Contains | `field contains value` | `Name contains 'auth'` |
| Not contains | `field not contains value` | `Tags not contains 'urgent'` |
| In list | `field in (val1,val2,...)` | `Id in (1,2,3)` |
| Is null | `field is null` | `Description is null` |
| Is not null | `field is not null` | `Description is not null` |

## Logical Operators

| Operator | Format |
|----------|--------|
| AND | `cond1 and cond2` |

**Note**: OR is not currently supported

## Examples

### Open items in project
```
where=Project.Id eq 123 and EntityState.Name eq 'Open'
```

### Items created in date range
```
where=(CreateDate gt '2024-01-01') and (CreateDate lt '2024-12-31')
```

### Items with specific priority
```
where=Priority.Name eq 'High'
```

### Items with custom field
```
where=CustomFields.RiskLevel eq 'Critical'
```

### Items with tags
```
where=Tags contains 'urgent'
```

## Custom Fields

### Query by custom field
```
where=CustomFields.FieldName eq 'Value'
```

### With spaces in field name
```
where=('CustomFields.Field With Spaces' eq 'Value')
```

### Not supported
- ❌ Filtering by Calculated Custom Fields
- ❌ Nested collection filters (use workarounds)

## Nested Collections

### Inner collections
```
GET /api/v1/UserStories/34256/Bugs
```

### Add to inner collection
Cannot add directly. Instead:

```
POST /api/v1/Bugs
Content-Type: application/json

{"UserStory":{"Id":123}, "Name":"New Bug", "Project":{"Id":2}}
```

### Comments on entities
```
POST /api/v1/Comments
Content-Type: application/json

{
  "General":{"Id":123},
  "Description":"Comment text"
}
```

## Pagination Response

When results exceed page size:

```json
{
  "Next": "https://instance.tpondemand.com/api/v1/UserStories?take=25&skip=25",
  "Prev": "https://instance.tpondemand.com/api/v1/UserStories?take=25&skip=0",
  "Items": [...]
}
```

If no next/prev page, field is omitted.

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid query) |
| 401 | Unauthorized (auth failed) |
| 404 | Not found |
| 500 | Server error |

## Related

- [API v2 Reference](api-v2-reference.md)
- [Query Syntax Reference](query-syntax.md)
- [Entity Types Reference](entity-types.md)
- [Authentication Methods](auth-methods.md)
