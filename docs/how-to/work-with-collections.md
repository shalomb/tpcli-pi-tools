# How To: Work with Resources and Collections

Complete guide to understanding and working with TargetProcess resources and collections.

**Source**: [IBM TargetProcess API v1 Resources & Collections](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-resources-collections)

## Core Concepts

### Resources

Resources are individual TargetProcess entities:
- User Stories
- Bugs
- Tasks
- Projects
- Teams
- Users
- etc.

Each resource has a unique ID and contains:
- **Fields**: Basic properties (Name, Description, etc.)
- **References**: Links to related resources (Project, Owner, etc.)
- **Collections**: Related child resources (Bugs, Tasks, Comments, etc.)

### Collections

Collections are sets of related resources. They fall into two types:

**1. Direct Collections** - All items of a type:
```bash
GET /api/v1/UserStories
# Returns all User Stories
```

**2. Inner Collections** - Items related to a specific resource:
```bash
GET /api/v1/UserStories/34256/Bugs
# Returns only Bugs related to User Story 34256
```

## Resource Access Patterns

### Get All Resources of a Type

```bash
# Get all projects
./tpcli list Projects

# Get all user stories
./tpcli list UserStories

# Get all bugs
./tpcli list Bugs
```

### Get Specific Resource by ID

```bash
# Get single user story
./tpcli get UserStories 2029500

# Get single project
./tpcli get Projects 222402

# Get single bug
./tpcli get Bugs 2028655
```

### Get Resource with Related Fields

Include nested entity data:

```bash
# Get user story with project and feature details
./tpcli list UserStories \
  --fields "Id,Name,Project[Id,Name],Feature[Id,Name],Owner[FirstName,LastName]" \
  --take 10
```

## User Story Relationships Overview

### Accessing References (Parent Entities)

References are resources that the User Story belongs to or relates to.

```
User Story References:
├── Project          (Parent - Required)
├── Release          (Product release)
├── Iteration        (Sprint)
├── Feature          (Parent feature)
├── EntityState      (Status)
└── ResponsibleTeam  (Team)
```

### Accessing Collections (Child Entities)

Collections are resources that belong to the User Story.

```
User Story Collections:
├── Bugs                    (Related defects)
├── Tasks                   (Sub-tasks)
├── UserStoryTestCases      (Test cases)
├── Assignments             (Team/user assignments)
├── Times                   (Time log entries)
├── Comments                (Discussion)
├── CustomFields            (Custom attributes)
└── SlaveRelations          (Linked items)
```

## Inner Collections: Getting Related Items

### Syntax

```
GET /api/v1/{Resource}/{Id}/{Collection}
```

### Example: Get Bugs for a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Bugs?access_token=TOKEN"
```

Response:
```json
{
  "Items": [
    {
      "Id": 2028655,
      "Name": "Create DQ Rule | Issues in fields Rule Configuration on UI",
      "Priority": {"Id": 7, "Name": "Low"},
      "EntityState": {"Id": 11600, "Name": "Backlog"}
    }
  ],
  "Next": "/api/v1/UserStories/34256/Bugs?skip=25&take=25"
}
```

### Get Tasks for a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Tasks?access_token=TOKEN"
```

### Get Comments for a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Comments?access_token=TOKEN"
```

### Get Time Entries for a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Times?access_token=TOKEN"
```

### Get Test Cases for a User Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/UserStoryTestCases?access_token=TOKEN"
```

## Filtering Collections

### Filter Inner Collection Items

```bash
# Get only open bugs in a user story
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Bugs?where=EntityState.Name%20eq%20'Open'&access_token=TOKEN"

# URL decoded for readability
/api/v1/UserStories/34256/Bugs?where=EntityState.Name eq 'Open'
```

### Paginate Collections

```bash
# Get first 10 bugs for a user story
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Bugs?take=10&access_token=TOKEN"

# Get next 10
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Bugs?skip=10&take=10&access_token=TOKEN"
```

### Include Fields from Collection

```bash
# Get only specific fields from bugs
curl "https://instance.tpondemand.com/api/v1/UserStories/34256/Bugs?include=[Id,Name,Priority]&access_token=TOKEN"
```

## Important: Cannot Directly Modify Collections

⚠️ **Key Limitation**: You **cannot** directly POST items to inner collections.

```bash
# ❌ This WON'T work
POST /api/v1/UserStories/34256/Bugs
```

### Correct Approach: Set Parent Reference

To add a Bug to a User Story, create the Bug with the User Story as parent:

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Bugs \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Login form validation broken",
    "Project": {"Id": 222402},
    "UserStory": {"Id": 34256},
    "Priority": {"Id": 5}
  }?access_token=TOKEN'
```

This creates the Bug AND automatically adds it to the User Story's Bugs collection.

## Resource Relationships: Full Examples

### Example 1: Get All Data for a User Story

```bash
#!/bin/bash

STORY_ID=34256
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get story details
echo "=== Story Details ==="
curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq '.'

# Get related bugs
echo "=== Related Bugs ==="
curl -s "$BASE/UserStories/$STORY_ID/Bugs?take=100&access_token=$TOKEN" | jq '.Items'

# Get related tasks
echo "=== Related Tasks ==="
curl -s "$BASE/UserStories/$STORY_ID/Tasks?take=100&access_token=$TOKEN" | jq '.Items'

# Get comments
echo "=== Comments ==="
curl -s "$BASE/UserStories/$STORY_ID/Comments?take=100&access_token=$TOKEN" | jq '.Items'

# Get time logs
echo "=== Time Logs ==="
curl -s "$BASE/UserStories/$STORY_ID/Times?take=100&access_token=$TOKEN" | jq '.Items'
```

