# Implementation Plan: Gmail CLI Tool

**Branch**: `001-gmail-cli` | **Date**: 2025-12-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-gmail-cli/spec.md`

## Summary

Gmail CLI Tool für Entwickler - ein Python-basiertes Command-Line Interface für Gmail mit OAuth 2.0 Authentifizierung, E-Mail-Suche mit Pagination, Lesen und Senden von E-Mails (inkl. Signatur-Support) sowie Attachment-Management. Das Tool wird über uv installiert und folgt dem gh CLI Design-Pattern.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: typer (CLI), google-api-python-client (Gmail API), keyring (Credential Storage), rich (Terminal Output)
**Storage**: System Keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)
**Testing**: pytest mit pytest-mock für Gmail API Mocks
**Target Platform**: macOS, Linux, Windows (Cross-Platform CLI)
**Project Type**: Single project (CLI application)
**Performance Goals**: Suchergebnisse <3s, E-Mail laden <2s, Senden <5s
**Constraints**: Gmail API Rate Limits, 25MB Attachment Limit, OAuth 2.0 Scopes
**Scale/Scope**: Single-User CLI Tool, lokale Installation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Modern Python Stack | ✅ PASS | Python 3.13+, uv, ruff, type hints throughout |
| II. CLI-First Design | ✅ PASS | typer CLI, `gmail <verb>` pattern, `--json` output support |
| III. Test-Driven Development | ✅ PASS | pytest mit Mocks für Gmail API, TDD workflow |
| IV. Secure Credential Handling | ✅ PASS | keyring library, keine Credentials in Logs/Output |
| V. Simplicity Over Features | ✅ PASS | Fokus auf Kernfunktionen, explizites Out-of-Scope |

**Gate Result**: PASS - Alle Constitution-Prinzipien erfüllt.

## Project Structure

### Documentation (this feature)

```text
specs/001-gmail-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
└── gmail_cli/
    ├── __init__.py
    ├── __main__.py      # Entry point
    ├── cli/
    │   ├── __init__.py
    │   ├── main.py      # Main CLI app (typer)
    │   ├── auth.py      # auth login/logout/status
    │   ├── search.py    # search command
    │   ├── read.py      # read command
    │   ├── send.py      # send/reply commands
    │   └── attachment.py # attachment list/download
    ├── services/
    │   ├── __init__.py
    │   ├── gmail.py     # Gmail API wrapper
    │   ├── auth.py      # OAuth flow + token management
    │   └── credentials.py # Keyring storage
    ├── models/
    │   ├── __init__.py
    │   ├── email.py     # Email dataclass
    │   └── attachment.py # Attachment dataclass
    └── utils/
        ├── __init__.py
        ├── output.py    # rich formatting, JSON output
        └── html.py      # HTML to text conversion

tests/
├── conftest.py          # Shared fixtures, Gmail API mocks
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
└── integration/
    ├── test_auth.py
    ├── test_search.py
    ├── test_read.py
    └── test_send.py

pyproject.toml           # uv project config
credentials.json         # OAuth client credentials (bundled)
```

**Structure Decision**: Single project structure gewählt - CLI-Anwendung ohne Backend/Frontend-Trennung. Klare Separation zwischen CLI-Befehlen (`cli/`), Business Logic (`services/`), Datenmodellen (`models/`) und Utilities (`utils/`).

## Complexity Tracking

> Keine Constitution-Violations - keine Komplexitäts-Rechtfertigungen erforderlich.
