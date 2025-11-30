"""TargetProcess API client wrapper for PI planning tools."""

import json
import subprocess
from functools import lru_cache
from typing import Any, Dict, List, Optional

from tpcli_pi.models.entities import (
    AgileReleaseTrain,
    Feature,
    PIObjective,
    ProgramPIObjective,
    Release,
    Team,
    TeamPIObjective,
    User,
)


class TPAPIError(Exception):
    """Base exception for TargetProcess API errors."""

    pass


class TPAPIClient:
    """
    Client for querying TargetProcess via tpcli subprocess.

    All queries return typed entity objects. Uses caching to minimize
    subprocess overhead for repeated queries.
    """

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize the TargetProcess API client.

        Args:
            verbose: Enable verbose output for debugging
        """
        self.verbose = verbose
        self._cache: Dict[str, Any] = {}

    def _run_tpcli(
        self, entity_type: str, args: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute tpcli command and return parsed JSON results.

        Args:
            entity_type: TargetProcess entity type (e.g., 'Releases', 'Teams')
            args: Additional tpcli arguments (e.g., ['--where', 'condition'])

        Returns:
            List of parsed JSON objects from API response

        Raises:
            TPAPIError: If tpcli command fails or returns invalid JSON
        """
        cmd = ["tpcli", "list", entity_type, "--take", "1000"]
        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

            # Extract JSON from output (tpcli may output request/response metadata)
            output = result.stdout
            json_start = output.find("[")
            if json_start == -1:
                json_start = output.find("{")

            if json_start == -1:
                raise TPAPIError(f"No JSON found in tpcli output: {output}")

            json_str = output[json_start:]

            # Handle both array and single object responses
            if json_str.strip().startswith("["):
                return json.loads(json_str)
            else:
                return [json.loads(json_str)]

        except subprocess.TimeoutExpired:
            raise TPAPIError(f"tpcli command timed out: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            raise TPAPIError(
                f"tpcli command failed: {' '.join(cmd)}\n"
                f"stderr: {e.stderr}"
            )
        except json.JSONDecodeError as e:
            raise TPAPIError(
                f"Failed to parse tpcli JSON response: {e}\n"
                f"Raw output: {output}"
            )

    def _cache_key(self, entity_type: str, args: Optional[List[str]] = None) -> str:
        """Generate cache key for a query."""
        args_str = "_".join(args) if args else ""
        return f"{entity_type}:{args_str}"

    def _get_cached(
        self, entity_type: str, args: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get result from cache if available."""
        key = self._cache_key(entity_type, args)
        return self._cache.get(key)

    def _set_cached(
        self,
        entity_type: str,
        results: List[Dict[str, Any]],
        args: Optional[List[str]] = None,
    ) -> None:
        """Store result in cache."""
        key = self._cache_key(entity_type, args)
        self._cache[key] = results

    # High-level query methods

    def get_arts(self) -> List[AgileReleaseTrain]:
        """Get all Agile Release Trains."""
        cached = self._get_cached("AgileReleaseTrains")
        if cached is None:
            cached = self._run_tpcli("AgileReleaseTrains")
            self._set_cached("AgileReleaseTrains", cached)

        return [self._parse_art(item) for item in cached]

    def get_art_by_name(self, name: str) -> Optional[AgileReleaseTrain]:
        """Get ART by name."""
        arts = self.get_arts()
        for art in arts:
            if art.name == name:
                return art
        return None

    def get_teams(self, art_id: Optional[int] = None) -> List[Team]:
        """Get all teams, optionally filtered by ART."""
        args = None
        if art_id is not None:
            args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]

        cached = self._get_cached("Teams", args)
        if cached is None:
            cached = self._run_tpcli("Teams", args)
            self._set_cached("Teams", cached, args)

        return [self._parse_team(item) for item in cached]

    def get_team_by_name(
        self, name: str, art_id: Optional[int] = None
    ) -> Optional[Team]:
        """Get team by name, optionally within specific ART."""
        teams = self.get_teams(art_id)
        for team in teams:
            if team.name == name:
                return team
        return None

    def get_releases(self, art_id: Optional[int] = None) -> List[Release]:
        """Get all releases, optionally filtered by ART."""
        args = None
        if art_id is not None:
            args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]

        cached = self._get_cached("Releases", args)
        if cached is None:
            cached = self._run_tpcli("Releases", args)
            self._set_cached("Releases", cached, args)

        return [self._parse_release(item) for item in cached]

    def get_release_by_name(
        self, name: str, art_id: Optional[int] = None
    ) -> Optional[Release]:
        """Get release by name, optionally within specific ART."""
        releases = self.get_releases(art_id)
        for release in releases:
            if release.name == name:
                return release
        return None

    def get_program_pi_objectives(
        self, art_id: Optional[int] = None, release_id: Optional[int] = None
    ) -> List[ProgramPIObjective]:
        """Get program-level PI objectives."""
        args: Optional[List[str]] = None
        if art_id is not None:
            args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]
        if release_id is not None:
            where = f"Release.Id eq {release_id}"
            if args:
                where = f"AgileReleaseTrain.Id eq {art_id} and {where}"
                args = ["--where", where]
            else:
                args = ["--where", where]

        cached = self._get_cached("ProgramPIObjectives", args)
        if cached is None:
            cached = self._run_tpcli("ProgramPIObjectives", args)
            self._set_cached("ProgramPIObjectives", cached, args)

        return [self._parse_program_objective(item) for item in cached]

    def get_team_pi_objectives(
        self,
        team_id: Optional[int] = None,
        art_id: Optional[int] = None,
        release_id: Optional[int] = None,
    ) -> List[TeamPIObjective]:
        """Get team-level PI objectives, optionally filtered by team/ART/release."""
        args: Optional[List[str]] = None
        where_clauses: List[str] = []

        if team_id is not None:
            where_clauses.append(f"Team.Id eq {team_id}")
        if art_id is not None:
            where_clauses.append(f"Team.AgileReleaseTrain.Id eq {art_id}")
        if release_id is not None:
            where_clauses.append(f"Release.Id eq {release_id}")

        if where_clauses:
            args = ["--where", " and ".join(where_clauses)]

        cached = self._get_cached("TeamPIObjectives", args)
        if cached is None:
            cached = self._run_tpcli("TeamPIObjectives", args)
            self._set_cached("TeamPIObjectives", cached, args)

        return [self._parse_team_objective(item) for item in cached]

    def get_features(
        self,
        team_id: Optional[int] = None,
        release_id: Optional[int] = None,
        parent_epic_id: Optional[int] = None,
    ) -> List[Feature]:
        """Get features, optionally filtered by team/release/epic."""
        args: Optional[List[str]] = None
        where_clauses: List[str] = []

        if team_id is not None:
            where_clauses.append(f"Team.Id eq {team_id}")
        if release_id is not None:
            where_clauses.append(f"Release.Id eq {release_id}")
        if parent_epic_id is not None:
            where_clauses.append(f"Parent.Id eq {parent_epic_id}")

        if where_clauses:
            args = ["--where", " and ".join(where_clauses)]

        cached = self._get_cached("Features", args)
        if cached is None:
            cached = self._run_tpcli("Features", args)
            self._set_cached("Features", cached, args)

        return [self._parse_feature(item) for item in cached]

    # Parsing methods

    def _parse_user(self, data: Dict[str, Any]) -> User:
        """Parse User entity from API response."""
        return User(
            id=data.get("Id", 0),
            first_name=data.get("FirstName", ""),
            last_name=data.get("LastName", ""),
            email=data.get("Email", ""),
        )

    def _parse_team(self, data: Dict[str, Any]) -> Team:
        """Parse Team entity from API response."""
        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        return Team(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
            owner=owner,
            member_count=data.get("Members", {}).get("length", 0)
            if isinstance(data.get("Members"), dict)
            else 0,
            is_active=data.get("IsActive", True),
            art_id=data.get("AgileReleaseTrain", {}).get("Id")
            if isinstance(data.get("AgileReleaseTrain"), dict)
            else None,
            art_name=data.get("AgileReleaseTrain", {}).get("Name")
            if isinstance(data.get("AgileReleaseTrain"), dict)
            else None,
        )

    def _parse_art(self, data: Dict[str, Any]) -> AgileReleaseTrain:
        """Parse AgileReleaseTrain entity from API response."""
        return AgileReleaseTrain(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
        )

    def _parse_release(self, data: Dict[str, Any]) -> Release:
        """Parse Release entity from API response."""
        from datetime import datetime

        start_date_str = data.get("StartDate")
        end_date_str = data.get("EndDate")

        start_date = (
            datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            if start_date_str
            else None
        )
        end_date = (
            datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            if end_date_str
            else None
        )

        return Release(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
            start_date=start_date or datetime.now(),
            end_date=end_date or datetime.now(),
            art_id=data.get("AgileReleaseTrain", {}).get("Id")
            if isinstance(data.get("AgileReleaseTrain"), dict)
            else 0,
            art_name=data.get("AgileReleaseTrain", {}).get("Name")
            if isinstance(data.get("AgileReleaseTrain"), dict)
            else "",
            is_current=data.get("IsCurrent", False),
        )

    def _parse_program_objective(self, data: Dict[str, Any]) -> ProgramPIObjective:
        """Parse ProgramPIObjective entity from API response."""
        from datetime import datetime

        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        start_date_str = data.get("StartDate")
        end_date_str = data.get("EndDate")
        created_date_str = data.get("CreatedDate")

        start_date = (
            datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            if start_date_str
            else None
        )
        end_date = (
            datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            if end_date_str
            else None
        )
        created_date = (
            datetime.fromisoformat(created_date_str.replace("Z", "+00:00"))
            if created_date_str
            else None
        )

        return ProgramPIObjective(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
            status=data.get("Status", "Pending"),
            owner=owner,
            description=data.get("Description"),
            start_date=start_date,
            end_date=end_date,
            release_id=data.get("Release", {}).get("Id")
            if isinstance(data.get("Release"), dict)
            else None,
            release_name=data.get("Release", {}).get("Name")
            if isinstance(data.get("Release"), dict)
            else None,
            effort=data.get("Effort", 0),
            created_date=created_date,
            art_id=data.get("AgileReleaseTrain", {}).get("Id")
            if isinstance(data.get("AgileReleaseTrain"), dict)
            else None,
            art_name=data.get("AgileReleaseTrain", {}).get("Name")
            if isinstance(data.get("AgileReleaseTrain"), dict)
            else None,
        )

    def _parse_team_objective(self, data: Dict[str, Any]) -> TeamPIObjective:
        """Parse TeamPIObjective entity from API response."""
        from datetime import datetime

        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        start_date_str = data.get("StartDate")
        end_date_str = data.get("EndDate")
        created_date_str = data.get("CreatedDate")

        start_date = (
            datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            if start_date_str
            else None
        )
        end_date = (
            datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            if end_date_str
            else None
        )
        created_date = (
            datetime.fromisoformat(created_date_str.replace("Z", "+00:00"))
            if created_date_str
            else None
        )

        return TeamPIObjective(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
            status=data.get("Status", "Pending"),
            owner=owner,
            description=data.get("Description"),
            start_date=start_date,
            end_date=end_date,
            release_id=data.get("Release", {}).get("Id")
            if isinstance(data.get("Release"), dict)
            else None,
            release_name=data.get("Release", {}).get("Name")
            if isinstance(data.get("Release"), dict)
            else None,
            effort=data.get("Effort", 0),
            created_date=created_date,
            team_id=data.get("Team", {}).get("Id")
            if isinstance(data.get("Team"), dict)
            else None,
            team_name=data.get("Team", {}).get("Name")
            if isinstance(data.get("Team"), dict)
            else None,
            committed=data.get("Committed", False),
        )

    def _parse_feature(self, data: Dict[str, Any]) -> Feature:
        """Parse Feature entity from API response."""
        from datetime import datetime

        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        team = None
        if "Team" in data and data["Team"]:
            team = self._parse_team(data["Team"])

        created_date_str = data.get("CreatedDate")
        created_date = (
            datetime.fromisoformat(created_date_str.replace("Z", "+00:00"))
            if created_date_str
            else None
        )

        return Feature(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
            status=data.get("Status", "Pending"),
            effort=data.get("Effort", 0),
            owner=owner,
            team=team,
            release_id=data.get("Release", {}).get("Id")
            if isinstance(data.get("Release"), dict)
            else None,
            release_name=data.get("Release", {}).get("Name")
            if isinstance(data.get("Release"), dict)
            else None,
            parent_epic_id=data.get("Parent", {}).get("Id")
            if isinstance(data.get("Parent"), dict)
            else None,
            parent_epic_name=data.get("Parent", {}).get("Name")
            if isinstance(data.get("Parent"), dict)
            else None,
            description=data.get("Description"),
            created_date=created_date,
        )

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
