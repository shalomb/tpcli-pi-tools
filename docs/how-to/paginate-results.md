# How To: Paginate Results

Complete guide to pagination in TargetProcess API.

**Source**: [IBM TargetProcess API v1 Paging](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-paging)

## Pagination Basics

TargetProcess API returns results in pages to avoid overwhelming responses. Each page contains a limited number of items.

### Default Behavior

- **Default page size**: 25 items
- **Maximum page size**: 1000 items
- **Response includes**: `Items` (results), `Next` (link to next page), `Prev` (link to previous page)

## Pagination Parameters

### `take` - Items Per Page

Specifies how many items to return per page (max 1000).

```bash
# Get 50 items per page
./tpcli list UserStories --take 50

# Get maximum items per page
./tpcli list UserStories --take 1000

# Use default (25 items)
./tpcli list UserStories
```

### `skip` - Offset

Specifies how many items to skip before returning results.

```bash
# Skip first 100 items, return next 50
./tpcli list UserStories --skip 100 --take 50

# Get second page (items 26-50)
./tpcli list UserStories --skip 25 --take 25

# Get third page (items 51-75)
./tpcli list UserStories --skip 50 --take 25
```

## Response Format

### Successful Response

```json
{
  "Items": [
    {"Id": 1, "Name": "Story 1"},
    {"Id": 2, "Name": "Story 2"},
    ...
  ],
  "Next": "/api/v1/UserStories?take=25&skip=25",
  "Prev": "/api/v1/UserStories?take=25&skip=0"
}
```

### Last Page (No More Results)

```json
{
  "Items": [
    {"Id": 101, "Name": "Story 101"},
    {"Id": 102, "Name": "Story 102"}
  ],
  "Prev": "/api/v1/UserStories?take=25&skip=75"
}
```

Note: `Next` is omitted when there are no more results.

## Common Pagination Patterns

### Iterate Through All Results

```bash
#!/bin/bash

SKIP=0
TAKE=100
BASE_URL="https://instance.tpondemand.com"
TOKEN="your_access_token"

while true; do
  # Get page
  RESPONSE=$(curl -s "$BASE_URL/api/v1/UserStories?take=$TAKE&skip=$SKIP&access_token=$TOKEN")

  # Process items
  echo "$RESPONSE" | jq '.Items[]' | while read item; do
    echo "Processing: $item"
  done

  # Check if there's a next page
  NEXT=$(echo "$RESPONSE" | jq -r '.Next // empty')

  if [ -z "$NEXT" ]; then
    break
  fi

  SKIP=$((SKIP + TAKE))
done
```

### Collect All Results into Array

```bash
#!/bin/bash

SKIP=0
TAKE=500
ALL_ITEMS=()
BASE_URL="https://instance.tpondemand.com"
TOKEN="your_access_token"

while true; do
  RESPONSE=$(curl -s "$BASE_URL/api/v1/UserStories?take=$TAKE&skip=$SKIP&access_token=$TOKEN")

  # Add items to array
  ITEMS=$(echo "$RESPONSE" | jq '.Items[]')
  ALL_ITEMS+=("$ITEMS")

  # Check if there are more results
  NEXT=$(echo "$RESPONSE" | jq -r '.Next // empty')

  if [ -z "$NEXT" ]; then
    break
  fi

  SKIP=$((SKIP + TAKE))
done

# Output all items as JSON array
echo "[" > all_stories.json
printf '%s\n' "${ALL_ITEMS[@]}" | paste -sd ',' >> all_stories.json
echo "]" >> all_stories.json
```

### Paginate with Filtering

```bash
# Get all Open user stories, 100 per page
./tpcli list UserStories \
  --where "EntityState.Name eq 'Open'" \
  --take 100

# Get second page (skip first 100)
./tpcli list UserStories \
  --where "EntityState.Name eq 'Open'" \
  --take 100 \
  --skip 100
```

## Pagination with Collections

### Inner Collections Pagination

When you have collections (child items) within parent resources, use the `innerTake` parameter to control how many items from each collection are returned.

#### Default Behavior (Without innerTake)

```bash
# Returns 25 items from each collection by default
curl "https://instance.tpondemand.com/api/v1/UserStories?include=[name,tasks]&access_token=TOKEN"
```

Result:
```json
{
  "Items": [
    {
      "Id": 1,
      "Name": "Story 1",
      "Tasks": [
        {"Id": 101},
        {"Id": 102},
        ...
        {"Id": 125}  // Only first 25 tasks
      ]
    }
  ]
}
```

#### With innerTake (Get All Collection Items)

```bash
# Get 1000 items from each collection
curl "https://instance.tpondemand.com/api/v1/UserStories?include=[name,tasks]&innerTake=1000&access_token=TOKEN"
```

This ensures you get all related items even if a single parent has many children.

#### Example: Get All Comments on All Stories

```bash
# Scenario: Some stories might have many comments
curl "https://instance.tpondemand.com/api/v1/UserStories?include=[name,comments]&take=500&innerTake=1000&access_token=TOKEN"
```

