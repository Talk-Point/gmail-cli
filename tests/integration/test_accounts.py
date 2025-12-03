"""Tests for accounts CLI commands."""

from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app

runner = CliRunner()


class TestAccountsList:
    """Tests for gmail accounts list command."""

    def test_accounts_list_shows_accounts_with_default_marker(self) -> None:
        """Test that accounts list shows all accounts with default marked."""
        with (
            patch("gmail_cli.cli.accounts.list_accounts") as mock_list,
            patch("gmail_cli.cli.accounts.get_default_account") as mock_default,
        ):
            mock_list.return_value = ["user@gmail.com", "work@company.com"]
            mock_default.return_value = "user@gmail.com"

            result = runner.invoke(app, ["accounts", "list"])

            assert result.exit_code == 0
            assert "user@gmail.com *" in result.output
            assert "work@company.com" in result.output
            assert "work@company.com *" not in result.output

    def test_accounts_list_no_accounts_shows_error(self) -> None:
        """Test that accounts list shows error when no accounts configured."""
        with (
            patch("gmail_cli.cli.accounts.list_accounts") as mock_list,
            patch("gmail_cli.cli.accounts.get_default_account") as mock_default,
        ):
            mock_list.return_value = []
            mock_default.return_value = None

            result = runner.invoke(app, ["accounts", "list"])

            assert result.exit_code == 1
            assert "Keine Konten konfiguriert" in result.output

    def test_accounts_list_json_output(self) -> None:
        """Test that accounts list outputs JSON when --json flag is used."""
        with (
            patch("gmail_cli.cli.accounts.list_accounts") as mock_list,
            patch("gmail_cli.cli.accounts.get_default_account") as mock_default,
        ):
            mock_list.return_value = ["user@gmail.com", "work@company.com"]
            mock_default.return_value = "user@gmail.com"

            result = runner.invoke(app, ["--json", "accounts", "list"])

            assert result.exit_code == 0
            assert '"accounts"' in result.output
            assert '"email": "user@gmail.com"' in result.output
            assert '"is_default": true' in result.output
            assert '"is_default": false' in result.output

    def test_accounts_list_json_empty(self) -> None:
        """Test that accounts list outputs empty JSON array when no accounts."""
        with (
            patch("gmail_cli.cli.accounts.list_accounts") as mock_list,
            patch("gmail_cli.cli.accounts.get_default_account") as mock_default,
        ):
            mock_list.return_value = []
            mock_default.return_value = None

            result = runner.invoke(app, ["--json", "accounts", "list"])

            assert result.exit_code == 1
            assert '"accounts": []' in result.output

    def test_accounts_list_single_account(self) -> None:
        """Test accounts list with single account."""
        with (
            patch("gmail_cli.cli.accounts.list_accounts") as mock_list,
            patch("gmail_cli.cli.accounts.get_default_account") as mock_default,
        ):
            mock_list.return_value = ["only@gmail.com"]
            mock_default.return_value = "only@gmail.com"

            result = runner.invoke(app, ["accounts", "list"])

            assert result.exit_code == 0
            assert "only@gmail.com *" in result.output
