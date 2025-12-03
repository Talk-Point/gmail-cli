# CLI Command Contracts: Multi-Account Support

**Feature**: 002-multi-account
**Date**: 2025-12-02

## Auth Commands

### gmail auth login

Authenticate a new Gmail account.

```
gmail auth login [--set-default]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| --set-default | flag | false | Set this account as default after login |

**Output (success)**:
```
✓ Authenticated as user@gmail.com
✓ Set as default account
```

**JSON Output**:
```json
{
  "status": "authenticated",
  "email": "user@gmail.com",
  "is_default": true,
  "scopes": ["gmail.readonly", "gmail.send", "gmail.settings.basic"]
}
```

**Exit Codes**:
- 0: Success
- 1: Authentication failed
- 2: credentials.json not found

---

### gmail auth logout

Remove account credentials.

```
gmail auth logout [--account EMAIL] [--all]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| --account, -a | str | None | Specific account to logout (default: logout default account) |
| --all | flag | false | Logout all accounts |

**Mutual Exclusion**: `--account` and `--all` cannot be used together.

**Output (success)**:
```
✓ Logged out: user@gmail.com
```

**JSON Output**:
```json
{
  "status": "logged_out",
  "accounts": ["user@gmail.com"]
}
```

**Exit Codes**:
- 0: Success
- 1: Account not found

---

### gmail auth status

Show authentication status for all accounts.

```
gmail auth status
```

**Output (authenticated)**:
```
Authenticated accounts:
  ★ user@gmail.com (default)
    work@company.com

Token status: All tokens valid
```

**Output (not authenticated)**:
```
✗ No accounts configured
  Run 'gmail auth login' to authenticate.
```

**JSON Output**:
```json
{
  "authenticated": true,
  "accounts": [
    {
      "email": "user@gmail.com",
      "is_default": true,
      "token_valid": true,
      "token_expiry": "2025-12-02T15:30:00"
    },
    {
      "email": "work@company.com",
      "is_default": false,
      "token_valid": true,
      "token_expiry": "2025-12-02T16:00:00"
    }
  ]
}
```

**Exit Codes**:
- 0: At least one account authenticated
- 1: No accounts configured

---

### gmail auth set-default

Set the default account.

```
gmail auth set-default EMAIL
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| EMAIL | str | yes | Email address to set as default |

**Output (success)**:
```
✓ Default account: user@gmail.com
```

**JSON Output**:
```json
{
  "status": "default_set",
  "email": "user@gmail.com"
}
```

**Exit Codes**:
- 0: Success
- 1: Account not found

---

## Email Operation Commands

All email operation commands gain the `--account` option.

### Common Account Option

```
--account, -a EMAIL    Gmail account for this operation (default: configured default)
```

### gmail search

```
gmail search QUERY [--account EMAIL] [existing options...]
```

**Account Resolution**: Uses specified account or resolved default.

**Output Header** (when multiple accounts exist):
```
Searching in: user@gmail.com
─────────────────────────────
[search results...]
```

---

### gmail read

```
gmail read MESSAGE_ID [--account EMAIL] [existing options...]
```

**Account Resolution**: Uses specified account or resolved default.

**Error (message not found in account)**:
```
✗ Message not found in account 'user@gmail.com'
  Try specifying a different account with --account
```

---

### gmail send

```
gmail send [--account EMAIL] [existing options...]
```

**Account Resolution**: Uses specified account or resolved default.

**Output Header**:
```
Sending from: work@company.com
```

---

### gmail reply

```
gmail reply MESSAGE_ID [--account EMAIL] [existing options...]
```

**Account Resolution**: Uses specified account or resolved default.

---

### gmail attachment list

```
gmail attachment list MESSAGE_ID [--account EMAIL]
```

**Account Resolution**: Uses specified account or resolved default.

---

### gmail attachment download

```
gmail attachment download MESSAGE_ID ATTACHMENT_ID [--account EMAIL] [existing options...]
```

**Account Resolution**: Uses specified account or resolved default.

---

## Error Responses

### Account Not Found

```
✗ Account 'unknown@example.com' not found.
  Available accounts:
    - user@gmail.com
    - work@company.com

  To add a new account: gmail auth login
```

**JSON**:
```json
{
  "error": "ACCOUNT_NOT_FOUND",
  "message": "Account 'unknown@example.com' not found",
  "available_accounts": ["user@gmail.com", "work@company.com"]
}
```

### No Account Configured

```
✗ No accounts configured
  Run 'gmail auth login' to authenticate.
```

**JSON**:
```json
{
  "error": "NO_ACCOUNT_CONFIGURED",
  "message": "No accounts configured",
  "hint": "Run 'gmail auth login' to authenticate"
}
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| GMAIL_ACCOUNT | Override default account for all commands (lower priority than --account flag) |
