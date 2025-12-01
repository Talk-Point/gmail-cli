"""Unit tests for email composition."""

from unittest.mock import MagicMock, patch


class TestComposeEmail:
    """Tests for email composition functionality."""

    def test_compose_email_creates_mime_message(self) -> None:
        """Test composing a basic email."""
        from gmail_cli.services.gmail import compose_email

        message = compose_email(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Hello World!",
        )

        assert message is not None
        assert "raw" in message

    def test_compose_email_with_cc_and_bcc(self) -> None:
        """Test composing email with CC and BCC."""
        from gmail_cli.services.gmail import compose_email

        message = compose_email(
            to=["recipient@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            subject="Test Subject",
            body="Hello World!",
        )

        assert message is not None

    def test_compose_email_with_attachment(self, tmp_path) -> None:
        """Test composing email with attachment."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        from gmail_cli.services.gmail import compose_email

        message = compose_email(
            to=["recipient@example.com"],
            subject="Test with attachment",
            body="See attached",
            attachments=[str(test_file)],
        )

        assert message is not None


class TestSendEmail:
    """Tests for email sending functionality."""

    def test_send_email_calls_api(self) -> None:
        """Test that send_email calls Gmail API."""
        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service,
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            mock_execute.return_value = {"id": "sent123", "threadId": "thread123"}

            from gmail_cli.services.gmail import send_email

            result = send_email({"raw": "test"})

            assert result is not None
            assert result["id"] == "sent123"


class TestReplyEmail:
    """Tests for email reply functionality."""

    def test_compose_reply_includes_thread_headers(self) -> None:
        """Test that reply includes proper threading headers."""
        from gmail_cli.services.gmail import compose_reply

        reply = compose_reply(
            to=["sender@example.com"],
            subject="Re: Original Subject",
            body="Thanks!",
            thread_id="thread123",
            message_id="<original@gmail.com>",
            references=["<ref1@gmail.com>"],
        )

        assert reply is not None
        assert "threadId" in reply
        assert reply["threadId"] == "thread123"
