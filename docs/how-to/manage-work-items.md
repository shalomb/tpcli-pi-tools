# How To: Manage Work Items

Complete guide to managing work item properties and operations in TargetProcess.

**Source**: [IBM TargetProcess API v1 Work Item Operations](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=cases-work-items)

## Work Items Overview

Work items are assignable entities that can be managed and tracked:
- User Stories
- Bugs
- Tasks
- Test Plans
- Requests

All work items share common management operations for dates, priorities, tags, and status.

## Common Work Item Operations

### Update Planned Dates

Set when a work item is planned to start and end.

**Update Planned Start Date**

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "PlannedStartDate": "/Date(1764500000000-0500)/"
  }?access_token=TOKEN'
```

**Update Planned End Date**

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "PlannedEndDate": "/Date(1764600000000-0500)/"
  }?access_token=TOKEN'
```

**Update Both Dates**

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "PlannedStartDate": "/Date(1764500000000-0500)/",
    "PlannedEndDate": "/Date(1764600000000-0500)/"
  }?access_token=TOKEN'
```

### Calculate Timestamps from Dates

**Convert ISO 8601 to TargetProcess Format**

```bash
#!/bin/bash

# ISO 8601 date: 2024-12-20
DATE="2024-12-20"

# Convert to Unix timestamp (milliseconds)
TIMESTAMP=$(($(date -d "$DATE" +%s) * 1000))
OFFSET="-0500"

# Format for TargetProcess
TP_DATE="/Date($TIMESTAMP$OFFSET)/"

echo "TargetProcess format: $TP_DATE"
# Output: /Date(1734067200000-0500)/
```

**Use jq for JSON Date Handling**

```bash
#!/bin/bash

# Create date string in TargetProcess format
UNIX_MS=$(date -d "2024-12-20" +%s)000
TP_DATE="/Date($UNIX_MS-0500)/"

# Update item with new date
curl -X POST https://instance.tpondemand.com/api/v1/Bugs/2028655 \
  -H "Content-Type: application/json" \
  -d '{
    "PlannedStartDate": "'$TP_DATE'"
  }?access_token=TOKEN'
```

## Managing Priority and Rank

### Update Priority Level

```bash
# Set to High priority (ID 5)
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "Priority": {"Id": 5}
  }?access_token=TOKEN'
```

### Adjust Rank/Numeric Priority

The `NumericPriority` field controls the ordering of items.

**Get Current Priority Values**

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories?include=[Id,Name,NumericPriority]&orderBy=NumericPriority&take=10&access_token=TOKEN"
```

**Move Item Up in Priority**

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get current priority
CURRENT=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq '.NumericPriority')

# Increase priority (higher number = higher priority in some systems)
NEW_PRIORITY=$(echo "$CURRENT + 1000" | bc)

# Update
curl -X POST "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "NumericPriority": '${NEW_PRIORITY}'
  }'
```

**Move Item Down in Priority**

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get current priority
CURRENT=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq '.NumericPriority')

# Decrease priority
NEW_PRIORITY=$(echo "$CURRENT - 1000" | bc)

# Update
curl -X POST "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "NumericPriority": '${NEW_PRIORITY}'
  }'
```

## Managing Tags

Tags are text labels that can be added to work items.

### Add Tags

```bash
# Add tags (overwrites existing)
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "Tags": "frontend,auth,security"
  }?access_token=TOKEN'
```

### Get Current Tags

```bash
curl "https://instance.tpondemand.com/api/v1/UserStories/2028653?include=[Tags]&access_token=TOKEN" | jq '.Tags'
```

### Append Tags (Without Overwriting)

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Get current tags
CURRENT_TAGS=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq -r '.Tags // ""')

# Add new tags
NEW_TAG="urgent"

# Combine (avoid duplicates)
if [[ "$CURRENT_TAGS" == *"$NEW_TAG"* ]]; then
  TAGS=$CURRENT_TAGS
else
  TAGS="$CURRENT_TAGS,$NEW_TAG"
fi

# Remove leading comma if any
TAGS=$(echo "$TAGS" | sed 's/^,//')

# Update
curl -X POST "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Tags": "'$TAGS'"
  }'
```

### Remove Specific Tag

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"
TAG_TO_REMOVE="urgent"

# Get current tags
CURRENT_TAGS=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" | jq -r '.Tags // ""')

# Remove tag
TAGS=$(echo "$CURRENT_TAGS" | tr ',' '\n' | grep -v "^$TAG_TO_REMOVE$" | tr '\n' ',' | sed 's/,$//')

# Update
curl -X POST "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Tags": "'$TAGS'"
  }'
```

### Query Items by Tag

```bash
# Find all user stories with "urgent" tag
curl "https://instance.tpondemand.com/api/v1/UserStories?where=Tags%20contains%20'urgent'&access_token=TOKEN"

# URL decoded
/api/v1/UserStories?where=Tags contains 'urgent'
```

### Bulk Tag Management

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Add tag to all high-priority items
ITEMS=$(curl -s "$BASE/UserStories?where=Priority.Id%20eq%205&access_token=$TOKEN" | jq '.Items[].Id')

for ITEM_ID in $ITEMS; do
  echo "Adding tag to story $ITEM_ID..."

  CURRENT=$(curl -s "$BASE/UserStories/$ITEM_ID?access_token=$TOKEN" | jq -r '.Tags // ""')
  NEW_TAGS="$CURRENT,needs-review"
  NEW_TAGS=$(echo "$NEW_TAGS" | sed 's/^,//')

  curl -X POST "$BASE/UserStories/$ITEM_ID?access_token=$TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "Tags": "'$NEW_TAGS'"
    }'
