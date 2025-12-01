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
            side_effect=TPAPIError("Failed to parse tpcli JSON response"),
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


class TestBulkOperations:
    """Tests for bulk create/update operations."""

    @pytest.fixture
    def client(self):
        """Fixture providing a TPAPIClient instance."""
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_objective_response(self):
        """Mock response for a single objective."""
        return {
            "Id": 12345,
            "Name": "Test Objective",
            "Team": {"Id": 1935991, "Name": "Platform Eco"},
            "Release": {"Id": 1942235, "Name": "PI-4/25"},
            "Effort": 34,
            "Status": "Pending",
        }

    def test_bulk_create_team_objectives_success(self, client, mock_objective_response, mocker):
        """Test bulk creating multiple objectives."""
        # Mock responses for 3 objectives
        mock_responses = [
            {**mock_objective_response, "Id": 100, "Name": "Objective 1"},
            {**mock_objective_response, "Id": 101, "Name": "Objective 2"},
            {**mock_objective_response, "Id": 102, "Name": "Objective 3"},
        ]

        # Mock the subprocess call
        call_count = [0]
        def mock_create(entity_type, payload):
            response = mock_responses[call_count[0]]
            call_count[0] += 1
            return [response]

        mocker.patch.object(
            client,
            "_run_tpcli_create",
            side_effect=mock_create,
        )

        # Bulk create
        objectives_to_create = [
            {"name": "Objective 1", "team_id": 1935991, "release_id": 1942235},
            {"name": "Objective 2", "team_id": 1935991, "release_id": 1942235},
            {"name": "Objective 3", "team_id": 1935991, "release_id": 1942235},
        ]

        results = client.bulk_create_team_objectives(objectives_to_create)

        # Verify results
        assert len(results) == 3
        assert all(isinstance(r, TeamPIObjective) for r in results)
        assert results[0].id == 100
        assert results[1].id == 101
        assert results[2].id == 102

    def test_bulk_create_empty_list(self, client):
        """Test bulk create with empty list returns empty."""
        results = client.bulk_create_team_objectives([])
        assert results == []

    def test_bulk_update_team_objectives_success(self, client, mock_objective_response, mocker):
        """Test bulk updating multiple objectives."""
        # Mock responses for 3 updates
        mock_responses = [
            {**mock_objective_response, "Id": 100, "Effort": 40},
            {**mock_objective_response, "Id": 101, "Effort": 50},
            {**mock_objective_response, "Id": 102, "Effort": 60},
        ]

        call_count = [0]
        def mock_update(entity_type, obj_id, payload):
            response = mock_responses[call_count[0]]
            call_count[0] += 1
            return [response]

        mocker.patch.object(
            client,
            "_run_tpcli_update",
            side_effect=mock_update,
        )

        # Bulk update
        updates = [
            {"id": 100, "effort": 40},
            {"id": 101, "effort": 50},
            {"id": 102, "effort": 60},
        ]

        results = client.bulk_update_team_objectives(updates)

        # Verify results
        assert len(results) == 3
        assert all(isinstance(r, TeamPIObjective) for r in results)
        assert results[0].effort == 40
        assert results[1].effort == 50
        assert results[2].effort == 60

    def test_bulk_update_empty_list(self, client):
        """Test bulk update with empty list returns empty."""
        results = client.bulk_update_team_objectives([])
        assert results == []

    def test_bulk_create_updates_cache(self, client, mock_objective_response, mocker):
        """Test bulk create updates the cache."""
        mock_responses = [
            {**mock_objective_response, "Id": 200, "Name": "Obj1"},
            {**mock_objective_response, "Id": 201, "Name": "Obj2"},
        ]

        call_count = [0]
        def mock_create(entity_type, payload):
            response = mock_responses[call_count[0]]
            call_count[0] += 1
            return [response]

        mocker.patch.object(client, "_run_tpcli_create", side_effect=mock_create)

        objectives = [
            {"name": "Obj1", "team_id": 1935991, "release_id": 1942235},
            {"name": "Obj2", "team_id": 1935991, "release_id": 1942235},
        ]

        client.bulk_create_team_objectives(objectives)

        # Verify cache is updated
        cached = client._get_cached("TeamPIObjectives")
        assert cached is not None
        assert len(cached) == 2

    def test_bulk_update_updates_cache(self, client, mock_objective_response, mocker):
        """Test bulk update updates the cache."""
        mock_responses = [
            {**mock_objective_response, "Id": 200, "Effort": 45},
            {**mock_objective_response, "Id": 201, "Effort": 55},
        ]

        call_count = [0]
        def mock_update(entity_type, obj_id, payload):
            response = mock_responses[call_count[0]]
            call_count[0] += 1
            return [response]

        mocker.patch.object(client, "_run_tpcli_update", side_effect=mock_update)

        updates = [
            {"id": 200, "effort": 45},
            {"id": 201, "effort": 55},
        ]

        client.bulk_update_team_objectives(updates)

        # Verify cache is updated
        cached = client._get_cached("TeamPIObjectives")
        assert cached is not None
        assert len(cached) == 2


