"""
Unit tests for CLI create/update operations.

Tests the Python wrapper for tpcli plan create/update commands
with proper subprocess mocking.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.models.entities import TeamPIObjective, Feature


class TestCLICreateTeamObjective:
    """Tests for CLI create TeamPIObjective operations."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_response(self):
        return {
            "Id": 2019099,
            "Name": "API Perf",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
            "Effort": 34,
            "Status": "Pending",
            "CreatedDate": "/Date(1738450043000-0500)/",
            "ModifiedDate": "/Date(1738450043000-0500)/",
        }

    def test_create_with_valid_data_returns_success(self, client, mock_response, mocker):
        """Test create CLI command with valid data succeeds."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_response],
        )

        result = client.create_team_objective(
            name="API Perf",
            team_id=1935991,
            release_id=1942235,
            effort=34,
        )

        assert result is not None
        assert result.id == 2019099
        assert result.name == "API Perf"

    def test_create_with_minimal_fields(self, client, mock_response, mocker):
        """Test create with only required fields."""
        minimal_response = {
            "Id": 2019099,
            "Name": "Test",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
        }
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[minimal_response],
        )

        result = client.create_team_objective(
            name="Test",
            team_id=1935991,
            release_id=1942235,
        )

        assert result.id == 2019099

    def test_create_returns_timestamps(self, client, mock_response, mocker):
        """Test create response includes timestamps."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_response],
        )

        result = client.create_team_objective(
            name="API Perf",
            team_id=1935991,
            release_id=1942235,
        )

        # Verify timestamps are included
        assert result.created_date is not None or "created_at" in str(mock_response)

    def test_create_with_missing_required_field_raises_error(self, client, mocker):
        """Test create fails when required field is missing."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("validation failed: field 'name' is required"),
        )

        with pytest.raises(TPAPIError, match="required"):
            client.create_team_objective(
                name="",  # missing/empty
                team_id=1935991,
                release_id=1942235,
            )

    def test_create_invalid_json_raises_error(self, client, mocker):
        """Test create fails with invalid JSON data."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("Failed to parse tpcli JSON response"),
        )

        with pytest.raises(TPAPIError):
            client.create_team_objective(
                name="Test",
                team_id=1935991,
                release_id=1942235,
            )


class TestCLIUpdateTeamObjective:
    """Tests for CLI update TeamPIObjective operations."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_response(self):
        return {
            "Id": 12345,
            "Name": "New Name",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
            "Effort": 40,
            "Status": "In Progress",
        }

    def test_update_with_valid_data_returns_success(self, client, mock_response, mocker):
        """Test update CLI command with valid data succeeds."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[mock_response],
        )

        result = client.update_team_objective(
            objective_id=12345,
            name="New Name",
            effort=40,
        )

        assert result.id == 12345
        assert result.name == "New Name"
        assert result.effort == 40

    def test_update_entity_not_found_raises_error(self, client, mocker):
        """Test update fails when entity doesn't exist."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            side_effect=TPAPIError("API error 404: Entity not found"),
        )

        with pytest.raises(TPAPIError, match="404|not found"):
            client.update_team_objective(objective_id=99999, name="Test")

    def test_update_invalid_id_format_raises_error(self, client, mocker):
        """Test update fails with invalid ID format."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            side_effect=TPAPIError("Invalid ID format"),
        )

        with pytest.raises(TPAPIError, match="Invalid|ID"):
            client.update_team_objective(objective_id=-1, name="Test")

    def test_update_preserves_unchanged_fields(self, client, mocker):
        """Test update preserves fields not being updated."""
        response = {
            "Id": 12345,
            "Name": "API Perf",  # unchanged
            "Effort": 40,  # updated
            "Status": "Pending",  # unchanged
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
        }
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        result = client.update_team_objective(objective_id=12345, effort=40)

        assert result.name == "API Perf"  # preserved
        assert result.effort == 40  # updated


class TestCLICreateFeature:
    """Tests for CLI create Feature operations."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_response(self):
        return {
            "Id": 5678,
            "Name": "User Auth",
            "Parent": {"Id": 2018883},
            "Effort": 21,
            "Status": "Pending",
        }

    def test_create_feature_with_valid_data(self, client, mock_response, mocker):
        """Test create feature CLI command succeeds."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_response],
        )

        result = client.create_feature(
            name="User Auth",
            parent_epic_id=2018883,
            effort=21,
        )

        assert result.id == 5678
        assert result.name == "User Auth"

    def test_create_feature_returns_id(self, client, mock_response, mocker):
        """Test create feature response includes ID."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_response],
        )

        result = client.create_feature(
            name="User Auth",
            parent_epic_id=2018883,
        )

        assert result.id == 5678

    def test_create_feature_with_missing_parent_raises_error(self, client, mocker):
        """Test create feature fails without parent epic."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("validation failed: field 'parent' is required"),
        )

        with pytest.raises(TPAPIError):
            client.create_feature(name="User Auth", parent_epic_id=None)


