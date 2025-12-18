"""Gmail API wrapper service."""

import base64
import mimetypes
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from pathlib import Path

from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gmail_cli.models.attachment import Attachment
from gmail_cli.models.email import Email
from gmail_cli.models.search import SearchResult
from gmail_cli.services.auth import get_credentials

# Rate limiting settings
MAX_RETRIES = 3
BASE_DELAY = 1  # seconds


def get_gmail_service(account: str | None = None):
    """Get an authenticated Gmail API service.

    Args:
        account: Account email to use. If None, uses resolved account.

    Returns:
        Gmail API service object.

    Raises:
        Exception: If not authenticated.
    """
    credentials = get_credentials(account=account)
    if not credentials:
        raise Exception("Not authenticated. Run 'gmail auth login' first.")

    return build("gmail", "v1", credentials=credentials)


class TokenExpiredError(Exception):
    """Raised when the OAuth token has expired or been revoked."""

    def __init__(self, account: str | None = None) -> None:
        self.account = account
        msg = "Token expired or revoked."
        if account:
            msg = f"Token for '{account}' expired or revoked."
        super().__init__(msg)


def _execute_with_retry(request, account: str | None = None):
    """Execute an API request with exponential backoff retry.

    Args:
        request: The API request to execute.
        account: Account email for error messages.

    Returns:
        The API response.

    Raises:
        HttpError: If all retries fail.
        TokenExpiredError: If the token has expired or been revoked.
    """
    for attempt in range(MAX_RETRIES):
        try:
            return request.execute()
        except RefreshError:
            raise TokenExpiredError(account)
        except HttpError as e:
            if e.resp.status == 429:  # Rate limited
                delay = BASE_DELAY * (2**attempt)
                time.sleep(delay)
            else:
                raise
    # Final attempt
    try:
        return request.execute()
    except RefreshError:
        raise TokenExpiredError(account)


def build_search_query(
    query: str = "",
    from_addr: str | None = None,
    to_addr: str | None = None,
    subject: str | None = None,
    label: str | None = None,
    after: str | None = None,
    before: str | None = None,
    has_attachment: bool = False,
) -> str:
    """Build a Gmail search query string.

    Args:
        query: Base search query.
        from_addr: Filter by sender.
        to_addr: Filter by recipient.
        subject: Filter by subject.
        label: Filter by label.
        after: Filter emails after date (YYYY-MM-DD).
        before: Filter emails before date (YYYY-MM-DD).
        has_attachment: Filter emails with attachments.

    Returns:
        Combined Gmail search query string.
    """
    parts = []

    if query:
        parts.append(query)
    if from_addr:
        parts.append(f"from:{from_addr}")
    if to_addr:
        parts.append(f"to:{to_addr}")
    if subject:
        parts.append(f"subject:{subject}")
    if label:
        parts.append(f"label:{label}")
    if after:
        parts.append(f"after:{after}")
    if before:
        parts.append(f"before:{before}")
    if has_attachment:
        parts.append("has:attachment")

    return " ".join(parts)


def search_emails(
    query: str = "",
    from_addr: str | None = None,
    to_addr: str | None = None,
    subject: str | None = None,
    label: str | None = None,
    after: str | None = None,
    before: str | None = None,
    has_attachment: bool = False,
    limit: int = 20,
    page_token: str | None = None,
    account: str | None = None,
) -> SearchResult:
    """Search emails with filters and pagination.

    Args:
        query: Search query string.
        from_addr: Filter by sender.
        to_addr: Filter by recipient.
        subject: Filter by subject.
        label: Filter by label.
        after: Filter emails after date.
        before: Filter emails before date.
        has_attachment: Filter emails with attachments.
        limit: Maximum number of results.
        page_token: Token for pagination.
        account: Account email to use. If None, uses resolved account.

    Returns:
        SearchResult with matching emails.
    """
    service = get_gmail_service(account=account)

    full_query = build_search_query(
        query=query,
        from_addr=from_addr,
        to_addr=to_addr,
        subject=subject,
        label=label,
        after=after,
        before=before,
        has_attachment=has_attachment,
    )

    # Get message list
    request = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=full_query,
            maxResults=limit,
            pageToken=page_token,
        )
    )
    response = _execute_with_retry(request, account=account)

    messages = response.get("messages", [])
    next_page_token = response.get("nextPageToken")
    total_estimate = response.get("resultSizeEstimate", 0)

    # Fetch message details for each result
    emails = []
    for msg in messages:
        email = get_email_summary(msg["id"], account=account)
        if email:
            emails.append(email)

    return SearchResult(
        emails=emails,
        total_estimate=total_estimate,
        next_page_token=next_page_token,
        query=full_query,
    )


