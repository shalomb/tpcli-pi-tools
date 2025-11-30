"""Analysis result models for PI planning insights."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .entities import User, Team, PIObjective


class RiskLevel(str, Enum):
    """Risk severity levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskCategory(str, Enum):
    """Categories of risks identified."""

    TECHNICAL = "Technical"
    SCHEDULE = "Schedule"
    RESOURCE = "Resource"
    DEPENDENCY = "Dependency"
    COMPLIANCE = "Compliance"
    CAPACITY = "Capacity"
    SKILLS = "Skills"
    ESTIMATION = "Estimation"


class DependencyType(str, Enum):
    """Types of dependencies between objectives."""

    BLOCKS = "Blocks"
    BLOCKED_BY = "Blocked By"
    RELATED = "Related"
    DUPLICATES = "Duplicates"
    DUPLICATED_BY = "Duplicated By"


@dataclass
class RiskItem:
    """Represents a single risk identified in analysis."""

    id: str
    title: str
    category: RiskCategory
    level: RiskLevel
    description: str
    owner: Optional[User] = None
    mitigations: List[str] = field(default_factory=list)
    created_date: Optional[datetime] = None
    target_resolution_date: Optional[datetime] = None
    status: str = "Open"  # Open, In Mitigation, Closed, Accepted


@dataclass
class DependencyMapping:
    """Represents a dependency relationship between two objectives."""

    source_objective_id: int
    source_objective_name: str
    target_objective_id: int
    target_objective_name: str
    dependency_type: DependencyType
    is_cross_team: bool = False
    is_cross_art: bool = False
    criticality: str = "Medium"  # Low, Medium, High
    notes: Optional[str] = None


@dataclass
class CapacityAnalysis:
    """Analysis of team capacity vs. commitments."""

    team: Team
    total_effort_available: int  # Story points or person-days
    total_effort_committed: int  # Effort in objectives
    total_effort_remaining: int = field(init=False)
    capacity_utilization_percent: float = field(init=False)
    is_overcommitted: bool = field(init=False)
    available_capacity_percent: float = field(init=False)

    # Per-person breakdown
    team_members: int = 0
    effort_per_person: Dict[str, int] = field(default_factory=dict)
    overcommitted_members: List[str] = field(default_factory=list)

    # Risk flags
    risk_flags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.total_effort_remaining = self.total_effort_available - self.total_effort_committed
        if self.total_effort_available > 0:
            self.capacity_utilization_percent = (
                self.total_effort_committed / self.total_effort_available
            ) * 100
            self.available_capacity_percent = 100 - self.capacity_utilization_percent
        else:
            self.capacity_utilization_percent = 0
            self.available_capacity_percent = 0

        self.is_overcommitted = self.total_effort_committed > self.total_effort_available

        # Auto-flag risks
        if self.is_overcommitted:
            self.risk_flags.append("Team is overcommitted")
        if self.capacity_utilization_percent > 90:
            self.risk_flags.append("Team at high capacity (>90%)")
        if self.team_members == 0:
            self.risk_flags.append("No team members defined")
        if len(self.overcommitted_members) > 0:
            self.risk_flags.append(f"{len(self.overcommitted_members)} team members overloaded")


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment for a PI objective or team."""

    subject_id: int
    subject_type: str  # "Objective", "Team", "Release"
    subject_name: str
    assessment_date: datetime = field(default_factory=datetime.now)

    # Risk items
    identified_risks: List[RiskItem] = field(default_factory=list)

    # Dependencies
    dependencies: List[DependencyMapping] = field(default_factory=list)
    blocking_dependencies: List[DependencyMapping] = field(default_factory=list)
    blocked_by_dependencies: List[DependencyMapping] = field(default_factory=list)
    critical_path_items: List[DependencyMapping] = field(default_factory=list)

    # Metrics
    total_risk_count: int = field(init=False)
    critical_risk_count: int = field(init=False)
    high_risk_count: int = field(init=False)
    medium_risk_count: int = field(init=False)
    low_risk_count: int = field(init=False)
    health_score: float = field(init=False)  # 0-100, lower is worse

    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    escalation_required: bool = field(init=False)

    def __post_init__(self) -> None:
        self.total_risk_count = len(self.identified_risks)
        self.critical_risk_count = sum(
            1 for r in self.identified_risks if r.level == RiskLevel.CRITICAL
        )
        self.high_risk_count = sum(1 for r in self.identified_risks if r.level == RiskLevel.HIGH)
        self.medium_risk_count = sum(
            1 for r in self.identified_risks if r.level == RiskLevel.MEDIUM
        )
        self.low_risk_count = sum(1 for r in self.identified_risks if r.level == RiskLevel.LOW)

        # Calculate health score: 100 = no risks, decreases with risk severity
        health_score = 100.0
        health_score -= self.critical_risk_count * 25  # Critical = -25 each
        health_score -= self.high_risk_count * 15  # High = -15 each
        health_score -= self.medium_risk_count * 5  # Medium = -5 each
        health_score -= self.low_risk_count * 2  # Low = -2 each
        self.health_score = max(0.0, health_score)

        # Determine if escalation needed
        self.escalation_required = (
            self.critical_risk_count > 0 or self.high_risk_count > 2 or self.health_score < 30
        )

        # Auto-generate recommendations based on risks
        if self.critical_risk_count > 0:
            self.recommendations.append(
                "CRITICAL: Escalate immediately. Critical risks must be addressed before PI."
            )
        if self.high_risk_count > 0:
            self.recommendations.append(
                f"HIGH: {self.high_risk_count} high-severity risks identified. "
                "Create mitigation plans and track closely."
            )
        if len(self.blocking_dependencies) > 0:
            self.recommendations.append(
                f"DEPENDENCIES: {len(self.blocking_dependencies)} blocking dependencies identified. "
                "Coordinate with dependent teams early."
            )
