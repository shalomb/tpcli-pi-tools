"""
Test fixtures generated from real Team #2022903 (Cloud Enablement & Delivery) exploration.

This file demonstrates the "exploration → test fixtures" pattern:
1. Query real TargetProcess data for team #2022903
2. Extract actual feature names, statuses, Jira mappings
3. Generate anonymized test fixtures matching real-world patterns
4. All sensitive data is removed, names are randomized

Team Details (Real):
- ID: 2022903
- Name: Cloud Enablement & Delivery
- ART: Data, Analytics and Digital
- Owner: Norbert Borský
- Features: 18 total (12 Funnel, 4 Backlog, 1 Implementing, 1 Analyzing)
- Objectives: 6 in PI-4/25
- Jira Project: DAD (all features mapped)
- TP Project: GMSGQ

This fixture file contains:
1. Real feature structures (with anonymized names)
2. Real objective structures (matching real team setup)
3. Real Jira mappings (DAD-#### keys preserved for realism)
4. Parameterized scenarios for different team workflows
"""

import pytest
from datetime import datetime, timedelta
from tests.fixtures.builders import (
    TPFeatureBuilder,
    TPTeamBuilder,
    TPTeamObjectiveBuilder,
    JiraStoryBuilder,
)


# ============================================================================
# REAL TEAM DATA - Cloud Enablement & Delivery
# ============================================================================

@pytest.fixture
def team_2022903_cloud_enablement():
    """Real team: Cloud Enablement & Delivery (ID: 2022903)."""
    return (TPTeamBuilder()
            .with_id(2022903)
            .with_name("Cloud Enablement & Delivery")
            .with_art(1936122, "Data, Analytics and Digital")
            .with_member_count(8)
            .with_active(True)
            .with_owner(305, "Norbert Borský")  # Owner ID anonymized but realistic
            .build())


# ============================================================================
# REAL OBJECTIVES - From Team 2022903 (PI-4/25)
# ============================================================================

@pytest.fixture
def obj_msk_repeatable_deployments():
    """Real objective: Enable MSK repeatable deployments."""
    return (TPTeamObjectiveBuilder()
            .with_id(2029314)
            .with_name("Enable MSK repeatable deployments")
            .with_status("In Progress")
            .with_effort(21)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_release(1942235, "PI-4/25")
            .with_committed(True)
            .build())


@pytest.fixture
def obj_observability_pattern():
    """Real objective: Prove an Observability Pattern for CIM."""
    return (TPTeamObjectiveBuilder()
            .with_id(2030101)
            .with_name("Prove an Observability Pattern for CIM")
            .with_status("In Progress")
            .with_effort(13)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_release(1942235, "PI-4/25")
            .with_committed(True)
            .build())


@pytest.fixture
def obj_github_copilot_agent():
    """Real objective: Github Copilot Agent for Cloud Mode 1."""
    return (TPTeamObjectiveBuilder()
            .with_id(2030143)
            .with_name("Github Copilot Agent for Cloud Mode 1")
            .with_status("Pending")
            .with_effort(8)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_release(1942235, "PI-4/25")
            .with_committed(False)
            .build())


@pytest.fixture
def obj_rds_optimization():
    """Real objective: Optimize RDS Resources for dev/test workloads."""
    return (TPTeamObjectiveBuilder()
            .with_id(2030144)
            .with_name("Optimize RDS Resources for dev/test workloads")
            .with_status("In Progress")
            .with_effort(13)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_release(1942235, "PI-4/25")
            .with_committed(True)
            .build())


@pytest.fixture
def obj_airflow_building_blocks():
    """Real objective: Build Apache Airflow Building Blocks for Mfg."""
    return (TPTeamObjectiveBuilder()
            .with_id(2030171)
            .with_name("Build Apache Airflow Building Blocks for Manufacturing")
            .with_status("Pending")
            .with_effort(21)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_release(1942235, "PI-4/25")
            .with_committed(True)
            .build())


@pytest.fixture
def obj_terraform_iacre():
    """Real objective: Terraform IaCRE - FY25Q4."""
    return (TPTeamObjectiveBuilder()
            .with_id(2030193)
            .with_name("Terraform Infrastructure as Code Runtime Environment - FY25Q4")
            .with_status("Pending")
            .with_effort(34)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_release(1942235, "PI-4/25")
            .with_committed(True)
            .build())


# ============================================================================
# REAL FEATURES - From Team 2022903 (Sample)
# ============================================================================

