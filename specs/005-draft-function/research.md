# Research: Draft-Funktion

**Feature**: 005-draft-function
**Date**: 2025-12-17

## Gmail API Draft Endpoints

### Decision: Gmail API v1 Draft Resource

**Rationale**: Die Gmail API bietet vollständige Draft-Unterstützung über die `users.drafts` Resource. Diese ist gut dokumentiert, stabil und wird bereits für andere Operationen im Projekt verwendet.

**Alternatives considered**:
- IMAP Draft-Ordner: Zu komplex, erfordert separate Verbindung, keine Threading-Unterstützung
- Lokale Speicherung: Nicht synchron mit Gmail, erfordert eigene Persistenz

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `users.drafts.create` | POST | Erstellt neuen Draft |
| `users.drafts.list` | GET | Listet alle Drafts |
| `users.drafts.get` | GET | Ruft einzelnen Draft ab |
| `users.drafts.send` | POST | Sendet Draft |
| `users.drafts.delete` | DELETE | Löscht Draft |
| `users.drafts.update` | PUT | Aktualisiert Draft (nicht benötigt) |

### Request/Response Format

**Create Draft Request**:
```python
body = {
    "message": {
        "raw": base64_encoded_message,
        "threadId": "optional_thread_id"  # Für Reply-Drafts
    }
}
service.users().drafts().create(userId="me", body=body).execute()
```

**Create Draft Response**:
```json
{
    "id": "r1234567890",
    "message": {
        "id": "msg_id",
        "threadId": "thread_id"
    }
}
```

**List Drafts Response**:
```json
{
    "drafts": [
        {
            "id": "r1234567890",
            "message": {
                "id": "msg_id",
                "threadId": "thread_id"
            }
        }
    ],
    "nextPageToken": "token",
    "resultSizeEstimate": 10
}
```

## OAuth Scopes

### Decision: Bestehende Scopes ausreichend

**Rationale**: Die bereits verwendeten Scopes `gmail.compose` und `gmail.send` umfassen Draft-Operationen. Kein zusätzlicher Scope erforderlich.

**Alternatives considered**:
- `gmail.modify`: Zu breit, umfasst Löschen von Nachrichten
- `gmail.drafts`: Existiert nicht als separater Scope

**Scope Coverage**:
| Scope | Create | List | Get | Send | Delete |
|-------|--------|------|-----|------|--------|
| gmail.compose | ✅ | ✅ | ✅ | ✅ | ✅ |
| gmail.send | ❌ | ❌ | ❌ | ✅ | ❌ |
| gmail.readonly | ❌ | ✅ | ✅ | ❌ | ❌ |

## Message Composition for Drafts

### Decision: Bestehende compose_email/compose_reply wiederverwenden

**Rationale**: Die bestehenden Funktionen `compose_email()` und `compose_reply()` erstellen bereits das korrekte Message-Format (`{"raw": base64_string}`). Für Drafts muss nur die Wrapper-Struktur angepasst werden.

**Implementation Pattern**:
```python
# Bestehend (für send)
message = compose_email(to, subject, body, ...)
send_email(message, account)

# Neu (für draft)
message = compose_email(to, subject, body, ...)
create_draft(message, account)  # Wraps in {"message": message}
```

**Alternatives considered**:
- Separate compose_draft() Funktion: Unnötige Duplikation
- Draft-spezifisches Message-Format: Gmail API akzeptiert gleiches Format

## Reply Draft Threading

### Decision: threadId aus Original-Message übernehmen

**Rationale**: Bei `reply --draft` muss der Draft mit dem Original-Thread verknüpft werden. Die bestehende `compose_reply()` Funktion gibt bereits `{"raw": ..., "threadId": ...}` zurück.

**Implementation**:
```python
# compose_reply() returns:
{"raw": base64_message, "threadId": original_thread_id}

# create_draft() wraps as:
{"message": {"raw": base64_message, "threadId": original_thread_id}}
```

## Error Handling

### Decision: Bestehende Retry-Logik wiederverwenden

**Rationale**: Die `_execute_with_retry()` Funktion behandelt bereits Rate Limiting (HTTP 429) und Token-Expiration. Für Draft-Operationen gelten die gleichen Fehlerszenarien.

**Draft-spezifische Fehler**:
| Error | HTTP Status | Handling |
|-------|-------------|----------|
| Draft not found | 404 | DraftNotFoundError mit Draft-ID |
| Invalid message | 400 | Weiterleiten mit verständlicher Meldung |
| Rate limited | 429 | Exponential backoff (bestehend) |
| Token expired | 401 | TokenExpiredError (bestehend) |

## CLI Pattern

### Decision: `gmail draft <verb>` mit separatem Typer App

**Rationale**: Folgt bestehendem Pattern für Subcommand-Gruppen (z.B. `gmail accounts`, `gmail auth`). Ermöglicht saubere Trennung und eigene Help-Texte.

**Command Structure**:
```
gmail draft list [--json] [--account EMAIL]
gmail draft show DRAFT_ID [--json] [--account EMAIL]
gmail draft send DRAFT_ID [--account EMAIL]
gmail draft delete DRAFT_ID [--account EMAIL]

gmail send ... --draft  # Neues Flag
gmail reply ... --draft  # Neues Flag
```

**Alternatives considered**:
- Einzelne Commands (`gmail draft-list`, `gmail draft-show`): Inkonsistent mit bestehendem Pattern
- Flags an bestehende Commands (`gmail send --list-drafts`): Unlogisch, vermischt Concerns

## Output Format

### Decision: Bestehende Output-Helper verwenden

**Rationale**: `print_success()`, `print_error()`, `print_json()` aus `utils/output.py` bieten konsistente Formatierung und JSON-Modus-Unterstützung.

**Draft List Output (Human)**:
```
Drafts (3):
  r1234567890  recipient@example.com  Subject line here
  r0987654321  another@example.com    Another subject
  r1111111111  third@example.com      Third email draft
```

**Draft List Output (JSON)**:
```json
{
    "drafts": [
        {
            "id": "r1234567890",
            "to": "recipient@example.com",
            "subject": "Subject line here",
            "snippet": "Preview text..."
        }
    ],
    "count": 3
}
```

## Summary

Alle Recherche-Fragen sind geklärt. Keine NEEDS CLARIFICATION Punkte verbleiben.

| Topic | Decision |
|-------|----------|
| API | Gmail API v1 users.drafts Resource |
| Scopes | Bestehende gmail.compose ausreichend |
| Composition | Wiederverwenden von compose_email/compose_reply |
| Threading | threadId aus compose_reply übernehmen |
| Errors | Bestehende _execute_with_retry nutzen |
| CLI Pattern | Separater draft Typer App |
| Output | Bestehende utils/output.py Helper |
