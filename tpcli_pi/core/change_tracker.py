"""
Change tracking and source detection for PI planning git-native workflows.

Detects:
- User edits: field changed, sync timestamp unchanged
- Jira updates: field changed, sync timestamp changed
- Conflicts: both user and Jira changed same field
- Audit trail: all sync operations (pull, push, user edits, conflicts)
"""

import re
from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from datetime import datetime


@dataclass
class FieldChange:
    """Represents a single field change in a diff."""
    field_name: str
    old_value: str
    new_value: str
    line_number: int


@dataclass
class ChangeSource:
    """Identifies source and nature of a change."""
    # Source of change: "user_edit" or "jira_update"
    source: str
    # Name of changed field (e.g., "Effort", "Status")
    field_name: str
    # Old and new values
    old_value: str
    new_value: str
    # Timestamp metadata (for detecting Jira updates)
    old_timestamp: Optional[str] = None
    new_timestamp: Optional[str] = None


@dataclass
class AuditLogEntry:
    """Single entry in an operation audit log."""
    timestamp: str
    operation: str  # "pull", "push", "user_edit", "conflict_detected"
    direction: Optional[str] = None  # "tp_to_git" or "git_to_tp"
    objectives_synced: int = 0
    epics_synced: int = 0
    stories_synced: int = 0
    objectives_updated: int = 0
    epics_updated: int = 0
    conflicts: int = 0
    status: str = "success"  # or "conflict_detected", "error"


class AuditLog:
    """
    Maintains audit trail of all sync operations.

    Tracks:
    - Pull operations (TP to Git sync)
    - Push operations (Git to TP sync)
    - User edits
    - Conflict detections
    """

    def __init__(self):
        """Initialize audit log."""
        self.entries: List[AuditLogEntry] = []

    def log_pull(self, timestamp: str, objectives: int, epics: int, stories: int,
                 conflicts: int = 0, status: str = "success") -> None:
        """Log a pull operation (TP → Git)."""
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation="pull",
            direction="tp_to_git",
            objectives_synced=objectives,
            epics_synced=epics,
            stories_synced=stories,
            conflicts=conflicts,
            status=status,
        )
        self.entries.append(entry)

    def log_push(self, timestamp: str, objectives: int, epics: int = 0,
                 status: str = "success") -> None:
        """Log a push operation (Git → TP)."""
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation="push",
            direction="git_to_tp",
            objectives_updated=objectives,
            epics_updated=epics,
            status=status,
        )
        self.entries.append(entry)

    def log_conflict(self, timestamp: str, num_conflicts: int) -> None:
        """Log conflict detection."""
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation="conflict_detected",
            conflicts=num_conflicts,
            status="conflict_detected",
        )
        self.entries.append(entry)

    def get_entries(self) -> List[AuditLogEntry]:
        """Get all audit log entries."""
        return self.entries

    def get_last_pull(self) -> Optional[AuditLogEntry]:
        """Get the most recent pull operation."""
        for entry in reversed(self.entries):
            if entry.operation == "pull":
                return entry
        return None

    def get_conflicts_count(self) -> int:
        """Get total number of conflicts detected."""
        return sum(entry.conflicts for entry in self.entries)

    def export_to_dict(self) -> List[Dict[str, Any]]:
        """Export audit log as list of dicts (for JSON serialization)."""
        result = []
        for entry in self.entries:
            entry_dict = {
                "timestamp": entry.timestamp,
                "operation": entry.operation,
                "status": entry.status,
            }
            if entry.direction:
                entry_dict["direction"] = entry.direction
            if entry.objectives_synced > 0:
                entry_dict["objectives_synced"] = entry.objectives_synced
            if entry.epics_synced > 0:
                entry_dict["epics_synced"] = entry.epics_synced
            if entry.stories_synced > 0:
                entry_dict["stories_synced"] = entry.stories_synced
            if entry.objectives_updated > 0:
                entry_dict["objectives_updated"] = entry.objectives_updated
            if entry.epics_updated > 0:
                entry_dict["epics_updated"] = entry.epics_updated
            if entry.conflicts > 0:
                entry_dict["conflicts"] = entry.conflicts
            result.append(entry_dict)
        return result


