"""Analysis logic for capacity, risks, and dependencies."""

from typing import Dict, List, Optional, Set

from tpcli_pi.models.analysis import (
    CapacityAnalysis,
    DependencyMapping,
    DependencyType,
    RiskAssessment,
    RiskCategory,
    RiskItem,
    RiskLevel,
)
from tpcli_pi.models.entities import (
    Feature,
    PIObjective,
    Team,
    TeamPIObjective,
)


class CapacityAnalyzer:
    """Analyze team capacity vs. commitments."""

    @staticmethod
    def analyze_team_capacity(
        team: Team, objectives: List[TeamPIObjective]
    ) -> CapacityAnalysis:
        """
        Analyze team capacity utilization.

        Args:
            team: Team to analyze
            objectives: Team's committed PI objectives

        Returns:
            CapacityAnalysis with utilization metrics and risk flags
        """
        # Calculate total effort committed
        total_effort_committed = sum(obj.effort for obj in objectives)

        # Estimate available capacity (assume 80 story points per team member per PI)
        # This is a placeholder; could be configured or pulled from TargetProcess
        estimated_effort_per_person = 80
        total_effort_available = team.member_count * estimated_effort_per_person

        analysis = CapacityAnalysis(
            team=team,
            total_effort_available=total_effort_available,
            total_effort_committed=total_effort_committed,
            team_members=team.member_count,
        )

        # Generate per-person effort estimate (naive distribution)
        if team.member_count > 0:
            effort_per_person_estimate = total_effort_committed / team.member_count
            for i in range(team.member_count):
                member_name = f"Member {i + 1}"
                analysis.effort_per_person[member_name] = int(
                    effort_per_person_estimate
                )

                # Flag if individual is overcommitted
                if effort_per_person_estimate > estimated_effort_per_person:
                    analysis.overcommitted_members.append(member_name)

        return analysis


