"""Tests for email address parsing utilities."""

import pytest

from gmail_cli.utils.email_utils import extract_email, extract_name, parse_email_address


class TestParseEmailAddress:
    """Tests for parse_email_address function."""

    def test_full_address_with_name(self):
        """Parse address with display name and email."""
        name, email = parse_email_address("John Doe <john@example.com>")
        assert name == "John Doe"
        assert email == "john@example.com"

    def test_email_only(self):
        """Parse address with only email."""
        name, email = parse_email_address("john@example.com")
        assert name == ""
        assert email == "john@example.com"

    def test_quoted_name(self):
        """Parse address with quoted display name."""
        name, email = parse_email_address('"John Doe" <john@example.com>')
        assert name == "John Doe"
        assert email == "john@example.com"

    def test_name_with_special_chars(self):
        """Parse address with special characters in name."""
        name, email = parse_email_address("'Max Theinert' via IT-Support <support@example.com>")
        assert name == "'Max Theinert' via IT-Support"
        assert email == "support@example.com"

    def test_empty_string(self):
        """Parse empty string."""
        name, email = parse_email_address("")
        assert name == ""
        assert email == ""


class TestExtractEmail:
    """Tests for extract_email function."""

    def test_full_address(self):
        """Extract email from full address."""
        assert extract_email("John Doe <john@example.com>") == "john@example.com"

    def test_email_only(self):
        """Extract email from email-only string."""
        assert extract_email("john@example.com") == "john@example.com"

    def test_google_groups_format(self):
        """Extract email from Google Groups rewritten address."""
        result = extract_email("'Notification' via IT-Support <it-support@talk-point.company>")
        assert result == "it-support@talk-point.company"

    def test_empty_string_returns_input(self):
        """Empty string returns empty string."""
        assert extract_email("") == ""


class TestExtractName:
    """Tests for extract_name function."""

    def test_full_address(self):
        """Extract name from full address."""
        assert extract_name("John Doe <john@example.com>") == "John Doe"

    def test_email_only_returns_email(self):
        """Email-only returns the email as fallback."""
        assert extract_name("john@example.com") == "john@example.com"

    def test_google_groups_format(self):
        """Extract name from Google Groups rewritten address."""
        result = extract_name("'Max Theinert' via IT-Support <it-support@talk-point.company>")
        assert result == "'Max Theinert' via IT-Support"

    def test_empty_string(self):
        """Empty string returns empty string."""
        assert extract_name("") == ""
