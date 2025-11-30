# Tutorial: Team Analysis & Workload Management

Learn how to use tpcli to analyze team composition, track workload, and generate team reports.

## Overview

This tutorial shows you how to:
1. Get team information and metadata
2. Query all work items assigned to a team
3. Analyze team workload across features, stories, bugs, and tasks
4. Generate team capacity reports
5. Create automated team dashboards

## Getting Team Details

### Get a Single Team

```bash
./tpcli get Teams 1001
```

This returns the team's basic information including:
- Team name and owner
- Agile Release Train (ART) assignment
- Custom fields (people count, daily rate, JIRA project)
- Active/inactive status

### Extract Key Information

```bash
./tpcli get Teams 1001 | jq '{
  Name,
  Owner: .Owner.FirstName,
  Status: (if .IsActive then "Active" else "Inactive" end),
  PeopleCount: (.CustomFields[] | select(.Name == "People Count") | .Value),
  ART: .AgileReleaseTrain.Name,
  JIRA_Project: (.CustomFields[] | select(.Name == "JIRA Project Key") | .Value)
}'
```

Output:
```json
{
  "Name": "Example Team",
  "Owner": "Norbert",
  "Status": "Active",
  "PeopleCount": 2,
  "ART": "Data, Analytics and Digital",
  "JIRA_Project": "DAD"
}
```

## Find Team's Work Items

### Get All Features Assigned to Team

```bash
./tpcli list Features --where "Team.Id eq 1001" --take 100
```

This returns all features where the Team field matches the team ID. Use jq to summarize:

```bash
./tpcli list Features --where "Team.Id eq 1001" --take 100 | jq -r '.[] | "\(.Id): \(.Name) [\(.EntityState.Name)]"'
```

### Get All User Stories for Team

```bash
./tpcli list UserStories --where "Team.Id eq 1001" --take 100
```

Analyze by status:

```bash
./tpcli list UserStories --where "Team.Id eq 1001" --take 100 | jq -r '[group_by(.EntityState.Name)[] | {status: .[0].EntityState.Name, count: length, effort: map(.Effort) | add}] | .[] | "\(.status): \(.count) stories, \(.effort) effort"'
```

### Get Bugs and Tasks

```bash
# Get bugs
./tpcli list Bugs --where "Team.Id eq 1001" --take 100

# Get tasks
./tpcli list Tasks --where "Team.Id eq 1001" --take 100
```

## Team Workload Analysis

### Calculate Total Effort

```bash
STORIES=$(./tpcli list UserStories --where "Team.Id eq 1001" --take 100)

# Total effort
echo "$STORIES" | jq '[.[].Effort] | add // 0'

# By status
echo "$STORIES" | jq -r '[group_by(.EntityState.Name)[] | {status: .[0].EntityState.Name, effort: map(.Effort) | add}] | .[] | "\(.status): \(.effort) effort"'
```

### Track Time Spent vs Remaining

```bash
./tpcli list Tasks --where "Team.Id eq 1001" --take 100 | jq '{
  TotalSpent: [.[].TimeSpent] | add,
  TotalRemaining: [.[].TimeRemain] | add,
  ByStatus: [group_by(.EntityState.Name)[] | {status: .[0].EntityState.Name, spent: map(.TimeSpent) | add, remaining: map(.TimeRemain) | add}]
}'
```

### Analyze Completion Status

```bash
STORIES=$(./tpcli list UserStories --where "Team.Id eq 1001" --take 100)

echo "$STORIES" | jq '{
  Total: length,
  Done: [.[] | select(.EntityState.Name == "Done")] | length,
  Open: [.[] | select(.EntityState.Name != "Done")] | length,
  Completion: (([.[] | select(.EntityState.Name == "Done")] | length) / length * 100 | round) | "\(.)%"
}'
```

## Real-World Example: Team Dashboard

Here's a complete script to generate a team dashboard (also available as `scripts/describe-team.sh`):

```bash
#!/bin/bash

TEAM_ID=1001
./tpcli get Teams $TEAM_ID | jq '{Name, Owner: .Owner.FirstName, PeopleCount: (.CustomFields[] | select(.Name == "People Count") | .Value)}'

echo "=== Workload Summary ==="

FEATURES=$(./tpcli list Features --where "Team.Id eq $TEAM_ID" --take 100)
STORIES=$(./tpcli list UserStories --where "Team.Id eq $TEAM_ID" --take 100)
BUGS=$(./tpcli list Bugs --where "Team.Id eq $TEAM_ID" --take 100)
TASKS=$(./tpcli list Tasks --where "Team.Id eq $TEAM_ID" --take 100)

echo "Features:  $(echo "$FEATURES" | jq 'length')"
echo "Stories:   $(echo "$STORIES" | jq 'length')"
echo "Bugs:      $(echo "$BUGS" | jq 'length')"
echo "Tasks:     $(echo "$TASKS" | jq 'length')"

echo ""
echo "=== Story Effort Summary ==="
echo "$STORIES" | jq -r '[group_by(.EntityState.Name)[] | {status: .[0].EntityState.Name, count: length, effort: map(.Effort) | add}] | .[] | "\(.status): \(.count) stories, \(.effort) effort"'

echo ""
echo "=== Task Time Summary ==="
echo "$TASKS" | jq '{
  TotalSpent: ([.[].TimeSpent] | add // 0),
  TotalRemaining: ([.[].TimeRemain] | add // 0)
}'
```

