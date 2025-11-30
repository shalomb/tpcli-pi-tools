# How To: Work with User Stories

Complete guide to creating, reading, updating, and deleting User Stories in TargetProcess.

**Source**: [IBM TargetProcess API v1 Operations & CRUD](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-operations-crud)

## User Story Relationships

### References (Parent/Related Entities)

| Reference | Type | Description | Required |
|-----------|------|-------------|----------|
| Project | Resource | Parent project | ✅ Yes |
| Release | Resource | Product release | ❌ No |
| Iteration | Resource | Sprint/iteration | ❌ No |
| Feature | Resource | Parent feature | ❌ No |
| EntityState | Resource | Status (Open, Done, etc) | ❌ No |
| ResponsibleTeam | Resource | Team owning the story | ❌ No |

### Collections (Child Entities)

| Collection | Type | Description | Mutable |
|------------|------|-------------|---------|
| Bugs | Related Items | Bugs associated with story | ❌ No |
| Tasks | Related Items | Sub-tasks | ❌ No |
| UserStoryTestCases | Related Items | Test cases | ❌ No |
| Assignments | Related Items | User assignments | ✅ Yes |
| Times | Related Items | Time logs | ✅ Yes |
| Comments | Related Items | Discussion comments | ✅ Yes |
| CustomFields | Related Items | Custom attributes | ✅ Yes |
| SlaveRelations | Related Items | Relationships to other items | ❌ No |

## Reading User Stories

### Get All User Stories

```bash
./tpcli list UserStories
```

With filtering and pagination:

```bash
./tpcli list UserStories \
  --where "EntityState.Name eq 'Open'" \
  --take 50 \
  --skip 0
```

### Get Single User Story

```bash
./tpcli get UserStories 2028653
```

### Get User Story with Specific Fields

```bash
./tpcli list UserStories \
  --fields "Id,Name,Description,Priority,Effort,EntityState"
```

### Get User Story with Related Entities

Include related fields in your query:

```bash
./tpcli list UserStories \
  --fields "Id,Name,Project[Name],Feature[Name,Epic[Name]],EntityState[Name]"
```

## Accessing Collections (Inner Collections)

### Get Bugs for a Specific User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Bugs?access_token=YOUR_TOKEN"
```

Using tpcli (requires custom implementation):

```bash
./tpcli get UserStories 34256 --collection Bugs
```

### Get Tasks for a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Tasks?access_token=YOUR_TOKEN"
```

### Get Comments on a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Comments?access_token=YOUR_TOKEN"
```

### Get Times Logged on a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Times?access_token=YOUR_TOKEN"
```

## Creating User Stories

### Minimum Required Fields

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "User can log in with email",
    "Project": {"Id": 222402}
  }?access_token=YOUR_TOKEN
```

### Create with Full Details

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "User can reset forgotten password",
    "Description": "Allow users to reset password via email link",
    "Project": {"Id": 222402},
    "Feature": {"Id": 2029239},
    "Release": {"Id": 1942235},
    "Iteration": {"Id": 1234567},
    "Effort": 8,
    "Priority": {"Id": 5},
    "Owner": {"Id": 450},
    "Tags": ["frontend", "auth"],
    "EntityState": {"Id": 11614}
  }?access_token=YOUR_TOKEN
```

### Create with Custom Fields

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Implement password reset",
    "Project": {"Id": 222402},
    "CustomFields": [
      {"Name": "Story Type", "Value": "Feature"},
      {"Name": "Jira Key", "Value": "EX-2791"}
    ]
  }?access_token=YOUR_TOKEN
```

**Response**:
```json
{
  "Id": 2029500,
  "Name": "User can reset forgotten password",
  "Project": {"Id": 222402, "Name": "GDDT"},
  "CreateDate": "/Date(1764414577000-0500)/",
  ...
}
```

## Updating User Stories

### Update Existing Story

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2029500 \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "User can securely reset forgotten password",
    "Description": "Allow users to reset password via secure email link",
    "Effort": 13,
    "EntityState": {"Id": 1750}
  }?access_token=YOUR_TOKEN
```

### Update Status/State

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2029500 \
  -H "Content-Type: application/json" \
  -d '{
    "EntityState": {"Id": 1750}
  }?access_token=YOUR_TOKEN
```

### Change Priority

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2029500 \
  -H "Content-Type: application/json" \
  -d '{
    "Priority": {"Id": 7}
  }?access_token=YOUR_TOKEN
```

### Assign to Team/User

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2029500 \
  -H "Content-Type: application/json" \
  -d '{
    "Owner": {"Id": 450},
    "ResponsibleTeam": {"Id": 1122361}
  }?access_token=YOUR_TOKEN
