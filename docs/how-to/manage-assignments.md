# How To: Manage Assignments

Complete guide to assigning work items to users and teams in TargetProcess.

**Source**: [IBM TargetProcess API v1 Assignments](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=cases-assignments)

## Assignments Overview

Assignments link users and teams to work items (User Stories, Bugs, Tasks, etc.). Each assignment includes:
- **Assignable**: The work item (User Story, Bug, Task, etc.)
- **User/Team**: Who is assigned
- **Role**: The role of the assignment (optional)

## Assignment Structure

### Assignment Resource Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Id` | Integer | Unique assignment ID | 456789 |
| `GeneralUser` or `Team` | Resource | Who is assigned | `{"Id": 450}` |
| `Role` | String | Role type | "Developer", "QA Tester" |
| `Assignable` | Resource | Work item assigned | `{"Id": 2028653}` |
| `CreateDate` | Date | When created | `/Date(...)/ ` |
| `ModifyDate` | Date | Last modified | `/Date(...)/` |

## Retrieving Assignments

### Get All Assignments for a Work Item

```bash
# Get all assignments for a User Story
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Assignments?access_token=TOKEN"

# Response
{
  "Items": [
    {
      "Id": 456789,
      "Assignable": {"Id": 2028653, "Name": "User can reset password"},
      "GeneralUser": {
        "Id": 450,
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john@example.com"
      },
      "Role": "Developer",
      "CreateDate": "/Date(1764414577000-0500)/"
    },
    {
      "Id": 456790,
      "Assignable": {"Id": 2028653},
      "Team": {
        "Id": 1122361,
        "Name": "Backend Team"
      },
      "Role": "Owner",
      "CreateDate": "/Date(1764414577000-0500)/"
    }
  ]
}
```

### Get Assignments with Pagination

```bash
# Get assignments page by page
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Assignments?take=50&skip=0&access_token=TOKEN"
```

### Filter Assignments by User

```bash
# Get all assignments for a specific user
curl "https://instance.tpondemand.com/api/v1/Assignments?where=GeneralUser.Id%20eq%20450&access_token=TOKEN"

# URL decoded
/api/v1/Assignments?where=GeneralUser.Id eq 450
```

### Filter Assignments by Role

```bash
# Get all assignments with a specific role
curl "https://instance.tpondemand.com/api/v1/Assignments?where=Role%20eq%20'Developer'&access_token=TOKEN"
```

## Creating Assignments

### Assign User to Work Item

**Method 1: Direct POST to Assignments Endpoint**

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Assignments \
  -H "Content-Type: application/json" \
  -d '{
    "GeneralUser": {"Id": 450},
    "Assignable": {"Id": 2028653},
    "Role": "Developer"
  }?access_token=TOKEN'
```

**Response:**
```json
{
  "Id": 456789,
  "GeneralUser": {"Id": 450},
  "Assignable": {"Id": 2028653},
  "Role": "Developer",
  "CreateDate": "/Date(1764414577000-0500)/"
}
```

### Assign Team to Work Item

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Assignments \
  -H "Content-Type: application/json" \
  -d '{
    "Team": {"Id": 1122361},
    "Assignable": {"Id": 2028653},
    "Role": "Owner"
  }?access_token=TOKEN'
```

### Assign Multiple Users to Same Item

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Assign first user as Developer
curl -X POST "$BASE/Assignments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "GeneralUser": {"Id": 450},
    "Assignable": {"Id": '${STORY_ID}'},
    "Role": "Developer"
  }'

# Assign second user as QA Tester
curl -X POST "$BASE/Assignments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "GeneralUser": {"Id": 500},
    "Assignable": {"Id": '${STORY_ID}'},
    "Role": "QA Tester"
  }'

# Assign team as Owner
curl -X POST "$BASE/Assignments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Team": {"Id": 1122361},
    "Assignable": {"Id": '${STORY_ID}'},
    "Role": "Owner"
  }'
```

## Updating Assignments

⚠️ **Note**: Assignment records typically cannot be updated. To change an assignment, delete the old one and create a new one.

### Change User for Assignment

```bash
#!/bin/bash

ASSIGNMENT_ID=456789
NEW_USER_ID=550
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Delete old assignment
curl -X DELETE "$BASE/Assignments/$ASSIGNMENT_ID?access_token=$TOKEN"

# Create new assignment with same story but different user
curl -X POST "$BASE/Assignments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "GeneralUser": {"Id": '${NEW_USER_ID}'},
    "Assignable": {"Id": 2028653},
    "Role": "Developer"
  }'
```

## Removing Assignments

### Delete Single Assignment

```bash
# Get assignment ID first
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Assignments?access_token=TOKEN" | jq '.Items[0].Id'

# Delete by ID
curl -X DELETE https://instance.tpondemand.com/api/v1/Assignments/456789?access_token=TOKEN
```

### Unassign All Users from Work Item

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get all assignment IDs
ASSIGNMENTS=$(curl -s "$BASE/UserStories/$STORY_ID/Assignments?access_token=$TOKEN" | jq '.Items[].Id')

# Delete each assignment
for ASSIGNMENT_ID in $ASSIGNMENTS; do
  curl -X DELETE "$BASE/Assignments/$ASSIGNMENT_ID?access_token=$TOKEN"
  echo "Deleted assignment $ASSIGNMENT_ID"
done
```

### Bulk Unassign with Header Override

Some systems support bulk operations via special headers:

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Assignments/456789 \
  -H "Content-Type: application/json" \
  -H "X-HTTP-Method-Override: DELETE" \
  -d '{}?access_token=TOKEN'