class ChangeTracker:
    """
    Detect change sources from git diffs and markdown files.

    Uses strategy:
    - If Last Synced timestamp changed → Jira update (automatic from sync process)
    - If Last Synced timestamp unchanged → User edit (manual)
    - If new sections added and timestamps updated → Jira sync (e.g., new stories)
    """

    # Pattern to match Last Synced metadata lines
    LAST_SYNCED_PATTERN = re.compile(
        r"\*\*Last Synced\*\*:\s*([^\s]+.*?)(?:\s*$|$)"
    )

    # Pattern to match field changes in diff
    FIELD_CHANGE_PATTERN = re.compile(
        r"^\+?\*\*([^*]+)\*\*:\s*(.+)$",
        re.MULTILINE
    )

    def __init__(self):
        """Initialize change tracker."""
        pass

    def detect_changes_in_diff(self, git_diff: str) -> List[ChangeSource]:
        """
        Detect change sources from a git diff.

        Strategy:
        1. Parse all field changes (lines starting with + or -)
        2. For each changed field, check if Last Synced timestamp also changed in SAME section
        3. If timestamp unchanged → user_edit
        4. If timestamp changed → jira_update

        Args:
            git_diff: Git diff output (unified format)

        Returns:
            List of ChangeSource objects identifying each change
        """
        changes = []

        lines = git_diff.split('\n')
        sections = self._split_diff_sections(lines)

        for section in sections:
            section_changes = self._analyze_section_v2(section)
            changes.extend(section_changes)

        return changes

    def _split_diff_sections(self, lines: List[str]) -> List[List[str]]:
        """Split diff into sections marked by @@ lines."""
        sections = []
        current_section = []

        for line in lines:
            if line.startswith('@@'):
                if current_section:
                    sections.append(current_section)
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append(current_section)

        return sections

    def _analyze_section_v2(self, section: List[str]) -> List[ChangeSource]:
        """
        Analyze a diff section returning changes with per-hierarchical-level timestamp context.

        Strategy: Track Last Synced timestamps at each hierarchical level (H2/H3/H4).
        When we encounter a field change, use the MOST RECENT Last Synced timestamp
        at that level (closest preceding Last Synced line).

        Returns:
            List of ChangeSource objects with timestamps matched to their hierarchy
        """
        changes = []

        # Track changes and their line positions
        removed = {}  # {field_name: (value, line_index)}
        added = {}    # {field_name: (value, line_index)}
        removed_timestamps = {}  # {line_index: (timestamp, hierarchy_marker)}
        added_timestamps = {}  # {line_index: (timestamp, hierarchy_marker)}

        # Build maps of what changed at each line
        for i, line in enumerate(section):
            if line.startswith('-') and line.startswith('-**'):
                field_match = re.match(r'-\*\*([^*]+)\*\*:\s*(.+)$', line)
                if field_match:
                    field_name = field_match.group(1).strip()
                    value = field_match.group(2).strip()
                    removed[field_name] = (value, i)

                    if field_name == "Last Synced":
                        removed_timestamps[i] = value

            elif line.startswith('+') and line.startswith('+**'):
                field_match = re.match(r'\+\*\*([^*]+)\*\*:\s*(.+)$', line)
                if field_match:
                    field_name = field_match.group(1).strip()
                    value = field_match.group(2).strip()
                    added[field_name] = (value, i)

                    if field_name == "Last Synced":
                        added_timestamps[i] = value

        # Find field pairs and their associated timestamps
        for field_name in removed:
            if field_name in added and field_name != "Last Synced":
                old_value, old_idx = removed[field_name]
                new_value, new_idx = added[field_name]

                # Find the Last Synced values that apply to this field
                # Strategy: Find the closest Last Synced (either before or after the field)
                old_timestamp = None
                new_timestamp = None

                # For removed lines: find nearest Last Synced (could be before or after)
                if removed_timestamps:
                    closest_ts_idx = min(removed_timestamps.keys(),
                                        key=lambda x: abs(x - old_idx))
                    old_timestamp = removed_timestamps[closest_ts_idx]

                # For added lines: find nearest Last Synced (could be before or after)
                if added_timestamps:
                    closest_ts_idx = min(added_timestamps.keys(),
                                        key=lambda x: abs(x - new_idx))
                    new_timestamp = added_timestamps[closest_ts_idx]

                # Determine source based on timestamp change
                if old_timestamp == new_timestamp:
                    source = "user_edit"
                else:
                    source = "jira_update"

                change = ChangeSource(
                    source=source,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    old_timestamp=old_timestamp,
                    new_timestamp=new_timestamp,
                )
                changes.append(change)

        return changes

    def _analyze_section(self, section: List[str]) -> List[ChangeSource]:
        """
        Analyze a diff section to detect changes and their sources.

        A section contains:
        - @@ line (hunk header)
        - Unchanged lines (no prefix)
        - Removed lines (- prefix)
        - Added lines (+ prefix)

        Strategy:
        1. Find all removed lines with **Field**: value pattern
        2. Find corresponding added lines
        3. Check if Last Synced timestamp changed
        4. Determine source: user_edit (timestamp same) or jira_update (timestamp different)
        """
        changes = []

        # Extract removed and added lines
        removed = {}  # {field_name: (value, line_index)}
        added = {}    # {field_name: (value, line_index)}
        removed_timestamps = {}  # {line_index: timestamp}
        added_timestamps = {}    # {line_index: timestamp}

        for i, line in enumerate(section):
            if line.startswith('-') and line.startswith('-**'):
                # Removed field line
                field_match = re.match(r'-\*\*([^*]+)\*\*:\s*(.+)$', line)
                if field_match:
                    field_name = field_match.group(1).strip()
                    value = field_match.group(2).strip()
                    removed[field_name] = (value, i)

                    # Extract timestamp if this is Last Synced
                    if field_name == "Last Synced":
                        removed_timestamps[i] = value

            elif line.startswith('+') and line.startswith('+**'):
                # Added field line
                field_match = re.match(r'\+\*\*([^*]+)\*\*:\s*(.+)$', line)
                if field_match:
                    field_name = field_match.group(1).strip()
                    value = field_match.group(2).strip()
                    added[field_name] = (value, i)

                    # Extract timestamp if this is Last Synced
                    if field_name == "Last Synced":
                        added_timestamps[i] = value

        # Find field pairs (removed vs added with same name)
        for field_name in removed:
            if field_name in added:
                old_value, _ = removed[field_name]
                new_value, _ = added[field_name]

                # Get timestamps (check if we have them from this section)
                # Look for Last Synced in the same section
                old_timestamp = None
                new_timestamp = None

                for timestamp_val in removed_timestamps.values():
                    if timestamp_val:
                        old_timestamp = timestamp_val
                        break

                for timestamp_val in added_timestamps.values():
                    if timestamp_val:
                        new_timestamp = timestamp_val
                        break

                # Determine source based on timestamp change
                if field_name != "Last Synced":
                    # For non-timestamp fields, check if timestamp changed
                    if old_timestamp == new_timestamp:
                        # Timestamp unchanged → user edit
                        source = "user_edit"
                    else:
                        # Timestamp changed → Jira update
                        source = "jira_update"

                    change = ChangeSource(
                        source=source,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        old_timestamp=old_timestamp,
                        new_timestamp=new_timestamp,
                    )
                    changes.append(change)

        return changes

    def has_timestamp_changed(self, old_timestamp: str, new_timestamp: str) -> bool:
        """
        Check if sync timestamps are different.

        Args:
            old_timestamp: Old Last Synced value
            new_timestamp: New Last Synced value

        Returns:
            True if timestamps differ (Jira update), False if same (user edit)
        """
        return old_timestamp != new_timestamp

    def detect_jira_updates(self, changes: List[ChangeSource]) -> List[ChangeSource]:
        """Filter to only Jira updates."""
        return [c for c in changes if c.source == "jira_update"]

    def detect_user_edits(self, changes: List[ChangeSource]) -> List[ChangeSource]:
        """Filter to only user edits."""
        return [c for c in changes if c.source == "user_edit"]

    def has_conflict(self, changes: List[ChangeSource]) -> bool:
        """
        Check if there are conflicting changes in the diff.

        A conflict exists when BOTH user edits AND Jira updates are present,
        indicating that the user edited something locally while Jira also updated
        the same item (objective/epic/story), requiring manual merge resolution.

        Args:
            changes: List of detected changes

        Returns:
            True if both user_edit and jira_update exist in the same diff
        """
        user_edits = self.detect_user_edits(changes)
        jira_updates = self.detect_jira_updates(changes)

        # Conflict exists if BOTH user edits and Jira updates are present
        return bool(user_edits and jira_updates)

    def get_conflicting_fields(self, changes: List[ChangeSource]) -> List[str]:
        """
        Get list of fields that have conflicting changes or related to conflicts.

        When there's a mixed user/Jira change situation, return all changed fields
        to help user understand what needs resolution.

        Args:
            changes: List of detected changes

        Returns:
            List of field names involved in the conflict
        """
        user_edits = self.detect_user_edits(changes)
        jira_updates = self.detect_jira_updates(changes)

        if not (user_edits and jira_updates):
            return []

        # Return all fields that were changed (in either direction)
        all_changed_fields = {c.field_name for c in user_edits + jira_updates}
        return sorted(all_changed_fields)

    def generate_conflict_hints(self, changes: List[ChangeSource]) -> List[str]:
        """
        Generate smart hints for resolving conflicts.

        Strategy:
        - If user edited field X and Jira updated field Y in same section:
          Hint: "Keep user's X change, accept Jira's Y update"
        - If both edited same field in different ways (rare):
          Hint: "Manual resolution needed for X"
        - No conflicts: Empty list

        Args:
            changes: List of detected changes

        Returns:
            List of hint messages for user
        """
        hints = []

        user_edits = self.detect_user_edits(changes)
        jira_updates = self.detect_jira_updates(changes)

        if not (user_edits and jira_updates):
            return hints  # No conflict

        # Organize by field
        user_fields = {c.field_name for c in user_edits}
        jira_fields = {c.field_name for c in jira_updates}

        # Fields changed by both (same field edited locally and updated by Jira)
        same_field_conflicts = user_fields & jira_fields
        if same_field_conflicts:
            for field in sorted(same_field_conflicts):
                hints.append(f"⚠️  Both you and Jira edited '{field}' - manual resolution needed")

        # Fields changed by only one side (complementary changes)
        user_only = user_fields - jira_fields
        jira_only = jira_fields - user_fields

        if user_only and jira_only:
            user_str = ", ".join(sorted(user_only))
            jira_str = ", ".join(sorted(jira_only))
            hints.append(f"✓ You edited: {user_str}")
            hints.append(f"✓ Jira updated: {jira_str}")
            hints.append("These changes are compatible - both can be kept")

        return hints

    def get_change_summary(self, changes: List[ChangeSource]) -> Dict[str, Any]:
        """
        Generate summary of changes.

        Args:
            changes: List of detected changes

        Returns:
            Dict with summary counts and conflict info
        """
        user_edits = self.detect_user_edits(changes)
        jira_updates = self.detect_jira_updates(changes)
        conflicting = self.get_conflicting_fields(changes)

        return {
            "total_changes": len(changes),
            "user_edits": len(user_edits),
            "jira_updates": len(jira_updates),
            "conflicts": len(conflicting),
            "conflicting_fields": conflicting,
            "has_conflict": len(conflicting) > 0,
        }
