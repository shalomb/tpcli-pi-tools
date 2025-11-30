"""Release Status CLI command - US-004."""

import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError

console = Console()


def health_status_color(health_score: float) -> str:
    """Get color for health score."""
    if health_score >= 80:
        return "green"
    elif health_score >= 60:
        return "yellow"
    elif health_score >= 40:
        return "dark_orange"
    else:
        return "red"


def health_status_symbol(health_score: float) -> str:
    """Get symbol for health score."""
    if health_score >= 80:
        return "✓"
    elif health_score >= 60:
        return "⚠"
    else:
        return "✗"


@click.command()
@click.option(
    "--release",
    required=True,
    help="Release name to track",
)
@click.option(
    "--art",
    default=None,
    help="ART name (optional)",
)
@click.option(
    "--pi",
    type=click.Choice(["current", "upcoming", "all"]),
    default="current",
    help="Filter to specific PI status",
)
@click.option(
    "--include-blockers",
    is_flag=True,
    help="Highlight blocking items",
)
@click.option(
    "--include-dependencies",
    is_flag=True,
    help="Show cross-team dependencies",
)
@click.option(
    "--compare-to",
    default=None,
    help="Compare to previous release",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    release: str,
    art: Optional[str],
    pi: str,
    include_blockers: bool,
    include_dependencies: bool,
    compare_to: Optional[str],
    format: str,  # noqa: A002 - click convention
    verbose: bool,
) -> None:
    """
    Track PI progress and identify blockers.

    Shows release timeline, team status, progress metrics, and at-risk items.

    Examples:
        release-status --release "DAD PI-123"
        release-status --release "DAD PI-123" --include-blockers
        release-status --release "DAD PI-123" --compare-to "DAD PI-122"
        release-status --release "DAD PI-123" --format json
    """
    try:
        client = TPAPIClient(verbose=verbose)

        # Find release
        console.print(f"[bold]Loading release:[/bold] {release}")
        releases = client.get_releases()
        release_list = [r for r in releases if r.name == release]

        if not release_list:
            console.print(
                f"[red]Error:[/red] Release not found: {release}",
                file=sys.stderr,
            )
            sys.exit(1)

        rel = release_list[0]

        # Get all objectives and features
        console.print("[bold]Loading program objectives...[/bold]")
        program_objectives = client.get_program_pi_objectives(release_id=rel.id)

        console.print("[bold]Loading team objectives...[/bold]")
        team_objectives = client.get_team_pi_objectives(release_id=rel.id)

        console.print("[bold]Loading teams...[/bold]")
        teams = client.get_teams(rel.art_id)

        console.print("[bold]Loading features...[/bold]")
        features = client.get_features(release_id=rel.id)

        # Calculate metrics
        total_effort = sum(o.effort for o in program_objectives)
        completed_effort = sum(
            o.effort
            for o in program_objectives
            if o.status in ["Done", "Accepted"]
        )
        progress_pct = (
            (completed_effort / total_effort * 100) if total_effort > 0 else 0
        )

        # Output results
        if format == "json":
            _output_json(
                rel, program_objectives, team_objectives, teams, features
            )
        elif format == "markdown":
            _output_markdown(
                rel, program_objectives, team_objectives, teams, features
            )
        else:
            _output_text(rel, program_objectives, team_objectives, teams, features)

        console.print(f"\n[green]✓ Status report complete[/green]")

    except TPAPIError as e:
        click.echo(f"[red]API Error:[/red] {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        click.echo(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


def _output_text(rel, program_objectives, team_objectives, teams, features) -> None:
    """Output status as formatted text."""
    console.print(f"\n[bold cyan]=== Release Status: {rel.name} ===[/bold cyan]\n")

    # Release Overview
    console.print("[bold]Release Overview[/bold]")
    overview_table = Table(show_header=True, header_style="bold magenta")
    overview_table.add_column("Property", style="cyan")
    overview_table.add_column("Value")

    overview_table.add_row("Release Name", rel.name)
    overview_table.add_row(
        "Start Date", rel.start_date.strftime("%Y-%m-%d") if rel.start_date else "N/A"
    )
    overview_table.add_row(
        "End Date", rel.end_date.strftime("%Y-%m-%d") if rel.end_date else "N/A"
    )

    days_remaining = (
        (rel.end_date.date() - datetime.now().date()).days
        if rel.end_date
        else None
    )
    if days_remaining is not None:
        overview_table.add_row(
            "Days Remaining",
            str(days_remaining) if days_remaining >= 0 else f"{abs(days_remaining)} days overdue",
        )

    is_current = rel.is_in_progress
    status = "Current" if is_current else "Upcoming" if rel.is_current else "Past"
    overview_table.add_row("Status", status)

    console.print(overview_table)

    # Progress Metrics
    console.print("\n[bold]Progress Metrics[/bold]")
    total_effort = sum(o.effort for o in program_objectives)
    completed_effort = sum(
        o.effort
        for o in program_objectives
        if o.status in ["Done", "Accepted"]
    )
    progress_pct = (completed_effort / total_effort * 100) if total_effort > 0 else 0

    metrics_table = Table(show_header=True, header_style="bold magenta")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value")

    metrics_table.add_row("Total Effort", f"{total_effort} points")
    metrics_table.add_row("Completed Effort", f"{completed_effort} points")
    metrics_table.add_row("Remaining Effort", f"{total_effort - completed_effort} points")
    metrics_table.add_row(
        "Progress",
        f"{progress_pct:.0f}%",
    )

    console.print(metrics_table)

    # Program Objectives Summary
    console.print(f"\n[bold]Program Objectives ({len(program_objectives)})[/bold]")
    if program_objectives:
        obj_table = Table(show_header=True, header_style="bold magenta")
        obj_table.add_column("Objective", style="cyan")
        obj_table.add_column("Status")
        obj_table.add_column("Effort")
        obj_table.add_column("Owner")

        for obj in program_objectives[:15]:  # Show first 15
            obj_table.add_row(
                obj.name,
                obj.status,
                str(obj.effort),
                obj.owner.first_name if obj.owner else "N/A",
            )

        console.print(obj_table)

        if len(program_objectives) > 15:
            console.print(
                f"[dim]... and {len(program_objectives) - 15} more objectives[/dim]"
            )
    else:
        console.print("[yellow]No program objectives found[/yellow]")

    # Team Status Summary
    console.print(f"\n[bold]Team Summary[/bold]")
    team_table = Table(show_header=True, header_style="bold magenta")
    team_table.add_column("Team", style="cyan")
    team_table.add_column("Objectives")
    team_table.add_column("Effort")
    team_table.add_column("Progress")

    for team in teams[:10]:  # Show first 10 teams
        team_objs = [o for o in team_objectives if o.team_id == team.id]
        team_effort = sum(o.effort for o in team_objs)
        team_completed = sum(
            o.effort
            for o in team_objs
            if o.status in ["Done", "Accepted"]
        )
        team_pct = (team_completed / team_effort * 100) if team_effort > 0 else 0

        team_table.add_row(
            team.name,
            str(len(team_objs)),
            str(team_effort),
            f"{team_pct:.0f}%",
        )

    console.print(team_table)

    # Health Summary
    console.print("\n[bold]Health Summary[/bold]")
    health_table = Table(show_header=True, header_style="bold magenta")
    health_table.add_column("Status", style="cyan")
    health_table.add_column("Count")

    not_started = sum(1 for o in program_objectives if o.status == "Pending")
    in_progress = sum(1 for o in program_objectives if o.status == "In Progress")
    done = sum(1 for o in program_objectives if o.status == "Done")

    health_table.add_row("Not Started", str(not_started))
    health_table.add_row("In Progress", str(in_progress))
    health_table.add_row("Done", str(done))

    console.print(health_table)


def _output_json(rel, program_objectives, team_objectives, teams, features) -> None:
    """Output status as JSON."""
    import json

    total_effort = sum(o.effort for o in program_objectives)
    completed_effort = sum(
        o.effort
        for o in program_objectives
        if o.status in ["Done", "Accepted"]
    )
    progress_pct = (completed_effort / total_effort * 100) if total_effort > 0 else 0

    output = {
        "release": {
            "id": rel.id,
            "name": rel.name,
            "start_date": rel.start_date.isoformat() if rel.start_date else None,
            "end_date": rel.end_date.isoformat() if rel.end_date else None,
            "is_current": rel.is_in_progress,
        },
        "progress": {
            "total_effort": total_effort,
            "completed_effort": completed_effort,
            "remaining_effort": total_effort - completed_effort,
            "progress_percentage": round(progress_pct, 1),
        },
        "program_objectives": [
            {
                "id": o.id,
                "name": o.name,
                "status": o.status,
                "effort": o.effort,
            }
            for o in program_objectives
        ],
        "team_count": len(teams),
        "teams": [
            {
                "id": t.id,
                "name": t.name,
                "member_count": t.member_count,
                "objectives": len([x for x in team_objectives if x.team_id == t.id]),
            }
            for t in teams
        ],
    }

    console.print(json.dumps(output, indent=2))


def _output_markdown(rel, program_objectives, team_objectives, teams, features) -> None:
    """Output status as Markdown."""
    console.print(f"\n# Release Status: {rel.name}\n")

    console.print("## Release Overview\n")
    console.print(
        f"- **Start Date:** {rel.start_date.strftime('%Y-%m-%d') if rel.start_date else 'N/A'}"
    )
    console.print(
        f"- **End Date:** {rel.end_date.strftime('%Y-%m-%d') if rel.end_date else 'N/A'}"
    )
    console.print(
        f"- **Status:** {'Current' if rel.is_in_progress else 'Upcoming'}\n"
    )

    # Progress
    total_effort = sum(o.effort for o in program_objectives)
    completed_effort = sum(
        o.effort
        for o in program_objectives
        if o.status in ["Done", "Accepted"]
    )
    progress_pct = (completed_effort / total_effort * 100) if total_effort > 0 else 0

    console.print("## Progress\n")
    console.print(f"- **Total Effort:** {total_effort} points")
    console.print(f"- **Completed:** {completed_effort} points")
    console.print(f"- **Progress:** {progress_pct:.0f}%\n")

    # Objectives
    console.print(f"## Program Objectives ({len(program_objectives)})\n")
    for obj in program_objectives[:20]:
        status_icon = "✓" if obj.status == "Done" else "▶" if obj.status == "In Progress" else "○"
        console.print(
            f"{status_icon} **{obj.name}** - {obj.status} ({obj.effort} points)"
        )

    console.print(f"\n## Team Summary\n")
    for team in teams[:10]:
        team_objs = [o for o in team_objectives if o.team_id == team.id]
        console.print(f"- **{team.name}**: {len(team_objs)} objectives")


if __name__ == "__main__":
    main()
