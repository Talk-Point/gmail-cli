"""Unit tests for draft service functions."""

from unittest.mock import MagicMock, patch

import pytest
from googleapiclient.errors import HttpError

from gmail_cli.services.gmail import (
    DraftNotFoundError,
    SendError,
    create_draft,
    delete_draft,
    get_draft,
    list_drafts,
    send_draft,
)


class TestCreateDraft:
    """Tests for create_draft function."""

    def test_create_draft_success(self) -> None:
        """Test successful draft creation."""
        mock_service = MagicMock()
        mock_create = MagicMock()
        mock_service.users.return_value.drafts.return_value.create.return_value = mock_create
        mock_create.execute.return_value = {
            "id": "r1234567890",
            "message": {
                "id": "msg123",
                "threadId": "thread123",
            },
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_service

            result = create_draft({"raw": "test_message"})

            assert result["id"] == "r1234567890"
            assert result["message"]["id"] == "msg123"
            mock_service.users.return_value.drafts.return_value.create.assert_called_once()

    def test_create_draft_invalid_format_error(self) -> None:
        """Test draft creation with invalid message format."""
        mock_service = MagicMock()
        mock_create = MagicMock()
        mock_service.users.return_value.drafts.return_value.create.return_value = mock_create

        resp = MagicMock()
        resp.status = 400
        mock_create.execute.side_effect = HttpError(resp, b"Invalid format")

        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get,
            pytest.raises(SendError) as exc_info,
        ):
            mock_get.return_value = mock_service
            create_draft({"raw": "invalid"})

        assert "Ungültiges Nachrichtenformat" in exc_info.value.message

    def test_create_draft_permission_error(self) -> None:
        """Test draft creation with permission denied."""
        mock_service = MagicMock()
        mock_create = MagicMock()
        mock_service.users.return_value.drafts.return_value.create.return_value = mock_create

        resp = MagicMock()
        resp.status = 403
        mock_create.execute.side_effect = HttpError(resp, b"Forbidden")

        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get,
            pytest.raises(SendError) as exc_info,
        ):
            mock_get.return_value = mock_service
            create_draft({"raw": "test"})

        assert "Keine Berechtigung" in exc_info.value.message


