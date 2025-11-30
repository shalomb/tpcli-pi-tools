"""Objective Deep-Dive CLI command - US-003."""

import sys

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from tpcli_pi.core.analysis import RiskAnalyzer
from tpcli_pi.core.api_client import TPAPIClient, TPAPIError

console = Console()


def parse_description(description: str | None) -> dict:
    """
    Parse structured description into goals, outcomes, acceptance criteria.

    Simple parser that looks for common section headers.
    """
    if not description:
        return {}

    sections = {
        "goals": [],
        "outcomes": [],
        "acceptance_criteria": [],
        "other": [],
    }

    current_section = "other"
    for line in description.split("\n"):
        line_lower = line.lower().strip()

        if any(keyword in line_lower for keyword in ["goal", "objective", "business need"]):
            current_section = "goals"
        elif any(keyword in line_lower for keyword in ["outcome", "result", "deliver"]):
            current_section = "outcomes"
        elif any(
            keyword in line_lower for keyword in ["acceptance", "criteria", "definition of done"]
        ):
            current_section = "acceptance_criteria"

        if line.strip():
            sections[current_section].append(line.strip())

    return sections


def risk_level_style(level: str) -> str:
    """Get style for risk level."""
    if level == "Critical":
        return "red bold"
    elif level == "High":
        return "dark_orange bold"
    elif level == "Medium":
        return "yellow"
    else:
        return "green"


