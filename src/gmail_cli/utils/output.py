"""Output formatting utilities using rich."""

import json
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError
# with special characters like ● ✓ ✗ ℹ 📎
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True if sys.platform == "win32" else None)

# Global flag for JSON output mode
_json_mode = False


def set_json_mode(enabled: bool) -> None:
    """Set global JSON output mode."""
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    """Check if JSON output mode is enabled."""
    return _json_mode


def print_success(message: str) -> None:
    """Print a success message."""
    if _json_mode:
        return
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str, details: str | None = None, tip: str | None = None) -> None:
    """Print an error message with optional details and tip."""
    if _json_mode:
        return
    console.print(f"[red]✗[/red] [bold]Fehler:[/bold] {message}")
    if details:
        console.print(f"  {details}")
    if tip:
        console.print(f"\n  [dim]Tipp: {tip}[/dim]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    if _json_mode:
        return
    console.print(f"[yellow]![/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    if _json_mode:
        return
    console.print(f"[blue]ℹ[/blue] {message}")


def print_json(data: dict[str, Any] | list[Any]) -> None:
    """Print data as formatted JSON."""
    console.print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


def print_json_error(code: str, message: str, details: str | None = None) -> None:
    """Print an error in JSON format."""
    error_data = {
        "error": True,
        "code": code,
        "message": message,
    }
    if details:
        error_data["details"] = details
    print_json(error_data)


def print_table(
    title: str | None,
    columns: list[str],
    rows: list[list[str]],
    footer: str | None = None,
) -> None:
    """Print a formatted table."""
    if _json_mode:
        return

    table = Table(title=title, show_header=True, header_style="bold")

    for column in columns:
        table.add_column(column)

    for row in rows:
        table.add_row(*row)

    console.print(table)

    if footer:
        console.print(f"\n[dim]{footer}[/dim]")


def print_email_header(
    sender: str,
    recipients: list[str],
    cc: list[str],
    date: str,
    subject: str,
) -> None:
    """Print formatted email header."""
    if _json_mode:
        return

    header_lines = [
        f"[bold]Von:[/bold]     {sender}",
        f"[bold]An:[/bold]      {', '.join(recipients)}",
    ]

    if cc:
        header_lines.append(f"[bold]CC:[/bold]      {', '.join(cc)}")

    header_lines.extend(
        [
            f"[bold]Datum:[/bold]   {date}",
            f"[bold]Betreff:[/bold] {subject}",
        ]
    )

    console.print(Panel("\n".join(header_lines), border_style="blue"))


def print_email_body(body: str) -> None:
    """Print formatted email body."""
    if _json_mode:
        return
    console.print(body)


def print_attachments_list(attachments: list[tuple[str, str]]) -> None:
    """Print list of attachments with name and size."""
    if _json_mode:
        return

    if not attachments:
        return

    console.print("\n[bold]Anhänge:[/bold]")
    for filename, size in attachments:
        console.print(f"  [blue]📎[/blue] {filename} ({size})")


def print_search_results(result: Any) -> None:
    """Print search results in a formatted table.

    Args:
        result: SearchResult object with emails and pagination info.
    """
    if _json_mode:
        return

    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("ID", style="dim", no_wrap=True, max_width=16)
    table.add_column("Status", width=2)
    table.add_column("Von", max_width=30)
    table.add_column("Betreff", max_width=40)
    table.add_column("Datum", no_wrap=True)

    for email in result.emails:
        # Format status indicator
        status = " " if email.is_read else "[bold blue]●[/bold blue]"

        # Format sender (extract name or email)
        sender = email.sender
        if "<" in sender:
            # Extract name before email, fallback to email if no name
            name_part = sender.split("<")[0].strip().strip('"')
            sender = name_part or sender.split("<")[1].rstrip(">")

        # Truncate if needed
        if len(sender) > 28:
            sender = sender[:25] + "..."

        # Format subject
        subject = email.subject
        if len(subject) > 38:
            subject = subject[:35] + "..."

        # Format date
        date_str = email.date.strftime("%d.%m.%Y %H:%M")

        # Truncate ID for display
        display_id = email.id[:16] if len(email.id) > 16 else email.id

        table.add_row(display_id, status, sender, subject, date_str)

    console.print(table)

    # Print pagination info
    footer_parts = []
    footer_parts.append(f"Gefunden: ~{result.total_estimate}")

    if result.next_page_token:
        footer_parts.append(f"Nächste Seite: --page {result.next_page_token}")

    console.print(f"\n[dim]{' | '.join(footer_parts)}[/dim]")


def print_email_detail(email: Any, body: str) -> None:
    """Print detailed email view.

    Args:
        email: Email object with full details.
        body: The body text to display (already converted from HTML if needed).
    """
    if _json_mode:
        return

    # Header panel
    print_email_header(
        sender=email.sender,
        recipients=email.recipients,
        cc=email.cc,
        date=email.date.strftime("%d.%m.%Y %H:%M"),
        subject=email.subject,
    )

    # Body
    console.print()
    console.print(body)

    # Attachments
    if email.attachments:
        print_attachments_list([(att.filename, att.size_human) for att in email.attachments])

    # Footer with metadata
    console.print()
    console.print(f"[dim]ID: {email.id} | Thread: {email.thread_id}[/dim]")
