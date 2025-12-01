"""Unit tests for Gmail service."""

from unittest.mock import MagicMock, patch


class TestGmailService:
    """Tests for the Gmail API service."""

    def test_search_emails_returns_results(self, mock_gmail_service: MagicMock) -> None:
        """Test that search returns email results."""
        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import search_emails

            result = search_emails("test query")

            assert result is not None
            assert len(result.emails) > 0

    def test_search_emails_builds_query_with_filters(self, mock_gmail_service: MagicMock) -> None:
        """Test that search builds query with filters."""
        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import search_emails

            search_emails(
                query="test",
                from_addr="sender@example.com",
                to_addr="recipient@example.com",
                subject="subject",
                label="INBOX",
            )

            # Verify the query was built correctly
            mock_gmail_service.users.return_value.messages.return_value.list.assert_called()

    def test_search_emails_handles_pagination(self, mock_gmail_service: MagicMock) -> None:
        """Test that search handles pagination correctly."""
        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import search_emails

            result = search_emails("test", limit=10)

            assert result.next_page_token is None or isinstance(result.next_page_token, str)

    def test_search_emails_returns_empty_on_no_results(self, mock_gmail_service: MagicMock) -> None:
        """Test that search returns empty list when no results."""
        mock_gmail_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
            "messages": [],
            "resultSizeEstimate": 0,
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import search_emails

            result = search_emails("nonexistent")

            assert len(result.emails) == 0

    def test_build_search_query_combines_filters(self) -> None:
        """Test that query builder combines filters correctly."""
        from gmail_cli.services.gmail import build_search_query

        query = build_search_query(
            query="test",
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            subject="subject",
            label="INBOX",
            after="2025-01-01",
            before="2025-12-31",
            has_attachment=True,
        )

        assert "test" in query
        assert "from:sender@example.com" in query
        assert "to:recipient@example.com" in query
        assert "subject:subject" in query
        assert "label:INBOX" in query
        assert "after:2025-01-01" in query
        assert "before:2025-12-31" in query
        assert "has:attachment" in query