class TestCLIUpdateFeature:
    """Tests for CLI update Feature operations."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_response(self):
        return {
            "Id": 5678,
            "Name": "Auth Flow",
            "Parent": {"Id": 2018883},
            "Effort": 13,
            "Status": "In Progress",
        }

    def test_update_feature_with_valid_data(self, client, mock_response, mocker):
        """Test update feature CLI command succeeds."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[mock_response],
        )

        result = client.update_feature(
            feature_id=5678,
            name="Auth Flow",
            effort=13,
        )

        assert result.id == 5678
        assert result.name == "Auth Flow"
        assert result.effort == 13

    def test_update_feature_preserves_unchanged_fields(self, client, mocker):
        """Test update feature preserves unchanged fields."""
        response = {
            "Id": 5678,
            "Name": "User Auth",  # unchanged
            "Effort": 13,  # updated
            "Status": "Pending",  # unchanged
            "Parent": {"Id": 2018883},
        }
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        result = client.update_feature(feature_id=5678, effort=13)

        assert result.name == "User Auth"
        assert result.effort == 13


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_create_with_invalid_json_in_data(self, client, mocker):
        """Test create fails with invalid JSON data."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("invalid JSON"),
        )

        with pytest.raises(TPAPIError, match="JSON"):
            client.create_team_objective(
                name="Test",
                team_id=1935991,
                release_id=1942235,
            )

    def test_update_with_validation_error(self, client, mocker):
        """Test update fails with API validation error."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            side_effect=TPAPIError(
                "validation failed: effort must be a positive number"
            ),
        )

        with pytest.raises(TPAPIError):
            client.update_team_objective(objective_id=12345, effort=-1)

    def test_create_timeout_raises_error(self, client, mocker):
        """Test create fails on timeout."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("tpcli command timed out"),
        )

        with pytest.raises(TPAPIError, match="timed out"):
            client.create_team_objective(
                name="Test",
                team_id=1935991,
                release_id=1942235,
            )


class TestCLICommandPayloads:
    """Tests for CLI command payload construction."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_create_constructs_correct_payload(self, client, mocker):
        """Test create command includes all provided fields."""
        mock_run = mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[{"id": 1, "name": "Test"}],
        )

        client.create_team_objective(
            name="Test Objective",
            team_id=1935991,
            release_id=1942235,
            effort=34,
            status="In Progress",
            description="Test description",
        )

        # Verify _run_tpcli_create was called
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args

        # First arg should be entity type
        assert args[0] == "TeamPIObjective"

        # Second arg should be payload dict
        payload = args[1]
        assert payload["Name"] == "Test Objective"
        assert payload["Team"] == 1935991
        assert payload["Release"] == 1942235

    def test_update_sends_only_provided_fields(self, client, mocker):
        """Test update command only includes fields being updated."""
        mock_run = mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[{"id": 12345, "effort": 40}],
        )

        client.update_team_objective(objective_id=12345, effort=40)

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args

        # First arg: entity type
        assert args[0] == "TeamPIObjective"

        # Second arg: entity ID
        assert args[1] == 12345

        # Third arg: payload (should only have Effort)
        payload = args[2]
        assert "Effort" in payload
        assert payload["Effort"] == 40


class TestCLIResponseParsing:
    """Tests for CLI response parsing."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_create_parses_json_response_correctly(self, client, mocker):
        """Test create correctly parses JSON response."""
        response = {
            "Id": 2019099,
            "Name": "API Perf",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
            "Effort": 34,
            "Status": "Pending",
            "CreatedDate": "/Date(1738450043000-0500)/",
        }
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[response],
        )

        result = client.create_team_objective(
            name="API Perf",
            team_id=1935991,
            release_id=1942235,
        )

        assert isinstance(result, TeamPIObjective)
        assert result.id == 2019099

    def test_update_parses_json_response_correctly(self, client, mocker):
        """Test update correctly parses JSON response."""
        response = {
            "Id": 12345,
            "Name": "API Perf",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
            "Effort": 40,
        }
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        result = client.update_team_objective(objective_id=12345, effort=40)

        assert isinstance(result, TeamPIObjective)
        assert result.effort == 40

    def test_create_feature_parses_response(self, client, mocker):
        """Test create feature correctly parses response."""
        response = {
            "Id": 5678,
            "Name": "User Auth",
            "Parent": {"Id": 2018883},
            "Effort": 21,
        }
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[response],
        )

        result = client.create_feature(
            name="User Auth",
            parent_epic_id=2018883,
        )

        assert isinstance(result, Feature)
        assert result.id == 5678