This retrieves:
- Up to 500 User Stories (take=500)
- Up to 1000 comments per story (innerTake=1000)

## Performance Optimization

### Choose Appropriate Page Size

```bash
# Small dataset or quick check
./tpcli list UserStories --take 25

# Medium dataset
./tpcli list UserStories --take 100

# Large dataset
./tpcli list UserStories --take 500

# Maximum performance (but heavy response)
./tpcli list UserStories --take 1000
```

### Use Filtering to Reduce Results

```bash
# Instead of getting all and filtering locally:
# ❌ Bad: retrieves everything
./tpcli list UserStories --take 1000

# ✅ Good: API filters before returning
./tpcli list UserStories \
  --where "EntityState.Name eq 'Open'" \
  --take 100
```

### Combine with Field Selection

```bash
# Return only needed fields to reduce payload
./tpcli list UserStories \
  --fields "Id,Name,Priority" \
  --take 100
```

## Handling Large Result Sets

### Count Total Results

⚠️ **Note**: TargetProcess doesn't provide a total count endpoint. Use this pattern:

```bash
#!/bin/bash

COUNT=0
SKIP=0
TAKE=500
BASE_URL="https://instance.tpondemand.com"
TOKEN="your_access_token"

while true; do
  RESPONSE=$(curl -s "$BASE_URL/api/v1/UserStories?take=$TAKE&skip=$SKIP&access_token=$TOKEN")

  ITEMS_COUNT=$(echo "$RESPONSE" | jq '.Items | length')
  COUNT=$((COUNT + ITEMS_COUNT))

  NEXT=$(echo "$RESPONSE" | jq -r '.Next // empty')
  if [ -z "$NEXT" ]; then
    break
  fi

  SKIP=$((SKIP + TAKE))
done

echo "Total User Stories: $COUNT"
```

### Process Large Datasets Efficiently

```bash
#!/bin/bash

SKIP=0
TAKE=1000
BASE_URL="https://instance.tpondemand.com"
TOKEN="your_access_token"
BATCH_FILE="batch_$SKIP.json"

# Process in batches of 1000
while true; do
  echo "Processing batch starting at $SKIP..."

  RESPONSE=$(curl -s "$BASE_URL/api/v1/UserStories?take=$TAKE&skip=$SKIP&access_token=$TOKEN")

  # Save batch to file
  echo "$RESPONSE" | jq '.Items' > "batch_$SKIP.json"

  # Process batch
  process_batch "batch_$SKIP.json"

  # Check for next page
  NEXT=$(echo "$RESPONSE" | jq -r '.Next // empty')
  if [ -z "$NEXT" ]; then
    break
  fi

  SKIP=$((SKIP + TAKE))
done

process_batch() {
  local file=$1
  echo "Processing $file..."
  # Your custom processing logic here
}
```

## Pagination in Filtering Scenarios

### Paginate Filtered Results

```bash
# Get high-priority stories, 50 per page
./tpcli list UserStories \
  --where "Priority.Name eq 'High' or Priority.Name eq 'Urgent'" \
  --take 50

# Get next page
./tpcli list UserStories \
  --where "Priority.Name eq 'High' or Priority.Name eq 'Urgent'" \
  --take 50 \
  --skip 50
```

### Paginate Date-Range Results

```bash
# Get stories from this month, page by page
./tpcli list UserStories \
  --where "CreateDate gt '2024-11-01' and CreateDate lt '2024-12-01'" \
  --take 100 \
  --skip 0

# Next page
./tpcli list UserStories \
  --where "CreateDate gt '2024-11-01' and CreateDate lt '2024-12-01'" \
  --take 100 \
  --skip 100
```

## Error Handling

### Invalid Skip Value

```bash
# If skip exceeds total results, you get empty Items
./tpcli list UserStories --skip 999999 --take 100

# Response:
{
  "Items": [],
  "Prev": "/api/v1/UserStories?take=100&skip=999900"
}
```

### Invalid Take Value

```bash
# If take exceeds 1000, API returns 1000
./tpcli list UserStories --take 9999  # Capped at 1000

# If take is negative or zero, API returns default (25)
./tpcli list UserStories --take 0  # Returns 25
```

## Best Practices

1. **Use Reasonable Page Sizes**: 50-500 items is usually optimal
2. **Cache Total Counts**: If you need to know total results, count once and cache
3. **Sort for Consistency**: Use `--orderBy` for predictable pagination
4. **Handle Edge Cases**: Account for pages changing while iterating
5. **Use innerTake for Collections**: Always set innerTake when including collections
6. **Filter Before Pagination**: Reduce dataset size with where clauses
7. **Monitor Performance**: Large page sizes consume more bandwidth

## Related

- [API v1 Reference](../reference/api-v1-reference.md)
- [Query Syntax Reference](../reference/query-syntax.md)
- [How to Work with Collections](./work-with-collections.md)
