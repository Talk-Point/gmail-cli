"""Authentication CLI commands."""

from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any

import typer

from gmail_cli.services.auth import (
    get_token_expiry,
    is_authenticated,
    logout,
    run_oauth_flow,
)
from gmail_cli.services.credentials import (
    delete_credentials,
    get_default_account,
    get_raw_credentials_json,
    has_credentials,
    list_accounts,
    set_default_account,
)
from gmail_cli.services.gmail import TokenExpiredError
from gmail_cli.utils.output import (
    is_json_mode,
    print_error,
    print_json,
    print_json_error,
    print_success,
)

auth_app = typer.Typer(
    name="auth",
    help="Manage Gmail authentication.",
    no_args_is_help=True,
)


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require authentication for a command.

    Args:
        func: The command function to wrap.

    Returns:
        Wrapped function that checks authentication first.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not is_authenticated():
            if is_json_mode():
                print_json_error(
                    "NOT_AUTHENTICATED",
                    "Nicht authentifiziert",
                    "Führe 'gmail auth login' aus um dich anzumelden.",
                )
            else:
                print_error(
                    "Nicht authentifiziert",
                    tip="Führe 'gmail auth login' aus um dich anzumelden.",
                )
            raise typer.Exit(1)
        try:
            return func(*args, **kwargs)
        except TokenExpiredError as e:
            # Delete the expired credentials
            if e.account:
                delete_credentials(account=e.account)
            if is_json_mode():
                print_json_error(
                    "TOKEN_EXPIRED",
                    f"Token abgelaufen für {e.account or 'Account'}",
                    "Führe 'gmail auth login' aus um dich erneut anzumelden.",
                )
            else:
                print_error(
                    f"Token abgelaufen für {e.account or 'Account'}",
                    tip="Führe 'gmail auth login' aus um dich erneut anzumelden.",
                )
            raise typer.Exit(1)

    return wrapper


@auth_app.command("login")
def login(
    set_default: Annotated[
        bool,
        typer.Option("--set-default", help="Set this account as the default account."),
    ] = False,
) -> None:
    """Authenticate with Gmail using OAuth 2.0.

    Supports multiple accounts. The first account authenticated becomes the default.
    Use --set-default to make a new account the default.
    """
    # Check if already authenticated with any account
    accounts = list_accounts()
    if accounts and has_credentials(account=accounts[0]):
        if not typer.confirm(
            "Du hast bereits authentifizierte Konten. Möchtest du ein weiteres Konto hinzufügen?"
        ):
            if is_json_mode():
                print_json({"status": "cancelled", "message": "Login abgebrochen"})
            else:
                print_success("Bestehende Authentifizierung beibehalten")
            return

    try:
        credentials, email = run_oauth_flow()

        # Determine if this is the first account (will be set as default automatically)
        was_first_account = len(accounts) == 0
        is_default = was_first_account or set_default

        # Set as default if requested or if first account
        if set_default and not was_first_account:
            set_default_account(email)

        if is_json_mode():
            print_json(
                {
                    "status": "authenticated",
                    "email": email,
                    "is_default": is_default,
                    "scopes": list(credentials.scopes) if credentials.scopes else [],
                }
            )
        else:
            if is_default:
                print_success(f"Erfolgreich authentifiziert als {email} (Standard-Konto)")
            else:
                print_success(f"Erfolgreich authentifiziert als {email}")

    except FileNotFoundError as e:
        if is_json_mode():
            print_json_error("CREDENTIALS_NOT_FOUND", str(e))
        else:
            print_error(
                "credentials.json nicht gefunden",
                details=str(e),
                tip="Stelle sicher, dass die OAuth-Credentials-Datei vorhanden ist.",
            )
        raise typer.Exit(2)

    except Exception as e:
        if is_json_mode():
            print_json_error("AUTH_FAILED", "Authentifizierung fehlgeschlagen", str(e))
        else:
            print_error(
                "Authentifizierung fehlgeschlagen",
                details=str(e),
            )
        raise typer.Exit(1)


