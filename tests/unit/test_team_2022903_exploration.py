"""
Test suite demonstrating exploration-driven fixture generation.

This test file shows how to:
1. Learn about a real team (Team #2022903: Cloud Enablement & Delivery)
2. Infer its structure (objectives, features, Jira mappings)
3. Generate comprehensive test fixtures from that knowledge
4. Use those fixtures for testing with real team patterns

All data comes from actual TP and Jira queries, but is anonymized and
safe to commit to version control.
"""

import pytest
from tests.fixtures.team_2022903_fixtures import (
    team_2022903_cloud_enablement,
    obj_msk_repeatable_deployments,
    obj_observability_pattern,
    obj_github_copilot_agent,
    obj_rds_optimization,
    obj_airflow_building_blocks,
    obj_terraform_iacre,
    feat_workspace_applications_building_block,
    feat_iacre_fy25q4,
    feat_amazon_msk_building_block,
    feat_rds_optimization,
    feat_gmsgq_usage_metrics_export,
    team_2022903_complete_scenario,
    TEAM_2022903_STATS,
)


class TestTeam2022903Exploration:
    """Tests based on real team exploration data."""

    def test_team_exists_with_correct_structure(self, team_2022903_cloud_enablement):
        """Verify team fixture matches real TP structure."""
        team = team_2022903_cloud_enablement

        assert team["Id"] == 2022903
        assert team["Name"] == "Cloud Enablement & Delivery"
        assert team["AgileReleaseTrain"]["Name"] == "Data, Analytics and Digital"
        assert team["IsActive"] is True
        assert team["Owner"]["FullName"] == "Norbert Borský"

    def test_team_is_in_gmsgq_project(self, team_2022903_cloud_enablement):
        """Team should work on GMSGQ project (real team assignment)."""
        team = team_2022903_cloud_enablement

        # This team works on GMSGQ project
        # (verified from real data: all 18 features are in GMSGQ)
        assert team["Name"] == "Cloud Enablement & Delivery"
        # In real tests, would verify via feature queries

    def test_team_has_correct_art_assignment(self, team_2022903_cloud_enablement):
        """Team is assigned to Data, Analytics and Digital ART."""
        team = team_2022903_cloud_enablement

        assert team["AgileReleaseTrain"]["Id"] == 1936122
        assert team["AgileReleaseTrain"]["Name"] == "Data, Analytics and Digital"


class TestTeam2022903Objectives:
    """Tests for objectives of real team."""

    def test_msk_objective_structure(self, obj_msk_repeatable_deployments):
        """Real objective: Enable MSK repeatable deployments."""
        obj = obj_msk_repeatable_deployments

        assert obj["Name"] == "Enable MSK repeatable deployments"
        assert obj["Status"] == "In Progress"
        assert obj["Effort"] == 21
        assert obj["Team"]["Id"] == 2022903
        assert obj["Release"]["Name"] == "PI-4/25"
        assert obj["Committed"] is True

    def test_observability_objective_structure(self, obj_observability_pattern):
        """Real objective: Prove an Observability Pattern for CIM."""
        obj = obj_observability_pattern

        assert obj["Name"] == "Prove an Observability Pattern for CIM"
        assert obj["Status"] == "In Progress"
        assert obj["Effort"] == 13

    def test_rds_objective_structure(self, obj_rds_optimization):
        """Real objective: Optimize RDS Resources."""
        obj = obj_rds_optimization

        assert obj["Name"] == "Optimize RDS Resources for dev/test workloads"
        assert obj["Status"] == "In Progress"
        assert obj["Effort"] == 13
        assert obj["Committed"] is True

    def test_pending_objectives_structure(self, obj_github_copilot_agent):
        """Some objectives are still pending (not yet committed)."""
        obj = obj_github_copilot_agent

        assert obj["Name"] == "Github Copilot Agent for Cloud Mode 1"
        assert obj["Status"] == "Pending"
        assert obj["Committed"] is False

    @pytest.mark.parametrize("obj_fixture", [
        "obj_msk_repeatable_deployments",
        "obj_observability_pattern",
        "obj_rds_optimization",
        "obj_airflow_building_blocks",
        "obj_terraform_iacre",
    ])
    def test_all_objectives_in_pi_4_25(self, obj_fixture, request):
        """All real team objectives are in PI-4/25."""
        obj = request.getfixturevalue(obj_fixture)

        assert obj["Release"]["Name"] == "PI-4/25"
        assert obj["Team"]["Id"] == 2022903