class TestListDrafts:
    """Tests for list_drafts function."""

    def test_list_drafts_returns_drafts(self) -> None:
        """Test listing drafts returns draft list."""
        mock_service = MagicMock()

        # Mock list response
        mock_list = MagicMock()
        mock_service.users.return_value.drafts.return_value.list.return_value = mock_list
        mock_list.execute.return_value = {
            "drafts": [
                {"id": "r1", "message": {"id": "msg1"}},
                {"id": "r2", "message": {"id": "msg2"}},
            ]
        }

        # Mock batch response
        mock_batch = MagicMock()
        mock_service.new_batch_http_request.return_value = mock_batch

        def batch_execute():
            # Simulate batch callbacks being called
            pass

        mock_batch.execute.side_effect = batch_execute

        # Mock individual get responses
        mock_get = MagicMock()
        mock_service.users.return_value.drafts.return_value.get.return_value = mock_get
        mock_get.execute.return_value = {
            "id": "r1",
            "message": {
                "id": "msg1",
                "threadId": "thread1",
                "snippet": "Test snippet",
                "payload": {
                    "headers": [
                        {"name": "To", "value": "test@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                    ]
                },
            },
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service:
            mock_get_service.return_value = mock_service

            result = list_drafts(max_results=10)

            # Should call list
            mock_service.users.return_value.drafts.return_value.list.assert_called_once()
            # Result is a list
            assert isinstance(result, list)

    def test_list_drafts_empty(self) -> None:
        """Test listing drafts when no drafts exist."""
        mock_service = MagicMock()

        mock_list = MagicMock()
        mock_service.users.return_value.drafts.return_value.list.return_value = mock_list
        mock_list.execute.return_value = {}

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_service

            result = list_drafts()

            assert result == []


class TestGetDraft:
    """Tests for get_draft function."""

    def test_get_draft_success(self) -> None:
        """Test getting a draft by ID."""
        mock_service = MagicMock()
        mock_get = MagicMock()
        mock_service.users.return_value.drafts.return_value.get.return_value = mock_get
        mock_get.execute.return_value = {
            "id": "r1234567890",
            "message": {
                "id": "msg123",
                "threadId": "thread123",
                "snippet": "Test snippet",
                "payload": {
                    "headers": [
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Cc", "value": "cc@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                    ],
                    "mimeType": "text/plain",
                    "body": {"data": "VGVzdCBib2R5"},  # "Test body" base64
                },
            },
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service:
            mock_get_service.return_value = mock_service

            result = get_draft("r1234567890", include_body=True)

            assert result["id"] == "r1234567890"
            assert result["to"] == "recipient@example.com"
            assert result["cc"] == "cc@example.com"
            assert result["subject"] == "Test Subject"

    def test_get_draft_not_found(self) -> None:
        """Test getting a non-existent draft."""
        mock_service = MagicMock()
        mock_get = MagicMock()
        mock_service.users.return_value.drafts.return_value.get.return_value = mock_get

        resp = MagicMock()
        resp.status = 404
        mock_get.execute.side_effect = HttpError(resp, b"Not found")

        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service,
            pytest.raises(DraftNotFoundError) as exc_info,
        ):
            mock_get_service.return_value = mock_service
            get_draft("invalid_id")

        assert "invalid_id" in exc_info.value.message

    def test_get_draft_without_body(self) -> None:
        """Test getting a draft without body (metadata only)."""
        mock_service = MagicMock()
        mock_get = MagicMock()
        mock_service.users.return_value.drafts.return_value.get.return_value = mock_get
        mock_get.execute.return_value = {
            "id": "r1234567890",
            "message": {
                "id": "msg123",
                "threadId": "thread123",
                "snippet": "Test snippet",
                "payload": {
                    "headers": [
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                    ],
                },
            },
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get_service:
            mock_get_service.return_value = mock_service

            result = get_draft("r1234567890", include_body=False)

            assert result["id"] == "r1234567890"
            assert "body_text" not in result
            # Verify metadata format was used
            call_args = mock_service.users.return_value.drafts.return_value.get.call_args
            assert call_args.kwargs["format"] == "metadata"


class TestSendDraft:
    """Tests for send_draft function."""

    def test_send_draft_success(self) -> None:
        """Test sending a draft successfully."""
        mock_service = MagicMock()
        mock_send = MagicMock()
        mock_service.users.return_value.drafts.return_value.send.return_value = mock_send
        mock_send.execute.return_value = {
            "id": "sent123",
            "threadId": "thread123",
            "labelIds": ["SENT"],
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_service

            result = send_draft("r1234567890")

            assert result["id"] == "sent123"
            assert result["threadId"] == "thread123"
            mock_service.users.return_value.drafts.return_value.send.assert_called_once()

    def test_send_draft_not_found(self) -> None:
        """Test sending a non-existent draft."""
        mock_service = MagicMock()
        mock_send = MagicMock()
        mock_service.users.return_value.drafts.return_value.send.return_value = mock_send

        resp = MagicMock()
        resp.status = 404
        mock_send.execute.side_effect = HttpError(resp, b"Not found")

        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get,
            pytest.raises(DraftNotFoundError) as exc_info,
        ):
            mock_get.return_value = mock_service
            send_draft("invalid_id")

        assert "invalid_id" in exc_info.value.message

    def test_send_draft_invalid_recipients(self) -> None:
        """Test sending a draft with invalid or missing recipients."""
        mock_service = MagicMock()
        mock_send = MagicMock()
        mock_service.users.return_value.drafts.return_value.send.return_value = mock_send

        resp = MagicMock()
        resp.status = 400
        mock_send.execute.side_effect = HttpError(resp, b"Invalid recipient")

        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get,
            pytest.raises(SendError) as exc_info,
        ):
            mock_get.return_value = mock_service
            send_draft("r1234567890")

        assert (
            "Ungültiger Entwurf" in exc_info.value.message
            or "fehlen Empfänger" in exc_info.value.message
        )


class TestDeleteDraft:
    """Tests for delete_draft function."""

    def test_delete_draft_success(self) -> None:
        """Test deleting a draft successfully."""
        mock_service = MagicMock()
        mock_delete = MagicMock()
        mock_service.users.return_value.drafts.return_value.delete.return_value = mock_delete
        mock_delete.execute.return_value = None

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_service

            # Should not raise
            delete_draft("r1234567890")

            mock_service.users.return_value.drafts.return_value.delete.assert_called_once()

    def test_delete_draft_not_found(self) -> None:
        """Test deleting a non-existent draft."""
        mock_service = MagicMock()
        mock_delete = MagicMock()
        mock_service.users.return_value.drafts.return_value.delete.return_value = mock_delete

        resp = MagicMock()
        resp.status = 404
        mock_delete.execute.side_effect = HttpError(resp, b"Not found")

        with (
            patch("gmail_cli.services.gmail.get_gmail_service") as mock_get,
            pytest.raises(DraftNotFoundError) as exc_info,
        ):
            mock_get.return_value = mock_service
            delete_draft("invalid_id")

        assert "invalid_id" in exc_info.value.message
