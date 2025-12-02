"""
Example test file demonstrating fixture builder usage.

This file shows best practices for using the fixture builders to create
realistic test data without sensitive company information.

These tests serve as both documentation and validation that:
1. Fixture builders work correctly
2. API client integration with real data structures works
3. Jira client integration with real data structures works
"""

import pytest
from unittest.mock import patch, MagicMock
from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.jira_api_client import JiraAPIClient, JiraStory
from tests.fixtures.builders import (
    TPFeatureBuilder,
    TPTeamBuilder,
    TPTeamObjectiveBuilder,
    JiraStoryBuilder,
    create_tech_debt_feature,
    create_platform_eco_team,
    create_platform_governance_objective,
)


class TestFixtureBuildersBasic:
    """Test basic fixture builder functionality."""

    def test_feature_builder_creates_valid_response(self):
        """Feature builder creates valid TP API response structure."""
        feature = (TPFeatureBuilder()
                   .with_id(1234567)
                   .with_name("Test Feature")
                   .with_status("In Progress")
                   .with_effort(13)
                   .build())

        assert feature["Id"] == 1234567
        assert feature["Name"] == "Test Feature"
        assert feature["Status"] == "In Progress"
        assert feature["Effort"] == 13
        assert feature["ResourceType"] == "Feature"
        assert "Team" in feature
        assert "AgileReleaseTrain" in feature
        assert "Owner" in feature

    def test_team_builder_creates_valid_response(self):
        """Team builder creates valid TP API response structure."""
        team = (TPTeamBuilder()
                .with_id(999999)
                .with_name("Test Team")
                .with_member_count(5)
                .build())

        assert team["Id"] == 999999
        assert team["Name"] == "Test Team"
        assert team["Members"]["length"] == 5
        assert team["ResourceType"] == "Team"
        assert "Owner" in team
        assert "AgileReleaseTrain" in team

    def test_objective_builder_creates_valid_response(self):
        """Objective builder creates valid TP API response structure."""
        objective = (TPTeamObjectiveBuilder()
                     .with_id(888888)
                     .with_name("Test Objective")
                     .with_effort(21)
                     .with_status("Pending")
                     .build())

        assert objective["Id"] == 888888
        assert objective["Name"] == "Test Objective"
        assert objective["Effort"] == 21
        assert objective["Status"] == "Pending"
        assert objective["ResourceType"] == "TeamPIObjective"

    def test_jira_story_builder_creates_valid_response(self):
        """Jira story builder creates valid Jira API response structure."""
        story = (JiraStoryBuilder()
                 .with_key("TST-100")
                 .with_summary("Test Story")
                 .with_status("To Do")
                 .with_story_points(8)
                 .build())

        assert story["key"] == "TST-100"
        assert story["fields"]["summary"] == "Test Story"
        assert story["fields"]["status"]["name"] == "To Do"
        assert story["fields"]["customfield_10001"] == 8


class TestFixtureBuildersChaining:
    """Test fixture builder method chaining."""

    def test_feature_builder_chaining(self):
        """Feature builder supports method chaining."""
        feature = (TPFeatureBuilder()
                   .with_id(1111111)
                   .with_name("Chained Feature")
                   .with_status("Completed")
                   .with_effort(34)
                   .with_team(5555555, "Test Team")
                   .with_jira_mapping("TEST-999", "Test Project")
                   .with_description("A test description")
                   .with_acceptance_criteria("<ul><li>Criterion 1</li></ul>")
                   .build())

        assert feature["Id"] == 1111111
        assert feature["Name"] == "Chained Feature"
        assert feature["Effort"] == 34
        assert feature["Team"]["Id"] == 5555555
        assert feature["Team"]["Name"] == "Test Team"
        # Verify Jira custom fields
        jira_fields = {cf["Name"]: cf["Value"] for cf in feature["CustomFields"]}
        assert jira_fields["Jira Key"] == "TEST-999"

    def test_team_builder_chaining(self):
        """Team builder supports method chaining."""
        team = (TPTeamBuilder()
                .with_id(2222222)
                .with_name("Chained Team")
                .with_art(3333333, "Test ART")
                .with_member_count(25)
                .with_active(True)
                .with_owner(4444444, "Test Owner")
                .build())

        assert team["Id"] == 2222222
        assert team["Name"] == "Chained Team"
        assert team["IsActive"] is True
        assert team["Owner"]["Id"] == 4444444


