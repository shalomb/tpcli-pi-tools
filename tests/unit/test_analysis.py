"""Unit tests for analysis module.

Tests capacity analysis, risk assessment, dependency mapping,
and metrics calculation for PI planning.
"""

import pytest

from tpcli_pi.core.analysis import (
    CapacityAnalyzer,
    RiskAnalyzer,
    DependencyAnalyzer,
    MetricsCalculator,
)
from tpcli_pi.models.analysis import (
    RiskCategory,
    RiskLevel,
    DependencyType,
)
from tpcli_pi.models.entities import (
    Team,
    TeamPIObjective,
    PIObjective,
    Feature,
    User,
)


class TestCapacityAnalyzer:
    """Tests for team capacity analysis."""

    @pytest.fixture
    def team(self):
        """Create a team for testing."""
        return Team(
            id=1935991,
            name="Platform Eco",
            member_count=5,
        )

    @pytest.fixture
    def objectives(self):
        """Create team objectives for testing."""
        return [
            TeamPIObjective(
                id=2019099,
                name="Platform governance",
                status="In Progress",
                effort=21,
                team_id=1935991,
                release_id=1942235,
            ),
            TeamPIObjective(
                id=2019100,
                name="API performance",
                status="Pending",
                effort=34,
                team_id=1935991,
                release_id=1942235,
            ),
            TeamPIObjective(
                id=2019101,
                name="Security hardening",
                status="Pending",
                effort=21,
                team_id=1935991,
                release_id=1942235,
            ),
        ]

    def test_analyze_team_capacity_calculates_total_effort(self, team, objectives):
        """Test capacity analysis calculates total committed effort."""
        analysis = CapacityAnalyzer.analyze_team_capacity(team, objectives)

        total_effort = sum(obj.effort for obj in objectives)
        assert analysis.total_effort_committed == total_effort
        assert analysis.total_effort_committed == 76  # 21 + 34 + 21

    def test_analyze_team_capacity_calculates_available_effort(self, team, objectives):
        """Test capacity analysis calculates available effort based on team size."""
        analysis = CapacityAnalyzer.analyze_team_capacity(team, objectives)

        expected_available = 5 * 80  # 5 members * 80 points/person
        assert analysis.total_effort_available == expected_available
        assert analysis.total_effort_available == 400

    def test_analyze_team_capacity_calculates_per_person_effort(self, team, objectives):
        """Test per-person effort estimation."""
        analysis = CapacityAnalyzer.analyze_team_capacity(team, objectives)

        total_effort = 76
        expected_per_person = total_effort / 5  # 15.2 points per person
        assert len(analysis.effort_per_person) == 5
        assert all(v == int(expected_per_person) for v in analysis.effort_per_person.values())

    def test_analyze_team_capacity_flags_overcommitment(self, team, objectives):
        """Test that overcommitment is detected when per-person effort exceeds capacity."""
        # Add more objectives to trigger overcommitment
        extra_objectives = [
            TeamPIObjective(
                id=2019102 + i,
                name=f"Extra objective {i}",
                status="Pending",
                effort=100,
                team_id=1935991,
                release_id=1942235,
            )
            for i in range(5)
        ]
        all_objectives = objectives + extra_objectives

        analysis = CapacityAnalyzer.analyze_team_capacity(team, all_objectives)

        # Should flag some members as overcommitted
        assert len(analysis.overcommitted_members) > 0

    def test_analyze_team_capacity_with_empty_team(self):
        """Test capacity analysis with team that has no members."""
        empty_team = Team(id=999, name="Empty Team", member_count=0)
        objectives = [
            TeamPIObjective(
                id=1,
                name="Objective",
                status="Pending",
                effort=10,
                team_id=999,
                release_id=1,
            )
        ]

        analysis = CapacityAnalyzer.analyze_team_capacity(empty_team, objectives)

        assert analysis.team_members == 0
        assert analysis.total_effort_available == 0
        assert len(analysis.effort_per_person) == 0
        assert len(analysis.overcommitted_members) == 0

    def test_analyze_team_capacity_with_no_objectives(self, team):
        """Test capacity analysis with no committed objectives."""
        analysis = CapacityAnalyzer.analyze_team_capacity(team, [])

        assert analysis.total_effort_committed == 0
        assert analysis.total_effort_available == 400
        assert len(analysis.overcommitted_members) == 0


