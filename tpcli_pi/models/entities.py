"""TargetProcess entity models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EntityStatus(str, Enum):
    """Status of an entity."""

    PENDING = "Pending"
    ACCEPTED = "Accepted"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    DRAFT = "Draft"


@dataclass
class User:
    """Represents a TargetProcess user."""

    id: int
    first_name: str
    last_name: str
    email: str
    full_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.full_name = f"{self.first_name} {self.last_name}"


@dataclass
class Team:
    """Represents a TargetProcess team."""

    id: int
    name: str
    owner: User | None = None
    member_count: int = 0
    is_active: bool = True
    art_id: int | None = None
    art_name: str | None = None


@dataclass
class AgileReleaseTrain:
    """Represents an Agile Release Train (ART)."""

    id: int
    name: str
    teams: list[Team] = field(default_factory=list)


@dataclass
class Release:
    """Represents a Release/PI."""

    id: int
    name: str
    start_date: datetime
    end_date: datetime
    art_id: int
    art_name: str
    is_current: bool = False

    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in release."""
        today = datetime.now().date()
        end = self.end_date.date()
        remaining = (end - today).days
        return max(0, remaining)

    @property
    def is_in_progress(self) -> bool:
        """Check if release is currently active."""
        today = datetime.now().date()
        return self.start_date.date() <= today <= self.end_date.date()

    @property
    def duration_days(self) -> int:
        """Calculate total days in release."""
        return (self.end_date.date() - self.start_date.date()).days


@dataclass
class PIObjective:
    """Base class for PI objectives."""

    id: int
    name: str
    status: EntityStatus
    owner: User | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    release_id: int | None = None
    release_name: str | None = None
    effort: int = 0
    created_date: datetime | None = None
    created_by: User | None = None


@dataclass
class ProgramPIObjective(PIObjective):
    """Represents a Program-level PI Objective."""

    art_id: int | None = None
    art_name: str | None = None


@dataclass
class TeamPIObjective(PIObjective):
    """Represents a Team-level PI Objective."""

    team_id: int | None = None
    team_name: str | None = None
    committed: bool = False
    program_objective_id: int | None = None


@dataclass
class Feature:
    """Represents a Feature in TargetProcess."""

    id: int
    name: str
    status: EntityStatus
    effort: int = 0
    owner: User | None = None
    team: Team | None = None
    release_id: int | None = None
    release_name: str | None = None
    parent_epic_id: int | None = None
    parent_epic_name: str | None = None
    description: str | None = None
    created_date: datetime | None = None