def get_email_summary(message_id: str, account: str | None = None) -> Email | None:
    """Get email summary (metadata only, not full body).

    Args:
        message_id: Gmail message ID.
        account: Account email to use. If None, uses resolved account.

    Returns:
        Email with metadata, or None if not found.
    """
    service = get_gmail_service(account=account)

    try:
        request = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            )
        )
        msg = _execute_with_retry(request, account=account)
    except HttpError as e:
        if e.resp.status == 404:
            return None
        raise

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Parse date
    date_str = headers.get("Date", "")
    try:
        date = parsedate_to_datetime(date_str)
    except Exception:
        # Fallback to internalDate
        internal_date = int(msg.get("internalDate", 0))
        date = datetime.fromtimestamp(internal_date / 1000, tz=timezone.utc)

    return Email(
        id=msg["id"],
        thread_id=msg["threadId"],
        subject=headers.get("Subject", "(no subject)"),
        sender=headers.get("From", ""),
        recipients=[headers.get("To", "")],
        date=date,
        snippet=msg.get("snippet", ""),
        labels=msg.get("labelIds", []),
        is_read="UNREAD" not in msg.get("labelIds", []),
    )


def get_email(message_id: str, account: str | None = None) -> Email | None:
    """Get full email with body and attachments.

    Args:
        message_id: Gmail message ID.
        account: Account email to use. If None, uses resolved account.

    Returns:
        Full Email object, or None if not found.
    """
    service = get_gmail_service(account=account)

    try:
        request = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
        )
        msg = _execute_with_retry(request, account=account)
    except HttpError as e:
        if e.resp.status == 404:
            return None
        raise

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Parse date
    date_str = headers.get("Date", "")
    try:
        date = parsedate_to_datetime(date_str)
    except Exception:
        internal_date = int(msg.get("internalDate", 0))
        date = datetime.fromtimestamp(internal_date / 1000, tz=timezone.utc)

    # Parse recipients
    to_header = headers.get("To", "")
    cc_header = headers.get("Cc", "")
    recipients = [r.strip() for r in to_header.split(",") if r.strip()]
    cc = [r.strip() for r in cc_header.split(",") if r.strip()]

    # Extract body and attachments
    body_text, body_html, attachments = _parse_message_parts(msg.get("payload", {}), message_id)

    return Email(
        id=msg["id"],
        thread_id=msg["threadId"],
        subject=headers.get("Subject", "(no subject)"),
        sender=headers.get("From", ""),
        recipients=recipients,
        cc=cc,
        date=date,
        body_text=body_text,
        body_html=body_html,
        snippet=msg.get("snippet", ""),
        labels=msg.get("labelIds", []),
        attachments=attachments,
        is_read="UNREAD" not in msg.get("labelIds", []),
        message_id=headers.get("Message-ID", ""),
        references=[r.strip() for r in headers.get("References", "").split() if r.strip()],
    )


