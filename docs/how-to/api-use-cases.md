# How To: Common API Use Cases

Complete guide to common workflows and patterns for using the TargetProcess API.

**Source**: [IBM TargetProcess API v1 Use Cases](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-use-cases)

## Overview

This guide demonstrates practical patterns and real-world workflows for managing TargetProcess entities via the API. Each use case includes step-by-step examples you can adapt to your needs.

## Use Case 1: Identify Entity Type and Get Details

Many systems return entity IDs without type information. This pattern determines what type of entity you're working with.

### Get Entity Type

```bash
#!/bin/bash

ENTITY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get entity info from General endpoint
ENTITY=$(curl -s "$BASE/General/$ENTITY_ID?access_token=$TOKEN")

# Extract entity type
ENTITY_TYPE=$(echo $ENTITY | jq -r '.EntityType.Name')
ENTITY_NAME=$(echo $ENTITY | jq -r '.Name')

echo "Entity $ENTITY_ID is a $ENTITY_TYPE: $ENTITY_NAME"
# Output: Entity 2028653 is a UserStory: User can reset password
```

### Process Entity Based on Type

```bash
#!/bin/bash

ENTITY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get entity details
ENTITY=$(curl -s "$BASE/General/$ENTITY_ID?access_token=$TOKEN")
ENTITY_TYPE=$(echo $ENTITY | jq -r '.EntityType.Name')

case $ENTITY_TYPE in
  UserStory)
    echo "Processing User Story..."
    echo "Effort: $(echo $ENTITY | jq '.Effort')"
    ;;
  Bug)
    echo "Processing Bug..."
    echo "Severity: $(echo $ENTITY | jq -r '.Severity.Name')"
    ;;
  Task)
    echo "Processing Task..."
    echo "Time Spent: $(echo $ENTITY | jq '.TimeSpent')"
    ;;
  *)
    echo "Unknown entity type: $ENTITY_TYPE"
    ;;
esac
```

## Use Case 2: Retrieve Entity Relationships

Get all related items and understand connections between entities.

### Get All Related Items for an Entity

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

echo "=== Story Details ==="
curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq '{Id, Name, Effort, Priority: .Priority.Name, Status: .EntityState.Name}'

echo -e "\n=== Master Relations (Items this depends on) ==="
curl -s "$BASE/UserStories/$STORY_ID/MasterRelations?access_token=$TOKEN" | jq '.Items[] | {Id, Name}'

echo -e "\n=== Slave Relations (Items depending on this) ==="
curl -s "$BASE/UserStories/$STORY_ID/SlaveRelations?access_token=$TOKEN" | jq '.Items[] | {Id, Name}'

echo -e "\n=== Bugs ==="
curl -s "$BASE/UserStories/$STORY_ID/Bugs?access_token=$TOKEN" | jq '.Items[] | {Id, Name, Severity: .Severity.Name}'

echo -e "\n=== Tasks ==="
curl -s "$BASE/UserStories/$STORY_ID/Tasks?access_token=$TOKEN" | jq '.Items[] | {Id, Name, TimeSpent, TimeRemain}'

echo -e "\n=== Comments ==="
curl -s "$BASE/UserStories/$STORY_ID/Comments?access_token=$TOKEN" | jq '.Items[] | {Id, Owner: .Owner.FirstName, CreateDate}'
```

### Follow Relationship Chain

Navigate through related items:

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Start with a task
TASK_ID=1234567

# Get parent user story
STORY=$(curl -s "$BASE/Tasks/$TASK_ID?include=[UserStory]&access_token=$TOKEN" | jq '.UserStory')
STORY_ID=$(echo $STORY | jq -r '.Id')

echo "Task $TASK_ID belongs to Story $STORY_ID"

# Get story's feature
FEATURE=$(curl -s "$BASE/UserStories/$STORY_ID?include=[Feature]&access_token=$TOKEN" | jq '.Feature')
FEATURE_ID=$(echo $FEATURE | jq -r '.Id')

echo "Story $STORY_ID belongs to Feature $FEATURE_ID"

# Get feature's epic
EPIC=$(curl -s "$BASE/Features/$FEATURE_ID?include=[Epic]&access_token=$TOKEN" | jq '.Epic')
EPIC_ID=$(echo $EPIC | jq -r '.Id')

echo "Feature $FEATURE_ID belongs to Epic $EPIC_ID"
```

