"""
pytest configuration and fixtures.

Configures VCR for cassette recording/replay, logging, and shared fixtures.
Also imports git repository test fixtures.
"""

import pytest
import vcr
import os
from tests.fixtures.git_helper import (
    git_repo,
    git_repo_with_branches,
    git_repo_tracking_scenario,
    git_repo_conflict_scenario,
)

# Import all mock data and builder fixtures
# This makes them available to all tests without explicit imports
pytest_plugins = [
    "tests.fixtures.mock_data",
]


# Configure VCR for golden file cassette recording/replay
vcr_config = vcr.VCR(
    # Record mode: 'once' = record if cassette doesn't exist, else replay
    # Use 'new_episodes' to add new interactions to existing cassettes
    record_mode=os.environ.get("VCR_RECORD_MODE", "once"),

    # Cassette directory
    cassette_library_dir="tests/fixtures/python",

    # Filter sensitive headers and query params
    filter_headers=[
        "Authorization",
        "access-token",
        "x-api-key",
    ],

    # Remove API tokens from URIs before recording
    filter_query_parameters=["access_token", "token"],

    # Match requests by method and URI (ignore body/headers variations)
    match_on=["method", "uri"],

    # Path transformer: extract just the path, not full URI
    # This makes cassettes more portable
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),

    # Don't record requests that match these patterns
    ignore_hosts=["localhost", "127.0.0.1"],
)


@pytest.fixture
def vcr_config_fixture():
    """
    Fixture providing VCR configuration for tests.

    Usage:
        @pytest.mark.vcr
        def test_something(vcr_cassette):
            # Cassette is auto-loaded from tests/fixtures/python/
            ...
    """
    return vcr_config


def pytest_configure(config):
    """
    pytest hook: Configure markers.
    """
    config.addinivalue_line(
        "markers",
        "vcr: mark test to use VCR cassette recording (requires vcrpy)"
    )
    config.addinivalue_line(
        "markers",
        "record: mark test to re-record VCR cassette (for maintenance)"
    )


@pytest.fixture
def tp_api_base_url():
    """Fixture providing TP API base URL."""
    return os.environ.get("TP_URL", "https://company.tpondemand.com")


@pytest.fixture
def tp_api_token():
    """Fixture providing TP API token (may be empty in CI/CD)."""
    return os.environ.get("TP_TOKEN", "test-token")


@pytest.fixture
def tp_test_team_id():
    """Fixture providing test team ID."""
    return 1935991


@pytest.fixture
def tp_test_release_id():
    """Fixture providing test release ID."""
    return 1942235


@pytest.fixture
def tp_test_objective_id():
    """Fixture providing test objective ID."""
    return 12345


@pytest.fixture
def tp_test_feature_id():
    """Fixture providing test feature ID."""
    return 5678
