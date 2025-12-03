# PI Planning Sync API Documentation

## TPAPIClient

The `TPAPIClient` class provides a Python interface to TargetProcess for PI planning operations.

### Initialization

```python
from tpcli_pi.core.api_client import TPAPIClient

# Default: 1 hour cache TTL
client = TPAPIClient(verbose=False)

# Custom cache TTL (30 minutes)
client = TPAPIClient(verbose=True, cache_ttl=1800)
```

### Parameters

- `verbose` (bool): Enable verbose logging (default: False)
- `cache_ttl` (int): Cache time-to-live in seconds (default: 3600)

### Query Methods

#### get_arts()

Get all Agile Release Trains.

```python
arts = client.get_arts()
for art in arts:
    print(f"{art.name}: {art.id}")
```

Returns: `list[AgileReleaseTrain]`

#### get_art_by_name(name: str)

Get ART by name.

```python
art = client.get_art_by_name("Data, Analytics and Digital")
if art:
    print(f"ART ID: {art.id}")
```

Returns: `AgileReleaseTrain | None`

#### get_teams(art_id: int | None = None)

Get all teams, optionally filtered by ART.

```python
# Get all teams
all_teams = client.get_teams()

# Get teams in specific ART
art = client.get_art_by_name("Data, Analytics and Digital")
teams = client.get_teams(art_id=art.id)
```

Returns: `list[Team]`

#### get_team_by_name(name: str, art_id: int | None = None)

Get team by name, optionally within specific ART.

```python
team = client.get_team_by_name("Platform Eco", art_id=1234567)
if team:
    print(f"Team ID: {team.id}")
```

Returns: `Team | None`

#### get_releases(art_id: int | None = None)

Get all releases, optionally filtered by ART.

```python
# Get all releases
all_releases = client.get_releases()

# Get releases for specific ART
releases = client.get_releases(art_id=art.id)
```

Returns: `list[Release]`

#### get_release_by_name(name: str, art_id: int | None = None)

Get release by name.

```python
release = client.get_release_by_name("PI-4/25")
if release:
    print(f"Release ID: {release.id}")
```

Returns: `Release | None`

#### get_program_pi_objectives(art_id: int | None = None, release_id: int | None = None)

Get program-level PI objectives.

```python
# Get all program objectives
prog_objs = client.get_program_pi_objectives()

# Get for specific release
objs = client.get_program_pi_objectives(
    release_id=1942235
)
```

Returns: `list[ProgramPIObjective]`

#### get_team_pi_objectives(team_id: int | None = None, art_id: int | None = None, release_id: int | None = None)

Get team-level PI objectives with optional filtering.

```python
# Get all team objectives
all_objs = client.get_team_pi_objectives()

# Get for specific team and release
objs = client.get_team_pi_objectives(
    team_id=1935991,
    release_id=1942235
)
```

Returns: `list[TeamPIObjective]`

#### get_features(team_id: int | None = None, release_id: int | None = None, parent_epic_id: int | None = None)

Get features with optional filtering.

```python
# Get all features
all_features = client.get_features()

# Get features for team and release
features = client.get_features(
    team_id=1935991,
    release_id=1942235
)

# Get child features of epic
children = client.get_features(parent_epic_id=2018883)
```

Returns: `list[Feature]`

### Create Methods

#### create_team_objective(name, team_id, release_id, **kwargs)

Create a new Team PI Objective.

```python
objective = client.create_team_objective(
    name="Platform Governance",
    team_id=1935991,
    release_id=1942235,
    effort=21,
    status="Pending",
    description="Establish governance framework"
)

print(f"Created objective {objective.id}")
```

Parameters:
- `name` (str): Objective name (required)
- `team_id` (int): Team ID (required)
- `release_id` (int): Release ID (required)
- `effort` (int): Effort estimate
- `status` (str): Objective status
- `description` (str): Description
- `owner_id` (int): Owner user ID

Returns: `TeamPIObjective`

Raises: `TPAPIError` on failure

#### create_feature(name, parent_epic_id, **kwargs)

Create a new Feature (epic).

```python
feature = client.create_feature(
    name="Security Framework",
    parent_epic_id=2019099,
    effort=8,
    owner_id=123456
)

print(f"Created feature {feature.id}")
```

Parameters:
- `name` (str): Feature name (required)
- `parent_epic_id` (int): Parent epic/objective ID (required)
- `effort` (int): Effort estimate
- `status` (str): Feature status
- `owner_id` (int): Owner user ID

Returns: `Feature`

Raises: `TPAPIError` on failure

### Update Methods

#### update_team_objective(objective_id, **kwargs)

Update an existing Team PI Objective.

```python
objective = client.update_team_objective(
    objective_id=2019099,
    effort=34,
    status="In Progress"
)

print(f"Updated objective {objective.id}")
```

Parameters:
- `objective_id` (int): Objective ID to update (required)
- `name` (str): New name
- `effort` (int): New effort
- `status` (str): New status
- `description` (str): New description
- `owner_id` (int): New owner

Returns: `TeamPIObjective`

Raises: `TPAPIError` on failure

#### update_feature(feature_id, **kwargs)

Update an existing Feature.

```python
feature = client.update_feature(
    feature_id=2018883,
    effort=13,
    status="In Progress"
)

print(f"Updated feature {feature.id}")
```

Parameters:
- `feature_id` (int): Feature ID to update (required)
- `name` (str): New name
- `effort` (int): New effort
- `status` (str): New status
- `owner_id` (int): New owner

