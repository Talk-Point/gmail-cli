"""Unit tests for attachment handling."""

from unittest.mock import MagicMock, patch


class TestAttachmentDownload:
    """Tests for attachment download functionality."""

    def test_get_attachment_returns_data(self) -> None:
        """Test getting attachment data."""
        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service,
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service

            # Base64 URL-safe encoded "Hello World" (with proper padding)
            mock_execute.return_value = {"data": "SGVsbG8gV29ybGQ="}

            from gmail_cli.services.gmail import get_attachment

            data = get_attachment("msg123", "att456")

            assert data == b"Hello World"

    def test_get_attachment_returns_none_on_error(self) -> None:
        """Test that get_attachment returns None on API error."""
        from googleapiclient.errors import HttpError

        with (
            patch("gmail_cli.services.gmail.get_gmail_service"),
            patch("gmail_cli.services.gmail._execute_with_retry") as mock_execute,
        ):
            mock_resp = MagicMock()
            mock_resp.status = 404
            mock_execute.side_effect = HttpError(mock_resp, b"Not found")

            from gmail_cli.services.gmail import get_attachment

            data = get_attachment("msg123", "nonexistent")

            assert data is None

    def test_download_attachment_writes_file(self, tmp_path) -> None:
        """Test downloading attachment to file."""
        with (
            patch("gmail_cli.services.gmail.get_attachment") as mock_get,
        ):
            mock_get.return_value = b"File content here"

            from gmail_cli.services.gmail import download_attachment

            output_path = tmp_path / "test.pdf"
            result = download_attachment("msg123", "att456", str(output_path))

            assert result is True
            assert output_path.exists()
            assert output_path.read_bytes() == b"File content here"

    def test_download_attachment_returns_false_on_error(self, tmp_path) -> None:
        """Test that download returns False when attachment not found."""
        with patch("gmail_cli.services.gmail.get_attachment") as mock_get:
            mock_get.return_value = None

            from gmail_cli.services.gmail import download_attachment

            output_path = tmp_path / "test.pdf"
            result = download_attachment("msg123", "att456", str(output_path))

            assert result is False
            assert not output_path.exists()