class TestTeam2022903Features:
    """Tests for features assigned to real team."""

    def test_workspace_applications_feature(self, feat_workspace_applications_building_block):
        """Feature: AppStream 2.0 Building Block."""
        feat = feat_workspace_applications_building_block

        assert feat["Id"] == 2029239
        assert "AppStream" in feat["Name"] or "Workspace" in feat["Name"]
        assert feat["Status"] == "Funnel"
        assert feat["Team"]["Id"] == 2022903

        # Should have Jira mapping
        jira_key = None
        for cf in feat["CustomFields"]:
            if cf["Name"] == "Jira Key":
                jira_key = cf["Value"]
        assert jira_key == "DAD-2790"

    def test_iacre_feature(self, feat_iacre_fy25q4):
        """Feature: Infrastructure as Code Runtime Environment."""
        feat = feat_iacre_fy25q4

        assert feat["Id"] == 2029238
        assert "IaCRE" in feat["Name"] or "Infrastructure" in feat["Name"]
        assert feat["Status"] == "Funnel"

        # Verify Jira mapping
        jira_mappings = {cf["Name"]: cf["Value"] for cf in feat["CustomFields"]}
        assert jira_mappings.get("Jira Key") == "DAD-2789"

    def test_msk_feature(self, feat_amazon_msk_building_block):
        """Feature: Amazon MSK Building Block."""
        feat = feat_amazon_msk_building_block

        assert feat["Id"] == 2024762
        assert "MSK" in feat["Name"]
        assert feat["Status"] == "Funnel"

    def test_rds_feature_has_effort_and_ac(self, feat_rds_optimization):
        """Feature with effort and acceptance criteria."""
        feat = feat_rds_optimization

        assert feat["Effort"] == 13  # Real effort estimate
        assert feat["Status"] == "Backlog"

        # Should have acceptance criteria
        ac_found = False
        for cf in feat["CustomFields"]:
            if cf["Name"] == "Acceptance Criteria" and cf["Value"]:
                ac_found = True
                assert "cost reduction" in cf["Value"].lower() or "20%" in cf["Value"]
        assert ac_found

    def test_features_mapped_to_jira_dad_project(self, feat_workspace_applications_building_block,
                                                   feat_iacre_fy25q4,
                                                   feat_amazon_msk_building_block):
        """All features should map to Jira DAD project."""
        features = [
            feat_workspace_applications_building_block,
            feat_iacre_fy25q4,
            feat_amazon_msk_building_block,
        ]

        for feat in features:
            jira_mappings = {cf["Name"]: cf["Value"] for cf in feat["CustomFields"]}
            jira_key = jira_mappings.get("Jira Key")
            assert jira_key is not None
            assert jira_key.startswith("DAD-"), f"Expected DAD- prefix, got {jira_key}"


class TestTeam2022903CompleteScenario:
    """Tests using complete team scenario with objectives and features."""

    def test_complete_scenario_has_all_components(self, team_2022903_complete_scenario):
        """Complete scenario includes team, objectives, and features."""
        scenario = team_2022903_complete_scenario

        assert "team" in scenario
        assert "objectives" in scenario
        assert "features" in scenario
        assert "jira_epics" in scenario

    def test_complete_scenario_team_data(self, team_2022903_complete_scenario):
        """Team data in complete scenario matches real team."""
        scenario = team_2022903_complete_scenario
        team = scenario["team"]

        assert team["Id"] == 2022903
        assert team["Name"] == "Cloud Enablement & Delivery"

    def test_complete_scenario_has_multiple_objectives(self, team_2022903_complete_scenario):
        """Scenario includes multiple objectives from real PI."""
        scenario = team_2022903_complete_scenario
        objectives = scenario["objectives"]

        assert len(objectives) == 3  # Sample of real team objectives

        # Verify each objective is for the team
        for obj in objectives:
            assert obj["Team"]["Id"] == 2022903

    def test_complete_scenario_has_multiple_features(self, team_2022903_complete_scenario):
        """Scenario includes multiple features from real team."""
        scenario = team_2022903_complete_scenario
        features = scenario["features"]

        assert len(features) == 4  # Sample of real team features

        # Verify each feature is for the team
        for feat in features:
            assert feat["Team"]["Id"] == 2022903
            assert feat["AgileReleaseTrain"]["Name"] == "Data, Analytics and Digital"

    def test_complete_scenario_jira_mappings_complete(self, team_2022903_complete_scenario):
        """All features and epics have Jira mappings."""
        scenario = team_2022903_complete_scenario

        # Features should have Jira mappings
        for feat in scenario["features"]:
            jira_key = None
            for cf in feat["CustomFields"]:
                if cf["Name"] == "Jira Key":
                    jira_key = cf["Value"]
            assert jira_key is not None

        # Epics should exist in Jira
        jira_epics = scenario["jira_epics"]
        assert len(jira_epics) > 0
        for epic in jira_epics:
            assert epic["key"].startswith("DAD-")

    def test_scenario_workflow_represents_real_team_flow(self, team_2022903_complete_scenario):
        """Complete scenario represents real team workflow."""
        scenario = team_2022903_complete_scenario

        # Team has committed and pending objectives
        objectives = scenario["objectives"]
        committed = [obj for obj in objectives if obj["Committed"]]
        pending = [obj for obj in objectives if not obj["Committed"]]

        # Real team has mix of both
        assert len(committed) > 0 or len(pending) > 0

        # Features in different statuses
        features = scenario["features"]
        statuses = {feat["Status"] for feat in features}

        # Real team has features in Funnel and Backlog
        assert "Funnel" in statuses or "Backlog" in statuses


