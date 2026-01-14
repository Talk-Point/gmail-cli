"""Main CLI application."""

from typing import Annotated

import typer

from gmail_cli import __version__
from gmail_cli.cli.accounts import accounts_app
from gmail_cli.cli.attachment import attachment_app, download_attachment_command, list_attachments
from gmail_cli.cli.auth import auth_app
from gmail_cli.cli.draft import draft_app
from gmail_cli.cli.mark import mark_command
from gmail_cli.cli.read import read_command
from gmail_cli.cli.search import search_command
from gmail_cli.cli.send import reply_command, send_command, sendas_command
from gmail_cli.utils.output import set_json_mode

app = typer.Typer(
    name="gmail",
    help="A command-line interface for Gmail, similar to gh CLI.",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"gmail-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[  # noqa: ARG001
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """Gmail CLI - Access Gmail from the command line."""
    set_json_mode(json_output)


# Register subcommands
app.add_typer(accounts_app, name="accounts")
app.add_typer(auth_app, name="auth")
app.add_typer(attachment_app, name="attachment")
app.add_typer(draft_app, name="draft")
app.command("search")(search_command)
app.command("read")(read_command)
app.command("send")(send_command)
app.command("reply")(reply_command)
app.command("sendas")(sendas_command)
app.command("mark")(mark_command)

# Top-level shortcuts for common attachment operations
app.command("download", help="Download attachment (shortcut for 'attachment download').")(
    download_attachment_command
)
app.command("attachments", help="List attachments (shortcut for 'attachment list').")(
    list_attachments
)


if __name__ == "__main__":
    app()
