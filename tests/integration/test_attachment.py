"""Integration tests for attachment CLI commands."""

from datetime import UTC, datetime
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app
from gmail_cli.models.attachment import Attachment
from gmail_cli.models.email import Email

runner = CliRunner()


class TestAttachmentList:
    """Tests for gmail attachment list command."""

    def test_attachment_list_requires_authentication(self) -> None:
        """Test that attachment list requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["attachment", "list", "msg123"])

            assert result.exit_code == 1

    def test_attachment_list_shows_attachments(self) -> None:
        """Test that attachment list displays attachments."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.attachment.get_email") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Test Email",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                attachments=[
                    Attachment(
                        id="att1",
                        message_id="msg123",
                        filename="document.pdf",
                        mime_type="application/pdf",
                        size=1024,
                    ),
                    Attachment(
                        id="att2",
                        message_id="msg123",
                        filename="image.png",
                        mime_type="image/png",
                        size=2048,
                    ),
                ],
            )

            result = runner.invoke(app, ["attachment", "list", "msg123"])

            assert result.exit_code == 0
            assert "document.pdf" in result.output
            assert "image.png" in result.output

    def test_attachment_list_shows_no_attachments_message(self) -> None:
        """Test message when email has no attachments."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.attachment.get_email") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Test Email",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                attachments=[],
            )

            result = runner.invoke(app, ["attachment", "list", "msg123"])

            assert result.exit_code == 0


class TestAttachmentDownload:
    """Tests for gmail attachment download command."""

    def test_attachment_download_requires_authentication(self) -> None:
        """Test that attachment download requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["attachment", "download", "msg123", "document.pdf"])

            assert result.exit_code == 1

    def test_attachment_download_saves_file(self, tmp_path) -> None:
        """Test that attachment download saves file."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.attachment.get_email") as mock_get_email,
            patch("gmail_cli.cli.attachment.download_attachment") as mock_download,
        ):
            mock_auth.return_value = True
            mock_get_email.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Test Email",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                attachments=[
                    Attachment(
                        id="att1",
                        message_id="msg123",
                        filename="document.pdf",
                        mime_type="application/pdf",
                        size=1024,
                    ),
                ],
            )
            mock_download.return_value = True

            output_file = tmp_path / "document.pdf"
            result = runner.invoke(
                app,
                [
                    "attachment",
                    "download",
                    "msg123",
                    "document.pdf",
                    "--output",
                    str(output_file),
                ],
            )

            assert result.exit_code == 0
            mock_download.assert_called_once()

    def test_attachment_download_not_found(self) -> None:
        """Test error when attachment not found."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.attachment.get_email") as mock_get_email,
        ):
            mock_auth.return_value = True
            mock_get_email.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Test Email",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                attachments=[],
            )

            result = runner.invoke(app, ["attachment", "download", "msg123", "nonexistent.pdf"])

            assert result.exit_code == 1
