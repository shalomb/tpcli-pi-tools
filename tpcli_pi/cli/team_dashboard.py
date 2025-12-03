"""Team Dashboard CLI command - Summary view of team status."""

import sys
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.core.config import get_default_art

console = Console()


def get_health_color(percentage: float) -> str:
    """Return color based on health percentage."""
    if percentage >= 80:
        return "green"
    elif percentage >= 50:
        return "yellow"
    else:
        return "red"


def format_utilization_text(utilization: float) -> Text:
    """Format utilization with color."""
    color = "green" if utilization <= 100 else "red"
    return Text(f"{utilization:.0f}%", style=color)


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
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    team: str,
    release_name: str | None,
    art: str | None,
    verbose: bool,
):
    """Display team health dashboard."""
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

        # Get team objectives
        objectives = client.get_team_pi_objectives(
            team_id=team_obj.id,
            release_id=release_obj.id if release_obj else None,
        )

        # Get features
        features = client.get_features(
            team_id=team_obj.id,
            release_id=release_obj.id if release_obj else None,
        )

        # Calculate metrics
        committed_objectives = [obj for obj in objectives if obj.committed]
        objective_effort = sum(obj.effort for obj in objectives)
        feature_effort = sum(f.effort for f in features)
        total_effort = objective_effort + feature_effort

        # Status counts
        in_progress_features = [f for f in features if hasattr(f.status, 'value') and f.status.value == 'In Progress']
        completed_features = [f for f in features if hasattr(f.status, 'value') and f.status.value in ('Done', 'Completed')]

        # Health calculation (placeholder)
        feature_completion_rate = (len(completed_features) / len(features)) if features else 0
        health_score = int(feature_completion_rate * 100)

        # Create dashboard
        title_text = f"{team_obj.name} Dashboard"
        if release_obj:
            title_text += f" | {release_obj.name}"

        # Header panel with key metrics
        header_content = []
        header_content.append(f"[bold cyan]Team:[/bold cyan] {team_obj.name}")
        if release_obj:
            header_content.append(f"[bold cyan]PI:[/bold cyan] {release_obj.name}")
        if art:
            header_content.append(f"[bold cyan]ART:[/bold cyan] {art}")

        console.print(Panel("\n".join(header_content), title=title_text, expand=False))
        console.print()

        # Main metrics table
        metrics_table = Table(title="Team Metrics", show_header=False, box=None)
        metrics_table.add_column(style="bold cyan")
        metrics_table.add_column(style="white", justify="right")

        metrics_table.add_row("Objectives", f"{len(objectives)}")
        metrics_table.add_row("  Committed", f"{len(committed_objectives)}")
        metrics_table.add_row("Features", f"{len(features)}")
        metrics_table.add_row("  In Progress", f"{len(in_progress_features)}")
        metrics_table.add_row("  Completed", f"{len(completed_features)}")
        metrics_table.add_row("Total Effort (points)", f"{total_effort}")
        metrics_table.add_row("Health Score", Text(f"{health_score}/100", style=get_health_color(health_score)))

        console.print(metrics_table)
        console.print()

        # Objectives summary
        if objectives:
            obj_table = Table(title=f"Objectives ({len(committed_objectives)} Committed)")
            obj_table.add_column("Name", style="cyan")
            obj_table.add_column("Status", style="white")
            obj_table.add_column("Effort", justify="right")
            obj_table.add_column("Committed", justify="center")

            for obj in sorted(committed_objectives, key=lambda x: x.name):
                status_str = obj.status.value if hasattr(obj.status, "value") else str(obj.status)
                committed_mark = "✓" if obj.committed else "○"
                obj_table.add_row(
                    obj.name,
                    status_str,
                    str(obj.effort),
                    committed_mark,
                )

            console.print(obj_table)
            console.print()

        # Features summary
        if features:
            feat_table = Table(title=f"Features ({len(features)} Total)")
            feat_table.add_column("Feature", style="cyan")
            feat_table.add_column("Status", style="white")
            feat_table.add_column("Effort", justify="right")
            feat_table.add_column("Owner", style="yellow")

            # Show features in progress and completed first
            for f in sorted(features, key=lambda x: x.name):
                status_str = f.status.value if hasattr(f.status, "value") else str(f.status)
                if status_str in ("In Progress", "Done", "Completed"):
                    owner_name = f.owner.full_name if f.owner else "Unassigned"
                    feat_table.add_row(
                        f.name,
                        status_str,
                        str(f.effort),
                        owner_name,
                    )

            console.print(feat_table)

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