class TestFixtureIntegrationWithTPAPIClient:
    """Test fixture data integration with TPAPIClient."""

    def test_api_client_can_parse_fixture_feature(self, mocker):
        """TPAPIClient can parse fixture-built feature responses."""
        client = TPAPIClient()
        fixture_feature = create_tech_debt_feature()

        # Mock the subprocess call
        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[fixture_feature],
        )

        # This would normally call tpcli, but we're mocking it
        features = client.get_features()
        assert len(features) == 1

        feature = features[0]
        assert feature.id == 1937700
        assert "Address all tagging issues" in feature.name
        assert feature.team.name == "Cloud Enablement & Delivery"

    def test_api_client_can_parse_fixture_team(self, mocker):
        """TPAPIClient can parse fixture-built team responses."""
        client = TPAPIClient()
        fixture_team = create_platform_eco_team()

        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[fixture_team],
        )

        teams = client.get_teams()
        assert len(teams) == 1

        team = teams[0]
        assert team.id == 1935991
        assert team.name == "Platform Eco"
        assert team.member_count == 12

    def test_api_client_can_parse_fixture_objective(self, mocker):
        """TPAPIClient can parse fixture-built objective responses."""
        client = TPAPIClient()
        fixture_objective = create_platform_governance_objective()

        mocker.patch.object(
            client,
            "_run_tpcli",
            return_value=[fixture_objective],
        )

        objectives = client.get_team_pi_objectives()
        assert len(objectives) == 1

        objective = objectives[0]
        assert objective.id == 2019099
        assert objective.name == "Platform governance"
        assert objective.effort == 21


class TestFixtureIntegrationWithJiraClient:
    """Test fixture data integration with JiraAPIClient."""

    def test_jira_client_can_parse_fixture_story(self, mocker):
        """JiraAPIClient can parse fixture-built story responses."""
        client = JiraAPIClient()
        fixture_story_response = (JiraStoryBuilder()
                                  .with_key("DAD-1760")
                                  .with_summary("Test story")
                                  .with_status("To Do")
                                  .with_assignee("Alice Chen")
                                  .with_story_points(21)
                                  .build())

        # Mock the Jira API response
        mocker.patch.object(
            client,
            "_search_jira",
            return_value=[JiraStory(
                key=fixture_story_response["key"],
                summary=fixture_story_response["fields"]["summary"],
                status=fixture_story_response["fields"]["status"]["name"],
                assignee=fixture_story_response["fields"]["assignee"]["displayName"],
                story_points=fixture_story_response["fields"]["customfield_10001"],
                description=fixture_story_response["fields"]["description"],
            )],
        )

        stories = client.fetch_stories_by_epic("DAD-2652")
        assert len(stories) == 1

        story = stories[0]
        assert story.key == "DAD-1760"
        assert story.status == "To Do"
        assert story.story_points == 21


class TestParametrizedFixtures:
    """Test parameterized fixtures for status variations."""

    @pytest.mark.parametrize("status", [
        "Pending",
        "In Progress",
        "Completed",
        "On Hold",
    ])
    def test_objective_with_various_statuses(self, status):
        """Objectives can be created with any valid status."""
        objective = (TPTeamObjectiveBuilder()
                     .with_name("Test Objective")
                     .with_status(status)
                     .build())

        assert objective["Status"] == status

    @pytest.mark.parametrize("status", [
        "Funnel",
        "In Progress",
        "Completed",
        "On Hold",
    ])
    def test_feature_with_various_statuses(self, status):
        """Features can be created with any valid status."""
        feature = (TPFeatureBuilder()
                   .with_name("Test Feature")
                   .with_status(status)
                   .build())

        assert feature["Status"] == status

    @pytest.mark.parametrize("status,points", [
        ("To Do", 5),
        ("In Progress", 13),
        ("In Review", 8),
        ("Done", 21),
    ])
    def test_jira_story_with_various_statuses_and_points(self, status, points):
        """Stories can be created with various statuses and point values."""
        story = (JiraStoryBuilder()
                 .with_key("TEST-100")
                 .with_summary("Test Story")
                 .with_status(status)
                 .with_story_points(points)
                 .build())

        assert story["fields"]["status"]["name"] == status
        assert story["fields"]["customfield_10001"] == points


