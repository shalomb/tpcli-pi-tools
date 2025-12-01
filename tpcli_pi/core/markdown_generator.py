"""
Markdown generator for PI planning export.

Exports TargetProcess data (objectives, epics, team info) to editable
markdown files with YAML frontmatter for git-native workflows.
"""

import json
from datetime import datetime, timezone
from typing import Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FrontmatterMetadata:
    """YAML frontmatter metadata for sync tracking."""
    release: str
    team: str
    art: str
    exported_at: str
    objectives: list[dict[str, Any]]


class MarkdownGenerator:
    """
    Generate markdown files from TargetProcess PI planning data.

    Produces:
    - YAML frontmatter with metadata for sync (release, team, ART, objectives list)
    - Program objectives as read-only reference section
    - Team objectives as H2 sections with metadata (ID, Status, Effort, Owner)
    - Epics/Features as H3 subsections under objectives
    - Valid GFM syntax compatible with git workflows
    """

    def __init__(self):
        """Initialize the markdown generator."""
        pass

    def generate(
        self,
        team_name: str,
        release_name: str,
        art_name: str,
        team_objectives: list[dict[str, Any]],
        program_objectives: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        """
        Generate markdown from TargetProcess data.

        Args:
            team_name: Team name for export
            release_name: Release/PI name (e.g., "PI-4/25")
            art_name: ART name
            team_objectives: List of team objectives with epics
            program_objectives: Optional list of program objectives for reference

        Returns:
            Generated markdown string
        """
        if program_objectives is None:
            program_objectives = []

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(
            team_name, release_name, art_name, team_objectives
        )

        # Start markdown with frontmatter
        lines = [
            "---",
            self._yaml_dump(asdict(frontmatter)),
            "---",
            "",
        ]

        # Title and sync status
        lines.extend([
            f"# PI-{release_name} Plan - {team_name}",
            "",
            self._sync_status_line(),
            "",
        ])

        # Program objectives section (read-only reference)
        if program_objectives:
            lines.extend(self._program_objectives_section(program_objectives))
            lines.append("")

        # Team objectives sections
        for objective in sorted(team_objectives, key=lambda x: x.get("id", 0)):
            lines.extend(self._objective_section(objective))
            lines.append("")

        return "\n".join(lines)

    def _generate_frontmatter(
        self,
        team_name: str,
        release_name: str,
        art_name: str,
        team_objectives: list[dict[str, Any]],
    ) -> FrontmatterMetadata:
        """Generate YAML frontmatter metadata."""
        now_iso = datetime.now(timezone.utc).isoformat()

        objectives_metadata = []
        for obj in team_objectives:
            objectives_metadata.append({
                "id": obj.get("id"),
                "name": obj.get("name"),
                "synced_at": now_iso,
            })

        return FrontmatterMetadata(
            release=release_name,
            team=team_name,
            art=art_name,
            exported_at=now_iso,
            objectives=objectives_metadata,
        )

    def _sync_status_line(self) -> str:
        """Generate sync status line."""
        now = datetime.now().strftime("%Y-%m-%d")
        return f"_Sync Status: Last exported {now}._"

    def _program_objectives_section(self, program_objectives: list[dict[str, Any]]) -> list[str]:
        """Generate program objectives reference section."""
        lines = [
            "## Program Objectives (for reference/alignment)",
            "",
        ]

        for obj in program_objectives:
            name = obj.get("name", "Unnamed")
            lines.append(f"- **{name}**")

        lines.extend([
            "",
            "> These are read-only reference. Team Objectives below align to these.",
        ])

        return lines

    def _objective_section(self, objective: dict[str, Any]) -> list[str]:
        """Generate markdown section for a team objective."""
        lines = []

        # H2 header
        name = objective.get("name", "Unnamed")
        lines.append(f"## Team Objective: {name}")
        lines.append("")

        # Metadata fields
        tp_id = objective.get("id", "unknown")
        lines.append(f"**TP ID**: {tp_id}")

        status = objective.get("status", "Unknown")
        lines.append(f"**Status**: {status}")

        effort = objective.get("effort", 0)
        lines.append(f"**Effort**: {effort} points")

        owner = objective.get("owner", {})
        if isinstance(owner, dict):
            owner_name = owner.get("Name", "Unassigned")
        else:
            owner_name = str(owner) if owner else "Unassigned"
        lines.append(f"**Owner**: {owner_name}")

        # Program objective link (if present)
        program_obj = objective.get("program_objective")
        if program_obj:
            lines.append(f"**Program Objective**: {program_obj}")

        lines.append("")

        # Description section
        description = objective.get("description")
        if description:
            lines.append("### Description")
            lines.append("")
            lines.append(description)
            lines.append("")
        else:
            lines.append("### Description")
            lines.append("")

        # Epics section
        epics = objective.get("epics", [])
        for epic in sorted(epics, key=lambda x: x.get("id", 0)):
            lines.extend(self._epic_section(epic))
            lines.append("")

        return lines

    def _epic_section(self, epic: dict[str, Any]) -> list[str]:
        """
        Generate markdown section for an epic.

        Phase 2A features:
        - Jira key displayed as clickable link (US-PA-1)
        - Acceptance criteria rendered as list (US-PA-2)
        - Note directing users to Jira for story decomposition (US-PA-3)
        - Graceful handling of missing Jira keys (US-PA-4)
        """
        lines = []

        # H3 header
        name = epic.get("name", "Unnamed")
        lines.append(f"### Epic: {name}")
        lines.append("")

        # Epic metadata
        if epic.get("owner"):
            lines.append(f"**Owner**: {epic['owner']}")

        if epic.get("status"):
            lines.append(f"**Status**: {epic['status']}")

        if epic.get("effort"):
            lines.append(f"**Effort**: {epic['effort']} points")

        # US-PA-1: Jira Key as clickable link
        jira_key = epic.get("jira_key") or epic.get("JiraKey")
        if jira_key:
            jira_url = self._format_jira_url(jira_key)
            lines.append(f"**Jira Epic**: [{jira_key}]({jira_url})")

        lines.append("")

        # US-PA-2: Acceptance Criteria from TP
        acceptance_criteria = epic.get("acceptance_criteria") or epic.get("AcceptanceCriteria")
        if acceptance_criteria:
            lines.append("**Acceptance Criteria**:")
            cleaned_ac = self._clean_html(acceptance_criteria)
            for line in cleaned_ac.split('\n'):
                if line.strip():
                    lines.append(f"  - {line.strip()}")
            lines.append("")

        # US-PA-3: Note directing users to Jira for story decomposition
        if jira_key:
            lines.append(f"*For detailed story decomposition, see [Jira {jira_key}]({self._format_jira_url(jira_key)})*")
            lines.append("")

        return lines

    def _format_jira_url(self, jira_key: str) -> str:
        """
        Format Jira URL from issue key (US-PA-1).

        Args:
            jira_key: Jira issue key (e.g., "DAD-2652")

        Returns:
            Full Jira URL to Takeda Jira instance
        """
        return f"https://jira.takeda.com/browse/{jira_key}"

    def _clean_html(self, text: str) -> str:
        """
        Clean HTML from text: decode entities and strip tags (US-PA-2).

        Preserves newlines for list-based AC. Converts HTML tags to whitespace but
        maintains line breaks for proper formatting.

        Args:
            text: Text potentially containing HTML

        Returns:
            Cleaned text with HTML removed and entities decoded
        """
        if not text:
            return ""

        import re
        import html

        # Decode HTML entities (&#44; → ,, &nbsp; → space)
        text = html.unescape(text)

        # Strip HTML tags but preserve newlines (<p> → \n, etc.)
        text = re.sub(r'</p>', '\n', text)  # </p> → newline
        text = re.sub(r'<br\s*/?>', '\n', text)  # <br> → newline
        text = re.sub(r'<[^>]+>', '', text)  # Remove all remaining tags

        # Clean up excessive whitespace within lines but preserve newlines
        lines = []
        for line in text.split('\n'):
            # Collapse multiple spaces within each line
            cleaned_line = re.sub(r'\s+', ' ', line).strip()
            if cleaned_line:
                lines.append(cleaned_line)

        return '\n'.join(lines)

    def _yaml_dump(self, data: dict[str, Any]) -> str:
        """Simple YAML dump for frontmatter."""
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append("  - " + json.dumps(item))
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, str):
                # Quote strings for YAML safety
                lines.append(f'{key}: "{value}"')
            elif isinstance(value, (int, float)):
                lines.append(f"{key}: {value}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def get_filename(self, team_name: str, release_name: str) -> str:
        """
        Generate safe filename for markdown export.

        Args:
            team_name: Team name
            release_name: Release name

        Returns:
            Safe filename with .md extension
        """
        # Normalize names for filename (lowercase, replace spaces with underscores)
        team_normalized = team_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        release_normalized = release_name.lower().replace("/", "-")

        # Remove special characters
        import re
        team_normalized = re.sub(r"[^a-z0-9-]", "", team_normalized)
        release_normalized = re.sub(r"[^a-z0-9-]", "", release_normalized)

        return f"{release_normalized}-{team_normalized}.md"
