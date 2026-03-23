# Feature Specification: E-Mail Scheduling

**Feature Branch**: `006-email-schedule`
**Created**: 2026-01-02
**Status**: Draft
**Input**: User description: "Implementiere eine Schedule-Funktion für den E-Mail-Versand in gmail-cli. Ein neuer --schedule Parameter soll beim send-Befehl hinzugefügt werden, der es ermöglicht, E-Mails zeitgesteuert zu versenden. Der Parameter soll ein Datum/Uhrzeit akzeptieren und die Gmail API Scheduling-Funktionen nutzen."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - E-Mail für späteren Versand planen (Priority: P1)

Als Benutzer möchte ich eine E-Mail verfassen und einen Zeitpunkt angeben, zu dem diese automatisch versendet werden soll, damit ich E-Mails vorbereiten kann, die zu einem optimalen Zeitpunkt beim Empfänger ankommen.

**Why this priority**: Dies ist die Kernfunktionalität des Features. Ohne diese Grundfunktion hat das gesamte Feature keinen Nutzen.

**Independent Test**: Kann vollständig getestet werden, indem eine E-Mail mit `--schedule` Parameter gesendet wird und überprüft wird, ob sie zum geplanten Zeitpunkt beim Empfänger ankommt.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer, **When** er `gmail send --to recipient@example.com --subject "Test" --body "Hallo" --schedule "2026-01-03 09:00"` ausführt, **Then** wird die E-Mail als geplant gespeichert und erst am 3. Januar 2026 um 09:00 Uhr versendet.

2. **Given** ein authentifizierter Benutzer, **When** er eine E-Mail mit `--schedule "in 2 hours"` plant, **Then** wird die E-Mail 2 Stunden nach dem Befehl versendet.

3. **Given** ein authentifizierter Benutzer, **When** er eine E-Mail mit `--schedule "tomorrow 08:00"` plant, **Then** wird die E-Mail am nächsten Tag um 08:00 Uhr versendet.

---

### User Story 2 - Feedback bei erfolgreicher Planung (Priority: P1)

Als Benutzer möchte ich eine Bestätigung erhalten, wenn meine E-Mail erfolgreich geplant wurde, damit ich sicher sein kann, dass der Versand zum gewünschten Zeitpunkt erfolgt.

**Why this priority**: Ohne Feedback weiß der Benutzer nicht, ob die Planung erfolgreich war - essentiell für die Benutzerfreundlichkeit.

**Independent Test**: Kann getestet werden, indem nach einem erfolgreichen Schedule-Befehl die Ausgabe auf Bestätigungsmeldung und geplanten Zeitpunkt überprüft wird.

**Acceptance Scenarios**:

1. **Given** eine erfolgreich geplante E-Mail, **When** der Befehl abgeschlossen ist, **Then** zeigt das System eine Erfolgsmeldung mit dem geplanten Versandzeitpunkt an.

2. **Given** JSON-Modus ist aktiviert, **When** eine E-Mail erfolgreich geplant wird, **Then** enthält die JSON-Ausgabe den Status, die Message-ID und den geplanten Zeitpunkt im ISO-8601 Format.

---

### User Story 3 - Fehlerbehandlung bei ungültigen Zeitangaben (Priority: P2)

Als Benutzer möchte ich bei ungültigen Zeitangaben eine verständliche Fehlermeldung erhalten, damit ich den Fehler korrigieren und die E-Mail erneut planen kann.

**Why this priority**: Wichtig für eine gute Benutzererfahrung, aber nicht kritisch für die Grundfunktionalität.

**Independent Test**: Kann getestet werden, indem ungültige Zeitformate eingegeben werden und die Fehlermeldungen überprüft werden.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer, **When** er eine E-Mail mit `--schedule "gestern"` plant (Zeitpunkt in der Vergangenheit), **Then** zeigt das System eine Fehlermeldung an, dass der Zeitpunkt in der Zukunft liegen muss.

2. **Given** ein authentifizierter Benutzer, **When** er eine E-Mail mit `--schedule "abc123"` plant (ungültiges Format), **Then** zeigt das System eine Fehlermeldung mit Beispielen für gültige Formate an.