def _parse_message_parts(payload: dict, message_id: str) -> tuple[str, str, list[Attachment]]:
    """Parse message payload to extract body and attachments.

    Args:
        payload: Message payload from API.
        message_id: Message ID for attachment references.

    Returns:
        Tuple of (body_text, body_html, attachments).
    """
    body_text = ""
    body_html = ""
    attachments = []

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    elif mime_type == "text/html":
        data = payload.get("body", {}).get("data", "")
        if data:
            body_html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    elif "multipart" in mime_type:
        for part in payload.get("parts", []):
            part_mime = part.get("mimeType", "")
            filename = part.get("filename", "")

            if filename:
                # This is an attachment
                attachment_id = part.get("body", {}).get("attachmentId", "")
                size = part.get("body", {}).get("size", 0)
                attachments.append(
                    Attachment(
                        id=attachment_id,
                        message_id=message_id,
                        filename=filename,
                        mime_type=part_mime,
                        size=size,
                    )
                )
            elif part_mime == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            elif part_mime == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    body_html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            elif "multipart" in part_mime:
                # Recursive parsing for nested multipart
                sub_text, sub_html, sub_attachments = _parse_message_parts(part, message_id)
                if not body_text:
                    body_text = sub_text
                if not body_html:
                    body_html = sub_html
                attachments.extend(sub_attachments)

    return body_text, body_html, attachments


def get_attachment(message_id: str, attachment_id: str, account: str | None = None) -> bytes | None:
    """Get attachment data.

    Args:
        message_id: Gmail message ID.
        attachment_id: Attachment ID.
        account: Account email to use. If None, uses resolved account.

    Returns:
        Attachment data as bytes, or None if not found.
    """
    service = get_gmail_service(account=account)

    try:
        request = (
            service.users()
            .messages()
            .attachments()
            .get(
                userId="me",
                messageId=message_id,
                id=attachment_id,
            )
        )
        response = _execute_with_retry(request, account=account)
        data = response.get("data", "")
        return base64.urlsafe_b64decode(data)
    except HttpError:
        return None


def download_attachment(
    message_id: str, attachment_id: str, output_path: str, account: str | None = None
) -> bool:
    """Download attachment to file.

    Args:
        message_id: Gmail message ID.
        attachment_id: Attachment ID.
        output_path: Path to save the file.
        account: Account email to use. If None, uses resolved account.

    Returns:
        True if download successful, False otherwise.
    """
    data = get_attachment(message_id, attachment_id, account=account)

    if data is None:
        return False

    with open(output_path, "wb") as f:
        f.write(data)

    return True


def get_signature(account: str | None = None) -> str | None:
    """Get the user's Gmail signature.

    Args:
        account: Account email to use. If None, uses resolved account.

    Returns:
        The signature HTML/text, or None if not set.
    """
    service = get_gmail_service(account=account)

    try:
        # Get send-as settings (includes signature)
        request = service.users().settings().sendAs().list(userId="me")
        response = _execute_with_retry(request, account=account)

        send_as_list = response.get("sendAs", [])
        for send_as in send_as_list:
            if send_as.get("isPrimary", False):
                signature = send_as.get("signature", "")
                return signature if signature else None

        return None
    except HttpError:
        return None


