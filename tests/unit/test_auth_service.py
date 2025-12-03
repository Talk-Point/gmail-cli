"""Unit tests for auth service."""

from unittest.mock import MagicMock, patch

from gmail_cli.services.auth import (
    get_credentials,
    get_user_email,
    is_authenticated,
    refresh_credentials,
)


class TestAuthService:
    """Tests for the authentication service."""

    def test_get_user_email_returns_email(self) -> None:
        """Test getting the authenticated user's email."""
        with patch("gmail_cli.services.auth.resolve_account") as mock_resolve:
            mock_resolve.return_value = "user@gmail.com"

            email = get_user_email()

            assert email == "user@gmail.com"

    def test_is_authenticated_returns_true_with_valid_creds(self) -> None:
        """Test is_authenticated returns True with valid credentials."""
        with (
            patch("gmail_cli.services.auth.list_accounts") as mock_list,
            patch("gmail_cli.services.auth.get_credentials") as mock_get_creds,
        ):
            mock_list.return_value = ["user@gmail.com"]
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_get_creds.return_value = mock_creds

            assert is_authenticated() is True

    def test_is_authenticated_returns_false_without_creds(self) -> None:
        """Test is_authenticated returns False without credentials."""
        with patch("gmail_cli.services.auth.list_accounts") as mock_list:
            mock_list.return_value = []

            assert is_authenticated() is False

    def test_refresh_credentials_refreshes_expired_token(self) -> None:
        """Test that expired credentials are refreshed."""
        with (
            patch("gmail_cli.services.auth.resolve_account") as mock_resolve,
            patch("gmail_cli.services.auth.load_credentials") as mock_load,
            patch("gmail_cli.services.auth.save_credentials") as mock_save,
            patch("gmail_cli.services.auth.Request"),
        ):
            mock_resolve.return_value = "user@gmail.com"
            mock_creds = MagicMock()
            mock_creds.expired = True
            mock_creds.refresh_token = "refresh_token"
            mock_load.return_value = mock_creds

            result = refresh_credentials()

            assert result is True
            mock_creds.refresh.assert_called_once()
            mock_save.assert_called_once_with(mock_creds, account="user@gmail.com")

    def test_refresh_credentials_returns_false_without_refresh_token(self) -> None:
        """Test that refresh fails without refresh token."""
        with (
            patch("gmail_cli.services.auth.resolve_account") as mock_resolve,
            patch("gmail_cli.services.auth.load_credentials") as mock_load,
        ):
            mock_resolve.return_value = "user@gmail.com"
            mock_creds = MagicMock()
            mock_creds.refresh_token = None
            mock_load.return_value = mock_creds

            result = refresh_credentials()

            assert result is False

    def test_get_credentials_returns_none_when_not_authenticated(self) -> None:
        """Test get_credentials returns None when no credentials stored."""
        with (
            patch("gmail_cli.services.auth.migrate_legacy_credentials") as mock_migrate,
            patch("gmail_cli.services.auth.resolve_account") as mock_resolve,
            patch("gmail_cli.services.auth.load_credentials") as mock_load,
        ):
            mock_migrate.return_value = False
            mock_resolve.return_value = "user@gmail.com"
            mock_load.return_value = None

            assert get_credentials() is None


class TestAccountResolution:
    """Tests for multi-account resolution (T010-T012)."""

    def test_resolve_account_returns_explicit_account(self) -> None:
        """T010: Test resolve_account returns explicit account when provided."""
        with patch("gmail_cli.services.auth.list_accounts") as mock_list:
            mock_list.return_value = ["user@gmail.com", "work@company.com"]

            from gmail_cli.services.auth import resolve_account

            result = resolve_account(explicit_account="work@company.com")

            assert result == "work@company.com"

    def test_resolve_account_returns_env_var_when_no_explicit(self) -> None:
        """T010: Test resolve_account uses GMAIL_ACCOUNT env var."""
        import os

        with (
            patch("gmail_cli.services.auth.list_accounts") as mock_list,
            patch("gmail_cli.services.auth.get_default_account") as mock_default,
            patch.dict(os.environ, {"GMAIL_ACCOUNT": "env@gmail.com"}),
        ):
            mock_list.return_value = ["env@gmail.com", "other@gmail.com"]
            mock_default.return_value = "other@gmail.com"

            from gmail_cli.services.auth import resolve_account

            result = resolve_account()

            assert result == "env@gmail.com"

    def test_resolve_account_returns_default_when_no_env(self) -> None:
        """T010: Test resolve_account uses default when no explicit or env."""
        import os

        with (
            patch("gmail_cli.services.auth.list_accounts") as mock_list,
            patch("gmail_cli.services.auth.get_default_account") as mock_default,
            patch.dict(os.environ, {}, clear=True),
        ):
            # Remove GMAIL_ACCOUNT if present
            os.environ.pop("GMAIL_ACCOUNT", None)
            mock_list.return_value = ["user@gmail.com", "work@company.com"]
            mock_default.return_value = "user@gmail.com"

            from gmail_cli.services.auth import resolve_account

            result = resolve_account()

            assert result == "user@gmail.com"

    def test_resolve_account_returns_first_when_no_default(self) -> None:
        """T010: Test resolve_account uses first account when no default."""
        import os

        with (
            patch("gmail_cli.services.auth.list_accounts") as mock_list,
            patch("gmail_cli.services.auth.get_default_account") as mock_default,
            patch.dict(os.environ, {}, clear=True),
        ):
            os.environ.pop("GMAIL_ACCOUNT", None)
            mock_list.return_value = ["first@gmail.com", "second@gmail.com"]
            mock_default.return_value = None

            from gmail_cli.services.auth import resolve_account

            result = resolve_account()

            assert result == "first@gmail.com"

    def test_account_not_found_error_includes_available_accounts(self) -> None:
        """T011: Test AccountNotFoundError contains available accounts."""
        from gmail_cli.services.auth import AccountNotFoundError

        error = AccountNotFoundError("unknown@gmail.com", ["user@gmail.com", "work@company.com"])

        assert error.account == "unknown@gmail.com"
        assert error.available == ["user@gmail.com", "work@company.com"]
        assert "unknown@gmail.com" in str(error)

    def test_resolve_account_raises_account_not_found_error(self) -> None:
        """T011: Test resolve_account raises AccountNotFoundError for invalid account."""
        with patch("gmail_cli.services.auth.list_accounts") as mock_list:
            mock_list.return_value = ["user@gmail.com"]

            from gmail_cli.services.auth import AccountNotFoundError, resolve_account

            try:
                resolve_account(explicit_account="unknown@gmail.com")
                raise AssertionError("Expected AccountNotFoundError")
            except AccountNotFoundError as e:
                assert e.account == "unknown@gmail.com"
                assert e.available == ["user@gmail.com"]

    def test_no_account_configured_error_raised_when_empty(self) -> None:
        """T012: Test NoAccountConfiguredError raised when no accounts exist."""
        import os

        with (
            patch("gmail_cli.services.auth.list_accounts") as mock_list,
            patch("gmail_cli.services.auth.get_default_account") as mock_default,
            patch.dict(os.environ, {}, clear=True),
        ):
            os.environ.pop("GMAIL_ACCOUNT", None)
            mock_list.return_value = []
            mock_default.return_value = None

            from gmail_cli.services.auth import NoAccountConfiguredError, resolve_account

            try:
                resolve_account()
                raise AssertionError("Expected NoAccountConfiguredError")
            except NoAccountConfiguredError:
                pass  # Expected
