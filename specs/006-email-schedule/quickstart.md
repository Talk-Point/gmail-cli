# Quickstart: E-Mail Scheduling

## Voraussetzungen

- gmail-cli installiert und authentifiziert (`gmail auth login`)
- `at` command verfügbar für automatischen Versand (optional)

## Basis-Verwendung

### E-Mail für morgen planen

```bash
gmail send \
  --to colleague@example.com \
  --subject "Morgendliches Update" \
  --body "Hier ist das versprochene Update." \
  --schedule "tomorrow 09:00"
```

### E-Mail in 2 Stunden senden

```bash
gmail send \
  --to client@example.com \
  --subject "Follow-up" \
  --body "Wie besprochen..." \
  --schedule "in 2 hours"
```

### Antwort zeitgesteuert senden

```bash
gmail reply 18c1234abcd5678 \
  --body "Danke für Ihre Nachricht!" \
  --schedule "tomorrow 08:00"
```

## Zeitformate

| Format | Beispiel | Beschreibung |
|--------|----------|--------------|
| Datum + Zeit | `2026-01-15 09:00` | Exakter Zeitpunkt |
| ISO-8601 | `2026-01-15T09:00` | Standardformat |
| Relativ (Minuten) | `in 30 minutes` | In 30 Minuten |
| Relativ (Stunden) | `in 2 hours` | In 2 Stunden |
| Relativ (Tage) | `in 3 days` | In 3 Tagen |
| Tomorrow | `tomorrow 09:00` | Morgen um 09:00 |

## JSON-Ausgabe

```bash
gmail send \
  --to x@x.com \
  --subject "Test" \
  --body "Hi" \
  --schedule "tomorrow 09:00" \
  --json
```

Ausgabe:
```json
{
  "status": "scheduled",
  "scheduled_time": "2026-01-03T09:00:00+01:00",
  "draft_id": "r1234567890"
}
```

## Fehlerbehebung

### "System-Scheduler nicht verfügbar"

Der `at` command ist nicht installiert. Die E-Mail wird als Draft gespeichert.

**Lösung 1**: `at` installieren
```bash
# Debian/Ubuntu
sudo apt install at

# macOS
brew install at
```

**Lösung 2**: Draft manuell senden
```bash
gmail draft send r1234567890
```

### "Zeitpunkt muss in der Zukunft liegen"

Der angegebene Zeitpunkt liegt in der Vergangenheit.

### "Maximale Planungszeit: 30 Tage"

E-Mails können maximal 30 Tage im Voraus geplant werden.

## Tipps

- Zeitzone wird automatisch aus dem System übernommen
- Geplante E-Mails können über `gmail draft list` eingesehen werden
- Zum Abbrechen: `gmail draft delete <draft-id>`
