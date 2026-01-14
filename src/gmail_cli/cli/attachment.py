"""Attachment CLI commands."""

from pathlib import Path
from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.gmail import download_attachment, get_email
from gmail_cli.utils.output import (
    console,
    is_json_mode,
    print_error,
    print_info,
    print_json,
    print_json_error,
    print_success,
    print_table,
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

attachment_app = typer.Typer(
    name="attachment",
    help="Manage email attachments.",
    no_args_is_help=True,
)


@attachment_app.command("list")
@require_auth
def list_attachments(
    message_id: Annotated[
        str,
        typer.Argument(
            help="The email message ID.",
        ),
    ],
    account: AccountOption = None,
) -> None:
    """List attachments for an email.

    Examples:
        gmail attachment list 18c1234abcd5678
        gmail attachment list 18c1234abcd5678 --account work@company.com
    """
    email = get_email(message_id, account=account)

    if not email:
        if is_json_mode():
            print_json_error("NOT_FOUND", f"E-Mail mit ID '{message_id}' nicht gefunden")
        else:
            print_error(f"E-Mail mit ID '{message_id}' nicht gefunden")
        raise typer.Exit(1)

    if is_json_mode():
        print_json(
            {
                "message_id": message_id,
                "attachments": [
                    {
                        "id": att.id,
                        "filename": att.filename,
                        "mime_type": att.mime_type,
                        "size": att.size,
                        "size_human": att.size_human,
                    }
                    for att in email.attachments
                ],
            }
        )
    else:
        if not email.attachments:
            print_info("Keine Anhänge vorhanden.")
            return

        print_table(
            title=f"Anhänge für E-Mail {message_id[:16]}...",
            columns=["Dateiname", "Typ", "Größe"],
            rows=[[att.filename, att.mime_type, att.size_human] for att in email.attachments],
        )


@attachment_app.command("download")
@require_auth
def download_attachment_command(
    message_id: Annotated[
        str,
        typer.Argument(
            help="The email message ID.",
        ),
    ],
    filename: Annotated[
        str | None,
        typer.Argument(
            help="The attachment filename to download (optional with --all).",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Output path. Defaults to current directory with original filename.",
        ),
    ] = None,
    all_attachments: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Download all attachments (filename argument is ignored).",
        ),
    ] = False,
    account: AccountOption = None,
) -> None:
    """Download an attachment from an email.

    Examples:
        gmail attachment download 18c1234abcd5678 document.pdf
        gmail attachment download 18c1234abcd5678 document.pdf --output ~/Downloads/doc.pdf
        gmail attachment download 18c1234abcd5678 --all
        gmail attachment download 18c1234abcd5678 --all --output ~/Downloads/
        gmail attachment download 18c1234abcd5678 doc.pdf --account work@company.com
    """
    # Validate: either filename or --all must be provided
    if not all_attachments and not filename:
        if is_json_mode():
            print_json_error("MISSING_ARGUMENT", "Bitte Dateiname angeben oder --all verwenden")
        else:
            print_error("Bitte Dateiname angeben oder --all verwenden")
        raise typer.Exit(1)

    email = get_email(message_id, account=account)

    if not email:
        if is_json_mode():
            print_json_error("NOT_FOUND", f"E-Mail mit ID '{message_id}' nicht gefunden")
        else:
            print_error(f"E-Mail mit ID '{message_id}' nicht gefunden")
        raise typer.Exit(1)

    if not email.attachments:
        if is_json_mode():
            print_json_error("NO_ATTACHMENTS", "E-Mail hat keine Anhänge")
        else:
            print_info("E-Mail hat keine Anhänge.")
        raise typer.Exit(1)

    if all_attachments:
        # Download all attachments
        downloaded = []
        for att in email.attachments:
            output_path = output if output else att.filename
            if Path(output_path).is_dir():
                output_path = str(Path(output_path) / att.filename)

            success = download_attachment(message_id, att.id, output_path, account=account)
            if success:
                downloaded.append({"filename": att.filename, "path": output_path})
                if not is_json_mode():
                    print_success(f"Heruntergeladen: {att.filename} → {output_path}")
            elif not is_json_mode():
                print_error(f"Fehler beim Herunterladen: {att.filename}")

        if is_json_mode():
            print_json({"downloaded": downloaded})
    else:
        # Download specific attachment
        attachment = None
        for att in email.attachments:
            if att.filename == filename:
                attachment = att
                break

        if not attachment:
            if is_json_mode():
                print_json_error(
                    "ATTACHMENT_NOT_FOUND",
                    f"Anhang '{filename}' nicht gefunden",
                )
            else:
                print_error(f"Anhang '{filename}' nicht gefunden")
                console.print("\n[dim]Verfügbare Anhänge:[/dim]")
                for att in email.attachments:
                    console.print(f"  - {att.filename}")
            raise typer.Exit(1)

        output_path = output if output else attachment.filename
        if Path(output_path).is_dir():
            output_path = str(Path(output_path) / attachment.filename)
        success = download_attachment(message_id, attachment.id, output_path, account=account)

        if success:
            if is_json_mode():
                print_json(
                    {
                        "downloaded": True,
                        "filename": attachment.filename,
                        "path": output_path,
                    }
                )
            else:
                print_success(f"Heruntergeladen: {output_path}")
        else:
            if is_json_mode():
                print_json_error("DOWNLOAD_FAILED", "Download fehlgeschlagen")
            else:
                print_error("Download fehlgeschlagen")
            raise typer.Exit(1)
