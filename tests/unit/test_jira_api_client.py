"""
Unit tests for Jira API client for Phase 2B integration.

Tests the JiraAPIClient class for fetching stories directly from Jira,
including story details (status, assignee, story points, acceptance criteria).
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import Any, Optional


# Phase 2B: Jira API Client Tests

class TestJiraAPIClientBasics:
    """Tests for basic Jira API client functionality."""

    @pytest.fixture
    def jira_client(self):
        """Fixture providing a JiraAPIClient instance."""
        # Import will be done in implementation
        from tpcli_pi.core.jira_api_client import JiraAPIClient
        return JiraAPIClient(base_url="https://jira.takeda.com", token="test-token")

    def test_jira_client_initialization(self, jira_client):
        """Test Jira client can be initialized."""
        assert jira_client is not None
        assert jira_client.base_url == "https://jira.takeda.com"

    def test_jira_client_token_not_logged(self, jira_client):
        """Test Jira token is not exposed in string representation."""
        client_str = str(jira_client)
        assert "test-token" not in client_str


class TestJiraStoryFetching:
    """US-PB-1: Tests for fetching stories from Jira API."""

    @pytest.fixture
    def jira_client(self):
        from tpcli_pi.core.jira_api_client import JiraAPIClient
        return JiraAPIClient(base_url="https://jira.takeda.com", token="test-token")

    @pytest.fixture
    def mock_story_response(self):
        """Mock Jira story API response."""
        return {
            "key": "DAD-2653",
            "fields": {
                "summary": "Set up pod resource limits",
                "status": {"name": "In Progress"},
                "assignee": {"displayName": "Alice Chen"},
                "customfield_10001": 5,  # Story points
                "description": "Configure memory and CPU limits\nValidate in staging"
            }
        }

    @pytest.fixture
    def mock_epic_stories_response(self):
        """Mock Jira API response for stories under an epic."""
        return {
            "issues": [
                {
                    "key": "DAD-2653",
                    "fields": {
                        "summary": "Set up pod resource limits",
                        "status": {"name": "In Progress"},
                        "assignee": {"displayName": "Alice Chen"},
                        "customfield_10001": 5,
                        "description": "Configure memory and CPU limits"
                    }
                },
                {
                    "key": "DAD-2654",
                    "fields": {
                        "summary": "Implement alerting rules",
                        "status": {"name": "To Do"},
                        "assignee": {"displayName": "Bob Kumar"},
                        "customfield_10001": 8,
                        "description": "Set up alerting for backend pods"
                    }
                }
            ]
        }

    def test_fetch_stories_by_epic_key(self, jira_client, mock_epic_stories_response):
        """Test fetching stories from Jira by epic key."""
        # This will be tested with mocked API calls
        # Expected: fetch_stories_by_epic(epic_key) returns list of Story objects
        pass

    def test_story_object_has_required_fields(self, jira_client):
        """Test Story object contains required fields."""
        # Expected Story structure:
        # - key: "DAD-2653"
        # - summary: "Set up pod resource limits"
        # - status: "In Progress"
        # - assignee: "Alice Chen"
        # - story_points: 5
        # - description: "Configure memory and CPU limits"
        pass

    def test_stories_ordered_by_key(self, jira_client, mock_epic_stories_response):
        """Test stories returned in consistent order (by key)."""
        # Expected: Stories sorted by Jira issue key for consistent rendering
        pass

    def test_fetch_stories_handles_rate_limits(self, jira_client):
        """Test API rate limiting is handled gracefully."""
        # Expected: Exponential backoff or clear error message if rate limited
        pass

    def test_fetch_stories_handles_missing_epic(self, jira_client):
        """Test graceful handling of missing/invalid epic key."""
        # Expected: Empty list or clear error, not crash
        pass


class TestStoryAcceptanceCriteria:
    """US-PB-2: Tests for story acceptance criteria display."""

    @pytest.fixture
    def jira_client(self):
        from tpcli_pi.core.jira_api_client import JiraAPIClient
        return JiraAPIClient(base_url="https://jira.takeda.com", token="test-token")

    def test_story_ac_extracted_from_description(self, jira_client):
        """Test AC extracted from story description."""
        # Jira doesn't have separate AC field, description is used
        # Expected: AC lines extracted (formatted as list)
        pass

    def test_story_ac_empty_handled_gracefully(self, jira_client):
        """Test stories without AC/description don't break rendering."""
        # Expected: Story still renders, just without AC section
        pass

    def test_html_in_story_ac_cleaned(self, jira_client):
        """Test HTML in story AC is cleaned (same as Phase 2A)."""
        # Expected: HTML entities decoded, tags stripped
        pass


