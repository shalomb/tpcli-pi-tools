# Reference: Entity Types

Complete list of TargetProcess entity types available via API.

**Source**: [IBM TargetProcess API Reference](https://www.ibm.com/docs/en/targetprocess/tp-dev-hub/saas)

## Entity Hierarchy

```
GeneralEntity (base for all)
├── AssignableEntity (can be assigned to users)
│   ├── InboundAssignable
│   │   ├── Epic
│   │   ├── Feature
│   │   ├── UserStory
│   │   ├── Task
│   │   ├── Bug
│   │   ├── TestPlan
│   │   ├── TestPlanRun
│   │   └── Request
│   └── OutboundAssignable
│
├── Project
├── Program
├── Release
├── Iteration
├── TeamIteration
├── Team
├── User
└── TestCase
```

## Work Items (Assignable)

These can be assigned to users, have status, priority, and effort.

### Epic
```
API: /api/v1/Epics
Single: Epic
Assignable: Yes
Description: High-level business initiative
Common fields: Name, Description, Owner, AssignedUser, Priority, Effort, EntityState
Example: Enterprise transformation initiative
```

### Feature
```
API: /api/v1/Features
Single: Feature
Assignable: Yes
Description: Major user-facing feature
Common fields: Name, Description, Owner, AssignedUser, Priority, Effort, EntityState, Parent (Epic)
Example: User authentication system
```

### User Story
```
API: /api/v1/UserStories
Single: UserStory
Assignable: Yes
Description: User-facing work item ("As a... I want... So that...")
Common fields: Name, Description, Owner, AssignedUser, Priority, Effort, EntityState, Parent (Feature/Epic)
Example: "Add login button to homepage"
```

### Task
```
API: /api/v1/Tasks
Single: Task
Assignable: Yes
Description: Unit of work, usually subtask of User Story
Common fields: Name, Description, Owner, AssignedUser, Priority, Effort, TimeSpent, TimeRemain, EntityState, Parent
Example: "Design login form layout"
```

### Bug
```
API: /api/v1/Bugs
Single: Bug
Assignable: Yes
Description: Defect or issue to fix
Common fields: Name, Description, Owner, AssignedUser, Priority, Severity, Effort, EntityState, Parent
Example: "Login button not responsive on mobile"
```

### Test Plan
```
API: /api/v1/TestPlans
Single: TestPlan
Assignable: Yes
Description: Set of test cases
Common fields: Name, Description, Owner, AssignedUser, EntityState
```

### Test Plan Run
```
API: /api/v1/TestPlanRuns
Single: TestPlanRun
Assignable: Yes
Description: Execution of a test plan
Common fields: Name, EntityState, TestPlan, StartDate, EndDate
```

### Request
```
API: /api/v1/Requests
Single: Request
Assignable: Yes
Description: Customer request or support ticket
Common fields: Name, Description, Owner, AssignedUser, EntityState, Priority
```

## Containers

These group other entities but cannot be assigned.

### Project
```
API: /api/v1/Projects
Single: Project
Description: Top-level container for work
Common fields: Id, Name, Description, Owner, Process, StartDate, EndDate
Children: All assignables, Iterations, Releases, Teams
Example: "Mobile App Development", "Backend Services"
```

### Program
```
API: /api/v1/Programs
Single: Program
Description: Portfolio-level grouping (multi-project)
Common fields: Id, Name, Description, Owner
Children: Projects
```

### Release
```
API: /api/v1/Releases
Single: Release
Description: Product version or milestone
Common fields: Id, Name, Description, ReleaseDate, Project, StartDate, EndDate
Example: "v2.0", "Q4 2024 Release"
```

### Iteration
```
API: /api/v1/Iterations
Single: Iteration
Description: Sprint or iteration cycle
Common fields: Id, Name, Project, StartDate, EndDate, IsCurrent, Process
Example: "Sprint 1", "Week of Nov 29"
```

### Team Iteration
```
API: /api/v1/TeamIterations
Single: TeamIteration
Description: Team-specific iteration
Common fields: Id, Name, Team, StartDate, EndDate
```

### Team
```
API: /api/v1/Teams
Single: Team
Description: Group of users
Common fields: Id, Name, Project, Description, Owner
Children: Users, TeamIterations
```

## Entity Management

### User
```
API: /api/v1/Users
Single: User
Description: TargetProcess user account
Common fields: Id, FirstName, LastName, Email, Login, IsActive, IsAdministrator, Role
```

### Test Case
```
API: /api/v1/TestCases
Single: TestCase
Description: Individual test case
Common fields: Id, Name, Description, Owner, EntityState, TestPlan
```

### Custom Field
```
API: /api/v1/CustomFields
Single: CustomField
Description: Custom attribute definition
Common fields: Id, Name, Type, Project, EntityTypes, Values
```

## Metadata

### Entity State
```
Name: EntityState
Description: Work item status (Open, In Progress, Done, etc.)
Attributes: Name, NumericPriority
Example states: Open, In Progress, Testing, Done, Closed
```

### Priority
```
Name: Priority
Description: Work item priority level
Attributes: Name, Importance (1-10)
Example priorities: Low, Normal, High, Urgent
```

### Severity
```
Name: Severity
Description: Bug severity level
Attributes: Name, Importance
Example values: Minor, Major, Critical
```

### Process
```
Name: Process
Description: Work process definition (Scrum, Kanban, etc.)
Attributes: Name, Characteristics
```

## Generic Types

### Assignable (Generic)
```
API: /api/v1/Assignables
Description: Base type for all assignable items
Returns: All Epic, Feature, UserStory, Task, Bug, TestPlan, TestPlanRun, Request
Use: When you want any assignable type
```

### General (Base Type)
```
API: /api/v1/General
Description: Base type for all entities
Returns: All entities (assignables + containers + metadata)
Use: Rarely needed
```

## Query Examples

### Get all user stories
```bash
./tpcli list UserStories --take 100
```

### Get user stories from a feature
```bash
./tpcli list UserStories --where "Parent.Id eq 12345"
```

### Get all bugs in a project
```bash
./tpcli list Bugs --where "Project.Id eq 1000"
```

### Get all open items
```bash
./tpcli list Assignables --where "EntityState.Name eq 'Open'"
```

### Get tasks assigned to me
```bash
./tpcli list Tasks --where "AssignedUser.Id eq 999"
```

### Get entities in current iteration
```bash
./tpcli list Assignables --where "Iteration.IsCurrent eq 'true'"
```

## Common Queries by Role

### Project Manager
```bash
# Project overview
./tpcli get Projects {id}

# Release status
./tpcli list Assignables --where "Release.Id eq {id}"

# Team workload
./tpcli list Tasks --where "Team.Id eq {id}"

# Iteration progress
./tpcli list Assignables --where "Iteration.IsCurrent eq 'true'"
```

### Developer
```bash
# My tasks
./tpcli list Tasks --where "AssignedUser.Id eq {myid}"

# Feature details
./tpcli get Features {id}

# Related bugs
./tpcli list Bugs --where "Parent.Id eq {id}"
```

### QA/Tester
```bash
# Bugs to test
./tpcli list Bugs --where "EntityState.Name eq 'Testing'"

# Test coverage
./tpcli list TestCases --where "Feature.Id eq {id}"

# Test plan progress
./tpcli get TestPlans {id}
```

## Tips

1. **Use Assignables** for broad queries across work items
2. **Use specific types** (UserStory, Bug, Task) for filtered queries
3. **Parent field** shows parent item (Feature in UserStory, Epic in Feature)
4. **Children accessible** via `/api/v1/{Type}/{id}/{ChildType}`
5. **Custom fields** accessed via `CustomFields.FieldName`

## Related

- [API v1 Reference](api-v1-reference.md)
- [Query Syntax Reference](query-syntax.md)
- [How to Work with Nested Entities](../how-to/work-with-nested-entities.md)
