# Tasks: Draft-Funktion

**Input**: Design documents from `/specs/005-draft-function/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-commands.md

**Tests**: Included per Constitution III (Test-Driven Development)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Shared infrastructure for draft functionality

- [x] T001 [P] Add `create_draft()` function to src/gmail_cli/services/gmail.py
- [x] T002 [P] Add `DraftNotFoundError` exception class to src/gmail_cli/services/gmail.py
- [x] T003 Create draft CLI app scaffold in src/gmail_cli/cli/draft.py
- [x] T004 Register draft_app in src/gmail_cli/cli/main.py

**Checkpoint**: Draft infrastructure ready - user story implementation can begin

---

## Phase 2: User Story 1 - E-Mail als Entwurf speichern (Priority: P1) 🎯 MVP

**Goal**: `gmail send --draft` speichert E-Mail als Entwurf statt zu senden

**Independent Test**: `gmail send --to test@example.com --subject "Test" --body "Content" --draft` erstellt Draft

### Tests for User Story 1

- [x] T005 [P] [US1] Unit test for create_draft() in tests/unit/test_draft.py

### Implementation for User Story 1

- [x] T006 [US1] Add `--draft` flag to send_command() in src/gmail_cli/cli/send.py
- [x] T007 [US1] Implement draft creation logic in send_command() using create_draft() in src/gmail_cli/cli/send.py
- [x] T008 [US1] Add draft success output (Draft ID, confirmation) in src/gmail_cli/cli/send.py
- [x] T009 [US1] Add JSON output for draft creation in src/gmail_cli/cli/send.py

**Checkpoint**: `gmail send --draft` fully functional

---

## Phase 3: User Story 2 - Antwort als Entwurf speichern (Priority: P1)

**Goal**: `gmail reply --draft` speichert Antwort als Entwurf mit Thread-Verknüpfung

**Independent Test**: `gmail reply <msg-id> --body "Reply" --draft` erstellt Draft im Thread

### Tests for User Story 2

- [x] T010 [P] [US2] Unit test for reply draft with threadId in tests/unit/test_draft.py

### Implementation for User Story 2

- [x] T011 [US2] Add `--draft` flag to reply_command() in src/gmail_cli/cli/send.py
- [x] T012 [US2] Implement reply draft logic with threadId in src/gmail_cli/cli/send.py
- [x] T013 [US2] Add draft success output for reply (Draft ID, Thread ID) in src/gmail_cli/cli/send.py

**Checkpoint**: `gmail reply --draft` fully functional with threading

---

## Phase 4: User Story 3 - Entwürfe auflisten (Priority: P2)

**Goal**: `gmail draft list` zeigt alle Entwürfe mit ID, Empfänger, Betreff

**Independent Test**: `gmail draft list` zeigt vorhandene Entwürfe an

### Tests for User Story 3

- [x] T014 [P] [US3] Unit test for list_drafts() in tests/unit/test_draft.py

### Implementation for User Story 3

- [x] T015 [P] [US3] Add `list_drafts()` function to src/gmail_cli/services/gmail.py
- [x] T016 [US3] Implement `list_command()` in src/gmail_cli/cli/draft.py
- [x] T017 [US3] Add human-readable output for draft list in src/gmail_cli/cli/draft.py
- [x] T018 [US3] Add JSON output for draft list in src/gmail_cli/cli/draft.py
- [x] T019 [US3] Handle empty drafts case with appropriate message in src/gmail_cli/cli/draft.py

**Checkpoint**: `gmail draft list` fully functional

---

## Phase 5: User Story 4 - Entwurf anzeigen (Priority: P2)

**Goal**: `gmail draft show <id>` zeigt vollständige Entwurf-Details

**Independent Test**: `gmail draft show r123` zeigt Empfänger, Betreff, Body, Anhänge

### Tests for User Story 4

- [x] T020 [P] [US4] Unit test for get_draft() in tests/unit/test_draft.py

### Implementation for User Story 4

- [x] T021 [P] [US4] Add `get_draft()` function to src/gmail_cli/services/gmail.py
- [x] T022 [US4] Implement `show_command()` in src/gmail_cli/cli/draft.py
- [x] T023 [US4] Add human-readable output for draft details in src/gmail_cli/cli/draft.py
- [x] T024 [US4] Add JSON output for draft details in src/gmail_cli/cli/draft.py
- [x] T025 [US4] Handle draft not found error with DraftNotFoundError in src/gmail_cli/cli/draft.py

**Checkpoint**: `gmail draft show` fully functional

---

## Phase 6: User Story 5 - Entwurf senden (Priority: P2)

**Goal**: `gmail draft send <id>` sendet existierenden Entwurf

**Independent Test**: `gmail draft send r123` sendet Draft und zeigt Message-ID

### Tests for User Story 5

- [x] T026 [P] [US5] Unit test for send_draft() in tests/unit/test_draft.py

### Implementation for User Story 5

- [x] T027 [P] [US5] Add `send_draft()` function to src/gmail_cli/services/gmail.py
- [x] T028 [US5] Implement `send_command()` in src/gmail_cli/cli/draft.py
- [x] T029 [US5] Add success output (Message ID, Thread ID) in src/gmail_cli/cli/draft.py
- [x] T030 [US5] Handle draft not found error in src/gmail_cli/cli/draft.py

**Checkpoint**: `gmail draft send` fully functional

---

## Phase 7: User Story 6 - Entwurf löschen (Priority: P3)

**Goal**: `gmail draft delete <id>` löscht Entwurf permanent

**Independent Test**: `gmail draft delete r123` löscht Draft und bestätigt

### Tests for User Story 6

- [x] T031 [P] [US6] Unit test for delete_draft() in tests/unit/test_draft.py

### Implementation for User Story 6

- [x] T032 [P] [US6] Add `delete_draft()` function to src/gmail_cli/services/gmail.py
- [x] T033 [US6] Implement `delete_command()` in src/gmail_cli/cli/draft.py
- [x] T034 [US6] Add success output for deletion in src/gmail_cli/cli/draft.py
- [x] T035 [US6] Handle draft not found error in src/gmail_cli/cli/draft.py

**Checkpoint**: `gmail draft delete` fully functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Quality assurance and integration

- [x] T036 [P] Add --account flag to all draft commands in src/gmail_cli/cli/draft.py
- [x] T037 [P] Integration test for complete draft workflow in tests/integration/test_draft_cli.py
- [x] T038 [P] Regression test for send/reply without --draft in tests/integration/test_draft_cli.py
- [x] T039 Run ruff check and ruff format on all modified files
- [x] T040 Run pytest to verify all tests pass
- [x] T041 Run quickstart.md validation (manual test of documented commands)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 2-7)**: All depend on Setup completion
  - US1 and US2 share send.py but can be done sequentially
  - US3-US6 all work on draft.py but can be parallelized with careful coordination
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Setup - No dependencies on other stories
- **US2 (P1)**: Can start after Setup - Independent of US1 (different function in send.py)
- **US3 (P2)**: Can start after Setup - Independent
- **US4 (P2)**: Can start after Setup - Independent
- **US5 (P2)**: Can start after Setup - Independent
- **US6 (P3)**: Can start after Setup - Independent

### Within Each User Story

- Test MUST be written and FAIL before implementation
- Service function before CLI command
- Core implementation before output formatting
- Human output before JSON output
- Error handling last

### Parallel Opportunities

**Within Setup:**
```
T001 [P] create_draft() function
T002 [P] DraftNotFoundError exception
```

**Within US3-US6 (service layer):**
```
T015 [P] list_drafts()
T021 [P] get_draft()
T027 [P] send_draft()
T032 [P] delete_draft()
```

**Within Polish:**
```
T036 [P] --account flag
T037 [P] Integration tests
T038 [P] Regression tests
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: User Story 1 (T005-T009)
3. Complete Phase 3: User Story 2 (T010-T013)
4. **STOP and VALIDATE**: Test `gmail send --draft` and `gmail reply --draft`
5. Deploy/demo if ready - users can create drafts!

### Incremental Delivery

| Release | User Stories | New Capability |
|---------|--------------|----------------|
| MVP | US1, US2 | Create drafts via --draft flag |
| v2 | + US3, US4 | View drafts (list, show) |
| v3 | + US5 | Send drafts from CLI |
| v4 | + US6 | Delete drafts |

### Task Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| 1 | Setup | 4 | 2 |
| 2 | US1 | 5 | 1 |
| 3 | US2 | 4 | 1 |
| 4 | US3 | 6 | 2 |
| 5 | US4 | 6 | 2 |
| 6 | US5 | 5 | 2 |
| 7 | US6 | 5 | 2 |
| 8 | Polish | 6 | 3 |
| **Total** | | **41** | **15** |

---

## Notes

- All draft operations reuse existing `get_gmail_service()` and `_execute_with_retry()`
- DraftNotFoundError follows pattern of existing SendError
- JSON output uses existing `print_json()` from utils/output.py
- Multi-account support uses existing `--account` pattern from send.py
