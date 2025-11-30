"""Team Deep-Dive CLI command - US-002."""

import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.analysis import CapacityAnalyzer, RiskAnalyzer
from tpcli_pi.core.api_client import TPAPIClient, TPAPIError

console = Console()


def format_percent(value: float) -> Text:
    """Format percentage with color based on utilization."""
    if value > 100:
        return Text(f"{value:.0f}%", style="red")
    elif value > 90:
        return Text(f"{value:.0f}%", style="yellow")
    elif value > 70:
        return Text(f"{value:.0f}%", style="cyan")
    else:
        return Text(f"{value:.0f}%", style="green")


def risk_level_color(level: str) -> str:
    """Get color for risk level."""
    if level == "Critical":
        return "red"
    elif level == "High":
        return "dark_orange"
    elif level == "Medium":
        return "yellow"
    else:
        return "green"


@click.command()
@click.option(
    "--team",
    required=True,
    help="Name of team to analyze",
)
@click.option(
    "--art",
    default=None,
    help="ART name (optional, for disambiguation)",
)
@click.option(
    "--pi",
    type=click.Choice(["current", "upcoming"]),
    default="current",
    help="Filter to specific PI",
)
@click.option(
    "--depth",
    type=click.Choice(["basic", "detailed", "comprehensive"]),
    default="detailed",
    help="Analysis depth",
)
@click.option(
    "--include-risks",
    is_flag=True,
    help="Include detailed risk assessment",
)
@click.option(
    "--include-jira",
    is_flag=True,
    help="Include Jira correlation",
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
    team: str,
    art: Optional[str],
    pi: str,
    depth: str,
    include_risks: bool,
    include_jira: bool,
    format: str,  # noqa: A002 - click convention
    verbose: bool,
) -> None:
    """
    Analyze a specific team's PI commitments, capacity, and risks.

    Shows team profile, objectives, features, capacity utilization, risks,
    and Jira alignment.

    Examples:
        team-deep-dive --team "Example Team"
        team-deep-dive --team "Example Team" --art DAD
        team-deep-dive --team "Example Team" --include-risks
        team-deep-dive --team "Example Team" --depth comprehensive
    """
    try:
        client = TPAPIClient(verbose=verbose)

        # Find team
        console.print(f"[bold]Loading team:[/bold] {team}")
        team_obj = client.get_team_by_name(team)
        if not team_obj:
            click.echo(f"[red]Error:[/red] Team not found: {team}", err=True)
            sys.exit(1)

        # Get objectives
        console.print("[bold]Loading objectives...[/bold]")
        objectives = client.get_team_pi_objectives(team_obj.id)

        # Get features
        console.print("[bold]Loading features...[/bold]")
        features = client.get_features(team_id=team_obj.id)

        # Perform capacity analysis
        console.print("[bold]Analyzing capacity...[/bold]")
        capacity = CapacityAnalyzer.analyze_team_capacity(team_obj, objectives)

        # Get all objectives for risk analysis
        all_objectives = client.get_team_pi_objectives()

        # Perform risk assessment if requested
        risk_assessment = None
        if include_risks:
            console.print("[bold]Assessing risks...[/bold]")
            risk_assessment = RiskAnalyzer.assess_team(
                team_obj, objectives, all_objectives, features
            )

        # Output results
        if format == "json":
            _output_json(team_obj, capacity, objectives, features, risk_assessment)
        elif format == "markdown":
            _output_markdown(team_obj, capacity, objectives, features, risk_assessment)
        else:
            _output_text(team_obj, capacity, objectives, features, risk_assessment)

        console.print(f"\n[green]✓ Analysis complete[/green]")

    except TPAPIError as e:
        click.echo(f"[red]API Error:[/red] {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        click.echo(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


def _output_text(team_obj, capacity, objectives, features, risk_assessment) -> None:
    """Output analysis as formatted text."""
    console.print(f"\n[bold cyan]=== Team Deep-Dive: {team_obj.name} ===[/bold cyan]\n")

    # Team Overview
    console.print("[bold]Team Overview[/bold]")
    overview_table = Table(show_header=True, header_style="bold magenta")
    overview_table.add_column("Property", style="cyan")
    overview_table.add_column("Value")

    overview_table.add_row("Team Name", team_obj.name)
    overview_table.add_row("Members", str(team_obj.member_count))
    overview_table.add_row(
        "Owner",
        f"{team_obj.owner.first_name} {team_obj.owner.last_name}"
        if team_obj.owner
        else "N/A",
    )
    overview_table.add_row("Status", "Active" if team_obj.is_active else "Inactive")
    overview_table.add_row("ART", team_obj.art_name or "N/A")

    console.print(overview_table)

    # Capacity Analysis
    console.print("\n[bold]Capacity Analysis[/bold]")
    capacity_table = Table(show_header=True, header_style="bold magenta")
    capacity_table.add_column("Metric", style="cyan")
    capacity_table.add_column("Value")

    capacity_table.add_row(
        "Total Capacity", f"{capacity.total_effort_available} points"
    )
    capacity_table.add_row(
        "Committed Effort", f"{capacity.total_effort_committed} points"
    )
    capacity_table.add_row(
        "Remaining Capacity", f"{capacity.total_effort_remaining} points"
    )
    capacity_table.add_row(
        "Utilization",
        format_percent(capacity.capacity_utilization_percent),
    )

    if capacity.is_overcommitted:
        capacity_table.add_row(
            "Status",
            Text("OVERCOMMITTED", style="red bold"),
        )
    else:
        capacity_table.add_row(
            "Status",
            Text("On Track", style="green"),
        )

    console.print(capacity_table)

    # Objectives
    console.print(f"\n[bold]PI Objectives ({len(objectives)})[/bold]")
    if objectives:
        obj_table = Table(show_header=True, header_style="bold magenta")
        obj_table.add_column("Objective", style="cyan")
        obj_table.add_column("Status")
        obj_table.add_column("Effort")
        obj_table.add_column("Owner")

        for obj in objectives:
            obj_table.add_row(
                obj.name,
                obj.status,
                str(obj.effort),
                obj.owner.first_name if obj.owner else "N/A",
            )

        console.print(obj_table)
    else:
        console.print("[yellow]No objectives found[/yellow]")

    # Features
    console.print(f"\n[bold]Features ({len(features)})[/bold]")
    if features:
        feat_table = Table(show_header=True, header_style="bold magenta")
        feat_table.add_column("Feature", style="cyan")
        feat_table.add_column("Status")
        feat_table.add_column("Effort")
        feat_table.add_column("Owner")

        for feat in features[:10]:  # Show first 10
            feat_table.add_row(
                feat.name,
                feat.status,
                str(feat.effort),
                feat.owner.first_name if feat.owner else "N/A",
            )

        console.print(feat_table)

        if len(features) > 10:
            console.print(f"[dim]... and {len(features) - 10} more features[/dim]")
    else:
        console.print("[yellow]No features found[/yellow]")

    # Risk Summary
    if risk_assessment:
        console.print(f"\n[bold]Risk Assessment[/bold]")
        risk_table = Table(show_header=True, header_style="bold magenta")
        risk_table.add_column("Risk Level", style="cyan")
        risk_table.add_column("Count")
        risk_table.add_column("Health Score")

        risk_table.add_row(
            Text("Critical", style="red"),
            str(risk_assessment.critical_risk_count),
            format_percent(risk_assessment.health_score),
        )
        risk_table.add_row(
            Text("High", style="dark_orange"),
            str(risk_assessment.high_risk_count),
            "",
        )
        risk_table.add_row(
            Text("Medium", style="yellow"),
            str(risk_assessment.medium_risk_count),
            "",
        )
        risk_table.add_row(
            Text("Low", style="green"),
            str(risk_assessment.low_risk_count),
            "",
        )

        console.print(risk_table)

        if risk_assessment.recommendations:
            console.print("\n[bold]Recommendations[/bold]")
            for rec in risk_assessment.recommendations:
                console.print(f"  • {rec}")


def _output_json(team_obj, capacity, objectives, features, risk_assessment) -> None:
    """Output analysis as JSON."""
    import json

    output = {
        "team": {
            "id": team_obj.id,
            "name": team_obj.name,
            "member_count": team_obj.member_count,
            "is_active": team_obj.is_active,
        },
        "capacity": {
            "total_effort_available": capacity.total_effort_available,
            "total_effort_committed": capacity.total_effort_committed,
            "total_effort_remaining": capacity.total_effort_remaining,
            "capacity_utilization_percent": capacity.capacity_utilization_percent,
            "is_overcommitted": capacity.is_overcommitted,
        },
        "objectives": [
            {
                "id": o.id,
                "name": o.name,
                "status": o.status,
                "effort": o.effort,
            }
            for o in objectives
        ],
        "features": [
            {
                "id": f.id,
                "name": f.name,
                "status": f.status,
                "effort": f.effort,
            }
            for f in features
        ],
    }

    if risk_assessment:
        output["risk_assessment"] = {
            "total_risk_count": risk_assessment.total_risk_count,
            "critical_risk_count": risk_assessment.critical_risk_count,
            "high_risk_count": risk_assessment.high_risk_count,
            "medium_risk_count": risk_assessment.medium_risk_count,
            "low_risk_count": risk_assessment.low_risk_count,
            "health_score": risk_assessment.health_score,
            "escalation_required": risk_assessment.escalation_required,
            "recommendations": risk_assessment.recommendations,
        }

    console.print(json.dumps(output, indent=2))


def _output_markdown(team_obj, capacity, objectives, features, risk_assessment) -> None:
    """Output analysis as Markdown."""
    console.print(f"\n# Team Deep-Dive: {team_obj.name}\n")

    console.print("## Team Overview\n")
    console.print(f"- **Team Name:** {team_obj.name}")
    console.print(f"- **Members:** {team_obj.member_count}")
    console.print(f"- **Status:** {'Active' if team_obj.is_active else 'Inactive'}")
    console.print(f"- **ART:** {team_obj.art_name or 'N/A'}\n")

    console.print("## Capacity Analysis\n")
    console.print(f"- **Total Capacity:** {capacity.total_effort_available} points")
    console.print(f"- **Committed Effort:** {capacity.total_effort_committed} points")
    console.print(f"- **Remaining Capacity:** {capacity.total_effort_remaining} points")
    console.print(
        f"- **Utilization:** {capacity.capacity_utilization_percent:.0f}%"
    )
    status_str = "⚠️ OVERCOMMITTED" if capacity.is_overcommitted else "✓ On Track"
    console.print(f"- **Status:** {status_str}\n")

    console.print(f"## PI Objectives ({len(objectives)})\n")
    for obj in objectives:
        console.print(f"- **{obj.name}** - {obj.status} ({obj.effort} points)")

    console.print(f"\n## Features ({len(features)})\n")
    for feat in features[:10]:
        console.print(f"- **{feat.name}** - {feat.status} ({feat.effort} points)")

    if risk_assessment and risk_assessment.recommendations:
        console.print("\n## Risk Assessment\n")
        console.print(f"- **Health Score:** {risk_assessment.health_score:.0f}/100")
        console.print(f"- **Critical Risks:** {risk_assessment.critical_risk_count}")
        console.print(f"- **High Risks:** {risk_assessment.high_risk_count}\n")

        console.print("### Recommendations\n")
        for rec in risk_assessment.recommendations:
            console.print(f"- {rec}")


if __name__ == "__main__":
    main()
