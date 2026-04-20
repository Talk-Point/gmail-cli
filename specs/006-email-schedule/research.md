# Research: E-Mail Scheduling

**Feature**: 006-email-schedule
**Date**: 2026-01-02

## Research Questions

### 1. Unterstützt die Gmail API natives E-Mail-Scheduling?

**Decision**: Nein - Gmail API bietet keine native Scheduling-Funktion

**Rationale**:
- Die Gmail Web-UI hat Scheduling seit 2019, aber diese Funktion ist nicht über die API zugänglich
- Die `messages.send` Methode hat keinen `scheduleTime` oder ähnlichen Parameter
- Google Issue Tracker zeigt Feature-Requests, aber keine Implementierung

**Alternatives considered**:
- Warten auf Gmail API Update: Nicht absehbar, Feature-Request seit 2019 offen
- Drittanbieter-Services (Boomerang, etc.): Widerspricht dem CLI-First Prinzip

**Sources**:
- [Gmail API Sending Guide](https://developers.google.com/gmail/api/guides/sending)
- [Gmail Community Discussion](https://support.google.com/mail/thread/5594544)
- [Google Issue Tracker #140922183](https://issuetracker.google.com/issues/140922183)

### 2. Welche Implementierungsstrategie ist für ein CLI-Tool geeignet?

**Decision**: Draft + System-Scheduler (at/cron) Ansatz

**Rationale**:
- E-Mail wird als Draft gespeichert (persistent in Gmail)
- System-Scheduler (`at` auf Unix, Task Scheduler auf Windows) triggert den Versand
- CLI bleibt einfach, nutzt bestehende OS-Funktionen
- Funktioniert auch wenn CLI nicht läuft (Scheduler ist persistent)

**Implementation approach**:
1. `--schedule` Parameter parst Zeitangabe
2. E-Mail wird als Draft mit Label/Metadata gespeichert
3. System-Job wird erstellt (`at` command oder alternative)
4. Job ruft `gmail draft send <draft-id>` zum geplanten Zeitpunkt auf

**Alternatives considered**:
- Daemon-Prozess: Zu komplex für ein CLI-Tool, widerspricht Simplicity-Prinzip
- Polling-basiert: Ressourcenverschwendung, unzuverlässig
- Nur Draft ohne Auto-Send: Schlechte UX, Benutzer muss manuell senden

### 3. Welche Zeitformate sollen unterstützt werden?

**Decision**: ISO-8601 + natürliche Sprache (begrenzt)

**Rationale**:
- ISO-8601 ist Standard und eindeutig: `2026-01-03T09:00`
- Natürliche Sprache für häufige Fälle: `tomorrow 09:00`, `in 2 hours`
- Python `dateutil` Bibliothek für Parsing

**Supported formats**:
- Absolut: `YYYY-MM-DD HH:MM`, `YYYY-MM-DDTHH:MM`
- Relativ: `in X minutes`, `in X hours`, `in X days`
- Natural: `tomorrow HH:MM`, `next monday HH:MM`

**Alternatives considered**:
- Nur ISO-8601: Zu strikt für CLI-Nutzung
- Vollständiges NLP: Zu komplex, fehleranfällig

### 4. Wie wird der System-Scheduler integriert?

**Decision**: `at` command auf Unix, Fallback auf Hinweis bei nicht-verfügbarem Scheduler

**Rationale**:
- `at` ist auf den meisten Unix-Systemen verfügbar
- Einfache Integration via subprocess
- Graceful Degradation: Wenn `at` nicht verfügbar, wird Draft erstellt mit Hinweis

**Implementation**:
```python
# Prüfe at-Verfügbarkeit
if shutil.which("at"):
    # Erstelle at-Job
    subprocess.run(["at", time_str], input=f"gmail draft send {draft_id}", ...)
else:
    # Fallback: Nur Draft erstellen mit Hinweis
    print("Hinweis: System-Scheduler nicht verfügbar. Draft wurde erstellt.")
```

**Alternatives considered**:
- Python APScheduler: Zusätzliche Dependency, widerspricht Simplicity
- Cron: Komplexere Einrichtung, nicht für einmalige Jobs geeignet
- systemd timer: Zu komplex für einzelne E-Mails

## Constraints Discovered

1. **Gmail API Limit**: Kein natives Scheduling
2. **System-Dependency**: Benötigt `at` command für automatischen Versand
3. **Offline-Limitation**: Computer muss zum Sendezeitpunkt laufen
4. **Max 30 Tage**: Obwohl technisch nicht limitiert (kein Gmail-Limit), begrenzen wir auf 30 Tage für UX

## Updated Technical Approach

```
User: gmail send --to x@x.com --subject "Test" --body "Hi" --schedule "tomorrow 09:00"

1. Parse schedule time → datetime
2. Validate: in future, within 30 days
3. Compose email message
4. Create Gmail draft via API
5. Schedule system job:
   - If `at` available: Create at-job
   - Else: Show warning + draft info
6. Confirm to user with scheduled time
```
