"""Credentials model for OAuth 2.0 authentication."""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Credentials:
    """OAuth 2.0 credentials for Gmail API access."""

    access_token: str
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: list[str]
    expiry: datetime

    @property
    def is_expired(self) -> bool:
        """Check if access token is expired."""
        return datetime.utcnow() >= self.expiry

    @property
    def needs_refresh(self) -> bool:
        """Check if token expires soon (< 5 min)."""
        return datetime.utcnow() >= (self.expiry - timedelta(minutes=5))
