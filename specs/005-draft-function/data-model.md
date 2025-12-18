# Data Model: Draft-Funktion

**Feature**: 005-draft-function
**Date**: 2025-12-17

## Entities

### Draft

Ein E-Mail-Entwurf, der in Gmail gespeichert ist.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Eindeutige Draft-ID (Gmail-generiert, z.B. "r1234567890") |
| message_id | string | Yes | ID der zugehörigen Message |
| thread_id | string | No | Thread-ID für Reply-Drafts |
| to | list[string] | No | Empfänger-Adressen |
| cc | list[string] | No | CC-Empfänger |
| bcc | list[string] | No | BCC-Empfänger |
| subject | string | No | Betreffzeile |
| body | string | No | E-Mail-Text (Plain oder HTML) |
| snippet | string | No | Vorschautext (von Gmail generiert) |
| attachments | list[Attachment] | No | Anhänge |
| created_at | datetime | No | Erstellungszeitpunkt |

### Relationships

```
Draft (1) ─────── (1) Message
  │
  └── (0..1) ─── Thread (für Reply-Drafts)
```

- Ein Draft enthält genau eine Message
- Ein Reply-Draft ist mit einem Thread verknüpft
- Attachments werden als Teil der Message gespeichert

## State Transitions

```
[None] ──create_draft()──> [Draft Saved]
                               │
                               ├──send_draft()──> [Sent] ──> [Draft Deleted]
                               │
                               └──delete_draft()──> [Deleted]
```

**States**:
- **None**: Kein Draft existiert
- **Draft Saved**: Draft in Gmail gespeichert, editierbar
- **Sent**: Draft wurde gesendet (automatisch gelöscht)
- **Deleted**: Draft wurde manuell gelöscht

## Validation Rules

| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| V001 | id | Must exist for get/send/delete | DraftNotFoundError |
| V002 | to | At least one recipient for send | InvalidMessageError |
| V003 | subject | Non-empty recommended | Warning only |

## Python Dataclass (Optional)

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Draft:
    """Represents a Gmail draft."""
    id: str
    message_id: str
    thread_id: str | None = None
    to: list[str] | None = None
    cc: list[str] | None = None
    subject: str | None = None
    body: str | None = None
    snippet: str | None = None
    created_at: datetime | None = None
```

**Note**: Ein separates Draft-Modell ist optional. Die bestehende `Email` Dataclass kann für die Anzeige wiederverwendet werden, da die Struktur ähnlich ist. Die Draft-ID wird separat gehandhabt.

## API Response Mapping

**Gmail API → Draft**:
```python
def _parse_draft(api_response: dict, full_message: dict | None = None) -> Draft:
    """Parse Gmail API draft response to Draft object."""
    draft_id = api_response["id"]
    message = api_response.get("message", {})

    if full_message:
        # Für get_draft mit vollständigen Details
        headers = {h["name"]: h["value"] for h in full_message.get("payload", {}).get("headers", [])}
        return Draft(
            id=draft_id,
            message_id=message.get("id"),
            thread_id=message.get("threadId"),
            to=headers.get("To", "").split(", ") if headers.get("To") else None,
            subject=headers.get("Subject"),
            snippet=full_message.get("snippet"),
        )

    # Für list_drafts (nur IDs)
    return Draft(
        id=draft_id,
        message_id=message.get("id"),
        thread_id=message.get("threadId"),
    )
```
