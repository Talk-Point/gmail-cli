# CLI Interface Contract: Gmail CLI Tool

**Feature Branch**: `001-gmail-cli`
**Date**: 2025-12-01

## Command Overview

```text
gmail
├── auth
│   ├── login      # OAuth-Authentifizierung starten
│   ├── logout     # Credentials löschen
│   └── status     # Authentifizierungsstatus anzeigen
├── search         # E-Mails suchen
├── read           # E-Mail lesen
├── send           # E-Mail senden
├── reply          # Auf E-Mail antworten
└── attachment
    ├── list       # Anhänge einer E-Mail auflisten
    └── download   # Anhänge herunterladen
```

## Global Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--help` | `-h` | flag | - | Hilfe anzeigen |
| `--version` | `-v` | flag | - | Version anzeigen |
| `--json` | - | flag | false | JSON-Ausgabe statt formatierter Text |

---

## Authentication Commands

### `gmail auth login`

Startet OAuth 2.0 Authentifizierung über Browser.

**Usage**: `gmail auth login [OPTIONS]`

**Options**: Keine

**Behavior**:
1. Prüft ob bereits authentifiziert
2. Falls ja: Fragt ob neu authentifizieren
3. Öffnet Browser mit Google OAuth Consent Screen
4. Startet lokalen HTTP-Server für Callback
5. Empfängt Authorization Code
6. Tauscht Code gegen Tokens
7. Speichert Tokens im System Keyring

**Output (success)**:
```text
✓ Erfolgreich authentifiziert als max.mustermann@gmail.com
```

**Output (--json)**:
```json
{
  "status": "authenticated",
  "email": "max.mustermann@gmail.com",
  "scopes": ["gmail.readonly", "gmail.send", "gmail.settings.basic"]
}
```

**Exit Codes**:
- `0`: Erfolg
- `1`: User hat Authentifizierung abgebrochen
- `2`: Netzwerkfehler

---

### `gmail auth logout`

Löscht gespeicherte Credentials.

**Usage**: `gmail auth logout`

**Options**: Keine

**Output (success)**:
```text
✓ Erfolgreich abgemeldet
```

**Exit Codes**:
- `0`: Erfolg (auch wenn keine Credentials vorhanden)

---

### `gmail auth status`

Zeigt aktuellen Authentifizierungsstatus.

**Usage**: `gmail auth status`

**Options**: Keine

**Output (authenticated)**:
```text
✓ Authentifiziert als max.mustermann@gmail.com
  Token gültig bis: 2025-12-01 15:30:00
```

**Output (not authenticated)**:
```text
✗ Nicht authentifiziert
  Führe 'gmail auth login' aus um dich anzumelden
```

**Output (--json)**:
```json
{
  "authenticated": true,
  "email": "max.mustermann@gmail.com",
  "token_expiry": "2025-12-01T15:30:00Z"
}
```

**Exit Codes**:
- `0`: Authentifiziert
- `1`: Nicht authentifiziert

---

## Search Command

### `gmail search`

Durchsucht E-Mails nach Kriterien.

**Usage**: `gmail search [QUERY] [OPTIONS]`

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `QUERY` | No | Suchbegriff (Gmail-Syntax) |

**Options**:
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--from` | `-f` | string | - | Absender filtern |
| `--to` | `-t` | string | - | Empfänger filtern |
| `--subject` | `-s` | string | - | Betreff filtern |
| `--label` | `-l` | string | - | Label filtern (z.B. INBOX, SENT) |
| `--after` | - | date | - | Nach Datum (YYYY-MM-DD) |
| `--before` | - | date | - | Vor Datum (YYYY-MM-DD) |
| `--has-attachment` | - | flag | false | Nur mit Anhängen |
| `--limit` | `-n` | int | 20 | Anzahl Ergebnisse |
| `--page` | `-p` | string | - | Page Token für Pagination |

**Output (table)**:
```text
ID               FROM                    SUBJECT                      DATE
─────────────────────────────────────────────────────────────────────────────
18c5a2b3d4e5f6a7 Max Mustermann         Meeting morgen               2025-12-01
18c5a2b3d4e5f6a8 Anna Schmidt           Re: Projektupdate            2025-11-30
18c5a2b3d4e5f6a9 GitHub                 [repo] New pull request      2025-11-30

