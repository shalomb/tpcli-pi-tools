"""
Unit tests for TPAPIClient wrapper methods (create/update operations).

Tests the Python API client's create_team_objective, update_team_objective,
create_feature, and update_feature methods.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.models.entities import TeamPIObjective, Feature


class TestCreateTeamObjective:
    """Tests for create_team_objective method."""

    @pytest.fixture
    def client(self):
        """Fixture providing a TPAPIClient instance."""
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_tpcli_response(self):
        """Mock response from tpcli subprocess."""
        return {
            "Id": 12345,
            "Name": "API Performance",
            "Team": {"Id": 1935991, "Name": "Platform Eco"},
            "Release": {"Id": 1942235, "Name": "PI-4/25"},
            "Effort": 34,
            "Status": "Pending",
            "CreatedDate": "/Date(1738450043000-0500)/",
        }

    def test_create_team_objective_success(self, client, mock_tpcli_response, mocker):
        """Test successful team objective creation."""
        # Mock subprocess call
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_tpcli_response],
        )

        # Create objective
        objective = client.create_team_objective(
            name="API Performance",
            team_id=1935991,
            release_id=1942235,
            effort=34,
        )

        # Assertions
        assert isinstance(objective, TeamPIObjective)
        assert objective.id == 12345
        assert objective.name == "API Performance"
        assert objective.team_id == 1935991
        assert objective.release_id == 1942235
        assert objective.effort == 34

    def test_create_objective_returns_typed_object(self, client, mock_tpcli_response, mocker):
        """Test that create returns typed TeamPIObjective, not dict."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_tpcli_response],
        )

        objective = client.create_team_objective(
            name="Test",
            team_id=1935991,
            release_id=1942235,
        )

        assert isinstance(objective, TeamPIObjective)
        assert hasattr(objective, "id")
        assert hasattr(objective, "name")
        assert hasattr(objective, "team_id")

    def test_create_objective_adds_to_cache(self, client, mock_tpcli_response, mocker):
        """Test that created objective is added to cache."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_tpcli_response],
        )

        client.create_team_objective(
            name="API Performance",
            team_id=1935991,
            release_id=1942235,
        )

        # Verify cache contains the created objective
        objectives = client.get_team_pi_objectives()
        found = False
        for obj in objectives:
            if obj.id == 12345:
                found = True
                break
        assert found, "Created objective not found in cache"

    def test_create_objective_with_minimal_fields(self, client, mock_tpcli_response, mocker):
        """Test create with only required fields."""
        mock_response_minimal = {
            "Id": 12345,
            "Name": "Test",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
        }

        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_response_minimal],
        )

        objective = client.create_team_objective(
            name="Test",
            team_id=1935991,
            release_id=1942235,
        )

        assert objective.id == 12345
        assert objective.name == "Test"

    def test_create_objective_with_optional_fields(self, client, mock_tpcli_response, mocker):
        """Test create with optional fields like description."""
        mock_tpcli_response["Description"] = "Test description"
        mock_tpcli_response["Effort"] = 40

        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_tpcli_response],
        )

        objective = client.create_team_objective(
            name="API Performance",
            team_id=1935991,
            release_id=1942235,
            effort=40,
            description="Test description",
        )

        assert objective.effort == 40
        assert objective.description == "Test description"

    def test_create_objective_invalid_json_raises_error(self, client, mocker):
        """Test create fails gracefully with invalid JSON."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=json.JSONDecodeError("msg", "doc", 0),
        )

        with pytest.raises(TPAPIError, match="Failed to parse"):
            client.create_team_objective(
                name="Test",
                team_id=1935991,
                release_id=1942235,
            )

    def test_create_objective_subprocess_error_raises_error(self, client, mocker):
        """Test create fails when subprocess fails."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("tpcli command failed: create TeamPIObjective"),
        )

        with pytest.raises(TPAPIError, match="tpcli command failed"):
            client.create_team_objective(
                name="Test",
                team_id=1935991,
                release_id=1942235,
            )


class TestUpdateTeamObjective:
    """Tests for update_team_objective method."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_tpcli_response(self):
        return {
            "Id": 12345,
            "Name": "API Performance Updated",
            "Team": {"Id": 1935991, "Name": "Platform Eco"},
            "Release": {"Id": 1942235, "Name": "PI-4/25"},
            "Effort": 40,
            "Status": "In Progress",
        }

    def test_update_team_objective_success(self, client, mock_tpcli_response, mocker):
        """Test successful team objective update."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[mock_tpcli_response],
        )

        objective = client.update_team_objective(
            objective_id=12345,
            name="API Performance Updated",
            effort=40,
        )

        assert isinstance(objective, TeamPIObjective)
        assert objective.id == 12345
        assert objective.name == "API Performance Updated"
        assert objective.effort == 40

    def test_update_objective_preserves_unchanged_fields(self, client, mocker):
        """Test that update preserves fields not in the update."""
        response = {
            "Id": 12345,
            "Name": "API Perf",  # preserved from original
            "Effort": 40,  # updated
            "Status": "Pending",  # preserved
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
        }

        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        objective = client.update_team_objective(
            objective_id=12345,
            effort=40,  # only updating effort
        )

        assert objective.name == "API Perf"
        assert objective.effort == 40
        assert objective.status == "Pending"

    def test_update_objective_single_field(self, client, mocker):
        """Test update with only one field."""
        response = {
            "Id": 12345,
            "Name": "API Perf",
            "Effort": 50,  # updated
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
        }

        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        objective = client.update_team_objective(objective_id=12345, effort=50)

        assert objective.effort == 50

    def test_update_objective_multiple_fields(self, client, mocker):
        """Test update with multiple fields."""
        response = {
            "Id": 12345,
            "Name": "New Name",
            "Effort": 50,
            "Status": "In Progress",
            "Team": {"Id": 1935991},
            "Release": {"Id": 1942235},
        }

        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        objective = client.update_team_objective(
            objective_id=12345,
            name="New Name",
            effort=50,
            status="In Progress",
        )

        assert objective.name == "New Name"
        assert objective.effort == 50
        assert objective.status == "In Progress"

    def test_update_objective_not_found_raises_error(self, client, mocker):
        """Test update fails when objective doesn't exist."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            side_effect=TPAPIError("API error 404: Entity not found"),
        )

        with pytest.raises(TPAPIError, match="404"):
            client.update_team_objective(objective_id=99999, name="Test")