class TestCachingWithTTL:
    """Tests for TTL-based caching and cache statistics."""

    @pytest.fixture
    def client(self):
        """Fixture providing a TPAPIClient with short TTL for testing."""
        # Short TTL (1 second) for testing expiration
        return TPAPIClient(verbose=False, cache_ttl=1)

    @pytest.fixture
    def mock_response(self):
        """Mock response data."""
        return {
            "Id": 100,
            "Name": "Test",
            "Team": {"Id": 1, "Name": "Test Team"},
        }

    def test_cache_ttl_expiration(self, client, mock_response, mocker):
        """Test cache entries expire after TTL."""
        import time

        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[mock_response],
        )

        # First call should miss cache and call API
        result1 = client.get_teams()
        assert len(result1) > 0

        # Second call should hit cache
        result2 = client.get_teams()
        assert len(result2) > 0

        # Wait for TTL to expire
        time.sleep(1.1)

        # Third call should miss cache (expired) and call API again
        result3 = client.get_teams()
        assert len(result3) > 0

        # Verify API was called twice (first and third calls)
        assert client._run_tpcli.call_count == 2

    def test_cache_statistics(self, client, mock_response, mocker):
        """Test cache statistics tracking."""
        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[mock_response],
        )

        # Make multiple queries
        client.get_teams()  # miss
        client.get_teams()  # hit
        client.get_teams()  # hit

        stats = client.get_cache_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["evictions"] == 0
        assert stats["size"] == 1
        assert stats["hit_rate"] == pytest.approx(66.67, rel=1)

    def test_clear_cache_resets_statistics(self, client, mock_response, mocker):
        """Test clear_cache resets statistics and timestamps."""
        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[mock_response],
        )

        # Generate some cache activity
        client.get_teams()
        client.get_teams()

        stats_before = client.get_cache_stats()
        assert stats_before["hits"] > 0

        # Clear cache
        client.clear_cache()

        stats_after = client.get_cache_stats()
        assert stats_after["hits"] == 0
        assert stats_after["misses"] == 0
        assert stats_after["evictions"] == 0
        assert stats_after["size"] == 0

    def test_cache_hit_rate_calculation(self, client, mock_response, mocker):
        """Test cache hit rate calculation."""
        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[mock_response],
        )

        # 1 miss, 9 hits = 90% hit rate
        for _ in range(10):
            client.get_teams()

        stats = client.get_cache_stats()
        assert stats["hit_rate"] == pytest.approx(90.0, rel=1)