done
```

## Managing Effort and Time

### Update Effort

```bash
# Set initial effort to 8 points
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "Effort": 8
  }?access_token=TOKEN'

# Update to 13 points
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "Effort": 13
  }?access_token=TOKEN'
```

### Update Time Tracking

```bash
# Set time spent and time remaining
curl -X POST https://instance.tpondemand.com/api/v1/Tasks/1234567 \
  -H "Content-Type: application/json" \
  -d '{
    "TimeSpent": 5.5,
    "TimeRemain": 2.5
  }?access_token=TOKEN'
```

### Calculate Effort to Do

```bash
# Set effort completed and calculate remaining
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "EffortCompleted": 6,
    "EffortToDo": 2
  }?access_token=TOKEN'
```

## Managing Status and State

### Change Item Status

```bash
# Mark as Done (assuming EntityState ID 1750)
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "EntityState": {"Id": 1750}
  }?access_token=TOKEN'
```

### Get Available States

```bash
curl "https://instance.tpondemand.com/api/v1/EntityStates?access_token=TOKEN" | jq '.Items[] | {Id, Name}'
```

### Query Items by Status

```bash
# Get all open items
curl "https://instance.tpondemand.com/api/v1/UserStories?where=EntityState.Name%20eq%20'Open'&access_token=TOKEN"

# Get all in-progress items
curl "https://instance.tpondemand.com/api/v1/UserStories?where=EntityState.Name%20eq%20'In Progress'&access_token=TOKEN"
```

## Combined Workflow: Update Multiple Properties

### Comprehensive Item Update

```bash
curl -X POST https://instance.tpondemand.com/api/v1/UserStories/2028653 \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "User can securely reset password",
    "Description": "Enhanced with security considerations",
    "Effort": 13,
    "Priority": {"Id": 5},
    "EntityState": {"Id": 1750},
    "PlannedStartDate": "/Date(1764500000000-0500)/",
    "PlannedEndDate": "/Date(1764600000000-0500)/",
    "Tags": "security,frontend,auth",
    "TimeSpent": 8.5,
    "TimeRemain": 4.5
  }?access_token=TOKEN'
```

## Bulk Operations

### Update Multiple Items

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Tag all high-priority items in project
ITEMS=$(curl -s "$BASE/UserStories?where=Project.Id%20eq%20222402%20and%20Priority.Id%20eq%205&access_token=$TOKEN" | jq '.Items[].Id')

for ITEM_ID in $ITEMS; do
  echo "Updating story $ITEM_ID..."

  curl -X POST "$BASE/UserStories/$ITEM_ID?access_token=$TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "Tags": "high-priority,urgent",
      "PlannedStartDate": "/Date(1764500000000-0500)/"
    }'
done
```

### Update with Conditional Logic

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Update priority based on effort
curl -s "$BASE/UserStories?where=Effort%20gt%2010&take=1000&access_token=$TOKEN" | \
  jq '.Items[]' | while read -r item; do
    ITEM_ID=$(echo "$item" | jq '.Id')

    echo "Item $ITEM_ID has high effort, setting high priority..."

    curl -X POST "$BASE/UserStories/$ITEM_ID?access_token=$TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "Priority": {"Id": 5}
      }'
  done
```

## Error Handling

### Validate Before Update

```bash
#!/bin/bash

STORY_ID=2028653
TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Check if item exists
ITEM=$(curl -s "$BASE/UserStories/$STORY_ID?access_token=$TOKEN")

if [ -z "$(echo $ITEM | jq '.Id // empty')" ]; then
  echo "Error: Story $STORY_ID not found"
  exit 1
fi

# Item exists, proceed with update
RESULT=$(curl -s -X POST "$BASE/UserStories/$STORY_ID?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Effort": 8
  }')

# Check for errors
if [ -z "$(echo $RESULT | jq '.Id // empty')" ]; then
  echo "Error updating story:"
  echo $RESULT | jq '.'
  exit 1
fi

echo "Successfully updated story"
```

### Handle Invalid State Transitions

```bash
#!/bin/bash

TOKEN="your_token"
BASE="https://instance.tpondemand.com/api/v1"

# Try to transition to invalid state
RESULT=$(curl -s -X POST "$BASE/UserStories/2028653?access_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "EntityState": {"Id": 999999}
  }')

# Check response
if echo $RESULT | jq -e '.Message' > /dev/null; then
  echo "State transition failed:"
  echo $RESULT | jq '.Message'
  exit 1
fi
```

## Best Practices

1. **Always Validate Dates**: Use proper ISO format conversion
2. **Cache Priority Values**: Don't hardcode IDs, query EntityStates
3. **Handle Tags Carefully**: Use proper concatenation to avoid duplicates
4. **Batch Operations**: Group updates when possible
5. **Check Preconditions**: Verify state exists before updating
6. **Error Handling**: Always check response for errors
7. **Audit Trail**: Log all changes for tracking

## Related

- [How To: Work with User Stories](./work-with-user-stories.md)
- [How To: Manage Assignments](./manage-assignments.md)
- [Reference: User Story Structure](../reference/user-story-structure.md)
- [API v1 Reference](../reference/api-v1-reference.md)
