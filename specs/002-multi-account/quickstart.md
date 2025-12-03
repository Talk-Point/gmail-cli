# Quick Start: Multi-Account Implementation

**Feature**: 002-multi-account
**Date**: 2025-12-02

## Overview

This guide provides the implementation sequence for adding multi-account support to Gmail CLI.

## Implementation Order

### Phase 1: Core Credential System (Foundation)

1. **services/credentials.py** - Multi-account keyring functions
   - `list_accounts() -> list[str]`
   - `get_default_account() -> str | None`
   - `set_default_account(account: str) -> None`
   - `save_credentials(credentials, account: str) -> None`
   - `load_credentials(account: str | None = None) -> Credentials | None`
   - `delete_credentials(account: str) -> None`
   - `migrate_legacy_credentials() -> bool`

2. **services/auth.py** - Account parameter threading
   - Add `account` parameter to `get_credentials()`
   - Add `account` parameter to `get_user_email()`
   - Add `resolve_account()` function
   - Call `migrate_legacy_credentials()` on first access

3. **Unit tests** - Test new credential functions
   - Test multi-account storage/retrieval
   - Test default account management
   - Test legacy migration

### Phase 2: Service Layer (API Integration)

4. **services/gmail.py** - Account parameter on all API calls
   - Update `get_gmail_service(account: str | None = None)`
   - Update `search_emails(..., account: str | None = None)`
   - Update `get_email_summary(..., account: str | None = None)`
   - Update `get_email(..., account: str | None = None)`
   - Update `get_attachment(..., account: str | None = None)`
   - Update `get_signature(account: str | None = None)`
   - Update `send_email(..., account: str | None = None)`
   - Replace hardcoded `userId="me"` with resolved account

5. **Unit tests** - Test account parameter passing
   - Mock API calls verify correct userId
   - Test account resolution integration

### Phase 3: CLI Commands (User Interface)

6. **cli/auth.py** - Enhanced auth commands
   - Update `login()` with `--set-default` option
   - Update `status()` to show all accounts
   - Update `logout()` with `--account` and `--all` options
   - Add `set_default()` command

7. **cli/search.py, cli/read.py, cli/send.py, cli/attachment.py** - Add --account option
   - Add `AccountOption` type annotation
   - Thread account through to service calls
   - Add account header to output (when multi-account)

8. **Integration tests** - Test full command flows
   - Test multi-account login flow
   - Test --account flag on all commands
   - Test environment variable override

## Key Code Patterns

### Shared Account Option

```python
# cli/common.py or top of each CLI file
from typing import Annotated
import typer

AccountOption = Annotated[
    str | None,
    typer.Option(
        "--account", "-a",
        help="Gmail account for this operation (default: configured default)",
    ),
]
```

### Account Resolution

```python
# services/auth.py
import os

class AccountNotFoundError(Exception):
    def __init__(self, account: str, available: list[str]):
        self.account = account
        self.available = available
        super().__init__(f"Account '{account}' not found")

class NoAccountConfiguredError(Exception):
    pass

def resolve_account(explicit_account: str | None = None) -> str:
    """Resolve which account to use with priority chain."""
    from gmail_cli.services.credentials import list_accounts, get_default_account

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
```

### Keyring Storage Pattern

```python
# services/credentials.py
import json
import keyring

SERVICE_NAME = "gmail-cli"
ACCOUNTS_LIST_KEY = "accounts_list"
DEFAULT_ACCOUNT_KEY = "default_account"

def _get_account_key(email: str) -> str:
    """Get keyring key for account credentials."""
    return f"oauth_{email}"

def list_accounts() -> list[str]:
    """List all authenticated accounts."""
    data = keyring.get_password(SERVICE_NAME, ACCOUNTS_LIST_KEY)
    if not data:
        return []
    return json.loads(data)

def save_credentials(credentials: Credentials, account: str) -> None:
    """Save credentials for specific account."""
    # Save credentials
    creds_data = _serialize_credentials(credentials)
    keyring.set_password(SERVICE_NAME, _get_account_key(account), json.dumps(creds_data))

    # Update accounts list
    accounts = list_accounts()
    if account not in accounts:
        accounts.append(account)
        keyring.set_password(SERVICE_NAME, ACCOUNTS_LIST_KEY, json.dumps(accounts))

    # Set default if first account
    if len(accounts) == 1:
        set_default_account(account)
```

## Testing Strategy

### Unit Tests (Mocked)

```python
# tests/unit/test_credentials.py
def test_list_accounts_empty(mock_keyring):
    mock_keyring.get_password.return_value = None
    assert list_accounts() == []

def test_save_credentials_adds_to_list(mock_keyring):
    mock_keyring.get_password.return_value = '[]'
    save_credentials(mock_creds, "test@gmail.com")
    # Verify set_password called with updated list
```

### Integration Tests (CLI)

```python
# tests/integration/test_auth.py
def test_multi_account_status(runner, mock_multi_accounts):
    result = runner.invoke(app, ["auth", "status"])
    assert "user@gmail.com" in result.output
    assert "work@company.com" in result.output
    assert "(default)" in result.output

def test_search_with_account_flag(runner, mock_multi_accounts):
    result = runner.invoke(app, ["search", "test", "--account", "work@company.com"])
    assert result.exit_code == 0
    # Verify correct account was used in API call
```

## Verification Checklist

Before merging, verify:

- [ ] All existing tests pass (backward compatibility)
- [ ] New unit tests for multi-account credentials
- [ ] New integration tests for --account flag
- [ ] `gmail auth status` shows all accounts
- [ ] `gmail auth set-default` works
- [ ] `gmail auth logout --account` removes specific account
- [ ] `gmail auth logout --all` removes all accounts
- [ ] All commands accept --account flag
- [ ] GMAIL_ACCOUNT environment variable works
- [ ] Legacy credential migration works
- [ ] Error messages list available accounts
