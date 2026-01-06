"""Integration tests for send/reply CLI commands."""

from datetime import datetime, timezone
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
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
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
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
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

    def test_send_requires_body(self) -> None:
        """Test that send requires body content."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = True

            result = runner.invoke(
                app,
                ["send", "--to", "recipient@example.com", "--subject", "Test"],
            )

            assert result.exit_code == 1
            assert "E-Mail-Text erforderlich" in result.output

    def test_send_with_body_file(self, tmp_path) -> None:
        """Test sending email with body from file."""
        body_file = tmp_path / "body.txt"
        body_file.write_text("Hello from file!")

        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body-file",
                    str(body_file),
                ],
            )

            assert result.exit_code == 0
            # Verify compose was called with file content
            call_kwargs = mock_compose.call_args.kwargs
            assert call_kwargs["body"] == "Hello from file!"

    def test_send_body_file_not_found(self) -> None:
        """Test error when body file doesn't exist."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = True

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body-file",
                    "/nonexistent/file.txt",
                ],
            )

            assert result.exit_code == 1
            assert "Datei nicht gefunden" in result.output

    def test_send_with_signature(self) -> None:
        """Test sending email with Gmail signature."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = "<div>My Signature</div>"
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi there",
                    "--signature",
                ],
            )

            assert result.exit_code == 0
            # Verify compose was called with signature in body
            call_kwargs = mock_compose.call_args.kwargs
            assert "--" in call_kwargs["body"]  # Signature separator

    def test_send_json_output(self) -> None:
        """Test send command with JSON output."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "--json",
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi",
                ],
            )

            assert result.exit_code == 0
            assert '"message_id": "sent123"' in result.output

    def test_send_default_includes_signature(self) -> None:
        """Test that send includes signature by default (no flag needed)."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = "<div>My Signature</div>"
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi there",
                ],
            )

            assert result.exit_code == 0
            # Signature should be included by default
            mock_sig.assert_called_once()
            call_kwargs = mock_compose.call_args.kwargs
            assert "--" in call_kwargs["body"]  # Signature separator

    def test_send_no_signature_excludes_signature(self) -> None:
        """Test that --no-signature flag excludes signature."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = "<div>My Signature</div>"
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi there",
                    "--no-signature",
                ],
            )

            assert result.exit_code == 0
            # Signature should NOT be fetched when --no-signature is used
            mock_sig.assert_not_called()
            call_kwargs = mock_compose.call_args.kwargs
            assert "--" not in call_kwargs["body"]  # No signature separator

    def test_send_no_signature_when_none_configured(self) -> None:
        """Test that send works gracefully when no signature is configured."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi there",
                ],
            )

            assert result.exit_code == 0
            # Should still work without error
            call_kwargs = mock_compose.call_args.kwargs
            assert call_kwargs["body"] == "Hi there"  # No signature added

    def test_send_with_sig_shorthand(self) -> None:
        """Test that --sig shorthand works (backwards compatibility)."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = "<div>My Signature</div>"
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi there",
                    "--sig",
                ],
            )

            assert result.exit_code == 0
            # Signature should be included
            mock_sig.assert_called_once()
            call_kwargs = mock_compose.call_args.kwargs
            assert "--" in call_kwargs["body"]  # Signature separator


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
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
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
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
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
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
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
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = None  # No signature configured
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                cc=["original-cc@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
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

    def test_reply_default_includes_signature(self) -> None:
        """Test that reply includes signature by default (no flag needed)."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = "<div>My Signature</div>"
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
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
            # Signature should be included by default
            mock_sig.assert_called_once()
            call_kwargs = mock_compose.call_args.kwargs
            assert "--" in call_kwargs["body"]  # Signature separator

    def test_reply_no_signature_excludes_signature(self) -> None:
        """Test that reply --no-signature excludes signature."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_sig.return_value = "<div>My Signature</div>"
            mock_get.return_value = Email(
                id="msg123",
                thread_id="thread123",
                subject="Original Subject",
                sender="sender@example.com",
                recipients=["me@example.com"],
                date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc),
                snippet="Test...",
                message_id="<original@gmail.com>",
                references=[],
            )
            mock_compose.return_value = {"raw": "test", "threadId": "thread123"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                ["reply", "msg123", "--body", "Thanks!", "--no-signature"],
            )

            assert result.exit_code == 0
            # Signature should NOT be fetched when --no-signature is used
            mock_sig.assert_not_called()
            call_kwargs = mock_compose.call_args.kwargs
            assert "--" not in call_kwargs["body"]  # No signature separator


class TestSendAsCommand:
    """Tests for gmail sendas command."""

    def test_sendas_requires_authentication(self) -> None:
        """Test that sendas requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["sendas"])

            assert result.exit_code == 1

    def test_sendas_lists_addresses(self) -> None:
        """Test listing Send-As addresses."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.list_send_as_addresses") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {
                    "email": "primary@example.com",
                    "displayName": "Primary User",
                    "isPrimary": True,
                    "isDefault": True,
                },
                {
                    "email": "alias@example.com",
                    "displayName": "",
                    "isPrimary": False,
                    "isDefault": False,
                },
            ]

            result = runner.invoke(app, ["sendas"])

            assert result.exit_code == 0
            assert "primary@example.com" in result.output
            assert "alias@example.com" in result.output
            assert "(primär)" in result.output

    def test_sendas_empty_list(self) -> None:
        """Test handling empty Send-As list."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.list_send_as_addresses") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = []

            result = runner.invoke(app, ["sendas"])

            assert result.exit_code == 0
            assert "Keine Send-As Adressen" in result.output

    def test_sendas_json_output(self) -> None:
        """Test JSON output for sendas command."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.list_send_as_addresses") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {
                    "email": "primary@example.com",
                    "displayName": "Primary",
                    "isPrimary": True,
                    "isDefault": True,
                },
            ]

            result = runner.invoke(app, ["--json", "sendas"])

            assert result.exit_code == 0
            assert '"sendas"' in result.output
            assert '"count": 1' in result.output


class TestSendWithFromOption:
    """Tests for send command with --from option."""

    def test_send_with_valid_from_address(self) -> None:
        """Test sending with valid --from address."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.list_send_as_addresses") as mock_list,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {"email": "alias@example.com", "isPrimary": False},
            ]
            mock_sig.return_value = None
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi",
                    "--from",
                    "alias@example.com",
                ],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args.kwargs
            assert call_kwargs["from_addr"] == "alias@example.com"

    def test_send_with_invalid_from_address(self) -> None:
        """Test sending with invalid --from address fails."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.list_send_as_addresses") as mock_list,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {"email": "valid@example.com", "isPrimary": True},
            ]

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi",
                    "--from",
                    "invalid@example.com",
                ],
            )

            assert result.exit_code == 1
            assert "ist keine gültige Send-As Adresse" in result.output
            assert "valid@example.com" in result.output

    def test_send_from_address_case_insensitive(self) -> None:
        """Test that --from address validation is case insensitive."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.list_send_as_addresses") as mock_list,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_list.return_value = [
                {"email": "Alias@Example.COM", "isPrimary": False},
            ]
            mock_sig.return_value = None
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "recipient@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Hi",
                    "--from",
                    "alias@example.com",
                ],
            )

            assert result.exit_code == 0
