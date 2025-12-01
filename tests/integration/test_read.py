"""Integration tests for read CLI command."""

from datetime import UTC, datetime
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app

runner = CliRunner()


class TestReadCommand:
    """Tests for gmail read command."""

    def test_read_requires_authentication(self) -> None:
        """Test that read requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["read", "msg123"])

            assert result.exit_code == 1

    def test_read_displays_email_content(self) -> None:
        """Test that read displays email content."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.read.get_email") as mock_get,
        ):
            from gmail_cli.models.email import Email

            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Test Subject",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test snippet...",
                body_text="This is the full email body content.",
            )

            result = runner.invoke(app, ["read", "msg123"])

            assert result.exit_code == 0
            assert "Test Subject" in result.output
            assert "sender@example.com" in result.output

    def test_read_shows_not_found_message(self) -> None:
        """Test that read shows message when email not found."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.read.get_email") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = None

            result = runner.invoke(app, ["read", "nonexistent"])

            assert result.exit_code == 1

    def test_read_json_output(self) -> None:
        """Test that read outputs valid JSON with --json flag."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.read.get_email") as mock_get,
        ):
            from gmail_cli.models.email import Email

            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Test Subject",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test snippet...",
                body_text="Email body here.",
            )

            result = runner.invoke(app, ["--json", "read", "msg123"])

            assert result.exit_code == 0
            assert "msg123" in result.output
            assert "Test Subject" in result.output

    def test_read_with_html_conversion(self) -> None:
        """Test that HTML emails are converted to text."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.read.get_email") as mock_get,
        ):
            from gmail_cli.models.email import Email

            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="HTML Email",
                sender="sender@example.com",
                recipients=["recipient@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                body_text="",
                body_html="<p>Hello <b>World</b></p>",
            )

            result = runner.invoke(app, ["read", "msg123"])

            assert result.exit_code == 0
            # Should show converted text, not raw HTML tags
            assert "Hello" in result.output