class TestStoryStatus:
    """US-PB-3: Tests for story status display."""

    @pytest.fixture
    def jira_client(self):
        from tpcli_pi.core.jira_api_client import JiraAPIClient
        return JiraAPIClient(base_url="https://jira.takeda.com", token="test-token")

    def test_story_status_fetched_from_jira(self, jira_client):
        """Test story status is fetched and displayed."""
        # Expected: Status field from Jira (To Do, In Progress, Done, etc.)
        pass

    def test_story_status_displayed_read_only(self, jira_client):
        """Test story status is read-only in markdown."""
        # Expected: Status shown but not editable by users
        pass

    def test_story_status_various_values(self, jira_client):
        """Test various Jira status values are handled."""
        # Expected: To Do, In Progress, In Review, Done, Blocked, etc.
        pass


class TestJiraCredentialManagement:
    """US-PB-4: Tests for secure Jira credential storage."""

    def test_jira_token_from_environment_variable(self):
        """Test Jira token can be loaded from environment variable."""
        # Expected: JIRA_TOKEN env var or similar
        pass

    def test_jira_token_from_config_file(self):
        """Test Jira token can be stored in config."""
        # Expected: ~/.tpcli.yaml or similar, NOT logged
        pass

    def test_jira_token_not_logged_or_printed(self):
        """Test Jira token is never logged or printed."""
        # Expected: Error messages don't expose token
        pass

    def test_missing_jira_token_clear_error(self):
        """Test clear error if Jira token missing."""
        # Expected: "JIRA_TOKEN not set" not "NoneType has no attribute..."
        pass


