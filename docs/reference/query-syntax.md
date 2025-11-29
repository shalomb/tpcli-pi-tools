# Reference: Query Syntax

Complete reference for TargetProcess filtering and query expressions.

**Source**: [IBM TargetProcess Sorting and Filters](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas?topic=v1-sorting-filters)

## Filtering Basics

Filter using the `where` parameter:

```bash
./tpcli list Bugs --where "EntityState.Name eq 'Open'"
```

## Comparison Operators

### Equality Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `eq` | `Name eq 'Bug'` | Equals |
| `ne` | `Status ne 'Closed'` | Not equals |

### Numeric Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `gt` | `Id gt 1000` | Greater than |
| `gte` | `Id gte 1000` | Greater than or equal |
| `lt` | `Priority.Id lt 5` | Less than |
| `lte` | `Priority.Id lte 5` | Less than or equal |

### String Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `contains` | `Name contains 'auth'` | Contains substring |
| `not contains` | `Tags not contains 'urgent'` | Does not contain |

### Collection Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `in` | `Id in (1,2,3)` | In list |

### Null Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `is null` | `Description is null` | Is empty |
| `is not null` | `Description is not null` | Is not empty |

## Logical Operators

### AND

Combine multiple conditions:

```bash
./tpcli list Bugs \
  --where "EntityState.Name eq 'Open' and Priority.Name eq 'High'"
```

Both conditions must be true.

### OR

❌ **NOT SUPPORTED** in API v1

Workaround: Use separate queries and merge results

### Parentheses

Optional grouping:

```bash
# Both equivalent:
./tpcli list Bugs --where "Project.Id eq 123 and EntityState.Name eq 'Open'"

./tpcli list Bugs --where "(Project.Id eq 123) and (EntityState.Name eq 'Open')"
```

## Nested Field Access

Access related entity fields with dot notation:

```bash
Owner.FirstName         # Owner's first name
Project.Name            # Project name
EntityState.Name        # Status name
Priority.Id             # Priority ID
Feature.Epic.Name       # Epic of parent feature
```

## Date Filtering

Filter by date (ISO 8601 format):

```bash
# Created after date
./tpcli list UserStories --where "CreateDate gt '2024-01-01'"

# Modified in date range
./tpcli list Tasks \
  --where "ModifyDate gte '2024-11-01' and ModifyDate lt '2024-12-01'"
```

## Custom Fields

### Standard custom fields

```bash
./tpcli list Bugs --where "CustomFields.RiskLevel eq 'High'"
```

### Custom field with spaces

Wrap in quotes:

```bash
./tpcli list UserStories --where "'CustomFields.Field Name' eq 'Value'"
```

### Filter by custom field type

- Text: `eq`, `ne`, `contains`
- Number: `gt`, `lt`, `gte`, `lte`, `eq`
- Date: `gt`, `lt`, `gte`, `lte`
- Dropdown: `eq`, `ne`

### ❌ Not supported

Cannot filter by Calculated Custom Fields

## Tags

Filter items with tags:

```bash
# Has tag 'urgent'
./tpcli list UserStories --where "Tags contains 'urgent'"

# Tag with spaces (in double quotes inside)
./tpcli list UserStories --where "Tags contains '\"two word tag\"'"

# Multiple words tag with wildcards
./tpcli list UserStories --where "Tags contains '*abc*'"
```

## Wildcards

Use `*` for wildcard matching:

```bash
# Starts with 'auth'
./tpcli list Bugs --where "Name contains 'auth*'"

# Ends with 'bug'
./tpcli list Bugs --where "Name contains '*bug'"

# Contains 'bug' anywhere
./tpcli list Bugs --where "Name contains '*bug*'"

# ❌ NOT supported: wildcards in middle
# ./tpcli list Bugs --where "Name contains 'b*g'"  # WRONG
```

## Escaping

### Escape single quotes

Use backslash:

```bash
./tpcli list UserStories --where "Name contains '\\''"
```

## Boolean Fields

Filter by true/false:

```bash
# Active users
./tpcli list Users --where "IsActive eq 'true'"

# Inactive
./tpcli list Users --where "IsActive eq 'false'"
```

## Complex Examples

### Open bugs in specific project, high priority

```bash
./tpcli list Bugs \
  --where "Project.Id eq 1234 and EntityState.Name eq 'Open' and Priority.Name eq 'High'"
```

### Tasks assigned to specific user

```bash
./tpcli list Tasks \
  --where "AssignedUser.Id eq 456"
```

### Items without description

```bash
./tpcli list UserStories \
  --where "Description is null"
```

### Created last 7 days

```bash
./tpcli list UserStories \
  --where "CreateDate gt '2024-11-22'"
```

### Items in current iteration

```bash
./tpcli list UserStories \
  --where "Iteration.IsCurrent eq 'true'"
```

## Escaping Special Characters

### In tpcli shell

Wrap complex filters in single or double quotes:

```bash
# Single quotes
./tpcli list Bugs --where 'Name contains "special"'

# Double quotes
./tpcli list Bugs --where "Name contains 'special'"
```

### In shell scripts

Use proper quoting:

```bash
#!/bin/bash
FILTER="EntityState.Name eq 'Open'"
./tpcli list Bugs --where "$FILTER"
```

## Filter Limitations

### Not supported

- ❌ OR operator
- ❌ Filtering by nested collection contents
- ❌ Calculated custom fields
- ❌ Filtering by attachments

### Workarounds

For OR logic, make separate API calls:

```bash
# Get high priority bugs
./tpcli list Bugs --where "Priority.Name eq 'High'" > high.json

# Get urgent bugs
./tpcli list Bugs --where "Tags contains 'urgent'" > urgent.json

# Merge results
jq -s 'map(.Items[]) | unique_by(.Id)' high.json urgent.json
```

## Sorting

Sort results with `orderBy`:

```bash
# Ascending (default)
./tpcli list UserStories --where "..." --orderBy=CreateDate

# Descending
./tpcli list UserStories --where "..." --orderByDesc=CreateDate

# Multiple sort (see API v2 reference)
```

**Note**: tpcli currently supports basic sorting. See API v2 for advanced multi-field sorting.

## Performance Tips

1. **Filter early** - Use `--where` to reduce result set
2. **Limit results** - Use `--take` to avoid huge responses
3. **Select fields** - Use `--fields` to reduce data transfer
4. **Avoid wildcards at start** - `*text` is slower than `text*`
5. **Index-friendly filters** - Filter by ID or state is fast

## Related

- [API v1 Reference](api-v1-reference.md)
- [API v2 Reference](api-v2-reference.md)
- [How to List and Filter](../how-to/list-and-filter.md)
