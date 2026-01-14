"""Unit tests for mark (read/unread) functionality."""

from unittest.mock import MagicMock, patch

import pytest
from googleapiclient.errors import HttpError


class TestMarkFunctions:
    """Tests for mark_as_read/unread service functions."""

    def test_mark_as_read_removes_unread_label(self, mock_gmail_service: MagicMock) -> None:
        """Test that mark_as_read removes UNREAD label."""
        # Setup mock for modify
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_modify.execute.return_value = {
            "id": "18c5a2b3d4e5f6a7",
            "labelIds": ["INBOX"],
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import mark_as_read

            result = mark_as_read("18c5a2b3d4e5f6a7")

            assert result["id"] == "18c5a2b3d4e5f6a7"
            mock_gmail_service.users.return_value.messages.return_value.modify.assert_called_once()
            call_args = (
                mock_gmail_service.users.return_value.messages.return_value.modify.call_args
            )
            assert call_args.kwargs["body"]["removeLabelIds"] == ["UNREAD"]

    def test_mark_as_unread_adds_unread_label(self, mock_gmail_service: MagicMock) -> None:
        """Test that mark_as_unread adds UNREAD label."""
        # Setup mock for modify
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_modify.execute.return_value = {
            "id": "18c5a2b3d4e5f6a7",
            "labelIds": ["INBOX", "UNREAD"],
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import mark_as_unread

            result = mark_as_unread("18c5a2b3d4e5f6a7")

            assert result["id"] == "18c5a2b3d4e5f6a7"
            mock_gmail_service.users.return_value.messages.return_value.modify.assert_called_once()
            call_args = (
                mock_gmail_service.users.return_value.messages.return_value.modify.call_args
            )
            assert call_args.kwargs["body"]["addLabelIds"] == ["UNREAD"]

    def test_mark_as_read_raises_message_not_found(
        self, mock_gmail_service: MagicMock
    ) -> None:
        """Test that mark_as_read raises MessageNotFoundError for non-existent message."""
        # Setup mock to raise 404
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_modify.execute.side_effect = HttpError(resp=mock_resp, content=b"Not Found")

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import MessageNotFoundError, mark_as_read

            with pytest.raises(MessageNotFoundError) as exc_info:
                mark_as_read("nonexistent")

            assert exc_info.value.message_id == "nonexistent"

    def test_modify_message_labels_with_account(self, mock_gmail_service: MagicMock) -> None:
        """Test that modify_message_labels passes account parameter."""
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_modify.execute.return_value = {"id": "msg1", "labelIds": []}

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import modify_message_labels

            modify_message_labels(
                "msg1",
                add_labels=["STARRED"],
                remove_labels=["UNREAD"],
                account="work@company.com",
            )

            mock_get.assert_called_once_with(account="work@company.com")


class TestModifyMessageLabels:
    """Tests for the generic modify_message_labels function."""

    def test_modify_with_both_add_and_remove(self, mock_gmail_service: MagicMock) -> None:
        """Test modifying with both add and remove labels."""
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_modify.execute.return_value = {
            "id": "msg1",
            "labelIds": ["INBOX", "STARRED"],
        }

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import modify_message_labels

            result = modify_message_labels(
                "msg1",
                add_labels=["STARRED", "IMPORTANT"],
                remove_labels=["UNREAD"],
            )

            assert result["id"] == "msg1"
            call_args = (
                mock_gmail_service.users.return_value.messages.return_value.modify.call_args
            )
            assert call_args.kwargs["body"]["addLabelIds"] == ["STARRED", "IMPORTANT"]
            assert call_args.kwargs["body"]["removeLabelIds"] == ["UNREAD"]

    def test_modify_with_only_add_labels(self, mock_gmail_service: MagicMock) -> None:
        """Test modifying with only add labels."""
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_modify.execute.return_value = {"id": "msg1", "labelIds": ["STARRED"]}

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import modify_message_labels

            modify_message_labels("msg1", add_labels=["STARRED"])

            call_args = (
                mock_gmail_service.users.return_value.messages.return_value.modify.call_args
            )
            assert "addLabelIds" in call_args.kwargs["body"]
            assert "removeLabelIds" not in call_args.kwargs["body"]

    def test_modify_with_only_remove_labels(self, mock_gmail_service: MagicMock) -> None:
        """Test modifying with only remove labels."""
        mock_modify = MagicMock()
        mock_gmail_service.users.return_value.messages.return_value.modify.return_value = (
            mock_modify
        )
        mock_modify.execute.return_value = {"id": "msg1", "labelIds": []}

        with patch("gmail_cli.services.gmail.get_gmail_service") as mock_get:
            mock_get.return_value = mock_gmail_service

            from gmail_cli.services.gmail import modify_message_labels

            modify_message_labels("msg1", remove_labels=["UNREAD"])

            call_args = (
                mock_gmail_service.users.return_value.messages.return_value.modify.call_args
            )
            assert "removeLabelIds" in call_args.kwargs["body"]
            assert "addLabelIds" not in call_args.kwargs["body"]
