"""
Fixture builders for TargetProcess and Jira API responses.

These builders create realistic test data structures that match real API
responses, without including any sensitive company information. They're
useful for creating parameterized tests and complex scenarios.

Usage:
    from tests.fixtures.builders import TPFeatureBuilder, TPTeamBuilder

    # Build a complete feature with nested objects
    feature = (TPFeatureBuilder()
        .with_id(1937700)
        .with_name("[Tech Debt] Address all tagging issues")
        .with_team("Cloud Enablement & Delivery")
        .with_art("Data, Analytics and Digital")
        .with_jira_mapping("DAD-1760", "Data, Analytics and Digital")
        .build())

    # Build multiple scenarios
    team_scenarios = [
        TPTeamBuilder().with_name("Platform Eco").build(),
        TPTeamBuilder().with_name("Cloud Enablement").build(),
        TPTeamBuilder().with_name("Data Analytics").build(),
    ]
"""

from datetime import datetime, timedelta
from typing import Any, Optional
import json


class TPTeamBuilder:
    """Builder for TargetProcess Team API responses."""

    def __init__(self):
        self._id = 2022903
        self._name = "Cloud Enablement & Delivery"
        self._art_id = 1936122
        self._art_name = "Data, Analytics and Digital"
        self._member_count = 8
        self._is_active = True
        self._owner_name = "Stéphane Dattenny"
        self._owner_id = 319

    def with_id(self, team_id: int) -> "TPTeamBuilder":
        """Set team ID."""
        self._id = team_id
        return self

    def with_name(self, name: str) -> "TPTeamBuilder":
        """Set team name."""
        self._name = name
        return self

    def with_art(self, art_id: int, art_name: str) -> "TPTeamBuilder":
        """Set ART."""
        self._art_id = art_id
        self._art_name = art_name
        return self

    def with_member_count(self, count: int) -> "TPTeamBuilder":
        """Set member count."""
        self._member_count = count
        return self

    def with_active(self, active: bool) -> "TPTeamBuilder":
        """Set active status."""
        self._is_active = active
        return self

    def with_owner(self, owner_id: int, owner_name: str) -> "TPTeamBuilder":
        """Set team owner."""
        self._owner_id = owner_id
        self._owner_name = owner_name
        return self

    def build(self) -> dict[str, Any]:
        """Build the TP Team API response."""
        return {
            "Id": self._id,
            "Name": self._name,
            "Abbreviation": "".join([word[0] for word in self._name.split()])[:4],
            "IsActive": self._is_active,
            "CreateDate": f"/Date({int((datetime.now() - timedelta(days=365)).timestamp() * 1000)}-0400)/",
            "ModifyDate": f"/Date({int(datetime.now().timestamp() * 1000)}-0500)/",
            "AgileReleaseTrain": {
                "Id": self._art_id,
                "Name": self._art_name,
                "ResourceType": "AgileReleaseTrain",
            } if self._art_id else None,
            "Owner": {
                "Id": self._owner_id,
                "FullName": self._owner_name,
                "ResourceType": "GeneralUser",
            },
            "Members": {"length": self._member_count},
            "ResourceType": "Team",
        }


