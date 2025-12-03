"""Team Capacity CLI command - Show team capacity vs committed effort."""

import sys
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.config import get_default_art

console = Console()


def get_utilization_color(utilization: float) -> str:
    """Return color based on utilization percentage."""
    if utilization <= 80:
        return "green"
    elif utilization <= 100:
        return "yellow"
    else:
        return "red"


def format_utilization(utilization: float) -> Text:
    """Format utilization with color."""
    color = get_utilization_color(utilization)
    return Text(f"{utilization:.0f}%", style=color)


@click.command()
@click.option(
    "--team",
    required=True,
    help="Team name or ID",
)
@click.option(
    "--capacity",
    type=float,
    required=False,
    default=None,
    help="Team total capacity in story points (for this PI)",
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
    capacity: float | None,
    release_name: str | None,
    art: str | None,
    format: str,
    verbose: bool,
):
    """Display team capacity vs committed effort."""
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

        # Get team objectives and features to calculate committed effort
        objectives = client.get_team_pi_objectives(
            team_id=team_obj.id,
            release_id=release_obj.id if release_obj else None,
        )

        features = client.get_features(
            team_id=team_obj.id,
            release_id=release_obj.id if release_obj else None,
        )

        # Calculate committed effort
        objective_effort = sum(obj.effort for obj in objectives)
        feature_effort = sum(f.effort for f in features)
        committed_effort = objective_effort + feature_effort

        # Determine available capacity
        if capacity is None:
            console.print(
                "[yellow]Note: Team capacity not specified. Use --capacity flag or provide team capacity config[/yellow]"
            )
            utilization = None
            available_capacity = None
        else:
            available_capacity = capacity - committed_effort
            utilization = (committed_effort / capacity * 100) if capacity > 0 else 0

        if format == "json":
            import json

            data = {
                "team_name": team_obj.name,
                "team_id": team_obj.id,
                "pi_name": release_obj.name if release_obj else None,
                "total_capacity": capacity,
                "committed_effort": committed_effort,
                "objective_effort": objective_effort,
                "feature_effort": feature_effort,
                "available_capacity": available_capacity,
                "utilization_percent": utilization,
            }
            console.print(json.dumps(data, indent=2))
        elif format == "csv":
            console.print("Team,PI,Total Capacity,Objective Effort,Feature Effort,Committed,Available,Utilization")
            utilization_str = f"{utilization:.0f}%" if utilization is not None else "N/A"
            available_str = f"{available_capacity:.0f}" if available_capacity is not None else "N/A"
            console.print(
                f"{team_obj.name},{release_obj.name if release_obj else 'All'},"
                f"{capacity if capacity else 'N/A'},{objective_effort},{feature_effort},"
                f"{committed_effort},{available_str},{utilization_str}"
            )
        else:  # text format
            # Header
            title = f"{team_obj.name} Capacity Analysis"
            if release_obj:
                title += f" | {release_obj.name}"

            console.print(f"[bold cyan]{title}[/bold cyan]")
            console.print()

            # Metrics table
            metrics_table = Table(show_header=False, box=None)
            metrics_table.add_column(style="bold cyan")
            metrics_table.add_column(style="white", justify="right")

            metrics_table.add_row("Total Capacity", f"{capacity:.0f} points" if capacity else "Not specified")
            metrics_table.add_row("Objective Effort", f"{objective_effort} points")
            metrics_table.add_row("Feature Effort", f"{feature_effort} points")
            metrics_table.add_row("Committed Effort", f"{committed_effort} points")

            if available_capacity is not None:
                metrics_table.add_row(
                    "Available Capacity",
                    f"{available_capacity:.0f} points"
                    if available_capacity >= 0
                    else Text(f"{available_capacity:.0f} points", style="red"),
                )

            if utilization is not None:
                metrics_table.add_row(
                    "Utilization",
                    format_utilization(utilization),
                )

                # Status indicator
                if utilization > 100:
                    console.print(metrics_table)
                    console.print()
                    console.print(
                        "[red bold]⚠️  OVER-COMMITTED[/red bold] - Team has committed more effort than available capacity"
                    )
                elif utilization > 80:
                    console.print(metrics_table)
                    console.print()
                    console.print(
                        "[yellow bold]⚠️  HIGH UTILIZATION[/yellow bold] - Team is at 80%+ capacity. Limited room for contingencies."
                    )
                else:
                    console.print(metrics_table)
                    console.print()
                    console.print("[green]✓ Healthy capacity[/green] - Team has available capacity for unexpected work")
            else:
                console.print(metrics_table)

            # Breakdown by source
            console.print()
            console.print("[bold]Committed Effort Breakdown:[/bold]")
            breakdown_table = Table(show_header=True, box=None)
            breakdown_table.add_column("Source", style="cyan")
            breakdown_table.add_column("Count", justify="right")
            breakdown_table.add_column("Effort", justify="right")

            breakdown_table.add_row("Objectives", str(len(objectives)), f"{objective_effort} points")
            breakdown_table.add_row("Features", str(len(features)), f"{feature_effort} points")
            breakdown_table.add_row("[bold]Total[/bold]", "[bold]" + str(len(objectives) + len(features)) + "[/bold]",
                                   "[bold]" + str(committed_effort) + " points[/bold]")

            console.print(breakdown_table)

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
