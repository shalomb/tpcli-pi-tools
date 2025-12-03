"""Team Dependencies CLI command - Show cross-team dependencies and blockers."""

import sys
import json
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.config import get_default_art

console = Console()


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
    release_name: str | None,
    art: str | None,
    format: str,
    verbose: bool,
):
    """Display team dependencies and blocking relationships."""
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

        # Query dependencies
        cached = client._get_cached("Dependencies", None)
        if cached is None:
            cached = client._run_tpcli("Dependencies", None)
            client._set_cached("Dependencies", cached, None)

        # Filter dependencies that involve this team
        team_dependencies = []
        for dep in cached:
            # Check if team is involved (simplified - just show items with team involved)
            if dep.get("Team", {}).get("Id") == team_obj.id or (
                release_obj and dep.get("AgileReleaseTrain", {}).get("Id") == art_obj.id
            ):
                team_dependencies.append(dep)

        if not team_dependencies:
            console.print(
                f"[yellow]No dependencies found for team '{team_obj.name}'"
                + (f" in PI '{release_obj.name}'" if release_obj else "")
                + "[/yellow]"
            )
            return

        if format == "json":
            data = [
                {
                    "id": d.get("Id"),
                    "name": d.get("Name"),
                    "status": d.get("EntityState", {}).get("Name"),
                    "owner": d.get("Owner", {}).get("FullName"),
                    "created_date": d.get("CreateDate"),
                }
                for d in team_dependencies
            ]
            console.print(json.dumps(data, indent=2))
        elif format == "csv":
            console.print("Name,Status,Owner")
            for d in team_dependencies:
                console.print(f"{d.get('Name')},{d.get('EntityState', {}).get('Name')},"
                             f"{d.get('Owner', {}).get('FullName')}")
        else:  # text format
            title = f"{team_obj.name} Dependencies"
            if release_obj:
                title += f" | {release_obj.name}"

            console.print(f"[bold cyan]{title}[/bold cyan]")
            console.print()

            table = Table(title=f"Dependencies ({len(team_dependencies)} Total)")
            table.add_column("Dependency", style="cyan")
            table.add_column("Status", style="white")
            table.add_column("Owner", style="yellow")

            for d in team_dependencies:
                status = d.get("EntityState", {}).get("Name", "N/A")
                owner = d.get("Owner", {}).get("FullName", "Unassigned") if d.get("Owner") else "Unassigned"
                table.add_row(
                    d.get("Name", "N/A"),
                    status,
                    owner,
                )

            console.print(table)

            # Summary
            console.print()
            done = len([d for d in team_dependencies if d.get("EntityState", {}).get("Name") == "Done"])
            in_progress = len([d for d in team_dependencies if d.get("EntityState", {}).get("Name") in ("In Progress", "Active")])
            console.print(
                f"[dim]Total: {len(team_dependencies)} dependencies | "
                f"Done: {done} | In Progress: {in_progress}[/dim]"
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
