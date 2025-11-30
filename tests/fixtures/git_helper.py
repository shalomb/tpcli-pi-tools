"""
Git repository test fixtures and helpers.

Provides utilities for creating, managing, and cleaning up temporary git repositories
for testing git operations, branching, merging, and conflict scenarios.

Usage:
    from tests.fixtures.git_helper import GitTestRepo

    # Create a temporary git repository
    repo = GitTestRepo()

    # Create branches and commits
    repo.create_branch("main")
    repo.write_file("README.md", "# Test Project")
    repo.commit("Initial commit")

    # Create another branch for feature work
    repo.create_branch("feature/my-feature")
    repo.write_file("feature.md", "# Feature")
    repo.commit("Add feature")

    # Switch back to main and make conflicting changes
    repo.checkout("main")
    repo.write_file("feature.md", "# Different content")
    repo.commit("Add different feature")

    # Now feature branch has a conflict
    # Clean up
    repo.cleanup()
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any


class GitTestRepo:
    """
    Manage a temporary git repository for testing.

    Provides high-level operations for creating branches, commits,
    simulating conflicts, and managing repository state.
    """

    def __init__(self, initial_branch: str = "main") -> None:
        """
        Initialize a temporary git repository.

        Args:
            initial_branch: Name of the initial branch (default: main)
        """
        self.tmpdir = tempfile.mkdtemp(prefix="git-test-repo-")
        self.repo_path = Path(self.tmpdir)
        self.initial_branch = initial_branch
        self.current_branch = initial_branch
        self.commits: Dict[str, List[str]] = {}  # branch -> list of commit hashes

        # Initialize repository
        self._run_git("init")
        self._run_git("config", "user.email", "test@example.com")
        self._run_git("config", "user.name", "Test User")

        # Create initial branch (git init creates 'master' by default)
        if initial_branch != "master":
            self._run_git("checkout", "-b", initial_branch)
        self.current_branch = initial_branch

        # Create initial commit so branches can be created
        self._create_initial_commit()

    def _create_initial_commit(self) -> None:
        """Create initial commit in the repository."""
        self.write_file(".gitkeep", "")
        self._run_git("add", ".gitkeep")
        self._run_git("commit", "-m", "Initial commit")

    def _run_git(self, *args: str, check: bool = True) -> str:
        """
        Run a git command in the repository.

        Args:
            *args: Git command arguments
            check: If True, raise exception on non-zero exit

        Returns:
            Command stdout as string

        Raises:
            subprocess.CalledProcessError: If command fails and check=True
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                output=result.stdout,
                stderr=result.stderr,
            )

        return result.stdout.strip()

    def write_file(
        self,
        filename: str,
        content: str,
        create_dirs: bool = True,
    ) -> Path:
        """
        Write a file to the repository.

        Args:
            filename: Relative path within repo
            content: File content
            create_dirs: If True, create parent directories as needed

        Returns:
            Path to the created file
        """
        filepath = self.repo_path / filename

        if create_dirs:
            filepath.parent.mkdir(parents=True, exist_ok=True)

        filepath.write_text(content)
        return filepath

    def read_file(self, filename: str) -> str:
        """
        Read a file from the repository.

        Args:
            filename: Relative path within repo

        Returns:
            File content
        """
        filepath = self.repo_path / filename
        return filepath.read_text()

    def add_file(self, filename: str) -> None:
        """
        Stage a file for commit.

        Args:
            filename: File to stage
        """
        self._run_git("add", filename)

    def add_all(self) -> None:
        """Stage all changes."""
        self._run_git("add", ".")

    def commit(self, message: str, filename: Optional[str] = None) -> str:
        """
        Create a commit.

        Args:
            message: Commit message
            filename: If provided, only commit this file

        Returns:
            Commit hash
        """
        if filename:
            self.add_file(filename)
        else:
            self.add_all()

        self._run_git("commit", "-m", message)

        # Get commit hash
        commit_hash = self._run_git("rev-parse", "HEAD")

        if self.current_branch not in self.commits:
            self.commits[self.current_branch] = []
        self.commits[self.current_branch].append(commit_hash)

        return commit_hash

    def create_branch(self, branch_name: str, start_point: Optional[str] = None) -> None:
        """
        Create a new branch.

        Args:
            branch_name: Name of the branch
            start_point: If provided, start from this commit/branch
        """
        if start_point:
            self._run_git("branch", branch_name, start_point)
        else:
            self._run_git("branch", branch_name)

    def checkout(self, branch_name: str, create: bool = False) -> None:
        """
        Checkout a branch.

        Args:
            branch_name: Branch to checkout
            create: If True, create branch if it doesn't exist
        """
        if create:
            self._run_git("checkout", "-b", branch_name)
        else:
            self._run_git("checkout", branch_name)

        self.current_branch = branch_name

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        return self.current_branch

    def get_branch_list(self) -> List[str]:
        """Get list of all branches in the repository."""
        output = self._run_git("branch", "-a")
        return [line.strip().lstrip("* ") for line in output.split("\n") if line.strip()]

    def get_commits_on_branch(self, branch_name: str) -> List[str]:
        """Get all commit hashes on a branch."""
        return self.commits.get(branch_name, [])

    def get_commit_count(self, branch_name: Optional[str] = None) -> int:
        """
        Get the number of commits on a branch.

        Args:
            branch_name: Branch to count (default: current branch)

        Returns:
            Number of commits
        """
        if branch_name is None:
            branch_name = self.current_branch

        try:
            output = self._run_git("rev-list", "--count", branch_name)
            return int(output)
        except (ValueError, subprocess.CalledProcessError):
            return 0

    def get_file_contents_at_commit(
        self,
        filename: str,
        commit: str = "HEAD",
    ) -> str:
        """
        Get file contents at a specific commit.

        Args:
            filename: File to read
            commit: Commit reference (default: HEAD)

        Returns:
            File contents
        """
        try:
            return self._run_git("show", f"{commit}:{filename}")
        except subprocess.CalledProcessError:
            return ""

    def create_conflict_scenario(
        self,
        filename: str,
        main_content: str,
        feature_content: str,
    ) -> None:
        """
        Create a merge conflict scenario.

        Args:
            filename: File that will have conflicts
            main_content: Content on main branch
            feature_content: Content on feature branch
        """
        # Start on main branch
        if self.current_branch != self.initial_branch:
            self.checkout(self.initial_branch)

        # Write content on main
        self.write_file(filename, main_content)
        self.commit(f"Add {filename} on main", filename)

        # Create and switch to feature branch
        feature_branch = "feature/conflict-test"
        self.create_branch(feature_branch, self.initial_branch)
        self.checkout(feature_branch)

        # Write different content on feature
        self.write_file(filename, feature_content)
        self.commit(f"Add {filename} on feature", filename)

    def simulate_conflict(self) -> None:
        """
        Simulate a merge conflict by checking out main and merging feature.

        This will leave the repository in a conflicted state.
        """
        if self.current_branch == "feature/conflict-test":
            # Already have a feature branch with conflicting content
            self.checkout(self.initial_branch)
            # This should create a conflict
            self._run_git("merge", "feature/conflict-test", check=False)
        else:
            # Just try a merge that will fail
            self.checkout(self.initial_branch)
            self._run_git("merge", "--no-ff", "feature/conflict-test", check=False)

    def get_status(self) -> str:
        """Get git status output."""
        return self._run_git("status", "--short")

    def get_diff(self, from_ref: str = "HEAD~1", to_ref: str = "HEAD") -> str:
        """
        Get diff between two commits.

        Args:
            from_ref: Starting commit
            to_ref: Ending commit

        Returns:
            Diff output
        """
        try:
            return self._run_git("diff", from_ref, to_ref)
        except subprocess.CalledProcessError:
            return ""

    def get_log(self, max_count: int = 10, oneline: bool = True) -> List[str]:
        """
        Get commit log.

        Args:
            max_count: Maximum number of commits to return
            oneline: If True, return one-line format

        Returns:
            List of log entries
        """
        args = ["log", f"--max-count={max_count}"]
        if oneline:
            args.append("--oneline")

        output = self._run_git(*args)
        return [line.strip() for line in output.split("\n") if line.strip()]

    def reset_to_commit(self, commit: str = "HEAD~1") -> None:
        """
        Reset to a specific commit.

        Args:
            commit: Commit reference
        """
        self._run_git("reset", "--hard", commit)

    def cleanup(self) -> None:
        """Remove the temporary repository."""
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)