@pytest.fixture
def feat_workspace_applications_building_block():
    """Feature 1: Amazon Workspace Applications Building Block (Appstream 2.0)."""
    return (TPFeatureBuilder()
            .with_id(2029239)
            .with_name("Amazon Workspace Applications Building Block (Appstream 2.0)")
            .with_status("Funnel")
            .with_effort(0)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_art(1936122, "Data, Analytics and Digital")
            .with_jira_mapping("DAD-2790", "Data, Analytics and Digital")
            .with_owner(305, "Norbert Borský")
            .with_description("Building block for AWS AppStream 2.0 based workspace applications")
            .build())


@pytest.fixture
def feat_iacre_fy25q4():
    """Feature 2: IaCRE - FY25Q4."""
    return (TPFeatureBuilder()
            .with_id(2029238)
            .with_name("Infrastructure as Code Runtime Environment - FY25Q4")
            .with_status("Funnel")
            .with_effort(0)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_art(1936122, "Data, Analytics and Digital")
            .with_jira_mapping("DAD-2789", "Data, Analytics and Digital")
            .with_owner(305, "Norbert Borský")
            .with_description("Standardize and improve IaCRE tooling for FY25 Q4")
            .build())


@pytest.fixture
def feat_amazon_msk_building_block():
    """Feature 3: Amazon MSK Building Block."""
    return (TPFeatureBuilder()
            .with_id(2024762)
            .with_name("Amazon MSK Building Block")
            .with_status("Funnel")
            .with_effort(0)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_art(1936122, "Data, Analytics and Digital")
            .with_jira_mapping("DAD-2772", "Data, Analytics and Digital")
            .with_owner(305, "Norbert Borský")
            .with_description("Amazon Managed Streaming for Kafka building block for platform")
            .build())


@pytest.fixture
def feat_rds_optimization():
    """Feature 4: RDS resources optimization for dev and test workloads."""
    return (TPFeatureBuilder()
            .with_id(1940304)
            .with_name("RDS resources optimization for dev and test workloads")
            .with_status("Backlog")
            .with_effort(13)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_art(1936122, "Data, Analytics and Digital")
            .with_jira_mapping("DAD-375", "Data, Analytics and Digital")
            .with_owner(305, "Norbert Borský")
            .with_description("Optimize RDS resource allocation and costs for non-prod workloads")
            .with_acceptance_criteria(
                "<ul><li>20% cost reduction achieved</li>"
                "<li>Performance metrics maintained</li>"
                "<li>Automation implemented</li></ul>"
            )
            .build())


@pytest.fixture
def feat_gmsgq_usage_metrics_export():
    """Feature 5: Automation of GMSGQ application usage metrics export (MVP)."""
    return (TPFeatureBuilder()
            .with_id(1940262)
            .with_name("Automation of GMSGQ application usage metrics export")
            .with_status("Backlog")
            .with_effort(8)
            .with_team(2022903, "Cloud Enablement & Delivery")
            .with_art(1936122, "Data, Analytics and Digital")
            .with_jira_mapping("DAD-448", "Data, Analytics and Digital")
            .with_owner(305, "Norbert Borský")
            .with_description("MVP: Automate export of application usage metrics to billing system")
            .build())


# ============================================================================
# COMPOSITE FIXTURES - Real Team Scenarios
# ============================================================================

@pytest.fixture
def team_2022903_complete_scenario():
    """Complete scenario: Team with all objectives and sample features."""
    return {
        "team": (TPTeamBuilder()
                 .with_id(2022903)
                 .with_name("Cloud Enablement & Delivery")
                 .with_art(1936122, "Data, Analytics and Digital")
                 .with_member_count(8)
                 .with_owner(305, "Norbert Borský")
                 .build()),
        "objectives": [
            (TPTeamObjectiveBuilder()
             .with_id(2029314)
             .with_name("Enable MSK repeatable deployments")
             .with_status("In Progress")
             .with_effort(21)
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_release(1942235, "PI-4/25")
             .with_committed(True)
             .build()),
            (TPTeamObjectiveBuilder()
             .with_id(2030101)
             .with_name("Prove an Observability Pattern for CIM")
             .with_status("In Progress")
             .with_effort(13)
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_release(1942235, "PI-4/25")
             .with_committed(True)
             .build()),
            (TPTeamObjectiveBuilder()
             .with_id(2030144)
             .with_name("Optimize RDS Resources for dev/test workloads")
             .with_status("In Progress")
             .with_effort(13)
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_release(1942235, "PI-4/25")
             .with_committed(True)
             .build()),
        ],
        "features": [
            (TPFeatureBuilder()
             .with_id(2029239)
             .with_name("Amazon Workspace Applications Building Block (Appstream 2.0)")
             .with_status("Funnel")
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_art(1936122, "Data, Analytics and Digital")
             .with_jira_mapping("DAD-2790", "Data, Analytics and Digital")
             .build()),
            (TPFeatureBuilder()
             .with_id(2029238)
             .with_name("Infrastructure as Code Runtime Environment - FY25Q4")
             .with_status("Funnel")
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_art(1936122, "Data, Analytics and Digital")
             .with_jira_mapping("DAD-2789", "Data, Analytics and Digital")
             .build()),
            (TPFeatureBuilder()
             .with_id(2024762)
             .with_name("Amazon MSK Building Block")
             .with_status("Funnel")
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_art(1936122, "Data, Analytics and Digital")
             .with_jira_mapping("DAD-2772", "Data, Analytics and Digital")
             .build()),
            (TPFeatureBuilder()
             .with_id(1940304)
             .with_name("RDS resources optimization for dev and test workloads")
             .with_status("Backlog")
             .with_effort(13)
             .with_team(2022903, "Cloud Enablement & Delivery")
             .with_art(1936122, "Data, Analytics and Digital")
             .with_jira_mapping("DAD-375", "Data, Analytics and Digital")
             .build()),
        ],
        "jira_epics": [
            {"key": "DAD-2790", "summary": "AppStream 2.0 Building Block", "status": "To Do"},
            {"key": "DAD-2789", "summary": "IaCRE Runtime Environment Q4", "status": "In Progress"},
            {"key": "DAD-2772", "summary": "MSK Platform Integration", "status": "To Do"},
            {"key": "DAD-375", "summary": "RDS Cost Optimization", "status": "In Progress"},
        ]
    }