@click.command()
@click.option(
    "--objective",
    required=True,
    help="Name of objective to analyze",
)
@click.option(
    "--team",
    default=None,
    help="Filter to team objectives",
)
@click.option(
    "--art",
    default=None,
    help="ART name (optional)",
)
@click.option(
    "--show-dependencies",
    is_flag=True,
    help="Display blocking/blocked-by relationships",
)
@click.option(
    "--show-risks",
    is_flag=True,
    help="Detailed risk analysis",
)
@click.option(
    "--compare-to",
    default=None,
    help="Compare to another objective",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "markdown", "html"]),
    default="text",
    help="Output format",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    objective: str,
    team: str | None,
    art: str | None,
    show_dependencies: bool,
    show_risks: bool,
    compare_to: str | None,
    format: str,  # noqa: A002 - click convention
    verbose: bool,
) -> None:
    """
    Analyze a specific PI objective in detail.

    Shows objective description, linked features, dependencies, risks,
    and Jira correlation.

    Examples:
        objective-deep-dive --objective "API Performance"
        objective-deep-dive --objective "API Performance" --show-risks
        objective-deep-dive --objective "API Performance" --show-dependencies
        objective-deep-dive --objective "API Performance" --compare-to "Cache Layer"
    """
    try:
        client = TPAPIClient(verbose=verbose)

        # Find objective
        console.print(f"[bold]Loading objective:[/bold] {objective}")
        all_objectives = client.get_program_pi_objectives()
        obj_list = [o for o in all_objectives if o.name == objective]

        if not obj_list:
            click.echo(f"[red]Error:[/red] Objective not found: {objective}", err=True)
            sys.exit(1)

        obj = obj_list[0]

        # Get features linked to objective
        console.print("[bold]Loading linked features...[/bold]")
        features = client.get_features()

        # Filter features linked to this objective (if there's a relationship)
        linked_features = [f for f in features if f.parent_epic_id == obj.id]

        # Perform risk assessment if requested
        risk_assessment = None
        if show_risks:
            console.print("[bold]Assessing risks...[/bold]")
            risk_assessment = RiskAnalyzer.assess_objective(obj, all_objectives, linked_features)

        # Output results
        if format == "json":
            _output_json(obj, linked_features, risk_assessment)
        elif format == "markdown":
            _output_markdown(obj, linked_features, risk_assessment)
        elif format == "html":
            _output_html(obj, linked_features, risk_assessment)
        else:
            _output_text(obj, linked_features, risk_assessment)

        console.print("\n[green]✓ Analysis complete[/green]")

    except TPAPIError as e:
        click.echo(f"[red]API Error:[/red] {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        click.echo(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


def _output_text(obj, linked_features, risk_assessment) -> None:  # noqa: C901
    """Output analysis as formatted text."""
    console.print(f"\n[bold cyan]=== Objective Deep-Dive: {obj.name} ===[/bold cyan]\n")

    # Objective Overview
    console.print("[bold]Objective Overview[/bold]")
    overview_table = Table(show_header=True, header_style="bold magenta")
    overview_table.add_column("Property", style="cyan")
    overview_table.add_column("Value")

    overview_table.add_row("Name", obj.name)
    overview_table.add_row("Status", obj.status)
    overview_table.add_row("Effort", str(obj.effort))
    overview_table.add_row(
        "Owner",
        f"{obj.owner.first_name} {obj.owner.last_name}" if obj.owner else "N/A",
    )
    overview_table.add_row("Release", obj.release_name or "N/A")
    if obj.start_date:
        overview_table.add_row("Start Date", obj.start_date.strftime("%Y-%m-%d"))
    if obj.end_date:
        overview_table.add_row("End Date", obj.end_date.strftime("%Y-%m-%d"))

    console.print(overview_table)

    # Description
    if obj.description:
        console.print("\n[bold]Description[/bold]")
        desc_sections = parse_description(obj.description)

        if desc_sections.get("goals"):
            console.print("\n[cyan]Goals:[/cyan]")
            for goal in desc_sections["goals"]:
                console.print(f"  • {goal}")

        if desc_sections.get("outcomes"):
            console.print("\n[cyan]Outcomes:[/cyan]")
            for outcome in desc_sections["outcomes"]:
                console.print(f"  • {outcome}")

        if desc_sections.get("acceptance_criteria"):
            console.print("\n[cyan]Acceptance Criteria:[/cyan]")
            for criteria in desc_sections["acceptance_criteria"]:
                console.print(f"  • {criteria}")

    # Linked Features
    console.print(f"\n[bold]Linked Features ({len(linked_features)})[/bold]")
    if linked_features:
        feat_table = Table(show_header=True, header_style="bold magenta")
        feat_table.add_column("Feature", style="cyan")
        feat_table.add_column("Status")
        feat_table.add_column("Effort")
        feat_table.add_column("Owner")

        for feat in linked_features:
            feat_table.add_row(
                feat.name,
                feat.status,
                str(feat.effort),
                feat.owner.first_name if feat.owner else "N/A",
            )

        console.print(feat_table)
    else:
        console.print("[yellow]No linked features found[/yellow]")

    # Risk Assessment
    if risk_assessment:
        console.print("\n[bold]Risk Assessment[/bold]")
        risk_table = Table(show_header=True, header_style="bold magenta")
        risk_table.add_column("Risk", style="cyan")
        risk_table.add_column("Level")
        risk_table.add_column("Category")
        risk_table.add_column("Description")

        for risk in risk_assessment.identified_risks:
            risk_table.add_row(
                risk.title,
                Text(risk.level.value, style=risk_level_style(risk.level.value)),
                risk.category.value,
                risk.description[:50] + "..." if len(risk.description) > 50 else risk.description,
            )

        console.print(risk_table)

        # Health Score
        console.print("\n[bold]Health Metrics[/bold]")
        health_table = Table(show_header=True, header_style="bold magenta")
        health_table.add_column("Metric", style="cyan")
        health_table.add_column("Value")

        health_table.add_row(
            "Health Score",
            format_health_score(risk_assessment.health_score),
        )
        health_table.add_row(
            "Critical Risks",
            Text(str(risk_assessment.critical_risk_count), style="red")
            if risk_assessment.critical_risk_count > 0
            else str(risk_assessment.critical_risk_count),
        )
        health_table.add_row(
            "High Risks",
            Text(str(risk_assessment.high_risk_count), style="dark_orange")
            if risk_assessment.high_risk_count > 0
            else str(risk_assessment.high_risk_count),
        )
        health_table.add_row(
            "Escalation Required",
            Text("YES", style="red bold") if risk_assessment.escalation_required else "No",
        )

        console.print(health_table)

        # Recommendations
        if risk_assessment.recommendations:
            console.print("\n[bold]Recommendations[/bold]")
            for rec in risk_assessment.recommendations:
                console.print(f"  • {rec}")


def format_health_score(score: float) -> Text:
    """Format health score with color."""
    if score >= 80:
        return Text(f"{score:.0f}/100", style="green")
    elif score >= 60:
        return Text(f"{score:.0f}/100", style="yellow")
    elif score >= 40:
        return Text(f"{score:.0f}/100", style="dark_orange")
    else:
        return Text(f"{score:.0f}/100", style="red bold")


def _output_json(obj, linked_features, risk_assessment) -> None:
    """Output analysis as JSON."""
    import json

    output = {
        "objective": {
            "id": obj.id,
            "name": obj.name,
            "status": obj.status,
            "effort": obj.effort,
            "description": obj.description,
        },
        "features": [
            {
                "id": f.id,
                "name": f.name,
                "status": f.status,
                "effort": f.effort,
            }
            for f in linked_features
        ],
    }

    if risk_assessment:
        output["risk_assessment"] = {
            "health_score": risk_assessment.health_score,
            "total_risk_count": risk_assessment.total_risk_count,
            "critical_risk_count": risk_assessment.critical_risk_count,
            "high_risk_count": risk_assessment.high_risk_count,
            "medium_risk_count": risk_assessment.medium_risk_count,
            "low_risk_count": risk_assessment.low_risk_count,
            "escalation_required": risk_assessment.escalation_required,
            "recommendations": risk_assessment.recommendations,
            "identified_risks": [
                {
                    "title": r.title,
                    "level": r.level.value,
                    "category": r.category.value,
                    "description": r.description,
                }
                for r in risk_assessment.identified_risks
            ],
        }

    console.print(json.dumps(output, indent=2))


def _output_markdown(obj, linked_features, risk_assessment) -> None:
    """Output analysis as Markdown."""
    console.print(f"\n# Objective Deep-Dive: {obj.name}\n")

    console.print("## Overview\n")
    console.print(f"- **Status:** {obj.status}")
    console.print(f"- **Effort:** {obj.effort} points")
    console.print(f"- **Owner:** {obj.owner.first_name if obj.owner else 'N/A'}")
    console.print(f"- **Release:** {obj.release_name or 'N/A'}\n")

    if obj.description:
        console.print("## Description\n")
        console.print(f"{obj.description}\n")

    console.print(f"## Features ({len(linked_features)})\n")
    for feat in linked_features:
        console.print(f"- **{feat.name}** - {feat.status} ({feat.effort} points)")

    if risk_assessment:
        console.print("\n## Risk Assessment\n")
        console.print(f"- **Health Score:** {risk_assessment.health_score:.0f}/100")
        console.print(f"- **Critical Risks:** {risk_assessment.critical_risk_count}")
        console.print(f"- **High Risks:** {risk_assessment.high_risk_count}")
        console.print(
            f"- **Escalation Required:** {'Yes' if risk_assessment.escalation_required else 'No'}\n"
        )

        if risk_assessment.identified_risks:
            console.print("### Identified Risks\n")
            for risk in risk_assessment.identified_risks:
                console.print(f"- **{risk.title}** ({risk.level.value}): {risk.description}")

        if risk_assessment.recommendations:
            console.print("\n### Recommendations\n")
            for rec in risk_assessment.recommendations:
                console.print(f"- {rec}")


def _output_html(obj, linked_features, risk_assessment) -> None:
    """Output analysis as HTML."""
    html = f"""
    <html>
    <head><title>Objective Deep-Dive: {obj.name}</title></head>
    <body>
    <h1>Objective Deep-Dive: {obj.name}</h1>

    <h2>Overview</h2>
    <p><strong>Status:</strong> {obj.status}</p>
    <p><strong>Effort:</strong> {obj.effort} points</p>

    <h2>Features ({len(linked_features)})</h2>
    <ul>
    """

    for feat in linked_features:
        html += f"<li><strong>{feat.name}</strong> - {feat.status} ({feat.effort} points)</li>"

    html += "</ul>"

    if risk_assessment:
        html += f"""
        <h2>Risk Assessment</h2>
        <p><strong>Health Score:</strong> {risk_assessment.health_score:.0f}/100</p>
        <p><strong>Critical Risks:</strong> {risk_assessment.critical_risk_count}</p>
        """

    html += "</body></html>"
    console.print(html)


if __name__ == "__main__":
    main()
