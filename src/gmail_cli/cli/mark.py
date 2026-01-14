"""Mark CLI command for marking emails as read/unread."""

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
    print_json_error,
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


@require_auth
def mark_command(
    message_ids: Annotated[
        list[str],
        typer.Argument(
            help="Message ID(s) to mark.",
        ),
    ],
    read: Annotated[
        bool,
        typer.Option(
            "--read",
            "-r",
            help="Mark as read.",
        ),
    ] = False,
    unread: Annotated[
        bool,
        typer.Option(
            "--unread",
            "-u",
            help="Mark as unread.",
        ),
    ] = False,
    account: AccountOption = None,
) -> None:
    """Mark email(s) as read or unread.

    Examples:
        gmail mark 18c1234abcd5678 --read
        gmail mark 18c1234abcd5678 --unread
        gmail mark 18c1234 18c5678 18c9012 --read
        gmail mark 18c1234abcd5678 --read --account work@company.com
    """
    # Validate: exactly one of --read or --unread must be specified
    if read == unread:
        if is_json_mode():
            print_json_error(
                "INVALID_ARGUMENTS",
                "Specify either --read or --unread (not both, not neither)",
            )
        else:
            print_error("Specify either --read or --unread (not both, not neither)")
        raise typer.Exit(1)

    account = resolve_account(account)
    action = "read" if read else "unread"
    action_de = "gelesen" if read else "ungelesen"
    mark_fn = mark_as_read if read else mark_as_unread

    results = []
    success_count = 0
    error_count = 0

    for msg_id in message_ids:
        try:
            mark_fn(msg_id, account=account)
            success_count += 1
            results.append({"id": msg_id, "status": "success", "action": action})
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
        # Summary for bulk operations
        typer.echo(f"\n{success_count}/{len(message_ids)} Nachrichten als {action_de} markiert")

    if error_count > 0:
        raise typer.Exit(1)