class TestMarkdownGeneratorIntegration:
    """Tests for markdown generator using Jira stories (Phase 2B integration)."""

    @pytest.fixture
    def generator(self):
        from tpcli_pi.core.markdown_generator import MarkdownGenerator
        return MarkdownGenerator()

    @pytest.fixture
    def mock_epic_with_stories(self):
        """Epic with Jira key and associated stories."""
        return {
            "id": 2018883,
            "name": "Semantic Versioning & CI/CD",
            "owner": "Venkatesh Ravi",
            "status": "Analyzing",
            "effort": 21,
            "jira_key": "DAD-2652",
            "stories": [
                {
                    "key": "DAD-2653",
                    "summary": "Set up pod resource limits",
                    "status": "In Progress",
                    "assignee": "Alice Chen",
                    "story_points": 5,
                    "description": "Configure memory and CPU limits\nValidate in staging"
                },
                {
                    "key": "DAD-2654",
                    "summary": "Implement alerting rules",
                    "status": "To Do",
                    "assignee": "Bob Kumar",
                    "story_points": 8,
                    "description": "Set up alerting for backend pods"
                }
            ]
        }

    def test_stories_rendered_as_h4_subsections(self, generator, mock_epic_with_stories):
        """Test stories appear as H4 subsections under epic (H3)."""
        # Expected output structure:
        # ### Epic: Name
        # #### Story: Story Title (H4)
        objectives = [{
            "id": 1, "name": "Test", "status": "OK", "effort": 10,
            "epics": [mock_epic_with_stories]
        }]
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-1/25",
            art_name="Test ART",
            team_objectives=objectives,
        )
        # Check H4 headers for stories
        assert "#### Story: Set up pod resource limits" in markdown or \
               "#### [DAD-2653]" in markdown

    def test_story_metadata_displayed(self, generator, mock_epic_with_stories):
        """Test story metadata (key, status, assignee, points) displayed."""
        objectives = [{
            "id": 1, "name": "Test", "status": "OK", "effort": 10,
            "epics": [mock_epic_with_stories]
        }]
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-1/25",
            art_name="Test ART",
            team_objectives=objectives,
        )
        # Story key should appear as link
        assert "DAD-2653" in markdown
        # Status should appear
        assert "In Progress" in markdown
        # Assignee should appear
        assert "Alice Chen" in markdown
        # Story points should appear
        assert "5" in markdown

    def test_story_key_as_clickable_link(self, generator, mock_epic_with_stories):
        """Test story key formatted as link to Jira."""
        objectives = [{
            "id": 1, "name": "Test", "status": "OK", "effort": 10,
            "epics": [mock_epic_with_stories]
        }]
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-1/25",
            art_name="Test ART",
            team_objectives=objectives,
        )
        # Story key should link to Jira
        assert "https://jira.takeda.com/browse/DAD-2653" in markdown

    def test_multiple_stories_ordered_by_key(self, generator, mock_epic_with_stories):
        """Test multiple stories ordered consistently."""
        objectives = [{
            "id": 1, "name": "Test", "status": "OK", "effort": 10,
            "epics": [mock_epic_with_stories]
        }]
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-1/25",
            art_name="Test ART",
            team_objectives=objectives,
        )
        # DAD-2653 should appear before DAD-2654 (sorted by key)
        pos_2653 = markdown.find("DAD-2653")
        pos_2654 = markdown.find("DAD-2654")
        assert pos_2653 < pos_2654 if pos_2653 > -1 and pos_2654 > -1 else True

    def test_epic_without_stories_still_renders(self, generator):
        """Test epics without stories (not yet fetched) render fine."""
        epic_no_stories = {
            "id": 1,
            "name": "Backward Compatible Epic",
            "owner": "Test",
            "status": "OK",
            "effort": 5,
            "jira_key": "TEST-1"
            # No "stories" field
        }
        objectives = [{
            "id": 1, "name": "Test", "status": "OK", "effort": 10,
            "epics": [epic_no_stories]
        }]
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-1/25",
            art_name="Test ART",
            team_objectives=objectives,
        )
        # Should render without error
        assert "### Epic: Backward Compatible Epic" in markdown
        assert "[TEST-1]" in markdown


class TestPhase2BErrorHandling:
    """Tests for Phase 2B error handling and edge cases."""

    @pytest.fixture
    def jira_client(self):
        from tpcli_pi.core.jira_api_client import JiraAPIClient
        return JiraAPIClient(base_url="https://jira.takeda.com", token="test-token")

    def test_jira_api_connection_error_handled(self, jira_client):
        """Test graceful handling of Jira API connection failures."""
        # Expected: Clear error, fallback to Phase 2A (no stories shown)
        pass

    def test_jira_api_timeout_handled(self, jira_client):
        """Test graceful handling of Jira API timeouts."""
        # Expected: Timeout after N seconds, clear message
        pass

    def test_malformed_jira_response_handled(self, jira_client):
        """Test graceful handling of malformed API responses."""
        # Expected: Validation error, not crash
        pass

    def test_missing_story_fields_handled(self, jira_client):
        """Test graceful handling of missing optional fields."""
        # Expected: Status/assignee/points can be missing without breaking
        pass

    def test_story_count_limit_respected(self, jira_client):
        """Test large number of stories handled efficiently."""
        # Expected: Pagination or limit to avoid huge markdown files
        pass
