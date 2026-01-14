"""Search CLI command."""

from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.gmail import search_emails
from gmail_cli.utils.output import (
    is_json_mode,
    print_info,
    print_json,
    print_search_results,
)

# Shared account option type
AccountOption = Annotated[
    str | None,
    typer.Option(
        "--account",
        "-A",
        help="Account email to use. Defaults to the default account.",
    ),
]


@require_auth
def search_command(
    query: Annotated[
        str,
        typer.Argument(
            help="Search query string.",
        ),
    ] = "",
    from_addr: Annotated[
        str | None,
        typer.Option(
            "--from",
            "-f",
            help="Filter by sender email address.",
        ),
    ] = None,
    to_addr: Annotated[
        str | None,
        typer.Option(
            "--to",
            "-t",
            help="Filter by recipient email address.",
        ),
    ] = None,
    subject: Annotated[
        str | None,
        typer.Option(
            "--subject",
            "-s",
            help="Filter by subject.",
        ),
    ] = None,
    label: Annotated[
        str | None,
        typer.Option(
            "--label",
            "-l",
            help="Filter by label (e.g., INBOX, SENT, STARRED).",
        ),
    ] = None,
    after: Annotated[
        str | None,
        typer.Option(
            "--after",
            help="Filter emails after date (YYYY-MM-DD).",
        ),
    ] = None,
    before: Annotated[
        str | None,
        typer.Option(
            "--before",
            help="Filter emails before date (YYYY-MM-DD).",
        ),
    ] = None,
    has_attachment: Annotated[
        bool,
        typer.Option(
            "--has-attachment",
            "-a",
            help="Filter emails with attachments.",
        ),
    ] = False,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            "--max-results",
            "--count",
            help="Maximum number of results to return.",
        ),
    ] = 20,
    page: Annotated[
        str | None,
        typer.Option(
            "--page",
            help="Page token for pagination.",
        ),
    ] = None,
    account: AccountOption = None,
) -> None:
    """Search emails with filters and pagination.

    Examples:
        gmail search "invoice"
        gmail search --from sender@example.com
        gmail search --label INBOX --has-attachment
        gmail search --after 2025-01-01 --before 2025-12-31
        gmail search "project" --account work@company.com
    """
    result = search_emails(
        query=query,
        from_addr=from_addr,
        to_addr=to_addr,
        subject=subject,
        label=label,
        after=after,
        before=before,
        has_attachment=has_attachment,
        limit=limit,
        page_token=page,
        account=account,
    )

    if is_json_mode():
        print_json(
            {
                "emails": [
                    {
                        "id": email.id,
                        "thread_id": email.thread_id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "date": email.date.isoformat(),
                        "snippet": email.snippet,
                        "is_read": email.is_read,
                        "labels": email.labels,
                    }
                    for email in result.emails
                ],
                "total_estimate": result.total_estimate,
                "next_page_token": result.next_page_token,
                "query": result.query,
            }
        )
    else:
        if not result.emails:
            print_info("Keine E-Mails gefunden.")
            return

        print_search_results(result)
