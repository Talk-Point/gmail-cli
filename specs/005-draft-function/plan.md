# Implementation Plan: Draft-Funktion

**Branch**: `005-draft-function` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-draft-function/spec.md`

## Summary

Implementierung einer Draft-Funktion für gmail-cli, die es Benutzern ermöglicht, E-Mails als Entwurf zu speichern statt sie direkt zu senden. Dies umfasst ein `--draft` Flag für bestehende `send` und `reply` Commands sowie neue `gmail draft` Subcommands für die Verwaltung von Entwürfen (list, show, send, delete).

## Technical Context

**Language/Version**: Python 3.11+ (kompatibel mit 3.11, 3.12, 3.13, 3.14)
**Primary Dependencies**: typer (CLI), google-api-python-client (Gmail API), rich (Output), keyring (Credentials)
**Storage**: Gmail API (Drafts werden in Gmail gespeichert, nicht lokal)
**Testing**: pytest mit Mocks für Gmail API
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single CLI application
**Performance Goals**: Draft-Operationen < 5 Sekunden (API-abhängig)
**Constraints**: Bestehende send/reply-Funktionalität darf nicht beeinträchtigt werden
**Scale/Scope**: Feature-Erweiterung für bestehende CLI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modern Python Stack | ✅ PASS | Python 3.11+, Type Hints, uv, ruff |
| II. CLI-First Design | ✅ PASS | `gmail draft <verb>` Pattern, `--json` Support |
| III. Test-Driven Development | ✅ PASS | pytest mit Gmail API Mocks geplant |
| IV. Secure Credential Handling | ✅ PASS | Wiederverwendet bestehende OAuth-Infrastruktur |
| V. Simplicity Over Features | ✅ PASS | Minimaler Scope: nur Draft CRUD + Flag |

**Gate Status**: PASSED - Keine Violations

## Project Structure

### Documentation (this feature)

```text
specs/005-draft-function/
├── spec.md              # Feature-Spezifikation
├── plan.md              # This file
├── research.md          # Phase 0: Gmail API Draft Research
├── data-model.md        # Phase 1: Draft Entity Model
├── quickstart.md        # Phase 1: Integration Guide
├── contracts/           # Phase 1: CLI Command Contracts
│   └── cli-commands.md
└── checklists/
    └── requirements.md  # Spec Quality Checklist
```

### Source Code (repository root)

```text
src/gmail_cli/
├── cli/
│   ├── main.py          # MODIFY: Register draft_app
│   ├── send.py          # MODIFY: Add --draft flag to send_command, reply_command
│   └── draft.py         # NEW: Draft CLI commands (list, show, send, delete)
├── services/
│   └── gmail.py         # MODIFY: Add create_draft, list_drafts, get_draft, send_draft, delete_draft
└── models/
    └── draft.py         # NEW: Draft dataclass (optional, may reuse Email)

tests/
├── unit/
│   └── test_draft.py    # NEW: Unit tests for draft functions
└── integration/
    └── test_draft_cli.py # NEW: CLI integration tests
```

**Structure Decision**: Single project structure, following existing patterns in `src/gmail_cli/`. New `draft.py` files in `cli/` and optionally `models/`. All draft API functions added to existing `gmail.py` service.

## Implementation Approach

### Phase 1: Service Layer (gmail.py)
Add Gmail API draft functions following existing patterns:
- `create_draft(message, account)` - Create draft from composed message
- `list_drafts(account, max_results)` - List all drafts
- `get_draft(draft_id, account)` - Get single draft details
- `send_draft(draft_id, account)` - Send existing draft
- `delete_draft(draft_id, account)` - Delete draft

### Phase 2: CLI Layer
1. Modify `send.py`: Add `--draft` flag to `send_command()` and `reply_command()`
2. Create `draft.py`: New typer app with list, show, send, delete commands
3. Modify `main.py`: Register `draft_app` as subcommand group

### Phase 3: Testing
- Unit tests for all new service functions (mocked API)
- CLI integration tests for all new commands
- Regression tests for existing send/reply functionality

## Complexity Tracking

> No violations - table not required.
