"""Integration tests for auth CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app

runner = CliRunner()


class TestAuthLogin:
    """Tests for gmail auth login command."""

    def test_login_opens_browser_for_oauth(self) -> None:
        """Test that login initiates OAuth flow."""
        with (
            patch("gmail_cli.cli.auth.run_oauth_flow") as mock_oauth,
            patch("gmail_cli.cli.auth.get_user_email") as mock_email,
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
        ):
            mock_has.return_value = False
            mock_creds = MagicMock()
            mock_creds.scopes = ["https://mail.google.com/"]
            mock_oauth.return_value = mock_creds
            mock_email.return_value = "user@gmail.com"

            result = runner.invoke(app, ["auth", "login"])

            # OAuth flow should be initiated
            mock_oauth.assert_called_once()
            assert result.exit_code == 0

    def test_login_prompts_when_already_authenticated(self) -> None:
        """Test that login prompts when already authenticated."""
        with (
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
        ):
            mock_has.return_value = True

            # Simulate user saying "n" to re-authenticate prompt
            result = runner.invoke(app, ["auth", "login"], input="n\n")

            assert result.exit_code == 0
            assert "beibehalten" in result.output or "cancelled" in result.output


class TestAuthLogout:
    """Tests for gmail auth logout command."""

    def test_logout_deletes_credentials(self) -> None:
        """Test that logout deletes stored credentials."""
        with patch("gmail_cli.cli.auth.logout") as mock_logout:
            result = runner.invoke(app, ["auth", "logout"])

            mock_logout.assert_called_once()
            assert result.exit_code == 0

    def test_logout_succeeds_when_no_credentials(self) -> None:
        """Test that logout succeeds even without credentials."""
        with patch("gmail_cli.cli.auth.logout") as mock_logout:
            mock_logout.return_value = None  # No error

            result = runner.invoke(app, ["auth", "logout"])

            assert result.exit_code == 0


class TestAuthStatus:
    """Tests for gmail auth status command."""

    def test_status_shows_authenticated_when_valid(self) -> None:
        """Test that status shows authenticated with valid credentials."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.auth.get_user_email") as mock_email,
            patch("gmail_cli.cli.auth.get_token_expiry") as mock_expiry,
        ):
            mock_auth.return_value = True
            mock_email.return_value = "user@gmail.com"
            mock_expiry.return_value = "2025-12-01 16:30:00"

            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 0
            assert "user@gmail.com" in result.output or "Authentifiziert" in result.output

    def test_status_shows_not_authenticated_when_invalid(self) -> None:
        """Test that status shows not authenticated without credentials."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 1

    def test_status_json_output(self) -> None:
        """Test that status outputs valid JSON with --json flag."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.auth.get_user_email") as mock_email,
            patch("gmail_cli.cli.auth.get_token_expiry") as mock_expiry,
        ):
            mock_auth.return_value = True
            mock_email.return_value = "user@gmail.com"
            mock_expiry.return_value = "2025-12-01T16:30:00Z"

            result = runner.invoke(app, ["--json", "auth", "status"])

            assert result.exit_code == 0
            assert "authenticated" in result.output
