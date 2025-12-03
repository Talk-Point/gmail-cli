# Research: Multi-Account Support

**Feature**: 002-multi-account
**Date**: 2025-12-02

## 1. Keyring Multi-Key Storage Pattern

**Decision**: Use account-prefixed keyring keys for credential isolation

**Rationale**: The `keyring` library supports storing multiple passwords under the same service name with different account names. This maps directly to our multi-account requirement.

**Implementation**:
```python
# Current (single account)
keyring.set_password("gmail-cli", "oauth_credentials", json_data)

# New (multi-account)
keyring.set_password("gmail-cli", f"oauth_{email}", json_data)       # Per-account credentials
keyring.set_password("gmail-cli", "accounts_list", json_list)        # Account registry
keyring.set_password("gmail-cli", "default_account", email)          # Default selection
```

**Alternatives Considered**:
- File-based storage: Rejected (security concerns, not OS-integrated)
- Encrypted SQLite: Rejected (adds complexity, keyring already secure)
- Single JSON blob with all accounts: Rejected (harder to manage, larger atomic writes)

## 2. Gmail API userId Parameter

**Decision**: Use email address as `userId` instead of `"me"` for explicit account targeting

**Rationale**: The Gmail API accepts both `"me"` (authenticated user) and the actual email address. Using email ensures correct account targeting when credentials exist for multiple accounts.

**Implementation**:
```python
# Current
service.users().messages().list(userId="me", ...)

# New
user_id = account or "me"  # account is resolved email address
service.users().messages().list(userId=user_id, ...)
```

**Alternatives Considered**:
- Always use "me" and switch credentials: Works but less explicit
- Pass email directly: Chosen for clarity and debugging

## 3. Account Resolution Priority

**Decision**: Explicit flag > Environment variable > Default account > First available

**Rationale**: This priority order provides maximum flexibility while maintaining predictable behavior. The explicit `--account` flag always wins, environment variables enable scripting, and defaults provide convenience.

**Implementation**:
```python
def resolve_account(explicit_account: str | None = None) -> str:
    # 1. Explicit --account flag
    if explicit_account:
        if explicit_account not in list_accounts():
            raise AccountNotFoundError(explicit_account, list_accounts())
        return explicit_account

    # 2. Environment variable
    env_account = os.environ.get("GMAIL_ACCOUNT")
    if env_account:
        if env_account not in list_accounts():
            raise AccountNotFoundError(env_account, list_accounts())
        return env_account

    # 3. Configured default
    default = get_default_account()
    if default:
        return default

    # 4. First available
    accounts = list_accounts()
    if accounts:
        return accounts[0]

    raise NoAccountConfiguredError()
```

**Alternatives Considered**:
- Only --account flag: Too inconvenient for regular use
- Only environment variable: Breaks interactive usage
- Config file for active account: Adds state complexity

## 4. Legacy Credential Migration

**Decision**: Automatic one-time migration on first access

**Rationale**: Existing users should not need to re-authenticate. Migration happens transparently when any command accesses credentials.

**Implementation**:
```python
def migrate_legacy_credentials() -> bool:
    """Migrate single-account credentials to multi-account format.

    Returns True if migration occurred, False if already migrated or no legacy creds.
    """
    # Check for old format
    old_creds = keyring.get_password("gmail-cli", "oauth_credentials")
    if not old_creds:
        return False

    # Check if already migrated (accounts_list exists)
    if keyring.get_password("gmail-cli", "accounts_list"):
        # Clean up legacy key if still present
        keyring.delete_password("gmail-cli", "oauth_credentials")
        return False

    # Load and determine email
    credentials = _parse_credentials(old_creds)
    email = _get_email_from_credentials(credentials)

    # Save in new format
    save_credentials(credentials, account=email)
    set_default_account(email)

    # Remove old key
    keyring.delete_password("gmail-cli", "oauth_credentials")

    return True
```

**Alternatives Considered**:
- Manual migration command: Poor UX, users might not know
- Keep both formats: Complexity in credential loading
- Force re-authentication: Bad UX for existing users

## 5. CLI Parameter Pattern

**Decision**: Add `--account`/`-a` option to all email operation commands via shared type annotation

**Rationale**: Consistent parameter definition across all commands reduces code duplication and ensures uniform behavior.

**Implementation**:
```python
# Shared type definition
AccountOption = Annotated[
    str | None,
    typer.Option(
        "--account", "-a",
        help="Gmail account for this operation (default: configured default)",
    ),
]

# Usage in commands
@search_app.command()
def search(
    query: str,
    account: AccountOption = None,
    # ... other params
) -> None:
    resolved_account = resolve_account(account)
    results = search_emails(query, account=resolved_account)
```

**Alternatives Considered**:
- Global option on app level: Typer doesn't support this well
- Context object: More complex, overkill for single parameter

## 6. Error Message Format

**Decision**: Display available accounts when specified account is not found

**Rationale**: Helps users understand which accounts are configured and what options they have.

**Implementation**:
```
✗ Account 'unknown@example.com' not found.
  Available accounts:
    - user@gmail.com
    - work@company.com

  To add a new account: gmail auth login
```

**Alternatives Considered**:
- Simple "not found" error: Less helpful
- Interactive selection: Out of scope for MVP

## 7. Auth Status Output Enhancement

**Decision**: Show all accounts with default indicator in status output

**Rationale**: Users need visibility into all configured accounts and which is default.

**Implementation**:
```
Authenticated accounts:
  ★ user@gmail.com (default)
    work@company.com
    personal@gmail.com

Token status: All tokens valid
```

JSON output:
```json
{
  "accounts": [
    {"email": "user@gmail.com", "is_default": true, "token_valid": true},
    {"email": "work@company.com", "is_default": false, "token_valid": true}
  ]
}
```

**Alternatives Considered**:
- Only show current/default: Less useful for management
- Separate list command: Redundant, status should show everything

## 8. Logout Behavior

**Decision**: `gmail auth logout` without flags logs out default account; `--account` for specific; `--all` for all

**Rationale**: Default behavior mirrors single-account experience. Explicit flags for other scenarios.

**Implementation**:
```python
@auth_app.command("logout")
def logout_command(
    account: AccountOption = None,
    all_accounts: Annotated[bool, typer.Option("--all")] = False,
) -> None:
    if all_accounts:
        for acc in list_accounts():
            delete_credentials(acc)
        clear_accounts_list()
        clear_default_account()
    elif account:
        delete_credentials(account)
        remove_from_accounts_list(account)
        if get_default_account() == account:
            set_new_default_if_available()
    else:
        # Logout default
        default = get_default_account()
        if default:
            delete_credentials(default)
            remove_from_accounts_list(default)
            set_new_default_if_available()
```

**Alternatives Considered**:
- Logout all by default: Disruptive
- Require explicit --account always: Bad UX
- Interactive selection: Out of scope

## Summary

All research items resolved. No NEEDS CLARIFICATION items remain. Ready for Phase 1 design.
