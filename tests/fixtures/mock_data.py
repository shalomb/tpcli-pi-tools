"""
Shared mock data and common test scenarios for API testing.

This module contains reusable mock data, fixtures, and test scenario builders
that can be shared across multiple test files without duplicating sensitive
company data.

All data is anonymized:
- Names are generic or randomized
- IDs are sequential/test-specific
- Dates are relative to test execution
- No real company/project names in most cases
"""

import pytest
from datetime import datetime, timedelta
from tests.fixtures.builders import (
    TPFeatureBuilder,
    TPTeamBuilder,
    TPTeamObjectiveBuilder,
    JiraStoryBuilder,
    create_tech_debt_feature,
    create_platform_eco_team,
    create_platform_governance_objective,
)


# ============================================================================
# TargetProcess Common Scenarios
# ============================================================================


@pytest.fixture
def tp_tech_debt_feature():
    """Fixture: Realistic tech debt feature (based on #1937700)."""
    return create_tech_debt_feature()


@pytest.fixture
def tp_platform_team():
    """Fixture: Realistic platform team."""
    return create_platform_eco_team()


@pytest.fixture
def tp_platform_objective():
    """Fixture: Realistic team objective."""
    return create_platform_governance_objective()


@pytest.fixture
def tp_multiple_teams():
    """Fixture: Multiple teams with different ARTs."""
    return [
        create_platform_eco_team(),
        (TPTeamBuilder()
         .with_id(2022904)
         .with_name("Data Analytics")
         .with_art(1936123, "Data Analytics and Engineering")
         .with_member_count(10)
         .build()),
        (TPTeamBuilder()
         .with_id(2022905)
         .with_name("Cloud Infrastructure")
         .with_art(1936122, "Data, Analytics and Digital")
         .with_member_count(15)
         .build()),
    ]


@pytest.fixture
def tp_multiple_objectives():
    """Fixture: Multiple team objectives."""
    return [
        create_platform_governance_objective(),
        (TPTeamObjectiveBuilder()
         .with_id(2019100)
         .with_name("API performance optimization")
         .with_effort(34)
         .with_team(1935991, "Platform Eco")
         .with_release(1942235, "PI-4/25")
         .with_status("In Progress")
         .build()),
        (TPTeamObjectiveBuilder()
         .with_id(2019101)
         .with_name("Security audit and remediation")
         .with_effort(28)
         .with_team(1935991, "Platform Eco")
         .with_release(1942236, "PI-5/25")
         .with_status("Pending")
         .build()),
    ]


@pytest.fixture
def tp_multiple_features():
    """Fixture: Multiple features in different states."""
    return [
        create_tech_debt_feature(),
        (TPFeatureBuilder()
         .with_id(1937701)
         .with_name("Implement distributed tracing")
         .with_status("In Progress")
         .with_effort(13)
         .with_team(1935991, "Platform Eco")
         .with_art(1936122, "Data, Analytics and Digital")
         .with_jira_mapping("DAD-1761", "Data, Analytics and Digital")
         .build()),
        (TPFeatureBuilder()
         .with_id(1937702)
         .with_name("Update monitoring dashboards")
         .with_status("Completed")
         .with_effort(8)
         .with_team(1935991, "Platform Eco")
         .with_art(1936122, "Data, Analytics and Digital")
         .with_jira_mapping("DAD-1762", "Data, Analytics and Digital")
         .build()),
    ]


# ============================================================================
# Jira Common Scenarios
# ============================================================================


@pytest.fixture
def jira_story_basic():
    """Fixture: Basic Jira story."""
    return (JiraStoryBuilder()
            .with_key("DAD-1760")
            .with_summary("[Tech Debt] Address all tagging issues")
            .with_status("To Do")
            .with_assignee("Alice Chen")
            .with_story_points(21)
            .build())


@pytest.fixture
def jira_stories_under_epic():
    """Fixture: Multiple stories under an epic."""
    return [
        (JiraStoryBuilder()
         .with_key("DAD-1760")
         .with_summary("[Tech Debt] Address all tagging issues")
         .with_status("To Do")
         .with_assignee("Alice Chen")
         .with_story_points(21)
         .build()),
        (JiraStoryBuilder()
         .with_key("DAD-1761")
         .with_summary("Implement distributed tracing")
         .with_status("In Progress")
         .with_assignee("Bob Johnson")
         .with_story_points(13)
         .build()),
        (JiraStoryBuilder()
         .with_key("DAD-1762")
         .with_summary("Update monitoring dashboards")
         .with_status("Done")
         .with_assignee("Charlie Davis")
         .with_story_points(8)
         .build()),
    ]


@pytest.fixture
def jira_story_no_assignee():
    """Fixture: Story without assignee."""
    return (JiraStoryBuilder()
            .with_key("DAD-1763")
            .with_summary("Technical spike: Evaluate new frameworks")
            .with_status("To Do")
            .with_assignee(None)
            .with_story_points(5)
            .build())


@pytest.fixture
def jira_story_high_points():
    """Fixture: Story with high story points."""
    return (JiraStoryBuilder()
            .with_key("DAD-1764")
            .with_summary("Major refactoring: Database schema redesign")
            .with_status("To Do")
            .with_assignee("Diana Martinez")
            .with_story_points(55)
            .build())


# ============================================================================
# Parametrized Test Data
# ============================================================================