Zeige 3 von ~150 Ergebnissen | Nächste Seite: gmail search --page=ABC123
```

**Output (--json)**:
```json
{
  "emails": [
    {
      "id": "18c5a2b3d4e5f6a7",
      "thread_id": "18c5a2b3d4e5f6a0",
      "from": "Max Mustermann <max@example.com>",
      "subject": "Meeting morgen",
      "date": "2025-12-01T10:30:00Z",
      "snippet": "Hallo, können wir das Meeting auf...",
      "has_attachments": false
    }
  ],
  "total_estimate": 150,
  "next_page_token": "ABC123"
}
```

**Exit Codes**:
- `0`: Erfolg (auch bei 0 Ergebnissen)
- `1`: Nicht authentifiziert
- `2`: Ungültige Suchparameter

---

## Read Command

### `gmail read`

Zeigt eine E-Mail vollständig an.

**Usage**: `gmail read <MESSAGE_ID>`

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `MESSAGE_ID` | Yes | Gmail Message ID |

**Options**: Keine (nur globale)

**Output (formatted)**:
```text
════════════════════════════════════════════════════════════════════════════
Von:     Max Mustermann <max@example.com>
An:      ich@gmail.com
Datum:   01.12.2025 10:30
Betreff: Meeting morgen
════════════════════════════════════════════════════════════════════════════

Hallo,

können wir das Meeting auf 14 Uhr verschieben?

Gruß
Max

────────────────────────────────────────────────────────────────────────────
Anhänge (2):
  📎 agenda.pdf (125.3 KB)
  📎 notes.docx (45.2 KB)

