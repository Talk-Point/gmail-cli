"""Unit tests for credentials storage."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch


class TestCredentialsStorage:
    """Tests for the credentials storage service."""

    def test_save_credentials_stores_in_keyring(self) -> None:
        """Test that credentials are saved to keyring."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            from gmail_cli.services.credentials import save_credentials

            mock_creds = MagicMock()
            mock_creds.token = "access_token"
            mock_creds.refresh_token = "refresh_token"
            mock_creds.token_uri = "https://oauth2.googleapis.com/token"
            mock_creds.client_id = "client_id"
            mock_creds.client_secret = "client_secret"
            mock_creds.expiry = datetime(2025, 12, 1, 16, 30, 0, tzinfo=UTC)

            save_credentials(mock_creds)

            mock_keyring.set_password.assert_called()

    def test_load_credentials_returns_none_when_not_found(self) -> None:
        """Test that load returns None when no credentials exist."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = None

            from gmail_cli.services.credentials import load_credentials

            result = load_credentials()

            assert result is None

    def test_load_credentials_returns_credentials_when_found(self) -> None:
        """Test that load returns credentials when they exist."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            creds_data = {
                "token": "access_token",
                "refresh_token": "refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "expiry": "2025-12-01T16:30:00+00:00",
            }
            mock_keyring.get_password.return_value = json.dumps(creds_data)

            from gmail_cli.services.credentials import load_credentials

            result = load_credentials()

            assert result is not None
            assert result.token == "access_token"
            assert result.refresh_token == "refresh_token"

    def test_delete_credentials_removes_from_keyring(self) -> None:
        """Test that credentials are deleted from keyring."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            from gmail_cli.services.credentials import delete_credentials

            delete_credentials()

            mock_keyring.delete_password.assert_called()

    def test_has_credentials_returns_true_when_exists(self) -> None:
        """Test has_credentials returns True when credentials exist."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = '{"token": "test"}'

            from gmail_cli.services.credentials import has_credentials

            assert has_credentials() is True

    def test_has_credentials_returns_false_when_not_exists(self) -> None:
        """Test has_credentials returns False when no credentials."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = None

            from gmail_cli.services.credentials import has_credentials

            assert has_credentials() is False
