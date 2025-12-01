"""Email model for Gmail messages."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gmail_cli.models.attachment import Attachment


@dataclass
class Email:
    """A Gmail message with all relevant metadata."""

    id: str
    thread_id: str
    subject: str
    sender: str
    recipients: list[str]
    date: datetime
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    body_text: str = ""
    body_html: str = ""
    snippet: str = ""
    labels: list[str] = field(default_factory=list)
    attachments: list["Attachment"] = field(default_factory=list)
    is_read: bool = True
    message_id: str = ""
    references: list[str] = field(default_factory=list)

    @property
    def has_attachments(self) -> bool:
        """Check if email has attachments."""
        return len(self.attachments) > 0

    @property
    def sender_name(self) -> str:
        """Extract only the name from the sender."""
        if "<" in self.sender:
            return self.sender.split("<")[0].strip().strip('"')
        return self.sender

    @property
    def sender_email(self) -> str:
        """Extract only the email address from the sender."""
        if "<" in self.sender and ">" in self.sender:
            return self.sender.split("<")[1].split(">")[0]
        return self.sender