## Use Case 3: Filter Items in Multiple States

Find items in specific statuses using state-based filtering.

### Get Items in Multiple States

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get items in "Planned" or "In Progress" states
STATES="Planned,In Progress"

# Since OR isn't supported in v1, make multiple queries
echo "=== Items in Planned State ==="
curl -s "$BASE/UserStories?where=EntityState.Name%20eq%20'Planned'&take=100&access_token=$TOKEN" | jq '.Items[] | {Id, Name, State: .EntityState.Name}'

echo -e "\n=== Items in In Progress State ==="
curl -s "$BASE/UserStories?where=EntityState.Name%20eq%20'In Progress'&take=100&access_token=$TOKEN" | jq '.Items[] | {Id, Name, State: .EntityState.Name}'
```

### Combine Results from Multiple Queries

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Fetch multiple states
declare -a STATES=("Open" "In Progress" "Testing")

# Collect all items
ALL_ITEMS=()

for STATE in "${STATES[@]}"; do
  echo "Fetching items in $STATE..."
  ENCODED_STATE=$(echo -n "$STATE" | jq -sRr @uri)

  curl -s "$BASE/UserStories?where=EntityState.Name%20eq%20'$STATE'&take=1000&access_token=$TOKEN" | \
    jq '.Items[]' | while read item; do
      ALL_ITEMS+=("$item")
    done
done

# Save combined results
{
  echo "["
  printf '%s\n' "${ALL_ITEMS[@]}" | paste -sd ',' -
  echo "]"
} | jq '.' > all_states.json
```

### Query with State ID (More Efficient)

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get all entity states first (cache these)
STATES=$(curl -s "$BASE/EntityStates?access_token=$TOKEN" | jq '.Items[] | {id: .Id, name: .Name}')

echo "Available states:"
echo $STATES | jq '.'

# Get items by state ID (more efficient than name matching)
OPEN_STATE_ID=$(echo $STATES | jq '.[] | select(.name=="Open") | .id')
curl -s "$BASE/UserStories?where=EntityState.Id%20eq%20$OPEN_STATE_ID&take=100&access_token=$TOKEN" | \
  jq '.Items[] | {Id, Name, State: .EntityState.Name}'
```

## Use Case 4: Team-Based Queries

Find items assigned to specific teams.

### Get Items Assigned to Team

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
TEAM_ID=1122361

# Query items where ResponsibleTeam is set
curl -s "$BASE/UserStories?where=ResponsibleTeam.Id%20eq%20$TEAM_ID&take=100&access_token=$TOKEN" | \
  jq '.Items[] | {Id, Name, Team: .ResponsibleTeam.Name, Status: .EntityState.Name}'
```

### Get Team Members

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
TEAM_ID=1122361

# Get team details with members
curl -s "$BASE/Teams/$TEAM_ID?include=[users]&access_token=$TOKEN" | \
  jq '{TeamName: .Name, Members: [.users[].FirstName]}'
```

### Get All Items Assigned to Team Members

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
TEAM_ID=1122361

# Get team members
MEMBERS=$(curl -s "$BASE/Teams/$TEAM_ID?include=[users]&access_token=$TOKEN" | jq '.users[].Id')

echo "Team members: $MEMBERS"

# Get items assigned to any team member
for MEMBER_ID in $MEMBERS; do
  echo -e "\n=== Items assigned to user $MEMBER_ID ==="
  curl -s "$BASE/UserStories?where=Owner.Id%20eq%20$MEMBER_ID&take=50&access_token=$TOKEN" | \
    jq '.Items[] | {Id, Name, Owner: .Owner.FirstName}'
done
```

