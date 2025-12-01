"""OAuth flow service for Gmail authentication."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from gmail_cli.services.credentials import (
    delete_credentials,
    load_credentials,
    save_credentials,
)

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.settings.basic",
]


def get_credentials_file() -> Path:
    """Get path to credentials.json file.

    Returns:
        Path to the credentials file.
    """
    # First check current directory
    local_path = Path("credentials.json")
    if local_path.exists():
        return local_path

    # Then check package directory
    package_path = Path(__file__).parent.parent.parent.parent / "credentials.json"
    if package_path.exists():
        return package_path

    raise FileNotFoundError(
        "credentials.json not found. Please ensure the OAuth credentials file exists."
    )


def run_oauth_flow() -> Credentials:
    """Run the OAuth 2.0 authorization flow.

    Opens a browser for the user to authenticate and authorize the application.

    Returns:
        Authorized credentials.
    """
    credentials_file = get_credentials_file()
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)

    # Run local server for OAuth callback
    credentials = flow.run_local_server(
        port=8080,
        prompt="consent",
        success_message="Authentication successful! You can close this window.",
    )

    # Save credentials to keyring
    save_credentials(credentials)

    return credentials


def get_credentials() -> Credentials | None:
    """Get valid credentials, refreshing if necessary.

    Returns:
        Valid credentials or None if not authenticated.
    """
    credentials = load_credentials()

    if not credentials:
        return None

    # Check if credentials need refresh
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_credentials(credentials)
        except Exception:
            # Refresh failed, need to re-authenticate
            delete_credentials()
            return None

    return credentials


def is_authenticated() -> bool:
    """Check if user is authenticated.

    Returns:
        True if valid credentials exist, False otherwise.
    """
    credentials = get_credentials()
    return credentials is not None and credentials.valid


def refresh_credentials() -> bool:
    """Refresh the OAuth credentials.

    Returns:
        True if refresh successful, False otherwise.
    """
    credentials = load_credentials()

    if not credentials or not credentials.refresh_token:
        return False

    try:
        credentials.refresh(Request())
        save_credentials(credentials)
        return True
    except Exception:
        return False


def get_user_email() -> str | None:
    """Get the email address of the authenticated user.

    Returns:
        Email address or None if not authenticated.
    """
    from googleapiclient.discovery import build

    credentials = get_credentials()
    if not credentials:
        return None

    try:
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress")
    except Exception:
        return None


def get_token_expiry() -> str | None:
    """Get the expiry time of the current access token.

    Returns:
        Formatted expiry time or None if not authenticated.
    """
    credentials = load_credentials()
    if not credentials or not credentials.expiry:
        return None

    return credentials.expiry.strftime("%Y-%m-%d %H:%M:%S")


def logout() -> None:
    """Log out by deleting stored credentials."""
    delete_credentials()
