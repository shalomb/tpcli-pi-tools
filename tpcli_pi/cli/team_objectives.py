"""Team Objectives CLI command - List team commitments for a PI."""

import sys
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.config import get_default_art

console = Console()


def format_date(dt: datetime | None) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d")


def format_status(status) -> Text:
    """Return colored status text."""
    status_str = status.value if hasattr(status, "value") else str(status)

    if status_str in ("Open", "Planned", "In Progress"):
        return Text(status_str, style="green")
    elif status_str in ("Done", "Completed", "Closed"):
        return Text(status_str, style="blue")
    else:
        return Text(status_str, style="yellow")


def format_commitment(committed: bool) -> Text:
    """Format commitment status."""
    if committed:
        return Text("✓ Committed", style="green")
    else:
        return Text("○ Not committed", style="dim")


@click.command()
@click.option(
    "--team",
    required=True,
    help="Team name or ID",
)
@click.option(
    "--pi",
    "--release",
    "release_name",
    required=False,
    default=None,
    help="PI/Release name (shows current PI if not specified)",
)
@click.option(
    "--art",
    required=False,
    default=None,
    help="Agile Release Train name (defaults to default-art in config)",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    team: str,
    release_name: str | None,
    art: str | None,
    format: str,
    verbose: bool,
):
    """List team objectives committed for a PI."""
    try:
        client = TPAPIClient(verbose=verbose)

        # Get default ART if not specified (but not if explicitly set to "")
        if art is None:
            default_art = get_default_art()
            if default_art:
                art = default_art
                if verbose:
                    console.print(f"[dim]Using default ART: {art}[/dim]")

        # Get ART
        art_obj = None
        if art:
            art_obj = client.get_art_by_name(art)
            if not art_obj:
                if verbose:
                    console.print(f"[yellow]Warning: ART '{art}' not found[/yellow]")
                # Continue anyway - will search all teams

        # Get team
        team_obj = client.get_team_by_name(team, art_id=art_obj.id if art_obj else None)
        if not team_obj:
            # If not found with ART filter, try without ART filter
            all_teams = client.get_teams()
            for t in all_teams:
                if t.name.lower() == team.lower():
                    team_obj = t
                    break

        if not team_obj:
            console.print(
                f"[red]Error: Team '{team}' not found{' in ART ' + art if art else ''}[/red]"
            )
            sys.exit(1)

        if verbose:
            console.print(f"[dim]Found team: {team_obj.name} (ID: {team_obj.id})[/dim]")

        # Get release if specified
        release_obj = None
        if release_name:
            release_obj = client.get_release_by_name(release_name, art_id=art_obj.id if art_obj else None)
            if not release_obj:
                console.print(
                    f"[red]Error: PI/Release '{release_name}' not found[/red]"
                )
                sys.exit(1)
            if verbose:
                console.print(
                    f"[dim]Found PI: {release_obj.name} (ID: {release_obj.id})[/dim]"
                )

        # Get team objectives
        objectives = client.get_team_pi_objectives(
            team_id=team_obj.id,
            release_id=release_obj.id if release_obj else None,
        )

        if not objectives:
            console.print(
                f"[yellow]No objectives found for team '{team_obj.name}'"
                + (f" in PI '{release_obj.name}'" if release_obj else "")
                + "[/yellow]"
            )
            return

        # Filter to committed if specified
        committed = [obj for obj in objectives if obj.committed]
        not_committed = [obj for obj in objectives if not obj.committed]

        if format == "json":
            import json

            data = []
            for obj in objectives:
                data.append(
                    {
                        "id": obj.id,
                        "name": obj.name,
                        "status": obj.status.value if hasattr(obj.status, "value") else str(obj.status),
                        "effort": obj.effort,
                        "committed": obj.committed,
                        "owner": obj.owner.full_name if obj.owner else None,
                        "release_name": obj.release_name,
                    }
                )
            console.print(json.dumps(data, indent=2))
        elif format == "csv":
            console.print("Name,Status,Effort,Committed,Owner,Release")
            for obj in objectives:
                status_str = obj.status.value if hasattr(obj.status, "value") else str(obj.status)
                owner_name = obj.owner.full_name if obj.owner else ""
                console.print(
                    f"{obj.name},{status_str},{obj.effort},{obj.committed},{owner_name},"
                    f"{obj.release_name}"
                )
        else:  # text format
            # Show committed objectives first
            if committed:
                table = Table(title=f"Committed Objectives - {team_obj.name}")
                table.add_column("Objective", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Effort", style="magenta", justify="right")
                table.add_column("Owner", style="yellow")
                table.add_column("PI", style="dim")

                for obj in sorted(committed, key=lambda x: x.name):
                    status_str = obj.status.value if hasattr(obj.status, "value") else str(obj.status)
                    owner_name = obj.owner.full_name if obj.owner else "Unassigned"
                    table.add_row(
                        obj.name,
                        status_str,
                        str(obj.effort),
                        owner_name,
                        obj.release_name or "N/A",
                    )

                console.print(table)
                console.print()

            # Show non-committed objectives
            if not_committed:
                table = Table(title=f"Not Committed - {team_obj.name}", style="dim")
                table.add_column("Objective", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Effort", style="magenta", justify="right")
                table.add_column("Owner", style="yellow")
                table.add_column("PI", style="dim")

                for obj in sorted(not_committed, key=lambda x: x.name):
                    status_str = obj.status.value if hasattr(obj.status, "value") else str(obj.status)
                    owner_name = obj.owner.full_name if obj.owner else "Unassigned"
                    table.add_row(
                        obj.name,
                        status_str,
                        str(obj.effort),
                        owner_name,
                        obj.release_name or "N/A",
                    )

                console.print(table)

            # Summary
            console.print()
            total_effort = sum(obj.effort for obj in objectives)
            committed_effort = sum(obj.effort for obj in committed)
            console.print(
                f"[dim]Total: {len(objectives)} objectives | "
                f"Committed: {len(committed)} ({committed_effort} points) | "
                f"Not committed: {len(not_committed)} ({total_effort - committed_effort} points)[/dim]"
            )

    except TPAPIError as e:
        console.print(f"[red]TargetProcess API Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        if verbose:
            raise
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
