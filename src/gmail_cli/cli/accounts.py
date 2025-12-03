"""Account management CLI commands."""

import typer

from gmail_cli.services.credentials import get_default_account, list_accounts
from gmail_cli.utils.output import is_json_mode, print_error, print_json

accounts_app = typer.Typer(
    name="accounts",
    help="Manage Gmail accounts.",
    no_args_is_help=True,
)


@accounts_app.command("list")
def list_command() -> None:
    """List all configured accounts.

    The default account is marked with an asterisk (*).

    Examples:
        gmail accounts list
    """
    accounts = list_accounts()
    default = get_default_account()

    if not accounts:
        if is_json_mode():
            print_json({"accounts": []})
        else:
            print_error(
                "Keine Konten konfiguriert",
                tip="Führe 'gmail auth login' aus um dich anzumelden.",
            )
        raise typer.Exit(1)

    if is_json_mode():
        print_json(
            {
                "accounts": [
                    {"email": acc, "is_default": acc == default} for acc in accounts
                ],
                "default": default,
            }
        )
    else:
        for acc in accounts:
            marker = " *" if acc == default else ""
            typer.echo(f"{acc}{marker}")
