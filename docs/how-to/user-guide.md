# PI Planning Sync User Guide

## Overview

The PI Planning Sync tool enables seamless bidirectional synchronization of PI (Planning Interval) planning data between TargetProcess and git. This guide covers how to use the tool for collaborative PI planning with version control.

## Features

- **Git-Based Workflow**: Use familiar git operations for planning
- **Bidirectional Sync**: Pull latest from TargetProcess, push changes back
- **Markdown Export**: Plan in editable markdown files with YAML metadata
- **Conflict Resolution**: Git's 3-way merge handles conflicts automatically
- **Multiple Releases**: Manage PI-4, PI-5, etc. independently
- **Team Collaboration**: Multiple teams can work on same PI without conflicts
- **Performance Optimized**: Bulk operations, caching, and efficient syncing

## Installation

### Prerequisites

- Python 3.11+
- Go 1.21+
- git
- TargetProcess account with API access

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tpcli.git
cd tpcli
```

2. Install dependencies:
```bash
make install-dev
```

3. Configure API access:
```bash
# Set environment variables
export TP_URL="https://company.tpondemand.com"
export TP_TOKEN="your-api-token"

# Or create .tpcli.yaml config file
cat > ~/.tpcli.yaml <<EOF
url: https://company.tpondemand.com
token: your-api-token
EOF
```

4. Build the tool:
```bash
make build
```

## Quick Start

### Initialize Plan Tracking

```bash
# Initialize tracking for a team and release
tpcli plan init --release PI-4/25 --team "Platform Eco"
```

This creates:
- Tracking branch: `TP-PI-4-25-platform-eco`
- Feature branch: `feature/plan-pi-4-25`
- Markdown file: `pi-4-25-platform-eco.md`

### Edit Your Plan

```bash
# Edit objectives in the markdown file
vim pi-4-25-platform-eco.md

# Commit your changes
git add pi-4-25-platform-eco.md
git commit -m "Update Platform Governance objective effort"
```

### Pull Latest from TargetProcess

```bash
# Fetch latest changes and rebase your work
tpcli plan pull

# If conflicts occur, resolve them:
# 1. Edit file to resolve conflict markers
# 2. Stage the resolved file
git add pi-4-25-platform-eco.md
git rebase --continue
```

### Push Changes to TargetProcess

```bash
# Submit your changes to TargetProcess
tpcli plan push
```

## Markdown File Format

The markdown file has a YAML frontmatter section and objective details:

```yaml
---
release: "PI-4/25"
team: "Platform Eco"
art: "Data, Analytics and Digital"
exported_at: "2025-11-30T20:01:13.150553+00:00"
objectives:
  - {id: 2019099, name: "Platform governance", synced_at: "2025-11-30T20:01:13.150553+00:00"}
---

# PI-PI-4/25 Plan - Platform Eco

## Team Objective: Platform governance

**TP ID**: 2019099
**Status**: Pending
**Effort**: 21 points
**Owner**: Unassigned

### Description

Description of the objective goes here.
```

### Editing Objectives

To update an objective:

```markdown
**Status**: In Progress
**Effort**: 34 points
```

### Adding Epics

Epics are child features of objectives:

```markdown
### Epic: Security Framework

**Owner**: John Smith
**Status**: Not Started
**Effort**: 8 points
```

## Workflow Examples

### Example 1: Update Objective Effort

```bash
# Initialize planning
tpcli plan init --release PI-4/25 --team "Platform Eco"

# Edit the markdown file
vim pi-4-25-platform-eco.md
# Change "Effort": 21 → 34

# Commit and push
git add pi-4-25-platform-eco.md
git commit -m "Increase Platform Governance effort to 34"
tpcli plan push
```

### Example 2: Multi-Team Collaboration

```bash
# Team 1 works on Platform Eco
tpcli plan init --release PI-4/25 --team "Platform Eco"
# ... make changes ...
tpcli plan push

# Team 2 works on Cloud Enablement (independently)
tpcli plan init --release PI-4/25 --team "Cloud Enablement"
# ... make changes ...
tpcli plan push

# Both changes go to TargetProcess without conflicts
```

### Example 3: Handling Conflicts

```bash
# Pull when another team made changes
tpcli plan pull

# If there's a conflict:
# 1. Fix the conflict markers in the markdown
# 2. Complete the rebase
git add pi-4-25-platform-eco.md
git rebase --continue

# Push the resolved changes
tpcli plan push
```

## CLI Commands Reference

### tpcli plan init

Initialize plan tracking for a team and release.

```bash
Usage: tpcli plan init --release <release> --team <team>

