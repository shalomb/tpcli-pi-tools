# Reference: User Story Structure

Complete reference for TargetProcess User Story entity, including all fields, relationships, and collections.

## User Story Overview

A User Story represents a feature or requirement from an end-user perspective. It's the primary work item in most TargetProcess projects.

**API Endpoints**:
- List: `GET /api/v1/UserStories`
- Single: `GET /api/v1/UserStories/{id}`
- Create: `POST /api/v1/UserStories`
- Update: `POST /api/v1/UserStories/{id}`
- Delete: `DELETE /api/v1/UserStories/{id}`

**Typical Status States**:
- Backlog
- Open
- In Progress
- Testing
- Done

## User Story Relationships Diagram

```
                    REFERENCES (Parent/Related Entities)
    ┌───────────────────────────────────────────────────┐
    │                                                   │
    │  Project (Required)                              │
    │     │                                            │
    │     ├─ Release (Optional)                        │
    │     │                                            │
    │     ├─ Iteration (Optional)                      │
    │     │                                            │
    │     └─ Feature (Optional) ─┬─ Epic (Optional)   │
    │                             │                    │
    │  EntityState (Required)     │                    │
    │  ResponsibleTeam (Optional) │                    │
    └─────────────────────────────────────────────────┘
                            │
                            │
                    ┌───────┴────────┐
                    │                │
            ┌───────▼────────┐    ┌──▼──────────────┐
            │  User Story    │    │   COLLECTIONS   │
            │  (Main Entity) │    │ (Child Entities)│
            └────────────────┘    └──────┬──────────┘
                                         │
            ┌────────────────────────────┴────────────────────────────┐
            │                                                          │
      ┌─────▼──────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐  │
      │    Bugs    │  │    Tasks     │  │  TestCases│  │Comments │  │
      └────────────┘  └──────────────┘  └──────────┘  └──────────┘  │
            │                                                          │
      ┌─────▼──────────┐  ┌──────────────┐  ┌─────────────────┐     │
      │  Assignments   │  │    Times     │  │  CustomFields   │     │
      └────────────────┘  └──────────────┘  └─────────────────┘     │
                                                                      │
                                    ┌─────────────────────────────┐  │
                                    │  SlaveRelations              │  │
                                    │  (Links to other items)      │  │
                                    └──────────────────────────────┘─┘
```

## Field Reference

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Name` | String | Story name/title | "User can log in with email" |
| `Project` | Resource | Parent project (ID only) | `{"Id": 222402}` |

### Core Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Id` | Integer | Unique identifier | 2028653 |
| `Description` | String | Detailed description | "Allow users to authenticate..." |
| `Effort` | Decimal | Story points/effort | 8.5 |
| `Priority` | Resource | Priority level | `{"Id": 5, "Name": "High"}` |
| `EntityState` | Resource | Current status | `{"Id": 11614, "Name": "Backlog"}` |
| `Owner` | Resource | Primary owner/creator | `{"Id": 450, "FirstName": "John"}` |
| `AssignedUser` | Resource | User assigned to story | `{"Id": 500, "FirstName": "Jane"}` |
| `Tags` | Array | Tags/labels | `["frontend", "auth"]` |

### Time Tracking Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `TimeSpent` | Decimal | Hours spent on story | 5.5 |
| `TimeRemain` | Decimal | Hours remaining | 2.5 |
| `EffortCompleted` | Decimal | Completed effort | 5 |
| `EffortToDo` | Decimal | Remaining effort | 3 |

### Timeline Fields

| Field | Type | Description | Format |
|-------|------|-------------|--------|
| `CreateDate` | Date | When created | `/Date(1764414577000-0500)/` |
| `ModifyDate` | Date | Last modified | `/Date(1764414580000-0500)/` |
| `StartDate` | Date | Planned start | `/Date(...)/` or null |
| `EndDate` | Date | Planned end | `/Date(...)/` or null |
| `PlannedStartDate` | Date | Planned start | `/Date(...)/` or null |
| `PlannedEndDate` | Date | Planned end | `/Date(...)/` or null |

### Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `EntityType` | Resource | Entity type | `{"Id": 4, "Name": "UserStory"}` |
| `EntityVersion` | Integer | Version number | 502435522 |
| `ResourceType` | String | Resource type string | "UserStory" |

### Relationship Fields (References)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Project` | Resource | ✅ Yes | Parent project |
| `Feature` | Resource | ❌ No | Parent feature (if in feature) |
| `Release` | Resource | ❌ No | Associated release |
| `Iteration` | Resource | ❌ No | Associated iteration/sprint |
| `ResponsibleTeam` | Resource | ❌ No | Team responsible for story |
| `Creator` | Resource | Auto | User who created it |
| `LastEditor` | Resource | Auto | Last user who edited it |

### Advanced Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Progress` | Decimal | Completion percentage | 0.75 (75%) |
| `NumericPriority` | Integer | Numeric priority value | 1337289 |
| `LastCommentDate` | Date | When last commented | `/Date(...)/` or null |
| `LastCommentedUser` | Resource | User who commented last | `{"Id": 450}` or null |

## Collections Reference

### Bugs Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/Bugs`

Bugs (defects) related to this User Story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Bugs?access_token=TOKEN"

# Response example
{
  "Items": [
    {
      "Id": 2028655,
      "Name": "Login button unresponsive on mobile",
      "Priority": {"Id": 7, "Name": "Low"},
      "EntityState": {"Id": 11600, "Name": "Backlog"}
    }
  ]
}
```

### Tasks Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/Tasks`

Sub-tasks or implementation tasks for this story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Tasks?access_token=TOKEN"
```

### UserStoryTestCases Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/UserStoryTestCases`

Test cases defined for this User Story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/UserStoryTestCases?access_token=TOKEN"
```

### Assignments Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/Assignments`

Team or user assignments for this story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Assignments?access_token=TOKEN"
```

### Times Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/Times`

Time entries (hours spent) logged against this story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Times?access_token=TOKEN"

# Response example
{
  "Items": [
    {
      "Id": 12345,
      "Spent": 2.5,
      "Remain": 5.5,
      "Description": "Completed form design",
      "User": {"Id": 450}
    }
  ]
}
```

### Comments Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/Comments`

Discussion comments on this story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Comments?access_token=TOKEN"

# Response example
{
  "Items": [
    {
      "Id": 99999,
      "Description": "Ready for testing",
      "General": {"Id": 2028653},
      "CreateDate": "/Date(1764414577000-0500)/",
      "Owner": {"Id": 450, "FirstName": "John"}
    }
  ]
}
```

### CustomFields Collection

**Endpoint**: Included in main request

Custom field values for this story.

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653?access_token=TOKEN"

# Response excerpt
{
  "Id": 2028653,
  "CustomFields": [
    {
      "Name": "Story Type",
      "Type": "DropDown",
      "Value": "Feature"
    },
    {
      "Name": "Acceptance Criteria",
      "Type": "RichText",
      "Value": "User enters email and password..."
    }
  ]
}
```

### SlaveRelations Collection

**Endpoint**: `GET /api/v1/UserStories/{id}/SlaveRelations`

