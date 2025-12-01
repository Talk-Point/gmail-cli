"""Authentication CLI commands."""

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from gmail_cli.services.auth import (
    get_token_expiry,
    get_user_email,
    is_authenticated,
    logout,
    run_oauth_flow,
)
from gmail_cli.services.credentials import has_credentials
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
        return func(*args, **kwargs)

    return wrapper


@auth_app.command("login")
def login() -> None:
    """Authenticate with Gmail using OAuth 2.0."""
    # Check if already authenticated
    if has_credentials():
        if not typer.confirm("Du bist bereits authentifiziert. Möchtest du dich neu anmelden?"):
            if is_json_mode():
                print_json({"status": "cancelled", "message": "Login abgebrochen"})
            else:
                print_success("Bestehende Authentifizierung beibehalten")
            return

    try:
        credentials = run_oauth_flow()
        email = get_user_email()

        if is_json_mode():
            print_json(
                {
                    "status": "authenticated",
                    "email": email,
                    "scopes": list(credentials.scopes) if credentials.scopes else [],
                }
            )
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
def logout_command() -> None:
    """Log out and delete stored credentials."""
    logout()

    if is_json_mode():
        print_json({"status": "logged_out"})
    else:
        print_success("Erfolgreich abgemeldet")


@auth_app.command("status")
def status() -> None:
    """Show current authentication status."""
    if is_authenticated():
        email = get_user_email()
        expiry = get_token_expiry()

        if is_json_mode():
            print_json(
                {
                    "authenticated": True,
                    "email": email,
                    "token_expiry": expiry,
                }
            )
        else:
            print_success(f"Authentifiziert als {email}")
            if expiry:
                typer.echo(f"  Token gültig bis: {expiry}")
    else:
        if is_json_mode():
            print_json({"authenticated": False})
        else:
            print_error(
                "Nicht authentifiziert",
                tip="Führe 'gmail auth login' aus um dich anzumelden.",
            )
        raise typer.Exit(1)
