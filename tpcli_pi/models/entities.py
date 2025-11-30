"""TargetProcess entity models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
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
    owner: Optional[User] = None
    member_count: int = 0
    is_active: bool = True
    art_id: Optional[int] = None
    art_name: Optional[str] = None


@dataclass
class AgileReleaseTrain:
    """Represents an Agile Release Train (ART)."""

    id: int
    name: str
    teams: List[Team] = field(default_factory=list)


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
    owner: Optional[User] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    release_id: Optional[int] = None
    release_name: Optional[str] = None
    effort: int = 0
    created_date: Optional[datetime] = None
    created_by: Optional[User] = None


@dataclass
class ProgramPIObjective(PIObjective):
    """Represents a Program-level PI Objective."""

    art_id: Optional[int] = None
    art_name: Optional[str] = None


@dataclass
class TeamPIObjective(PIObjective):
    """Represents a Team-level PI Objective."""

    team_id: Optional[int] = None
    team_name: Optional[str] = None
    committed: bool = False
    program_objective_id: Optional[int] = None


@dataclass
class Feature:
    """Represents a Feature in TargetProcess."""

    id: int
    name: str
    status: EntityStatus
    effort: int = 0
    owner: Optional[User] = None
    team: Optional[Team] = None
    release_id: Optional[int] = None
    release_name: Optional[str] = None
    parent_epic_id: Optional[int] = None
    parent_epic_name: Optional[str] = None
    description: Optional[str] = None
    created_date: Optional[datetime] = None