class TestDateParsing:
    """Tests for _parse_tp_date method."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_parse_tp_date_format_with_timezone(self, client):
        """Test parsing TargetProcess date format with timezone."""
        result = client._parse_tp_date("/Date(1738450043000-0500)/")
        assert result is not None
        assert result.year == 2025
        assert result.month == 2  # 1738450043000ms converts to Feb 1, 2025

    def test_parse_tp_date_format_utc(self, client):
        """Test parsing TargetProcess date format with UTC."""
        result = client._parse_tp_date("/Date(1609459200000+0000)/")
        assert result is not None
        assert isinstance(result, type(result))

    def test_parse_iso_format_date(self, client):
        """Test parsing ISO format date."""
        result = client._parse_tp_date("2025-01-01T00:00:00Z")
        assert result is not None
        assert result.year == 2025

    def test_parse_iso_format_with_offset(self, client):
        """Test parsing ISO format with timezone offset."""
        result = client._parse_tp_date("2025-01-01T00:00:00-05:00")
        assert result is not None

    def test_parse_date_none_returns_none(self, client):
        """Test parsing None date string returns None."""
        result = client._parse_tp_date(None)
        assert result is None

    def test_parse_date_empty_string_returns_none(self, client):
        """Test parsing empty string returns None."""
        result = client._parse_tp_date("")
        assert result is None

    def test_parse_date_invalid_format_returns_none(self, client):
        """Test parsing invalid date format returns None."""
        result = client._parse_tp_date("not a date")
        assert result is None


class TestQueryFiltering:
    """Tests for query methods with filtering parameters."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    @pytest.fixture
    def mock_teams(self):
        return [
            {"Id": 1, "Name": "Team A", "AgileReleaseTrain": {"Id": 100, "Name": "ART 1"}},
            {"Id": 2, "Name": "Team B", "AgileReleaseTrain": {"Id": 100, "Name": "ART 1"}},
            {"Id": 3, "Name": "Team C", "AgileReleaseTrain": {"Id": 200, "Name": "ART 2"}},
        ]

    def test_get_teams_without_filter(self, client, mock_teams, mocker):
        """Test get_teams without ART filter."""
        mocker.patch.object(client, "_run_tpcli", return_value=mock_teams)
        teams = client.get_teams()
        assert len(teams) == 3
        assert all(hasattr(t, "id") for t in teams)

    def test_get_teams_with_art_filter(self, client, mock_teams, mocker):
        """Test get_teams with ART ID filter."""
        filtered = [t for t in mock_teams if t["AgileReleaseTrain"]["Id"] == 100]
        mocker.patch.object(client, "_run_tpcli", return_value=filtered)

        teams = client.get_teams(art_id=100)
        assert len(teams) == 2

    def test_get_team_by_name_success(self, client, mock_teams, mocker):
        """Test get_team_by_name finds team."""
        mocker.patch.object(client, "_run_tpcli", return_value=mock_teams)
        team = client.get_team_by_name("Team A")
        assert team is not None
        assert team.name == "Team A"

    def test_get_team_by_name_not_found(self, client, mock_teams, mocker):
        """Test get_team_by_name returns None when not found."""
        mocker.patch.object(client, "_run_tpcli", return_value=mock_teams)
        team = client.get_team_by_name("Nonexistent")
        assert team is None

    def test_get_team_by_name_with_art_filter(self, client, mock_teams, mocker):
        """Test get_team_by_name filters by ART."""
        art1_teams = [t for t in mock_teams if t["AgileReleaseTrain"]["Id"] == 100]
        mocker.patch.object(client, "_run_tpcli", return_value=art1_teams)

        team = client.get_team_by_name("Team A", art_id=100)
        assert team is not None
        assert team.name == "Team A"

    @pytest.fixture
    def mock_releases(self):
        return [
            {"Id": 10, "Name": "PI-4/25", "AgileReleaseTrain": {"Id": 100, "Name": "ART 1"}},
            {"Id": 11, "Name": "PI-5/25", "AgileReleaseTrain": {"Id": 200, "Name": "ART 2"}},
        ]

    def test_get_release_by_name(self, client, mock_releases, mocker):
        """Test get_release_by_name."""
        mocker.patch.object(client, "_run_tpcli", return_value=mock_releases)
        release = client.get_release_by_name("PI-4/25")
        assert release is not None
        assert release.name == "PI-4/25"

    def test_get_program_pi_objectives_no_filter(self, client, mocker):
        """Test get_program_pi_objectives without filters."""
        mock_data = [
            {"Id": 1, "Name": "Strategic Goal 1", "Release": {"Id": 10}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        objs = client.get_program_pi_objectives()
        assert len(objs) == 1

    def test_get_program_pi_objectives_with_art_filter(self, client, mocker):
        """Test get_program_pi_objectives with ART filter."""
        mock_data = [
            {"Id": 1, "Name": "Strategic Goal 1", "Release": {"Id": 10}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        objs = client.get_program_pi_objectives(art_id=100)
        assert len(objs) == 1

    def test_get_program_pi_objectives_with_release_filter(self, client, mocker):
        """Test get_program_pi_objectives with release filter."""
        mock_data = [
            {"Id": 1, "Name": "Strategic Goal 1", "Release": {"Id": 10}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        objs = client.get_program_pi_objectives(release_id=10)
        assert len(objs) == 1

    def test_get_program_pi_objectives_with_both_filters(self, client, mocker):
        """Test get_program_pi_objectives with both ART and release filters."""
        mock_data = [
            {"Id": 1, "Name": "Strategic Goal 1", "Release": {"Id": 10}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        objs = client.get_program_pi_objectives(art_id=100, release_id=10)
        assert len(objs) == 1

    def test_get_team_pi_objectives_with_team_filter(self, client, mocker):
        """Test get_team_pi_objectives with team filter."""
        mock_data = [
            {"Id": 1, "Name": "Objective 1", "Team": {"Id": 1}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        objs = client.get_team_pi_objectives(team_id=1)
        assert len(objs) == 1

    def test_get_team_pi_objectives_with_multiple_filters(self, client, mocker):
        """Test get_team_pi_objectives with team, ART, and release filters."""
        mock_data = [
            {"Id": 1, "Name": "Objective 1", "Team": {"Id": 1}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        objs = client.get_team_pi_objectives(team_id=1, art_id=100, release_id=10)
        assert len(objs) == 1

    def test_get_features_with_team_filter(self, client, mocker):
        """Test get_features with team filter."""
        mock_data = [
            {"Id": 1, "Name": "Feature 1", "Team": {"Id": 1}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        features = client.get_features(team_id=1)
        assert len(features) == 1

    def test_get_features_with_release_filter(self, client, mocker):
        """Test get_features with release filter."""
        mock_data = [
            {"Id": 1, "Name": "Feature 1", "Release": {"Id": 10}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        features = client.get_features(release_id=10)
        assert len(features) == 1

    def test_get_features_with_parent_epic_filter(self, client, mocker):
        """Test get_features with parent epic filter."""
        mock_data = [
            {"Id": 1, "Name": "Feature 1", "Parent": {"Id": 100}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        features = client.get_features(parent_epic_id=100)
        assert len(features) == 1

    def test_get_features_with_multiple_filters(self, client, mocker):
        """Test get_features with multiple filters."""
        mock_data = [
            {"Id": 1, "Name": "Feature 1", "Team": {"Id": 1}, "Release": {"Id": 10}},
        ]
        mocker.patch.object(client, "_run_tpcli", return_value=mock_data)
        features = client.get_features(team_id=1, release_id=10)
        assert len(features) == 1


class TestEntityParsing:
    """Tests for entity parsing methods with edge cases."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_parse_user_complete(self, client):
        """Test parsing complete user data."""
        data = {
            "Id": 123,
            "FirstName": "John",
            "LastName": "Doe",
            "Email": "john@example.com",
        }
        user = client._parse_user(data)
        assert user.id == 123
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john@example.com"

    def test_parse_user_missing_fields(self, client):
        """Test parsing user with missing fields."""
        data = {"Id": 123}
        user = client._parse_user(data)
        assert user.id == 123
        assert user.first_name == ""
        assert user.last_name == ""
        assert user.email == ""

    def test_parse_team_complete(self, client):
        """Test parsing complete team data."""
        data = {
            "Id": 1,
            "Name": "Platform Eco",
            "Owner": {"Id": 123, "FirstName": "John", "LastName": "Doe"},
            "Members": {"length": 5},
            "IsActive": True,
            "AgileReleaseTrain": {"Id": 100, "Name": "ART 1"},
        }
        team = client._parse_team(data)
        assert team.id == 1
        assert team.name == "Platform Eco"
        assert team.owner is not None
        assert team.member_count == 5
        assert team.is_active is True
        assert team.art_id == 100

    def test_parse_team_without_owner(self, client):
        """Test parsing team without owner."""
        data = {
            "Id": 1,
            "Name": "Team",
            "Members": {"length": 3},
        }
        team = client._parse_team(data)
        assert team.owner is None
        assert team.member_count == 3

    def test_parse_team_with_invalid_members(self, client):
        """Test parsing team with invalid members format."""
        data = {
            "Id": 1,
            "Name": "Team",
            "Members": None,
        }
        team = client._parse_team(data)
        assert team.member_count == 0

    def test_parse_art(self, client):
        """Test parsing ART."""
        data = {"Id": 100, "Name": "Data Analytics"}
        art = client._parse_art(data)
        assert art.id == 100
        assert art.name == "Data Analytics"

    def test_parse_release_complete(self, client):
        """Test parsing complete release."""
        data = {
            "Id": 10,
            "Name": "PI-4/25",
            "StartDate": "/Date(1609459200000-0500)/",
            "EndDate": "/Date(1609545600000-0500)/",
            "AgileReleaseTrain": {"Id": 100, "Name": "ART 1"},
            "IsCurrent": True,
        }
        release = client._parse_release(data)
        assert release.id == 10
        assert release.name == "PI-4/25"
        assert release.is_current is True

    def test_parse_release_missing_dates(self, client):
        """Test parsing release with missing dates."""
        data = {
            "Id": 10,
            "Name": "PI-4/25",
        }
        release = client._parse_release(data)
        assert release.id == 10
        assert release.start_date is not None  # Should default to now()
        assert release.end_date is not None

    def test_parse_program_objective_complete(self, client):
        """Test parsing complete program objective."""
        data = {
            "Id": 1,
            "Name": "Strategic Initiative",
            "Status": "In Progress",
            "Owner": {"Id": 123, "FirstName": "Jane"},
            "Description": "Initiative description",
            "StartDate": "/Date(1609459200000-0500)/",
            "EndDate": "/Date(1609545600000-0500)/",
            "Release": {"Id": 10, "Name": "PI-4/25"},
            "Effort": 100,
            "CreatedDate": "/Date(1609459200000-0500)/",
            "AgileReleaseTrain": {"Id": 100, "Name": "ART 1"},
        }
        obj = client._parse_program_objective(data)
        assert obj.id == 1
        assert obj.name == "Strategic Initiative"
        assert obj.owner is not None
        assert obj.effort == 100

    def test_parse_program_objective_without_optional_fields(self, client):
        """Test parsing program objective with minimal fields."""
        data = {
            "Id": 1,
            "Name": "Initiative",
        }
        obj = client._parse_program_objective(data)
        assert obj.id == 1
        assert obj.status == "Pending"
        assert obj.effort == 0

    def test_parse_team_objective_complete(self, client):
        """Test parsing complete team objective."""
        data = {
            "Id": 2019099,
            "Name": "Platform governance",
            "Status": "In Progress",
            "Owner": {"Id": 123, "FirstName": "John"},
            "Description": "Governance frameworks",
            "StartDate": "/Date(1609459200000-0500)/",
            "EndDate": "/Date(1609545600000-0500)/",
            "Release": {"Id": 10, "Name": "PI-4/25"},
            "Effort": 21,
            "CreatedDate": "/Date(1609459200000-0500)/",
            "Team": {"Id": 1935991, "Name": "Platform Eco"},
            "Committed": True,
        }
        obj = client._parse_team_objective(data)
        assert obj.id == 2019099
        assert obj.team_id == 1935991
        assert obj.committed is True

    def test_parse_feature_complete(self, client):
        """Test parsing complete feature."""
        data = {
            "Id": 1001,
            "Name": "Authentication",
            "Status": "In Progress",
            "Effort": 13,
            "Owner": {"Id": 123, "FirstName": "John"},
            "Team": {"Id": 1, "Name": "Team A"},
            "Release": {"Id": 10, "Name": "PI-4/25"},
            "Parent": {"Id": 100, "Name": "Security Epic"},
            "Description": "Auth feature",
            "CreatedDate": "/Date(1609459200000-0500)/",
        }
        feature = client._parse_feature(data)
        assert feature.id == 1001
        assert feature.team is not None
        assert feature.parent_epic_id == 100

    def test_parse_feature_without_owner(self, client):
        """Test parsing feature without owner."""
        data = {
            "Id": 1001,
            "Name": "Feature",
            "Parent": {"Id": 100},
        }
        feature = client._parse_feature(data)
        assert feature.owner is None
        assert feature.parent_epic_id == 100


class TestSubprocessExecutionEdgeCases:
    """Tests for subprocess execution edge cases."""

    @pytest.fixture
    def client(self):
        return TPAPIClient(verbose=False)

    def test_run_tpcli_with_array_response(self, client, mocker):
        """Test _run_tpcli with array response."""
        mock_output = '[{"Id": 1}, {"Id": 2}]'
        mocker.patch(
            "subprocess.run",
            return_value=MagicMock(
                stdout=mock_output,
                stderr="",
                returncode=0,
            ),
        )
        result = client._run_tpcli("Teams")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_run_tpcli_with_single_object_response(self, client, mocker):
        """Test _run_tpcli with single object response."""
        mock_output = '{"Id": 1, "Name": "Test"}'
        mocker.patch(
            "subprocess.run",
            return_value=MagicMock(
                stdout=mock_output,
                stderr="",
                returncode=0,
            ),
        )
        result = client._run_tpcli("Teams")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_run_tpcli_with_metadata_before_json(self, client, mocker):
        """Test _run_tpcli handles metadata before JSON."""
        mock_output = "Fetching data...\n[{\"Id\": 1}]"
        mocker.patch(
            "subprocess.run",
            return_value=MagicMock(
                stdout=mock_output,
                stderr="",
                returncode=0,
            ),
        )
        result = client._run_tpcli("Teams")
        assert len(result) == 1

    def test_run_tpcli_timeout_raises_error(self, client, mocker):
        """Test _run_tpcli handles subprocess timeout."""
        mocker.patch(
            "subprocess.run",
            side_effect=__import__("subprocess").TimeoutExpired("cmd", 30),
        )
        with pytest.raises(TPAPIError, match="timed out"):
            client._run_tpcli("Teams")

    def test_run_tpcli_command_error_raises_error(self, client, mocker):
        """Test _run_tpcli handles command failure."""
        mocker.patch(
            "subprocess.run",
            side_effect=__import__("subprocess").CalledProcessError(1, "cmd"),
        )
        with pytest.raises(TPAPIError, match="tpcli command failed"):
            client._run_tpcli("Teams")

    def test_run_tpcli_no_json_raises_error(self, client, mocker):
        """Test _run_tpcli raises error when no JSON found."""
        mock_output = "No data available"
        mocker.patch(
            "subprocess.run",
            return_value=MagicMock(
                stdout=mock_output,
                stderr="",
                returncode=0,
            ),
        )
        with pytest.raises(TPAPIError, match="No JSON found"):
            client._run_tpcli("Teams")