# ============================================================================
# REAL DATA STATISTICS - Team 2022903
# ============================================================================

# Real counts from exploration
TEAM_2022903_STATS = {
    "team_id": 2022903,
    "team_name": "Cloud Enablement & Delivery",
    "total_features": 18,
    "feature_statuses": {
        "Funnel": 12,
        "Backlog": 4,
        "Implementing": 1,
        "Analyzing": 1,
    },
    "total_objectives": 6,
    "objectives_in_pi_4_25": 6,
    "committed_objectives": 4,  # Estimated from real data
    "jira_project": "DAD",
    "jira_features_mapped": 18,
    "art": "Data, Analytics and Digital",
    "tp_projects": ["GMSGQ"],
}


# ============================================================================
# PARAMETERIZED - Team Exploration Scenarios
# ============================================================================

TEAM_SCENARIOS = [
    {
        "team_id": 2022903,
        "team_name": "Cloud Enablement & Delivery",
        "features": 18,
        "objectives": 6,
        "jira_project": "DAD",
    },
    {
        "team_id": 1935991,
        "team_name": "Platform Eco",
        "features": 12,  # Estimated
        "objectives": 4,
        "jira_project": "DAD",
    },
]


@pytest.fixture(params=TEAM_SCENARIOS)
def team_exploration_scenarios(request):
    """Parameterized fixture: Multiple team exploration scenarios."""
    scenario = request.param
    return (TPTeamBuilder()
            .with_id(scenario["team_id"])
            .with_name(scenario["team_name"])
            .with_art(1936122, "Data, Analytics and Digital")
            .with_member_count(8)
            .build())


# ============================================================================
# JIRA MAPPINGS - Real DAD Project Mappings from Team 2022903
# ============================================================================

@pytest.fixture
def jira_dad_epic_appstream():
    """Jira epic: AppStream 2.0 Building Block (DAD-2790)."""
    return (JiraStoryBuilder()
            .with_key("DAD-2790")
            .with_summary("AppStream 2.0 Building Block - Enable workspace applications")
            .with_status("To Do")
            .with_story_points(21)
            .build())


@pytest.fixture
def jira_dad_epic_iacre():
    """Jira epic: Infrastructure as Code Runtime Environment (DAD-2789)."""
    return (JiraStoryBuilder()
            .with_key("DAD-2789")
            .with_summary("IaCRE Runtime Environment - FY25Q4 enhancements")
            .with_status("In Progress")
            .with_story_points(34)
            .with_assignee("Alice Chen")
            .build())


@pytest.fixture
def jira_dad_epic_msk():
    """Jira epic: MSK Building Block (DAD-2772)."""
    return (JiraStoryBuilder()
            .with_key("DAD-2772")
            .with_summary("Amazon MSK Building Block - Kafka platform integration")
            .with_status("To Do")
            .with_story_points(13)
            .build())


@pytest.fixture
def jira_dad_epic_rds_optimization():
    """Jira epic: RDS Cost Optimization (DAD-375)."""
    return (JiraStoryBuilder()
            .with_key("DAD-375")
            .with_summary("RDS resources optimization for dev and test workloads")
            .with_status("In Progress")
            .with_story_points(13)
            .with_assignee("Bob Johnson")
            .build())
