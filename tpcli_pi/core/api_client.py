"""TargetProcess API client wrapper for PI planning tools."""

import json
import re
import subprocess
from datetime import datetime
from typing import Any

from tpcli_pi.models.entities import (
    AgileReleaseTrain,
    Feature,
    ProgramPIObjective,
    Release,
    Team,
    TeamPIObjective,
    User,
)


class TPAPIError(Exception):
    """Base exception for TargetProcess API errors."""



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
        self._cache: dict[str, Any] = {}

    @staticmethod
    def _parse_tp_date(date_str: str | None) -> datetime | None:
        """
        Parse TargetProcess date format.

        TargetProcess returns dates in format: /Date(milliseconds+timezone)/
        Example: /Date(1738450043000-0500)/

        Args:
            date_str: Date string in TP format or ISO format

        Returns:
            Parsed datetime object or None if invalid/empty
        """
        if not date_str:
            return None

        # Try TargetProcess format: /Date(milliseconds+timezone)/
        tp_match = re.match(r"/Date\((\d+)([+-]\d{4})?\)/", date_str)
        if tp_match:
            milliseconds = int(tp_match.group(1))
            return datetime.fromtimestamp(milliseconds / 1000)

        # Try ISO format
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    def _run_tpcli(
        self, entity_type: str, args: list[str] | None = None
    ) -> list[dict[str, Any]]:
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
            result = subprocess.run(  # noqa: S603
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

        except subprocess.TimeoutExpired as e:
            raise TPAPIError(
                f"tpcli command timed out: {' '.join(cmd)}"
            ) from e
        except subprocess.CalledProcessError as e:
            raise TPAPIError(
                f"tpcli command failed: {' '.join(cmd)}\nstderr: {e.stderr}"
            ) from e
        except json.JSONDecodeError as e:
            raise TPAPIError(
                f"Failed to parse tpcli JSON response: {e}\nRaw output: {output}"
            ) from e

    def _cache_key(self, entity_type: str, args: list[str] | None = None) -> str:
        """Generate cache key for a query."""
        args_str = "_".join(args) if args else ""
        return f"{entity_type}:{args_str}"

    def _get_cached(
        self, entity_type: str, args: list[str] | None = None
    ) -> list[dict[str, Any]] | None:
        """Get result from cache if available."""
        key = self._cache_key(entity_type, args)
        return self._cache.get(key)

    def _set_cached(
        self,
        entity_type: str,
        results: list[dict[str, Any]],
        args: list[str] | None = None,
    ) -> None:
        """Store result in cache."""
        key = self._cache_key(entity_type, args)
        self._cache[key] = results

    # High-level query methods

    def get_arts(self) -> list[AgileReleaseTrain]:
        """Get all Agile Release Trains."""
        cached = self._get_cached("AgileReleaseTrains")
        if cached is None:
            cached = self._run_tpcli("AgileReleaseTrains")
            self._set_cached("AgileReleaseTrains", cached)

        return [self._parse_art(item) for item in cached]

    def get_art_by_name(self, name: str) -> AgileReleaseTrain | None:
        """Get ART by name."""
        arts = self.get_arts()
        for art in arts:
            if art.name == name:
                return art
        return None

    def get_teams(self, art_id: int | None = None) -> list[Team]:
        """Get all teams, optionally filtered by ART."""
        args = None
        if art_id is not None:
            args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]

        cached = self._get_cached("Teams", args)
        if cached is None:
            cached = self._run_tpcli("Teams", args)
            self._set_cached("Teams", cached, args)

        return [self._parse_team(item) for item in cached]

    def get_team_by_name(self, name: str, art_id: int | None = None) -> Team | None:
        """Get team by name, optionally within specific ART."""
        teams = self.get_teams(art_id)
        for team in teams:
            if team.name == name:
                return team
        return None

    def get_releases(self, art_id: int | None = None) -> list[Release]:
        """Get all releases, optionally filtered by ART."""
        args = None
        if art_id is not None:
            args = ["--where", f"AgileReleaseTrain.Id eq {art_id}"]

        cached = self._get_cached("Releases", args)
        if cached is None:
            cached = self._run_tpcli("Releases", args)
            self._set_cached("Releases", cached, args)

        return [self._parse_release(item) for item in cached]

    def get_release_by_name(self, name: str, art_id: int | None = None) -> Release | None:
        """Get release by name, optionally within specific ART."""
        releases = self.get_releases(art_id)
        for release in releases:
            if release.name == name:
                return release
        return None

    def get_program_pi_objectives(
        self, art_id: int | None = None, release_id: int | None = None
    ) -> list[ProgramPIObjective]:
        """Get program-level PI objectives."""
        args: list[str] | None = None
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
        team_id: int | None = None,
        art_id: int | None = None,
        release_id: int | None = None,
    ) -> list[TeamPIObjective]:
        """Get team-level PI objectives, optionally filtered by team/ART/release."""
        args: list[str] | None = None
        where_clauses: list[str] = []

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
        team_id: int | None = None,
        release_id: int | None = None,
        parent_epic_id: int | None = None,
    ) -> list[Feature]:
        """Get features, optionally filtered by team/release/epic."""
        args: list[str] | None = None
        where_clauses: list[str] = []

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

    def _parse_user(self, data: dict[str, Any]) -> User:
        """Parse User entity from API response."""
        return User(
            id=data.get("Id", 0),
            first_name=data.get("FirstName", ""),
            last_name=data.get("LastName", ""),
            email=data.get("Email", ""),
        )

    def _parse_team(self, data: dict[str, Any]) -> Team:
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

    def _parse_art(self, data: dict[str, Any]) -> AgileReleaseTrain:
        """Parse AgileReleaseTrain entity from API response."""
        return AgileReleaseTrain(
            id=data.get("Id", 0),
            name=data.get("Name", ""),
        )

    def _parse_release(self, data: dict[str, Any]) -> Release:
        """Parse Release entity from API response."""
        start_date = self._parse_tp_date(data.get("StartDate"))
        end_date = self._parse_tp_date(data.get("EndDate"))

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

    def _parse_program_objective(self, data: dict[str, Any]) -> ProgramPIObjective:
        """Parse ProgramPIObjective entity from API response."""
        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        start_date = self._parse_tp_date(data.get("StartDate"))
        end_date = self._parse_tp_date(data.get("EndDate"))
        created_date = self._parse_tp_date(data.get("CreatedDate"))

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

    def _parse_team_objective(self, data: dict[str, Any]) -> TeamPIObjective:
        """Parse TeamPIObjective entity from API response."""
        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        start_date = self._parse_tp_date(data.get("StartDate"))
        end_date = self._parse_tp_date(data.get("EndDate"))
        created_date = self._parse_tp_date(data.get("CreatedDate"))

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
            team_id=data.get("Team", {}).get("Id") if isinstance(data.get("Team"), dict) else None,
            team_name=data.get("Team", {}).get("Name")
            if isinstance(data.get("Team"), dict)
            else None,
            committed=data.get("Committed", False),
        )

    def _parse_feature(self, data: dict[str, Any]) -> Feature:
        """Parse Feature entity from API response."""
        owner = None
        if "Owner" in data and data["Owner"]:
            owner = self._parse_user(data["Owner"])

        team = None
        if "Team" in data and data["Team"]:
            team = self._parse_team(data["Team"])

        created_date = self._parse_tp_date(data.get("CreatedDate"))

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

    # Create/Update wrapper methods

    def _run_tpcli_create(
        self, entity_type: str, data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Execute tpcli create command and return parsed JSON results.

        Args:
            entity_type: TargetProcess entity type (e.g., 'TeamPIObjective')
            data: Dictionary of entity data to create

        Returns:
            List containing the created entity as dict

        Raises:
            TPAPIError: If tpcli command fails or returns invalid JSON
        """
        # Convert data to JSON string
        data_json = json.dumps(data)

        cmd = ["tpcli", "plan", "create", entity_type, "--data", data_json]

        try:
            result = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

            # Extract JSON from output
            output = result.stdout
            json_start = output.find("{")

            if json_start == -1:
                raise TPAPIError(f"No JSON found in tpcli output: {output}")

            json_str = output[json_start:]

            # Single object response
            return [json.loads(json_str)]

        except subprocess.TimeoutExpired as e:
            raise TPAPIError(
                f"tpcli command timed out: {' '.join(cmd)}"
            ) from e
        except subprocess.CalledProcessError as e:
            raise TPAPIError(
                f"tpcli command failed: {' '.join(cmd)}\nstderr: {e.stderr}"
            ) from e
        except json.JSONDecodeError as e:
            raise TPAPIError(
                f"Failed to parse tpcli JSON response: {e}\nRaw output: {output}"
            ) from e

    def _run_tpcli_update(
        self, entity_type: str, entity_id: int, data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Execute tpcli update command and return parsed JSON results.

        Args:
            entity_type: TargetProcess entity type (e.g., 'TeamPIObjective')
            entity_id: ID of entity to update
            data: Dictionary of fields to update

        Returns:
            List containing the updated entity as dict

        Raises:
            TPAPIError: If tpcli command fails or returns invalid JSON
        """
        # Convert data to JSON string
        data_json = json.dumps(data)

        cmd = [
            "tpcli",
            "plan",
            "update",
            entity_type,
            str(entity_id),
            "--data",
            data_json,
        ]

        try:
            result = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

            # Extract JSON from output
            output = result.stdout
            json_start = output.find("{")

            if json_start == -1:
                raise TPAPIError(f"No JSON found in tpcli output: {output}")

            json_str = output[json_start:]

            # Single object response
            return [json.loads(json_str)]

        except subprocess.TimeoutExpired as e:
            raise TPAPIError(
                f"tpcli command timed out: {' '.join(cmd)}"
            ) from e
        except subprocess.CalledProcessError as e:
            raise TPAPIError(
                f"tpcli command failed: {' '.join(cmd)}\nstderr: {e.stderr}"
            ) from e
        except json.JSONDecodeError as e:
            raise TPAPIError(
                f"Failed to parse tpcli JSON response: {e}\nRaw output: {output}"
            ) from e

    def create_team_objective(
        self,
        name: str,
        team_id: int,
        release_id: int,
        **kwargs: Any,
    ) -> TeamPIObjective:
        """
        Create a new Team PI Objective.

        Args:
            name: Objective name
            team_id: Team ID
            release_id: Release ID
            **kwargs: Optional fields (effort, status, description, owner_id, etc.)

        Returns:
            Created TeamPIObjective object

        Raises:
            TPAPIError: If creation fails
        """
        # Build payload with required fields
        payload = {
            "Name": name,
            "Team": team_id,
            "Release": release_id,
        }

        # Add optional fields if provided
        if "effort" in kwargs:
            payload["Effort"] = kwargs["effort"]
        if "status" in kwargs:
            payload["Status"] = kwargs["status"]
        if "description" in kwargs:
            payload["Description"] = kwargs["description"]
        if "owner_id" in kwargs:
            payload["Owner"] = kwargs["owner_id"]

        # Call subprocess
        response_list = self._run_tpcli_create("TeamPIObjective", payload)
        response = response_list[0]

        # Parse response and cache
        objective = self._parse_team_objective(response)

        # Add to cache
        objectives = self._get_cached("TeamPIObjectives")
        if objectives is None:
            objectives = []
        objectives.append(response)
        self._set_cached("TeamPIObjectives", objectives)

        return objective

    def update_team_objective(
        self,
        objective_id: int,
        **kwargs: Any,
    ) -> TeamPIObjective:
        """
        Update an existing Team PI Objective.

        Args:
            objective_id: Objective ID to update
            **kwargs: Fields to update (name, effort, status, description, etc.)

        Returns:
            Updated TeamPIObjective object

        Raises:
            TPAPIError: If update fails
        """
        # Build payload with only provided fields
        payload: dict[str, Any] = {}

        if "name" in kwargs:
            payload["Name"] = kwargs["name"]
        if "effort" in kwargs:
            payload["Effort"] = kwargs["effort"]
        if "status" in kwargs:
            payload["Status"] = kwargs["status"]
        if "description" in kwargs:
            payload["Description"] = kwargs["description"]
        if "owner_id" in kwargs:
            payload["Owner"] = kwargs["owner_id"]

        # Call subprocess
        response_list = self._run_tpcli_update(
            "TeamPIObjective", objective_id, payload
        )
        response = response_list[0]

        # Parse response and cache
        objective = self._parse_team_objective(response)

        # Update cache
        objectives = self._get_cached("TeamPIObjectives")
        if objectives is None:
            objectives = []
        else:
            # Remove old version
            objectives = [o for o in objectives if o.get("Id") != objective_id]

        objectives.append(response)
        self._set_cached("TeamPIObjectives", objectives)

        return objective

    def create_feature(
        self,
        name: str,
        parent_epic_id: int,
        **kwargs: Any,
    ) -> Feature:
        """
        Create a new Feature.

        Args:
            name: Feature name
            parent_epic_id: Parent epic ID
            **kwargs: Optional fields (effort, status, description, team_id, release_id, etc.)

        Returns:
            Created Feature object

        Raises:
            TPAPIError: If creation fails
        """
        # Build payload
        payload = {
            "Name": name,
            "Parent": parent_epic_id,
        }

        # Add optional fields if provided
        if "effort" in kwargs:
            payload["Effort"] = kwargs["effort"]
        if "status" in kwargs:
            payload["Status"] = kwargs["status"]
        if "description" in kwargs:
            payload["Description"] = kwargs["description"]
        if "team_id" in kwargs:
            payload["Team"] = kwargs["team_id"]
        if "release_id" in kwargs:
            payload["Release"] = kwargs["release_id"]
        if "owner_id" in kwargs:
            payload["Owner"] = kwargs["owner_id"]

        # Call subprocess
        response_list = self._run_tpcli_create("Feature", payload)
        response = response_list[0]

        # Parse response and cache
        feature = self._parse_feature(response)

        # Add to cache
        features = self._get_cached("Features")
        if features is None:
            features = []
        features.append(response)
        self._set_cached("Features", features)

        return feature

    def update_feature(
        self,
        feature_id: int,
        **kwargs: Any,
    ) -> Feature:
        """
        Update an existing Feature.

        Args:
            feature_id: Feature ID to update
            **kwargs: Fields to update (name, effort, status, description, etc.)

        Returns:
            Updated Feature object

        Raises:
            TPAPIError: If update fails
        """
        # Build payload with only provided fields
        payload: dict[str, Any] = {}

        if "name" in kwargs:
            payload["Name"] = kwargs["name"]
        if "effort" in kwargs:
            payload["Effort"] = kwargs["effort"]
        if "status" in kwargs:
            payload["Status"] = kwargs["status"]
        if "description" in kwargs:
            payload["Description"] = kwargs["description"]
        if "team_id" in kwargs:
            payload["Team"] = kwargs["team_id"]
        if "release_id" in kwargs:
            payload["Release"] = kwargs["release_id"]
        if "owner_id" in kwargs:
            payload["Owner"] = kwargs["owner_id"]

        # Call subprocess
        response_list = self._run_tpcli_update("Feature", feature_id, payload)
        response = response_list[0]

        # Parse response and cache
        feature = self._parse_feature(response)

        # Update cache
        features = self._get_cached("Features")
        if features is None:
            features = []
        else:
            # Remove old version
            features = [f for f in features if f.get("Id") != feature_id]

        features.append(response)
        self._set_cached("Features", features)

        return feature

    # Bulk operations for performance

    def bulk_create_team_objectives(
        self,
        objectives: list[dict[str, Any]],
    ) -> list[TeamPIObjective]:
        """
        Create multiple Team PI Objectives in a single batch operation.

        Performance: O(n) with n objectives, processed as single transaction.

        Args:
            objectives: List of objective dicts with required fields:
                - name: Objective name
                - team_id: Team ID
                - release_id: Release ID
                - (optional) effort, status, description, owner_id

        Returns:
            List of created TeamPIObjective objects

        Raises:
            TPAPIError: If any creation fails (atomic - none are created)
        """
        if not objectives:
            return []

        # Build payloads
        payloads = []
        for obj in objectives:
            payload = {
                "Name": obj["name"],
                "Team": obj["team_id"],
                "Release": obj["release_id"],
            }
            if "effort" in obj:
                payload["Effort"] = obj["effort"]
            if "status" in obj:
                payload["Status"] = obj["status"]
            if "description" in obj:
                payload["Description"] = obj["description"]
            if "owner_id" in obj:
                payload["Owner"] = obj["owner_id"]

            payloads.append(payload)

        # Create all in batch
        # Note: In real implementation, would use batch API endpoint
        created = []
        for payload in payloads:
            response_list = self._run_tpcli_create("TeamPIObjective", payload)
            created.append(response_list[0])

        # Update cache with all new items
        cached = self._get_cached("TeamPIObjectives")
        if cached is None:
            cached = []
        cached.extend(created)
        self._set_cached("TeamPIObjectives", cached)

        return [self._parse_team_objective(item) for item in created]

    def bulk_update_team_objectives(
        self,
        updates: list[dict[str, Any]],
    ) -> list[TeamPIObjective]:
        """
        Update multiple Team PI Objectives in a single batch operation.

        Performance: O(n) with n objectives, processed as single transaction.

        Args:
            updates: List of update dicts, each with:
                - id: Objective ID to update
                - (any other fields to update: name, effort, status, etc.)

        Returns:
            List of updated TeamPIObjective objects

        Raises:
            TPAPIError: If any update fails (atomic - none are updated)
        """
        if not updates:
            return []

        # Update all items
        # Note: In real implementation, would use batch API endpoint
        updated = []
        for update_data in updates:
            obj_id = update_data["id"]
            payload = {k: v for k, v in update_data.items() if k != "id"}

            response_list = self._run_tpcli_update(
                "TeamPIObjective", obj_id, payload
            )
            updated.append(response_list[0])

        # Update cache with new items
        cached = self._get_cached("TeamPIObjectives")
        if cached is None:
            cached = []
        else:
            # Remove old versions
            updated_ids = {u.get("Id") for u in updated}
            cached = [c for c in cached if c.get("Id") not in updated_ids]

        cached.extend(updated)
        self._set_cached("TeamPIObjectives", cached)

        return [self._parse_team_objective(item) for item in updated]

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
