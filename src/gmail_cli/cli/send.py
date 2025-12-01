"""Send and reply CLI commands."""

from pathlib import Path
from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.gmail import (
    SendError,
    compose_email,
    compose_reply,
    get_email,
    get_signature,
    send_email,
)
from gmail_cli.utils.html import html_to_text
from gmail_cli.utils.output import (
    is_json_mode,
    print_error,
    print_info,
    print_json,
    print_json_error,
    print_success,
)


@require_auth
def send_command(
    to: Annotated[
        list[str],
        typer.Option(
            "--to",
            "-t",
            help="Recipient email address. Can be specified multiple times.",
        ),
    ],
    subject: Annotated[
        str,
        typer.Option(
            "--subject",
            "-s",
            help="Email subject.",
        ),
    ],
    body: Annotated[
        str | None,
        typer.Option(
            "--body",
            "-b",
            help="Email body text.",
        ),
    ] = None,
    body_file: Annotated[
        str | None,
        typer.Option(
            "--body-file",
            "-f",
            help="Path to file containing email body.",
        ),
    ] = None,
    cc: Annotated[
        list[str] | None,
        typer.Option(
            "--cc",
            help="CC recipient. Can be specified multiple times.",
        ),
    ] = None,
    bcc: Annotated[
        list[str] | None,
        typer.Option(
            "--bcc",
            help="BCC recipient. Can be specified multiple times.",
        ),
    ] = None,
    attach: Annotated[
        list[str] | None,
        typer.Option(
            "--attach",
            "-a",
            help="File to attach. Can be specified multiple times.",
        ),
    ] = None,
    signature: Annotated[
        bool,
        typer.Option(
            "--signature",
            "--sig",
            help="Append your Gmail signature to the message.",
        ),
    ] = False,
) -> None:
    """Send a new email.

    Examples:
        gmail send --to recipient@example.com --subject "Hello" --body "Hi there!"
        gmail send --to a@x.com --to b@x.com --subject "Test" --body-file message.txt
        gmail send --to x@x.com --subject "Report" --body "See attached" --attach report.pdf
    """
    # Get body content
    if body_file:
        path = Path(body_file)
        if not path.exists():
            if is_json_mode():
                print_json_error("FILE_NOT_FOUND", f"Datei nicht gefunden: {body_file}")
            else:
                print_error(f"Datei nicht gefunden: {body_file}")
            raise typer.Exit(1)
        body_content = path.read_text()
    elif body:
        body_content = body
    else:
        if is_json_mode():
            print_json_error("NO_BODY", "E-Mail-Text erforderlich (--body oder --body-file)")
        else:
            print_error("E-Mail-Text erforderlich (--body oder --body-file)")
        raise typer.Exit(1)

    # Prepare HTML body if signature requested
    html_body = None
    if signature:
        sig = get_signature()
        if sig:
            # Plain text version: convert HTML signature to text
            sig_text = html_to_text(sig)
            body_content = f"{body_content}\n\n--\n{sig_text}"
            # HTML version: wrap body in HTML and append signature
            body_html = body.replace("\n", "<br>") if body else ""
            if body_file:
                body_html = Path(body_file).read_text().replace("\n", "<br>")
            html_body = f"<div>{body_html}</div><br><div>--</div>{sig}"

    # Compose message
    message = compose_email(
        to=to,
        subject=subject,
        body=body_content,
        cc=cc,
        bcc=bcc,
        attachments=attach,
        html_body=html_body,
    )

    # Send
    try:
        result = send_email(message)
        if is_json_mode():
            print_json(
                {
                    "sent": True,
                    "message_id": result.get("id"),
                    "thread_id": result.get("threadId"),
                }
            )
        else:
            msg_id = result.get("id")
            thread_id = result.get("threadId")
            print_success("E-Mail gesendet!")
            print_info(f"Message-ID: {msg_id}")
            print_info(f"Thread-ID:  {thread_id}")
    except SendError as e:
        if is_json_mode():
            print_json_error("SEND_FAILED", e.message)
        else:
            print_error("E-Mail konnte nicht gesendet werden", details=e.message)
        raise typer.Exit(1)


