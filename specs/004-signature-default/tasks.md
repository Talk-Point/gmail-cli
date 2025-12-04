# Tasks: Signature Default Behavior Change

**Input**: Design documents from `/specs/004-signature-default/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: TDD approach - tests written before implementation per Constitution Principle III.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed - this feature modifies existing code

This feature requires no new project setup. The codebase already has:
- typer CLI framework configured
- pytest testing infrastructure
- signature handling code (`get_signature()`)

**Checkpoint**: Setup complete (nothing to do)

---

## Phase 2: Foundational

**Purpose**: No foundational changes needed

This feature modifies existing CLI command behavior only. No new infrastructure required.

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Default Signature Inclusion (Priority: P1) 🎯 MVP

**Goal**: Change default behavior to include signature automatically when no flag is specified

**Independent Test**: Send email without any signature flags → signature is appended

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T001 [P] [US1] Add test `test_send_default_includes_signature` in tests/integration/test_send.py
- [x] T002 [P] [US1] Add test `test_reply_default_includes_signature` in tests/integration/test_send.py
- [x] T003 [P] [US1] Add test `test_send_no_signature_when_none_configured` in tests/integration/test_send.py

### Implementation for User Story 1

- [x] T004 [US1] Change signature parameter in `send_command()` to use `--signature/--no-signature` flag pair with default `True` in src/gmail_cli/cli/send.py
- [x] T005 [US1] Change signature parameter in `reply_command()` to use `--signature/--no-signature` flag pair with default `True` in src/gmail_cli/cli/send.py
- [x] T006 [US1] Update docstrings for both commands to reflect new default behavior in src/gmail_cli/cli/send.py

**Checkpoint**: User Story 1 complete - default behavior now includes signature ✅

---

## Phase 4: User Story 2 - Opt-Out with No-Signature Flag (Priority: P1)

**Goal**: Users can explicitly exclude signature using `--no-signature` flag

**Independent Test**: Send email with `--no-signature` → no signature appended

### Tests for User Story 2

> **NOTE: Tests should pass after US1 implementation (flag pair already exists)**

- [x] T007 [P] [US2] Add test `test_send_no_signature_excludes_signature` in tests/integration/test_send.py
- [x] T008 [P] [US2] Add test `test_reply_no_signature_excludes_signature` in tests/integration/test_send.py

### Implementation for User Story 2

> **NOTE**: The `--no-signature` flag is implemented as part of US1 (typer's flag pair pattern). No additional implementation needed - just verify tests pass.

- [x] T009 [US2] Verify `--no-signature` flag works correctly for send command (run tests)
- [x] T010 [US2] Verify `--no-sig` shorthand works correctly for send command (run tests)

**Checkpoint**: User Story 2 complete - opt-out flag works ✅

---

## Phase 5: User Story 3 - Backwards Compatibility (Priority: P2)

**Goal**: Existing `--signature` flag continues to work (now redundant but functional)

**Independent Test**: Send email with `--signature` flag → signature appended (same as default)

### Tests for User Story 3

- [x] T011 [P] [US3] Update existing test `test_send_with_signature` to verify it still works in tests/integration/test_send.py
- [x] T012 [P] [US3] Add test `test_send_with_sig_shorthand` to verify `--sig` works in tests/integration/test_send.py

### Implementation for User Story 3

> **NOTE**: Backwards compatibility is automatically provided by typer's flag pair pattern. The `--signature` flag sets the boolean to `True` (same as default).

- [x] T013 [US3] Verify `--signature` flag works (should be no-op, same as default) (run tests)
- [x] T014 [US3] Verify `--sig` shorthand works (should be no-op, same as default) (run tests)

**Checkpoint**: User Story 3 complete - backwards compatibility verified ✅

---

## Phase 6: Polish & Documentation

**Purpose**: Update documentation and finalize

- [x] T015 [P] Update Send Emails section in README.md to reflect new default behavior
- [x] T016 [P] Update options table in README.md with `--no-signature` flag description
- [x] T017 [P] Update Reply section in README.md with new signature behavior
- [x] T018 Run full test suite to verify no regressions: `pytest`
- [x] T019 Run linting to ensure code quality: `ruff check .`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A - no setup needed
- **Foundational (Phase 2)**: N/A - no foundation needed
- **User Stories (Phase 3-5)**: Can proceed immediately

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - implements core flag change
- **User Story 2 (P1)**: Depends on US1 (flag pair must exist) - but tests can be written in parallel
- **User Story 3 (P2)**: Depends on US1 (flag pair must exist) - but tests can be written in parallel

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation changes flag behavior
- Verify tests pass after implementation

### Parallel Opportunities

- T001, T002, T003 can run in parallel (different test functions)
- T007, T008 can run in parallel (different test functions)
- T011, T012 can run in parallel (different test functions)
- T015, T016, T017 can run in parallel (different README sections)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Add test test_send_default_includes_signature in tests/integration/test_send.py"
Task: "Add test test_reply_default_includes_signature in tests/integration/test_send.py"
Task: "Add test test_send_no_signature_when_none_configured in tests/integration/test_send.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Write tests T001-T003 (should fail)
2. Implement T004-T006 (change flag default)
3. **VALIDATE**: Run tests - should pass
4. Feature delivers value immediately

### Incremental Delivery

1. US1: Default includes signature → Core value delivered
2. US2: Opt-out works → User control added
3. US3: Backwards compat verified → Safe for existing users
4. Polish: Documentation updated → Feature complete

### Quick Execution Path

Since US1 and US2 share implementation (typer flag pair), they can be combined:

1. Write all tests (T001-T012)
2. Implement flag change (T004-T006)
3. Run all tests
4. Update documentation (T015-T017)
5. Final validation (T018-T019)

---

## Notes

- This is a minimal-change feature - only `send.py` and tests are modified
- Typer's `--flag/--no-flag` pattern handles most complexity automatically
- Existing signature logic (`get_signature`, HTML/text handling) is unchanged
- Total estimated tasks: 19
- Parallelizable tasks: 11 (marked with [P])
- Critical path: T001 → T004 → T018 (tests → implement → validate)

---

## Completion Summary

**Status**: ✅ ALL TASKS COMPLETE

**Tests**: 163 passed
**Linting**: Clean (0 errors)

**Files Modified**:
- `src/gmail_cli/cli/send.py` - Changed signature flag default from `False` to `True`, updated help text
- `tests/integration/test_send.py` - Added new tests, updated existing tests to mock signature
- `tests/integration/test_send_markdown.py` - Updated plain mode tests
- `README.md` - Updated documentation for new default behavior
