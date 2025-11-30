"""ART Dashboard CLI command - US-001."""

import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.analysis import CapacityAnalyzer

console = Console()


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d")


def format_days_remaining(dt: Optional[datetime]) -> str:
    """Format days remaining until date."""
    if not dt:
        return "N/A"
    today = datetime.now().date()
    end = dt.date()
    remaining = (end - today).days
    if remaining < 0:
        return f"{abs(remaining)} ago"
    elif remaining == 0:
        return "Today"
    elif remaining == 1:
        return "Tomorrow"
    else:
        return f"{remaining} days"


def get_health_status(risks: int) -> Text:
    """Return colored health status based on risk count."""
    if risks == 0:
        return Text("Healthy", style="green")
    elif risks == 1:
        return Text("Caution", style="yellow")
    else:
        return Text("At Risk", style="red")


@click.command()
@click.option(
    "--art",
    required=True,
    help="Name of Agile Release Train to display",
)
@click.option(
    "--pi",
    type=click.Choice(["current", "upcoming", "all"]),
    default="all",
    help="Filter releases by status",
)
@click.option(
    "--team",
    default=None,
    help="Filter to specific team",
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
    art: str,
    pi: str,
    team: Optional[str],
    format: str,  # noqa: A002 - click convention
    verbose: bool,
) -> None:
    """
    Display ART Dashboard - overview of all teams, releases, and program objectives.

    Shows capacity utilization, health status, and risk summary for the entire ART.

    Examples:
        art-dashboard --art DAD
        art-dashboard --art DAD --pi current
        art-dashboard --art DAD --team "Example Team"
        art-dashboard --art DAD --format json
    """
    try:
        client = TPAPIClient(verbose=verbose)

        # Get ART
        console.print(f"[bold]Loading ART:[/bold] {art}")
        art_obj = client.get_art_by_name(art)
        if not art_obj:
            click.echo(f"[red]Error:[/red] ART not found: {art}", err=True)
            sys.exit(1)

        # Get releases
        console.print(f"[bold]Loading releases...[/bold]")
        releases = client.get_releases(art_obj.id)

        # Filter releases by status
        if pi == "current":
            releases = [r for r in releases if r.is_in_progress]
        elif pi == "upcoming":
            releases = [r for r in releases if r.start_date > datetime.now()]

        if not releases:
            console.print(f"[yellow]No releases found for ART: {art}[/yellow]")
            return

        # Get teams
        console.print("[bold]Loading teams...[/bold]")
        teams = client.get_teams(art_obj.id)
        if team:
            teams = [t for t in teams if t.name == team]

        # Get program objectives for all releases
        console.print("[bold]Loading program objectives...[/bold]")
        program_objectives = client.get_program_pi_objectives(art_obj.id)

        # Build dashboard display
        if format == "json":
            _output_json(art_obj, releases, teams, program_objectives)
        elif format == "csv":
            _output_csv(art_obj, releases, teams, program_objectives)
        else:
            _output_text(art_obj, releases, teams, program_objectives)

        console.print(f"\n[green]✓ Dashboard complete[/green]")

    except TPAPIError as e:
        click.echo(f"[red]API Error:[/red] {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        console.print(
            f"[red]Error:[/red] {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def _output_text(art_obj, releases, teams, program_objectives) -> None:
    """Output dashboard as formatted text."""
    console.print(f"\n[bold cyan]=== ART Dashboard: {art_obj.name} ===[/bold cyan]\n")

    # Releases Table
    console.print("[bold]Releases[/bold]")
    releases_table = Table(show_header=True, header_style="bold magenta")
    releases_table.add_column("Release", style="cyan")
    releases_table.add_column("Start Date")
    releases_table.add_column("End Date")
    releases_table.add_column("Days Remaining")
    releases_table.add_column("Status")

    for release in releases:
        status = "Current" if release.is_in_progress else "Upcoming" if release.is_current else "Past"
        releases_table.add_row(
            release.name,
            format_date(release.start_date),
            format_date(release.end_date),
            format_days_remaining(release.end_date),
            status,
        )

    console.print(releases_table)

    # Teams Table
    console.print("\n[bold]Teams[/bold]")
    teams_table = Table(show_header=True, header_style="bold magenta")
    teams_table.add_column("Team", style="cyan")
    teams_table.add_column("Members")
    teams_table.add_column("Status")
    teams_table.add_column("Owner")

    for team in teams:
        status = "Active" if team.is_active else "Inactive"
        owner_name = (
            f"{team.owner.first_name} {team.owner.last_name}"
            if team.owner
            else "N/A"
        )
        teams_table.add_row(
            team.name,
            str(team.member_count),
            status,
            owner_name,
        )

    console.print(teams_table)

    # Program Objectives Summary
    console.print("\n[bold]Program Objectives Summary[/bold]")
    obj_table = Table(show_header=True, header_style="bold magenta")
    obj_table.add_column("Objective", style="cyan")
    obj_table.add_column("Status")
    obj_table.add_column("Effort")
    obj_table.add_column("Release")

    for objective in program_objectives[:10]:  # Show first 10
        obj_table.add_row(
            objective.name,
            objective.status,
            str(objective.effort),
            objective.release_name or "N/A",
        )

    console.print(obj_table)

    # Health Summary
    console.print("\n[bold]Health Summary[/bold]")
    health_table = Table(show_header=True, header_style="bold magenta")
    health_table.add_column("Metric", style="cyan")
    health_table.add_column("Value")

    health_table.add_row("Total Releases", str(len(releases)))
    health_table.add_row("Total Teams", str(len(teams)))
    health_table.add_row("Program Objectives", str(len(program_objectives)))
    health_table.add_row("Committed Objectives", str(sum(1 for o in program_objectives if o.status == "Accepted")))

    console.print(health_table)


def _output_json(art_obj, releases, teams, program_objectives) -> None:
    """Output dashboard as JSON."""
    import json

    output = {
        "art": {
            "id": art_obj.id,
            "name": art_obj.name,
        },
        "releases": [
            {
                "id": r.id,
                "name": r.name,
                "start_date": r.start_date.isoformat() if r.start_date else None,
                "end_date": r.end_date.isoformat() if r.end_date else None,
                "is_current": r.is_current,
            }
            for r in releases
        ],
        "teams": [
            {
                "id": t.id,
                "name": t.name,
                "member_count": t.member_count,
                "is_active": t.is_active,
            }
            for t in teams
        ],
        "program_objectives": [
            {
                "id": o.id,
                "name": o.name,
                "status": o.status,
                "effort": o.effort,
                "release_id": o.release_id,
                "release_name": o.release_name,
            }
            for o in program_objectives
        ],
    }

    console.print(json.dumps(output, indent=2))


def _output_csv(art_obj, releases, teams, program_objectives) -> None:
    """Output dashboard as CSV (multiple tables)."""
    import csv

    console.print("Release,Start Date,End Date,Status")
    for release in releases:
        status = "Current" if release.is_in_progress else "Upcoming" if release.is_current else "Past"
        console.print(
            f"{release.name},{format_date(release.start_date)},"
            f"{format_date(release.end_date)},{status}"
        )

    console.print("\nTeam,Members,Status,Owner")
    for team in teams:
        status = "Active" if team.is_active else "Inactive"
        owner = (
            f"{team.owner.first_name} {team.owner.last_name}"
            if team.owner
            else "N/A"
        )
        console.print(f"{team.name},{team.member_count},{status},{owner}")

    console.print("\nObjective,Status,Effort,Release")
    for objective in program_objectives:
        console.print(
            f"{objective.name},{objective.status},"
            f"{objective.effort},{objective.release_name or 'N/A'}"
        )


if __name__ == "__main__":
    main()