Download: gmail attachment download 18c5a2b3d4e5f6a7 agenda.pdf
```

**Output (--json)**:
```json
{
  "id": "18c5a2b3d4e5f6a7",
  "thread_id": "18c5a2b3d4e5f6a0",
  "from": "Max Mustermann <max@example.com>",
  "to": ["ich@gmail.com"],
  "cc": [],
  "date": "2025-12-01T10:30:00Z",
  "subject": "Meeting morgen",
  "body": "Hallo,\n\nkönnen wir das Meeting auf 14 Uhr verschieben?\n\nGruß\nMax",
  "attachments": [
    {"id": "att1", "filename": "agenda.pdf", "mime_type": "application/pdf", "size": 128307},
    {"id": "att2", "filename": "notes.docx", "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "size": 46285}
  ]
}
```

**Exit Codes**:
- `0`: Erfolg
- `1`: Nicht authentifiziert
- `2`: E-Mail nicht gefunden

---

## Send Commands

### `gmail send`

Sendet eine neue E-Mail.

**Usage**: `gmail send [OPTIONS]`

**Options**:
| Option | Short | Type | Required | Description |
|--------|-------|------|----------|-------------|
| `--to` | `-t` | string | Yes | Empfänger (mehrfach verwendbar) |
| `--cc` | `-c` | string | No | CC-Empfänger (mehrfach verwendbar) |
| `--bcc` | `-b` | string | No | BCC-Empfänger (mehrfach verwendbar) |
| `--subject` | `-s` | string | Yes | Betreff |
| `--body` | `-m` | string | Yes* | Nachrichtentext |
| `--body-file` | `-f` | path | Yes* | Nachricht aus Datei |
| `--attach` | `-a` | path | No | Dateianhang (mehrfach verwendbar) |
| `--signature` | - | flag | false | Gmail-Signatur anhängen |

*Entweder `--body` oder `--body-file` erforderlich

**Example**:
```bash
gmail send \
  --to anna@example.com \
  --cc team@example.com \
  --subject "Projektupdate" \
  --body "Hier ist das Update..." \
  --attach report.pdf \
  --signature
```

**Output (success)**:
```text
✓ E-Mail gesendet an anna@example.com
  Message-ID: 18c5a2b3d4e5f6b0
```

**Output (--json)**:
```json
{
  "status": "sent",
  "message_id": "18c5a2b3d4e5f6b0",
  "to": ["anna@example.com"],
  "cc": ["team@example.com"],
  "subject": "Projektupdate"
}
```

**Exit Codes**:
- `0`: Erfolg
- `1`: Nicht authentifiziert
- `2`: Validierungsfehler (ungültige E-Mail, fehlende Felder)
- `3`: Anhang zu groß (>25MB)
- `4`: Sendefehler

---

### `gmail reply`

Antwortet auf eine E-Mail im selben Thread.

**Usage**: `gmail reply <MESSAGE_ID> [OPTIONS]`

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `MESSAGE_ID` | Yes | ID der Original-E-Mail |

**Options**:
| Option | Short | Type | Required | Description |
|--------|-------|------|----------|-------------|
| `--body` | `-m` | string | Yes* | Antworttext |
| `--body-file` | `-f` | path | Yes* | Antwort aus Datei |
| `--attach` | `-a` | path | No | Dateianhang |
| `--all` | - | flag | false | Reply-All (alle Empfänger) |
| `--signature` | - | flag | false | Gmail-Signatur anhängen |

**Output (success)**:
```text
✓ Antwort gesendet an Max Mustermann <max@example.com>
  Thread: 18c5a2b3d4e5f6a0
```

**Exit Codes**: Wie `gmail send`

---

## Attachment Commands

### `gmail attachment list`

Listet Anhänge einer E-Mail auf.

**Usage**: `gmail attachment list <MESSAGE_ID>`

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `MESSAGE_ID` | Yes | Gmail Message ID |

**Output (table)**:
```text
FILENAME          SIZE       TYPE
───────────────────────────────────────────────
agenda.pdf        125.3 KB   application/pdf
notes.docx        45.2 KB    application/vnd...wordprocessingml.document

2 Anhänge | Download: gmail attachment download 18c5a2b3d4e5f6a7 <filename>
```

**Output (--json)**:
```json
{
  "message_id": "18c5a2b3d4e5f6a7",
  "attachments": [
    {"id": "att1", "filename": "agenda.pdf", "mime_type": "application/pdf", "size": 128307},
    {"id": "att2", "filename": "notes.docx", "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "size": 46285}
  ]
}
```

**Exit Codes**:
- `0`: Erfolg
- `1`: Nicht authentifiziert
- `2`: E-Mail nicht gefunden

---

### `gmail attachment download`

Lädt Anhänge herunter.

**Usage**: `gmail attachment download <MESSAGE_ID> [FILENAME] [OPTIONS]`

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `MESSAGE_ID` | Yes | Gmail Message ID |
| `FILENAME` | No* | Dateiname des Anhangs |

**Options**:
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--all` | `-a` | flag | false | Alle Anhänge herunterladen |
| `--output` | `-o` | path | . | Zielverzeichnis |

*`FILENAME` erforderlich wenn `--all` nicht gesetzt

**Example**:
```bash
# Einzelner Anhang
gmail attachment download 18c5a2b3d4e5f6a7 agenda.pdf

# Alle Anhänge in Verzeichnis
gmail attachment download 18c5a2b3d4e5f6a7 --all --output ./downloads/
```

**Output (success)**:
```text
✓ agenda.pdf heruntergeladen (125.3 KB)
  Gespeichert: ./agenda.pdf
```

**Output (--all)**:
```text
✓ 2 Anhänge heruntergeladen
  ./downloads/agenda.pdf (125.3 KB)
  ./downloads/notes.docx (45.2 KB)
```

**Exit Codes**:
- `0`: Erfolg
- `1`: Nicht authentifiziert
- `2`: E-Mail nicht gefunden
- `3`: Anhang nicht gefunden
- `4`: Schreibfehler (Berechtigungen, Speicherplatz)

---

## Error Output Format

Alle Fehler folgen einheitlichem Format:

**Formatted**:
```text
✗ Fehler: E-Mail nicht gefunden
  Message-ID '18c5a2b3invalid' existiert nicht oder wurde gelöscht.

  Tipp: Verwende 'gmail search' um gültige Message-IDs zu finden.
```

**JSON (--json)**:
```json
{
  "error": true,
  "code": "EMAIL_NOT_FOUND",
  "message": "E-Mail nicht gefunden",
  "details": "Message-ID '18c5a2b3invalid' existiert nicht oder wurde gelöscht."
}
```
