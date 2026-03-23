# Implementation Plan: E-Mail Scheduling

**Branch**: `006-email-schedule` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-email-schedule/spec.md`

## Summary

Implementierung eines `--schedule` Parameters für die `send` und `reply` Befehle, der zeitgesteuerten E-Mail-Versand ermöglicht. Da die Gmail API kein natives Scheduling unterstützt, wird eine Draft-basierte Lösung mit System-Scheduler (`at` command) verwendet.

## Technical Context

**Language/Version**: Python 3.13+ (wie in Constitution definiert)
**Primary Dependencies**: typer (CLI), google-api-python-client (Gmail API), python-dateutil (Zeit-Parsing)
**Storage**: Gmail Drafts (API), keine lokale Persistenz
**Testing**: pytest mit Gmail API Mocks
**Target Platform**: Linux, macOS, Windows (mit Einschränkungen beim Scheduler)
**Project Type**: Single CLI Application
**Performance Goals**: E-Mail-Planung < 5 Sekunden
**Constraints**: System-Scheduler (`at`) für automatischen Versand erforderlich
**Scale/Scope**: Einzelne geplante E-Mails pro Aufruf

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modern Python Stack | ✅ PASS | Python 3.13+, uv, ruff |
| II. CLI-First Design | ✅ PASS | `--schedule` Parameter, `--json` Output |
| III. Test-Driven Development | ✅ PASS | pytest mit Mocks geplant |
| IV. Secure Credential Handling | ✅ PASS | Keine Änderung am Auth-Flow |
| V. Simplicity Over Features | ✅ PASS | Nutzt OS-Scheduler statt eigener Daemon |

**Gate Status**: ✅ PASSED

## Project Structure

### Documentation (this feature)

```text
specs/006-email-schedule/
├── spec.md              # Feature-Spezifikation
├── plan.md              # Dieser Plan
├── research.md          # Phase 0: Research-Ergebnisse
├── data-model.md        # Phase 1: Datenmodell
├── quickstart.md        # Phase 1: Schnellstart-Anleitung
├── contracts/           # Phase 1: CLI-Interface
│   └── cli-interface.md
└── checklists/
    └── requirements.md  # Quality-Checklist
```

### Source Code (repository root)

```text
src/gmail_cli/
├── cli/
│   ├── send.py          # MODIFY: --schedule Parameter
│   └── draft.py         # EXISTING: Draft-Funktionen
├── services/
│   ├── gmail.py         # EXISTING: Gmail API
│   └── scheduler.py     # NEW: System-Scheduler Integration
├── utils/
│   └── time_parser.py   # NEW: Zeit-Parsing
└── models/
    └── schedule.py      # NEW: ScheduledEmail Model

tests/
├── unit/
│   ├── test_time_parser.py    # NEW
│   └── test_scheduler.py      # NEW
└── integration/
    └── test_schedule_send.py  # NEW
```

**Structure Decision**: Single project structure (Option 1) - konsistent mit bestehendem Codebase.

## Implementation Components

### 1. Time Parser (`utils/time_parser.py`)

Parst verschiedene Zeitformate in datetime-Objekte.

```python
def parse_schedule_time(time_str: str) -> datetime:
    """Parse schedule time string to datetime."""
    # Unterstützt:
    # - ISO-8601: "2026-01-15T09:00"
    # - Datum+Zeit: "2026-01-15 09:00"
    # - Relativ: "in 30 minutes", "in 2 hours"
    # - Natural: "tomorrow 09:00"
```

### 2. Scheduler Service (`services/scheduler.py`)

Integriert System-Scheduler für automatischen Versand.

```python
def schedule_draft_send(draft_id: str, send_time: datetime, account: str | None) -> ScheduleResult:
    """Schedule a draft to be sent at specified time."""
    # 1. Prüfe at-Verfügbarkeit
    # 2. Erstelle at-Job: gmail draft send <draft_id>
    # 3. Rückgabe: job_id oder None wenn nicht verfügbar
```

### 3. CLI Integration (`cli/send.py`)

Erweiterung des bestehenden send_command.

```python
schedule: Annotated[
    str | None,
    typer.Option(
        "--schedule", "-S",
        help="Schedule email for later. Examples: '2026-01-15 09:00', 'in 2 hours', 'tomorrow 09:00'"
    ),
] = None
```

### 4. Model (`models/schedule.py`)

Dataclass für geplante E-Mails.

```python
@dataclass
class ScheduledEmail:
    draft_id: str
    scheduled_time: datetime
    recipients: list[str]
    subject: str
    job_id: str | None = None
    status: ScheduleStatus = ScheduleStatus.PENDING
```

## Dependencies

### New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-dateutil | ^2.8 | Flexibles Zeit-Parsing |

### Existing Dependencies (unverändert)

- typer
- google-api-python-client
- keyring
- rich

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `at` nicht verfügbar | Medium | Medium | Graceful Degradation: Draft + Hinweis |
| Zeit-Parsing Fehler | Low | Low | Umfangreiche Tests + klare Fehlermeldungen |
| Gmail API Änderungen | Low | High | Draft-API ist stabil, API-Version pinnen |

## Complexity Tracking

> Keine Constitution-Verletzungen - Tabelle nicht erforderlich.

## Next Steps

1. **`/speckit.tasks`**: Generiert tasks.md mit konkreten Implementierungsschritten
2. **`/speckit.implement`**: Führt die Tasks aus

## Artifacts Generated

- [x] `research.md` - Gmail API Recherche, Implementierungsstrategie
- [x] `data-model.md` - ScheduledEmail, ScheduleTime Entities
- [x] `contracts/cli-interface.md` - CLI Parameter und Output-Formate
- [x] `quickstart.md` - Benutzeranleitung
