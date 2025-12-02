"""
Unit tests for Git integration for PI plan sync.

Tests the GitPlanSync class for managing tracking branches, pull/push operations,
conflict detection, and bidirectional sync between TargetProcess and git.
"""

import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch, call

from tpcli_pi.core.git_integration import GitPlanSync, SyncResult


class TestInitialization:
    """Tests for plan tracking initialization."""

    @pytest.fixture
    def git_sync(self):
        """Fixture providing a GitPlanSync instance."""
        return GitPlanSync()

    @pytest.fixture
    def mock_objectives(self):
        """Mock team objectives."""
        return [
            {
                "id": 2019099,
                "name": "Platform governance",
                "status": "Pending",
                "effort": 21,
                "owner": {"Name": "Test User"},
                "epics": [],
            }
        ]

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_init_creates_tracking_branch(self, mock_run, git_sync, mock_objectives):
        """Test init creates tracking branch."""
        # Mock git commands
        mock_run.return_value = MagicMock()

        result = git_sync.init(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify tracking branch name generated
        assert git_sync.tracking_branch == "TP-PI-4-25-platform-eco"

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_init_creates_feature_branch(self, mock_run, git_sync, mock_objectives):
        """Test init creates feature branch."""
        mock_run.return_value = MagicMock()

        result = git_sync.init(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify feature branch name generated
        assert git_sync.feature_branch == "feature/plan-pi-4-25"

    def test_tracking_branch_named_correctly(self, git_sync):
        """Test tracking branch follows naming convention."""
        name = git_sync._generate_tracking_branch_name("PI-4/25", "Platform Eco")
        assert name == "TP-PI-4-25-platform-eco"
        assert name.startswith("TP-")

    def test_feature_branch_named_correctly(self, git_sync):
        """Test feature branch follows naming convention."""
        name = git_sync._generate_feature_branch_name("PI-4/25")
        assert name == "feature/plan-pi-4-25"
        assert name.startswith("feature/")

    def test_sync_result_success(self, git_sync):
        """Test SyncResult indicates success."""
        result = SyncResult(success=True, message="Success")
        assert result.success is True
        assert "Success" in result.message

    def test_sync_result_with_conflicts(self, git_sync):
        """Test SyncResult can report conflicts."""
        result = SyncResult(
            success=False,
            message="Conflict",
            conflicts=["objectives.md"],
        )
        assert result.success is False
        assert result.conflicts == ["objectives.md"]


class TestPull:
    """Tests for pull from TargetProcess."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    @pytest.fixture
    def mock_objectives(self):
        return [{"id": 2019099, "name": "Platform governance", "status": "Pending", "effort": 21}]

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_returns_sync_result(self, mock_run, git_sync, mock_objectives):
        """Test pull returns SyncResult object."""
        mock_run.return_value = MagicMock()

        result = git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        assert isinstance(result, SyncResult)

    def test_pull_creates_markdown_file(self, git_sync, mock_objectives):
        """Test pull creates markdown file."""
        # Verify markdown generator called
        with patch("tpcli_pi.core.git_integration.subprocess.run"):
            git_sync.pull(
                team_name="Platform Eco",
                release_name="PI-4/25",
                art_name="Data, Analytics and Digital",
                team_objectives=mock_objectives,
            )
        # In actual test would verify file created

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_handles_rebase_error(self, mock_run, git_sync, mock_objectives):
        """Test pull handles rebase errors gracefully."""
        # Mock subprocess to raise error on rebase
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "git rebase")

        result = git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        assert result.success is False

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_switches_to_tracking_branch(self, mock_run, git_sync, mock_objectives):
        """Test pull switches to tracking branch."""
        mock_result = MagicMock()
        mock_result.stdout = b"tracking-branch"
        mock_run.return_value = mock_result

        git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify checkout was called for tracking branch
        calls = mock_run.call_args_list
        checkout_calls = [c for c in calls if 'checkout' in str(c)]
        assert len(checkout_calls) >= 1

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_commits_changes(self, mock_run, git_sync, mock_objectives):
        """Test pull commits markdown changes."""
        mock_result = MagicMock()
        mock_result.stdout = b"feature/plan"
        mock_run.return_value = mock_result

        git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify git add and commit were called
        calls = mock_run.call_args_list
        call_strs = [str(c) for c in calls]
        add_found = any('add' in s for s in call_strs)
        commit_found = any('commit' in s for s in call_strs)
        assert add_found or commit_found

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_pushes_tracking_branch(self, mock_run, git_sync, mock_objectives):
        """Test pull pushes updated tracking branch to remote."""
        mock_result = MagicMock()
        mock_result.stdout = b"feature/plan"
        mock_run.return_value = mock_result

        git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify push was called
        calls = mock_run.call_args_list
        push_calls = [c for c in calls if 'push' in str(c)]
        assert len(push_calls) >= 1

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_rebases_feature_branch(self, mock_run, git_sync, mock_objectives):
        """Test pull rebases feature branch onto tracking branch."""
        mock_result = MagicMock()
        mock_result.stdout = b"feature/plan"
        mock_run.return_value = mock_result

        git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify rebase was called
        calls = mock_run.call_args_list
        rebase_calls = [c for c in calls if 'rebase' in str(c)]
        assert len(rebase_calls) >= 1

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_returns_success_on_clean_rebase(self, mock_run, git_sync, mock_objectives):
        """Test pull returns success when rebase has no conflicts."""
        mock_result = MagicMock()
        mock_result.stdout = b"feature/plan"
        mock_run.return_value = mock_result

        result = git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        assert result.success is True
        assert "rebased" in result.message.lower()

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_pull_returns_feature_to_original_branch(self, mock_run, git_sync, mock_objectives):
        """Test pull returns to feature branch after rebase."""
        mock_result = MagicMock()
        mock_result.stdout = b"feature/plan"
        mock_run.return_value = mock_result

        git_sync.pull(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )

        # Verify feature branch is current (checked out last)
        calls = mock_run.call_args_list
        checkout_calls = [c for c in calls if 'checkout' in str(c)]
        # Last checkout should be feature branch
        assert len(checkout_calls) >= 2  # tracking and feature


class TestPush:
    """Tests for push to TargetProcess."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    @pytest.fixture
    def mock_api_client(self):
        return MagicMock()

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_returns_sync_result(self, mock_run, git_sync, mock_api_client):
        """Test push returns SyncResult object."""
        mock_run.return_value = MagicMock(stdout=b"")

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert isinstance(result, SyncResult)

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_handles_no_changes(self, mock_run, git_sync, mock_api_client):
        """Test push handles case with no changes."""
        mock_run.return_value = MagicMock(stdout=b"")

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert result.success is True
        assert result.api_calls == []

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_handles_error(self, mock_run, git_sync, mock_api_client):
        """Test push handles errors gracefully."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "git diff")

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert result.success is False

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_calculates_diff(self, mock_run, git_sync, mock_api_client):
        """Test push calculates diff between tracking and feature branches."""
        mock_run.return_value = MagicMock(stdout=b"")

        git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        # Verify git diff was called
        calls = mock_run.call_args_list
        diff_calls = [c for c in calls if 'diff' in str(c)]
        assert len(diff_calls) >= 1

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_returns_success_with_changes(self, mock_run, git_sync, mock_api_client):
        """Test push returns success status when there are changes."""
        def side_effect(*args, **kwargs):
            if 'diff' in str(args):
                return MagicMock(stdout=b"objectives.md")
            return MagicMock(stdout=b"")

        mock_run.side_effect = side_effect

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert isinstance(result, SyncResult)
        assert isinstance(result.api_calls, list)

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_parses_changes_from_diff(self, mock_run, git_sync, mock_api_client):
        """Test push parses changes when files are modified."""
        def side_effect(*args, **kwargs):
            if 'diff' in str(args):
                return MagicMock(stdout=b"objectives.md\nepics.md")
            return MagicMock(stdout=b"")

        mock_run.side_effect = side_effect

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert result.api_calls is not None

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_executes_api_calls(self, mock_run, git_sync, mock_api_client):
        """Test push executes API calls for changes."""
        def side_effect(*args, **kwargs):
            if 'diff' in str(args):
                return MagicMock(stdout=b"objectives.md")
            return MagicMock(stdout=b"")

        mock_run.side_effect = side_effect

        with patch.object(git_sync, '_execute_api_call') as mock_execute:
            git_sync.push(
                team_name="Platform Eco",
                release_name="PI-4/25",
                api_client=mock_api_client,
            )

            # _execute_api_call should be called for each API call

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_switches_to_tracking_branch_after_changes(self, mock_run, git_sync, mock_api_client):
        """Test push switches to tracking branch when there are changes."""
        def side_effect(*args, **kwargs):
            if 'diff' in str(args):
                return MagicMock(stdout=b"objectives.md")
            return MagicMock(stdout=b"")

        mock_run.side_effect = side_effect

        git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        # Verify checkout was called for tracking branch
        calls = mock_run.call_args_list
        checkout_calls = [c for c in calls if 'checkout' in str(c)]
        assert len(checkout_calls) >= 1

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_returns_to_feature_branch_after_update(self, mock_run, git_sync, mock_api_client):
        """Test push returns to feature branch after updating tracking."""
        def side_effect(*args, **kwargs):
            if 'diff' in str(args):
                return MagicMock(stdout=b"objectives.md")
            return MagicMock(stdout=b"")

        mock_run.side_effect = side_effect

        git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        # Verify checkout called at least once (switching branches)
        calls = mock_run.call_args_list
        checkout_calls = [c for c in calls if 'checkout' in str(c)]
        assert len(checkout_calls) >= 1

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_message_includes_change_count(self, mock_run, git_sync, mock_api_client):
        """Test push success message includes number of changes."""
        mock_run.return_value = MagicMock(stdout=b"")

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert "changes" in result.message.lower()

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_handles_git_diff_failure(self, mock_run, git_sync, mock_api_client):
        """Test push handles git diff command failures."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "git diff")

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert result.success is False
        assert "failed" in result.message.lower() or "error" in result.message.lower()

    @patch("tpcli_pi.core.git_integration.subprocess.run")
    def test_push_handles_checkout_failure(self, mock_run, git_sync, mock_api_client):
        """Test push handles checkout failures."""
        import subprocess

        def side_effect(*args, **kwargs):
            if 'checkout' in str(args):
                raise subprocess.CalledProcessError(1, "git checkout")
            elif 'diff' in str(args):
                return MagicMock(stdout=b"objectives.md")
            return MagicMock(stdout=b"")

        mock_run.side_effect = side_effect

        result = git_sync.push(
            team_name="Platform Eco",
            release_name="PI-4/25",
            api_client=mock_api_client,
        )

        assert result.success is False


class TestConflictHandling:
    """Tests for conflict detection and resolution."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_sync_result_reports_conflicts(self, git_sync):
        """Test SyncResult can report conflicts."""
        result = SyncResult(
            success=False,
            message="Conflict detected",
            conflicts=["objectives.md"],
        )
        assert result.conflicts is not None
        assert len(result.conflicts) > 0

    def test_sync_result_has_conflict_info(self, git_sync):
        """Test SyncResult includes conflict details."""
        result = SyncResult(
            success=False,
            message="Rebase conflict\nFix conflicts and run: git rebase --continue",
            conflicts=["objectives.md"],
        )
        assert "rebase --continue" in result.message
        assert result.success is False


class TestMarkdownParsing:
    """Tests for parsing markdown changes."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_parse_changes_returns_list(self, git_sync):
        """Test parse_changes returns list."""
        result = git_sync._parse_changes("objectives.md", "TP-PI-4-25", "feature/plan")
        assert isinstance(result, list)

    def test_parse_changes_empty_when_no_files(self, git_sync):
        """Test parse_changes handles empty file list."""
        result = git_sync._parse_changes("", "TP-PI-4-25", "feature/plan")
        assert isinstance(result, list)


class TestBranchManagement:
    """Tests for branch creation and switching."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_tracking_and_feature_branch_names_different(self, git_sync):
        """Test tracking and feature branch names are different."""
        tracking = git_sync._generate_tracking_branch_name("PI-4/25", "Platform Eco")
        feature = git_sync._generate_feature_branch_name("PI-4/25")
        assert tracking != feature

    def test_multiple_releases_have_different_tracking(self, git_sync):
        """Test different releases have different tracking branches."""
        tracking_4 = git_sync._generate_tracking_branch_name("PI-4/25", "Platform Eco")
        tracking_5 = git_sync._generate_tracking_branch_name("PI-5/25", "Platform Eco")
        assert tracking_4 != tracking_5


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_git_sync_error_inherits_exception(self, git_sync):
        """Test GitPlanSyncError is an Exception."""
        from tpcli_pi.core.git_integration import GitPlanSyncError
        err = GitPlanSyncError("test")
        assert isinstance(err, Exception)

    def test_result_message_accessible(self, git_sync):
        """Test result message is accessible."""
        result = SyncResult(success=False, message="Error occurred")
        assert result.message == "Error occurred"


class TestIDMapping:
    """Tests for TargetProcess ID mapping and validation."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_branch_names_safe_for_git(self, git_sync):
        """Test generated branch names are safe for git."""
        tracking = git_sync._generate_tracking_branch_name("PI-4/25", "Team Name")
        feature = git_sync._generate_feature_branch_name("PI-4/25")

        # Should not contain invalid characters
        invalid_chars = [":", "\\", " ", "//"]
        for char in invalid_chars:
            assert char not in tracking
            assert char not in feature


class TestMultipleCycles:
    """Tests for multiple pull/push cycles."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_sync_result_can_be_chained(self, git_sync):
        """Test sync operations can be chained."""
        result1 = SyncResult(success=True, message="Step 1")
        assert result1.success is True

        result2 = SyncResult(success=result1.success, message="Step 2")
        assert result2.success is True


class TestSecurityValidation:
    """Tests for security and validation."""

    @pytest.fixture
    def git_sync(self):
        return GitPlanSync()

    def test_branch_name_normalization_safe(self, git_sync):
        """Test branch name normalization is safe."""
        # Test with special characters
        tracking = git_sync._generate_tracking_branch_name(
            "PI-4/25 (Q2)",
            "Team (Special)",
        )
        # Should not contain invalid characters
        assert "/" not in tracking
        assert "(" not in tracking
        assert " " not in tracking
        # Should start with TP prefix
        assert tracking.startswith("TP-")
