# Tasks: Multi-Account Support

**Input**: Design documents from `/specs/002-multi-account/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-commands.md, quickstart.md

**Tests**: TDD approach per constitution (Principle III). Tests written before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (No Code Changes)

**Purpose**: Verify existing structure supports multi-account changes

- [x] T001 Verify existing test structure in tests/ supports new test files
- [x] T002 Run existing tests to confirm baseline passes: `pytest tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core credential system that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation

- [ ] T003 [P] Unit test for `list_accounts()` in tests/unit/test_credentials.py
- [ ] T004 [P] Unit test for `get_default_account()` in tests/unit/test_credentials.py
- [ ] T005 [P] Unit test for `set_default_account()` in tests/unit/test_credentials.py
- [ ] T006 [P] Unit test for multi-account `save_credentials()` in tests/unit/test_credentials.py
- [ ] T007 [P] Unit test for multi-account `load_credentials()` in tests/unit/test_credentials.py
- [ ] T008 [P] Unit test for `delete_credentials()` with account param in tests/unit/test_credentials.py
- [ ] T009 [P] Unit test for `migrate_legacy_credentials()` in tests/unit/test_credentials.py
- [ ] T010 [P] Unit test for `resolve_account()` priority chain in tests/unit/test_auth_service.py
- [ ] T011 [P] Unit test for `AccountNotFoundError` in tests/unit/test_auth_service.py
- [ ] T012 [P] Unit test for `NoAccountConfiguredError` in tests/unit/test_auth_service.py

### Implementation for Foundation

- [ ] T013 Add keyring key constants `ACCOUNTS_LIST_KEY`, `DEFAULT_ACCOUNT_KEY` in src/gmail_cli/services/credentials.py
- [ ] T014 Add `_get_account_key(email: str) -> str` helper in src/gmail_cli/services/credentials.py
- [ ] T015 Implement `list_accounts() -> list[str]` in src/gmail_cli/services/credentials.py
- [ ] T016 Implement `get_default_account() -> str | None` in src/gmail_cli/services/credentials.py
- [ ] T017 Implement `set_default_account(account: str) -> None` in src/gmail_cli/services/credentials.py
- [ ] T018 Refactor `save_credentials(credentials, account: str)` to use account-specific key in src/gmail_cli/services/credentials.py
- [ ] T019 Refactor `load_credentials(account: str | None = None)` to load from account-specific key in src/gmail_cli/services/credentials.py
- [ ] T020 Refactor `delete_credentials(account: str)` to delete account-specific key in src/gmail_cli/services/credentials.py
- [ ] T021 Implement `migrate_legacy_credentials() -> bool` in src/gmail_cli/services/credentials.py
- [ ] T022 Add `AccountNotFoundError` exception class in src/gmail_cli/services/auth.py
- [ ] T023 Add `NoAccountConfiguredError` exception class in src/gmail_cli/services/auth.py
- [ ] T024 Implement `resolve_account(explicit_account: str | None = None) -> str` in src/gmail_cli/services/auth.py
- [ ] T025 Refactor `get_credentials(account: str | None = None)` to use resolved account in src/gmail_cli/services/auth.py
- [ ] T026 Refactor `get_user_email(account: str | None = None)` to use account param in src/gmail_cli/services/auth.py
- [ ] T027 Add migration call in `get_credentials()` for backward compatibility in src/gmail_cli/services/auth.py
- [ ] T028 Add multi-account test fixtures in tests/conftest.py

**Checkpoint**: Foundation ready - all credential functions work with multiple accounts

---

## Phase 3: User Story 1 - Authenticate Multiple Gmail Accounts (Priority: P1) 🎯 MVP

**Goal**: Users can authenticate multiple Gmail accounts and have the first one set as default

**Independent Test**: Run `gmail auth login` multiple times with different accounts, verify each is stored

### Tests for User Story 1

- [ ] T029 [P] [US1] Integration test for first login sets default in tests/integration/test_auth.py
- [ ] T030 [P] [US1] Integration test for second login adds to list in tests/integration/test_auth.py
- [ ] T031 [P] [US1] Integration test for legacy migration on login in tests/integration/test_auth.py

### Implementation for User Story 1

- [ ] T032 [US1] Update `run_oauth_flow()` to detect account email after auth in src/gmail_cli/services/auth.py
- [ ] T033 [US1] Update `login()` command to save credentials with account email in src/gmail_cli/cli/auth.py
- [ ] T034 [US1] Update `login()` to set first account as default automatically in src/gmail_cli/cli/auth.py
- [ ] T035 [US1] Add `--set-default` flag to `login()` command in src/gmail_cli/cli/auth.py
- [ ] T036 [US1] Update login output to show if account was set as default in src/gmail_cli/cli/auth.py
- [ ] T037 [US1] Update JSON output for login with `is_default` field in src/gmail_cli/cli/auth.py

**Checkpoint**: Users can authenticate multiple accounts. First account is default. Migration works.

---