Returns: `Feature`

Raises: `TPAPIError` on failure

### Bulk Operations

#### bulk_create_team_objectives(objectives)

Create multiple Team PI Objectives in a single batch operation.

```python
objectives = [
    {
        "name": "Objective 1",
        "team_id": 1935991,
        "release_id": 1942235,
        "effort": 21
    },
    {
        "name": "Objective 2",
        "team_id": 1935991,
        "release_id": 1942235,
        "effort": 34
    }
]

results = client.bulk_create_team_objectives(objectives)

print(f"Created {len(results)} objectives")
for obj in results:
    print(f"  - {obj.name}: {obj.id}")
```

Parameters:
- `objectives` (list[dict]): List of objective specifications
  - Each dict has: name, team_id, release_id, (optional) effort, status, description, owner_id

Returns: `list[TeamPIObjective]`

Raises: `TPAPIError` if any creation fails (atomic - none created)

#### bulk_update_team_objectives(updates)

Update multiple Team PI Objectives in a single batch operation.

```python
updates = [
    {"id": 2019099, "effort": 40},
    {"id": 2027963, "effort": 50},
    {"id": 2030000, "status": "In Progress"}
]

results = client.bulk_update_team_objectives(updates)

print(f"Updated {len(results)} objectives")
```

Parameters:
- `updates` (list[dict]): List of update specifications
  - Each dict has: id (required), plus any fields to update

Returns: `list[TeamPIObjective]`

Raises: `TPAPIError` if any update fails (atomic - none updated)

### Cache Management

#### get_cache_stats()

Get cache performance statistics.

```python
stats = client.get_cache_stats()

print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Cache evictions: {stats['evictions']}")
print(f"Cached entries: {stats['size']}")
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

Returns: `dict[str, Any]` with keys:
- `hits`: Number of cache hits
- `misses`: Number of cache misses
- `evictions`: Number of expired entries evicted
- `size`: Current number of cached entries
- `hit_rate`: Cache hit rate as percentage (0-100)

#### clear_cache()

Clear all cached results and reset statistics.

```python
client.clear_cache()

# Cache is now empty
stats = client.get_cache_stats()
assert stats['size'] == 0
```

## Data Models

### AgileReleaseTrain

```python
@dataclass
class AgileReleaseTrain:
    id: int
    name: str
```

### Team

```python
@dataclass
class Team:
    id: int
    name: str
    art_id: int
    owner: User | None = None
```

### Release

```python
@dataclass
class Release:
    id: int
    name: str
    art_id: int
    start_date: datetime | None = None
    end_date: datetime | None = None
```

### ProgramPIObjective

```python
@dataclass
class ProgramPIObjective:
    id: int
    name: str
    effort: int | None = None
    status: str | None = None
    description: str | None = None
    owner: User | None = None
```

### TeamPIObjective

```python
@dataclass
class TeamPIObjective:
    id: int
    name: str
    team_id: int
    release_id: int
    effort: int | None = None
    status: str | None = None
    description: str | None = None
    owner: User | None = None
```

### Feature

```python
@dataclass
class Feature:
    id: int
    name: str
    parent_id: int
    effort: int | None = None
    status: str | None = None
    owner: User | None = None
```

### User

```python
@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    email: str
```

## Error Handling

### TPAPIError

Raised when API calls fail.

```python
from tpcli_pi.core.api_client import TPAPIError

try:
    objective = client.create_team_objective(
        name="Test",
        team_id=invalid_id,
        release_id=invalid_id
    )
except TPAPIError as e:
    print(f"API error: {e}")
    # Handle error appropriately
```

## Examples

### Complete PI Planning Workflow

```python
from tpcli_pi.core.api_client import TPAPIClient

client = TPAPIClient(verbose=True)

# Get ART
art = client.get_art_by_name("Data, Analytics and Digital")
if not art:
    print("ART not found")
    exit(1)

# Get team
team = client.get_team_by_name("Platform Eco", art_id=art.id)
if not team:
    print("Team not found")
    exit(1)

# Get release
release = client.get_release_by_name("PI-4/25", art_id=art.id)
if not release:
    print("Release not found")
    exit(1)

# Get existing objectives
objectives = client.get_team_pi_objectives(
    team_id=team.id,
    release_id=release.id
)

print(f"Found {len(objectives)} objectives")

# Update first objective
if objectives:
    updated = client.update_team_objective(
        objectives[0].id,
        effort=objectives[0].effort + 5
    )
    print(f"Updated {updated.name}: effort now {updated.effort}")

# Check cache performance
stats = client.get_cache_stats()
print(f"Cache efficiency: {stats['hit_rate']:.1f}% hit rate")
```

### Bulk Operations Example

```python
# Create multiple objectives
new_objectives = [
    {
        "name": f"Objective {i}",
        "team_id": team.id,
        "release_id": release.id,
        "effort": 20 + i * 5
    }
    for i in range(5)
]

created = client.bulk_create_team_objectives(new_objectives)
print(f"Created {len(created)} objectives")

# Update multiple objectives
updates = [
    {"id": obj.id, "effort": obj.effort + 10}
    for obj in created
]

updated = client.bulk_update_team_objectives(updates)
print(f"Updated {len(updated)} objectives with increased effort")
```

---

## Version History

- **v1.0.0** (2025-11-30)
  - Initial API release
  - Full query and create/update methods
  - Bulk operations
  - TTL-based caching
  - Cache statistics