### Find Team's Workload

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
TEAM_ID=1122361

# Get team members
MEMBERS=$(curl -s "$BASE/Teams/$TEAM_ID?include=[users]&access_token=$TOKEN" | jq '.users')

echo "=== Team Workload Analysis ==="

echo $MEMBERS | jq '.[] |
  {
    Name: .FirstName,
    Id: .Id
  }' | while read -r member; do
    MEMBER_ID=$(echo "$member" | jq -r '.Id')
    MEMBER_NAME=$(echo "$member" | jq -r '.Name')

    # Count their open items
    OPEN_COUNT=$(curl -s "$BASE/UserStories?where=Owner.Id%20eq%20$MEMBER_ID%20and%20EntityState.Name%20eq%20'Open'&access_token=$TOKEN" | jq '.Items | length')

    # Sum their effort
    TOTAL_EFFORT=$(curl -s "$BASE/UserStories?where=Owner.Id%20eq%20$MEMBER_ID&take=1000&access_token=$TOKEN" | jq '[.Items[].Effort] | add // 0')

    echo "$MEMBER_NAME: $OPEN_COUNT open items, $TOTAL_EFFORT total effort"
  done
```

## Use Case 5: Add Comments and Feedback

Create discussions and documentation on work items.

### Add Comment to Work Item

```bash
curl -X POST https://instance.tpondemand.com/api/v1/Comments \
  -H "Content-Type: application/json" \
  -d '{
    "General": {"Id": 2028653},
    "Description": "Completed initial design. Ready for review."
  }?access_token=TOKEN'
```

### Add Comment with Context

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get current status
STATUS=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq -r '.EntityState.Name')

# Add comment with context
COMMENT="Status update: Work item is now in $STATUS. All blockers have been resolved."

curl -X POST "$BASE/Comments?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "General": {"Id": '${STORY_ID}'},
    "Description": "'$COMMENT'"
  }'
```

### Get All Comments on Item

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

curl -s "$BASE/UserStories/$STORY_ID/Comments?take=1000&access_token=$TOKEN" | \
  jq '.Items[] | {Author: .Owner.FirstName, Date: .CreateDate, Comment: .Description}'
```

## Use Case 6: Bulk Operations

Perform operations on multiple items efficiently.

### Bulk Update Tags

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
PROJECT_ID=222402

# Get all open stories in project
STORIES=$(curl -s "$BASE/UserStories?where=Project.Id%20eq%20$PROJECT_ID%20and%20EntityState.Name%20eq%20'Open'&take=1000&access_token=$TOKEN" | jq '.Items[].Id')

echo "Updating tags for all open stories in project $PROJECT_ID..."

for STORY_ID in $STORIES; do
  echo "Updating story $STORY_ID..."

  CURRENT=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq -r '.Tags // ""')
  NEW_TAGS="$CURRENT,needs-qa"
  NEW_TAGS=$(echo "$NEW_TAGS" | sed 's/^,//')

  curl -X POST "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "Tags": "'$NEW_TAGS'"
    }'
done
```

### Bulk Change Priority

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Promote all high-effort items to high priority
HIGH_EFFORT_ITEMS=$(curl -s "$BASE/UserStories?where=Effort%20gt%2010&take=1000&access_token=$TOKEN" | jq '.Items[].Id')

for ITEM_ID in $HIGH_EFFORT_ITEMS; do
  curl -X POST "$BASE/UserStories/$ITEM_ID?access_token=$TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "Priority": {"Id": 5}
    }'
