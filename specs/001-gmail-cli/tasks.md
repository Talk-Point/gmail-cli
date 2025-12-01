# Tasks: Gmail CLI Tool

**Input**: Design documents from `/specs/001-gmail-cli/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included as the Constitution specifies TDD (Test-Driven Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure with src/gmail_cli/, tests/ directories
- [x] T002 Initialize uv project with pyproject.toml (Python 3.13+, dependencies: typer, rich, google-api-python-client, google-auth-oauthlib, keyring, html2text)
- [x] T003 [P] Configure ruff for linting and formatting in pyproject.toml
- [x] T004 [P] Add credentials.json (OAuth client credentials) to project root
- [x] T005 [P] Create src/gmail_cli/__init__.py with version string
- [x] T006 [P] Create src/gmail_cli/__main__.py entry point

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 [P] Create shared models in src/gmail_cli/models/__init__.py (exports)
- [x] T008 [P] Create Email dataclass in src/gmail_cli/models/email.py (per data-model.md)
- [x] T009 [P] Create Attachment dataclass in src/gmail_cli/models/attachment.py (per data-model.md)
- [x] T010 Create output utilities in src/gmail_cli/utils/output.py (rich formatting, JSON output, error formatting)
- [x] T011 [P] Create HTML to text converter in src/gmail_cli/utils/html.py (html2text wrapper)
- [x] T012 Create base CLI app structure in src/gmail_cli/cli/main.py (typer app with --help, --version, --json global options)
- [x] T013 Create test fixtures and Gmail API mocks in tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1+2 - Authentication & Installation (Priority: P1)

**Goal**: User kann sich bei Gmail authentifizieren und das Tool über uv installieren

**Independent Test**: `uv tool install .` gefolgt von `gmail auth login` → OAuth-Flow → Token gespeichert

### Tests for User Story 1+2

- [x] T014 [P] [US1] Unit test for credentials storage in tests/unit/test_credentials.py
- [x] T015 [P] [US1] Unit test for auth service in tests/unit/test_auth_service.py
- [x] T016 [P] [US1] Integration test for auth CLI commands in tests/integration/test_auth.py

### Implementation for User Story 1+2

- [x] T017 [P] [US1] Create Credentials model in src/gmail_cli/models/credentials.py (per data-model.md)
- [x] T018 [US1] Implement keyring storage service in src/gmail_cli/services/credentials.py (save/load/delete tokens)
- [x] T019 [US1] Implement OAuth flow service in src/gmail_cli/services/auth.py (browser auth, token exchange, refresh)
- [x] T020 [US1] Implement `gmail auth login` command in src/gmail_cli/cli/auth.py
- [x] T021 [US1] Implement `gmail auth logout` command in src/gmail_cli/cli/auth.py
- [x] T022 [US1] Implement `gmail auth status` command in src/gmail_cli/cli/auth.py
- [x] T023 [US1] Register auth subcommand in src/gmail_cli/cli/main.py
- [x] T024 [US1] Add auth-required decorator for protected commands in src/gmail_cli/cli/auth.py

**Checkpoint**: User Story 1+2 complete - `gmail auth login/logout/status` and `gmail --version/--help` work

---

## Phase 4: User Story 3 - E-Mails suchen (Priority: P2)

**Goal**: User kann E-Mails durchsuchen mit Filtern und Pagination

**Independent Test**: `gmail search "test"` → Liste mit ID, Absender, Betreff, Datum

### Tests for User Story 3

- [ ] T025 [P] [US3] Unit test for Gmail search service in tests/unit/test_gmail_service.py
- [ ] T026 [P] [US3] Integration test for search CLI in tests/integration/test_search.py

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create SearchResult model in src/gmail_cli/models/search.py (per data-model.md)
- [ ] T028 [US3] Implement Gmail API wrapper base in src/gmail_cli/services/gmail.py (client initialization, rate limiting, exponential backoff)
- [ ] T029 [US3] Implement search_emails method in src/gmail_cli/services/gmail.py (query building, pagination, message parsing)
- [ ] T030 [US3] Implement `gmail search` command in src/gmail_cli/cli/search.py (--from, --to, --subject, --label, --after, --before, --has-attachment, --limit, --page)
- [ ] T031 [US3] Register search command in src/gmail_cli/cli/main.py
- [ ] T032 [US3] Add search results table formatting in src/gmail_cli/utils/output.py

**Checkpoint**: User Story 3 complete - `gmail search` with filters and pagination works

---

## Phase 5: User Story 4 - E-Mail lesen (Priority: P2)

**Goal**: User kann eine E-Mail vollständig lesen inkl. HTML-zu-Text Konvertierung

**Independent Test**: `gmail read <id>` → Vollständige E-Mail mit Absender, Betreff, Body, Anhänge-Liste

### Tests for User Story 4

- [ ] T033 [P] [US4] Unit test for email parsing in tests/unit/test_email_parser.py
- [ ] T034 [P] [US4] Integration test for read CLI in tests/integration/test_read.py

### Implementation for User Story 4

- [ ] T035 [US4] Implement get_email method in src/gmail_cli/services/gmail.py (full message fetch, MIME parsing, attachment extraction)
- [ ] T036 [US4] Implement email body parser (HTML to text) in src/gmail_cli/services/gmail.py
- [ ] T037 [US4] Implement `gmail read` command in src/gmail_cli/cli/read.py (formatted output with headers, body, attachment list)
- [ ] T038 [US4] Register read command in src/gmail_cli/cli/main.py
- [ ] T039 [US4] Add email detail formatting in src/gmail_cli/utils/output.py (rich panels, attachment list)

**Checkpoint**: User Story 4 complete - `gmail read <id>` shows full email content

---

## Phase 6: User Story 5 - Attachments verwalten (Priority: P2)

**Goal**: User kann Anhänge einer E-Mail auflisten und herunterladen

**Independent Test**: `gmail attachment list <id>` → Anhänge-Liste; `gmail attachment download <id> <name>` → Datei gespeichert

### Tests for User Story 5

- [ ] T040 [P] [US5] Unit test for attachment download in tests/unit/test_attachment.py
- [ ] T041 [P] [US5] Integration test for attachment CLI in tests/integration/test_attachment.py

### Implementation for User Story 5

- [ ] T042 [US5] Implement get_attachment method in src/gmail_cli/services/gmail.py (attachment fetch, base64 decode)
- [ ] T043 [US5] Implement download_attachment method in src/gmail_cli/services/gmail.py (file writing with progress)
- [ ] T044 [US5] Implement `gmail attachment list` command in src/gmail_cli/cli/attachment.py
- [ ] T045 [US5] Implement `gmail attachment download` command in src/gmail_cli/cli/attachment.py (single file, --all, --output)
- [ ] T046 [US5] Register attachment subcommand in src/gmail_cli/cli/main.py
- [ ] T047 [US5] Add download progress indicator in src/gmail_cli/utils/output.py (rich progress bar)

**Checkpoint**: User Story 5 complete - `gmail attachment list/download` works

---

## Phase 7: User Story 6 - E-Mail senden (Priority: P3)

**Goal**: User kann E-Mails senden und auf bestehende antworten, optional mit Gmail-Signatur

**Independent Test**: `gmail send --to x@x.com --subject "Test" --body "Hi"` → E-Mail gesendet

### Tests for User Story 6

- [ ] T048 [P] [US6] Unit test for email composition in tests/unit/test_compose.py
- [ ] T049 [P] [US6] Unit test for signature fetching in tests/unit/test_signature.py
- [ ] T050 [P] [US6] Integration test for send/reply CLI in tests/integration/test_send.py

### Implementation for User Story 6

- [ ] T051 [P] [US6] Create Signature model in src/gmail_cli/models/signature.py (per data-model.md)
- [ ] T052 [US6] Implement get_signature method in src/gmail_cli/services/gmail.py (Gmail Settings API)
- [ ] T053 [US6] Implement compose_email method in src/gmail_cli/services/gmail.py (MIME message creation, attachment encoding)
- [ ] T054 [US6] Implement send_email method in src/gmail_cli/services/gmail.py (message send API)
- [ ] T055 [US6] Implement reply_to_email method in src/gmail_cli/services/gmail.py (thread handling, In-Reply-To, References headers)
- [ ] T056 [US6] Implement `gmail send` command in src/gmail_cli/cli/send.py (--to, --cc, --bcc, --subject, --body, --body-file, --attach, --signature)
- [ ] T057 [US6] Implement `gmail reply` command in src/gmail_cli/cli/send.py (--body, --body-file, --attach, --all, --signature)
- [ ] T058 [US6] Register send and reply commands in src/gmail_cli/cli/main.py
- [ ] T059 [US6] Add send confirmation formatting in src/gmail_cli/utils/output.py

**Checkpoint**: User Story 6 complete - `gmail send` and `gmail reply` work with signature support

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Add comprehensive error messages with tips in src/gmail_cli/utils/output.py
- [ ] T061 [P] Add --json output support verification for all commands
- [ ] T062 Run full test suite and fix any failing tests
- [ ] T063 Run ruff check and ruff format, fix any issues
- [ ] T064 Verify all type hints are present on public functions
- [ ] T065 Run quickstart.md validation (manual test of all documented commands)
- [ ] T066 Update pyproject.toml with final entry point configuration for `gmail` command

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1+2 (Phase 3)**: Depends on Foundational - Authentication BLOCKS other stories
- **User Stories 3-6 (Phases 4-7)**: Depend on Authentication (Phase 3)
  - US3 (Search), US4 (Read), US5 (Attachments) can proceed in parallel after auth
  - US6 (Send) can proceed in parallel but benefits from US4 for reply functionality
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```text
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational)
    │
    ▼
