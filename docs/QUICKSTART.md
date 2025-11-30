# tpcli - TargetProcess CLI

A command-line interface for interacting with the TargetProcess (Apptio) REST API.

## Features

- Query user stories, bugs, tasks, features, and other entities
- Filter and search using TargetProcess query syntax
- Support for both API v1 and v2
- Token-based authentication
- Flexible configuration via CLI flags, environment variables, or config file

## Installation

```bash
cd ~/shalomb/tpcli
go build -o tpcli
```

## Configuration

You can configure `tpcli` in three ways (in order of precedence):

### 1. Command-line flags

```bash
tpcli list UserStories --url https://example.tpondemand.com --token YOUR_TOKEN
```

### 2. Environment variables

```bash
export TP_URL=https://example.tpondemand.com
export TP_TOKEN=YOUR_TOKEN
tpcli list UserStories
```

### 3. Configuration file

Create `~/.tpcli.yaml`:

```yaml
url: https://example.tpondemand.com
token: YOUR_TOKEN_HERE
verbose: false
```

## Usage

### List entities

```bash
# List all user stories (default: 25 items)
tpcli list UserStories

# List with filtering
tpcli list UserStories --where "EntityState.Name eq 'Open'"

# List specific fields
tpcli list Bugs --fields Id,Name,EntityState,Priority --take 10

# List with pagination
tpcli list Tasks --where "Project.Id eq 1234" --take 20 --skip 40
```

### Get a specific entity

```bash
# Get a user story by ID
tpcli get UserStory 12345

# Get specific fields only
tpcli get Bug 67890 --fields Id,Name,Description,EntityState,AssignedUser
```

### Common entity types

- `UserStories` - User stories
- `Bugs` - Bugs
- `Tasks` - Tasks
- `Features` - Features
- `Epics` - Epics
- `Releases` - Releases
- `Iterations` - Iterations/Sprints
- `Projects` - Projects
- `Users` - Users
- `Teams` - Teams

### Filtering examples

```bash
# Open user stories
tpcli list UserStories --where "EntityState.Name eq 'Open'"

# Bugs in a specific project
tpcli list Bugs --where "Project.Id eq 1234"

# Tasks assigned to a user
tpcli list Tasks --where "AssignedUser.Id eq 5678"

# User stories in current sprint
tpcli list UserStories --where "Iteration.IsCurrent eq 'true'"

# High priority bugs
tpcli list Bugs --where "Priority.Name eq 'High'"
```

## Verbose mode

Use `-v` or `--verbose` to see request/response details:

```bash
tpcli list UserStories -v
```

## API Token

Your API token should be base64-encoded. You can get it from:
1. TargetProcess UI: Settings > Access Tokens
2. Or use Basic Auth format: `base64(username:password)`

Current token from environment:
```bash
echo $API_TOKEN
```

## Examples

```bash
# Get all open bugs in project 1234
tpcli list Bugs \
  --where "Project.Id eq 1234 and EntityState.Name eq 'Open'" \
  --fields Id,Name,Priority,AssignedUser \
  --take 50

# Get details of a specific user story
tpcli get UserStory 98765 \
  --fields Id,Name,Description,EntityState,Owner,Tags

# List current iteration tasks
tpcli list Tasks \
  --where "Iteration.IsCurrent eq 'true'" \
  --fields Id,Name,EntityState,AssignedUser,TimeRemaining
```

## Development

```bash
# Run without building
go run main.go list UserStories

# Build
go build -o tpcli

# Install to $GOPATH/bin
go install
```

## Resources

- [TargetProcess API Documentation](https://dev.targetprocess.com/docs)
- [REST API v1 Guide](https://dev.targetprocess.com/docs/rest-getting-started)
- [Authentication](https://dev.targetprocess.com/docs/authentication)