def compose_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
    html_body: str | None = None,
) -> dict:
    """Compose an email message.

    Args:
        to: List of recipient email addresses.
        subject: Email subject.
        body: Email body text (plain text).
        cc: List of CC recipients.
        bcc: List of BCC recipients.
        attachments: List of file paths to attach.
        html_body: Optional HTML version of the body.

    Returns:
        Message dict ready for Gmail API.
    """
    msg = EmailMessage()
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject

    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)

    # Set plain text content
    msg.set_content(body)

    # Add HTML alternative if provided
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    # Add attachments
    if attachments:
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                continue

            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type is None:
                mime_type = "application/octet-stream"

            maintype, subtype = mime_type.split("/", 1)

            with open(path, "rb") as f:
                data = f.read()
                msg.add_attachment(
                    data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=path.name,
                )

    # Encode for Gmail API
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def compose_reply(
    to: list[str],
    subject: str,
    body: str,
    thread_id: str,
    message_id: str,
    references: list[str] | None = None,
    cc: list[str] | None = None,
    attachments: list[str] | None = None,
    html_body: str | None = None,
) -> dict:
    """Compose a reply email.

    Args:
        to: List of recipient email addresses.
        subject: Email subject.
        body: Reply body text (plain text).
        thread_id: Thread ID to reply in.
        message_id: Message-ID of email being replied to.
        references: List of previous Message-IDs in thread.
        cc: List of CC recipients.
        attachments: List of file paths to attach.
        html_body: Optional HTML version of the body.

    Returns:
        Message dict ready for Gmail API with thread info.
    """
    msg = EmailMessage()
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject

    if cc:
        msg["Cc"] = ", ".join(cc)

    # Threading headers
    msg["In-Reply-To"] = message_id
    all_refs = (references or []) + [message_id]
    msg["References"] = " ".join(all_refs)

    # Set plain text content
    msg.set_content(body)

    # Add HTML alternative if provided
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    # Add attachments
    if attachments:
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                continue

            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type is None:
                mime_type = "application/octet-stream"

            maintype, subtype = mime_type.split("/", 1)

            with open(path, "rb") as f:
                data = f.read()
                msg.add_attachment(
                    data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=path.name,
                )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw, "threadId": thread_id}


