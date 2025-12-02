"""Integration tests for send/reply CLI commands."""

from datetime import UTC, datetime
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app
from gmail_cli.models.email import Email
from gmail_cli.services.gmail import SendError

runner = CliRunner()


class TestSendCommand:
    """Tests for gmail send command."""

    def test_send_requires_authentication(self) -> None:
        """Test that send requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(
                app,
                ["send", "--to", "recipient@example.com", "--subject", "Test", "--body", "Hi"],
            )

            assert result.exit_code == 1

    def test_send_with_required_options(self) -> None:
        """Test sending email with required options."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
        ):
            mock_auth.return_value = True
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                ["send", "--to", "recipient@example.com", "--subject", "Test", "--body", "Hi"],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            mock_send.assert_called_once()

    def test_send_requires_recipient(self) -> None:
        """Test that send requires --to option."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = True

            result = runner.invoke(
                app,
                ["send", "--subject", "Test", "--body", "Hi"],
            )

            # Should fail due to missing --to
            assert result.exit_code != 0

    def test_send_shows_error_details(self) -> None:
        """Test that send shows detailed error message on failure."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
        ):
            mock_auth.return_value = True
            mock_compose.return_value = {"raw": "test"}
            mock_send.side_effect = SendError(
                "Ungültige E-Mail-Adresse oder Nachrichtenformat", 400
            )

            result = runner.invoke(
                app,
                ["send", "--to", "invalid", "--subject", "Test", "--body", "Hi"],
            )

            assert result.exit_code == 1
            assert "Ungültige E-Mail-Adresse" in result.output


class TestReplyCommand:
    """Tests for gmail reply command."""

    def test_reply_requires_authentication(self) -> None:
        """Test that reply requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(
                app,
                ["reply", "msg123", "--body", "Thanks!"],
            )

            assert result.exit_code == 1

    def test_reply_to_email(self) -> None:
        """Test replying to an email."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
        ):
            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                message_id="<original@gmail.com>",
                references=[],
            )
            mock_compose.return_value = {"raw": "test", "threadId": "thread123"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                ["reply", "msg123", "--body", "Thanks!"],
            )

            assert result.exit_code == 0

    def test_reply_email_not_found(self) -> None:
        """Test error when replying to non-existent email."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = None

            result = runner.invoke(
                app,
                ["reply", "nonexistent", "--body", "Thanks!"],
            )

            assert result.exit_code == 1

    def test_reply_with_cc(self) -> None:
        """Test replying to an email with CC recipients."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
        ):
            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                message_id="<original@gmail.com>",
                references=[],
            )
            mock_compose.return_value = {"raw": "test", "threadId": "thread123"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                ["reply", "msg123", "--body", "Thanks!", "--cc", "support@example.com"],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            # Verify CC was passed to compose_reply
            call_kwargs = mock_compose.call_args.kwargs
            assert call_kwargs["cc"] == ["support@example.com"]

    def test_reply_with_multiple_cc(self) -> None:
        """Test replying with multiple CC recipients."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
        ):
            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                message_id="<original@gmail.com>",
                references=[],
            )
            mock_compose.return_value = {"raw": "test", "threadId": "thread123"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "reply",
                    "msg123",
                    "--body",
                    "Thanks!",
                    "--cc",
                    "support@example.com",
                    "--cc",
                    "team@example.com",
                ],
            )

            assert result.exit_code == 0
            call_kwargs = mock_compose.call_args.kwargs
            assert "support@example.com" in call_kwargs["cc"]
            assert "team@example.com" in call_kwargs["cc"]

    def test_reply_all_with_cc_merges_recipients(self) -> None:
        """Test that reply all merges user CC with original CC."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
        ):
            mock_auth.return_value = True
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                cc=["original-cc@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                snippet="Test...",
                message_id="<original@gmail.com>",
                references=[],
            )
            mock_compose.return_value = {"raw": "test", "threadId": "thread123"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "reply",
                    "msg123",
                    "--body",
                    "Thanks!",
                    "--all",
                    "--cc",
                    "new-cc@example.com",
                ],
            )

            assert result.exit_code == 0
            call_kwargs = mock_compose.call_args.kwargs
            # Should contain both user-specified and original CC
            assert "new-cc@example.com" in call_kwargs["cc"]
            assert "original-cc@example.com" in call_kwargs["cc"]
