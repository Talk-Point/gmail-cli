# Feature Specification: Draft-Funktion

**Feature Branch**: `005-draft-function`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "Draft-Funktion für gmail-cli - Entwürfe speichern statt senden (IT#13754)"
**GitHub Issue**: [Talk-Point/IT#13754](https://github.com/Talk-Point/IT/issues/13754)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - E-Mail als Entwurf speichern (Priority: P1)

Als Benutzer möchte ich beim Verfassen einer neuen E-Mail die Option haben, diese als Entwurf zu speichern statt sie direkt zu senden, damit ich die E-Mail vor dem Senden nochmal überprüfen kann.

**Why this priority**: Dies ist die Kernfunktionalität des Features. Ohne diese Fähigkeit gibt es keinen Mehrwert für Benutzer, die E-Mails vor dem Senden überprüfen möchten.

**Independent Test**: Kann vollständig getestet werden durch Ausführen von `gmail send --draft` und anschließende Überprüfung, ob der Entwurf im Gmail-Postfach erscheint.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer, **When** er `gmail send --to empfaenger@example.com --subject "Test" --body "Inhalt" --draft` ausführt, **Then** wird die E-Mail als Entwurf im Gmail-Konto gespeichert und nicht gesendet.
2. **Given** ein authentifizierter Benutzer, **When** er einen Entwurf erfolgreich erstellt, **Then** wird die Draft-ID und eine Bestätigungsmeldung angezeigt.
3. **Given** ein authentifizierter Benutzer mit mehreren Accounts, **When** er `gmail send --draft --account work@example.com` ausführt, **Then** wird der Entwurf im angegebenen Account gespeichert.

---

### User Story 2 - Antwort als Entwurf speichern (Priority: P1)

Als Benutzer möchte ich beim Beantworten einer E-Mail die Option haben, meine Antwort als Entwurf zu speichern, damit ich sie vor dem Senden überarbeiten kann.

**Why this priority**: Gleichrangig mit US1, da Antworten ein häufiger Anwendungsfall ist und der gleiche Nutzen (Überprüfung vor Senden) gilt.

**Independent Test**: Kann getestet werden durch Ausführen von `gmail reply <message-id> --draft` und Überprüfung, ob der Antwort-Entwurf im korrekten Thread erscheint.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer und eine existierende E-Mail, **When** er `gmail reply <message-id> --body "Antworttext" --draft` ausführt, **Then** wird die Antwort als Entwurf im gleichen Thread gespeichert.
2. **Given** ein authentifizierter Benutzer, **When** er `gmail reply <message-id> --all --draft` ausführt, **Then** werden alle ursprünglichen Empfänger in den Entwurf übernommen.

---

### User Story 3 - Entwürfe auflisten (Priority: P2)

Als Benutzer möchte ich alle meine gespeicherten Entwürfe auflisten können, damit ich einen Überblick über noch zu sendende E-Mails habe.

**Why this priority**: Wichtig für die Verwaltung von Entwürfen, aber nicht essentiell für die Kernfunktionalität.

**Independent Test**: Kann getestet werden durch Ausführen von `gmail draft list` und Überprüfung, ob vorhandene Entwürfe angezeigt werden.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer mit Entwürfen, **When** er `gmail draft list` ausführt, **Then** werden alle Entwürfe mit ID, Empfänger und Betreff angezeigt.
2. **Given** ein authentifizierter Benutzer ohne Entwürfe, **When** er `gmail draft list` ausführt, **Then** wird eine entsprechende Meldung angezeigt.
3. **Given** ein authentifizierter Benutzer, **When** er `gmail draft list --json` ausführt, **Then** wird die Liste im JSON-Format ausgegeben.

---

### User Story 4 - Entwurf anzeigen (Priority: P2)

Als Benutzer möchte ich den Inhalt eines bestimmten Entwurfs anzeigen können, damit ich ihn vor dem Senden überprüfen kann.

**Why this priority**: Ermöglicht die Überprüfung von Entwürfen vor dem Senden.

**Independent Test**: Kann getestet werden durch Ausführen von `gmail draft show <draft-id>` und Überprüfung der Ausgabe.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer und ein existierender Entwurf, **When** er `gmail draft show <draft-id>` ausführt, **Then** werden alle Details des Entwurfs (Empfänger, Betreff, Text, Anhänge) angezeigt.
2. **Given** ein authentifizierter Benutzer, **When** er `gmail draft show <ungültige-id>` ausführt, **Then** wird eine verständliche Fehlermeldung angezeigt.

---

### User Story 5 - Entwurf senden (Priority: P2)

Als Benutzer möchte ich einen gespeicherten Entwurf direkt senden können, damit ich fertige Entwürfe einfach absenden kann.

**Why this priority**: Vervollständigt den Workflow von Entwurf zu gesendeter E-Mail.

**Independent Test**: Kann getestet werden durch Ausführen von `gmail draft send <draft-id>` und Überprüfung, ob die E-Mail im Gesendet-Ordner erscheint.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer und ein existierender Entwurf, **When** er `gmail draft send <draft-id>` ausführt, **Then** wird der Entwurf gesendet und aus der Entwürfe-Liste entfernt.
2. **Given** ein authentifizierter Benutzer, **When** er einen Entwurf erfolgreich sendet, **Then** werden Message-ID und Thread-ID der gesendeten E-Mail angezeigt.

---

### User Story 6 - Entwurf löschen (Priority: P3)

Als Benutzer möchte ich Entwürfe löschen können, die ich nicht mehr benötige.

**Why this priority**: Nice-to-have Funktion für Aufräumarbeiten, aber nicht essentiell.

**Independent Test**: Kann getestet werden durch Ausführen von `gmail draft delete <draft-id>` und Überprüfung, dass der Entwurf nicht mehr existiert.

**Acceptance Scenarios**:

1. **Given** ein authentifizierter Benutzer und ein existierender Entwurf, **When** er `gmail draft delete <draft-id>` ausführt, **Then** wird der Entwurf dauerhaft gelöscht.
2. **Given** ein authentifizierter Benutzer, **When** er einen Entwurf erfolgreich löscht, **Then** wird eine Bestätigung angezeigt.

---

### Edge Cases

- Was passiert, wenn der Benutzer `--draft` zusammen mit ungültigen Empfänger-Adressen verwendet? (Entwurf wird trotzdem gespeichert, Validierung erst beim Senden)
- Wie verhält sich das System bei Netzwerkfehlern während der Entwurf-Erstellung? (Retry-Logik wie bei send)
- Was passiert, wenn der Benutzer versucht, einen bereits gelöschten Entwurf zu senden? (Verständliche Fehlermeldung)
- Wie werden große Anhänge in Entwürfen behandelt? (Gleiche Limits wie bei send)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUSS eine `--draft` Option für den `send` Command bereitstellen
- **FR-002**: System MUSS eine `--draft` Option für den `reply` Command bereitstellen
- **FR-003**: System MUSS einen `draft list` Subcommand bereitstellen, der alle Entwürfe auflistet
- **FR-004**: System MUSS einen `draft show <id>` Subcommand bereitstellen, der einen Entwurf anzeigt
- **FR-005**: System MUSS einen `draft send <id>` Subcommand bereitstellen, der einen Entwurf sendet
- **FR-006**: System MUSS einen `draft delete <id>` Subcommand bereitstellen, der einen Entwurf löscht
- **FR-007**: Alle Draft-Commands MÜSSEN Multi-Account Support unterstützen (via `--account` Flag)
- **FR-008**: Alle Draft-Commands MÜSSEN JSON-Output unterstützen (via `--json` Flag)
- **FR-009**: Bei `reply --draft` MUSS der Entwurf mit dem Original-Thread verknüpft werden
- **FR-010**: System MUSS aussagekräftige Fehlermeldungen bei nicht gefundenen Entwürfen anzeigen

### Key Entities

- **Draft**: Ein nicht gesendeter E-Mail-Entwurf mit ID, Nachrichteninhalt, Empfängern, Betreff und optionalen Anhängen
- **Thread**: Eine E-Mail-Konversation, mit der Antwort-Entwürfe verknüpft werden

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Benutzer können eine E-Mail als Entwurf in unter 5 Sekunden speichern (exkl. Eingabezeit)
- **SC-002**: Benutzer können alle ihre Entwürfe mit einem einzigen Befehl auflisten
- **SC-003**: Der gespeicherte Entwurf erscheint sofort im Gmail-Webinterface unter "Entwürfe"
- **SC-004**: Antwort-Entwürfe erscheinen im korrekten E-Mail-Thread
- **SC-005**: 100% der bestehenden send/reply-Funktionalität bleibt unverändert (keine Breaking Changes)

## Assumptions

- Benutzer ist bereits authentifiziert (OAuth-Flow abgeschlossen)
- Gmail API Draft-Endpunkte sind verfügbar und funktional
- Bestehende OAuth-Scopes (`gmail.compose` oder `gmail.modify`) sind ausreichend für Draft-Operationen
- E-Mail-Validierung erfolgt beim Senden, nicht beim Speichern als Entwurf
