"""Read CLI command."""

from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.gmail import get_email
from gmail_cli.utils.html import html_to_text
from gmail_cli.utils.output import (
    is_json_mode,
    print_email_detail,
    print_error,
    print_json,
    print_json_error,
)


@require_auth
def read_command(
    message_id: Annotated[
        str,
        typer.Argument(
            help="The email message ID to read.",
        ),
    ],
    raw: Annotated[
        bool,
        typer.Option(
            "--raw",
            "-r",
            help="Show raw body without HTML conversion.",
        ),
    ] = False,
) -> None:
    """Read a full email by its message ID.

    Examples:
        gmail read 18c1234abcd5678
        gmail read 18c1234abcd5678 --raw
    """
    email = get_email(message_id)

    if not email:
        if is_json_mode():
            print_json_error("NOT_FOUND", f"E-Mail mit ID '{message_id}' nicht gefunden")
        else:
            print_error(f"E-Mail mit ID '{message_id}' nicht gefunden")
        raise typer.Exit(1)

    if is_json_mode():
        print_json(
            {
                "id": email.id,
                "thread_id": email.thread_id,
                "subject": email.subject,
                "sender": email.sender,
                "recipients": email.recipients,
                "cc": email.cc,
                "date": email.date.isoformat(),
                "body_text": email.body_text,
                "body_html": email.body_html,
                "snippet": email.snippet,
                "labels": email.labels,
                "is_read": email.is_read,
                "attachments": [
                    {
                        "id": att.id,
                        "filename": att.filename,
                        "mime_type": att.mime_type,
                        "size": att.size,
                    }
                    for att in email.attachments
                ],
            }
        )
    else:
        # Determine body to display
        if raw:
            body = email.body_text or email.body_html
        elif email.body_text:
            body = email.body_text
        elif email.body_html:
            body = html_to_text(email.body_html)
        else:
            body = "(kein Inhalt)"

        print_email_detail(email, body)