class RiskAnalyzer:
    """Identify and assess risks in PI planning."""

    # Risk scoring thresholds
    EFFORT_ESTIMATION_THRESHOLD = 5  # Flag objectives with effort < this
    DEPENDENCY_PENALTY = 10  # Risk points per blocking dependency

    @staticmethod
    def assess_objective(
        objective: PIObjective,
        all_objectives: List[PIObjective],
        features: Optional[List[Feature]] = None,
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment of a PI objective.

        Args:
            objective: Objective to assess
            all_objectives: All objectives for dependency analysis
            features: Linked features/work items

        Returns:
            RiskAssessment with identified risks and recommendations
        """
        assessment = RiskAssessment(
            subject_id=objective.id,
            subject_type="Objective",
            subject_name=objective.name,
        )

        # Check for estimation risks
        RiskAnalyzer._check_estimation_risks(objective, assessment)

        # Check for feature/work item risks
        if features:
            RiskAnalyzer._check_feature_risks(features, assessment)

        # Check for dependency risks (simple implementation for now)
        RiskAnalyzer._check_dependency_risks(objective, all_objectives, assessment)

        # Generate recommendations based on identified risks
        RiskAnalyzer._generate_recommendations(assessment)

        return assessment

    @staticmethod
    def assess_team(
        team: Team,
        objectives: List[TeamPIObjective],
        all_objectives: List[PIObjective],
        features: Optional[List[Feature]] = None,
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment of a team.

        Args:
            team: Team to assess
            objectives: Team's committed objectives
            all_objectives: All objectives for dependency analysis
            features: Linked features/work items

        Returns:
            RiskAssessment with team-level risks and recommendations
        """
        assessment = RiskAssessment(
            subject_id=team.id,
            subject_type="Team",
            subject_name=team.name,
        )

        # Aggregate risks from all team objectives
        for objective in objectives:
            obj_assessment = RiskAnalyzer.assess_objective(
                objective, all_objectives, features
            )
            assessment.identified_risks.extend(obj_assessment.identified_risks)
            assessment.dependencies.extend(obj_assessment.dependencies)
            assessment.blocking_dependencies.extend(
                obj_assessment.blocking_dependencies
            )

        # Check for team-level risks
        if len(objectives) == 0:
            assessment.identified_risks.append(
                RiskItem(
                    id="TEAM-001",
                    title="No objectives committed",
                    category=RiskCategory.RESOURCE,
                    level=RiskLevel.MEDIUM,
                    description="Team has no committed PI objectives. Unclear scope and expectations.",
                )
            )

        if len(objectives) > 5 * team.member_count and team.member_count > 0:
            assessment.identified_risks.append(
                RiskItem(
                    id="TEAM-002",
                    title="High objective-to-person ratio",
                    category=RiskCategory.CAPACITY,
                    level=RiskLevel.HIGH,
                    description=f"Team has {len(objectives)} objectives for {team.member_count} members. "
                    f"Ratio of {len(objectives) / team.member_count:.1f} objectives per person may indicate overcommitment.",
                )
            )

        # Generate recommendations based on identified risks
        RiskAnalyzer._generate_recommendations(assessment)

        return assessment

    @staticmethod
    def _check_estimation_risks(
        objective: PIObjective, assessment: RiskAssessment
    ) -> None:
        """Check for risks related to effort estimation."""
        if objective.effort == 0:
            assessment.identified_risks.append(
                RiskItem(
                    id=f"EST-{objective.id}",
                    title="Missing effort estimation",
                    category=RiskCategory.ESTIMATION,
                    level=RiskLevel.HIGH,
                    description="Objective has no effort estimate. Cannot assess team capacity or schedule feasibility.",
                    status="Open",
                )
            )
        elif objective.effort < RiskAnalyzer.EFFORT_ESTIMATION_THRESHOLD:
            assessment.identified_risks.append(
                RiskItem(
                    id=f"EST-{objective.id}-LOW",
                    title="Unusually low effort estimate",
                    category=RiskCategory.ESTIMATION,
                    level=RiskLevel.MEDIUM,
                    description=f"Objective effort ({objective.effort} points) is very low. May indicate incomplete breakdown or underestimation.",
                    status="Open",
                )
            )

    @staticmethod
    def _check_feature_risks(
        features: List[Feature], assessment: RiskAssessment
    ) -> None:
        """Check for risks in linked features/work items."""
        unstarted_features = [
            f for f in features if f.status not in ["In Progress", "Done"]
        ]
        features_without_owner = [f for f in features if f.owner is None]
        features_without_effort = [f for f in features if f.effort == 0]

        if len(unstarted_features) > len(features) * 0.7:
            assessment.identified_risks.append(
                RiskItem(
                    id=f"FEAT-{assessment.subject_id}",
                    title="High proportion of unstarted work",
                    category=RiskCategory.SCHEDULE,
                    level=RiskLevel.HIGH,
                    description=f"{len(unstarted_features)} of {len(features)} features not started. "
                    "May indicate schedule risk or scope that's not ready.",
                    status="Open",
                )
            )

        if len(features_without_owner) > 0:
            assessment.identified_risks.append(
                RiskItem(
                    id=f"OWN-{assessment.subject_id}",
                    title="Features without assigned owners",
                    category=RiskCategory.RESOURCE,
                    level=RiskLevel.MEDIUM,
                    description=f"{len(features_without_owner)} features lack assigned owners. "
                    "Unclear accountability may cause delays.",
                    status="Open",
                )
            )

        if len(features_without_effort) > 0:
            assessment.identified_risks.append(
                RiskItem(
                    id=f"EFFO-{assessment.subject_id}",
                    title="Features without effort estimates",
                    category=RiskCategory.ESTIMATION,
                    level=RiskLevel.HIGH,
                    description=f"{len(features_without_effort)} features lack effort estimates. "
                    "Cannot assess capacity or schedule.",
                    status="Open",
                )
            )

    @staticmethod
    def _check_dependency_risks(
        objective: PIObjective,
        all_objectives: List[PIObjective],
        assessment: RiskAssessment,
    ) -> None:
        """Check for risks related to dependencies (placeholder implementation)."""
        # This is a simplified implementation
        # In a full implementation, you would:
        # 1. Query TargetProcess for explicit dependency links
        # 2. Analyze naming patterns for implicit dependencies
        # 3. Check for circular dependencies
        # 4. Assess cross-team/cross-ART dependencies

        # For now, we'll look for objectives with similar names as a heuristic
        similar_objectives = [
            o
            for o in all_objectives
            if o.id != objective.id
            and any(
                keyword in objective.name.lower()
                for keyword in o.name.lower().split()
                if len(keyword) > 3
            )
        ]

        if len(similar_objectives) > 0:
            for similar in similar_objectives[:3]:  # Limit to top 3
                assessment.dependencies.append(
                    DependencyMapping(
                        source_objective_id=objective.id,
                        source_objective_name=objective.name,
                        target_objective_id=similar.id,
                        target_objective_name=similar.name,
                        dependency_type=DependencyType.RELATED,
                        criticality="Low",
                        notes="Heuristic: Similar objective names",
                    )
                )

    @staticmethod
    def _generate_recommendations(assessment: RiskAssessment) -> None:
        """Generate recommendations based on identified risks."""
        # Existing recommendations from RiskAssessment.__post_init__
        # are already auto-generated based on risk counts

        # Add additional contextual recommendations
        if assessment.health_score < 50:
            assessment.recommendations.append(
                f"WARNING: Health score {assessment.health_score:.0f}/100. "
                "Consider deferring lower-priority work to free capacity for risk mitigation."
            )

        if len(assessment.blocking_dependencies) > 0:
            assessment.recommendations.append(
                "DEPENDENCIES: Establish regular sync with dependent teams. "
                "Consider early delivery/integration of blocking items."
            )

        if assessment.subject_type == "Team":
            assessment.recommendations.append(
                "NEXT STEPS: Review this assessment with the team during planning. "
                "Create mitigation plans for HIGH/CRITICAL risks. "
                "Track risks throughout the PI."
            )


class DependencyAnalyzer:
    """Analyze dependencies between objectives and teams."""

    @staticmethod
    def map_dependencies(
        objectives: List[PIObjective], build_graph: bool = False
    ) -> List[DependencyMapping]:
        """
        Map dependencies between objectives.

        Args:
            objectives: All objectives to analyze
            build_graph: If True, analyze for circular dependencies

        Returns:
            List of dependency mappings
        """
        dependencies: List[DependencyMapping] = []

        # This is a placeholder implementation
        # In a full implementation, you would:
        # 1. Query TargetProcess CustomLinks for explicit dependencies
        # 2. Analyze time-based dependencies (end_date of one <= start_date of another)
        # 3. Detect cross-team and cross-ART dependencies
        # 4. Build dependency graph and detect cycles

        return dependencies

    @staticmethod
    def find_critical_path(
        objectives: List[PIObjective], dependencies: List[DependencyMapping]
    ) -> List[PIObjective]:
        """
        Find critical path through objectives.

        Args:
            objectives: All objectives
            dependencies: All dependencies

        Returns:
            List of objectives in critical path (in execution order)
        """
        # This is a placeholder implementation
        # In a full implementation, you would use graph algorithms
        # (topological sort, critical path method) to identify
        # the longest dependent chain

        return objectives[:3]  # Placeholder


class MetricsCalculator:
    """Calculate metrics for reporting and analysis."""

    @staticmethod
    def calculate_team_velocity(
        team: Team, historical_objectives: List[PIObjective]
    ) -> float:
        """
        Calculate team velocity (avg points completed per PI).

        Args:
            team: Team to analyze
            historical_objectives: Completed objectives from previous PIs

        Returns:
            Average story points completed per PI
        """
        # This is a placeholder
        # In a full implementation, you would:
        # 1. Query historical objectives by status and dates
        # 2. Calculate actual effort completed per past PI
        # 3. Return moving average (e.g., last 3 PIs)

        return 0.0

    @staticmethod
    def calculate_burndown_rate(
        objectives: List[PIObjective],
        current_progress_pct: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculate expected burndown rate for PI.

        Args:
            objectives: Current PI objectives
            current_progress_pct: Current progress (0-100)

        Returns:
            Dictionary with burndown metrics
        """
        total_effort = sum(obj.effort for obj in objectives)
        completed_effort = int(total_effort * (current_progress_pct / 100))

        return {
            "total_effort": float(total_effort),
            "completed_effort": float(completed_effort),
            "remaining_effort": float(total_effort - completed_effort),
            "completion_percentage": current_progress_pct,
        }