## Phase 4: User Story 2 - List and Manage Configured Accounts (Priority: P1)

**Goal**: Users can see all accounts, set default, and logout specific accounts

**Independent Test**: Run `gmail auth status` to see all accounts, use `gmail auth set-default` and `gmail auth logout --account`

### Tests for User Story 2

- [ ] T038 [P] [US2] Integration test for `auth status` lists all accounts in tests/integration/test_auth.py
- [ ] T039 [P] [US2] Integration test for `auth set-default` changes default in tests/integration/test_auth.py
- [ ] T040 [P] [US2] Integration test for `auth logout --account` removes specific account in tests/integration/test_auth.py
- [ ] T041 [P] [US2] Integration test for `auth logout --all` removes all accounts in tests/integration/test_auth.py

### Implementation for User Story 2

- [ ] T042 [US2] Refactor `status()` command to show all accounts with default indicator in src/gmail_cli/cli/auth.py
- [ ] T043 [US2] Update `status()` JSON output with accounts array in src/gmail_cli/cli/auth.py
- [ ] T044 [US2] Add `set_default(email: str)` command in src/gmail_cli/cli/auth.py
- [ ] T045 [US2] Refactor `logout_command()` to accept `--account` option in src/gmail_cli/cli/auth.py
- [ ] T046 [US2] Add `--all` flag to `logout_command()` in src/gmail_cli/cli/auth.py
- [ ] T047 [US2] Implement logout logic: specific account removes from list in src/gmail_cli/cli/auth.py
- [ ] T048 [US2] Implement logout logic: default logout uses default account in src/gmail_cli/cli/auth.py
- [ ] T049 [US2] Implement logout logic: handle default reassignment after logout in src/gmail_cli/cli/auth.py
- [ ] T050 [US2] Update logout JSON output with accounts array in src/gmail_cli/cli/auth.py

**Checkpoint**: Full account lifecycle management (add, list, set-default, remove) working

---

## Phase 5: User Story 3 - Use Specific Account for Operations (Priority: P1)

**Goal**: Users can specify `--account` on all email commands to use a specific account

**Independent Test**: Run `gmail search "test" --account work@company.com` and verify correct account is used

### Tests for User Story 3

- [ ] T051 [P] [US3] Unit test for `get_gmail_service(account)` passes correct credentials in tests/unit/test_gmail_service.py
- [ ] T052 [P] [US3] Unit test for API calls use account email as userId in tests/unit/test_gmail_service.py
- [ ] T053 [P] [US3] Integration test for `search --account` uses correct account in tests/integration/test_search.py
- [ ] T054 [P] [US3] Integration test for `read --account` uses correct account in tests/integration/test_read.py
- [ ] T055 [P] [US3] Integration test for `send --account` uses correct account in tests/integration/test_send.py

### Implementation for User Story 3

- [ ] T056 [US3] Refactor `get_gmail_service(account: str | None = None)` in src/gmail_cli/services/gmail.py
- [ ] T057 [US3] Refactor `search_emails()` to accept and pass account param in src/gmail_cli/services/gmail.py
- [ ] T058 [US3] Refactor `get_email_summary()` to accept and pass account param in src/gmail_cli/services/gmail.py
- [ ] T059 [US3] Refactor `get_email()` to accept and pass account param in src/gmail_cli/services/gmail.py
- [ ] T060 [US3] Refactor `get_attachment()` to accept and pass account param in src/gmail_cli/services/gmail.py
- [ ] T061 [US3] Refactor `get_signature()` to accept and pass account param in src/gmail_cli/services/gmail.py
- [ ] T062 [US3] Refactor `send_email()` to accept and pass account param in src/gmail_cli/services/gmail.py
- [ ] T063 [US3] Replace all `userId="me"` with resolved account in src/gmail_cli/services/gmail.py
- [ ] T064 [US3] Define shared `AccountOption` type annotation for CLI commands in src/gmail_cli/cli/auth.py
- [ ] T065 [US3] Add `--account` option to `search` command in src/gmail_cli/cli/search.py
- [ ] T066 [US3] Add `--account` option to `read` command in src/gmail_cli/cli/read.py
- [ ] T067 [US3] Add `--account` option to `send` command in src/gmail_cli/cli/send.py
- [ ] T068 [US3] Add `--account` option to `reply` command in src/gmail_cli/cli/send.py
- [ ] T069 [US3] Add `--account` option to `attachment list` command in src/gmail_cli/cli/attachment.py
- [ ] T070 [US3] Add `--account` option to `attachment download` command in src/gmail_cli/cli/attachment.py
- [ ] T071 [US3] Add account header to output when multi-account mode active in src/gmail_cli/cli/search.py
- [ ] T072 [US3] Update `require_auth` decorator to handle account-specific auth in src/gmail_cli/cli/auth.py

**Checkpoint**: All commands accept --account flag and use correct account for API calls

---

## Phase 6: User Story 4 - Account Resolution with Environment Variable (Priority: P2)

**Goal**: Power users can set GMAIL_ACCOUNT environment variable to override default