class TestFixtureEdgeCases:
    """Test fixture builders with edge cases."""

    def test_feature_with_special_characters_in_name(self):
        """Feature builder handles special characters in name."""
        special_name = 'Feature with <html> & "quotes" & special™'
        feature = (TPFeatureBuilder()
                   .with_name(special_name)
                   .build())

        assert feature["Name"] == special_name

    def test_feature_with_empty_description(self):
        """Feature builder handles empty description."""
        feature = (TPFeatureBuilder()
                   .with_description("")
                   .build())

        assert feature["Description"] == ""

    def test_jira_story_with_no_assignee(self):
        """Jira story builder handles stories with no assignee."""
        story = (JiraStoryBuilder()
                 .with_summary("Unassigned Story")
                 .with_assignee(None)
                 .build())

        assert story["fields"]["assignee"] is None

    def test_jira_story_with_long_description(self):
        """Jira story builder handles very long descriptions."""
        long_desc = "X" * 10000
        story = (JiraStoryBuilder()
                 .with_description(long_desc)
                 .build())

        assert len(story["fields"]["description"]) == 10000


class TestRealWorldScenarios:
    """Test real-world scenarios using fixtures."""

    def test_tech_debt_feature_scenario(self):
        """Real-world scenario: Tech debt feature with Jira mapping."""
        feature = create_tech_debt_feature()

        # Verify all expected fields for a real-world tech debt feature
        assert feature["Id"] == 1937700
        assert "[Tech Debt]" in feature["Name"]
        assert feature["Team"]["Name"] == "Cloud Enablement & Delivery"
        assert feature["AgileReleaseTrain"]["Name"] == "Data, Analytics and Digital"

        # Verify Jira mapping
        jira_fields = {cf["Name"]: cf["Value"] for cf in feature["CustomFields"]}
        assert jira_fields["Jira Key"] == "DAD-1760"
        assert jira_fields["Jira Priority"] == "Medium"

    def test_platform_team_scenario(self):
        """Real-world scenario: Platform team with members and ART."""
        team = create_platform_eco_team()

        assert team["Id"] == 1935991
        assert team["Name"] == "Platform Eco"
        assert team["Members"]["length"] == 12
        assert team["IsActive"] is True
        assert team["AgileReleaseTrain"]["Name"] == "Data, Analytics and Digital"

    def test_objective_commitment_scenario(self):
        """Real-world scenario: Committed team objective in PI."""
        objective = create_platform_governance_objective()

        assert objective["Id"] == 2019099
        assert objective["Committed"] is True
        assert objective["Status"] == "Pending"
        assert objective["Team"]["Name"] == "Platform Eco"
        assert objective["Release"]["Name"] == "PI-4/25"


# Integration example: Using fixtures with fixture functions
@pytest.fixture
def tech_debt_scenario():
    """Composite fixture: Tech debt feature with related objects."""
    return {
        "feature": create_tech_debt_feature(),
        "team": create_platform_eco_team(),
        "objective": create_platform_governance_objective(),
    }


class TestCompositeFixtures:
    """Test using composite fixtures."""

    def test_tech_debt_scenario_integration(self, tech_debt_scenario):
        """Composite fixtures provide complete scenarios."""
        scenario = tech_debt_scenario

        # All pieces should be present
        assert scenario["feature"]["Id"] == 1937700
        assert scenario["team"]["Id"] == 1935991
        assert scenario["objective"]["Id"] == 2019099

        # Verify each piece has proper structure
        assert scenario["feature"]["ResourceType"] == "Feature"
        assert scenario["team"]["ResourceType"] == "Team"
        assert scenario["objective"]["ResourceType"] == "TeamPIObjective"

        # Verify relationships exist (even if not directly matching in this scenario)
        assert "Team" in scenario["feature"]
        assert "Team" in scenario["objective"]