class SendError(Exception):
    """Error when sending email fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DraftNotFoundError(Exception):
    """Error when draft is not found."""

    def __init__(self, draft_id: str):
        self.draft_id = draft_id
        self.message = f"Draft '{draft_id}' not found"
        super().__init__(self.message)


def send_email(message: dict, account: str | None = None) -> dict:
    """Send an email message.

    Args:
        message: Message dict from compose_email or compose_reply.
        account: Account email to use. If None, uses resolved account.

    Returns:
        API response with message ID.

    Raises:
        SendError: If sending fails.
    """
    service = get_gmail_service(account=account)

    try:
        request = service.users().messages().send(userId="me", body=message)
        return _execute_with_retry(request, account=account)
    except HttpError as e:
        error_msg = str(e)
        if e.resp.status == 400:
            error_msg = "Ungültige E-Mail-Adresse oder Nachrichtenformat"
        elif e.resp.status == 403:
            error_msg = "Keine Berechtigung zum Senden"
        elif e.resp.status == 429:
            error_msg = "Zu viele Anfragen - bitte warte einen Moment"
        raise SendError(error_msg, e.resp.status) from e


def create_draft(message: dict, account: str | None = None) -> dict:
    """Create a draft email.

    Args:
        message: Message dict from compose_email or compose_reply.
        account: Account email to use. If None, uses resolved account.

    Returns:
        API response with draft ID and message info.

    Raises:
        SendError: If creating draft fails.
    """
    service = get_gmail_service(account=account)

    try:
        body = {"message": message}
        request = service.users().drafts().create(userId="me", body=body)
        return _execute_with_retry(request, account=account)
    except HttpError as e:
        error_msg = str(e)
        if e.resp.status == 400:
            error_msg = "Invalid message format"
        elif e.resp.status == 403:
            error_msg = "Permission denied to create drafts"
        elif e.resp.status == 429:
            error_msg = "Too many requests - please wait a moment"
        raise SendError(error_msg, e.resp.status) from e


def list_drafts(
    account: str | None = None,
    max_results: int = 20,
) -> list[dict]:
    """List all drafts.

    Uses batch requests to fetch draft details efficiently.

    Args:
        account: Account email to use. If None, uses resolved account.
        max_results: Maximum number of drafts to return.

    Returns:
        List of draft dicts with id and message info.
    """
    service = get_gmail_service(account=account)

    request = service.users().drafts().list(userId="me", maxResults=max_results)
    response = _execute_with_retry(request, account=account)

    drafts = response.get("drafts", [])

    if not drafts:
        return []

    # Use batch request to fetch all draft details at once
    result = []
    errors = []

    def handle_response(_request_id: str, response: dict, exception: Exception | None):
        if exception is not None:
            errors.append(exception)
            return

        # Parse message headers
        message = response.get("message", {})
        headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}

        result.append(
            {
                "id": response["id"],
                "message_id": message.get("id"),
                "thread_id": message.get("threadId"),
                "to": headers.get("To", ""),
                "cc": headers.get("Cc", ""),
                "subject": headers.get("Subject", "(no subject)"),
                "snippet": message.get("snippet", ""),
            }
        )

    batch = service.new_batch_http_request(callback=handle_response)

    for draft in drafts:
        batch.add(
            service.users()
            .drafts()
            .get(
                userId="me",
                id=draft["id"],
                format="metadata",
            )
        )

    batch.execute()

    return result


def get_draft(
    draft_id: str,
    account: str | None = None,
    include_body: bool = True,
) -> dict | None:
    """Get a draft by ID.

    Args:
        draft_id: The draft ID.
        account: Account email to use. If None, uses resolved account.
        include_body: Whether to include the full message body.

    Returns:
        Draft dict with message details, or None if not found.

    Raises:
        DraftNotFoundError: If draft is not found.
    """
    service = get_gmail_service(account=account)

    try:
        format_type = "full" if include_body else "metadata"
        request = (
            service.users()
            .drafts()
            .get(
                userId="me",
                id=draft_id,
                format=format_type,
            )
        )
        response = _execute_with_retry(request, account=account)

        # Parse message headers
        message = response.get("message", {})
        headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}

        result = {
            "id": response["id"],
            "message_id": message.get("id"),
            "thread_id": message.get("threadId"),
            "to": headers.get("To", ""),
            "cc": headers.get("Cc", ""),
            "subject": headers.get("Subject", "(no subject)"),
            "snippet": message.get("snippet", ""),
        }

        if include_body:
            body_text, body_html, attachments = _parse_message_parts(
                message.get("payload", {}), message.get("id", "")
            )
            result["body_text"] = body_text
            result["body_html"] = body_html
            result["attachments"] = [
                {"filename": a.filename, "size": a.size, "mime_type": a.mime_type}
                for a in attachments
            ]

        return result

    except HttpError as e:
        if e.resp.status == 404:
            raise DraftNotFoundError(draft_id) from e
        raise


def send_draft(draft_id: str, account: str | None = None) -> dict:
    """Send an existing draft.

    Args:
        draft_id: The draft ID to send.
        account: Account email to use. If None, uses resolved account.

    Returns:
        API response with sent message info.

    Raises:
        DraftNotFoundError: If draft is not found.
        SendError: If sending fails.
    """
    service = get_gmail_service(account=account)

    try:
        request = (
            service.users()
            .drafts()
            .send(
                userId="me",
                body={"id": draft_id},
            )
        )
        return _execute_with_retry(request, account=account)
    except HttpError as e:
        if e.resp.status == 404:
            raise DraftNotFoundError(draft_id) from e
        error_msg = str(e)
        if e.resp.status == 400:
            error_msg = "Invalid draft - possibly missing recipients"
        elif e.resp.status == 403:
            error_msg = "Permission denied to send"
        raise SendError(error_msg, e.resp.status) from e


def delete_draft(draft_id: str, account: str | None = None) -> None:
    """Delete a draft.

    Args:
        draft_id: The draft ID to delete.
        account: Account email to use. If None, uses resolved account.

    Raises:
        DraftNotFoundError: If draft is not found.
    """
    service = get_gmail_service(account=account)

    try:
        request = service.users().drafts().delete(userId="me", id=draft_id)
        _execute_with_retry(request, account=account)
    except HttpError as e:
        if e.resp.status == 404:
            raise DraftNotFoundError(draft_id) from e
        raise
