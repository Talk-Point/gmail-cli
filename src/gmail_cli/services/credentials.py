"""Keyring storage service for OAuth credentials."""

import json
from datetime import datetime

import keyring
from google.oauth2.credentials import Credentials

SERVICE_NAME = "gmail-cli"
ACCOUNT_NAME = "oauth_credentials"


def save_credentials(credentials: Credentials) -> None:
    """Save OAuth credentials to system keyring.

    Args:
        credentials: Google OAuth credentials to store.
    """
    creds_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes) if credentials.scopes else [],
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }
    keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, json.dumps(creds_data))


def load_credentials() -> Credentials | None:
    """Load OAuth credentials from system keyring.

    Returns:
        Credentials object if found, None otherwise.
    """
    creds_json = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
    if not creds_json:
        return None

    try:
        creds_data = json.loads(creds_json)
        expiry = None
        if creds_data.get("expiry"):
            expiry = datetime.fromisoformat(creds_data["expiry"])

        return Credentials(
            token=creds_data["token"],
            refresh_token=creds_data["refresh_token"],
            token_uri=creds_data["token_uri"],
            client_id=creds_data["client_id"],
            client_secret=creds_data["client_secret"],
            scopes=creds_data.get("scopes", []),
            expiry=expiry,
        )
    except (json.JSONDecodeError, KeyError):
        return None


def delete_credentials() -> None:
    """Delete OAuth credentials from system keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
    except keyring.errors.PasswordDeleteError:
        # Credentials don't exist, that's fine
        pass


def has_credentials() -> bool:
    """Check if credentials exist in keyring.

    Returns:
        True if credentials exist, False otherwise.
    """
    return keyring.get_password(SERVICE_NAME, ACCOUNT_NAME) is not None
