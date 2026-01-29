"""Tests for Email model."""

from datetime import datetime, timezone

from gmail_cli.models.email import Email


class TestEmailModel:
    """Tests for Email model properties."""

    def create_email(self, **kwargs) -> Email:
        """Create an Email with default values."""
        defaults = {
            "id": "test123",
            "thread_id": "thread123",
            "subject": "Test Subject",
            "sender": "sender@example.com",
            "recipients": ["recipient@example.com"],
            "date": datetime(2024, 1, 1, tzinfo=timezone.utc),
        }
        defaults.update(kwargs)
        return Email(**defaults)

    def test_sender_email_simple(self):
        """Extract email from simple sender."""
        email = self.create_email(sender="john@example.com")
        assert email.sender_email == "john@example.com"

    def test_sender_email_with_name(self):
        """Extract email from sender with display name."""
        email = self.create_email(sender="John Doe <john@example.com>")
        assert email.sender_email == "john@example.com"

    def test_sender_name_simple(self):
        """Extract name from simple sender (returns email as fallback)."""
        email = self.create_email(sender="john@example.com")
        assert email.sender_name == "john@example.com"

    def test_sender_name_with_name(self):
        """Extract name from sender with display name."""
        email = self.create_email(sender="John Doe <john@example.com>")
        assert email.sender_name == "John Doe"

    def test_sender_name_google_groups(self):
        """Extract name from Google Groups rewritten sender."""
        email = self.create_email(
            sender="'Max Theinert' via IT-Support <it-support@talk-point.company>"
        )
        assert email.sender_name == "'Max Theinert' via IT-Support"

    def test_reply_to_email_without_reply_to(self):
        """reply_to_email falls back to sender when no Reply-To header."""
        email = self.create_email(sender="John Doe <john@example.com>")
        assert email.reply_to_email == "john@example.com"

    def test_reply_to_email_with_reply_to(self):
        """reply_to_email uses Reply-To header when available."""
        email = self.create_email(
            sender="'Max' via Support <support@example.com>",
            reply_to="Max Theinert <max@example.com>",
        )
        assert email.reply_to_email == "max@example.com"

    def test_reply_to_email_google_groups_scenario(self):
        """reply_to_email correctly handles Google Groups emails."""
        email = self.create_email(
            sender="'Max Theinert' via IT-Support <it-support@talk-point.company>",
            reply_to="Max Theinert <max.theinert@talk-point.de>",
        )
        # Should return the Reply-To address, not the Groups address
        assert email.reply_to_email == "max.theinert@talk-point.de"
        # sender_email should still return the From address
        assert email.sender_email == "it-support@talk-point.company"
