"""Mark CLI commands for marking emails as read/unread."""

from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.auth import resolve_account
from gmail_cli.services.gmail import (
    MessageNotFoundError,
    mark_as_read,
    mark_as_unread,
)
from gmail_cli.utils.output import (
    is_json_mode,
    print_error,
    print_json,
    print_success,
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


def _mark_messages(message_ids: list[str], account: str | None, as_read: bool) -> None:
    """Internal helper to mark messages as read or unread."""
    account = resolve_account(account)
    action = "read" if as_read else "unread"
    action_de = "gelesen" if as_read else "ungelesen"
    mark_fn = mark_as_read if as_read else mark_as_unread

    results = []
    success_count = 0
    error_count = 0

    for msg_id in message_ids:
        try:
            mark_fn(msg_id, account=account)
            success_count += 1
            results.append({"id": msg_id, "status": "success"})
            if not is_json_mode():
                print_success(f"{msg_id} als {action_de} markiert")
        except MessageNotFoundError:
            error_count += 1
            results.append({"id": msg_id, "status": "error", "error": "not_found"})
            if not is_json_mode():
                print_error(f"{msg_id}: Nachricht nicht gefunden")
        except Exception as e:
            error_count += 1
            results.append({"id": msg_id, "status": "error", "error": str(e)})
            if not is_json_mode():
                print_error(f"{msg_id}: {e}")

    if is_json_mode():
        print_json(
            {
                "action": action,
                "success_count": success_count,
                "error_count": error_count,
                "total": len(message_ids),
                "results": results,
            }
        )
    elif len(message_ids) > 1:
        typer.echo(f"\n{success_count}/{len(message_ids)} Nachrichten als {action_de} markiert")

    if error_count > 0:
        raise typer.Exit(1)


@require_auth
def mark_read_command(
    message_ids: Annotated[
        list[str],
        typer.Argument(help="Message ID(s) to mark as read."),
    ],
    account: AccountOption = None,
) -> None:
    """Mark email(s) as read.

    Examples:
        gmail mark-read 18c1234abcd5678
        gmail mark-read 18c1234 18c5678 18c9012
        gmail mark-read 18c1234abcd5678 --account work@company.com
    """
    _mark_messages(message_ids, account, as_read=True)


@require_auth
def mark_unread_command(
    message_ids: Annotated[
        list[str],
        typer.Argument(help="Message ID(s) to mark as unread."),
    ],
    account: AccountOption = None,
) -> None:
    """Mark email(s) as unread.

    Examples:
        gmail mark-unread 18c1234abcd5678
        gmail mark-unread 18c1234 18c5678 18c9012
        gmail mark-unread 18c1234abcd5678 --account work@company.com
    """
    _mark_messages(message_ids, account, as_read=False)