class GitBranchScenario:
    """
    Helper for setting up common git branch scenarios.

    Provides pre-built scenarios for testing:
    - Multiple feature branches
    - Diverged histories
    - Merge conflicts
    - Linear history
    """

    @staticmethod
    def setup_simple_workflow(repo: GitTestRepo) -> Dict[str, Any]:
        """
        Set up a simple main + feature workflow.

        Structure:
            main: [initial, update1]
            feature: [initial, feature1, feature2]

        Args:
            repo: GitTestRepo instance

        Returns:
            Dictionary with branch info and commit hashes
        """
        # Create initial file on main
        repo.write_file("README.md", "# Project")
        main_initial = repo.commit("Initial commit")

        # Add another commit on main
        repo.write_file("README.md", "# Project\n\nUpdated")
        main_update = repo.commit("Update README")

        # Create feature branch from main
        repo.create_branch("feature/my-feature")
        repo.checkout("feature/my-feature")

        # Add feature commits
        repo.write_file("feature.py", "def feature(): pass")
        feature_1 = repo.commit("Add feature function")

        repo.write_file("feature.py", "def feature(): pass\ndef helper(): pass")
        feature_2 = repo.commit("Add helper function")

        return {
            "main": {
                "commits": [main_initial, main_update],
                "branch": "main",
            },
            "feature": {
                "commits": [main_initial, feature_1, feature_2],
                "branch": "feature/my-feature",
            },
        }

    @staticmethod
    def setup_tracking_branch_scenario(repo: GitTestRepo) -> Dict[str, Any]:
        """
        Set up a tracking branch + feature branch scenario.

        Structure:
            tracking: [init, tp-update1, tp-update2]
            feature: [init, user-change1, user-change2]

        Args:
            repo: GitTestRepo instance

        Returns:
            Dictionary with branch info
        """
        # Create initial objectives markdown on main/tracking
        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: Pending\nEffort: 5\n",
        )
        init_commit = repo.commit("Initial objectives from TargetProcess")

        # Create tracking branch
        repo.create_branch("TP-PI-4-25-platform-eco")
        repo.checkout("TP-PI-4-25-platform-eco")

        # Add TP updates
        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: In Progress\nEffort: 5\n",
        )
        tp_update1 = repo.commit("TP sync: Update status")

        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: In Progress\nEffort: 8\n",
        )
        tp_update2 = repo.commit("TP sync: Update effort")

        # Create feature branch from tracking
        repo.create_branch("feature/plan-pi-4-25", "TP-PI-4-25-platform-eco")
        repo.checkout("feature/plan-pi-4-25")

        # User makes changes on feature
        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: In Progress\nEffort: 6\nOwner: John Doe\n",
        )
        user_change1 = repo.commit("Add owner to Objective 1")

        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: In Progress\nEffort: 6\nOwner: John Doe\n\n## Objective 2\nStatus: Pending\nEffort: 3\n",
        )
        user_change2 = repo.commit("Add Objective 2")

        return {
            "tracking": {
                "branch": "TP-PI-4-25-platform-eco",
                "commits": [init_commit, tp_update1, tp_update2],
            },
            "feature": {
                "branch": "feature/plan-pi-4-25",
                "commits": [init_commit, tp_update1, tp_update2, user_change1, user_change2],
            },
        }

    @staticmethod
    def setup_conflict_scenario(repo: GitTestRepo) -> Dict[str, Any]:
        """
        Set up a merge conflict scenario.

        Structure:
            main: [init, update-effort-5]
            feature: [init, update-effort-8] (conflict on same file)

        Args:
            repo: GitTestRepo instance

        Returns:
            Dictionary with branch info
        """
        # Create initial file
        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: Pending\nEffort: 5\n",
        )
        init_commit = repo.commit("Initial objectives")

        # Update on main branch
        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: Pending\nEffort: 5\nComment: Main branch change\n",
        )
        main_update = repo.commit("Update on main")

        # Create feature branch from initial
        repo.create_branch("feature/conflict-test", init_commit)
        repo.checkout("feature/conflict-test")

        # Conflicting update on feature
        repo.write_file(
            "objectives.md",
            "# Team Objectives\n\n## Objective 1\nStatus: In Progress\nEffort: 8\nComment: Feature branch change\n",
        )
        feature_update = repo.commit("Update on feature")

        return {
            "main": {
                "branch": "main",
                "commits": [init_commit, main_update],
            },
            "feature": {
                "branch": "feature/conflict-test",
                "commits": [init_commit, feature_update],
            },
        }


# Pytest fixtures for easy integration

import pytest


@pytest.fixture
def git_repo() -> GitTestRepo:
    """Fixture providing a temporary git repository."""
    repo = GitTestRepo()
    yield repo
    repo.cleanup()


@pytest.fixture
def git_repo_with_branches() -> GitTestRepo:
    """Fixture providing a git repo with main + feature branches."""
    repo = GitTestRepo()
    GitBranchScenario.setup_simple_workflow(repo)
    repo.checkout("main")
    yield repo
    repo.cleanup()


@pytest.fixture
def git_repo_tracking_scenario() -> GitTestRepo:
    """Fixture providing a git repo with tracking + feature branches."""
    repo = GitTestRepo()
    GitBranchScenario.setup_tracking_branch_scenario(repo)
    repo.checkout("feature/plan-pi-4-25")
    yield repo
    repo.cleanup()


@pytest.fixture
def git_repo_conflict_scenario() -> GitTestRepo:
    """Fixture providing a git repo with a merge conflict."""
    repo = GitTestRepo()
    GitBranchScenario.setup_conflict_scenario(repo)
    yield repo
    repo.cleanup()
