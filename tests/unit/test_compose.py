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


class TestComposeEmailWithFromAddr:
    """Tests for email composition with Send-As address."""

    def test_compose_email_with_from_addr(self) -> None:
        """Test composing email with custom From address."""
        import base64
        import email

        from gmail_cli.services.gmail import compose_email

        message = compose_email(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Hello World!",
            from_addr="alias@example.com",
        )

        assert message is not None
        assert "raw" in message

        # Decode and verify From header
        raw_bytes = base64.urlsafe_b64decode(message["raw"])
        msg = email.message_from_bytes(raw_bytes)
        assert msg["From"] == "alias@example.com"

    def test_compose_email_without_from_addr(self) -> None:
        """Test composing email without From address (default behavior)."""
        import base64
        import email

        from gmail_cli.services.gmail import compose_email

        message = compose_email(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Hello World!",
        )

        assert message is not None
        # Decode and verify From header is not set
        raw_bytes = base64.urlsafe_b64decode(message["raw"])
        msg = email.message_from_bytes(raw_bytes)
        assert msg["From"] is None

    def test_compose_reply_with_from_addr(self) -> None:
        """Test composing reply with custom From address."""
        import base64
        import email

        from gmail_cli.services.gmail import compose_reply

        reply = compose_reply(
            to=["sender@example.com"],
            subject="Re: Original Subject",
            body="Thanks!",
            thread_id="thread123",
            message_id="<original@gmail.com>",
            from_addr="alias@example.com",
        )

        assert reply is not None
        # Decode and verify From header
        raw_bytes = base64.urlsafe_b64decode(reply["raw"])
        msg = email.message_from_bytes(raw_bytes)
        assert msg["From"] == "alias@example.com"


class TestListSendAsAddresses:
    """Tests for listing Send-As addresses."""

    def test_list_send_as_addresses_returns_verified_only(self) -> None:
        """Test that only verified addresses are returned."""
        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service,
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            mock_execute.return_value = {
                "sendAs": [
                    {
                        "sendAsEmail": "primary@example.com",
                        "displayName": "Primary",
                        "isPrimary": True,
                        "isDefault": True,
                        "verificationStatus": "accepted",
                    },
                    {
                        "sendAsEmail": "alias@example.com",
                        "displayName": "Alias",
                        "isPrimary": False,
                        "isDefault": False,
                        "verificationStatus": "accepted",
                    },
                    {
                        "sendAsEmail": "pending@example.com",
                        "displayName": "Pending",
                        "isPrimary": False,
                        "isDefault": False,
                        "verificationStatus": "pending",
                    },
                ]
            }

            from gmail_cli.services.gmail import list_send_as_addresses

            result = list_send_as_addresses()

            assert len(result) == 2
            emails = [addr["email"] for addr in result]
            assert "primary@example.com" in emails
            assert "alias@example.com" in emails
            assert "pending@example.com" not in emails

    def test_list_send_as_addresses_empty(self) -> None:
        """Test handling empty Send-As list."""
        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service,
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            mock_execute.return_value = {"sendAs": []}

            from gmail_cli.services.gmail import list_send_as_addresses

            result = list_send_as_addresses()

            assert result == []
