# Quickstart: Gmail CLI Tool

**Feature Branch**: `001-gmail-cli`
**Date**: 2025-12-01

## Installation

```bash
# Mit uv (empfohlen)
uv tool install gmail-cli

# Oder mit pipx
pipx install gmail-cli
```

## Setup

### 1. Authentifizierung

```bash
# Bei Gmail anmelden
gmail auth login
```

Dies öffnet deinen Browser für die Google OAuth-Authentifizierung. Melde dich mit deinem Google-Konto an und erlaube den Zugriff.

```text
✓ Erfolgreich authentifiziert als deine.email@gmail.com
```

### 2. Status prüfen

```bash
gmail auth status
```

```text
✓ Authentifiziert als deine.email@gmail.com
  Token gültig bis: 2025-12-01 15:30:00
```

## Grundlegende Verwendung

### E-Mails suchen

```bash
# Einfache Suche
gmail search "meeting"

# Mit Filtern
gmail search --from "chef@firma.de" --after 2025-11-01

# Nur ungelesene E-Mails
gmail search "is:unread"

# Mit Anhängen
gmail search --has-attachment --limit 10
```

### E-Mail lesen

```bash
# Aus der Suche die ID kopieren und lesen
gmail read 18c5a2b3d4e5f6a7
```

### E-Mail senden

```bash
# Einfache E-Mail
gmail send \
  --to empfaenger@example.com \
  --subject "Betreff" \
  --body "Nachrichtentext"

# Mit Anhang und Signatur
gmail send \
  --to empfaenger@example.com \
  --subject "Dokument" \
  --body "Im Anhang das Dokument." \
  --attach dokument.pdf \
  --signature
```

### Auf E-Mail antworten

```bash
# Antworten
gmail reply 18c5a2b3d4e5f6a7 --body "Danke für die Info!"

# Allen antworten
gmail reply 18c5a2b3d4e5f6a7 --all --body "Danke an alle!"
```

### Anhänge herunterladen

```bash
# Anhänge einer E-Mail anzeigen
gmail attachment list 18c5a2b3d4e5f6a7

# Einzelnen Anhang herunterladen
gmail attachment download 18c5a2b3d4e5f6a7 dokument.pdf

# Alle Anhänge herunterladen
gmail attachment download 18c5a2b3d4e5f6a7 --all --output ./downloads/
```

## Tipps

### JSON-Ausgabe für Scripting

```bash
# Alle Befehle unterstützen --json
gmail search "meeting" --json | jq '.emails[].subject'
```

### Gmail-Suchsyntax nutzen

```bash
# Gmail-native Suche funktioniert
gmail search "from:chef@firma.de subject:wichtig after:2025/11/01"
gmail search "has:attachment filename:pdf"
gmail search "in:inbox is:unread"
```

### Pagination

```bash
# Ergebnisse sind paginiert (Standard: 20)
gmail search "meeting" --limit 50

# Nächste Seite laden (Token aus vorheriger Ausgabe)
gmail search "meeting" --page ABC123DEF456
```

## Abmelden

```bash
gmail auth logout
```

## Hilfe

```bash
# Allgemeine Hilfe
gmail --help

# Hilfe zu einem Befehl
gmail search --help
gmail send --help
```

## Fehlerbehebung

### "Nicht authentifiziert"

```bash
# Erneut anmelden
gmail auth login
```

### "Token abgelaufen"

Tokens werden automatisch erneuert. Falls nicht:

```bash
gmail auth logout
gmail auth login
```

### "Rate Limit erreicht"

Das Tool versucht automatisch bis zu 3 Mal mit Wartezeit. Bei anhaltenden Problemen kurz warten und erneut versuchen.

## Nächste Schritte

- Vollständige CLI-Referenz: `gmail --help`
- Gmail-Suchsyntax: https://support.google.com/mail/answer/7190