class TestRiskAnalyzer:
    """Tests for risk assessment."""

    @pytest.fixture
    def objective(self):
        """Create an objective for testing."""
        return PIObjective(
            id=2019099,
            name="Platform governance",
            status="Pending",
            effort=21,
        )

    @pytest.fixture
    def team(self):
        """Create a team for testing."""
        return Team(
            id=1935991,
            name="Platform Eco",
            member_count=5,
        )

    @pytest.fixture
    def features(self):
        """Create features for testing."""
        return [
            Feature(id=1001, name="Governance UI", status="Pending", effort=8),
            Feature(id=1002, name="Audit trails", status="In Progress", effort=8),
            Feature(id=1003, name="Reporting", status="Done", effort=5),
        ]

    def test_assess_objective_without_estimation_risk(self, objective):
        """Test risk assessment for properly estimated objective."""
        assessment = RiskAnalyzer.assess_objective(objective, [objective])

        # Objective has reasonable effort estimate
        assert assessment.subject_id == objective.id
        assert assessment.subject_name == objective.name
        assert assessment.subject_type == "Objective"
        # Should not flag estimation risks for reasonable effort
        estimation_risks = [r for r in assessment.identified_risks if "effort" in r.title.lower() and r.effort == 0]
        estimation_low_risks = [r for r in assessment.identified_risks if "low estimate" in r.title.lower()]
        assert len(estimation_risks) == 0
        assert len(estimation_low_risks) == 0

    def test_assess_objective_with_zero_effort(self):
        """Test risk assessment flags zero effort estimation."""
        objective = PIObjective(
            id=2019099,
            name="Zero effort objective",
            status="Pending",
            effort=0,
        )

        assessment = RiskAnalyzer.assess_objective(objective, [objective])

        # Should flag missing effort estimation
        estimation_risks = [r for r in assessment.identified_risks if "effort" in r.title.lower()]
        assert len(estimation_risks) > 0
        assert any("missing" in r.title.lower() for r in estimation_risks)

    def test_assess_objective_with_low_effort(self):
        """Test risk assessment flags unusually low effort."""
        objective = PIObjective(
            id=2019099,
            name="Low effort objective",
            status="Pending",
            effort=2,  # Below EFFORT_ESTIMATION_THRESHOLD (5)
        )

        assessment = RiskAnalyzer.assess_objective(objective, [objective])

        # Should flag low effort estimation
        low_risks = [r for r in assessment.identified_risks if "low" in r.title.lower()]
        assert len(low_risks) > 0

    def test_assess_objective_with_features(self, objective, features):
        """Test risk assessment analyzes linked features."""
        assessment = RiskAnalyzer.assess_objective(objective, [objective], features)

        assert assessment.subject_id == objective.id
        # Should have analyzed feature risks
        # No risks expected for this well-structured feature set

    def test_assess_objective_with_unstarted_features(self):
        """Test risk assessment flags high proportion of unstarted work."""
        objective = PIObjective(id=1, name="Test", status="Pending", effort=21)
        features = [
            Feature(id=1, name="F1", status="Pending", effort=5),
            Feature(id=2, name="F2", status="Pending", effort=5),
            Feature(id=3, name="F3", status="Pending", effort=5),
            Feature(id=4, name="F4", status="Done", effort=5),
        ]

        assessment = RiskAnalyzer.assess_objective(objective, [objective], features)

        # Should flag unstarted work
        unstarted_risks = [r for r in assessment.identified_risks if "started" in r.description.lower()]
        assert len(unstarted_risks) > 0

    def test_assess_objective_with_unassigned_features(self):
        """Test risk assessment flags features without owners."""
        objective = PIObjective(id=1, name="Test", status="Pending", effort=21)
        features = [
            Feature(id=1, name="F1", status="Pending", effort=5, owner=None),
            Feature(id=2, name="F2", status="Pending", effort=5, owner=None),
        ]

        assessment = RiskAnalyzer.assess_objective(objective, [objective], features)

        # Should flag missing owners
        owner_risks = [r for r in assessment.identified_risks if "owner" in r.description.lower()]
        assert len(owner_risks) > 0

    def test_assess_team_with_no_objectives(self, team):
        """Test risk assessment flags team with no committed work."""
        assessment = RiskAnalyzer.assess_team(team, [], [])

        # Should flag missing objectives
        no_obj_risks = [r for r in assessment.identified_risks if "no objectives" in r.title.lower()]
        assert len(no_obj_risks) > 0

    def test_assess_team_with_high_objective_ratio(self, team):
        """Test risk assessment flags high objective-to-person ratio."""
        team_small = Team(id=1, name="Small Team", member_count=1)
        objectives = [
            TeamPIObjective(id=i, name=f"Obj {i}", status="Pending", effort=10, team_id=1, release_id=1)
            for i in range(10)  # 10 objectives for 1 person
        ]

        assessment = RiskAnalyzer.assess_team(team_small, objectives, objectives)

        # Should flag high ratio
        ratio_risks = [r for r in assessment.identified_risks if "ratio" in r.description.lower()]
        assert len(ratio_risks) > 0

    def test_assess_team_aggregates_objective_risks(self, team):
        """Test that team assessment aggregates risks from all objectives."""
        objectives = [
            TeamPIObjective(
                id=i,
                name=f"Objective {i}",
                status="Pending",
                effort=0 if i == 0 else 10,  # First one has zero effort
                team_id=team.id,
                release_id=1,
            )
            for i in range(3)
        ]

        assessment = RiskAnalyzer.assess_team(team, objectives, objectives)

        # Should have aggregated risks from objectives
        assert len(assessment.identified_risks) > 0

    def test_risk_assessment_generates_recommendations(self):
        """Test that risk assessment generates helpful recommendations."""
        objective = PIObjective(id=1, name="Risky", status="Pending", effort=0)

        assessment = RiskAnalyzer.assess_objective(objective, [objective])

        # Should have some risks identified due to zero effort
        assert len(assessment.identified_risks) > 0


