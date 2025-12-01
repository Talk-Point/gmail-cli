"""Attachment model for Gmail attachments."""

from dataclasses import dataclass


@dataclass
class Attachment:
    """An attachment of a Gmail message."""

    id: str
    message_id: str
    filename: str
    mime_type: str
    size: int

    @property
    def size_human(self) -> str:
        """Human-readable size."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        else:
            return f"{self.size / (1024 * 1024):.1f} MB"
