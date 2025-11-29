# TargetProcess API Discovery

## Instance Information
- **Domain**: takedamain.tpondemand.com
- **Authentication**: API Key format (base64 encoded `userId:apiToken`)
- **API Base URL**: https://takedamain.tpondemand.com/api/v1
- **API v2 URL**: https://takedamain.tpondemand.com/api/v2

## Entity Model

### Core Entity Types Observed

Based on UI navigation and API documentation, the main entity types are:

#### Hierarchy Levels
```
Epic
├── Feature (User Story)
│   ├── Task
│   └── Bug
└── Initiative
    └── Epic
        └── ...
```

### Primary Entities

| Entity Type | API Name | Description | ID Example |
|-------------|----------|-------------|-----------|
| Epic | `Epics` | High-level work grouping | 5555673480067962920 |
| Feature | `Features` | Major work item | 1940304, 1938766 |
| User Story | `UserStories` | Work unit assigned to users | 1938771 |
| Task | `Tasks` | Subtask of a User Story | - |
| Bug | `Bugs` | Defect report | - |
| Project | `Projects` | Top-level container | - |
| Iteration | `Iterations` | Sprint or release cycle | - |
| Release | `Releases` | Version release | - |
| Team | `Teams` | User team | - |
| User | `Users` | Team member | - |

### UI URL Patterns

#### Board View (Epic/Feature Level)
```
https://takedamain.tpondemand.com/RestUI/Board.aspx
  #page=board/{boardId}
  &appConfig={encodedConfig}
  &boardPopup={entityType}/{entityId}/silent
```

Example:
- Board: `5555673480067962920`
- Feature popup: `feature/1940304/silent`
- Feature popup: `feature/1938766/silent`

#### Entity View (Direct)
```
https://takedamain.tpondemand.com/entity/{id}-{slug}
https://takedamain.tpondemand.com/restui/board.aspx?#page={entityType}/{id}
```

Example:
- User Story: `https://takedamain.tpondemand.com/entity/1938771-idt-lims-update`
- Redirects to: `https://takedamain.tpondemand.com/restui/board.aspx?#page=userstory/1938771`

## API Authentication

### Method 1: API Key (Recommended)
```bash
Authorization: Basic {base64(userId:apiToken)}
```

Environment Variable:
```bash
TP_API_KEY=NDUwOkU1UUhmL1pWUm1Ld2RyYlBFbDl6OUtQVXd3OEFhTG54dGxXcEdNMk42RWc9
TP_DOMAIN=takedamain.tpondemand.com
```

### Method 2: Basic Auth
```bash
Authorization: Basic {base64(username:password)}
```

Environment Variables:
```bash
TP_USERNAME=your-username
TP_PASSWORD=your-password
TP_DOMAIN=takedamain.tpondemand.com
```

## API Response Format

### List Response
```json
{
  "Items": [
    {
      "Id": 12345,
      "Name": "Entity Name",
      "EntityState": { "Name": "Open" },
      "Owner": { "Id": 100, "FirstName": "John", "LastName": "Doe" },
      ...
    }
  ]
}
```

### Single Entity Response
```json
{
  "Id": 12345,
  "Name": "Entity Name",
  "Description": "...",
  "EntityState": { "Name": "Open" },
  ...
}
```

## Query Parameters

### Common Query Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `take` | int | Number of items to return (max 1000) | 25 |
| `skip` | int | Items to skip for pagination | 0 |
| `where` | string | Filter expression | `EntityState.Name eq 'Open'` |
| `include` | string | Related data to include | `[Owner,Project]` |
| `orderBy` | string | Sort order | `Name asc` |
| `format` | string | Response format | `json` |

### Where Clause Syntax
```
Field.Property operator Value

Operators:
- eq (equals)
- ne (not equals)
- gt (greater than)
- lt (less than)
- ge (greater than or equal)
- le (less than or equal)
- contains
- in (in list)

Logical:
- and
- or
```

Examples:
```
EntityState.Name eq 'Open'
Project.Id eq 1234
Owner.Id eq 100
Priority.Name eq 'High' and EntityState.Name eq 'Open'
CreateDate gt '2024-01-01'
```

## Known Issues

### Issue 1: "startIndex cannot be larger than length of string"
**Error**: HTTP 400/500 from TargetProcess server
**Possible Causes**:
- Malformed where clause
- Invalid include parameter format
- Empty required field in query
- Query parameter encoding issue

**Workaround**: Start with minimal queries (no where/include)

## Discovery Roadmap

- [ ] Test basic entity fetch (Projects, Epics, Features)
- [ ] Document entity relationships and includes
- [ ] Map custom fields and properties
- [ ] Test filtering and search
- [ ] Document state transitions and workflows
- [ ] Map user roles and permissions
- [ ] Document time tracking fields
- [ ] Map attachment handling
- [ ] Document comment/discussion API

## Related Resources

- [MCP Implementation Reference](../projects/aaronsb/apptio-target-process-mcp/)
- [Official TP Documentation](https://dev.targetprocess.com/docs)
- [API v1 Reference](https://dev.targetprocess.com/docs/rest-getting-started)
- [API v2 (Read-only)](https://dev.targetprocess.com/docs/rest-api-v2)