```

## Assignment Query Patterns

### Get Users Assigned to a Story

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653/Assignments?include=[GeneralUser,Role]&access_token=TOKEN"
```

### Find All Work Items Assigned to a User

```bash
curl "https://instance.tpondemand.com/api/v1/Assignments?where=GeneralUser.Id%20eq%20450&include=[Assignable,Role]&access_token=TOKEN"

# URL decoded
/api/v1/Assignments?where=GeneralUser.Id eq 450&include=[Assignable,Role]
```

### Find All Assignments with Specific Role

```bash
curl "https://instance.tpondemand.com/api/v1/Assignments?where=Role%20eq%20'QA Tester'&access_token=TOKEN"
```

### Get Team Assignments Only

```bash
curl "https://instance.tpondemand.com/api/v1/Assignments?where=Team%20is%20not%20null&access_token=TOKEN"
```

### Get User Assignments Only

```bash
curl "https://instance.tpondemand.com/api/v1/Assignments?where=GeneralUser%20is%20not%20null&access_token=TOKEN"
```

## Common Assignment Workflows

### Workflow 1: Assign User and Check Status

```bash
#!/bin/bash

STORY_ID=2028653
USER_ID=450
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

echo "Creating assignment..."
RESULT=$(curl -s -X POST "$BASE/Assignments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "GeneralUser": {"Id": '${USER_ID}'},
    "Assignable": {"Id": '${STORY_ID}'},
    "Role": "Developer"
  }')

ASSIGNMENT_ID=$(echo $RESULT | jq '.Id')
echo "Created assignment: $ASSIGNMENT_ID"

# Verify assignment
echo "Verifying assignment..."
curl -s "$BASE/Assignments/$ASSIGNMENT_ID?access_token=$TOKEN" | jq '.'
```

### Workflow 2: Load Balance - Assign to User with Fewest Tasks

```bash
#!/bin/bash

PROJECT_ID=222402
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get users and count their assignments
echo "Counting assignments per user..."
curl -s "$BASE/Assignments?where=Assignable.Project.Id%20eq%20${PROJECT_ID}&access_token=$TOKEN" | \
  jq '[.Items[] | select(.GeneralUser != null) | .GeneralUser.Id] | group_by(.) | map({user_id: .[0], count: length}) | sort_by(.count) | .[0]'

# This would return the user with fewest assignments
# Then assign the new task to that user
```

### Workflow 3: Team-Based Assignment

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# First, assign the team as responsible
curl -X POST "$BASE/Assignments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Team": {"Id": 1122361},
    "Assignable": {"Id": '${STORY_ID}'},
    "Role": "Owner"
  }'

# Then get team members and assign individual users
TEAM_ID=1122361
curl -s "$BASE/Teams/$TEAM_ID?include=[users]&access_token=$TOKEN" | \
  jq '.Users[]' | while read user; do
    USER_ID=$(echo $user | jq '.Id')
    curl -X POST "$BASE/Assignments?access_token=$TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "GeneralUser": {"Id": '${USER_ID}'},
        "Assignable": {"Id": '${STORY_ID}'},
        "Role": "Developer"
      }'
  done
```

## Assignment Best Practices

### 1. Always Specify Role

```bash
# ✅ Good - includes role
{
  "GeneralUser": {"Id": 450},
  "Assignable": {"Id": 2028653},
  "Role": "Developer"
}

# ❌ Avoid - no role information
{
  "GeneralUser": {"Id": 450},
  "Assignable": {"Id": 2028653}
}
```

### 2. Validate User Exists Before Assigning

```bash
#!/bin/bash

USER_ID=450
TOKEN="your_token"

# Check if user exists
USER=$(curl -s "https://instance.tpondemand.com/api/v1/Users/$USER_ID?access_token=$TOKEN")

if [ -z "$(echo $USER | jq '.Id // empty')" ]; then
  echo "Error: User $USER_ID not found"
  exit 1
fi

# User exists, proceed with assignment
```

### 3. Cache Assignment Data

For large-scale operations, fetch all assignments once:

```bash
#!/bin/bash

TOKEN="your_token"

# Save all assignments to a file
curl -s "https://instance.tpondemand.com/api/v1/Assignments?take=1000&access_token=$TOKEN" > assignments.json

# Query from cache instead of API
jq '.Items[] | select(.GeneralUser.Id == 450)' assignments.json
```

### 4. Use Transactions for Multiple Assignments

When assigning multiple users, wrap in error handling:

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
USERS=(450 500 550)
FAILED=()

for USER_ID in "${USERS[@]}"; do
  RESULT=$(curl -s -X POST "$BASE/Assignments?access_token=$TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "GeneralUser": {"Id": '${USER_ID}'},
      "Assignable": {"Id": '${STORY_ID}'},
      "Role": "Developer"
    }')

  if [ -z "$(echo $RESULT | jq '.Id // empty')" ]; then
    FAILED+=($USER_ID)
    echo "Failed to assign user $USER_ID"
  fi
done

if [ ${#FAILED[@]} -gt 0 ]; then
  echo "Failed assignments: ${FAILED[@]}"
  exit 1
fi
```

### 5. Monitor Assignment Changes

Track when assignments are created/modified:

```bash
#!/bin/bash

TOKEN="your_token"

# Get assignments modified in last 24 hours
curl -s "https://instance.tpondemand.com/api/v1/Assignments?where=ModifyDate%20gt%20'$(date -d '1 day ago' +%Y-%m-%d)'&access_token=$TOKEN" | jq '.'
```

## Related

- [How To: Work with User Stories](./work-with-user-stories.md)
- [Reference: User Story Structure](../reference/user-story-structure.md)
- [API v1 Reference](../reference/api-v1-reference.md)
