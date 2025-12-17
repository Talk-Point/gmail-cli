# Quickstart: Draft-Funktion

**Feature**: 005-draft-function
**Date**: 2025-12-17

## Voraussetzungen

- gmail-cli installiert und authentifiziert (`gmail auth login`)
- Gmail-Account mit aktiviertem API-Zugriff

## Schnellstart

### 1. E-Mail als Entwurf speichern

```bash
# Neue E-Mail als Entwurf
gmail send \
  --to empfaenger@example.com \
  --subject "Meeting morgen" \
  --body "Hallo, können wir morgen telefonieren?" \
  --draft

# Output:
# Draft created.
#   Draft ID: r1234567890
```

### 2. Antwort als Entwurf speichern

```bash
# Antwort auf eine E-Mail als Entwurf
gmail reply msg123456 \
  --body "Danke für die Info, ich melde mich!" \
  --draft

# Output:
# Reply draft created.
#   Draft ID: r0987654321
#   Thread ID: thread789
```

### 3. Alle Entwürfe auflisten

```bash
gmail draft list

# Output:
# Drafts (2):
#   r1234567890  empfaenger@example.com  Meeting morgen
#   r0987654321  sender@example.com      Re: Ihre Anfrage
```

### 4. Entwurf anzeigen

```bash
gmail draft show r1234567890

# Output:
# Draft: r1234567890
#
# To: empfaenger@example.com
# Subject: Meeting morgen
#
# Hallo, können wir morgen telefonieren?
```

### 5. Entwurf senden

```bash
gmail draft send r1234567890

# Output:
# Draft sent successfully.
#   Message ID: msg789
#   Thread ID: thread456
```

### 6. Entwurf löschen

```bash
gmail draft delete r0987654321

# Output:
# Draft deleted.
```

## JSON-Output für Scripting

```bash
# Alle Entwürfe als JSON
gmail draft list --json

# Entwurf-Details als JSON
gmail draft show r1234567890 --json
```

## Multi-Account Support

```bash
# Entwurf für bestimmten Account
gmail send --to user@example.com --subject "Test" --body "Content" \
  --draft --account work@company.com

# Entwürfe eines bestimmten Accounts auflisten
gmail draft list --account work@company.com
```

## Typische Workflows

### Entwurf erstellen → überprüfen → senden

```bash
# 1. Entwurf erstellen
gmail send -t user@example.com -s "Wichtig" -b "Inhalt..." --draft
# → Draft ID: r123

# 2. Im Browser überprüfen (Gmail Entwürfe)
# ... oder ...
gmail draft show r123

# 3. Senden wenn zufrieden
gmail draft send r123
```

### Batch-Entwürfe mit Skript

```bash
#!/bin/bash
# Mehrere Entwürfe erstellen
for email in user1@example.com user2@example.com user3@example.com; do
  gmail send \
    --to "$email" \
    --subject "Newsletter" \
    --body-file newsletter.md \
    --draft
done

# Alle erstellten Entwürfe anzeigen
gmail draft list --json | jq '.drafts[].id'
```

## Fehlerbehandlung

```bash
# Nicht existierender Entwurf
gmail draft show invalid_id
# Error: Draft 'invalid_id' not found.

# Nicht authentifiziert
gmail draft list
# Error: Not authenticated. Run 'gmail auth login' first.
```