@require_auth
def reply_command(
    message_id: Annotated[
        str,
        typer.Argument(
            help="The message ID to reply to.",
        ),
    ],
    body: Annotated[
        str | None,
        typer.Option(
            "--body",
            "-b",
            help="Reply body text.",
        ),
    ] = None,
    body_file: Annotated[
        str | None,
        typer.Option(
            "--body-file",
            "-f",
            help="Path to file containing reply body.",
        ),
    ] = None,
    reply_all: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Reply to all recipients.",
        ),
    ] = False,
    attach: Annotated[
        list[str] | None,
        typer.Option(
            "--attach",
            help="File to attach. Can be specified multiple times.",
        ),
    ] = None,
    signature: Annotated[
        bool,
        typer.Option(
            "--signature",
            "--sig",
            help="Append your Gmail signature to the reply.",
        ),
    ] = False,
) -> None:
    """Reply to an email.

    Examples:
        gmail reply 18c1234abcd5678 --body "Thanks for your message!"
        gmail reply 18c1234abcd5678 --body-file reply.txt
        gmail reply 18c1234abcd5678 --all --body "Thanks everyone!"
        gmail reply 18c1234abcd5678 --body "Danke!" --signature
    """
    # Get original email
    email = get_email(message_id)

    if not email:
        if is_json_mode():
            print_json_error("NOT_FOUND", f"E-Mail mit ID '{message_id}' nicht gefunden")
        else:
            print_error(f"E-Mail mit ID '{message_id}' nicht gefunden")
        raise typer.Exit(1)

    # Get body content
    if body_file:
        path = Path(body_file)
        if not path.exists():
            if is_json_mode():
                print_json_error("FILE_NOT_FOUND", f"Datei nicht gefunden: {body_file}")
            else:
                print_error(f"Datei nicht gefunden: {body_file}")
            raise typer.Exit(1)
        body_content = path.read_text()
    elif body:
        body_content = body
    else:
        if is_json_mode():
            print_json_error("NO_BODY", "Antwort-Text erforderlich (--body oder --body-file)")
        else:
            print_error("Antwort-Text erforderlich (--body oder --body-file)")
        raise typer.Exit(1)

    # Prepare HTML body if signature requested
    html_body = None
    if signature:
        sig = get_signature()
        if sig:
            # Plain text version: convert HTML signature to text
            sig_text = html_to_text(sig)
            body_content = f"{body_content}\n\n--\n{sig_text}"
            # HTML version: wrap body in HTML and append signature
            body_html = body.replace("\n", "<br>") if body else ""
            if body_file:
                body_html = Path(body_file).read_text().replace("\n", "<br>")
            html_body = f"<div>{body_html}</div><br><div>--</div>{sig}"

    # Determine recipients
    # Extract email from "Name <email>" format
    sender_email = email.sender
    if "<" in sender_email:
        sender_email = sender_email.split("<")[1].rstrip(">")

    recipients = [sender_email]

    if reply_all:
        # Add CC recipients
        if email.cc:
            recipients.extend(email.cc)
        # Add other To recipients (excluding ourselves)
        for r in email.recipients:
            if r not in recipients:
                recipients.append(r)

    # Build reply subject
    subject = email.subject
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    # Compose reply
    message = compose_reply(
        to=recipients,
        subject=subject,
        body=body_content,
        thread_id=email.thread_id,
        message_id=email.message_id or f"<{email.id}@gmail.com>",
        references=email.references,
        cc=email.cc if reply_all else None,
        attachments=attach,
        html_body=html_body,
    )

    # Send
    try:
        result = send_email(message)
        if is_json_mode():
            print_json(
                {
                    "sent": True,
                    "message_id": result.get("id"),
                    "thread_id": result.get("threadId"),
                    "replied_to": message_id,
                }
            )
        else:
            msg_id = result.get("id")
            thread_id = result.get("threadId")
            print_success("Antwort gesendet!")
            print_info(f"Message-ID: {msg_id}")
            print_info(f"Thread-ID:  {thread_id}")
    except SendError as e:
        if is_json_mode():
            print_json_error("SEND_FAILED", e.message)
        else:
            print_error("Antwort konnte nicht gesendet werden", details=e.message)
        raise typer.Exit(1)
