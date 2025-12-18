"""Integration tests for draft CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app
from gmail_cli.services.gmail import DraftNotFoundError, SendError

runner = CliRunner()


class TestDraftListCommand:
    """Tests for gmail draft list command."""

    def test_draft_list_requires_authentication(self) -> None:
        """Test that draft list requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["draft", "list"])

            assert result.exit_code == 1

    def test_draft_list_shows_drafts(self) -> None:
        """Test listing drafts."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.list_drafts") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {
                    "id": "r1234567890",
                    "to": "recipient@example.com",
                    "subject": "Test Subject",
                    "snippet": "Test snippet...",
                },
                {
                    "id": "r0987654321",
                    "to": "another@example.com",
                    "subject": "Another Subject",
                    "snippet": "Another snippet...",
                },
            ]

            result = runner.invoke(app, ["draft", "list"])

            assert result.exit_code == 0
            assert "r1234567890" in result.output
            assert "recipient@example.com" in result.output
            assert "Test Subject" in result.output

    def test_draft_list_empty(self) -> None:
        """Test listing drafts when none exist."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.list_drafts") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = []

            result = runner.invoke(app, ["draft", "list"])

            assert result.exit_code == 0
            assert "No drafts" in result.output

    def test_draft_list_with_limit(self) -> None:
        """Test listing drafts with limit option."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.list_drafts") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = []

            result = runner.invoke(app, ["draft", "list", "--limit", "5"])

            assert result.exit_code == 0
            mock_list.assert_called_once_with(account=None, max_results=5)

    def test_draft_list_json_output(self) -> None:
        """Test listing drafts with JSON output."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.list_drafts") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {"id": "r1234567890", "to": "test@example.com", "subject": "Test"},
            ]

            result = runner.invoke(app, ["--json", "draft", "list"])

            assert result.exit_code == 0
            assert '"drafts"' in result.output
            assert '"count"' in result.output


class TestDraftShowCommand:
    """Tests for gmail draft show command."""

    def test_draft_show_displays_details(self) -> None:
        """Test showing draft details."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.get_draft") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = {
                "id": "r1234567890",
                "to": "recipient@example.com",
                "cc": "cc@example.com",
                "subject": "Test Subject",
                "thread_id": "thread123",
                "body_text": "This is the email body.",
                "attachments": [],
            }

            result = runner.invoke(app, ["draft", "show", "r1234567890"])

            assert result.exit_code == 0
            assert "r1234567890" in result.output
            assert "recipient@example.com" in result.output
            assert "Test Subject" in result.output
            assert "This is the email body" in result.output

    def test_draft_show_not_found(self) -> None:
        """Test showing non-existent draft."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.get_draft") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.side_effect = DraftNotFoundError("invalid_id")

            result = runner.invoke(app, ["draft", "show", "invalid_id"])

            assert result.exit_code == 1
            assert "invalid_id" in result.output
            assert "not found" in result.output

    def test_draft_show_with_attachments(self) -> None:
        """Test showing draft with attachments."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.get_draft") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = {
                "id": "r1234567890",
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "body_text": "Body with attachment.",
                "attachments": [
                    {"filename": "document.pdf", "size": 1048576, "mime_type": "application/pdf"},
                ],
            }

            result = runner.invoke(app, ["draft", "show", "r1234567890"])

            assert result.exit_code == 0
            assert "Attachments" in result.output
            assert "document.pdf" in result.output


class TestDraftSendCommand:
    """Tests for gmail draft send command."""

    def test_draft_send_success(self) -> None:
        """Test sending a draft successfully."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.send_draft") as mock_send,
        ):
            mock_auth.return_value = True
            mock_send.return_value = {
                "id": "sent123",
                "threadId": "thread123",
            }

            result = runner.invoke(app, ["draft", "send", "r1234567890"])

            assert result.exit_code == 0
            assert "Draft sent" in result.output
            assert "sent123" in result.output

    def test_draft_send_not_found(self) -> None:
        """Test sending non-existent draft."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.send_draft") as mock_send,
        ):
            mock_auth.return_value = True
            mock_send.side_effect = DraftNotFoundError("invalid_id")

            result = runner.invoke(app, ["draft", "send", "invalid_id"])

            assert result.exit_code == 1
            assert "invalid_id" in result.output
            assert "not found" in result.output

    def test_draft_send_failure(self) -> None:
        """Test draft send failure."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.send_draft") as mock_send,
        ):
            mock_auth.return_value = True
            mock_send.side_effect = SendError("Failed to send", 400)

            result = runner.invoke(app, ["draft", "send", "r1234567890"])

            assert result.exit_code == 1