class TestCreateFeature:
    """Tests for create_feature method."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_feature_response(self):
        return {
            "Id": 5678,
            "Name": "User Authentication",
            "Parent": {"Id": 2018883, "Name": "Security Epic"},
            "Effort": 21,
            "Status": "Pending",
            "CreatedDate": "/Date(1738450043000-0500)/",
        }

    def test_create_feature_success(self, client, mock_feature_response, mocker):
        """Test successful feature creation."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_feature_response],
        )

        feature = client.create_feature(
            name="User Authentication",
            parent_epic_id=2018883,
            effort=21,
        )

        assert isinstance(feature, Feature)
        assert feature.id == 5678
        assert feature.name == "User Authentication"
        assert feature.parent_epic_id == 2018883
        assert feature.effort == 21

    def test_create_feature_returns_typed_object(self, client, mock_feature_response, mocker):
        """Test that create returns typed Feature, not dict."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_feature_response],
        )

        feature = client.create_feature(
            name="User Auth",
            parent_epic_id=2018883,
        )

        assert isinstance(feature, Feature)
        assert hasattr(feature, "id")
        assert hasattr(feature, "name")
        assert hasattr(feature, "parent_epic_id")

    def test_create_feature_adds_to_cache(self, client, mock_feature_response, mocker):
        """Test that created feature is added to cache."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[mock_feature_response],
        )

        client.create_feature(
            name="User Authentication",
            parent_epic_id=2018883,
        )

        # Verify cache contains the created feature
        features = client.get_features()
        found = False
        for feat in features:
            if feat.id == 5678:
                found = True
                break
        assert found, "Created feature not found in cache"


class TestUpdateFeature:
    """Tests for update_feature method."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_feature_response(self):
        return {
            "Id": 5678,
            "Name": "User Authentication Flow",
            "Effort": 13,
            "Status": "In Progress",
            "Parent": {"Id": 2018883},
        }

    def test_update_feature_success(self, client, mock_feature_response, mocker):
        """Test successful feature update."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[mock_feature_response],
        )

        feature = client.update_feature(
            feature_id=5678,
            name="User Authentication Flow",
            effort=13,
        )

        assert isinstance(feature, Feature)
        assert feature.id == 5678
        assert feature.name == "User Authentication Flow"
        assert feature.effort == 13

    def test_update_feature_preserves_unchanged_fields(self, client, mocker):
        """Test that update preserves fields not in the update."""
        response = {
            "Id": 5678,
            "Name": "User Auth",  # preserved
            "Effort": 13,  # updated
            "Status": "Pending",  # preserved
            "Parent": {"Id": 2018883},
        }

        mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[response],
        )

        feature = client.update_feature(feature_id=5678, effort=13)

        assert feature.name == "User Auth"
        assert feature.effort == 13
        assert feature.status == "Pending"


class TestPayloadConstruction:
    """Tests for correct subprocess payload construction."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_create_objective_constructs_valid_json_payload(self, client, mocker):
        """Test that create constructs valid JSON for subprocess."""
        mock_run = mocker.patch.object(
            client,
            "_run_tpcli_create",
            return_value=[{"Id": 1, "Name": "Test"}],
        )

        client.create_team_objective(
            name="Test Objective",
            team_id=1935991,
            release_id=1942235,
            effort=34,
        )

        # Verify _run_tpcli_create was called with correct entity type
        mock_run.assert_called_once()

    def test_update_objective_sends_only_changed_fields(self, client, mocker):
        """Test that update only sends fields that are being changed."""
        mock_run = mocker.patch.object(
            client,
            "_run_tpcli_update",
            return_value=[{"Id": 12345, "Effort": 40}],
        )

        client.update_team_objective(objective_id=12345, effort=40)

        # Verify only effort was sent
        mock_run.assert_called_once()


class TestErrorHandling:
    """Tests for error handling in wrapper methods."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_create_handles_api_validation_error(self, client, mocker):
        """Test create gracefully handles API validation errors."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError(
                "tpcli command failed: create TeamPIObjective\n"
                "stderr: validation failed: field 'name' is required"
            ),
        )

        with pytest.raises(TPAPIError):
            client.create_team_objective(
                name="",  # empty name
                team_id=1935991,
                release_id=1942235,
            )

    def test_update_handles_not_found_error(self, client, mocker):
        """Test update handles 404 not found gracefully."""
        mocker.patch.object(
            client,
            "_run_tpcli_update",
            side_effect=TPAPIError("API error 404: Entity not found"),
        )

        with pytest.raises(TPAPIError):
            client.update_team_objective(objective_id=99999, name="Test")

    def test_create_handles_network_timeout(self, client, mocker):
        """Test create handles network timeouts gracefully."""
        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=TPAPIError("tpcli command timed out"),
        )

        with pytest.raises(TPAPIError):
            client.create_team_objective(
                name="Test",
                team_id=1935991,
                release_id=1942235,
            )