Run it:

```bash
TP_TOKEN=your_token TP_URL=https://instance.tpondemand.com ./scripts/describe-team.sh 1001
```

## Advanced: Team Member Assignments

### Get Assignments for a Team

```bash
./tpcli list Assignments --where "Team.Id eq 1001" --take 100
```

### Find What Each Team Member is Working On

```bash
# Get all assignments to team members
./tpcli list Assignments --where "GeneralUser is not null" --take 1000 | jq -r '[group_by(.GeneralUser.FirstName)[] | {member: .[0].GeneralUser.FirstName, assignments: length}] | .[] | "\(.member): \(.assignments) assignments"'
```

### Calculate Workload Per Person

```bash
#!/bin/bash

TEAM_ID=1001

# Get all stories assigned to team
STORIES=$(./tpcli list UserStories --where "Team.Id eq $TEAM_ID" --take 1000)

# Group by assignee
echo "$STORIES" | jq -r '[group_by(.AssignedUser.FirstName // "Unassigned")[] | {person: .[0].AssignedUser.FirstName // "Unassigned", count: length, effort: map(.Effort) | add}] | .[] | "\(.person): \(.count) stories, \(.effort) effort"'
```

## Use Cases

### Use Case 1: Weekly Team Standup Report

```bash
#!/bin/bash

TEAM_ID=1001

echo "=== Weekly Standup Report ==="
echo "Generated: $(date)"
echo ""

./tpcli get Teams $TEAM_ID | jq '.Name'

echo ""
echo "Active Stories:"
./tpcli list UserStories --where "Team.Id eq $TEAM_ID and EntityState.Name eq 'In Progress'" --take 10 | jq -r '.[] | "  • \(.Name) (Owner: \(.Owner.FirstName))"'

echo ""
echo "Blocked Items:"
./tpcli list UserStories --where "Team.Id eq $TEAM_ID and Tags contains 'blocked'" --take 10 | jq -r '.[] | "  • \(.Name) - Blocked"'

echo ""
echo "Ready for Review:"
./tpcli list UserStories --where "Team.Id eq $TEAM_ID and EntityState.Name eq 'Testing'" --take 10 | jq -r '.[] | "  • \(.Name)"'
```

### Use Case 2: Capacity Planning

```bash
#!/bin/bash

TEAM_ID=1001

echo "=== Team Capacity Analysis ==="

PEOPLE_COUNT=$(./tpcli get Teams $TEAM_ID | jq '.CustomFields[] | select(.Name == "People Count") | .Value')
OPEN_EFFORT=$(./tpcli list UserStories --where "Team.Id eq $TEAM_ID and EntityState.Name != 'Done'" --take 1000 | jq '[.[].Effort] | add // 0')

echo "Team Size: $PEOPLE_COUNT people"
echo "Open Effort: $OPEN_EFFORT points"

if [ "$PEOPLE_COUNT" -gt 0 ]; then
  AVG_PER_PERSON=$(echo "$OPEN_EFFORT / $PEOPLE_COUNT" | bc -l | awk '{printf "%.1f", $0}')
  echo "Average per person: $AVG_PER_PERSON points"
fi
```

### Use Case 3: Burndown Tracking

```bash
#!/bin/bash

TEAM_ID=1001

echo "=== Sprint Burndown ==="

./tpcli list UserStories --where "Team.Id eq $TEAM_ID and Iteration.IsCurrent eq 'true'" --take 100 | jq '{
  Total: length,
  TotalEffort: [.[].Effort] | add,
  Completed: [.[] | select(.EntityState.Name == "Done")] | length,
  CompletedEffort: [.[] | select(.EntityState.Name == "Done") | .Effort] | add,
  Remaining: [.[] | select(.EntityState.Name != "Done")] | length,
  RemainingEffort: [.[] | select(.EntityState.Name != "Done") | .Effort] | add
}'
```

## Tips & Tricks

1. **Use `--take 1000`** for comprehensive analysis (API supports up to 1000 items)
2. **Filter early** - Use `where` clause to reduce data before processing
3. **Cache results** - Save API responses to files to avoid repeated calls
4. **Pipe to jq** - Powerful for analyzing and formatting JSON responses
5. **Use custom fields** - Team has people count and JIRA project info

## Complete Script Example

See `scripts/describe-team.sh` for a complete, production-ready team analysis script that includes:
- Team information
- Feature workload
- Story effort tracking
- Bug and task summary
- Total workload calculation

Usage:

```bash
TP_TOKEN=your_token TP_URL=https://instance.tpondemand.com ./scripts/describe-team.sh 1001
```

## Related Documentation

- [How To: Manage Assignments](../how-to/manage-assignments.md)
- [How To: Manage Work Items](../how-to/manage-work-items.md)
- [How To: API Use Cases](../how-to/api-use-cases.md)
- [Reference: User Story Structure](../reference/user-story-structure.md)