Links to other items (dependencies, blocking relationships, etc.).

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/SlaveRelations?access_token=TOKEN"
```

## Complete JSON Example

### Minimal User Story (Create)

```json
{
  "Name": "User can reset password",
  "Project": {"Id": 222402}
}
```

### Full User Story (Response)

```json
{
  "Id": 2028653,
  "Name": "User can reset forgotten password",
  "Description": "Allow users to reset password via email link",
  "Project": {
    "Id": 222402,
    "Name": "GDDT",
    "ResourceType": "Project"
  },
  "Feature": {
    "Id": 2029239,
    "Name": "Authentication",
    "ResourceType": "Feature"
  },
  "Release": {
    "Id": 1942235,
    "Name": "PI-4/25",
    "ResourceType": "Release"
  },
  "Iteration": {
    "Id": 1234567,
    "Name": "Sprint 10",
    "ResourceType": "Iteration"
  },
  "EntityState": {
    "Id": 11614,
    "Name": "Backlog",
    "NumericPriority": 2,
    "ResourceType": "EntityState"
  },
  "Owner": {
    "Id": 450,
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john@example.com",
    "ResourceType": "GeneralUser"
  },
  "AssignedUser": {
    "Id": 500,
    "FirstName": "Jane",
    "LastName": "Smith",
    "Email": "jane@example.com",
    "ResourceType": "GeneralUser"
  },
  "Priority": {
    "Id": 5,
    "Name": "High",
    "Importance": 8,
    "ResourceType": "Priority"
  },
  "ResponsibleTeam": {
    "Id": 1122361,
    "Name": "Backend Team",
    "ResourceType": "Team"
  },
  "Effort": 8,
  "TimeSpent": 5.5,
  "TimeRemain": 2.5,
  "EffortCompleted": 5,
  "EffortToDo": 3,
  "Progress": 0.625,
  "CreateDate": "/Date(1764414577000-0500)/",
  "ModifyDate": "/Date(1764414580000-0500)/",
  "CreateDate": "/Date(1764414577000-0500)/",
  "LastCommentDate": "/Date(1764415000000-0500)/",
  "StartDate": null,
  "EndDate": null,
  "PlannedStartDate": "/Date(1764415000000-0500)/",
  "PlannedEndDate": "/Date(1764500000000-0500)/",
  "Creator": {
    "Id": 356,
    "FirstName": "Admin",
    "LastName": "User",
    "ResourceType": "GeneralUser"
  },
  "LastEditor": {
    "Id": 450,
    "FirstName": "John",
    "LastName": "Doe",
    "ResourceType": "GeneralUser"
  },
  "LastCommentedUser": {
    "Id": 450,
    "FirstName": "John",
    "LastName": "Doe",
    "ResourceType": "GeneralUser"
  },
  "Tags": ["auth", "frontend", "security"],
  "EntityType": {
    "Id": 4,
    "Name": "UserStory",
    "ResourceType": "EntityType"
  },
  "EntityVersion": 502435522,
  "NumericPriority": 1337289,
  "ResourceType": "UserStory",
  "CustomFields": [
    {
      "Name": "Story Type",
      "Type": "DropDown",
      "Value": "Feature"
    },
    {
      "Name": "Acceptance Criteria",
      "Type": "RichText",
      "Value": "User enters email and receives reset link"
    },
    {
      "Name": "Jira Key",
      "Type": "TemplatedURL",
      "Value": "EX-2791"
    }
  ]
}
```

## Status Transitions

Valid state transitions for User Stories:

```
           ┌──────────────┐
           │   Backlog    │
           └──────┬───────┘
                  │
           ┌──────▼───────┐
           │     Open     │
           └──────┬───────┘
                  │
      ┌───────────┴──────────────┐
      │                          │
  ┌───▼────┐            ┌────────▼───┐
  │Testing │            │ In Progress│
  └───┬────┘            └────────┬───┘
      │                          │
      └──────────┬───────────────┘
                 │
            ┌────▼──────┐
            │    Done    │
            └───────────┘
```

## Querying User Stories

### By Status

```bash
./tpcli list UserStories --where "EntityState.Name eq 'Open'"
```

### By Effort

```bash
./tpcli list UserStories --where "Effort gt 5"
```

### By Assignee

```bash
./tpcli list UserStories --where "Owner.Id eq 450"
```

### By Iteration

```bash
./tpcli list UserStories --where "Iteration.IsCurrent eq 'true'"
```

### By Feature

```bash
./tpcli list UserStories --where "Feature.Id eq 2029239"
```

### Complex Query

```bash
./tpcli list UserStories \
  --where "Project.Id eq 222402 and EntityState.Name eq 'Open' and Priority.Id gt 3 and Effort gt 5"
```

## Related Documentation

- [How To: Work with User Stories](../how-to/work-with-user-stories.md)
- [How To: Work with Collections](../how-to/work-with-collections.md)
- [How To: Paginate Results](../how-to/paginate-results.md)
- [Entity Types Reference](./entity-types.md)
- [API v1 Reference](./api-v1-reference.md)