class TPFeatureBuilder:
    """Builder for TargetProcess Feature API responses."""

    def __init__(self):
        self._id = 1937700
        self._name = "[Tech Debt] Address all tagging issues across the application/solutions deployed on the platform"
        self._status = "Funnel"
        self._effort = 0
        self._team_id = 2022903
        self._team_name = "Cloud Enablement & Delivery"
        self._art_id = 1936122
        self._art_name = "Data, Analytics and Digital"
        self._owner_id = 319
        self._owner_name = "Stéphane Dattenny"
        self._editor_id = 450
        self._editor_name = "Shalom Bhooshi"
        self._description = "Problem Statement: specifically in Takeda Enterprise Cloud, there are still too many AWS resources that are not tagged appropriately"
        self._priority = "Will Not Have"
        self._project_id = 223264
        self._project_name = "GMSGQ"
        self._jira_key = "DAD-1760"
        self._jira_project = "Data, Analytics and Digital"
        self._jira_priority = "Medium"
        self._created_date = datetime.now() - timedelta(days=30)
        self._modified_date = datetime.now() - timedelta(days=1)
        self._acceptance_criteria = "<ul><li><p>80% of the untagged resources are addressed</p></li></ul>"

    def with_id(self, feature_id: int) -> "TPFeatureBuilder":
        """Set feature ID."""
        self._id = feature_id
        return self

    def with_name(self, name: str) -> "TPFeatureBuilder":
        """Set feature name."""
        self._name = name
        return self

    def with_status(self, status: str) -> "TPFeatureBuilder":
        """Set feature status."""
        self._status = status
        return self

    def with_effort(self, effort: int) -> "TPFeatureBuilder":
        """Set effort in story points."""
        self._effort = effort
        return self

    def with_team(self, team_id: int, team_name: str = None) -> "TPFeatureBuilder":
        """Set team."""
        self._team_id = team_id
        if team_name:
            self._team_name = team_name
        return self

    def with_art(self, art_id: int, art_name: str = None) -> "TPFeatureBuilder":
        """Set ART."""
        self._art_id = art_id
        if art_name:
            self._art_name = art_name
        return self

    def with_owner(self, owner_id: int, owner_name: str) -> "TPFeatureBuilder":
        """Set owner."""
        self._owner_id = owner_id
        self._owner_name = owner_name
        return self

    def with_jira_mapping(self, jira_key: str, jira_project: str = None) -> "TPFeatureBuilder":
        """Set Jira mapping."""
        self._jira_key = jira_key
        if jira_project:
            self._jira_project = jira_project
        return self

    def with_jira_priority(self, priority: str) -> "TPFeatureBuilder":
        """Set Jira priority."""
        self._jira_priority = priority
        return self

    def with_description(self, description: str) -> "TPFeatureBuilder":
        """Set description."""
        self._description = description
        return self

    def with_acceptance_criteria(self, criteria: str) -> "TPFeatureBuilder":
        """Set acceptance criteria (HTML)."""
        self._acceptance_criteria = criteria
        return self

    def _ts(self, dt: datetime) -> str:
        """Convert datetime to TP format."""
        ms = int(dt.timestamp() * 1000)
        offset = "-0400" if dt.month > 10 else "-0500"
        return f"/Date({ms}{offset})/"

    def build(self) -> dict[str, Any]:
        """Build the TP Feature API response."""
        return {
            "Id": self._id,
            "Name": self._name,
            "Description": self._description,
            "EntityType": {"Id": 9, "Name": "Feature", "ResourceType": "EntityType"},
            "EntityState": {
                "Id": 87,
                "Name": self._status,
                "NumericPriority": 1,
                "ResourceType": "EntityState",
            },
            "Status": self._status,
            "Priority": {
                "Id": 10,
                "Importance": 4,
                "Name": self._priority,
                "ResourceType": "Priority",
            },
            "Effort": self._effort,
            "EffortCompleted": 0,
            "EffortToDo": self._effort,
            "InitialEstimate": 0,
            "TimeSpent": 0,
            "TimeRemain": 0,
            "Progress": 0,
            "Team": {
                "Id": self._team_id,
                "Name": self._team_name,
                "ResourceType": "Team",
            },
            "AgileReleaseTrain": {
                "Id": self._art_id,
                "Name": self._art_name,
                "ResourceType": "AgileReleaseTrain",
            },
            "Project": {
                "Id": self._project_id,
                "Name": self._project_name,
                "ResourceType": "Project",
            },
            "Owner": {
                "Id": self._owner_id,
                "FullName": self._owner_name,
                "ResourceType": "GeneralUser",
            },
            "Creator": {
                "Id": self._owner_id,
                "FullName": self._owner_name,
                "ResourceType": "GeneralUser",
            },
            "LastEditor": {
                "Id": self._editor_id,
                "FullName": self._editor_name,
                "ResourceType": "GeneralUser",
            },
            "CreateDate": self._ts(self._created_date),
            "ModifyDate": self._ts(self._modified_date),
            "LastStateChangeDate": self._ts(self._modified_date),
            "StartDate": None,
            "EndDate": None,
            "PlannedStartDate": self._ts(self._created_date + timedelta(days=7)),
            "PlannedEndDate": self._ts(self._created_date + timedelta(days=35)),
            "CustomFields": [
                {
                    "Name": "Acceptance Criteria",
                    "Type": "RichText",
                    "Value": self._acceptance_criteria,
                },
                {
                    "Name": "Jira Key",
                    "Type": "TemplatedURL",
                    "Value": self._jira_key,
                },
                {
                    "Name": "Jira Priority",
                    "Type": "DropDown",
                    "Value": self._jira_priority,
                },
                {
                    "Name": "Jira Project",
                    "Type": "Text",
                    "Value": self._jira_project,
                },
            ],
            "ResourceType": "Feature",
        }


class JiraStoryBuilder:
    """Builder for Jira story API responses."""

    def __init__(self):
        self._key = "DAD-1760"
        self._summary = "[Tech Debt] Address all tagging issues across the application"
        self._status = "In Progress"
        self._assignee = "Stéphane Dattenny"
        self._story_points = 21
        self._description = "Need to tag all untagged resources in AWS"
        self._epic_link = "DAD-2652"

    def with_key(self, key: str) -> "JiraStoryBuilder":
        """Set Jira key (e.g., DAD-1760)."""
        self._key = key
        return self

    def with_summary(self, summary: str) -> "JiraStoryBuilder":
        """Set issue summary."""
        self._summary = summary
        return self

    def with_status(self, status: str) -> "JiraStoryBuilder":
        """Set status."""
        self._status = status
        return self

    def with_assignee(self, assignee: str) -> "JiraStoryBuilder":
        """Set assignee."""
        self._assignee = assignee
        return self

    def with_story_points(self, points: int) -> "JiraStoryBuilder":
        """Set story points."""
        self._story_points = points
        return self

    def with_description(self, description: str) -> "JiraStoryBuilder":
        """Set description."""
        self._description = description
        return self

    def with_epic_link(self, epic: str) -> "JiraStoryBuilder":
        """Set epic link."""
        self._epic_link = epic
        return self

    def build(self) -> dict[str, Any]:
        """Build the Jira story API response."""
        return {
            "key": self._key,
            "fields": {
                "summary": self._summary,
                "status": {"name": self._status},
                "assignee": (
                    {"displayName": self._assignee}
                    if self._assignee
                    else None
                ),
                "customfield_10001": self._story_points,
                "description": self._description,
                "customfield_10002": self._epic_link,
            },
        }


