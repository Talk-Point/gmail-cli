"""Draft CLI commands."""

from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.gmail import (
    DraftNotFoundError,
    SendError,
    delete_draft,
    get_draft,
    list_drafts,
    send_draft,
)
from gmail_cli.utils.output import (
    is_json_mode,
    print_error,
    print_info,
    print_json,
    print_json_error,
    print_success,
    print_warning,
)

draft_app = typer.Typer(
    name="draft",
    help="Manage email drafts.",
    no_args_is_help=True,
)

# Account option type
AccountOption = Annotated[
    str | None,
    typer.Option(
        "--account",
        "-A",
        help="Account email to use. Defaults to the default account.",
    ),
]


@draft_app.command("list")
@require_auth
def list_command(
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            "--max-results",
            "--count",
            help="Maximum number of drafts to show.",
        ),
    ] = 20,
    account: AccountOption = None,
) -> None:
    """List all drafts.

    Examples:
        gmail draft list
        gmail draft list --limit 10
        gmail draft list --json
        gmail draft list --account work@company.com
    """
    drafts = list_drafts(account=account, max_results=limit)

    if is_json_mode():
        print_json(
            {
                "drafts": drafts,
                "count": len(drafts),
            }
        )
    else:
        if not drafts:
            print_warning("Keine Entwürfe vorhanden.")
            return

        print_info(f"Entwürfe ({len(drafts)}):")
        for draft in drafts:
            draft_id = draft["id"]
            to = draft.get("to", "") or "(kein Empfänger)"
            subject = draft.get("subject", "(kein Betreff)")
            # Truncate for display
            if len(to) > 30:
                to = to[:27] + "..."
            if len(subject) > 40:
                subject = subject[:37] + "..."
            print(f"  {draft_id}  {to:<30}  {subject}")


@draft_app.command("show")
@require_auth
def show_command(
    draft_id: Annotated[
        str,
        typer.Argument(
            help="The draft ID to show.",
        ),
    ],
    account: AccountOption = None,
) -> None:
    """Show draft details.

    Examples:
        gmail draft show r1234567890
        gmail draft show r1234567890 --json
        gmail draft show r1234567890 --account work@company.com
    """
    try:
        draft = get_draft(draft_id, account=account, include_body=True)
    except DraftNotFoundError as e:
        if is_json_mode():
            print_json_error("NOT_FOUND", e.message)
        else:
            print_error(e.message)
        raise typer.Exit(1)

    if is_json_mode():
        print_json(draft)
    else:
        print_info(f"Entwurf: {draft['id']}")
        print()
        print(f"An:      {draft.get('to', '(kein Empfänger)')}")
        if draft.get("cc"):
            print(f"Cc:      {draft['cc']}")
        print(f"Betreff: {draft.get('subject', '(kein Betreff)')}")
        if draft.get("thread_id"):
            print(f"Thread:  {draft['thread_id']}")
        print()

        # Show body
        body = draft.get("body_text") or draft.get("snippet", "")
        if body:
            print(body)

        # Show attachments
        attachments = draft.get("attachments", [])
        if attachments:
            print()
            print("Anhänge:")
            for att in attachments:
                size_mb = att["size"] / (1024 * 1024)
                print(f"  - {att['filename']} ({size_mb:.1f} MB)")


@draft_app.command("send")
@require_auth
def send_command(
    draft_id: Annotated[
        str,
        typer.Argument(
            help="The draft ID to send.",
        ),
    ],
    account: AccountOption = None,
) -> None:
    """Send an existing draft.

    Examples:
        gmail draft send r1234567890
        gmail draft send r1234567890 --account work@company.com
    """
    try:
        result = send_draft(draft_id, account=account)

        if is_json_mode():
            print_json(
                {
                    "status": "sent",
                    "message_id": result.get("id"),
                    "thread_id": result.get("threadId"),
                }
            )
        else:
            print_success("Entwurf gesendet!")
            print_info(f"Message-ID: {result.get('id')}")
            print_info(f"Thread-ID:  {result.get('threadId')}")

    except DraftNotFoundError as e:
        if is_json_mode():
            print_json_error("NOT_FOUND", e.message)
        else:
            print_error(e.message)
        raise typer.Exit(1)
    except SendError as e:
        if is_json_mode():
            print_json_error("SEND_FAILED", e.message)
        else:
            print_error("Entwurf konnte nicht gesendet werden", details=e.message)
        raise typer.Exit(1)


@draft_app.command("delete")
@require_auth
def delete_command(
    draft_id: Annotated[
        str,
        typer.Argument(
            help="The draft ID to delete.",
        ),
    ],
    account: AccountOption = None,
) -> None:
    """Delete a draft.

    Examples:
        gmail draft delete r1234567890
        gmail draft delete r1234567890 --account work@company.com
    """
    try:
        delete_draft(draft_id, account=account)

        if is_json_mode():
            print_json(
                {
                    "status": "deleted",
                    "draft_id": draft_id,
                }
            )
        else:
            print_success("Entwurf gelöscht.")

    except DraftNotFoundError as e:
        if is_json_mode():
            print_json_error("NOT_FOUND", e.message)
        else:
            print_error(e.message)
        raise typer.Exit(1)
