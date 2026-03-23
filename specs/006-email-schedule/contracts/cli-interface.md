# CLI Interface Contract: E-Mail Scheduling

**Feature**: 006-email-schedule
**Date**: 2026-01-02

## Modified Commands

### `gmail send`

Erweiterung des bestehenden `send` Befehls um `--schedule` Parameter.

```
gmail send --to <email> --subject <text> --body <text> [--schedule <time>] [options]
```

#### New Parameter

| Parameter | Short | Type | Required | Description |
|-----------|-------|------|----------|-------------|
| `--schedule` | `-S` | string | No | Zeitpunkt für geplanten Versand |

#### Schedule Time Formats

```bash
# Absolute Zeit
--schedule "2026-01-15 09:00"
--schedule "2026-01-15T09:00"

# Relative Zeit
--schedule "in 30 minutes"
--schedule "in 2 hours"
--schedule "in 3 days"

# Natural Language
--schedule "tomorrow 09:00"
--schedule "tomorrow 14:30"
```

#### Output (Success - Human)

```
E-Mail geplant!
Versand:      15. Januar 2026, 09:00 Uhr
Empfänger:    recipient@example.com
Betreff:      Test-E-Mail
Draft-ID:     r1234567890
```

#### Output (Success - JSON)

```json
{
  "status": "scheduled",
  "scheduled_time": "2026-01-15T09:00:00+01:00",
  "draft_id": "r1234567890",
  "message_id": "18d1234abcd5678",
  "recipients": ["recipient@example.com"],
  "subject": "Test-E-Mail",
  "job_id": "at-12345"
}
```

#### Output (Scheduler Unavailable - Human)

```
E-Mail als Entwurf gespeichert!
Draft-ID:     r1234567890

⚠ Hinweis: System-Scheduler nicht verfügbar.
  Der Entwurf muss manuell versendet werden:
  gmail draft send r1234567890

  Geplanter Zeitpunkt war: 15. Januar 2026, 09:00 Uhr
```

#### Error Cases

| Error | Exit Code | Message |
|-------|-----------|---------|
| Invalid time format | 1 | `Ungültiges Zeitformat. Beispiele: "2026-01-15 09:00", "in 2 hours", "tomorrow 09:00"` |
| Time in past | 1 | `Zeitpunkt muss in der Zukunft liegen` |
| Time > 30 days | 1 | `Maximale Planungszeit: 30 Tage` |
| Draft creation failed | 1 | `Entwurf konnte nicht erstellt werden: <details>` |

---

### `gmail reply`

Erweiterung des bestehenden `reply` Befehls um `--schedule` Parameter.

```
gmail reply <message-id> --body <text> [--schedule <time>] [options]
```

#### New Parameter

Identisch zu `gmail send --schedule`.

#### Output

Identisch zu `gmail send`, mit zusätzlichem `replied_to` Feld in JSON-Output:

```json
{
  "status": "scheduled",
  "scheduled_time": "2026-01-15T09:00:00+01:00",
  "draft_id": "r1234567890",
  "replied_to": "18c1234abcd5678"
}
```

---

## Interaction with Existing Options

### `--schedule` + `--draft`

`--schedule` hat Vorrang. Die E-Mail wird als Draft mit geplantem Versand gespeichert.

```bash
# --draft wird ignoriert wenn --schedule angegeben
gmail send --to x@x.com --subject "Test" --body "Hi" --schedule "tomorrow 09:00" --draft
# Ergebnis: Geplante E-Mail (nicht nur Draft)
```

### `--schedule` + `--account`

Funktioniert wie erwartet - E-Mail wird vom angegebenen Account geplant.

```bash
gmail send --to x@x.com --subject "Test" --body "Hi" --schedule "tomorrow 09:00" --account work@company.com
```

### `--schedule` + Attachments

Vollständig unterstützt.

```bash
gmail send --to x@x.com --subject "Report" --body "Siehe Anhang" --attach report.pdf --schedule "monday 09:00"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | E-Mail erfolgreich geplant |
| 1 | Fehler (siehe Error Cases) |