```

## Adding to Collections

### Cannot Add Directly to Collections

⚠️ **Important**: You **cannot** directly add items to inner collections. Instead, you must:

1. Create the related entity
2. Set its parent reference to the User Story

### Example: Create a Bug for a User Story

Instead of:
```bash
# ❌ This won't work - can't POST to inner collection
POST /api/v1/UserStories/34256/Bugs
```

Do this:
```bash
# ✅ Create a Bug and set its parent
curl -X POST https://instance.tpondemand.com/api/v1/Bugs \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Login button doesn'\''t work on mobile",
    "Project": {"Id": 222402},
    "UserStory": {"Id": 2029500}
  }?access_token=YOUR_TOKEN
```

### Create a Task for a User Story

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Tasks \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Implement password reset endpoint",
    "Project": {"Id": 222402},
    "UserStory": {"Id": 2029500},
    "Effort": 5
  }?access_token=YOUR_TOKEN
```

### Add Time Log Entry

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Times \
  -H "Content-Type: application/json" \
  -d '{
    "General": {"Id": 2029500},
    "Spent": 2.5,
    "Remain": 5.5,
    "Description": "Completed password reset form"
  }?access_token=YOUR_TOKEN
```

### Add Comment

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Comments \
  -H "Content-Type: application/json" \
  -d '{
    "General": {"Id": 2029500},
    "Description": "Ready for testing in staging environment"
  }?access_token=YOUR_TOKEN
```

## Deleting User Stories

### Delete a User Story

```bash
curl -X DELETE https://instance.tpondemand.com/api/v1/UserStories/2029500?access_token=YOUR_TOKEN
```

### Constraints

⚠️ **Important Deletion Rules**:
- Can only delete User Stories in certain states (check with your admin)
- Deleting a User Story may cascade to child items depending on configuration
- Related bugs, tasks, and comments may be affected
- Always backup or archive important data before deletion

## Common Query Patterns

### Find User Stories by Iteration

```bash
./tpcli list UserStories \
  --where "Iteration.Id eq 1234567"
```

### Find User Stories by Feature

```bash
./tpcli list UserStories \
  --where "Feature.Id eq 2029239"
```

### Find Open User Stories in Current Sprint

```bash
./tpcli list UserStories \
  --where "EntityState.Name eq 'Open' and Iteration.IsCurrent eq 'true'"
```

### Find User Stories Assigned to Specific User

```bash
./tpcli list UserStories \
  --where "Owner.Id eq 450"
```

### Find User Stories by Priority

```bash
./tpcli list UserStories \
  --where "Priority.Name eq 'High' or Priority.Name eq 'Urgent'"
```

### Find High-Effort User Stories

```bash
./tpcli list UserStories \
  --where "Effort gt 8"
```

### Find User Stories Without Assignment

```bash
./tpcli list UserStories \
  --where "Owner == null"
```

### Find User Stories with Custom Field Value

```bash
./tpcli list UserStories \
  --where "CustomFields.'Story Type' eq 'Feature'"
```

## Working with Time and Dates

### Find User Stories Created This Month

```bash
./tpcli list UserStories \
  --where "CreateDate gt '2024-11-01' and CreateDate lt '2024-12-01'"
```

### Find Recently Modified Stories

```bash
./tpcli list UserStories \
  --where "ModifyDate gt '2024-11-20'" \
  --orderByDesc "ModifyDate"
```

### Find Stories with Overdue Dates

```bash
./tpcli list UserStories \
  --where "EndDate lt today() and EntityState.Name ne 'Done'"
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Invalid field or format | Check field names and JSON syntax |
| 401 Unauthorized | Invalid token | Verify access token is valid and not expired |
| 404 Not Found | User Story ID doesn't exist | Check the ID value |
| 409 Conflict | State transition invalid | Verify the target state is valid from current state |

### Example Error Response

```json
{
  "Message": "Creation model state is invalid.",
  "FieldMessages": {
    "Project": ["Project is required"]
  }
}
```

## Best Practices

1. **Always Include Project**: Every User Story must belong to a Project
2. **Use Batch Operations**: When creating multiple stories, batch them to reduce API calls
3. **Cache Lookups**: Store Project IDs, Feature IDs, and user IDs locally to avoid repeated lookups
4. **Pagination**: Use `take=50` or `take=100` for better performance than default 25
5. **Inner Collections**: Use `innerTake=1000` when accessing collections to get complete data
6. **Error Handling**: Always check response status and handle errors gracefully
7. **Rate Limiting**: Add delays between rapid API calls to avoid throttling

## Related

- [API v1 Reference](../reference/api-v1-reference.md)
- [Entity Types Reference](../reference/entity-types.md)
- [Query Syntax Reference](../reference/query-syntax.md)
- [How to Paginate Results](../how-to/paginate-results.md)
- [How to Work with Collections](../how-to/work-with-collections.md)
