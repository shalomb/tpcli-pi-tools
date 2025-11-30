# Idea: Entity Discovery and Instance-Agnostic Query Helpers

**Status:** Proposed
**Date Created:** 2025-11-30
**Relates to:** PI Planning, PI Objectives, Team Analysis

## Problem Statement

Many TargetProcess queries require instance-specific IDs:
- Team IDs (e.g., 1001 for "Example Team")
- Agile Release Train (ART) IDs (e.g., 1936122 for "Data, Analytics and Digital")
- Project IDs (e.g., 223264 for "GMSGQ")
- Release IDs (e.g., 1942235 for "PI-4/25")
- Custom Field definitions

**Current approach:** Hardcoded IDs in scripts
```bash
./tpcli list TeamPIObjectives --where "Team.Id eq 1001" --take 100
./tpcli list ProgramPIObjectives --where "AgileReleaseTrain.Id eq 1936122" --take 100
```

These queries are **not portable across instances** or even within the same instance after data migrations.

## Proposed Solution

Create discovery/lookup helpers that work with **names instead of IDs**:

### Option 1: Enhanced CLI Subcommands
```bash
# Discover available ARTs and return their IDs
./tpcli discover artsbyname --name "Data, Analytics and Digital"

# List teams in an ART by name
./tpcli discover teamsinart --artname "Data, Analytics and Digital"

# Find a team by name and list its PI Objectives
./tpcli discover teampi --teamname "Example Team" --release "PI-4/25"
```

### Option 2: Lookup/Helper Functions in Scripts
```bash
# Utility functions for shell scripts
source tpcli-helpers.sh

team_id_by_name "Example Team"
art_id_by_name "Data, Analytics and Digital"
release_id_by_name "PI-4/25"

# Then use normally
./tpcli list TeamPIObjectives --where "Team.Id eq $(team_id_by_name 'Example Team')" --take 100
```

### Option 3: Configuration-Based Aliases
```yaml
# ~/.config/tpcli/entities.yaml
aliases:
  artsbyname:
    - name: "Data, Analytics and Digital"
      id: 1936122
    - name: "Developer Experience Platform"
      id: 891544
  teamsbyname:
    - name: "Example Team"
      id: 1001
  releasesbyname:
    - name: "PI-4/25"
      id: 1942235
```

## Use Cases

### 1. **PI Planning Dashboard**
Show all PI Objectives for an ART (by name):
```bash
./tpcli pi-dashboard --art "Data, Analytics and Digital" --pi "PI-4/25"
```

### 2. **Team Workload Analysis**
Get team PI objectives without knowing the team ID:
```bash
./tpcli describe-team --teamname "Example Team" --pi "PI-4/25"
```

### 3. **Cross-Instance Portability**
Same scripts work on dev, test, and production instances without modification.

### 4. **Automation & CI/CD**
Fill in epics from Jira based on named PI Objectives:
```bash
# Find all Program PI Objectives for an ART
pi_objectives=$(./tpcli list-pi-objectives --art "Data, Analytics and Digital")

# For each objective, check Jira for linked issues
for obj in $pi_objectives; do
  jira issue list --jql "text ~ '${obj}'"
done
```

## Technical Considerations

### Challenges
- **Duplicate names:** What if two teams have the same name?
- **Name changes:** When an ART/team name changes, scripts break
- **Performance:** Lookup requires list → search → extract ID (extra API calls)
- **Caching:** Should we cache the name→ID mappings?

### Possible Approaches

**A. Simple lookup (stateless)**
```go
// For each query, fetch entities and search by name
team := findTeamByName(name)
// Then: ./tpcli list ... --where "Team.Id eq " + team.ID
```
- Pros: Always up-to-date, no cache invalidation
- Cons: More API calls per query

**B. Cached lookup (with TTL)**
- Cache name→ID mappings with 1-hour TTL
- Invalidate on-demand with `--refresh-cache` flag
- Trade-off: Performance vs. freshness

**C. Configuration file (manual sync)**
- User maintains `~/.config/tpcli/entities.yaml`
- Simple, no extra API calls, but requires manual updates

## Implementation Priority

1. **Phase 1 (High Value):** `discover` subcommands (Option 1)
   - `tpcli discover artsbyname`
   - `tpcli discover teamsbyname`
   - `tpcli discover releasebyname`
   - Document in how-to guides

2. **Phase 2 (Medium Value):** Helper scripts (Option 2)
   - `scripts/tpcli-helpers.sh` with utility functions
   - Update existing team analysis script to use helpers

3. **Phase 3 (Nice to Have):** Configuration aliasing (Option 3)
   - User-maintained entity alias file
   - Requires more sophisticated config parsing

## Related Ideas

- [Unification of TargetProcess and Jira PI Planning](./jira-targetprocess-pi-sync.md) (future)
- Better error messages when IDs don't exist
- Batch operation support (query multiple teams at once)

## Open Questions

1. Should name lookups be case-insensitive?
2. Should we require unique names or handle duplicates gracefully?
3. What's the acceptable latency for discover operations?
4. Should we support fuzzy matching for typos?

## Next Steps

- [ ] Gather feedback on preferred approach (Option 1, 2, or 3)
- [ ] Prototype Phase 1 (discover subcommands)
- [ ] Test against real TargetProcess instance
- [ ] Update documentation with examples