Phase 3 (US1+2: Auth + Install) ─── GATE: All other stories require auth
    │
    ├──────────────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼
Phase 4        Phase 5        Phase 6        Phase 7
(US3: Search)  (US4: Read)    (US5: Attach)  (US6: Send)
    │              │              │              │
    └──────────────┴──────────────┴──────────────┘
                          │
                          ▼
                   Phase 8 (Polish)
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before CLI commands
- CLI commands before registration in main.py

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# Parallel: T003, T004, T005, T006
```

**Phase 2 (Foundational)**:
```bash
# Parallel: T007, T008, T009, T011
```

**Phase 3 (US1+2: Auth)**:
```bash
# Parallel tests: T014, T015, T016
```

**Phases 4-7 (US3-6)**: Can run in parallel after Phase 3 completes
```bash
# Start all user story phases simultaneously if team capacity allows
```

---

## Implementation Strategy

### MVP First (User Story 1+2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1+2 (Auth + Install)
4. **STOP and VALIDATE**: Test auth flow end-to-end
5. Deploy/demo if ready - minimal working CLI

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1+2 (Auth) → Test independently → **MVP!** (can authenticate)
3. Add US3 (Search) → Test independently → Can search emails
4. Add US4 (Read) → Test independently → Can read emails
5. Add US5 (Attachments) → Test independently → Can download attachments
6. Add US6 (Send) → Test independently → Full feature set complete
7. Each story adds value without breaking previous stories

### Single Developer Strategy

Recommended order for solo development:

1. Phase 1 → Phase 2 → Phase 3 (foundation + auth)
2. Phase 4 (search) - most common operation
3. Phase 5 (read) - builds on search results
4. Phase 6 (attachments) - enhances read
5. Phase 7 (send) - least common, most complex
6. Phase 8 (polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requires: TDD, type hints, ruff passing, keyring storage