class TPTeamObjectiveBuilder:
    """Builder for TargetProcess Team PI Objective API responses."""

    def __init__(self):
        self._id = 2019099
        self._name = "Platform governance"
        self._status = "Pending"
        self._effort = 21
        self._team_id = 1935991
        self._team_name = "Platform Eco"
        self._release_id = 1942235
        self._release_name = "PI-4/25"
        self._owner_id = 450
        self._owner_name = "Shalom Bhooshi"
        self._description = "Establish governance frameworks"
        self._committed = True
        self._created_date = datetime.now() - timedelta(days=60)

    def with_id(self, obj_id: int) -> "TPTeamObjectiveBuilder":
        """Set objective ID."""
        self._id = obj_id
        return self

    def with_name(self, name: str) -> "TPTeamObjectiveBuilder":
        """Set objective name."""
        self._name = name
        return self

    def with_status(self, status: str) -> "TPTeamObjectiveBuilder":
        """Set status."""
        self._status = status
        return self

    def with_effort(self, effort: int) -> "TPTeamObjectiveBuilder":
        """Set effort."""
        self._effort = effort
        return self

    def with_team(self, team_id: int, team_name: str = None) -> "TPTeamObjectiveBuilder":
        """Set team."""
        self._team_id = team_id
        if team_name:
            self._team_name = team_name
        return self

    def with_release(self, release_id: int, release_name: str = None) -> "TPTeamObjectiveBuilder":
        """Set release."""
        self._release_id = release_id
        if release_name:
            self._release_name = release_name
        return self

    def with_committed(self, committed: bool) -> "TPTeamObjectiveBuilder":
        """Set committed status."""
        self._committed = committed
        return self

    def build(self) -> dict[str, Any]:
        """Build the TP Team Objective API response."""
        return {
            "Id": self._id,
            "Name": self._name,
            "Description": self._description,
            "Status": self._status,
            "Effort": self._effort,
            "Committed": self._committed,
            "Team": {
                "Id": self._team_id,
                "Name": self._team_name,
                "ResourceType": "Team",
            },
            "Release": {
                "Id": self._release_id,
                "Name": self._release_name,
                "ResourceType": "Release",
            },
            "Owner": {
                "Id": self._owner_id,
                "FullName": self._owner_name,
                "ResourceType": "GeneralUser",
            },
            "CreatedDate": f"/Date({int(self._created_date.timestamp() * 1000)}-0400)/",
            "ModifyDate": f"/Date({int(datetime.now().timestamp() * 1000)}-0500)/",
            "ResourceType": "TeamPIObjective",
        }


# Convenience functions for common scenarios

def create_tech_debt_feature() -> dict[str, Any]:
    """Create a realistic tech debt feature (based on real #1937700)."""
    return (
        TPFeatureBuilder()
        .with_id(1937700)
        .with_name("[Tech Debt] Address all tagging issues across the application/solutions deployed on the platform")
        .with_status("Funnel")
        .with_team(2022903, "Cloud Enablement & Delivery")
        .with_art(1936122, "Data, Analytics and Digital")
        .with_jira_mapping("DAD-1760", "Data, Analytics and Digital")
        .with_jira_priority("Medium")
        .with_acceptance_criteria("<ul><li><p>80% of the untagged resources are addressed</p></li></ul>")
        .build()
    )


def create_platform_eco_team() -> dict[str, Any]:
    """Create a realistic team scenario."""
    return (
        TPTeamBuilder()
        .with_id(1935991)
        .with_name("Platform Eco")
        .with_art(1936122, "Data, Analytics and Digital")
        .with_member_count(12)
        .with_owner(450, "Shalom Bhooshi")
        .build()
    )


def create_platform_governance_objective() -> dict[str, Any]:
    """Create a realistic team objective."""
    return (
        TPTeamObjectiveBuilder()
        .with_id(2019099)
        .with_name("Platform governance")
        .with_effort(21)
        .with_team(1935991, "Platform Eco")
        .with_release(1942235, "PI-4/25")
        .with_status("Pending")
        .with_committed(True)
        .build()
    )