class TestDraftDeleteCommand:
    """Tests for gmail draft delete command."""

    def test_draft_delete_success(self) -> None:
        """Test deleting a draft successfully."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.delete_draft") as mock_delete,
        ):
            mock_auth.return_value = True
            mock_delete.return_value = None

            result = runner.invoke(app, ["draft", "delete", "r1234567890"])

            assert result.exit_code == 0
            assert "Draft deleted" in result.output

    def test_draft_delete_not_found(self) -> None:
        """Test deleting non-existent draft."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.delete_draft") as mock_delete,
        ):
            mock_auth.return_value = True
            mock_delete.side_effect = DraftNotFoundError("invalid_id")

            result = runner.invoke(app, ["draft", "delete", "invalid_id"])

            assert result.exit_code == 1
            assert "invalid_id" in result.output
            assert "not found" in result.output


class TestSendWithDraftFlag:
    """Tests for gmail send --draft command."""

    def test_send_with_draft_flag_creates_draft(self) -> None:
        """Test sending with --draft flag creates a draft instead of sending."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.create_draft") as mock_create,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None
            mock_compose.return_value = {"raw": "test"}
            mock_create.return_value = {"id": "r1234567890", "message": {"threadId": "thread123"}}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to", "recipient@example.com",
                    "--subject", "Test Subject",
                    "--body", "Test body",
                    "--draft",
                ],
            )

            assert result.exit_code == 0
            assert "Draft created" in result.output
            mock_create.assert_called_once()


class TestReplyWithDraftFlag:
    """Tests for gmail reply --draft command."""

    def test_reply_with_draft_flag_creates_draft(self) -> None:
        """Test reply with --draft flag creates a draft instead of sending."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.create_draft") as mock_create,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
            patch("gmail_cli.cli.send.get_email") as mock_get_email,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None

            # Mock the original email
            mock_email = MagicMock()
            mock_email.sender = "sender@example.com"
            mock_email.subject = "Original Subject"
            mock_email.thread_id = "thread123"
            mock_email.message_id = "<msg@example.com>"
            mock_email.references = []
            mock_get_email.return_value = mock_email

            mock_compose.return_value = {"raw": "test"}
            mock_create.return_value = {
                "id": "r1234567890",
                "message": {"threadId": "thread123"},
            }

            result = runner.invoke(
                app,
                ["reply", "msg123", "--body", "Reply body", "--draft"],
            )

            assert result.exit_code == 0
            assert "Reply draft created" in result.output
            mock_create.assert_called_once()


class TestDraftMultiAccount:
    """Tests for draft commands with multi-account support."""

    def test_draft_list_with_account_option(self) -> None:
        """Test listing drafts for specific account."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.list_drafts") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = []

            result = runner.invoke(
                app,
                ["draft", "list", "--account", "work@company.com"],
            )

            assert result.exit_code == 0
            mock_list.assert_called_once_with(account="work@company.com", max_results=20)

    def test_draft_show_with_account_option(self) -> None:
        """Test showing draft for specific account."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.draft.get_draft") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = {
                "id": "r123",
                "to": "test@example.com",
                "subject": "Test",
                "body_text": "Body",
                "attachments": [],
            }

            result = runner.invoke(
                app,
                ["draft", "show", "r123", "--account", "work@company.com"],
            )

            assert result.exit_code == 0
            mock_get.assert_called_once_with("r123", account="work@company.com", include_body=True)