3. **Given** ein authentifizierter Benutzer, **When** er eine E-Mail mehr als 30 Tage in der Zukunft plant, **Then** zeigt das System eine Fehlermeldung an, dass die maximale Planungszeit 30 Tage beträgt.

---

### User Story 4 - Schedule mit Reply-Befehl (Priority: P2)

Als Benutzer möchte ich auch Antworten auf E-Mails zeitgesteuert versenden können, damit ich auf E-Mails zu einem passenden Zeitpunkt antworten kann.

**Why this priority**: Erweitert die Funktionalität auf den Reply-Befehl, aber die Kern-Schedule-Funktion beim Send-Befehl hat höhere Priorität.

**Independent Test**: Kann getestet werden, indem eine Reply mit `--schedule` Parameter gesendet wird und die geplante Antwort überprüft wird.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer und eine vorhandene E-Mail, **When** er `gmail reply MESSAGE_ID --body "Danke!" --schedule "tomorrow 10:00"` ausführt, **Then** wird die Antwort für den nächsten Tag um 10:00 Uhr geplant.

---

### Edge Cases

- Was passiert, wenn der Benutzer die Zeitzone nicht angibt? Das System verwendet die lokale Zeitzone des Benutzers.
- Was passiert, wenn die geplante E-Mail vor dem Versand abgebrochen werden soll? Der Benutzer kann geplante E-Mails über das Draft-Management stornieren.
- Was passiert bei Netzwerkproblemen während der Planung? Das System zeigt eine entsprechende Fehlermeldung und die E-Mail wird nicht geplant.
- Was passiert, wenn --schedule und --draft gleichzeitig verwendet werden? --schedule hat Vorrang, da eine geplante E-Mail technisch ein Draft mit Versandzeitpunkt ist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUSS einen `--schedule` Parameter für den `send` Befehl bereitstellen
- **FR-002**: System MUSS einen `--schedule` Parameter für den `reply` Befehl bereitstellen
- **FR-003**: System MUSS absolute Zeitangaben im Format "YYYY-MM-DD HH:MM" akzeptieren
- **FR-004**: System MUSS relative Zeitangaben wie "in X hours", "in X minutes", "tomorrow HH:MM" akzeptieren
- **FR-005**: System MUSS Zeitangaben in der Vergangenheit ablehnen und eine Fehlermeldung anzeigen
- **FR-006**: System MUSS nach erfolgreicher Planung eine Bestätigung mit dem geplanten Zeitpunkt anzeigen
- **FR-007**: System MUSS im JSON-Modus strukturierte Ausgaben mit Status und geplantem Zeitpunkt liefern
- **FR-008**: System MUSS Zeitangaben mehr als 30 Tage in der Zukunft ablehnen (Gmail API Limit)
- **FR-009**: System MUSS die lokale Zeitzone des Benutzers für Zeitangaben ohne explizite Zeitzone verwenden

### Key Entities

- **Scheduled Email**: Eine E-Mail mit zugeordnetem Versandzeitpunkt, die bis zum geplanten Zeitpunkt als Draft gespeichert wird
- **Schedule Time**: Der geplante Versandzeitpunkt als Unix-Timestamp in Millisekunden für die Gmail API

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Benutzer können E-Mails innerhalb von 5 Sekunden erfolgreich für späteren Versand planen
- **SC-002**: Geplante E-Mails werden innerhalb von 2 Minuten nach dem geplanten Zeitpunkt versendet
- **SC-003**: 100% der ungültigen Zeitangaben werden mit verständlichen Fehlermeldungen abgelehnt
- **SC-004**: Benutzer erhalten bei jeder erfolgreichen Planung eine Bestätigung mit dem exakten Versandzeitpunkt
- **SC-005**: Die Schedule-Funktion ist sowohl für neue E-Mails als auch für Antworten verfügbar

## Assumptions

- Die Gmail API Scheduled Send Funktion ist verfügbar und stabil
- Benutzer haben eine funktionierende Internetverbindung zum Zeitpunkt der Planung
- Das System hat Zugriff auf die lokale Zeitzone des Benutzers
- Die maximale Planungszeit von 30 Tagen (Gmail API Limit) ist für die meisten Anwendungsfälle ausreichend
