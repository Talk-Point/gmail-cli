"""Unit tests for auth service."""

from unittest.mock import MagicMock, patch


class TestAuthService:
    """Tests for the authentication service."""

    def test_get_user_email_returns_email(self) -> None:
        """Test getting the authenticated user's email."""
        with (
            patch("gmail_cli.services.auth.get_credentials") as mock_get_creds,
            patch("googleapiclient.discovery.build") as mock_build,
        ):
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_get_creds.return_value = mock_creds

            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.users.return_value.getProfile.return_value.execute.return_value = {
                "emailAddress": "user@gmail.com"
            }

            from gmail_cli.services.auth import get_user_email

            email = get_user_email()

            assert email == "user@gmail.com"

    def test_is_authenticated_returns_true_with_valid_creds(self) -> None:
        """Test is_authenticated returns True with valid credentials."""
        with patch("gmail_cli.services.auth.get_credentials") as mock_get_creds:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_get_creds.return_value = mock_creds

            from gmail_cli.services.auth import is_authenticated

            assert is_authenticated() is True

    def test_is_authenticated_returns_false_without_creds(self) -> None:
        """Test is_authenticated returns False without credentials."""
        with patch("gmail_cli.services.auth.get_credentials") as mock_get_creds:
            mock_get_creds.return_value = None

            from gmail_cli.services.auth import is_authenticated

            assert is_authenticated() is False

    def test_refresh_credentials_refreshes_expired_token(self) -> None:
        """Test that expired credentials are refreshed."""
        with (
            patch("gmail_cli.services.auth.load_credentials") as mock_load,
            patch("gmail_cli.services.auth.save_credentials") as mock_save,
            patch("gmail_cli.services.auth.Request"),
        ):
            mock_creds = MagicMock()
            mock_creds.expired = True
            mock_creds.refresh_token = "refresh_token"
            mock_load.return_value = mock_creds

            from gmail_cli.services.auth import refresh_credentials

            result = refresh_credentials()

            assert result is True
            mock_creds.refresh.assert_called_once()
            mock_save.assert_called_once_with(mock_creds)

    def test_refresh_credentials_returns_false_without_refresh_token(self) -> None:
        """Test that refresh fails without refresh token."""
        with patch("gmail_cli.services.auth.load_credentials") as mock_load:
            mock_creds = MagicMock()
            mock_creds.refresh_token = None
            mock_load.return_value = mock_creds

            from gmail_cli.services.auth import refresh_credentials

            result = refresh_credentials()

            assert result is False

    def test_get_credentials_returns_none_when_not_authenticated(self) -> None:
        """Test get_credentials returns None when no credentials stored."""
        with patch("gmail_cli.services.auth.load_credentials") as mock_load:
            mock_load.return_value = None

            from gmail_cli.services.auth import get_credentials

            assert get_credentials() is None
