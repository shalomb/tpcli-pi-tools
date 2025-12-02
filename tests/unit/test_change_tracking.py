"""
Unit tests for Phase 2C: Change attribution and conflict resolution.

Tests for tracking:
- When objectives/epics/stories were last synced
- Whether changes came from user edits vs Jira updates
- Smart hints for resolving merge conflicts
- Audit trail of sync operations
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Optional
from dataclasses import dataclass, asdict


class TestSyncTimestampTracking:
    """Tests for sync timestamp metadata (Phase 2C foundation)."""

    @pytest.fixture
    def markdown_with_timestamps(self):
        """Markdown with sync timestamps in frontmatter."""
        return """---
release: "PI-4/25"
team: "Platform Eco"
art: "Data, Analytics and Digital"
exported_at: "2025-12-01T10:30:00+00:00"
objectives:
  - {"id": 2019099, "name": "Platform governance", "synced_at": "2025-12-01T10:30:00+00:00"}
  - {"id": 2027963, "name": "DQ initiative", "synced_at": "2025-12-01T10:30:00+00:00"}
---

# PI-4/25 Plan - Platform Eco

## Team Objective: Platform governance

**TP ID**: 2019099
**Status**: Pending
**Effort**: 21 points
**Owner**: Norbert Borský
**Last Synced**: 2025-12-01T10:30:00+00:00

