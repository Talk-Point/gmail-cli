"""Shared test fixtures and Gmail API mocks."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from gmail_cli.models.attachment import Attachment
from gmail_cli.models.email import Email


@pytest.fixture
def sample_email() -> Email:
    """Create a sample email for testing."""
    return Email(
        id="18c5a2b3d4e5f6a7",
        thread_id="18c5a2b3d4e5f6a0",
        subject="Test Subject",
        sender="Max Mustermann <max@example.com>",
        recipients=["recipient@example.com"],
        date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
        cc=["cc@example.com"],
        bcc=[],
        body_text="This is the plain text body.",
        body_html="<p>This is the <b>HTML</b> body.</p>",
        snippet="This is the plain text body...",
        labels=["INBOX", "UNREAD"],
        attachments=[],
        is_read=False,
        message_id="<message-id@example.com>",
        references=[],
    )


@pytest.fixture
def sample_email_with_attachments(sample_email: Email) -> Email:
    """Create a sample email with attachments."""
    sample_email.attachments = [
        Attachment(
            id="att1",
            message_id=sample_email.id,
            filename="document.pdf",
            mime_type="application/pdf",
            size=128307,
        ),
        Attachment(
            id="att2",
            message_id=sample_email.id,
            filename="image.png",
            mime_type="image/png",
            size=45678,
        ),
    ]
    return sample_email


@pytest.fixture
def sample_attachment() -> Attachment:
    """Create a sample attachment for testing."""
    return Attachment(
        id="att1",
        message_id="18c5a2b3d4e5f6a7",
        filename="document.pdf",
        mime_type="application/pdf",
        size=128307,
    )


@pytest.fixture
def mock_gmail_service() -> MagicMock:
    """Create a mock Gmail API service."""
    mock_service = MagicMock()

    # Mock users().messages().list()
    mock_messages = MagicMock()
    mock_service.users.return_value.messages.return_value = mock_messages

    mock_list = MagicMock()
    mock_messages.list.return_value = mock_list
    mock_list.execute.return_value = {
        "messages": [
            {"id": "18c5a2b3d4e5f6a7", "threadId": "18c5a2b3d4e5f6a0"},
            {"id": "18c5a2b3d4e5f6a8", "threadId": "18c5a2b3d4e5f6a1"},
        ],
        "nextPageToken": None,
        "resultSizeEstimate": 2,
    }

    # Mock users().messages().get()
    mock_get = MagicMock()
    mock_messages.get.return_value = mock_get
    mock_get.execute.return_value = {
        "id": "18c5a2b3d4e5f6a7",
        "threadId": "18c5a2b3d4e5f6a0",
        "labelIds": ["INBOX", "UNREAD"],
        "snippet": "This is a test email...",
        "internalDate": "1701426600000",  # 2025-12-01 10:30:00 UTC
        "payload": {
            "headers": [
                {"name": "From", "value": "Max Mustermann <max@example.com>"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Subject", "value": "Test Subject"},
                {"name": "Date", "value": "Mon, 1 Dec 2025 10:30:00 +0000"},
                {"name": "Message-ID", "value": "<message-id@example.com>"},
            ],
            "mimeType": "text/plain",
            "body": {
                "size": 100,
                "data": "VGhpcyBpcyB0aGUgcGxhaW4gdGV4dCBib2R5Lg==",  # Base64 encoded
            },
        },
    }

    # Mock users().messages().send()
    mock_send = MagicMock()
    mock_messages.send.return_value = mock_send
    mock_send.execute.return_value = {
        "id": "18c5a2b3d4e5f6b0",
        "threadId": "18c5a2b3d4e5f6a0",
        "labelIds": ["SENT"],
    }

    return mock_service


@pytest.fixture
def mock_credentials() -> MagicMock:
    """Create mock OAuth credentials."""
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.refresh_token = "mock_refresh_token"
    mock_creds.token = "mock_access_token"
    mock_creds.expiry = datetime(2025, 12, 1, 16, 30, 0, tzinfo=timezone.utc)
    return mock_creds


@pytest.fixture
def mock_keyring():
    """Mock the keyring module."""
    with patch("gmail_cli.services.credentials.keyring") as mock:
        yield mock


@pytest.fixture
def mock_multi_account_keyring():
    """Mock keyring with multiple accounts configured."""
    import json

    accounts_data = {
        "accounts_list": json.dumps(["user@gmail.com", "work@company.com"]),
        "default_account": "user@gmail.com",
        "oauth_user@gmail.com": json.dumps(
            {
                "token": "user_access_token",
                "refresh_token": "user_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "expiry": "2025-12-01T16:30:00+00:00",
            }
        ),
        "oauth_work@company.com": json.dumps(
            {
                "token": "work_access_token",
                "refresh_token": "work_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "expiry": "2025-12-01T17:00:00+00:00",
            }
        ),
    }

    def get_password(_service: str, key: str) -> str | None:
        return accounts_data.get(key)

    with patch("gmail_cli.services.credentials.keyring") as mock:
        mock.get_password.side_effect = get_password
        yield mock


@pytest.fixture
def mock_single_account_auth():
    """Mock authentication with a single account."""
    with (
        patch("gmail_cli.services.auth.list_accounts") as mock_list,
        patch("gmail_cli.services.auth.get_default_account") as mock_default,
        patch("gmail_cli.services.auth.load_credentials") as mock_load,
        patch("gmail_cli.services.auth.migrate_legacy_credentials") as mock_migrate,
    ):
        mock_list.return_value = ["user@gmail.com"]
        mock_default.return_value = "user@gmail.com"
        mock_migrate.return_value = False

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.expired = False
        mock_creds.token = "mock_token"
        mock_load.return_value = mock_creds

        yield {
            "list_accounts": mock_list,
            "get_default_account": mock_default,
            "load_credentials": mock_load,
            "credentials": mock_creds,
        }


@pytest.fixture
def mock_multi_account_auth():
    """Mock authentication with multiple accounts."""
    with (
        patch("gmail_cli.services.auth.list_accounts") as mock_list,
        patch("gmail_cli.services.auth.get_default_account") as mock_default,
        patch("gmail_cli.services.auth.load_credentials") as mock_load,
        patch("gmail_cli.services.auth.migrate_legacy_credentials") as mock_migrate,
    ):
        mock_list.return_value = ["user@gmail.com", "work@company.com"]
        mock_default.return_value = "user@gmail.com"
        mock_migrate.return_value = False

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.expired = False
        mock_creds.token = "mock_token"
        mock_load.return_value = mock_creds

        yield {
            "list_accounts": mock_list,
            "get_default_account": mock_default,
            "load_credentials": mock_load,
            "credentials": mock_creds,
        }
