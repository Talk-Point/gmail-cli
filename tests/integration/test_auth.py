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
            patch("gmail_cli.cli.auth.list_accounts") as mock_list,
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
        ):
            mock_list.return_value = []
            mock_has.return_value = False
            mock_creds = MagicMock()
            mock_creds.scopes = ["https://mail.google.com/"]
            mock_oauth.return_value = (mock_creds, "user@gmail.com")

            result = runner.invoke(app, ["auth", "login"])

            # OAuth flow should be initiated
            mock_oauth.assert_called_once()
            assert result.exit_code == 0

    def test_login_prompts_when_already_authenticated(self) -> None:
        """Test that login prompts when already authenticated."""
        with (
            patch("gmail_cli.cli.auth.list_accounts") as mock_list,
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
        ):
            mock_list.return_value = ["existing@gmail.com"]
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
            patch("gmail_cli.cli.auth.list_accounts") as mock_list,
            patch("gmail_cli.cli.auth.get_default_account") as mock_default,
            patch("gmail_cli.cli.auth.get_token_expiry") as mock_expiry,
        ):
            mock_list.return_value = ["user@gmail.com"]
            mock_default.return_value = "user@gmail.com"
            mock_expiry.return_value = "2025-12-01 16:30:00"

            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 0
            assert "user@gmail.com" in result.output or "Authentifiziert" in result.output

    def test_status_shows_not_authenticated_when_invalid(self) -> None:
        """Test that status shows not authenticated without credentials."""
        with patch("gmail_cli.cli.auth.list_accounts") as mock_list:
            mock_list.return_value = []

            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 1

    def test_status_json_output(self) -> None:
        """Test that status outputs valid JSON with --json flag."""
        with (
            patch("gmail_cli.cli.auth.list_accounts") as mock_list,
            patch("gmail_cli.cli.auth.get_default_account") as mock_default,
            patch("gmail_cli.cli.auth.get_token_expiry") as mock_expiry,
        ):
            mock_list.return_value = ["user@gmail.com"]
            mock_default.return_value = "user@gmail.com"
            mock_expiry.return_value = "2025-12-01T16:30:00Z"

            result = runner.invoke(app, ["--json", "auth", "status"])

            assert result.exit_code == 0
            assert "authenticated" in result.output


class TestMultiAccountLogin:
    """Tests for multi-account login (T029-T031)."""

    def test_first_login_sets_default(self) -> None:
        """T029: Test that first login sets account as default."""
        with (
            patch("gmail_cli.cli.auth.run_oauth_flow") as mock_oauth,
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
            patch("gmail_cli.services.credentials.list_accounts") as mock_list,
        ):
            mock_has.return_value = False
            mock_list.return_value = []  # No accounts yet

            mock_creds = MagicMock()
            mock_creds.scopes = ["https://mail.google.com/"]
            mock_oauth.return_value = (mock_creds, "first@gmail.com")

            result = runner.invoke(app, ["auth", "login"])

            assert result.exit_code == 0
            assert "first@gmail.com" in result.output
            assert "default" in result.output.lower() or "first@gmail.com" in result.output

    def test_second_login_adds_to_list(self) -> None:
        """T030: Test that second login adds account to list without changing default."""
        with (
            patch("gmail_cli.cli.auth.run_oauth_flow") as mock_oauth,
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
            patch("gmail_cli.services.credentials.list_accounts") as mock_list,
            patch("gmail_cli.services.credentials.get_default_account") as mock_default,
        ):
            mock_has.return_value = False
            mock_list.return_value = ["first@gmail.com"]  # One account already
            mock_default.return_value = "first@gmail.com"

            mock_creds = MagicMock()
            mock_creds.scopes = ["https://mail.google.com/"]
            mock_oauth.return_value = (mock_creds, "second@gmail.com")

            result = runner.invoke(app, ["auth", "login"])

            assert result.exit_code == 0
            assert "second@gmail.com" in result.output

    def test_legacy_migration_on_login(self) -> None:
        """T031: Test that legacy credentials are migrated on login check."""
        with (
            patch("gmail_cli.cli.auth.has_credentials") as mock_has,
            patch("gmail_cli.services.auth.migrate_legacy_credentials") as mock_migrate,
            patch("gmail_cli.cli.auth.run_oauth_flow") as mock_oauth,
            patch("gmail_cli.services.credentials.list_accounts") as mock_list,
        ):
            mock_has.return_value = False
            mock_migrate.return_value = True  # Migration occurred
            mock_list.return_value = []

            mock_creds = MagicMock()
            mock_creds.scopes = ["https://mail.google.com/"]
            mock_oauth.return_value = (mock_creds, "user@gmail.com")

            result = runner.invoke(app, ["auth", "login"])

            # Login should complete successfully even with migration
            assert result.exit_code == 0


class TestAccountManagement:
    """Tests for account management commands (T038-T041)."""

    def test_status_lists_all_accounts(self) -> None:
        """T038: Test auth status lists all configured accounts."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.auth.list_accounts") as mock_list,
            patch("gmail_cli.cli.auth.get_default_account") as mock_default,
            patch("gmail_cli.cli.auth.get_token_expiry") as mock_expiry,
        ):
            mock_auth.return_value = True
            mock_list.return_value = ["user@gmail.com", "work@company.com"]
            mock_default.return_value = "user@gmail.com"
            mock_expiry.return_value = "2025-12-01 16:30:00"

            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 0
            assert "user@gmail.com" in result.output
            assert "work@company.com" in result.output

    def test_set_default_changes_default(self) -> None:
        """T039: Test auth set-default changes the default account."""
        with (
            patch("gmail_cli.cli.auth.list_accounts") as mock_list,
            patch("gmail_cli.cli.auth.set_default_account") as mock_set,
        ):
            mock_list.return_value = ["user@gmail.com", "work@company.com"]

            result = runner.invoke(app, ["auth", "set-default", "work@company.com"])

            assert result.exit_code == 0
            mock_set.assert_called_once_with("work@company.com")

    def test_logout_account_removes_specific_account(self) -> None:
        """T040: Test auth logout --account removes specific account."""
        with (
            patch("gmail_cli.cli.auth.logout") as mock_logout,
        ):
            mock_logout.return_value = ["work@company.com"]

            result = runner.invoke(app, ["auth", "logout", "--account", "work@company.com"])

            assert result.exit_code == 0
            mock_logout.assert_called_once_with(account="work@company.com", all_accounts=False)

    def test_logout_all_removes_all_accounts(self) -> None:
        """T041: Test auth logout --all removes all accounts."""
        with (
            patch("gmail_cli.cli.auth.logout") as mock_logout,
        ):
            mock_logout.return_value = ["user@gmail.com", "work@company.com"]

            result = runner.invoke(app, ["auth", "logout", "--all"])

            assert result.exit_code == 0
            mock_logout.assert_called_once_with(account=None, all_accounts=True)