# Teams with different configurations
TEAM_SCENARIOS = [
    {"id": 1935991, "name": "Platform Eco", "art": "Data, Analytics and Digital", "members": 12},
    {"id": 2022903, "name": "Cloud Enablement & Delivery", "art": "Data, Analytics and Digital", "members": 8},
    {"id": 2022904, "name": "Data Analytics", "art": "Data Analytics and Engineering", "members": 10},
]

# Objectives with different statuses
OBJECTIVE_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
    "On Hold",
]

# Feature statuses
FEATURE_STATUSES = [
    "Funnel",
    "In Progress",
    "Completed",
    "Cancelled",
    "On Hold",
]

# Jira statuses
JIRA_STATUSES = [
    "To Do",
    "In Progress",
    "In Review",
    "Done",
    "Blocked",
]

# Jira priorities
JIRA_PRIORITIES = [
    "Highest",
    "High",
    "Medium",
    "Low",
    "Lowest",
]


@pytest.fixture(params=TEAM_SCENARIOS)
def tp_team_scenarios(request):
    """Parametrized fixture: Teams with different configs."""
    scenario = request.param
    return (TPTeamBuilder()
            .with_id(scenario["id"])
            .with_name(scenario["name"])
            .with_art(1936122, scenario["art"])
            .with_member_count(scenario["members"])
            .build())


@pytest.fixture(params=OBJECTIVE_STATUSES)
def tp_objective_statuses(request):
    """Parametrized fixture: Objectives with different statuses."""
    status = request.param
    return (TPTeamObjectiveBuilder()
            .with_id(2019099)
            .with_name("Sample Objective")
            .with_status(status)
            .build())


@pytest.fixture(params=FEATURE_STATUSES)
def tp_feature_statuses(request):
    """Parametrized fixture: Features with different statuses."""
    status = request.param
    return (TPFeatureBuilder()
            .with_id(1937700)
            .with_name("Sample Feature")
            .with_status(status)
            .build())


@pytest.fixture(params=JIRA_STATUSES)
def jira_story_statuses(request):
    """Parametrized fixture: Stories with different statuses."""
    status = request.param
    return (JiraStoryBuilder()
            .with_key("TEST-100")
            .with_summary("Sample Story")
            .with_status(status)
            .build())


# ============================================================================
# Edge Cases and Error Scenarios
# ============================================================================


@pytest.fixture
def tp_feature_minimal():
    """Fixture: Minimal feature with only required fields."""
    return {
        "Id": 9999999,
        "Name": "Minimal Feature",
        "ResourceType": "Feature",
    }


@pytest.fixture
def tp_feature_with_nulls():
    """Fixture: Feature with many null/empty fields."""
    return (TPFeatureBuilder()
            .with_id(1937799)
            .with_name("Sparse Feature")
            .with_effort(0)
            .with_description("")
            .build())


@pytest.fixture
def tp_feature_with_special_chars():
    """Fixture: Feature with special characters in name."""
    return (TPFeatureBuilder()
            .with_id(1937798)
            .with_name("Feature with <special> & \"characters\" in name™")
            .build())


@pytest.fixture
def jira_story_with_long_description():
    """Fixture: Story with very long description."""
    long_desc = "A" * 5000  # 5000 character description
    return (JiraStoryBuilder()
            .with_key("TEST-200")
            .with_summary("Story with long description")
            .with_description(long_desc)
            .build())


# ============================================================================
# Batch Operations
# ============================================================================


@pytest.fixture
def tp_batch_create_objectives():
    """Fixture: Batch data for creating multiple objectives."""
    return [
        {
            "name": "Objective 1",
            "team_id": 1935991,
            "release_id": 1942235,
            "effort": 21,
        },
        {
            "name": "Objective 2",
            "team_id": 1935991,
            "release_id": 1942235,
            "effort": 34,
        },
        {
            "name": "Objective 3",
            "team_id": 1935991,
            "release_id": 1942235,
            "effort": 13,
        },
    ]


@pytest.fixture
def tp_batch_update_objectives():
    """Fixture: Batch data for updating multiple objectives."""
    return [
        {
            "id": 2019099,
            "name": "Updated Objective 1",
            "effort": 25,
        },
        {
            "id": 2019100,
            "name": "Updated Objective 2",
            "effort": 30,
        },
    ]


# ============================================================================
# Constants and Mappings
# ============================================================================

# Common test IDs (non-sensitive)
TEST_IDS = {
    "team_1": 1935991,
    "team_2": 2022903,
    "art_1": 1936122,
    "art_2": 1936123,
    "release_1": 1942235,
    "release_2": 1942236,
    "objective_1": 2019099,
    "objective_2": 2019100,
    "feature_1": 1937700,
    "feature_2": 1937701,
    "user_1": 450,
    "user_2": 319,
}

# Common test names (anonymized)
TEST_NAMES = {
    "team_1": "Platform Eco",
    "team_2": "Cloud Enablement & Delivery",
    "art_1": "Data, Analytics and Digital",
    "art_2": "Data Analytics and Engineering",
    "objective_1": "Platform governance",
    "objective_2": "API performance optimization",
    "feature_1": "[Tech Debt] Address all tagging issues",
    "feature_2": "Implement distributed tracing",
    "user_1": "Test User 1",
    "user_2": "Test User 2",
}
