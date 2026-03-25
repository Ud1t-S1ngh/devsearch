"""
Rich-powered terminal output for DevSearch.
Handles: spinner, live reasoning display, and final structured answer.
"""

from __future__ import annotations

import re
from contextlib import contextmanager

from rich import print as rprint
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme


THEME = Theme(
    {
        "action": "bold cyan",
        "query": "italic yellow",
        "observation": "dim white",
        "done": "bold green",
        "high": "bold green",
        "medium": "bold yellow",
        "low": "bold red",
        "source": "cyan underline",
        "header": "bold magenta",
        "elapsed": "dim white",
    }
)

console = Console(theme=THEME)


LOGO = """[bold cyan]
 ██████╗ ███████╗██╗   ██╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
 ██╔══██╗██╔════╝██║   ██║██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
 ██║  ██║█████╗  ██║   ██║███████╗█████╗  ███████║██████╔╝██║     ███████║
 ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
 ██████╔╝███████╗ ╚████╔╝ ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
 ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
[/bold cyan][dim]  AI-powered coding research · SO + Docs + GitHub + Web[/dim]
"""


def print_logo():
    console.print(LOGO)



_reasoning_lines: list[str] = []


def reasoning_print(text: str, style: str):
    """Callback passed to the agent for live reasoning display."""
    _reasoning_lines.append((text, style))
    if style == "action":
        console.print(f"  [action]→ {text}[/action]")
    elif style == "query":
        console.print(f"    [query]{text}[/query]")
    elif style == "observation":
        console.print(f"    [observation]{text}[/observation]")
    elif style == "done":
        console.print(f"  [done]✓ {text}[/done]")



@contextmanager
def searching_spinner(query: str):
    """Show a spinner while the agent is working (non-verbose mode)."""
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[cyan]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Researching: {query[:60]}{'...' if len(query) > 60 else ''}", total=None)
        yield progress



def print_reasoning_header(query: str):
    console.print()
    console.print(Rule("[bold cyan]🔍 Agent Reasoning[/bold cyan]", style="cyan"))
    console.print(f"[dim]Query: {query}[/dim]")
    console.print()



def _extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """Extract (language, code) pairs from fenced code blocks."""
    pattern = r"```(\w*)\n?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or "text", code.strip()) for lang, code in matches]


def _confidence_style(level: str) -> str:
    mapping = {"high": "high", "medium": "medium", "low": "low"}
    return mapping.get(level.lower(), "dim")


def _confidence_icon(level: str) -> str:
    return {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(level.lower(), "⚪")


def render_answer(parsed: dict, query: str):
    """Render the full structured answer to the terminal."""
    console.print()
    console.print(Rule("[bold magenta]📋 DevSearch Answer[/bold magenta]", style="magenta"))
    console.print()


    if parsed.get("explanation"):
        console.print(
            Panel(
                Text(parsed["explanation"], style="white"),
                title="[bold]Explanation[/bold]",
                border_style="blue",
                padding=(1, 2),
            )
        )
        console.print()


    code_text = parsed.get("code", "")
    if code_text:
        blocks = _extract_code_blocks(code_text)
        if blocks:
            for lang, code in blocks:
                console.print(
                    Panel(
                        Syntax(code, lang, theme="monokai", line_numbers=True, word_wrap=True),
                        title=f"[bold green]Code[/bold green] [dim]({lang})[/dim]",
                        border_style="green",
                        padding=(0, 1),
                    )
                )
        else:
            console.print(
                Panel(
                    Syntax(code_text, "text", theme="monokai", word_wrap=True),
                    title="[bold green]Code[/bold green]",
                    border_style="green",
                    padding=(0, 1),
                )
            )
        console.print()

    sources = parsed.get("sources", [])
    if sources:
        table = Table(
            title="Sources",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
            expand=False,
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Source", style="cyan")

        for i, src in enumerate(sources[:6], 1):
            table.add_row(str(i), src)

        console.print(table)
        console.print()

    level = parsed.get("confidence", "Low")
    reason = parsed.get("reason", "")
    c_style = _confidence_style(level)
    icon = _confidence_icon(level)

    confidence_text = Text()
    confidence_text.append(f"{icon} Confidence: ", style="bold")
    confidence_text.append(level, style=c_style)
    if reason:
        confidence_text.append(f"  —  {reason}", style="dim")

    console.print(
        Panel(confidence_text, border_style="dim", padding=(0, 2))
    )

    elapsed = parsed.get("elapsed", 0)
    console.print()
    console.print(f"[elapsed]  ⏱  Completed in {elapsed}s[/elapsed]")
    console.print()



def render_error(message: str):
    console.print()
    console.print(
        Panel(
            Text(message, style="bold red"),
            title="[red]Error[/red]",
            border_style="red",
        )
    )
    console.print()


def render_not_found(query: str):
    """Graceful 'not found' display with manual links."""
    console.print()
    console.print(
        Panel(
            f"[yellow]No confident answer found for:[/yellow]\n[bold]{query}[/bold]\n\n"
            f"[dim]Try searching manually:[/dim]\n"
            f"  • [cyan]https://stackoverflow.com/search?q={query.replace(' ', '+')}[/cyan]\n"
            f"  • [cyan]https://github.com/search?q={query.replace(' ', '+')}&type=issues[/cyan]\n"
            f"  • [cyan]https://www.google.com/search?q={query.replace(' ', '+')}[/cyan]",
            title="[yellow]Not Found[/yellow]",
            border_style="yellow",
        )
    )
