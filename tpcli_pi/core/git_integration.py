"""
Git integration for PI plan sync.

Manages bidirectional sync between TargetProcess and git repository.
Handles tracking branches, pull/push operations, conflict detection,
and coordinated updates to markdown files.
"""

import subprocess
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


class GitPlanSyncError(Exception):
    """Base exception for git plan sync errors."""
    pass


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    message: str
    conflicts: Optional[List[str]] = None
    api_calls: Optional[List[Dict[str, Any]]] = None


class GitPlanSync:
    """
    Manage bidirectional sync between TargetProcess and git.

    Handles:
    - Creating and managing tracking branches (TP-PI-<release>-<team>)
    - Creating feature branches for user edits
    - Pulling latest from TargetProcess and rebasing
    - Pushing changes back to TargetProcess
    - Detecting and reporting conflicts
    - Managing remote synchronization
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialize git sync manager.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = repo_path
        self.tracking_branch: Optional[str] = None
        self.feature_branch: Optional[str] = None

    def init(
        self,
        team_name: str,
        release_name: str,
        art_name: str,
        team_objectives: List[Dict[str, Any]],
    ) -> SyncResult:
        """
        Initialize plan tracking for a team and release.

        Creates:
        1. Tracking branch: TP-<release>-<team>
        2. Initial markdown commit with TP data
        3. Feature branch: feature/plan-<release>
        4. Push tracking branch to remote

        Args:
            team_name: Team name
            release_name: Release/PI name
            art_name: ART name
            team_objectives: Initial team objectives from TP

        Returns:
            SyncResult with success status and branch information
        """
        try:
            # Generate branch names
            tracking_name = self._generate_tracking_branch_name(release_name, team_name)
            feature_name = self._generate_feature_branch_name(release_name)

            self.tracking_branch = tracking_name
            self.feature_branch = feature_name

            # Create tracking branch from main/master
            self._run_git(["checkout", "-b", tracking_name])

            # Export markdown and commit
            from tpcli_pi.core.markdown_generator import MarkdownGenerator
            generator = MarkdownGenerator()
            markdown = generator.generate(
                team_name=team_name,
                release_name=release_name,
                art_name=art_name,
                team_objectives=team_objectives,
            )
            filename = generator.get_filename(team_name, release_name)

            # Write markdown file
            with open(f"{self.repo_path}/{filename}", "w") as f:
                f.write(markdown)

            # Commit to tracking branch
            self._run_git(["add", filename])
            self._run_git(["commit", "-m", f"Initial {release_name} plan for {team_name}"])

            # Push tracking branch to remote
            self._run_git(["push", "-u", "origin", tracking_name])

            # Create and checkout feature branch
            self._run_git(["checkout", "-b", feature_name])

            return SyncResult(
                success=True,
                message=f"Initialized plan tracking for {release_name} {team_name}\n"
                        f"Created tracking branch: {tracking_name}\n"
                        f"Checked out feature branch: {feature_name}",
            )
        except Exception as e:
            return SyncResult(success=False, message=f"Initialization failed: {str(e)}")

    def pull(
        self,
        team_name: str,
        release_name: str,
        art_name: str,
        team_objectives: List[Dict[str, Any]],
    ) -> SyncResult:
        """
        Pull latest from TargetProcess and rebase feature branch.

        Process:
        1. Fetch latest state from TargetProcess API
        2. Export fresh markdown
        3. Update tracking branch with new markdown
        4. Push tracking branch to remote
        5. Rebase current branch onto updated tracking branch

        Args:
            team_name: Team name
            release_name: Release name
            art_name: ART name
            team_objectives: Latest objectives from TP API

        Returns:
            SyncResult with success/conflict status
        """
        try:
            tracking_name = self._generate_tracking_branch_name(release_name, team_name)

            # Switch to tracking branch
            current_branch = self._get_current_branch()
            self._run_git(["checkout", tracking_name])

            # Export fresh markdown from TP
            from tpcli_pi.core.markdown_generator import MarkdownGenerator
            generator = MarkdownGenerator()
            markdown = generator.generate(
                team_name=team_name,
                release_name=release_name,
                art_name=art_name,
                team_objectives=team_objectives,
            )
            filename = generator.get_filename(team_name, release_name)

            # Write updated markdown
            with open(f"{self.repo_path}/{filename}", "w") as f:
                f.write(markdown)

            # Commit to tracking branch
            self._run_git(["add", filename])
            self._run_git(["commit", "-m", f"Sync {release_name} from TargetProcess"])

            # Push to remote
            self._run_git(["push", "origin", tracking_name])

            # Switch back to feature branch and rebase
            self._run_git(["checkout", current_branch])

            try:
                self._run_git(["rebase", tracking_name])
                return SyncResult(
                    success=True,
                    message=f"Successfully rebased {current_branch} onto {tracking_name}\n"
                           f"Latest changes from TargetProcess applied",
                )
            except subprocess.CalledProcessError as e:
                # Rebase failed - likely due to conflicts
                return SyncResult(
                    success=False,
                    message=f"Rebase conflict detected in {filename}\n"
                           f"Fix conflicts and run: git rebase --continue",
                    conflicts=[filename],
                )
        except Exception as e:
            return SyncResult(success=False, message=f"Pull failed: {str(e)}")

    def push(
        self,
        team_name: str,
        release_name: str,
        api_client,
    ) -> SyncResult:
        """
        Push changes to TargetProcess.

        Process:
        1. Calculate diff from tracking branch to HEAD
        2. Parse markdown changes
        3. Create API call list (create/update operations)
        4. Execute API calls
        5. Update tracking branch with new state
        6. Push tracking branch to remote

        Args:
            team_name: Team name
            release_name: Release name
            api_client: TPAPIClient instance for API calls

        Returns:
            SyncResult with API calls made and success status
        """
        try:
            tracking_name = self._generate_tracking_branch_name(release_name, team_name)
            current_branch = self._get_current_branch()

            # Get diff between tracking and current branch
            diff_output = self._run_git(
                ["diff", f"{tracking_name}..HEAD", "--name-only"],
                capture_output=True,
            ).stdout.decode().strip()

            if not diff_output:
                return SyncResult(
                    success=True,
                    message="No changes to push",
                    api_calls=[],
                )

            # Parse changes from markdown
            api_calls = self._parse_changes(diff_output, tracking_name, current_branch)

            # Execute API calls
            for call_spec in api_calls:
                self._execute_api_call(call_spec, api_client)

            # Update tracking branch with fresh state from TP
            self._run_git(["checkout", tracking_name])

            # Re-export from TP to get current state
            # (In production, would call TP API to get fresh state)

            self._run_git(["checkout", current_branch])

            return SyncResult(
                success=True,
                message=f"Successfully pushed {len(api_calls)} changes to TargetProcess",
                api_calls=api_calls,
            )
        except Exception as e:
            return SyncResult(success=False, message=f"Push failed: {str(e)}")

    def _generate_tracking_branch_name(self, release: str, team: str) -> str:
        """Generate tracking branch name from release and team."""
        # Normalize release: keep uppercase, replace / with -, remove parens
        release_normalized = release.upper().replace("/", "-")
        release_normalized = re.sub(r"[^A-Z0-9-]", "", release_normalized)

        # Normalize team: lowercase, replace spaces with -, remove special chars
        team_normalized = team.lower().replace(" ", "-")
        team_normalized = re.sub(r"[^a-z0-9-]", "", team_normalized)

        return f"TP-{release_normalized}-{team_normalized}"

    def _generate_feature_branch_name(self, release: str) -> str:
        """Generate feature branch name from release."""
        release_normalized = release.lower().replace("/", "-")
        return f"feature/plan-{release_normalized}"

    def _run_git(self, args: List[str], capture_output: bool = False):
        """
        Execute a git command.

        Args:
            args: Git command arguments (without 'git' prefix)
            capture_output: Whether to capture output

        Returns:
            CompletedProcess result

        Raises:
            GitPlanSyncError: If git command fails
        """
        cmd = ["git", "-C", self.repo_path] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=True,
            )
            return result
        except subprocess.CalledProcessError as e:
            raise GitPlanSyncError(f"Git command failed: {' '.join(cmd)}\n{e.stderr}")

    def _get_current_branch(self) -> str:
        """Get currently checked out branch name."""
        result = self._run_git(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
        )
        return result.stdout.decode().strip()

    def _parse_changes(
        self,
        files_changed: str,
        tracking_branch: str,
        feature_branch: str,
    ) -> List[Dict[str, Any]]:
        """
        Parse changes from markdown diff.

        Args:
            files_changed: Files that changed
            tracking_branch: Tracking branch name
            feature_branch: Feature branch name

        Returns:
            List of API call specifications
        """
        api_calls = []

        # For now, return empty list - parsing logic would extract
        # objectives and epics from markdown and determine create/update/delete ops
        # This would be more complex in production

        return api_calls

    def _execute_api_call(self, call_spec: Dict[str, Any], api_client) -> None:
        """
        Execute an API call to TargetProcess.

        Args:
            call_spec: API call specification (operation, entity_type, params)
            api_client: TPAPIClient instance
        """
        # Placeholder for actual API execution
        # In production, would call appropriate method on api_client
        pass