done
```

### Bulk Status Update

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Move all "Testing" items to "Done" if they have no comments
TESTING_ITEMS=$(curl -s "$BASE/UserStories?where=EntityState.Name%20eq%20'Testing'&take=1000&access_token=$TOKEN" | jq '.Items[].Id')

for ITEM_ID in $TESTING_ITEMS; do
  # Check for comments
  COMMENT_COUNT=$(curl -s "$BASE/UserStories/$ITEM_ID/Comments?access_token=$TOKEN" | jq '.Items | length')

  if [ "$COMMENT_COUNT" -eq 0 ]; then
    echo "Moving item $ITEM_ID to Done (no comments to address)"

    curl -X POST "$BASE/UserStories/$ITEM_ID?access_token=$TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "EntityState": {"Id": 1750}
      }'
  fi
done
```

## Use Case 7: Generate Reports

Extract and analyze data from TargetProcess.

### Effort Summary by Status

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
PROJECT_ID=222402

# Get all states
STATES=$(curl -s "$BASE/EntityStates?access_token=$TOKEN" | jq '.Items[] | select(.IsStateForCustomers==false) | .Name' | tr '\n' '|' | sed 's/|$//')

echo "=== Effort Summary by Status ==="

echo $STATES | tr '|' '\n' | while read STATE; do
  ENCODED=$(echo -n "$STATE" | jq -sRr @uri)

  TOTAL=$(curl -s "$BASE/UserStories?where=Project.Id%20eq%20$PROJECT_ID%20and%20EntityState.Name%20eq%20'$STATE'&take=1000&access_token=$TOKEN" | \
    jq '[.Items[].Effort] | add // 0')

  echo "$STATE: $TOTAL points"
done
```

### Workload by User

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
PROJECT_ID=222402

echo "=== Workload by User ==="

# Get all users in project
curl -s "$BASE/Users?where=Project.Id%20eq%20$PROJECT_ID&take=1000&access_token=$TOKEN" | \
  jq '.Items[] | .Id' | while read USER_ID; do
    # Get user name
    USER_NAME=$(curl -s "$BASE/Users/$USER_ID?access_token=$TOKEN" | jq -r '.FirstName + " " + .LastName')

    # Count and sum their items
    ITEMS=$(curl -s "$BASE/UserStories?where=Project.Id%20eq%20$PROJECT_ID%20and%20Owner.Id%20eq%20$USER_ID&take=1000&access_token=$TOKEN")

    COUNT=$(echo $ITEMS | jq '.Items | length')
    EFFORT=$(echo $ITEMS | jq '[.Items[].Effort] | add // 0')

    echo "$USER_NAME: $COUNT items, $EFFORT points"
  done
```

### Completion Status Report

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
PROJECT_ID=222402

TOTAL=$(curl -s "$BASE/UserStories?where=Project.Id%20eq%20$PROJECT_ID&take=1000&access_token=$TOKEN" | jq '.Items | length')
DONE=$(curl -s "$BASE/UserStories?where=Project.Id%20eq%20$PROJECT_ID%20and%20EntityState.Name%20eq%20'Done'&take=1000&access_token=$TOKEN" | jq '.Items | length')

PERCENT=$(echo "scale=2; $DONE * 100 / $TOTAL" | bc)

echo "=== Project Completion ==="
echo "Total: $TOTAL"
echo "Done: $DONE"
echo "Completion: $PERCENT%"
```

## Best Practices for Workflows

1. **Cache Reference Data**: Store state IDs, priority IDs, user IDs locally
2. **Handle Pagination**: Use loops for large result sets
3. **Error Checking**: Always validate responses
4. **Rate Limiting**: Add delays for bulk operations
5. **Logging**: Log all API calls for audit trails
6. **Transactions**: Group related operations
7. **Testing**: Test workflows with small datasets first

## Related

- [How To: Work with User Stories](./work-with-user-stories.md)
- [How To: Manage Assignments](./manage-assignments.md)
- [How To: Manage Work Items](./manage-work-items.md)
- [How To: Work with Collections](./work-with-collections.md)
- [API v1 Reference](../reference/api-v1-reference.md)
