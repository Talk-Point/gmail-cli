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


class TestMultiAccountCredentials:
    """Tests for multi-account credentials storage (T003-T009)."""

    def test_list_accounts_returns_empty_when_no_accounts(self) -> None:
        """T003: Test list_accounts returns empty list when no accounts exist."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = None

            from gmail_cli.services.credentials import list_accounts

            result = list_accounts()
            assert result == []

    def test_list_accounts_returns_accounts_list(self) -> None:
        """T003: Test list_accounts returns list of account emails."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            mock_keyring.get_password.return_value = json.dumps(
                ["user@gmail.com", "work@company.com"]
            )

            from gmail_cli.services.credentials import list_accounts

            result = list_accounts()
            assert result == ["user@gmail.com", "work@company.com"]

    def test_get_default_account_returns_none_when_not_set(self) -> None:
        """T004: Test get_default_account returns None when no default."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = None

            from gmail_cli.services.credentials import get_default_account

            result = get_default_account()
            assert result is None

    def test_get_default_account_returns_email(self) -> None:
        """T004: Test get_default_account returns the default email."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = "user@gmail.com"

            from gmail_cli.services.credentials import get_default_account

            result = get_default_account()
            assert result == "user@gmail.com"

    def test_set_default_account_stores_email(self) -> None:
        """T005: Test set_default_account stores the email in keyring."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            from gmail_cli.services.credentials import (
                DEFAULT_ACCOUNT_KEY,
                SERVICE_NAME,
                set_default_account,
            )

            set_default_account("user@gmail.com")

            mock_keyring.set_password.assert_called_with(
                SERVICE_NAME, DEFAULT_ACCOUNT_KEY, "user@gmail.com"
            )

    def test_save_credentials_with_account_stores_in_account_specific_key(
        self,
    ) -> None:
        """T006: Test save_credentials stores under account-specific key."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            mock_keyring.get_password.return_value = json.dumps([])

            from gmail_cli.services.credentials import save_credentials

            mock_creds = MagicMock()
            mock_creds.token = "access_token"
            mock_creds.refresh_token = "refresh_token"
            mock_creds.token_uri = "https://oauth2.googleapis.com/token"
            mock_creds.client_id = "client_id"
            mock_creds.client_secret = "client_secret"
            mock_creds.scopes = ["gmail.readonly"]
            mock_creds.expiry = datetime(2025, 12, 1, 16, 30, 0, tzinfo=UTC)

            save_credentials(mock_creds, account="test@gmail.com")

            # Verify credentials stored under account-specific key
            calls = mock_keyring.set_password.call_args_list
            creds_call = [c for c in calls if "oauth_test@gmail.com" in str(c)]
            assert len(creds_call) == 1

    def test_save_credentials_adds_to_accounts_list(self) -> None:
        """T006: Test save_credentials adds account to accounts list."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            mock_keyring.get_password.return_value = json.dumps([])

            from gmail_cli.services.credentials import save_credentials

            mock_creds = MagicMock()
            mock_creds.token = "access_token"
            mock_creds.refresh_token = "refresh_token"
            mock_creds.token_uri = "https://oauth2.googleapis.com/token"
            mock_creds.client_id = "client_id"
            mock_creds.client_secret = "client_secret"
            mock_creds.scopes = ["gmail.readonly"]
            mock_creds.expiry = datetime(2025, 12, 1, 16, 30, 0, tzinfo=UTC)

            save_credentials(mock_creds, account="new@gmail.com")

            # Verify accounts list updated
            calls = mock_keyring.set_password.call_args_list
            list_calls = [c for c in calls if "accounts_list" in str(c)]
            assert len(list_calls) == 1

    def test_load_credentials_with_account_loads_from_account_key(self) -> None:
        """T007: Test load_credentials loads from account-specific key."""
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

            result = load_credentials(account="test@gmail.com")

            mock_keyring.get_password.assert_called_with("gmail-cli", "oauth_test@gmail.com")
            assert result is not None
            assert result.token == "access_token"

    def test_delete_credentials_with_account_removes_from_keyring(self) -> None:
        """T008: Test delete_credentials removes account-specific credentials."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            mock_keyring.get_password.return_value = json.dumps(
                ["test@gmail.com", "other@gmail.com"]
            )

            from gmail_cli.services.credentials import delete_credentials

            delete_credentials(account="test@gmail.com")

            mock_keyring.delete_password.assert_called_with("gmail-cli", "oauth_test@gmail.com")

    def test_migrate_legacy_credentials_migrates_old_format(self) -> None:
        """T009: Test migrate_legacy_credentials converts old single-account format."""
        with (
            patch("gmail_cli.services.credentials.keyring") as mock_keyring,
            patch("gmail_cli.services.credentials._get_email_from_credentials") as mock_get_email,
        ):
            import json

            legacy_creds = {
                "token": "access_token",
                "refresh_token": "refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "expiry": "2025-12-01T16:30:00+00:00",
            }

            def get_password_side_effect(_service: str, key: str) -> str | None:
                if key == "oauth_credentials":
                    return json.dumps(legacy_creds)
                if key == "accounts_list":
                    return None
                return None

            mock_keyring.get_password.side_effect = get_password_side_effect
            mock_get_email.return_value = "legacy@gmail.com"

            from gmail_cli.services.credentials import migrate_legacy_credentials

            result = migrate_legacy_credentials()

            assert result is True
            # Verify old key was deleted
            mock_keyring.delete_password.assert_called()

    def test_migrate_legacy_credentials_returns_false_when_no_legacy(self) -> None:
        """T009: Test migrate_legacy_credentials returns False when no legacy creds."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = None

            from gmail_cli.services.credentials import migrate_legacy_credentials

            result = migrate_legacy_credentials()

            assert result is False

    def test_delete_credentials_updates_default_when_deleted(self) -> None:
        """Test delete_credentials updates default when deleting default account."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            def get_password_side_effect(_service: str, key: str) -> str | None:
                if key == "accounts_list":
                    return json.dumps(["first@gmail.com", "second@gmail.com"])
                if key == "default_account":
                    return "first@gmail.com"
                return None

            mock_keyring.get_password.side_effect = get_password_side_effect

            from gmail_cli.services.credentials import delete_credentials

            delete_credentials(account="first@gmail.com")

            # Should have updated default to second account
            set_calls = [
                c for c in mock_keyring.set_password.call_args_list if "default_account" in str(c)
            ]
            assert len(set_calls) >= 1

    def test_clear_all_accounts(self) -> None:
        """Test clear_all_accounts removes all account data."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            import json

            mock_keyring.get_password.return_value = json.dumps(
                ["user1@gmail.com", "user2@gmail.com"]
            )

            from gmail_cli.services.credentials import clear_all_accounts

            clear_all_accounts()

            # Should have deleted credentials for both accounts plus metadata
            delete_calls = mock_keyring.delete_password.call_args_list
            assert len(delete_calls) >= 2  # At least the two account credentials

    def test_has_credentials_with_account(self) -> None:
        """Test has_credentials with specific account."""
        with patch("gmail_cli.services.credentials.keyring") as mock_keyring:
            mock_keyring.get_password.return_value = '{"token": "test"}'

            from gmail_cli.services.credentials import has_credentials

            result = has_credentials(account="test@gmail.com")

            assert result is True
            mock_keyring.get_password.assert_called_with("gmail-cli", "oauth_test@gmail.com")
