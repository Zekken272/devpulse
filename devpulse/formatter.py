"""Rich terminal output formatter for DevPulse."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box
from rich.spinner import Spinner
from rich.live import Live
import time

from devpulse.reviewer import ReviewResult

console = Console()


def print_header(model: str) -> None:
    """Print the DevPulse banner."""
    console.print()
    console.print(
        "[bold cyan]DevPulse[/bold cyan] [dim]🔍 Local AI Code Review[/dim]",
        justify="center",
    )
    console.print(
        f"[dim]Model: {model}[/dim]",
        justify="center",
    )
    console.print(Rule(style="cyan"))
    console.print()


def print_error(message: str) -> None:
    """Print a formatted error panel."""
    console.print()
    console.print(
        Panel(
            f"[bold red]{message}[/bold red]",
            title="[red]❌ Error[/red]",
            border_style="red",
        )
    )
    console.print()


def print_empty_diff() -> None:
    """Inform the user there is nothing to review."""
    console.print()
    console.print(
        Panel(
            "[yellow]No changes detected.[/yellow]\n\n"
            "Make sure you have uncommitted changes, or use [bold]--staged[/bold] "
            "to review staged changes.",
            title="[yellow]⚠ Nothing to Review[/yellow]",
            border_style="yellow",
        )
    )
    console.print()


def _section_panel(
    title: str,
    content: str,
    border_color: str,
    icon: str,
) -> Panel:
    """Build a single review section panel."""
    is_empty = not content or content.strip() == "None found."
    body = (
        f"[dim italic]None found.[/dim italic]"
        if is_empty
        else content.strip()
    )
    return Panel(
        body,
        title=f"[bold {border_color}]{icon} {title}[/bold {border_color}]",
        border_style=border_color,
        padding=(1, 2),
    )


def print_review(result: ReviewResult, plain: bool = False) -> None:
    """
    Render the full review result to the terminal.

    Args:
        result: The ReviewResult from the AI reviewer.
        plain: If True, print plain text without Rich formatting.
    """
    if plain:
        _print_plain(result)
        return

    print_header(result.model)

    # Issues panel
    console.print(
        _section_panel(
            "Issues",
            result.issues,
            "red",
            "🐛",
        )
    )

    # Suggestions panel
    console.print(
        _section_panel(
            "Suggestions",
            result.suggestions,
            "yellow",
            "💡",
        )
    )

    # Security panel
    security_color = "bright_red" if result.security_count > 0 else "green"
    console.print(
        _section_panel(
            "Security",
            result.security,
            security_color,
            "🔒",
        )
    )

    # Summary panel
    if result.summary:
        console.print(
            Panel(
                f"[italic]{result.summary.strip()}[/italic]",
                title="[bold blue]📋 Summary[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Stats table
    console.print()
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold dim")
    table.add_column("Category", style="dim")
    table.add_column("Count", justify="center")

    issues_style = "red" if result.issue_count > 0 else "green"
    security_style = "bright_red" if result.security_count > 0 else "green"

    table.add_row(
        "🐛 Issues",
        f"[{issues_style}]{result.issue_count}[/{issues_style}]",
    )
    table.add_row(
        "💡 Suggestions",
        f"[yellow]{result.suggestion_count}[/yellow]",
    )
    table.add_row(
        "🔒 Security Flags",
        f"[{security_style}]{result.security_count}[/{security_style}]",
    )

    console.print(table)
    console.print()


def _print_plain(result: ReviewResult) -> None:
    """Plain text output for piping or CI environments."""
    print(f"=== DevPulse Review (model: {result.model}) ===\n")
    print("ISSUES\n------")
    print(result.issues or "None found.")
    print("\nSUGGESTIONS\n-----------")
    print(result.suggestions or "None found.")
    print("\nSECURITY\n--------")
    print(result.security or "None found.")
    print("\nSUMMARY\n-------")
    print(result.summary or "N/A")
    print(f"\nStats: {result.issue_count} issues | "
          f"{result.suggestion_count} suggestions | "
          f"{result.security_count} security flags")


def show_spinner(message: str = "Reviewing with AI...") -> Live:
    """
    Return a Rich Live context manager showing a spinner.
    Usage:
        with show_spinner():
            result = review_diff(...)
    """
    spinner = Spinner("dots", text=f"[cyan]{message}[/cyan]")
    return Live(spinner, console=console, refresh_per_second=10)