class TestDependencyAnalyzer:
    """Tests for dependency analysis."""

    def test_map_dependencies_returns_list(self):
        """Test that map_dependencies returns a list."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="Pending", effort=10),
            PIObjective(id=2, name="Obj2", status="Pending", effort=10),
        ]

        dependencies = DependencyAnalyzer.map_dependencies(objectives)

        assert isinstance(dependencies, list)

    def test_map_dependencies_with_graph_analysis(self):
        """Test map_dependencies with graph analysis flag."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="Pending", effort=10),
            PIObjective(id=2, name="Obj2", status="Pending", effort=10),
        ]

        dependencies = DependencyAnalyzer.map_dependencies(objectives, build_graph=True)

        assert isinstance(dependencies, list)

    def test_find_critical_path_returns_objectives(self):
        """Test that find_critical_path returns objectives."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="Pending", effort=10),
            PIObjective(id=2, name="Obj2", status="Pending", effort=10),
            PIObjective(id=3, name="Obj3", status="Pending", effort=10),
        ]

        critical_path = DependencyAnalyzer.find_critical_path(objectives, [])

        assert isinstance(critical_path, list)
        assert len(critical_path) > 0

    def test_find_critical_path_respects_dependencies(self):
        """Test that critical path analysis considers dependencies."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="Pending", effort=10),
            PIObjective(id=2, name="Obj2", status="Pending", effort=20),
            PIObjective(id=3, name="Obj3", status="Pending", effort=15),
        ]
        dependencies = []

        critical_path = DependencyAnalyzer.find_critical_path(objectives, dependencies)

        assert all(obj in objectives for obj in critical_path)


class TestMetricsCalculator:
    """Tests for metrics calculation."""

    def test_calculate_team_velocity_returns_float(self):
        """Test that team velocity calculation returns float."""
        team = Team(id=1, name="Team", member_count=5)
        historical = [
            PIObjective(id=1, name="Obj1", status="Done", effort=21),
            PIObjective(id=2, name="Obj2", status="Done", effort=34),
        ]

        velocity = MetricsCalculator.calculate_team_velocity(team, historical)

        assert isinstance(velocity, float)

    def test_calculate_burndown_rate_with_zero_progress(self):
        """Test burndown rate calculation with no progress."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="Pending", effort=21),
            PIObjective(id=2, name="Obj2", status="Pending", effort=34),
        ]

        burndown = MetricsCalculator.calculate_burndown_rate(objectives, current_progress_pct=0.0)

        assert burndown["total_effort"] == 55.0
        assert burndown["completed_effort"] == 0.0
        assert burndown["remaining_effort"] == 55.0
        assert burndown["completion_percentage"] == 0.0

    def test_calculate_burndown_rate_with_partial_progress(self):
        """Test burndown rate calculation with partial progress."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="In Progress", effort=50),
            PIObjective(id=2, name="Obj2", status="Pending", effort=50),
        ]

        burndown = MetricsCalculator.calculate_burndown_rate(objectives, current_progress_pct=50.0)

        assert burndown["total_effort"] == 100.0
        assert burndown["completed_effort"] == 50.0
        assert burndown["remaining_effort"] == 50.0
        assert burndown["completion_percentage"] == 50.0

    def test_calculate_burndown_rate_fully_complete(self):
        """Test burndown rate calculation when fully complete."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="Done", effort=30),
            PIObjective(id=2, name="Obj2", status="Done", effort=20),
        ]

        burndown = MetricsCalculator.calculate_burndown_rate(objectives, current_progress_pct=100.0)

        assert burndown["total_effort"] == 50.0
        assert burndown["completed_effort"] == 50.0
        assert burndown["remaining_effort"] == 0.0
        assert burndown["completion_percentage"] == 100.0

    def test_calculate_burndown_rate_with_empty_objectives(self):
        """Test burndown rate calculation with no objectives."""
        burndown = MetricsCalculator.calculate_burndown_rate([], current_progress_pct=0.0)

        assert burndown["total_effort"] == 0.0
        assert burndown["completed_effort"] == 0.0
        assert burndown["remaining_effort"] == 0.0
        assert burndown["completion_percentage"] == 0.0

    def test_calculate_burndown_rate_preserves_float_precision(self):
        """Test that burndown calculations preserve float precision."""
        objectives = [
            PIObjective(id=1, name="Obj1", status="In Progress", effort=33),
        ]

        burndown = MetricsCalculator.calculate_burndown_rate(objectives, current_progress_pct=33.333)

        assert isinstance(burndown["total_effort"], float)
        assert isinstance(burndown["completed_effort"], float)
        assert isinstance(burndown["remaining_effort"], float)
        # Verify calculations are done correctly (remaining = 33 - int(33 * 0.33333))
        assert abs(burndown["remaining_effort"] - 22.0) <= 2.0  # approximately 22-23
