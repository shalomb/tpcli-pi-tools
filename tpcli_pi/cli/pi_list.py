"""PI List CLI command - List all PIs with timeline and status."""

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


def format_status(release) -> Text:
    """Return colored status based on release dates."""
    today = datetime.now().date()
    start = release.start_date.date()
    end = release.end_date.date()

    if today < start:
        return Text("Upcoming", style="blue")
    elif today > end:
        return Text("Closed", style="dim")
    else:
        return Text("In Progress", style="green")


def format_duration(release) -> str:
    """Format duration in days."""
    delta = (release.end_date - release.start_date).days
    return f"{delta} days"


def format_time_remaining(release) -> str:
    """Format time remaining in PI."""
    today = datetime.now().date()
    end = release.end_date.date()
    remaining = (end - today).days

    if remaining < 0:
        return f"{abs(remaining)} days ago"
    elif remaining == 0:
        return "Ends today"
    elif remaining == 1:
        return "1 day left"
    else:
        return f"{remaining} days left"


@click.command()
@click.option(
    "--art",
    required=False,
    default=None,
    help="Name of Agile Release Train to filter by (defaults to default-art in config)",
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
def main(art: str, format: str, verbose: bool):
    """List all PIs (Releases) with timeline information."""
    try:
        client = TPAPIClient(verbose=verbose)

        # Get default ART if not specified
        if not art:
            default_art = get_default_art()
            if default_art:
                art = default_art
                if verbose:
                    console.print(f"[dim]Using default ART: {art}[/dim]")

        # Get releases
        if art:
            # Get ART ID
            art_obj = client.get_art_by_name(art)
            if not art_obj:
                console.print(f"[red]Error: ART '{art}' not found[/red]", file=sys.stderr)
                sys.exit(1)
            releases = client.get_releases(art_id=art_obj.id)
        else:
            # Get all releases from all ARTs
            releases = client.get_releases()

        if not releases:
            console.print("[yellow]No PIs found[/yellow]")
            return

        if format == "json":
            import json
            data = [
                {
                    "id": r.id,
                    "name": r.name,
                    "start_date": r.start_date.isoformat(),
                    "end_date": r.end_date.isoformat(),
                    "art_name": r.art_name,
                }
                for r in releases
            ]
            console.print(json.dumps(data, indent=2))
        elif format == "csv":
            console.print("Name,Start Date,End Date,Status,Duration,ART")
            for release in releases:
                status_text = "Upcoming" if datetime.now().date() < release.start_date.date() else (
                    "Closed" if datetime.now().date() > release.end_date.date() else "In Progress"
                )
                console.print(
                    f"{release.name},{format_date(release.start_date)},{format_date(release.end_date)},"
                    f"{status_text},{format_duration(release)},{release.art_name}"
                )
        else:  # text format
            table = Table(title="Program Increments (PIs)")
            table.add_column("PI Name", style="cyan")
            table.add_column("Start Date", style="white")
            table.add_column("End Date", style="white")
            table.add_column("Status", style="white")
            table.add_column("Duration", style="dim")
            table.add_column("Time Remaining", style="yellow")
            table.add_column("ART", style="magenta")

            for release in sorted(releases, key=lambda r: r.start_date):
                table.add_row(
                    release.name,
                    format_date(release.start_date),
                    format_date(release.end_date),
                    format_status(release),
                    format_duration(release),
                    format_time_remaining(release),
                    release.art_name,
                )

            console.print(table)

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