@auth_app.command("logout")
def logout_command(
    account: Annotated[
        str | None,
        typer.Option("--account", "-A", help="Specific account to log out."),
    ] = None,
    all_accounts: Annotated[
        bool,
        typer.Option("--all", help="Log out all accounts."),
    ] = False,
) -> None:
    """Log out and delete stored credentials.

    Without options, logs out the default account.
    Use --account to log out a specific account.
    Use --all to log out all accounts.
    """
    logged_out = logout(account=account, all_accounts=all_accounts)

    if is_json_mode():
        print_json({"status": "logged_out", "accounts": logged_out})
    else:
        if not logged_out:
            print_success("Keine Konten abgemeldet")
        elif len(logged_out) == 1:
            print_success(f"Erfolgreich abgemeldet: {logged_out[0]}")
        else:
            print_success(f"Erfolgreich abgemeldet: {', '.join(logged_out)}")


@auth_app.command("status")
def status() -> None:
    """Show current authentication status.

    Lists all configured accounts with their status.
    The default account is marked with an asterisk (*).
    """
    accounts = list_accounts()
    default = get_default_account()

    if not accounts:
        if is_json_mode():
            print_json({"authenticated": False, "accounts": []})
        else:
            print_error(
                "Nicht authentifiziert",
                tip="Führe 'gmail auth login' aus um dich anzumelden.",
            )
        raise typer.Exit(1)

    if is_json_mode():
        accounts_info = []
        for acc in accounts:
            expiry = get_token_expiry(account=acc)
            accounts_info.append(
                {
                    "email": acc,
                    "is_default": acc == default,
                    "token_expiry": expiry,
                }
            )
        print_json(
            {
                "authenticated": True,
                "default_account": default,
                "accounts": accounts_info,
            }
        )
    else:
        print_success(f"Authentifiziert mit {len(accounts)} Konto(en):")
        for acc in accounts:
            marker = " *" if acc == default else ""
            expiry = get_token_expiry(account=acc)
            expiry_info = f" (Token bis: {expiry})" if expiry else ""
            typer.echo(f"  {acc}{marker}{expiry_info}")


@auth_app.command("set-default")
def set_default_command(
    email: Annotated[
        str,
        typer.Argument(help="Email address of the account to set as default."),
    ],
) -> None:
    """Set the default account for commands.

    The default account is used when no --account option is specified.
    """
    accounts = list_accounts()

    if email not in accounts:
        if is_json_mode():
            print_json_error(
                "ACCOUNT_NOT_FOUND",
                f"Konto '{email}' nicht gefunden",
                f"Verfügbare Konten: {', '.join(accounts)}",
            )
        else:
            print_error(
                f"Konto '{email}' nicht gefunden",
                tip=f"Verfügbare Konten: {', '.join(accounts)}",
            )
        raise typer.Exit(1)

    set_default_account(email)

    if is_json_mode():
        print_json({"status": "default_set", "account": email})
    else:
        print_success(f"Standard-Konto gesetzt: {email}")


@auth_app.command("token")
def token_command(
    account: Annotated[
        str | None,
        typer.Option("--account", "-A", help="Account to show token for."),
    ] = None,
) -> None:
    """Show credentials JSON for server deployment.

    Outputs the raw OAuth credentials as JSON, which can be used to
    transfer authentication to a headless server.

    WARNING: This contains sensitive data. Handle with care!
    """
    accounts = list_accounts()

    if not accounts:
        if is_json_mode():
            print_json_error("NOT_AUTHENTICATED", "Keine Konten konfiguriert")
        else:
            print_error(
                "Keine Konten konfiguriert",
                tip="Führe 'gmail auth login' aus um dich anzumelden.",
            )
        raise typer.Exit(1)

    # Resolve account
    target_account = account or get_default_account() or accounts[0]

    if target_account not in accounts:
        if is_json_mode():
            print_json_error(
                "ACCOUNT_NOT_FOUND",
                f"Konto '{target_account}' nicht gefunden",
                f"Verfügbare Konten: {', '.join(accounts)}",
            )
        else:
            print_error(
                f"Konto '{target_account}' nicht gefunden",
                tip=f"Verfügbare Konten: {', '.join(accounts)}",
            )
        raise typer.Exit(1)

    creds_json = get_raw_credentials_json(target_account)

    if not creds_json:
        if is_json_mode():
            print_json_error("NO_CREDENTIALS", f"Keine Credentials für {target_account}")
        else:
            print_error(f"Keine Credentials für {target_account}")
        raise typer.Exit(1)

    # Output raw JSON (always JSON, regardless of --json flag)
    typer.echo(creds_json)
