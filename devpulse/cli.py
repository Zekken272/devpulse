"""DevPulse CLI — entry point for all commands."""

import typer
from typing import Optional
from rich.console import Console

from devpulse import __version__
from devpulse.config import load_config
from devpulse.git_utils import get_diff
from devpulse.reviewer import review_diff
from devpulse.formatter import (
    print_review,
    print_error,
    print_empty_diff,
    show_spinner,
)

app = typer.Typer(
    name="devpulse",
    help="🔍 Local AI-powered code review — no cloud, no leaks.",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[cyan]DevPulse[/cyan] version [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """DevPulse — Local AI code review CLI."""
    pass


@app.command()
def review(
    staged: bool = typer.Option(
        False,
        "--staged",
        "-s",
        help="Review only staged (git add) changes.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Ollama model to use (e.g. mistral, codellama).",
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        "-p",
        help="Plain text output, no colors (useful for piping).",
    ),
    max_lines: Optional[int] = typer.Option(
        None,
        "--max-lines",
        help="Max diff lines to send to the model.",
    ),
    config_path: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to a custom .devpulse.toml config file.",
    ),
    fail_on_security: bool = typer.Option(
        False,
        "--fail-on-security",
        help="Exit with code 1 if any security issues are found.",
    ),
) -> None:
    """
    Review the current git diff using a local AI model.

    By default, reviews all unstaged changes. Use --staged for staged changes.
    """
    # Load config (CLI flags override config file values)
    cfg = load_config(config_path)
    resolved_model = model or cfg.model
    resolved_max_lines = max_lines or cfg.max_lines

    # Get the diff
    try:
        diff = get_diff(staged=staged, max_lines=resolved_max_lines)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    if not diff:
        print_empty_diff()
        raise typer.Exit(code=0)

    # Run the AI review with a spinner
    with show_spinner(f"Reviewing with [bold]{resolved_model}[/bold]..."):
        result = review_diff(
            diff=diff,
            model=resolved_model,
            language=cfg.review_language,
        )

    # Handle errors from the reviewer
    if result.has_error:
        print_error(result.error)
        raise typer.Exit(code=1)

    # Print the review
    print_review(result, plain=plain)

    # Exit with error code if security issues found and flag is set
    if fail_on_security and result.security_count > 0:
        console.print(
            "[bold red]Exiting with code 1 — security issues detected.[/bold red]"
        )
        raise typer.Exit(code=1)


@app.command()
def diff(
    staged: bool = typer.Option(
        False,
        "--staged",
        "-s",
        help="Show only staged changes.",
    ),
    max_lines: Optional[int] = typer.Option(
        500,
        "--max-lines",
        help="Max lines to display.",
    ),
) -> None:
    """
    Show the current git diff that DevPulse would review.
    Useful for debugging what will be sent to the AI.
    """
    try:
        result = get_diff(staged=staged, max_lines=max_lines)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    if not result:
        print_empty_diff()
        return

    console.print(result)


@app.command()
def models() -> None:
    """List all Ollama models available for review."""
    from devpulse.reviewer import list_available_models, check_ollama_running

    if not check_ollama_running():
        print_error(
            "Ollama is not running.\nStart it with: [bold]ollama serve[/bold]"
        )
        raise typer.Exit(code=1)

    available = list_available_models()

    if not available:
        console.print("[yellow]No models found. Pull one with:[/yellow]")
        console.print("  [bold]ollama pull mistral[/bold]")
        return

    console.print("\n[bold cyan]Available Ollama Models:[/bold cyan]\n")
    for m in available:
        console.print(f"  [green]✓[/green] {m}")
    console.print()