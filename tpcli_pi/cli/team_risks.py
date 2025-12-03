"""Team Risks CLI command - Show risks for a team."""

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


def get_severity_color(severity: str | None) -> str:
    """Return color based on severity level."""
    if not severity:
        return "dim"
    severity_lower = severity.lower()
    if "critical" in severity_lower or "1 -" in severity_lower:
        return "red"
    elif "high" in severity_lower or "2 -" in severity_lower:
        return "yellow"
    elif "medium" in severity_lower or "3 -" in severity_lower:
        return "yellow"
    else:
        return "dim"


def format_severity(severity: str | None) -> Text:
    """Format severity with color."""
    if not severity:
        return Text("N/A", style="dim")
    return Text(severity, style=get_severity_color(severity))


def extract_custom_field(custom_fields: list, field_name: str) -> str | None:
    """Extract custom field value from TP response."""
    if not custom_fields:
        return None
    for field in custom_fields:
        if field.get("Name") == field_name:
            return field.get("Value")
    return None


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
    "--severity",
    type=click.Choice(["all", "critical", "high", "medium", "low"]),
    default="all",
    help="Filter by severity",
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
    severity: str,
    format: str,
    verbose: bool,
):
    """Display risks for a team."""
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

        # Query risks for this team/release
        # Note: We query via tpcli and parse the JSON response
        where_clauses = []
        if team_obj.id:
            where_clauses.append(f"Team.Id eq {team_obj.id}")
        if release_obj and release_obj.id:
            where_clauses.append(f"AgileReleaseTrain.Id eq {art_obj.id}" if art_obj else "")

        where_query = " and ".join([w for w in where_clauses if w])

        # Use the client to run a tpcli query for risks
        args = []
        if where_query:
            args = ["--where", where_query]

        # Get all risks and filter by team manually
        cached = client._get_cached("Risks", args)
        if cached is None:
            cached = client._run_tpcli("Risks", args)
            client._set_cached("Risks", cached, args)

        # Filter risks by team
        risks = []
        for risk in cached:
            if risk.get("Team", {}).get("Id") == team_obj.id or (
                release_obj and risk.get("Release", {}).get("Id") == release_obj.id
            ):
                risks.append(risk)

        if not risks:
            console.print(
                f"[yellow]No risks found for team '{team_obj.name}'"
                + (f" in PI '{release_obj.name}'" if release_obj else "")
                + "[/yellow]"
            )
            return

        # Parse severity from custom fields
        parsed_risks = []
        for risk in risks:
            risk_severity = extract_custom_field(risk.get("CustomFields", []), "Severity")
            risk_impact = extract_custom_field(risk.get("CustomFields", []), "Impact")
            risk_likelihood = extract_custom_field(risk.get("CustomFields", []), "Likelihood")

            parsed_risks.append({
                "id": risk.get("Id"),
                "name": risk.get("Name"),
                "severity": risk_severity,
                "impact": risk_impact,
                "likelihood": risk_likelihood,
                "owner": risk.get("Owner", {}).get("FullName") if risk.get("Owner") else None,
                "status": risk.get("EntityState", {}).get("Name"),
                "description": risk.get("Description"),
                "mitigation": extract_custom_field(risk.get("CustomFields", []), "Mitigation Plan"),
            })

        # Filter by severity if needed
        if severity != "all":
            parsed_risks = [r for r in parsed_risks if severity.lower() in (r["severity"] or "").lower()]

        # Sort by severity
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

        def get_severity_order(risk):
            sev = risk["severity"] or ""
            for key in severity_order:
                if key.lower() in sev.lower():
                    return severity_order[key]
            return 999

        parsed_risks.sort(key=get_severity_order)

        if format == "json":
            data = [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "severity": r["severity"],
                    "impact": r["impact"],
                    "likelihood": r["likelihood"],
                    "owner": r["owner"],
                    "status": r["status"],
                }
                for r in parsed_risks
            ]
            console.print(json.dumps(data, indent=2))
        elif format == "csv":
            console.print("Name,Severity,Impact,Likelihood,Owner,Status")
            for r in parsed_risks:
                console.print(
                    f"{r['name']},{r['severity']},{r['impact']},{r['likelihood']},"
                    f"{r['owner']},{r['status']}"
                )
        else:  # text format
            title = f"{team_obj.name} Risk Register"
            if release_obj:
                title += f" | {release_obj.name}"

            console.print(f"[bold cyan]{title}[/bold cyan]")
            console.print()

            table = Table(title=f"Risks ({len(parsed_risks)} Total)")
            table.add_column("Risk", style="cyan")
            table.add_column("Severity", style="white")
            table.add_column("Impact", style="white")
            table.add_column("Likelihood", style="white")
            table.add_column("Owner", style="yellow")
            table.add_column("Status", style="white")

            for r in parsed_risks:
                table.add_row(
                    r["name"],
                    format_severity(r["severity"]),
                    r["impact"] or "N/A",
                    r["likelihood"] or "N/A",
                    r["owner"] or "Unassigned",
                    r["status"] or "N/A",
                )

            console.print(table)

            # Summary
            console.print()
            critical = len([r for r in parsed_risks if "critical" in (r["severity"] or "").lower()])
            high = len([r for r in parsed_risks if "high" in (r["severity"] or "").lower()])
            medium = len([r for r in parsed_risks if "medium" in (r["severity"] or "").lower()])

            summary = f"[dim]Total: {len(parsed_risks)} risks | "
            if critical:
                summary += f"[red]Critical: {critical}[/red] | "
            if high:
                summary += f"[yellow]High: {high}[/yellow] | "
            if medium:
                summary += f"[yellow]Medium: {medium}[/yellow]"
            summary += "[/dim]"
            console.print(summary)

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