### Example 2: Get Project with All User Stories and Their Tasks

```bash
# Get project details
curl -s "https://instance.tpondemand.com/api/v1/Projects/222402?access_token=TOKEN" | jq '.'

# Get all user stories in project
curl -s "https://instance.tpondemand.com/api/v1/UserStories?where=Project.Id%20eq%20222402&include=[Id,Name]&take=1000&access_token=TOKEN" | jq '.Items'

# For each story, get tasks
# (Note: This requires iteration - API v2 supports nested collection queries)
```

### Example 3: Create Linked Items

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
PROJECT_ID=222402
STORY_ID=34256

# Create User Story
echo "Creating User Story..."
STORY=$(curl -s -X POST "$BASE/UserStories?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Implement password reset",
    "Project": {"Id": '${PROJECT_ID}'}
  }')

NEW_STORY_ID=$(echo $STORY | jq '.Id')
echo "Created story: $NEW_STORY_ID"

# Create Task for the story
echo "Creating Task..."
curl -s -X POST "$BASE/Tasks?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Implement reset endpoint",
    "Project": {"Id": '${PROJECT_ID}'},
    "UserStory": {"Id": '${NEW_STORY_ID}'},
    "Effort": 5
  }' | jq '.Id'

# Create Bug for the story
echo "Creating Bug..."
curl -s -X POST "$BASE/Bugs?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "Reset link expires too quickly",
    "Project": {"Id": '${PROJECT_ID}'},
    "UserStory": {"Id": '${NEW_STORY_ID}'},
    "Priority": {"Id": 5}
  }' | jq '.Id'

# Verify by getting all bugs in the story
echo "Bugs in story $NEW_STORY_ID:"
curl -s "$BASE/UserStories/$NEW_STORY_ID/Bugs?access_token=$TOKEN" | jq '.Items | length'
```

## Collection Pagination with innerTake

### When You Need innerTake

Use `innerTake` when including collections in your request:

```bash
# Get projects with all their stories (not just first 25)
curl "https://instance.tpondemand.com/api/v1/Projects?include=[Id,Name,userstories]&innerTake=1000&access_token=TOKEN"
```

### Without innerTake (Limited to 25 items per collection)

```bash
curl "https://instance.tpondemand.com/api/v1/Projects?include=[Id,Name,userstories]&access_token=TOKEN"

# Result:
{
  "Items": [{
    "Id": 222402,
    "Name": "GDDT",
    "userstories": [
      // Only first 25 stories shown
    ]
  }]
}
```

### With innerTake=1000 (Get All Items)

```bash
curl "https://instance.tpondemand.com/api/v1/Projects?include=[Id,Name,userstories]&innerTake=1000&access_token=TOKEN"

# Result shows all stories even if project has 500+
```

## Working with Different Entity Types

### Get Tasks and Their Related Items

```bash
# Get all tasks
./tpcli list Tasks --take 100

# Get specific task
./tpcli get Tasks 1234567

# Get user story for a task
./tpcli list Tasks \
  --fields "Id,Name,UserStory[Id,Name],Project[Id,Name]"

# Get time entries for task
curl "https://instance.tpondemand.com/api/v1/Tasks/1234567/Times?access_token=TOKEN"
```

### Get Bugs and Their Information

```bash
# Get all bugs
./tpcli list Bugs --take 100

# Get bug with details
./tpcli get Bugs 2028655 \
  --fields "Id,Name,Priority,Severity,EntityState,UserStory[Name],Project[Name]"

# Get comments on bug
curl "https://instance.tpondemand.com/api/v1/Bugs/2028655/Comments?access_token=TOKEN"
```

### Get Iterations and Their Items

```bash
# Get current iteration
./tpcli list Iterations --where "IsCurrent eq 'true'"

# Get user stories in iteration
./tpcli list UserStories \
  --where "Iteration.Id eq 1234567" \
  --take 100

# Get all assignables in iteration
./tpcli list Assignables \
  --where "Iteration.IsCurrent eq 'true'"
```

## Best Practices

1. **Always Use Project Reference**: Every assignable item needs a Project
2. **Include Parent References**: Always include parent IDs when querying children
3. **Use innerTake for Collections**: Set innerTake=1000 to get complete data
4. **Filter Before Including**: Reduce payload by filtering before including collections
5. **Cache Lookups**: Store frequently used IDs (Projects, Teams) locally
6. **Handle Pagination**: Account for collections spanning multiple pages
7. **Use Specific Fields**: Include only needed fields to reduce response size
8. **Error Handling**: Check for null references in responses

## Common Query Patterns

### Get All User Stories with Their Tasks

```bash
#!/bin/bash

TOKEN="your_token"

# Get stories with task count via API v2 (more efficient)
curl -s "https://instance.tpondemand.com/api/v2/userstory?select={id,name,taskCount:tasks.count()}&access_token=$TOKEN" | jq '.items'
```

### Find Items Without Parent

```bash
# User stories without feature
./tpcli list UserStories --where "Feature == null"

# Tasks without parent user story
./tpcli list Tasks --where "UserStory == null"
```

### Chain Multiple Filters

```bash
# Open bugs in a specific project without assignment
./tpcli list Bugs \
  --where "Project.Id eq 222402 and EntityState.Name eq 'Open' and Owner == null"
```

## Related

- [How To: Work with User Stories](./work-with-user-stories.md)
- [How To: Paginate Results](./paginate-results.md)
- [API v1 Reference](../reference/api-v1-reference.md)
- [API v2 Reference](../reference/api-v2-reference.md)
- [Entity Types Reference](../reference/entity-types.md)
