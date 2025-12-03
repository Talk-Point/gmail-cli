# Feature Specification: Multi-Account Support for Gmail CLI

**Feature Branch**: `002-multi-account`
**Created**: 2025-12-02
**Status**: Draft
**Input**: User description: "Multi-Account-Fähigkeit für Gmail CLI basierend auf Studie docs/studies/multi-account-capability-study.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticate Multiple Gmail Accounts (Priority: P1)

As a user with multiple Gmail accounts (personal and work), I want to authenticate each account separately so that I can access emails from all my accounts through the CLI.

**Why this priority**: This is the foundational capability - without multi-account authentication, no other multi-account features can work.

**Independent Test**: Can be fully tested by running `gmail auth login` multiple times with different Google accounts and verifying each is stored and accessible.

**Acceptance Scenarios**:

1. **Given** a user with no accounts configured, **When** they run `gmail auth login`, **Then** the OAuth flow completes and the account is stored as the default account
2. **Given** a user with one account configured, **When** they run `gmail auth login` with a different Google account, **Then** the new account is added to the stored accounts list
3. **Given** a user with legacy single-account credentials, **When** they upgrade and run any command, **Then** their existing credentials are automatically migrated to the new multi-account format

---

### User Story 2 - List and Manage Configured Accounts (Priority: P1)

As a user with multiple accounts configured, I want to see all my authenticated accounts and manage which one is the default so that I know which accounts are available and can control my workflow.

**Why this priority**: Essential for account management and user awareness of configured accounts.

**Independent Test**: Can be tested by configuring multiple accounts and running `gmail auth status` to verify all accounts are listed with default indicator.

**Acceptance Scenarios**:

1. **Given** a user with multiple accounts configured, **When** they run `gmail auth status`, **Then** they see a list of all authenticated accounts with the default account clearly marked
2. **Given** a user with multiple accounts, **When** they run `gmail auth set-default <email>`, **Then** that account becomes the new default account
3. **Given** a user with multiple accounts, **When** they run `gmail auth logout --account <email>`, **Then** only that specific account is removed from storage
4. **Given** a user with multiple accounts, **When** they run `gmail auth logout --all`, **Then** all accounts are removed from storage

---

### User Story 3 - Use Specific Account for Operations (Priority: P1)

As a user with multiple accounts, I want to specify which account to use for any email operation so that I can read, search, and send emails from the correct account.

**Why this priority**: Core functionality that enables the primary use case of working with multiple accounts.

**Independent Test**: Can be tested by running `gmail search "test" --account user@gmail.com` and verifying results come from the specified account.

**Acceptance Scenarios**:

1. **Given** a user with multiple accounts, **When** they run `gmail search "query" --account work@company.com`, **Then** the search is performed on the specified work account
2. **Given** a user with multiple accounts, **When** they run `gmail read <msg-id> --account user@gmail.com`, **Then** the email is retrieved from the specified account
3. **Given** a user with multiple accounts, **When** they run `gmail send --to recipient@example.com --account work@company.com`, **Then** the email is sent from the specified work account
4. **Given** a user with multiple accounts and a default set, **When** they run any command without `--account`, **Then** the default account is used

---

### User Story 4 - Account Resolution with Environment Variable (Priority: P2)

As a power user or script author, I want to set an account via environment variable so that I can control account selection without modifying command arguments.

**Why this priority**: Enhances scripting capabilities but is not essential for basic multi-account usage.

**Independent Test**: Can be tested by setting `GMAIL_ACCOUNT=work@company.com` and running `gmail search "test"` without --account flag.

**Acceptance Scenarios**:

1. **Given** `GMAIL_ACCOUNT` environment variable is set, **When** a user runs a command without `--account`, **Then** the environment variable account is used instead of the default
2. **Given** both `--account` flag and `GMAIL_ACCOUNT` are specified, **When** a user runs a command, **Then** the explicit `--account` flag takes precedence

---

### Edge Cases

- What happens when a user specifies a non-existent account with `--account`?
  - System shows clear error message listing available accounts and suggesting `gmail auth login`
- What happens when all accounts are logged out and user runs a command?
  - System shows error message prompting to authenticate first
- What happens when token for an account expires?
  - System automatically refreshes the token; if refresh fails, prompts user to re-authenticate
- What happens when the default account is logged out?
  - System selects the next available account as default, or shows message if no accounts remain
- What happens during migration when old credentials exist?
  - System detects legacy credentials, migrates them to new format, and sets as default

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support storing credentials for multiple Gmail accounts in the system keyring
- **FR-002**: System MUST maintain a list of all authenticated accounts
- **FR-003**: System MUST allow designating one account as the default
- **FR-004**: System MUST provide an `--account` (or `-a`) option on all email operation commands (search, read, send, reply, attachment list, attachment download)
- **FR-005**: System MUST resolve the target account using this priority: explicit `--account` flag > `GMAIL_ACCOUNT` environment variable > configured default > first available account
- **FR-006**: System MUST provide `gmail auth status` command showing all authenticated accounts with default indicator
- **FR-007**: System MUST provide `gmail auth set-default <email>` command to change the default account
- **FR-008**: System MUST provide `gmail auth logout` with optional `--account` to remove specific account or `--all` to remove all accounts
- **FR-009**: System MUST automatically migrate existing single-account credentials to multi-account format on first use
- **FR-010**: System MUST display clear error messages when specified account is not authenticated, listing available accounts
- **FR-011**: System MUST remain backward-compatible: existing commands without `--account` continue to work using the default account

### Key Entities

- **Account**: Represents an authenticated Gmail account, identified by email address, with associated OAuth credentials (token, refresh token, expiry)
- **Accounts List**: Collection of all authenticated account email addresses
- **Default Account**: The currently selected default account email address
- **Credentials**: OAuth2 credentials including access token, refresh token, and metadata for a specific account

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can authenticate and use 2 or more Gmail accounts within the same CLI installation
- **SC-002**: Users can switch between accounts in under 3 seconds (time to specify --account and execute command)
- **SC-003**: 100% of existing single-account workflows continue to work without modification (backward compatibility)
- **SC-004**: Account resolution follows documented priority order in all scenarios
- **SC-005**: All commands display which account is being used when operating in multi-account mode
- **SC-006**: Users can complete full account lifecycle (add, list, set-default, remove) with clear feedback at each step

## Assumptions

- Users have valid Google accounts with Gmail access
- System keyring is available and accessible on the user's operating system
- OAuth2 refresh tokens remain valid for extended periods (Google's standard token lifetime)
- The Gmail API accepts email address as userId parameter for authenticated user's own account
- Environment variable name `GMAIL_ACCOUNT` is appropriate (not conflicting with other tools)

## Out of Scope

- Google Workspace delegation (accessing other users' mailboxes)
- Account-specific configuration/settings beyond credentials
- Account aliases or nicknames
- Automatic account detection when reading/replying to messages
- Searching across multiple accounts in a single query
- Maximum account limit enforcement