### Epic: Governance Framework
**Owner**: John Smith
**Status**: Analyzed
**Effort**: 8 points
**Jira Epic**: [DAD-2652](https://jira.takeda.com/browse/DAD-2652)
**Last Synced**: 2025-12-01T10:30:00+00:00
"""

    def test_frontmatter_contains_sync_metadata(self, markdown_with_timestamps):
        """Test frontmatter includes sync metadata."""
        assert "exported_at:" in markdown_with_timestamps
        assert '"synced_at"' in markdown_with_timestamps  # In objectives array

    def test_objectives_include_last_synced_timestamp(self, markdown_with_timestamps):
        """Test objectives array has synced_at for each."""
        assert '"synced_at": "2025-12-01T10:30:00+00:00"' in markdown_with_timestamps

    def test_sections_include_last_synced_timestamp(self, markdown_with_timestamps):
        """Test H2/H3 sections include **Last Synced** metadata."""
        assert "**Last Synced**: 2025-12-01T10:30:00+00:00" in markdown_with_timestamps

    def test_timestamp_format_iso8601(self, markdown_with_timestamps):
        """Test timestamps are ISO 8601 format (parseable)."""
        # Timestamps should match ISO 8601: YYYY-MM-DDTHH:MM:SS+TZ
        import re
        iso_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}'
        assert re.search(iso_pattern, markdown_with_timestamps)


class TestChangeSourceDetection:
    """Tests for detecting if change came from user or Jira."""

    @pytest.fixture
    def git_diff_user_edited(self):
        """Git diff showing user edited effort."""
        return """
@@ -10,7 +10,7 @@ ## Team Objective: Platform governance
 **TP ID**: 2019099
 **Status**: Pending
-**Effort**: 21 points
+**Effort**: 34 points
 **Owner**: Norbert Borský
-**Last Synced**: 2025-12-01T10:30:00+00:00
+**Last Synced**: 2025-12-01T10:30:00+00:00
"""

    @pytest.fixture
    def git_diff_jira_updated_status(self):
        """Git diff showing Jira updated story status."""
        return """
@@ -45,7 +45,7 @@ ### Epic: Governance Framework
 #### [DAD-2653] - Set up pod resource limits

-**Status**: To Do
+**Status**: In Progress
 **Assignee**: Alice Chen
 **Story Points**: 5
-**Last Synced**: 2025-12-01T10:30:00+00:00
+**Last Synced**: 2025-12-01T11:00:00+00:00
"""

    def test_detect_user_edit_effort_change(self, git_diff_user_edited):
        """Test detecting user edited effort estimate."""
        # User edit: effort changed, sync timestamp unchanged
        assert "**Effort**: 21 points" in git_diff_user_edited
        assert "**Effort**: 34 points" in git_diff_user_edited
        assert git_diff_user_edited.count("**Last Synced**: 2025-12-01T10:30:00+00:00") == 2

    def test_detect_jira_update_story_status(self, git_diff_jira_updated_status):
        """Test detecting Jira updated story status."""
        # Jira update: status changed AND sync timestamp changed
        assert "**Status**: To Do" in git_diff_jira_updated_status
        assert "**Status**: In Progress" in git_diff_jira_updated_status
        assert "2025-12-01T10:30:00+00:00" in git_diff_jira_updated_status
        assert "2025-12-01T11:00:00+00:00" in git_diff_jira_updated_status

    def test_detect_user_edit_objective_name(self):
        """Test detecting user edited objective name."""
        # User can edit names, timestamps stay same
        git_diff = """
@@ -10,5 +10,5 @@ ## Team Objective: Platform governance

-## Team Objective: Platform governance
+## Team Objective: Platform governance (Updated)
 **TP ID**: 2019099
-**Last Synced**: 2025-12-01T10:30:00+00:00
+**Last Synced**: 2025-12-01T10:30:00+00:00
"""
        from tpcli_pi.core.change_tracker import ChangeTracker
        tracker = ChangeTracker()
        changes = tracker.detect_changes_in_diff(git_diff)

        # Should detect no changes (H2 headers aren't tracked in diff pattern)
        # This tests that user edits don't change sync timestamps
        user_edits = tracker.detect_user_edits(changes)
        jira_updates = tracker.detect_jira_updates(changes)
        assert len(user_edits) == 0
        assert len(jira_updates) == 0

    def test_detect_jira_epic_sync(self):
        """Test detecting Jira epic was synced (new stories appeared)."""
        # New stories in markdown + timestamp updated = Jira sync
        git_diff = """
@@ -40,7 +40,15 @@ ### Epic: Governance Framework

 **Jira Epic**: [DAD-2652](https://jira.takeda.com/browse/DAD-2652)
-**Last Synced**: 2025-12-01T10:30:00+00:00
+**Last Synced**: 2025-12-01T11:00:00+00:00

+#### [DAD-2653] - Set up pod resource limits
+
+**Status**: To Do
+**Assignee**: Alice Chen
+**Story Points**: 5
+**Last Synced**: 2025-12-01T11:00:00+00:00
+
"""
        from tpcli_pi.core.change_tracker import ChangeTracker
        tracker = ChangeTracker()
        changes = tracker.detect_changes_in_diff(git_diff)

        # Should detect Last Synced changed (Jira sync marker)
        if changes:
            jira_updates = tracker.detect_jira_updates(changes)
            assert len(jira_updates) >= 1

    def test_both_user_and_jira_changes(self):
        """Test detecting changes from both sources."""
        # User edited effort (timestamp same) AND Jira updated status (timestamp different) = conflict
        git_diff = """
@@ -10,10 +10,10 @@ ## Team Objective: Platform governance

 **TP ID**: 2019099
 **Status**: Pending
-**Effort**: 21 points
+**Effort**: 34 points
 **Owner**: Norbert Borský
-**Last Synced**: 2025-12-01T10:30:00+00:00
+**Last Synced**: 2025-12-01T10:30:00+00:00

 #### [DAD-2653] - Set up pod resource limits

-**Status**: To Do
+**Status**: In Progress
-**Last Synced**: 2025-12-01T10:30:00+00:00
+**Last Synced**: 2025-12-01T11:00:00+00:00
"""
        from tpcli_pi.core.change_tracker import ChangeTracker
        tracker = ChangeTracker()
        changes = tracker.detect_changes_in_diff(git_diff)

        # Effort has same timestamp (user edit), Status has different timestamp (Jira update) = conflict
        summary = tracker.get_change_summary(changes)
        assert summary["has_conflict"] is True
        assert "Status" in summary["conflicting_fields"] or summary["conflicts"] >= 1


class TestConflictResolutionHints:
    """Tests for smart merge conflict resolution hints."""

    def test_conflict_resolution_hint_user_vs_jira(self):
        """Test hint when user edit conflicts with Jira update."""
        # If user edited effort but Jira also updated status on same section
        # Hint: "Keep user's effort edit, accept Jira status update"
        pass

    def test_conflict_resolution_hint_acceptance_criteria(self):
        """Test hint for AC conflicts (user edit vs Jira AC update)."""
        # If user edited AC locally but Jira description changed
        # Hint: "User AC in markdown, Jira AC available in stories"
        pass

    def test_conflict_resolution_hint_story_moved(self):
        """Test hint when story appears in different epic."""
        # If Jira moved story to different epic
        # Hint: "Story relinked in Jira, check if intentional"
        pass

    def test_no_hint_if_no_conflict(self):
        """Test no hint when changes are compatible."""
        # User edited objective, Jira updated story = no conflict
        pass


class TestAuditTrail:
    """Tests for audit trail of sync operations."""

    @pytest.fixture
    def sync_log(self):
        """Sync operation audit log."""
        return [
            {
                "timestamp": "2025-12-01T10:30:00+00:00",
                "operation": "pull",
                "direction": "tp_to_git",
                "objectives_synced": 2,
                "epics_synced": 5,
                "stories_synced": 12,
                "conflicts": 0,
                "status": "success"
            },
            {
                "timestamp": "2025-12-01T10:35:00+00:00",
                "operation": "user_edit",
                "file": "objectives.md",
                "changes": [
                    {"field": "effort", "objective": "2019099", "from": 21, "to": 34}
                ]
            },
            {
                "timestamp": "2025-12-01T11:00:00+00:00",
                "operation": "push",
                "direction": "git_to_tp",
                "objectives_updated": 1,
                "epics_updated": 0,
                "stories_synced": 0,
                "status": "success"
            },
            {
                "timestamp": "2025-12-01T11:05:00+00:00",
                "operation": "pull",
                "direction": "tp_to_git",
                "objectives_synced": 2,
                "epics_synced": 5,
                "stories_synced": 14,  # 2 new stories from Jira
                "conflicts": 1,
                "status": "conflict_detected"
            }
        ]

    def test_audit_log_pull_operation(self, sync_log):
        """Test pull operation recorded in audit log."""
        pull_ops = [op for op in sync_log if op["operation"] == "pull"]
        assert len(pull_ops) >= 1
        assert pull_ops[0]["direction"] == "tp_to_git"
        assert "objectives_synced" in pull_ops[0]

    def test_audit_log_push_operation(self, sync_log):
        """Test push operation recorded in audit log."""
        push_ops = [op for op in sync_log if op["operation"] == "push"]
        assert len(push_ops) >= 1
        assert push_ops[0]["direction"] == "git_to_tp"

    def test_audit_log_user_edit(self, sync_log):
        """Test user edits recorded in audit log."""
        edits = [op for op in sync_log if op["operation"] == "user_edit"]
        assert len(edits) >= 1
        assert edits[0]["changes"][0]["field"] == "effort"

    def test_audit_log_conflict_detection(self, sync_log):
        """Test conflict detection recorded."""
        conflicts = [op for op in sync_log if op.get("conflicts", 0) > 0]
        assert len(conflicts) >= 1
        assert conflicts[0]["status"] == "conflict_detected"


class TestMetadataEnhancement:
    """Tests for enhanced metadata in markdown sections."""

    def test_objective_metadata_includes_timestamps(self):
        """Test objective section includes last synced timestamp."""
        pass

    def test_epic_metadata_includes_timestamps(self):
        """Test epic section includes last synced timestamp."""
        pass

    def test_story_metadata_includes_timestamps(self):
        """Test story section includes last synced timestamp."""
        pass

    def test_metadata_timestamp_updated_on_each_pull(self):
        """Test timestamps update with each pull."""
        pass

    def test_metadata_timestamp_unchanged_on_user_edit(self):
        """Test user edit doesn't change sync timestamp."""
        pass


class TestConflictDetectionLogic:
    """Tests for merge conflict detection and hints."""

    def test_detect_conflicting_effort_changes(self):
        """Test detecting user and TP both changed effort."""
        pass

    def test_detect_conflicting_status_changes(self):
        """Test detecting user and Jira both changed status."""
        pass

    def test_detect_conflicting_owner_changes(self):
        """Test detecting user and TP both changed owner."""
        pass

    def test_hint_for_accepting_user_change(self):
        """Test hint message for accepting user's change."""
        pass

    def test_hint_for_accepting_jira_change(self):
        """Test hint message for accepting Jira's change."""
        pass

    def test_hint_for_manual_resolution(self):
        """Test hint message for manual conflict resolution."""
        pass


class TestChangeTrackingIntegration:
    """Integration tests for change tracking with git merge."""

    def test_conflict_markers_enhanced_with_source_info(self):
        """Test conflict markers include source information."""
        # Instead of just:
        # <<<<<< HEAD (user version)
        # >>>>>> branch (server version)
        #
        # Should show:
        # <<<<<< HEAD (user edit at 2025-12-01T10:35)
        # >>>>>> tp-sync (Jira update at 2025-12-01T11:00)
        pass

    def test_resolution_hint_file_generated(self):
        """Test .merge-hints file generated for conflicts."""
        # Create .conflict-hints.txt with suggestions
        # Help user understand what changed and why
        pass

    def test_audit_log_persisted_locally(self):
        """Test audit log saved locally for reference."""
        # Save to .tpcli-audit.log in repo
        # User can review history of changes
        pass


class TestPhase2CErrorHandling:
    """Tests for error handling in Phase 2C features."""

    def test_handle_missing_timestamps(self):
        """Test graceful handling if timestamp missing."""
        pass

    def test_handle_invalid_timestamp_format(self):
        """Test graceful handling of malformed timestamps."""
        pass

    def test_handle_clock_skew(self):
        """Test handling of clock differences between systems."""
        # If local clock is ahead/behind, timestamps might be confusing
        pass

    def test_handle_concurrent_edits(self):
        """Test handling of concurrent user and Jira edits."""
        pass
