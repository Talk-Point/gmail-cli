# Data Model: Multi-Account Support

**Feature**: 002-multi-account
**Date**: 2025-12-02

## Entities

### AccountCredentials

Represents OAuth2 credentials for a single Gmail account.

| Field | Type | Description |
|-------|------|-------------|
| email | str | Gmail account email address (unique identifier) |
| token | str | Current OAuth2 access token |
| refresh_token | str | OAuth2 refresh token for token renewal |
| token_uri | str | Google's token endpoint URL |
| client_id | str | OAuth2 client ID |
| client_secret | str | OAuth2 client secret |
| scopes | list[str] | Authorized OAuth2 scopes |
| expiry | datetime \| None | Access token expiration time |

**Storage**: System keyring under key `gmail-cli/oauth_{email}`

**Validation Rules**:
- `email` must be valid email format
- `refresh_token` required for token refresh capability
- `scopes` must include gmail.readonly at minimum

### AccountsRegistry

Manages the list of authenticated accounts and default selection.

| Field | Type | Description |
|-------|------|-------------|
| accounts | list[str] | List of authenticated account email addresses |
| default_account | str \| None | Email of the default account |

**Storage**:
- Accounts list: System keyring under key `gmail-cli/accounts_list` (JSON array)
- Default account: System keyring under key `gmail-cli/default_account` (plain string)

**Validation Rules**:
- `default_account` must exist in `accounts` list
- `accounts` list contains unique email addresses
- Empty list is valid (no accounts configured)

## State Transitions

### Account Lifecycle

```
[Not Configured] ──login──> [Authenticated] ──logout──> [Not Configured]
                                   │
                                   │──set-default──> [Default]
                                   │
                                   │──token expired──> [Refresh Needed]
                                   │                        │
                                   │<──auto refresh ok──────┘
                                   │
                                   │<──refresh failed: re-login required
```

### Default Account Selection

```
[No Default] ──first login──> [Default = first account]
     │
     │──set-default <email>──> [Default = specified]
     │
     │──logout default──> [Default = next available OR No Default]
```

## Keyring Schema

```
gmail-cli/
├── accounts_list        → '["user@gmail.com", "work@company.com"]'
├── default_account      → 'user@gmail.com'
├── oauth_user@gmail.com → '{"token": "...", "refresh_token": "...", ...}'
└── oauth_work@company.com → '{"token": "...", "refresh_token": "...", ...}'
```

### Legacy Schema (Pre-Migration)

```
gmail-cli/
└── oauth_credentials    → '{"token": "...", "refresh_token": "...", ...}'
```

Migration converts legacy to new schema automatically on first access.

## Error States

### AccountNotFoundError

Raised when specified account is not in the accounts registry.

```python
class AccountNotFoundError(Exception):
    account: str           # The requested account
    available: list[str]   # Available accounts for user reference
```

### NoAccountConfiguredError

Raised when no accounts are authenticated and operation requires one.

```python
class NoAccountConfiguredError(Exception):
    pass  # Simple error, message provides guidance
```

### CredentialRefreshError

Raised when token refresh fails and re-authentication is needed.

```python
class CredentialRefreshError(Exception):
    account: str  # The account that needs re-authentication
```

## Relationships

```
┌─────────────────┐
│ AccountsRegistry│
│                 │
│ accounts[]──────┼───────┐
│ default_account─┼──┐    │
└─────────────────┘  │    │
                     │    │ 1..n
                     │    ▼
                     │  ┌─────────────────────┐
                     └─>│ AccountCredentials  │
                        │                     │
                        │ email (PK)          │
                        │ token               │
                        │ refresh_token       │
                        │ ...                 │
                        └─────────────────────┘
```

## Data Volume Assumptions

- Typical user: 1-3 accounts
- Maximum practical: ~10 accounts (no enforced limit)
- Credential payload size: ~1KB per account
- Total keyring usage: <20KB for typical scenarios