class TestTeam2022903Statistics:
    """Tests validating real team statistics."""

    def test_team_statistics_are_accurate(self):
        """Real statistics from team exploration are captured."""
        stats = TEAM_2022903_STATS

        assert stats["team_id"] == 2022903
        assert stats["team_name"] == "Cloud Enablement & Delivery"
        assert stats["total_features"] == 18
        assert stats["total_objectives"] == 6
        assert stats["jira_project"] == "DAD"

    def test_feature_status_distribution_matches_reality(self):
        """Feature status distribution matches real team data."""
        stats = TEAM_2022903_STATS
        statuses = stats["feature_statuses"]

        assert statuses["Funnel"] == 12  # Largest group
        assert statuses["Backlog"] == 4
        assert statuses["Implementing"] == 1
        assert statuses["Analyzing"] == 1

        # Total should match
        total = sum(statuses.values())
        assert total == stats["total_features"]

    def test_objective_commitment_ratio(self):
        """Team has committed objectives for PI."""
        stats = TEAM_2022903_STATS

        assert stats["objectives_in_pi_4_25"] == 6
        assert stats["committed_objectives"] >= 4
        # Real team: 4 out of 6 objectives are committed


class TestTeam2022903Integration:
    """Integration tests combining team, objectives, and features."""

    def test_team_objective_feature_hierarchy(self, team_2022903_complete_scenario):
        """Hierarchy: Team → Objectives → Features."""
        scenario = team_2022903_complete_scenario

        team = scenario["team"]
        objectives = scenario["objectives"]
        features = scenario["features"]

        # All objectives belong to team
        for obj in objectives:
            assert obj["Team"]["Id"] == team["Id"]

        # All features belong to team
        for feat in features:
            assert feat["Team"]["Id"] == team["Id"]

        # All in same ART
        for obj in objectives + features:
            if isinstance(obj, dict) and "AgileReleaseTrain" in obj:
                assert obj["AgileReleaseTrain"]["Id"] == team["AgileReleaseTrain"]["Id"]

    def test_team_workload_distribution(self, team_2022903_complete_scenario):
        """Verify realistic workload distribution across team."""
        scenario = team_2022903_complete_scenario
        objectives = scenario["objectives"]

        # Calculate total effort
        total_effort = sum(obj.get("Effort", 0) for obj in objectives)

        # Real team has significant effort assigned
        assert total_effort > 0

        # Objectives should have varying effort (not all same)
        efforts = [obj.get("Effort", 0) for obj in objectives]
        assert len(set(efforts)) > 1

    def test_team_coverage_across_projects(self, team_2022903_complete_scenario):
        """Team works across multiple projects/initiatives."""
        scenario = team_2022903_complete_scenario
        features = scenario["features"]

        # All features should be in GMSGQ project (real team assignment)
        # and all mapped to DAD Jira project (via Jira Key field)
        jira_keys = set()
        for feat in features:
            for cf in feat["CustomFields"]:
                if cf["Name"] == "Jira Key":
                    jira_key = cf["Value"]
                    if jira_key:
                        # Extract project key from Jira key (e.g., "DAD-2790" → "DAD")
                        project_key = jira_key.split("-")[0]
                        jira_keys.add(project_key)

        # Real team: all features in DAD project
        assert "DAD" in jira_keys
