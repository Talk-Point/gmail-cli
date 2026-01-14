"""Integration tests for mark-read/mark-unread CLI commands."""

import json
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app

runner = CliRunner()


class TestMarkReadCommand:
    """Tests for gmail mark-read command."""

    def test_mark_read_requires_authentication(self) -> None:
        """Test that mark-read requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["mark-read", "msg123"])

            assert result.exit_code == 1

    def test_mark_read_single_message(self) -> None:
        """Test marking a single message as read."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["INBOX"]}

            result = runner.invoke(app, ["mark-read", "msg123"])

            assert result.exit_code == 0
            assert "gelesen" in result.output
            mock_mark.assert_called_once_with("msg123", account="user@gmail.com")

    def test_mark_read_multiple_messages(self) -> None:
        """Test marking multiple messages as read."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg", "labelIds": ["INBOX"]}

            result = runner.invoke(app, ["mark-read", "msg1", "msg2", "msg3"])

            assert result.exit_code == 0
            assert mock_mark.call_count == 3
            assert "3/3" in result.output

    def test_mark_read_handles_not_found(self) -> None:
        """Test that mark-read handles MessageNotFoundError."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            from gmail_cli.services.gmail import MessageNotFoundError

            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.side_effect = MessageNotFoundError("nonexistent")

            result = runner.invoke(app, ["mark-read", "nonexistent"])

            assert result.exit_code == 1
            assert "nicht gefunden" in result.output

    def test_mark_read_json_output(self) -> None:
        """Test that mark-read outputs valid JSON."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["INBOX"]}

            result = runner.invoke(app, ["--json", "mark-read", "msg123"])

            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["action"] == "read"
            assert data["success_count"] == 1

    def test_mark_read_with_account(self) -> None:
        """Test mark-read with account option."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_read") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "work@company.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": []}

            result = runner.invoke(app, ["mark-read", "msg123", "--account", "work@company.com"])

            assert result.exit_code == 0
            mock_resolve.assert_called_once_with("work@company.com")


class TestMarkUnreadCommand:
    """Tests for gmail mark-unread command."""

    def test_mark_unread_requires_authentication(self) -> None:
        """Test that mark-unread requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["mark-unread", "msg123"])

            assert result.exit_code == 1

    def test_mark_unread_single_message(self) -> None:
        """Test marking a single message as unread."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_unread") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["INBOX", "UNREAD"]}

            result = runner.invoke(app, ["mark-unread", "msg123"])

            assert result.exit_code == 0
            assert "ungelesen" in result.output
            mock_mark.assert_called_once_with("msg123", account="user@gmail.com")

    def test_mark_unread_multiple_messages(self) -> None:
        """Test marking multiple messages as unread."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_unread") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg", "labelIds": ["UNREAD"]}

            result = runner.invoke(app, ["mark-unread", "msg1", "msg2"])

            assert result.exit_code == 0
            assert mock_mark.call_count == 2
            assert "2/2" in result.output

    def test_mark_unread_partial_failure(self) -> None:
        """Test that mark-unread continues on partial failure."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_unread") as mock_mark,
        ):
            from gmail_cli.services.gmail import MessageNotFoundError

            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.side_effect = [
                {"id": "msg1", "labelIds": []},
                MessageNotFoundError("msg2"),
                {"id": "msg3", "labelIds": []},
            ]

            result = runner.invoke(app, ["mark-unread", "msg1", "msg2", "msg3"])

            assert result.exit_code == 1
            assert "2/3" in result.output

    def test_mark_unread_json_output(self) -> None:
        """Test that mark-unread outputs valid JSON."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.mark.resolve_account") as mock_resolve,
            patch("gmail_cli.cli.mark.mark_as_unread") as mock_mark,
        ):
            mock_auth.return_value = True
            mock_resolve.return_value = "user@gmail.com"
            mock_mark.return_value = {"id": "msg123", "labelIds": ["UNREAD"]}

            result = runner.invoke(app, ["--json", "mark-unread", "msg123"])

            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["action"] == "unread"
            assert data["success_count"] == 1
