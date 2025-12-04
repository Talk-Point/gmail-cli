"""Integration tests for Markdown in send and reply commands."""

from datetime import UTC, datetime
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app
from gmail_cli.models.email import Email

runner = CliRunner()


class TestSendWithMarkdown:
    """Tests for gmail send with Markdown conversion."""

    def test_send_with_bold_converts_to_html(self) -> None:
        """Markdown bold text is converted to HTML strong tags."""
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
                [
                    "send",
                    "--to",
                    "test@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "**Bold text**",
                ],
            )

            assert result.exit_code == 0
            # Check that compose_email was called with html_body
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            assert call_kwargs.get("html_body") is not None
            assert "<strong>" in call_kwargs["html_body"]

    def test_send_with_table_converts_to_html(self) -> None:
        """Markdown tables are converted to HTML tables."""
        table_md = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |"""

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
                [
                    "send",
                    "--to",
                    "test@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    table_md,
                ],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            assert call_kwargs.get("html_body") is not None
            assert "<table" in call_kwargs["html_body"]

    def test_send_with_code_block_converts_to_html(self) -> None:
        """Markdown code blocks are converted to HTML pre/code tags."""
        code_md = """```python
def hello():
    print("Hello")
```"""

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
                [
                    "send",
                    "--to",
                    "test@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    code_md,
                ],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            assert call_kwargs.get("html_body") is not None
            assert "<pre" in call_kwargs["html_body"]
            assert "<code" in call_kwargs["html_body"]

    def test_send_plain_no_html_conversion(self) -> None:
        """With --plain flag, Markdown is NOT converted to HTML."""
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
                [
                    "send",
                    "--to",
                    "test@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "**not bold**",
                    "--plain",
                ],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            # html_body should be None in plain mode
            assert call_kwargs.get("html_body") is None

    def test_send_with_signature_combines_html(self) -> None:
        """Markdown body + HTML signature are properly combined."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}
            mock_sig.return_value = '<div class="signature">Test Sig</div>'

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "test@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "**Bold message**",
                    "--signature",
                ],
            )

            assert result.exit_code == 0
            mock_sig.assert_called_once()
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            # Should have HTML body with signature
            assert call_kwargs.get("html_body") is not None
            assert "signature" in call_kwargs["html_body"].lower()


class TestReplyWithMarkdown:
    """Tests for gmail reply with Markdown conversion."""

    def _create_mock_email(self) -> Email:
        """Create a mock email for reply tests."""
        return Email(
            id="original123",
            thread_id="thread123",
            message_id="<original@gmail.com>",
            sender="sender@example.com",
            recipients=["me@example.com"],
            cc=[],
            subject="Original Subject",
            snippet="Original snippet",
            body_text="Original body",
            body_html=None,
            date=datetime.now(UTC),
            labels=["INBOX"],
            references=[],
            attachments=[],
        )

    def test_reply_with_markdown_converts_to_html(self) -> None:
        """Reply with Markdown body is converted to HTML."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
            patch("gmail_cli.cli.send.get_email") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = self._create_mock_email()
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "reply",
                    "original123",
                    "--body",
                    "## Heading\n**Bold reply**",
                ],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            assert call_kwargs.get("html_body") is not None
            assert "<h2" in call_kwargs["html_body"]
            assert "<strong>" in call_kwargs["html_body"]

    def test_reply_with_signature_combines_markdown_and_sig(self) -> None:
        """Reply with Markdown and --signature combines both properly."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
            patch("gmail_cli.cli.send.get_email") as mock_get,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_get.return_value = self._create_mock_email()
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}
            mock_sig.return_value = '<div class="signature">Test Sig</div>'

            result = runner.invoke(
                app,
                [
                    "reply",
                    "original123",
                    "--body",
                    "Thank you for **your message**.",
                    "--signature",
                ],
            )

            assert result.exit_code == 0
            mock_sig.assert_called_once()
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            assert call_kwargs.get("html_body") is not None
            assert "signature" in call_kwargs["html_body"].lower()

    def test_reply_plain_no_html_conversion(self) -> None:
        """Reply with --plain does NOT convert Markdown."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_reply") as mock_compose,
            patch("gmail_cli.cli.send.get_email") as mock_get,
        ):
            mock_auth.return_value = True
            mock_get.return_value = self._create_mock_email()
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "reply123", "threadId": "thread123"}

            result = runner.invoke(
                app,
                [
                    "reply",
                    "original123",
                    "--body",
                    "**not bold**",
                    "--plain",
                ],
            )

            assert result.exit_code == 0
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            # html_body should be None in plain mode
            assert call_kwargs.get("html_body") is None


class TestPlainTextMode:
    """Tests for --plain flag behavior."""

    def test_plain_with_signature_uses_html_for_signature(self) -> None:
        """With --plain and --signature, signature is still HTML."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.send.send_email") as mock_send,
            patch("gmail_cli.cli.send.compose_email") as mock_compose,
            patch("gmail_cli.cli.send.get_signature") as mock_sig,
        ):
            mock_auth.return_value = True
            mock_compose.return_value = {"raw": "test"}
            mock_send.return_value = {"id": "sent123", "threadId": "thread123"}
            mock_sig.return_value = '<div class="signature">Test Sig</div>'

            result = runner.invoke(
                app,
                [
                    "send",
                    "--to",
                    "test@example.com",
                    "--subject",
                    "Test",
                    "--body",
                    "Plain text body",
                    "--plain",
                    "--signature",
                ],
            )

            assert result.exit_code == 0
            mock_sig.assert_called_once()
            mock_compose.assert_called_once()
            call_kwargs = mock_compose.call_args[1]
            # Even in plain mode, signature requires HTML
            assert call_kwargs.get("html_body") is not None
            assert "signature" in call_kwargs["html_body"].lower()