**Independent Test**: Set `GMAIL_ACCOUNT=work@company.com` and run `gmail search "test"` without --account flag

### Tests for User Story 4

- [ ] T073 [P] [US4] Unit test for env var takes precedence over default in tests/unit/test_auth_service.py
- [ ] T074 [P] [US4] Unit test for explicit --account takes precedence over env var in tests/unit/test_auth_service.py
- [ ] T075 [P] [US4] Integration test for GMAIL_ACCOUNT env var works in tests/integration/test_search.py

### Implementation for User Story 4

- [ ] T076 [US4] Update `resolve_account()` to check `GMAIL_ACCOUNT` env var in src/gmail_cli/services/auth.py
- [ ] T077 [US4] Add error handling for invalid env var account in src/gmail_cli/services/auth.py

**Checkpoint**: Full account resolution priority chain working (--account > env var > default > first)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and final validation

### Error Handling

- [ ] T078 [P] Implement account not found error with available accounts list in src/gmail_cli/cli/auth.py
- [ ] T079 [P] Implement no account configured error with login hint in src/gmail_cli/cli/auth.py
- [ ] T080 [P] Add JSON error responses for account errors in src/gmail_cli/utils/output.py

### Backward Compatibility

- [ ] T081 Verify all existing tests still pass: `pytest tests/`
- [ ] T082 Verify commands without --account use default (backward compatible)

### Documentation & Cleanup

- [ ] T083 [P] Update help text for all commands with --account option
- [ ] T084 Run `ruff check .` and fix any linting issues
- [ ] T085 Run `ruff format .` to ensure consistent formatting
- [ ] T086 Run quickstart.md verification checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1, US2, US3 are all P1 priority but have logical dependencies:
    - US1 must complete first (provides multi-account auth)
    - US2 depends on US1 (needs accounts to manage)
    - US3 depends on US1 (needs accounts to select)
    - US4 is P2 and builds on US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs multiple accounts to exist for management)
- **User Story 3 (P1)**: Depends on US1 (needs multiple accounts for --account to make sense)
- **User Story 4 (P2)**: Depends on US3 (extends account resolution)

### Within Each Phase

- Tests (T003-T012, etc.) MUST be written and FAIL before implementation
- Foundation implementation (T013-T028) follows test structure
- Models/utilities before services
- Services before CLI commands
- Core implementation before error handling

### Parallel Opportunities

- **Phase 2**: T003-T012 (all foundation tests) can run in parallel
- **Phase 2**: After tests, T013-T014 (constants/helpers) then T015-T021 (credential functions) in sequence
- **Phase 3**: T029-T031 (US1 tests) can run in parallel
- **Phase 4**: T038-T041 (US2 tests) can run in parallel
- **Phase 5**: T051-T055 (US3 tests) can run in parallel; T065-T070 (CLI --account options) can run in parallel
- **Phase 6**: T073-T075 (US4 tests) can run in parallel
- **Phase 7**: T078-T080 (error handling) can run in parallel

---

## Parallel Example: User Story 3 Tests

```bash
# Launch all US3 tests together:
Task: "Unit test for get_gmail_service(account) in tests/unit/test_gmail_service.py"
Task: "Unit test for API calls use account email as userId in tests/unit/test_gmail_service.py"
Task: "Integration test for search --account in tests/integration/test_search.py"
Task: "Integration test for read --account in tests/integration/test_read.py"
Task: "Integration test for send --account in tests/integration/test_send.py"
```

## Parallel Example: User Story 3 CLI Options

```bash
# Launch all --account CLI additions together:
Task: "Add --account option to search command in src/gmail_cli/cli/search.py"
Task: "Add --account option to read command in src/gmail_cli/cli/read.py"
Task: "Add --account option to send command in src/gmail_cli/cli/send.py"
Task: "Add --account option to reply command in src/gmail_cli/cli/send.py"
Task: "Add --account option to attachment list command in src/gmail_cli/cli/attachment.py"
Task: "Add --account option to attachment download command in src/gmail_cli/cli/attachment.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test `gmail auth login` with multiple accounts
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test multi-account auth → Deploy (MVP!)
3. Add User Story 2 → Test account management → Deploy
4. Add User Story 3 → Test --account flag → Deploy
5. Add User Story 4 → Test env var override → Deploy
6. Complete Polish phase → Final release

### Recommended Execution Order

Since US1, US2, US3 are all P1 and have dependencies:

1. **Phase 1 + 2**: Setup + Foundational (T001-T028)
2. **Phase 3**: User Story 1 (T029-T037) - Multi-account auth
3. **Phase 4**: User Story 2 (T038-T050) - Account management
4. **Phase 5**: User Story 3 (T051-T072) - --account flag on commands
5. **Phase 6**: User Story 4 (T073-T077) - Environment variable
6. **Phase 7**: Polish (T078-T086) - Error handling, cleanup

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable (after dependencies met)
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `pytest tests/` after each phase to ensure no regressions
