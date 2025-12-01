"""Unit tests for email parsing."""

from unittest.mock import MagicMock, patch


class TestEmailParser:
    """Tests for email body parsing."""

    def test_parse_plain_text_body(self) -> None:
        """Test parsing plain text email body."""
        from gmail_cli.services.gmail import _parse_message_parts

        payload = {
            "mimeType": "text/plain",
            "body": {
                "data": "SGVsbG8gV29ybGQh"  # "Hello World!" base64 encoded
            },
        }

        body_text, body_html, attachments = _parse_message_parts(payload, "msg123")

        assert body_text == "Hello World!"
        assert body_html == ""
        assert len(attachments) == 0

    def test_parse_html_body(self) -> None:
        """Test parsing HTML email body."""
        from gmail_cli.services.gmail import _parse_message_parts

        # "<p>Hello</p>" base64 encoded
        payload = {
            "mimeType": "text/html",
            "body": {
                "data": "PHA-SGVsbG88L3A-"  # URL-safe base64
            },
        }

        body_text, body_html, attachments = _parse_message_parts(payload, "msg123")

        assert body_text == ""
        assert "<p" in body_html or "Hello" in body_html

    def test_parse_multipart_message(self) -> None:
        """Test parsing multipart email with text and HTML."""
        from gmail_cli.services.gmail import _parse_message_parts

        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "filename": "",
                    "body": {"data": "SGVsbG8gV29ybGQh"},  # "Hello World!"
                },
                {
                    "mimeType": "text/html",
                    "filename": "",
                    "body": {"data": "PGI-SGVsbG88L2I-"},  # "<b>Hello</b>"
                },
            ],
        }

        body_text, body_html, attachments = _parse_message_parts(payload, "msg123")

        assert "Hello World!" in body_text
        assert len(attachments) == 0

    def test_parse_message_with_attachment(self) -> None:
        """Test parsing email with attachment."""
        from gmail_cli.services.gmail import _parse_message_parts

        payload = {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "filename": "",
                    "body": {"data": "SGVsbG8h"},  # "Hello!"
                },
                {
                    "mimeType": "application/pdf",
                    "filename": "document.pdf",
                    "body": {"attachmentId": "att123", "size": 1024},
                },
            ],
        }

        body_text, body_html, attachments = _parse_message_parts(payload, "msg123")

        assert len(attachments) == 1
        assert attachments[0].filename == "document.pdf"
        assert attachments[0].id == "att123"
        assert attachments[0].size == 1024


class TestGetEmail:
    """Tests for get_email function."""

    def test_get_email_returns_full_email(self) -> None:
        """Test getting full email with body."""
        with (
            patch("gmail_cli.services.gmail.get_gmail_service"),
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_execute.return_value = {
                "id": "msg123",
                "threadId": "thread123",
                "labelIds": ["INBOX"],
                "snippet": "Test snippet",
                "internalDate": "1701432000000",
                "payload": {
                    "mimeType": "text/plain",
                    "headers": [
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                        {"name": "Date", "value": "Sun, 01 Dec 2025 12:00:00 +0000"},
                    ],
                    "body": {"data": "VGVzdCBib2R5"},  # "Test body"
                },
            }

            from gmail_cli.services.gmail import get_email

            email = get_email("msg123")

            assert email is not None
            assert email.id == "msg123"
            assert email.subject == "Test Subject"
            assert email.sender == "sender@example.com"
            assert "Test body" in email.body_text

    def test_get_email_returns_none_for_not_found(self) -> None:
        """Test that get_email returns None for non-existent message."""
        from googleapiclient.errors import HttpError

        with (
            patch("gmail_cli.services.gmail.get_gmail_service"),
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_resp = MagicMock()
            mock_resp.status = 404
            mock_execute.side_effect = HttpError(mock_resp, b"Not found")

            from gmail_cli.services.gmail import get_email

            email = get_email("nonexistent")

            assert email is None
