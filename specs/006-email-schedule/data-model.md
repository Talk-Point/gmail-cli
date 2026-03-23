# Data Model: E-Mail Scheduling

**Feature**: 006-email-schedule
**Date**: 2026-01-02

## Entities

### ScheduledEmail

Repräsentiert eine zur Zustellung geplante E-Mail.

| Field | Type | Description |
|-------|------|-------------|
| draft_id | string | Gmail Draft ID (von API) |
| message_id | string | Gmail Message ID des Drafts |
| scheduled_time | datetime | Geplanter Versandzeitpunkt (UTC) |
| recipients | list[string] | Empfänger-Adressen |
| subject | string | Betreff |
| job_id | string (optional) | System-Job ID (at-job) |
| status | ScheduleStatus | Aktueller Status |
| created_at | datetime | Erstellungszeitpunkt |
| account | string (optional) | Gmail-Account falls Multi-Account |

### ScheduleStatus (Enum)

| Value | Description |
|-------|-------------|
| PENDING | Draft erstellt, wartet auf Versand |
| SENT | Erfolgreich versendet |
| FAILED | Versand fehlgeschlagen |
| CANCELLED | Vom Benutzer abgebrochen |

### ScheduleTime

Hilfsentität für Zeit-Parsing.

| Field | Type | Description |
|-------|------|-------------|
| raw_input | string | Original-Eingabe des Benutzers |
| parsed_time | datetime | Geparste Zeit (UTC) |
| timezone | string | Verwendete Zeitzone |
| is_relative | bool | True wenn relativ (z.B. "in 2 hours") |

## Relationships

```
ScheduledEmail
    └── has one → ScheduleTime (embedded, nicht persistent)
    └── references → Gmail Draft (via draft_id)
    └── managed by → System Job (via job_id, optional)
```

## State Transitions

```
[User runs --schedule]
        │
        ▼
    PENDING ──────────────────┐
        │                     │
        │ (scheduled time)    │ (user cancels)
        ▼                     ▼
      SENT               CANCELLED
        │
        │ (error)
        ▼
     FAILED
```

## Validation Rules

### ScheduledEmail
- `scheduled_time` MUSS in der Zukunft liegen
- `scheduled_time` MUSS innerhalb von 30 Tagen sein
- `recipients` MUSS mindestens einen Eintrag haben
- `draft_id` MUSS gültiges Gmail Draft ID Format haben

### ScheduleTime
- Unterstützte Formate:
  - ISO-8601: `YYYY-MM-DDTHH:MM`, `YYYY-MM-DD HH:MM`
  - Relativ: `in N minutes`, `in N hours`, `in N days`
  - Natural: `tomorrow HH:MM`, `next monday HH:MM`
- Zeit MUSS mindestens 1 Minute in der Zukunft liegen
- Zeit DARF nicht mehr als 30 Tage in der Zukunft liegen

## Storage Notes

- **Keine lokale Persistenz erforderlich**: Drafts werden in Gmail gespeichert
- **Job-Tracking optional**: System-Jobs (`at`) sind selbst-verwaltend
- **Kein lokaler State**: CLI ist stateless, nutzt Gmail als Source of Truth
