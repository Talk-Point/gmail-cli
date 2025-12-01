# Research: Gmail CLI Tool

**Feature Branch**: `001-gmail-cli`
**Date**: 2025-12-01

## Technology Decisions

### CLI Framework: typer

**Decision**: typer als CLI Framework

**Rationale**:
- Basiert auf click, aber mit modernem Python-Ansatz (Type Hints)
- Automatische `--help` Generierung aus Docstrings und Type Annotations
- Native Unterstützung für Subcommands (`gmail auth login`, `gmail search`)
- Exzellente Integration mit rich für formatierte Output
- Aktiv maintained, Teil des FastAPI-Ökosystems

**Alternatives Considered**:
- **click**: Bewährt, aber mehr Boilerplate ohne Type Hints
- **argparse**: Standard library, aber deutlich mehr manueller Aufwand
- **fire**: Zu implizit, weniger Kontrolle über CLI-Struktur

### Gmail API Client: google-api-python-client

**Decision**: google-api-python-client (offizielles Google SDK)

**Rationale**:
- Offizielle Google-Bibliothek, vollständige Gmail API Abdeckung
- Integrierte OAuth 2.0 Flow-Unterstützung via google-auth-oauthlib
- Automatisches Token-Refresh-Handling
- Gut dokumentiert mit vielen Beispielen
- Stabile, langfristig supported API

**Alternatives Considered**:
- **httpx + manuell**: Mehr Kontrolle, aber erheblicher Mehraufwand
- **gmail-api-wrapper (3rd party)**: Weniger maintained, unvollständige Features

### Terminal Output: rich

**Decision**: rich für formatierte Terminal-Ausgabe

**Rationale**:
- Best-in-class Terminal-Formatting für Python
- Native Table, Progress, Syntax Highlighting Support
- Funktioniert plattformübergreifend (inkl. Windows)
- Harmoniert perfekt mit typer (gleicher Autor)
- Einfache JSON-Ausgabe für `--json` Flag

**Alternatives Considered**:
- **colorama + tabulate**: Funktional, aber zwei Dependencies statt einer
- **termcolor**: Zu basic für Tabellen und komplexe Layouts

### Credential Storage: keyring

**Decision**: keyring library für Token-Speicherung

**Rationale**:
- Plattform-native Backends (Keychain, Credential Manager, Secret Service)
- Transparente API, gleicher Code auf allen Plattformen
- Industrie-Standard für Python CLI-Tools
- Verschlüsselung durch OS-Mechanismen

**Alternatives Considered**:
- **Encrypted file (~/.gmail-cli/tokens.json)**: Weniger sicher, Encryption-Key-Problem
- **Environment variables**: Nicht persistent, unpraktisch für CLI-Tools

### HTML to Text: html2text

**Decision**: html2text für HTML-zu-Text-Konvertierung

**Rationale**:
- Spezialisiert auf lesbare Text-Konvertierung aus HTML
- Erhält Struktur (Listen, Links) als Markdown-ähnliches Format
- Lightweight, keine JavaScript-Engine erforderlich
- Bewährt und stabil

**Alternatives Considered**:
- **BeautifulSoup + manuell**: Mehr Kontrolle, aber mehr Code
- **lxml**: Overkill für einfache Text-Extraktion

## Gmail API Patterns

### OAuth 2.0 Scopes

Erforderliche Scopes für die spezifizierten Features:

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',     # Lesen, Suchen
    'https://www.googleapis.com/auth/gmail.send',         # Senden
    'https://www.googleapis.com/auth/gmail.settings.basic' # Signatur abrufen
]
```

### Rate Limiting Strategy

Gmail API Limits:
- 250 quota units pro User pro Sekunde
- messages.list: 5 units, messages.get: 5 units, messages.send: 100 units

**Strategy**: Exponential Backoff bei 429 Responses
```python
# Base delay: 1s, Max retries: 3, Max delay: 8s
delays = [1, 2, 4]  # seconds
```

### Pagination Pattern

Gmail API verwendet `pageToken` für Pagination:

```python
def search_emails(query: str, limit: int = 20) -> list[Email]:
    results = []
    page_token = None

    while len(results) < limit:
        response = gmail.users().messages().list(
            userId='me',
            q=query,
            maxResults=min(limit - len(results), 100),
            pageToken=page_token
        ).execute()

        results.extend(response.get('messages', []))
        page_token = response.get('nextPageToken')

        if not page_token:
            break

    return results[:limit]
```

### Thread-basiertes Reply

Für korrekte Thread-Zuordnung bei Antworten:

```python
def reply_to_email(original_id: str, body: str) -> str:
    original = get_email(original_id)

    message = create_message(
        to=original.sender,
        subject=f"Re: {original.subject}",
        body=body,
        thread_id=original.thread_id,
        in_reply_to=original.message_id,
        references=original.references + [original.message_id]
    )

    return send_message(message)
```

## Security Considerations

### Credentials Bundling

Die `credentials.json` (OAuth Client ID/Secret) wird im Package gebundelt:
- Client Secret ist bei Desktop-Apps nicht wirklich "secret" (decompilierbar)
- Google erlaubt dies für "installed applications"
- Scope-Beschränkung limitiert Missbrauchspotential
- Alternative: User erstellt eigene OAuth App (schlechtere UX)

### Token Security

- Tokens im System Keyring gespeichert (OS-verschlüsselt)
- Refresh Tokens nie in Logs oder Output
- Access Tokens kurzlebig (1h), automatisch refreshed
- Logout löscht alle gespeicherten Credentials

## Dependencies Summary

```toml
[project]
dependencies = [
    "typer>=0.12.0",
    "rich>=13.0.0",
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.0.0",
    "keyring>=24.0.0",
    "html2text>=2024.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.5.0",
]
```

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| CLI Framework | typer (Type Hints, rich integration) |
| Gmail API Client | google-api-python-client (official) |
| Credential Storage | keyring (platform-native) |
| Terminal Formatting | rich (tables, colors, progress) |
| HTML Conversion | html2text (readable output) |
