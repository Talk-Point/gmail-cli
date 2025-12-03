"""OAuth flow service for Gmail authentication with multi-account support."""

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from gmail_cli.services.credentials import (
    clear_all_accounts,
    delete_credentials,
    get_default_account,
    list_accounts,
    load_credentials,
    migrate_legacy_credentials,
    save_credentials,
)

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.settings.basic",
]


class AccountNotFoundError(Exception):
    """Raised when a specified account is not found in the accounts list."""

    def __init__(self, account: str, available: list[str]) -> None:
        self.account = account
        self.available = available
        super().__init__(f"Account '{account}' not found")


class NoAccountConfiguredError(Exception):
    """Raised when no accounts are configured and an operation requires one."""

    pass


def resolve_account(explicit_account: str | None = None) -> str:
    """Resolve which account to use with priority chain.

    Priority order:
    1. Explicit --account flag
    2. GMAIL_ACCOUNT environment variable
    3. Configured default account
    4. First available account

    Args:
        explicit_account: Account explicitly specified via --account flag.

    Returns:
        Resolved account email address.

    Raises:
        AccountNotFoundError: If specified account doesn't exist.
        NoAccountConfiguredError: If no accounts are configured.
    """
    accounts = list_accounts()

    # Priority 1: Explicit --account flag
    if explicit_account:
        if explicit_account not in accounts:
            raise AccountNotFoundError(explicit_account, accounts)
        return explicit_account

    # Priority 2: Environment variable
    env_account = os.environ.get("GMAIL_ACCOUNT")
    if env_account:
        if env_account not in accounts:
            raise AccountNotFoundError(env_account, accounts)
        return env_account

    # Priority 3: Configured default
    default = get_default_account()
    if default and default in accounts:
        return default

    # Priority 4: First available
    if accounts:
        return accounts[0]

    raise NoAccountConfiguredError()


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


def run_oauth_flow() -> tuple[Credentials, str]:
    """Run the OAuth 2.0 authorization flow.

    Opens a browser for the user to authenticate and authorize the application.

    Returns:
        Tuple of (authorized credentials, email address).
    """
    credentials_file = get_credentials_file()
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)

    # Run local server for OAuth callback (port=0 auto-selects free port)
    credentials = flow.run_local_server(
        port=0,
        prompt="consent",
        success_message="Authentication successful! You can close this window.",
    )

    # Get email address for the authenticated user
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()
    email = profile.get("emailAddress", "")

    # Save credentials with account email
    save_credentials(credentials, account=email)

    return credentials, email


def get_credentials(account: str | None = None) -> Credentials | None:
    """Get valid credentials for an account, refreshing if necessary.

    Args:
        account: Account email to get credentials for. If None, resolves account.

    Returns:
        Valid credentials or None if not authenticated.
    """
    # Try migration first for backward compatibility
    migrate_legacy_credentials()

    # Resolve account if not specified
    if account is None:
        try:
            account = resolve_account()
        except (AccountNotFoundError, NoAccountConfiguredError):
            return None

    credentials = load_credentials(account=account)

    if not credentials:
        return None

    # Check if credentials need refresh
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_credentials(credentials, account=account)
        except Exception:
            # Refresh failed, need to re-authenticate
            delete_credentials(account=account)
            return None

    return credentials


def is_authenticated(account: str | None = None) -> bool:
    """Check if user is authenticated.

    Args:
        account: Account to check. If None, checks if any account is authenticated.

    Returns:
        True if valid credentials exist, False otherwise.
    """
    if account:
        credentials = get_credentials(account=account)
        return credentials is not None and credentials.valid

    # Check if any account is authenticated
    accounts = list_accounts()
    if not accounts:
        return False

    # Check first available account
    credentials = get_credentials(account=accounts[0])
    return credentials is not None and credentials.valid


def refresh_credentials(account: str | None = None) -> bool:
    """Refresh the OAuth credentials.

    Args:
        account: Account to refresh. If None, refreshes default.

    Returns:
        True if refresh successful, False otherwise.
    """
    if account is None:
        try:
            account = resolve_account()
        except (AccountNotFoundError, NoAccountConfiguredError):
            return False

    credentials = load_credentials(account=account)

    if not credentials or not credentials.refresh_token:
        return False

    try:
        credentials.refresh(Request())
        save_credentials(credentials, account=account)
        return True
    except Exception:
        return False


def get_user_email(account: str | None = None) -> str | None:
    """Get the email address of the authenticated user.

    Args:
        account: Account to get email for. If None, uses resolved account.

    Returns:
        Email address or None if not authenticated.
    """
    if account:
        # If account is specified, that IS the email
        return account

    # Resolve and return the default/first account
    try:
        return resolve_account()
    except (AccountNotFoundError, NoAccountConfiguredError):
        return None


def get_token_expiry(account: str | None = None) -> str | None:
    """Get the expiry time of the current access token.

    Args:
        account: Account to check. If None, uses resolved account.

    Returns:
        Formatted expiry time or None if not authenticated.
    """
    if account is None:
        try:
            account = resolve_account()
        except (AccountNotFoundError, NoAccountConfiguredError):
            return None

    credentials = load_credentials(account=account)
    if not credentials or not credentials.expiry:
        return None

    return credentials.expiry.strftime("%Y-%m-%d %H:%M:%S")


def logout(account: str | None = None, all_accounts: bool = False) -> list[str]:
    """Log out by deleting stored credentials.

    Args:
        account: Specific account to log out. If None, logs out default.
        all_accounts: If True, logs out all accounts.

    Returns:
        List of logged out account emails.
    """
    if all_accounts:
        accounts = list_accounts()
        clear_all_accounts()
        return accounts

    if account:
        delete_credentials(account=account)
        return [account]

    # Logout default account
    try:
        default = resolve_account()
        delete_credentials(account=default)
        return [default]
    except (AccountNotFoundError, NoAccountConfiguredError):
        return []
