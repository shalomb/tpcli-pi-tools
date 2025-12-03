"""Team Features CLI command - List features implementing team objectives."""

import sys
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.config import get_default_art

console = Console()


def format_status(status) -> Text:
    """Return colored status text."""
    status_str = status.value if hasattr(status, "value") else str(status)

    if status_str in ("Open", "Planned", "In Progress"):
        return Text(status_str, style="green")
    elif status_str in ("Done", "Completed", "Closed"):
        return Text(status_str, style="blue")
    else:
        return Text(status_str, style="yellow")


@click.command()
@click.option(
    "--team",
    required=True,
    help="Team name or ID",
)
@click.option(
    "--objective",
    required=False,
    default=None,
    help="Filter by specific objective name",
)
@click.option(
    "--pi",
    "--release",
    "release_name",
    required=False,
    default=None,
    help="PI/Release name",
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
    objective: str | None,
    release_name: str | None,
    art: str | None,
    format: str,
    verbose: bool,
):
    """List features for a team, optionally filtered by objective."""
    try:
        client = TPAPIClient(verbose=verbose)

        # Get default ART if not specified
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

        # Get features
        features = client.get_features(
            team_id=team_obj.id,
            release_id=release_obj.id if release_obj else None,
        )

        if not features:
            console.print(
                f"[yellow]No features found for team '{team_obj.name}'"
                + (f" in PI '{release_obj.name}'" if release_obj else "")
                + "[/yellow]"
            )
            return

        # Filter by objective if specified
        if objective:
            filtered = [f for f in features if objective.lower() in f.name.lower()]
            if not filtered:
                console.print(f"[yellow]No features matching '{objective}' found[/yellow]")
                return
            features = filtered

        if format == "json":
            import json

            data = []
            for f in features:
                data.append(
                    {
                        "id": f.id,
                        "name": f.name,
                        "status": f.status.value if hasattr(f.status, "value") else str(f.status),
                        "effort": f.effort,
                        "owner": f.owner.full_name if f.owner else None,
                        "team_name": f.team.name if f.team else None,
                        "release_name": f.release_name,
                    }
                )
            console.print(json.dumps(data, indent=2))
        elif format == "csv":
            console.print("Name,Status,Effort,Owner,Team,Release")
            for f in features:
                status_str = f.status.value if hasattr(f.status, "value") else str(f.status)
                owner_name = f.owner.full_name if f.owner else ""
                team_name = f.team.name if f.team else ""
                console.print(
                    f"{f.name},{status_str},{f.effort},{owner_name},{team_name},"
                    f"{f.release_name}"
                )
        else:  # text format
            table = Table(title=f"Features - {team_obj.name}")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="white")
            table.add_column("Effort", style="magenta", justify="right")
            table.add_column("Owner", style="yellow")
            table.add_column("PI", style="dim")

            # Add rows
            for f in sorted(features, key=lambda x: x.name):
                status_str = f.status.value if hasattr(f.status, "value") else str(f.status)
                owner_name = f.owner.full_name if f.owner else "Unassigned"
                table.add_row(
                    f.name,
                    status_str,
                    str(f.effort),
                    owner_name,
                    f.release_name or "N/A",
                )

            console.print(table)

            # Summary
            console.print()
            total_effort = sum(f.effort for f in features)
            console.print(
                f"[dim]Total: {len(features)} features | "
                f"Effort: {total_effort} points[/dim]"
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
