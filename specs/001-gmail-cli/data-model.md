# Data Model: Gmail CLI Tool

**Feature Branch**: `001-gmail-cli`
**Date**: 2025-12-01

## Entities

### Email

Repräsentiert eine E-Mail-Nachricht aus Gmail.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Email:
    """Eine Gmail-Nachricht mit allen relevanten Metadaten."""

    id: str                          # Gmail Message ID (z.B. "18c5a2b3d4e5f6a7")
    thread_id: str                   # Gmail Thread ID für Konversationen
    subject: str                     # Betreff der E-Mail
    sender: str                      # Absender (z.B. "Max Mustermann <max@example.com>")
    recipients: list[str]            # To-Empfänger
    cc: list[str] = field(default_factory=list)   # CC-Empfänger
    bcc: list[str] = field(default_factory=list)  # BCC-Empfänger
    date: datetime                   # Sende-/Empfangsdatum
    body_text: str = ""              # Plain-Text Body
    body_html: str = ""              # HTML Body (falls vorhanden)
    snippet: str = ""                # Vorschau-Text (max 200 chars)
    labels: list[str] = field(default_factory=list)  # Gmail Labels
    attachments: list["Attachment"] = field(default_factory=list)
    is_read: bool = True             # Gelesen-Status
    message_id: str = ""             # RFC 2822 Message-ID Header
    references: list[str] = field(default_factory=list)  # References Header für Threading

    @property
    def has_attachments(self) -> bool:
        """Prüft ob E-Mail Anhänge hat."""
        return len(self.attachments) > 0

    @property
    def sender_name(self) -> str:
        """Extrahiert nur den Namen aus dem Absender."""
        if "<" in self.sender:
            return self.sender.split("<")[0].strip().strip('"')
        return self.sender

    @property
    def sender_email(self) -> str:
        """Extrahiert nur die E-Mail-Adresse aus dem Absender."""
        if "<" in self.sender and ">" in self.sender:
            return self.sender.split("<")[1].split(">")[0]
        return self.sender
