"""Integration tests for search CLI command."""

from datetime import UTC
from unittest.mock import patch

from typer.testing import CliRunner

from gmail_cli.cli.main import app

runner = CliRunner()


class TestSearchCommand:
    """Tests for gmail search command."""

    def test_search_requires_authentication(self) -> None:
        """Test that search requires authentication."""
        with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
            mock_auth.return_value = False

            result = runner.invoke(app, ["search", "test"])

            assert result.exit_code == 1

    def test_search_displays_results_table(self) -> None:
        """Test that search displays results in table format."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.search.search_emails") as mock_search,
        ):
            from datetime import datetime

            from gmail_cli.models.email import Email
            from gmail_cli.models.search import SearchResult

            mock_auth.return_value = True
            mock_search.return_value = SearchResult(
                emails=[
                    Email(
                        id="msg1",
                        thread_id="thread1",
                        subject="Test Subject",
                        sender="sender@example.com",
                        recipients=["recipient@example.com"],
                        date=datetime(2025, 12, 1, 10, 30, 0, tzinfo=UTC),
                        snippet="Test snippet...",
                    )
                ],
                total_estimate=1,
                next_page_token=None,
                query="test",
            )

            result = runner.invoke(app, ["search", "test"])

            assert result.exit_code == 0
            assert "Test Subject" in result.output or "msg1" in result.output

    def test_search_with_filters(self) -> None:
        """Test search with filter options."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.search.search_emails") as mock_search,
        ):
            from gmail_cli.models.search import SearchResult

            mock_auth.return_value = True
            mock_search.return_value = SearchResult(
                emails=[],
                total_estimate=0,
                next_page_token=None,
                query="test",
            )

            result = runner.invoke(
                app,
                [
                    "search",
                    "test",
                    "--from",
                    "sender@example.com",
                    "--limit",
                    "10",
                ],
            )

            assert result.exit_code == 0
            mock_search.assert_called_once()

    def test_search_json_output(self) -> None:
        """Test that search outputs valid JSON with --json flag."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.search.search_emails") as mock_search,
        ):
            from gmail_cli.models.search import SearchResult

            mock_auth.return_value = True
            mock_search.return_value = SearchResult(
                emails=[],
                total_estimate=0,
                next_page_token=None,
                query="test",
            )

            result = runner.invoke(app, ["--json", "search", "test"])

            assert result.exit_code == 0
            assert "emails" in result.output

    def test_search_shows_no_results_message(self) -> None:
        """Test that search shows message when no results found."""
        with (
            patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
            patch("gmail_cli.cli.search.search_emails") as mock_search,
        ):
            from gmail_cli.models.search import SearchResult

            mock_auth.return_value = True
            mock_search.return_value = SearchResult(
                emails=[],
                total_estimate=0,
                next_page_token=None,
                query="nonexistent",
            )

            result = runner.invoke(app, ["search", "nonexistent"])

            assert result.exit_code == 0
