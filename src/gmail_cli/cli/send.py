"""Send and reply CLI commands."""

from pathlib import Path
from typing import Annotated

import typer

from gmail_cli.cli.auth import require_auth
from gmail_cli.services.gmail import (
    SendError,
    compose_email,
    compose_reply,
    create_draft,
    get_email,
    get_signature,
    list_send_as_addresses,
    send_email,
)
from gmail_cli.utils.html import html_to_text
from gmail_cli.utils.markdown import markdown_to_html, wrap_html_for_email
from gmail_cli.utils.output import (
    is_json_mode,
    print_error,
    print_info,
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
            "--signature/--no-signature",
            "--sig/--no-sig",
            help="Include Gmail signature (default: enabled).",
        ),
    ] = True,
    plain: Annotated[
        bool,
        typer.Option(
            "--plain",
            help="Disable Markdown processing and send as plain text only.",
        ),
    ] = False,
    draft: Annotated[
        bool,
        typer.Option(
            "--draft",
            help="Save as draft instead of sending.",
        ),
    ] = False,
    from_addr: Annotated[
        str | None,
        typer.Option(
            "--from",
            help="Send-As address to send from (must be configured in Gmail settings).",
        ),
    ] = None,
    account: AccountOption = None,
) -> None:
    """Send a new email.

    By default, the body is processed as Markdown and converted to HTML,
    and your Gmail signature is automatically appended.

    Use --no-signature to exclude the signature.
    Use --plain to send as plain text without Markdown conversion.
    Use --from to send from an alternative Send-As address.

    Examples:
        gmail send --to recipient@example.com --subject "Hello" --body "Hi there!"
        gmail send --to a@x.com --to b@x.com --subject "Test" --body-file message.txt
        gmail send --to x@x.com --subject "Report" --body "See attached" --attach report.pdf
        gmail send --to x@x.com --subject "Work" --body "From work" --account work@company.com
        gmail send --to x@x.com --subject "Test" --body "**Bold**" --plain
        gmail send --to x@x.com --subject "Quick note" --body "Hi" --no-signature
        gmail send --to x@x.com --subject "Hi" --body "From alias" --from alias@example.com
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

    # Validate Send-As address if provided
    if from_addr:
        send_as_addresses = list_send_as_addresses(account=account)
        valid_emails = [sa["email"].lower() for sa in send_as_addresses]
        if from_addr.lower() not in valid_emails:
            if is_json_mode():
                print_json_error(
                    "INVALID_SEND_AS",
                    f"'{from_addr}' ist keine gültige Send-As Adresse. "
                    f"Verfügbar: {', '.join(valid_emails) if valid_emails else 'keine'}",
                )
            else:
                print_error(
                    f"'{from_addr}' ist keine gültige Send-As Adresse",
                    details=f"Verfügbar: {', '.join(valid_emails) if valid_emails else 'keine'}",
                )
            raise typer.Exit(1)

    # Prepare HTML body: Markdown conversion (default) or plain text
    html_body = None
    if not plain:
        # Convert Markdown to HTML (default behavior)
        html_body = markdown_to_html(body_content)
        html_body = wrap_html_for_email(html_body)

    # Handle signature
    if signature:
        sig = get_signature(account=account)
        if sig:
            # Plain text version: convert HTML signature to text and append
            sig_text = html_to_text(sig)
            body_content = f"{body_content}\n\n--\n{sig_text}"
            # HTML version: append signature to HTML body
            if html_body:
                html_body = f"{html_body}<br><div>--</div>{sig}"
            else:
                # Plain mode with signature: create minimal HTML for signature
                body_html = body_content.replace("\n", "<br>")
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
        from_addr=from_addr,
    )

    # Send or save as draft
    try:
        if draft:
            result = create_draft(message, account=account)
            if is_json_mode():
                print_json(
                    {
                        "status": "draft_created",
                        "draft_id": result.get("id"),
                        "message_id": result.get("message", {}).get("id"),
                        "thread_id": result.get("message", {}).get("threadId"),
                    }
                )
            else:
                draft_id = result.get("id")
                print_success("Entwurf erstellt!")
                print_info(f"Draft-ID: {draft_id}")
        else:
            result = send_email(message, account=account)
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
            error_type = "DRAFT_FAILED" if draft else "SEND_FAILED"
            print_json_error(error_type, e.message)
        else:
            action = (
                "Entwurf konnte nicht erstellt werden"
                if draft
                else "E-Mail konnte nicht gesendet werden"
            )
            print_error(action, details=e.message)
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
    cc: Annotated[
        list[str] | None,
        typer.Option(
            "--cc",
            help="CC recipient. Can be specified multiple times.",
        ),
    ] = None,
    signature: Annotated[
        bool,
        typer.Option(
            "--signature/--no-signature",
            "--sig/--no-sig",
            help="Include Gmail signature (default: enabled).",
        ),
    ] = True,
    plain: Annotated[
        bool,
        typer.Option(
            "--plain",
            help="Disable Markdown processing and send reply as plain text only.",
        ),
    ] = False,
    draft: Annotated[
        bool,
        typer.Option(
            "--draft",
            help="Save as draft instead of sending.",
        ),
    ] = False,
    from_addr: Annotated[
        str | None,
        typer.Option(
            "--from",
            help="Send-As address to send from (must be configured in Gmail settings).",
        ),
    ] = None,
    account: AccountOption = None,
) -> None:
    """Reply to an email.

    By default, the body is processed as Markdown and converted to HTML,
    and your Gmail signature is automatically appended.

    Use --no-signature to exclude the signature.
    Use --plain to send as plain text without Markdown conversion.
    Use --draft to save the reply as a draft instead of sending it.
    Use --from to reply from an alternative Send-As address.

    Examples:
        gmail reply 18c1234abcd5678 --body "Thanks for your message!"
        gmail reply 18c1234abcd5678 --body-file reply.txt
        gmail reply 18c1234abcd5678 --all --body "Thanks everyone!"
        gmail reply 18c1234abcd5678 --body "Info" --cc support@example.com
        gmail reply 18c1234abcd5678 --body "Reply" --account work@company.com
        gmail reply 18c1234abcd5678 --body "**Bold reply**" --plain
        gmail reply 18c1234abcd5678 --body "Quick reply" --no-signature
        gmail reply 18c1234abcd5678 --body "Review this later" --draft
        gmail reply 18c1234abcd5678 --body "From alias" --from alias@example.com
    """
    # Get original email
    email = get_email(message_id, account=account)

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

    # Validate Send-As address if provided
    if from_addr:
        send_as_addresses = list_send_as_addresses(account=account)
        valid_emails = [sa["email"].lower() for sa in send_as_addresses]
        if from_addr.lower() not in valid_emails:
            if is_json_mode():
                print_json_error(
                    "INVALID_SEND_AS",
                    f"'{from_addr}' ist keine gültige Send-As Adresse. "
                    f"Verfügbar: {', '.join(valid_emails) if valid_emails else 'keine'}",
                )
            else:
                print_error(
                    f"'{from_addr}' ist keine gültige Send-As Adresse",
                    details=f"Verfügbar: {', '.join(valid_emails) if valid_emails else 'keine'}",
                )
            raise typer.Exit(1)

    # Prepare HTML body: Markdown conversion (default) or plain text
    html_body = None
    if not plain:
        # Convert Markdown to HTML (default behavior)
        html_body = markdown_to_html(body_content)
        html_body = wrap_html_for_email(html_body)

    # Handle signature
    if signature:
        sig = get_signature(account=account)
        if sig:
            # Plain text version: convert HTML signature to text and append
            sig_text = html_to_text(sig)
            body_content = f"{body_content}\n\n--\n{sig_text}"
            # HTML version: append signature to HTML body
            if html_body:
                html_body = f"{html_body}<br><div>--</div>{sig}"
            else:
                # Plain mode with signature: create minimal HTML for signature
                body_html = body_content.replace("\n", "<br>")
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

    # Build CC list: combine user-specified CC with original CC (if reply_all)
    reply_cc = list(cc) if cc else []
    if reply_all and email.cc:
        for addr in email.cc:
            if addr not in reply_cc:
                reply_cc.append(addr)

    # Compose reply
    message = compose_reply(
        to=recipients,
        subject=subject,
        body=body_content,
        thread_id=email.thread_id,
        message_id=email.message_id or f"<{email.id}@gmail.com>",
        references=email.references,
        cc=reply_cc if reply_cc else None,
        attachments=attach,
        html_body=html_body,
        from_addr=from_addr,
    )

    # Send or save as draft
    try:
        if draft:
            result = create_draft(message, account=account)
            if is_json_mode():
                print_json(
                    {
                        "status": "draft_created",
                        "draft_id": result.get("id"),
                        "message_id": result.get("message", {}).get("id"),
                        "thread_id": result.get("message", {}).get("threadId"),
                        "replied_to": message_id,
                    }
                )
            else:
                draft_id = result.get("id")
                thread_id = result.get("message", {}).get("threadId")
                print_success("Antwort-Entwurf erstellt!")
                print_info(f"Draft-ID:  {draft_id}")
                print_info(f"Thread-ID: {thread_id}")
        else:
            result = send_email(message, account=account)
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
            error_type = "DRAFT_FAILED" if draft else "SEND_FAILED"
            print_json_error(error_type, e.message)
        else:
            action = (
                "Antwort-Entwurf konnte nicht erstellt werden"
                if draft
                else "Antwort konnte nicht gesendet werden"
            )
            print_error(action, details=e.message)
        raise typer.Exit(1)


@require_auth
def sendas_command(
    account: AccountOption = None,
) -> None:
    """List available Send-As addresses.

    Shows all verified email addresses that can be used as sender address.
    These must be configured in Gmail settings under "Send mail as".

    Examples:
        gmail sendas
        gmail sendas --json
        gmail sendas --account work@company.com
    """
    addresses = list_send_as_addresses(account=account)

    if is_json_mode():
        print_json({"sendas": addresses, "count": len(addresses)})
    else:
        if not addresses:
            print_info("Keine Send-As Adressen konfiguriert.")
            return

        print_info(f"Send-As Adressen ({len(addresses)}):")
        for addr in addresses:
            email = addr["email"]
            name = addr.get("displayName", "")
            primary = " (primär)" if addr.get("isPrimary") else ""
            default = " [Standard]" if addr.get("isDefault") else ""
            display = f"{name} <{email}>" if name else email
            print(f"  {display}{primary}{default}")