```

### Attachment

Repräsentiert einen E-Mail-Anhang.

```python
@dataclass
class Attachment:
    """Ein Anhang einer Gmail-Nachricht."""

    id: str                          # Gmail Attachment ID
    message_id: str                  # Zugehörige Message ID
    filename: str                    # Dateiname (z.B. "document.pdf")
    mime_type: str                   # MIME-Type (z.B. "application/pdf")
    size: int                        # Größe in Bytes

    @property
    def size_human(self) -> str:
        """Menschenlesbare Größenangabe."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        else:
            return f"{self.size / (1024 * 1024):.1f} MB"
```

### Credentials

Repräsentiert die OAuth 2.0 Authentifizierungsdaten.

```python
@dataclass
class Credentials:
    """OAuth 2.0 Credentials für Gmail API Zugriff."""

    access_token: str                # Kurzlebiger Access Token (1h)
    refresh_token: str               # Langlebiger Refresh Token
    token_uri: str                   # Google Token Endpoint
    client_id: str                   # OAuth Client ID
    client_secret: str               # OAuth Client Secret
    scopes: list[str]                # Gewährte Scopes
    expiry: datetime                 # Access Token Ablaufzeit

    @property
    def is_expired(self) -> bool:
        """Prüft ob Access Token abgelaufen ist."""
        return datetime.utcnow() >= self.expiry

    @property
    def needs_refresh(self) -> bool:
        """Prüft ob Token bald abläuft (< 5 min)."""
        from datetime import timedelta
        return datetime.utcnow() >= (self.expiry - timedelta(minutes=5))
```

### Signature

Repräsentiert eine Gmail-Signatur.

```python
@dataclass
class Signature:
    """Gmail-Signatur eines Users."""

    send_as_email: str               # E-Mail-Adresse für die Signatur gilt
    signature_html: str              # HTML-formatierte Signatur
    is_default: bool = False         # Standard-Signatur für neue E-Mails

    @property
    def signature_text(self) -> str:
        """Plain-Text Version der Signatur."""
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        return h.handle(self.signature_html).strip()
```

### SearchResult

Wrapper für paginierte Suchergebnisse.

```python
@dataclass
class SearchResult:
    """Paginiertes Suchergebnis."""

    emails: list[Email]              # Gefundene E-Mails
    total_estimate: int              # Geschätzte Gesamtanzahl
    next_page_token: Optional[str]   # Token für nächste Seite (None = letzte Seite)
    query: str                       # Ursprüngliche Suchanfrage
```

## Entity Relationships

```text
┌─────────────────┐
│     Email       │
├─────────────────┤
│ id (PK)         │
│ thread_id       │───────┐
│ subject         │       │  Emails im selben Thread
│ sender          │       │  teilen thread_id
│ recipients[]    │◄──────┘
│ date            │
│ body_text       │
│ body_html       │
│ attachments[] ──┼──────────┐
└─────────────────┘          │
                             │ 1:n
                             ▼
                    ┌─────────────────┐
                    │   Attachment    │
                    ├─────────────────┤
                    │ id (PK)         │
                    │ message_id (FK) │
                    │ filename        │
                    │ mime_type       │
                    │ size            │
                    └─────────────────┘

┌─────────────────┐
│   Credentials   │
├─────────────────┤
│ access_token    │         ┌─────────────────┐
│ refresh_token   │         │    Signature    │
│ expiry          │         ├─────────────────┤
│ scopes[]        │         │ send_as_email   │
└─────────────────┘         │ signature_html  │
        │                   │ is_default      │
        │                   └─────────────────┘
        │
        └──── Stored in System Keyring
              (not persisted as file)
```

## Validation Rules

### Email
- `id`: Nicht leer, alphanumerisch
- `thread_id`: Nicht leer, alphanumerisch
- `subject`: Kann leer sein (kein Subject)
- `sender`: Muss gültiges E-Mail-Format enthalten
- `recipients`: Mindestens ein Empfänger beim Senden
- `date`: Gültiges datetime
- `attachments`: Jeder Anhang < 25MB

### Attachment
- `filename`: Nicht leer, gültige Dateiname-Zeichen
- `size`: >= 0, max 25MB (Gmail Limit)
- `mime_type`: Gültiger MIME-Type String

### Credentials
- `access_token`: Nicht leer
- `refresh_token`: Nicht leer
- `scopes`: Mindestens ein Scope erforderlich

## State Transitions

### Email Lifecycle (aus CLI-Perspektive)

```text
                    ┌─────────────┐
                    │   SEARCH    │
                    │  (listing)  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    READ     │
                    │  (details)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌───────────┐ ┌───────────┐ ┌───────────┐
       │  REPLY    │ │ DOWNLOAD  │ │  (done)   │
       │           │ │ ATTACHMENT│ │           │
       └───────────┘ └───────────┘ └───────────┘
```

### Authentication State

```text
    ┌──────────────────┐
    │  NOT_AUTHENTICATED│◄─────────────────┐
    └────────┬─────────┘                   │
             │ gmail auth login            │ gmail auth logout
             ▼                             │
    ┌──────────────────┐                   │
    │  OAUTH_FLOW      │                   │
    │  (browser open)  │                   │
    └────────┬─────────┘                   │
             │ user grants access          │
             ▼                             │
    ┌──────────────────┐                   │
    │  AUTHENTICATED   │───────────────────┘
    │  (tokens stored) │
    └────────┬─────────┘
             │ token expires
             ▼
    ┌──────────────────┐
    │  TOKEN_REFRESH   │──┐
    │  (automatic)     │  │ success
    └────────┬─────────┘  │
             │ failure    │
             ▼            │
    ┌──────────────────┐  │
    │  RE-AUTH NEEDED  │  │
    └──────────────────┘  │
             │            │
             └────────────┘
```

## Gmail API Mapping

| Entity Field | Gmail API Field |
|--------------|-----------------|
| Email.id | messages.id |
| Email.thread_id | messages.threadId |
| Email.subject | payload.headers[Subject] |
| Email.sender | payload.headers[From] |
| Email.recipients | payload.headers[To] |
| Email.date | internalDate |
| Email.body_text | payload.parts[text/plain] |
| Email.body_html | payload.parts[text/html] |
| Email.snippet | snippet |
| Email.labels | labelIds |
| Attachment.id | payload.parts[].body.attachmentId |
| Attachment.filename | payload.parts[].filename |
| Attachment.mime_type | payload.parts[].mimeType |
| Attachment.size | payload.parts[].body.size |
