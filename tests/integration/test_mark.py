"""Integration tests for mark CLI command."""

import json
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app

runner = CliRunner()


class TestMarkCommand:
    """Tests for gmail mark command."""

    def test_mark_requires_authentication(self) -> None:
        """Test that mark requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["mark", "msg123", "--read"])

            assert result.exit_code == 1

    def test_mark_requires_read_or_unread_flag(self) -> None:
        """Test that mark requires either --read or --unread flag."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"

            result = runner.invoke(app, ["mark", "msg123"])

            assert result.exit_code == 1
            assert "--read" in result.output or "--unread" in result.output

    def test_mark_rejects_both_read_and_unread(self) -> None:
        """Test that mark rejects both --read and --unread together."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"

            result = runner.invoke(app, ["mark", "msg123", "--read", "--unread"])

            assert result.exit_code == 1

    def test_mark_as_read_single_message(self) -> None:
        """Test marking a single message as read."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["INBOX"]}

            result = runner.invoke(app, ["mark", "msg123", "--read"])

            assert result.exit_code == 0
            assert "gelesen" in result.output
            mock_mark.assert_called_once_with("msg123", account="user@gmail.com")

    def test_mark_as_unread_single_message(self) -> None:
        """Test marking a single message as unread."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_unread") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["INBOX", "UNREAD"]}

            result = runner.invoke(app, ["mark", "msg123", "--unread"])

            assert result.exit_code == 0
            assert "ungelesen" in result.output
            mock_mark.assert_called_once_with("msg123", account="user@gmail.com")

    def test_mark_multiple_messages(self) -> None:
        """Test marking multiple messages at once."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg", "labelIds": ["INBOX"]}

            result = runner.invoke(app, ["mark", "msg1", "msg2", "msg3", "--read"])

            assert result.exit_code == 0
            assert mock_mark.call_count == 3
            assert "3/3" in result.output

    def test_mark_handles_not_found_error(self) -> None:
        """Test that mark handles MessageNotFoundError."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            from gmail_cli.services.gmail import MessageNotFoundError

            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.side_effect = MessageNotFoundError("nonexistent")

            result = runner.invoke(app, ["mark", "nonexistent", "--read"])

            assert result.exit_code == 1
            assert "nicht gefunden" in result.output

    def test_mark_partial_failure(self) -> None:
        """Test that mark continues on partial failure."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            from gmail_cli.services.gmail import MessageNotFoundError

            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            # First call succeeds, second fails, third succeeds
            mock_mark.side_effect = [
                {"id": "msg1", "labelIds": []},
                MessageNotFoundError("msg2"),
                {"id": "msg3", "labelIds": []},
            ]

            result = runner.invoke(app, ["mark", "msg1", "msg2", "msg3", "--read"])

            assert result.exit_code == 1  # Partial failure
            assert "2/3" in result.output

    def test_mark_json_output(self) -> None:
        """Test that mark outputs valid JSON with --json flag."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["INBOX"]}

            result = runner.invoke(app, ["--json", "mark", "msg123", "--read"])

            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["action"] == "read"
            assert data["success_count"] == 1
            assert data["total"] == 1

    def test_mark_with_account_option(self) -> None:
        """Test that mark uses specified account."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "work@company.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": []}

            result = runner.invoke(
                app, ["mark", "msg123", "--read", "--account", "work@company.com"]
            )

            assert result.exit_code == 0
            mock_resolve.assert_called_once_with("work@company.com")