Options:
  --release    Release name (e.g., PI-4/25) (required)
  --team       Team name (required)
  --url        TargetProcess base URL
  --token      API token for authentication

Example:
  tpcli plan init --release PI-4/25 --team "Platform Eco"
```

### tpcli plan pull

Pull latest changes from TargetProcess and rebase feature branch.

```bash
Usage: tpcli plan pull

Options:
  --url        TargetProcess base URL
  --token      API token for authentication

Example:
  tpcli plan pull
```

### tpcli plan push

Push changes to TargetProcess.

```bash
Usage: tpcli plan push

Options:
  --url        TargetProcess base URL
  --token      API token for authentication

Example:
  tpcli plan push
```

## Best Practices

### Commit Frequency

- Commit after each logical change (e.g., updating one objective)
- Use clear, descriptive commit messages
- Include the objective ID in commit messages when relevant

```bash
git commit -m "Update Platform Governance objective effort to 34 (TP-2019099)"
```

### Pull Before Push

Always pull latest changes before pushing to avoid conflicts:

```bash
tpcli plan pull
tpcli plan push
```

### Review Changes

Before pushing, review what you changed:

```bash
git log origin/TP-PI-4-25-platform-eco..HEAD
git diff origin/TP-PI-4-25-platform-eco HEAD
```

### Communicate Changes

- Use clear, detailed commit messages
- Reference TP objectives/epics in commits
- Document reasoning for changes

### Regular Syncs

For long-lived plans, pull frequently to stay in sync:

```bash
# Daily during PI planning
tpcli plan pull
```

## Troubleshooting

### Authentication Errors

**Error**: "API token is required"

**Solution**: Set `TP_TOKEN` environment variable or configure `~/.tpcli.yaml`

```bash
export TP_TOKEN="your-token"
tpcli plan init --release PI-4/25 --team "Platform Eco"
```

### Rebase Conflicts

**Error**: "Rebase conflict detected"

**Solution**:
1. Edit file to resolve conflict markers (<<<<<<, ======, >>>>>>>)
2. Stage resolved file: `git add <file>`
3. Continue rebase: `git rebase --continue`

### Network Errors

**Error**: "git sync operation failed"

**Solution**: Check network connection and TP API availability, then retry:

```bash
tpcli plan pull  # Retry pull
tpcli plan push  # Retry push
```

### Cache Issues

If data seems stale, clear the cache:

```bash
# The tool automatically manages cache with TTL
# Cache expires after 1 hour by default
# Force refresh by reinitializing the client
```

## Performance Tips

### Bulk Operations

When updating multiple objectives:

```bash
# Edit multiple objectives in one session
vim pi-4-25-platform-eco.md

# Commit all changes together
git add pi-4-25-platform-eco.md
git commit -m "Update multiple objectives for refined estimates"

# Single push operation handles all changes
tpcli plan push
```

### Efficient Syncing

- Use pull before push to minimize conflicts
- Commit frequently for better history
- Review changes before pushing

## Getting Help

### Common Questions

**Q: Can I work offline?**
A: Yes! Make changes locally, then `tpcli plan pull` and `tpcli plan push` when online.

**Q: What if two teams edit the same objective?**
A: Git's 3-way merge handles non-overlapping changes automatically. For overlapping changes, resolve conflicts manually.

**Q: How do I undo changes?**
A: Use git revert to create a reverting commit:
```bash
git revert <commit-hash>
tpcli plan push
```

### Reporting Issues

Found a bug? Report it with:
- Steps to reproduce
- Expected vs actual behavior
- Environment info (Python version, OS, etc.)

## Advanced Usage

### Git History

View planning history across your team:

```bash
# See all commits on tracking branch
git log origin/TP-PI-4-25-platform-eco

# See only your team's changes
git log origin/TP-PI-4-25-platform-eco -- pi-4-25-platform-eco.md

# View changes between syncs
git diff origin/TP-PI-4-25-platform-eco HEAD
```

### Branch Management

Switch between releases:

```bash
# Work on PI-4/25
git checkout feature/plan-pi-4-25

# Switch to PI-5/25
git checkout feature/plan-pi-5-25

# Both can be worked on independently
```

### Cache Monitoring

Check cache performance:

```python
from tpcli_pi.core.api_client import TPAPIClient

client = TPAPIClient()
stats = client.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1f}%")
print(f"Cached entries: {stats['size']}")
```

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the code documentation
3. Check git log for similar changes
4. Contact the development team

---

## Version History

- **v1.0.0** (2025-11-30): Initial release
  - Git-native plan sync
  - Markdown export/import
  - Bulk operations
  - TTL-based caching
  - Comprehensive CLI
