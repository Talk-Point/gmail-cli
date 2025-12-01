# Feature Specification: Gmail CLI Tool

**Feature Branch**: `001-gmail-cli`
**Created**: 2025-12-01
**Status**: Draft
**Input**: Gmail CLI Tool für Entwickler mit Python/uv - Authentifizierung, Suche mit Pagination, Mails lesen/senden mit Signatur-Support, Attachments

## Scope

**In-Scope**: Authentifizierung, E-Mail-Suche, E-Mail lesen, E-Mail senden (mit Signatur), Attachments herunterladen

**Out-of-Scope**: Label-Management, Drafts/Entwürfe, Google Kalender-Integration, Google Kontakte-Verwaltung

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gmail Authentication (Priority: P1)

Als Entwickler möchte ich mich einmalig bei Gmail authentifizieren, damit ich das CLI-Tool sicher nutzen kann, ohne bei jeder Aktion erneut Zugangsdaten eingeben zu müssen.

**Why this priority**: Ohne Authentifizierung ist keine weitere Funktionalität nutzbar. Dies ist die fundamentale Basis für alle anderen Features.

**Independent Test**: Kann vollständig getestet werden durch `gmail auth login`, Durchführung des OAuth-Flows und Verifizierung, dass der Token sicher gespeichert wird.

**Acceptance Scenarios**:

1. **Given** der Nutzer hat das CLI installiert und ist nicht authentifiziert, **When** er `gmail auth login` ausführt, **Then** öffnet sich der Browser für den OAuth-Flow und nach erfolgreicher Anmeldung wird eine Bestätigung angezeigt
2. **Given** der Nutzer ist bereits authentifiziert, **When** er `gmail auth login` erneut ausführt, **Then** wird er gefragt, ob er sich neu authentifizieren möchte oder die bestehende Session beibehalten will
3. **Given** der Nutzer ist authentifiziert, **When** er `gmail auth status` ausführt, **Then** sieht er den aktuellen Authentifizierungsstatus und die verbundene E-Mail-Adresse
4. **Given** der Nutzer möchte sich abmelden, **When** er `gmail auth logout` ausführt, **Then** werden die gespeicherten Credentials gelöscht und der Nutzer ist abgemeldet

---

### User Story 2 - Einfache Installation (Priority: P1)

Als Entwickler möchte ich das Tool einfach über uv installieren können, damit ich schnell produktiv werde.

**Why this priority**: Ohne einfache Installation kann das Tool nicht genutzt werden. Dies ist Voraussetzung für alle anderen Features.

**Independent Test**: Kann getestet werden durch `uv tool install gmail-cli` und Ausführung von `gmail --version`.

**Acceptance Scenarios**:

1. **Given** ein Entwickler hat uv installiert, **When** er `uv tool install gmail-cli` ausführt, **Then** wird das Tool global verfügbar installiert
2. **Given** das Tool ist installiert, **When** der Nutzer `gmail --help` ausführt, **Then** wird eine übersichtliche Hilfe mit allen verfügbaren Befehlen angezeigt
3. **Given** das Tool ist installiert, **When** der Nutzer `gmail --version` ausführt, **Then** wird die installierte Version angezeigt

---

### User Story 3 - E-Mails suchen (Priority: P2)

Als Entwickler möchte ich E-Mails durchsuchen und filtern können, damit ich schnell relevante Nachrichten finde, ohne die Gmail-Weboberfläche öffnen zu müssen.

**Why this priority**: Die Suche ist die häufigste Interaktion mit dem Postfach und ermöglicht das Auffinden von E-Mails für weitere Aktionen.

**Independent Test**: Kann getestet werden durch `gmail search "test"` und Überprüfung, dass relevante E-Mails mit ID, Absender, Betreff und Datum aufgelistet werden.

**Acceptance Scenarios**:

1. **Given** der Nutzer ist authentifiziert, **When** er `gmail search "Suchbegriff"` ausführt, **Then** werden passende E-Mails in einer übersichtlichen Liste angezeigt (ID, Absender, Betreff, Datum)
2. **Given** es gibt viele Suchergebnisse, **When** die Suche ausgeführt wird, **Then** werden die Ergebnisse paginiert angezeigt mit der Möglichkeit zur Navigation
3. **Given** der Nutzer möchte die Suche eingrenzen, **When** er Filter wie `--from`, `--to`, `--subject`, `--label`, `--after`, `--before`, `--has:attachment` verwendet, **Then** werden nur E-Mails angezeigt, die allen Filterkriterien entsprechen
4. **Given** keine E-Mails entsprechen der Suche, **When** die Suche ausgeführt wird, **Then** wird eine aussagekräftige Meldung angezeigt, dass keine Ergebnisse gefunden wurden

---

### User Story 4 - E-Mail lesen (Priority: P2)

Als Entwickler möchte ich eine E-Mail vollständig lesen können, inklusive aller Details und Anhänge, damit ich alle relevanten Informationen erhalte.

**Why this priority**: Das Lesen von E-Mails ist eine Kernfunktion, die auf die Suche aufbaut und vor dem Senden benötigt wird.

**Independent Test**: Kann getestet werden durch `gmail read <mail-id>` und Überprüfung, dass der vollständige E-Mail-Inhalt korrekt angezeigt wird.

**Acceptance Scenarios**:

1. **Given** der Nutzer hat eine Mail-ID, **When** er `gmail read <id>` ausführt, **Then** wird die E-Mail mit Absender, Empfänger, Betreff, Datum und Inhalt angezeigt
2. **Given** die E-Mail enthält HTML-Inhalt, **When** sie angezeigt wird, **Then** wird der Inhalt als lesbarer Text formatiert im Terminal dargestellt
3. **Given** die E-Mail hat Anhänge, **When** sie angezeigt wird, **Then** werden alle Anhänge mit Name und Größe aufgelistet
4. **Given** die Mail-ID existiert nicht, **When** der Nutzer versucht sie zu lesen, **Then** wird eine verständliche Fehlermeldung angezeigt

---

### User Story 5 - Attachments verwalten (Priority: P2)

Als Entwickler möchte ich Anhänge einer E-Mail herunterladen können, damit ich auf Dateien zugreifen kann, ohne den Browser zu öffnen.

**Why this priority**: Attachment-Handling ist essenziell für die vollständige E-Mail-Verwaltung und eng mit dem Lesen verknüpft.

**Independent Test**: Kann getestet werden durch `gmail attachment download <mail-id> <attachment-name>` und Überprüfung, dass die Datei korrekt gespeichert wird.

**Acceptance Scenarios**:

1. **Given** eine E-Mail hat Anhänge, **When** der Nutzer `gmail attachment list <mail-id>` ausführt, **Then** werden alle Anhänge mit Name, Größe und MIME-Type aufgelistet
2. **Given** der Nutzer möchte einen Anhang herunterladen, **When** er `gmail attachment download <mail-id> <attachment-name>` ausführt, **Then** wird der Anhang im aktuellen Verzeichnis gespeichert (oder im angegebenen Pfad mit `--output`)
3. **Given** der Nutzer möchte alle Anhänge herunterladen, **When** er `gmail attachment download <mail-id> --all` ausführt, **Then** werden alle Anhänge in das angegebene Verzeichnis heruntergeladen

---

### User Story 6 - E-Mail senden (Priority: P3)

Als Entwickler möchte ich E-Mails direkt aus dem Terminal senden können, optional mit meiner Gmail-Signatur, damit ich effizient kommunizieren kann.

**Why this priority**: Das Senden ist wichtig, aber weniger häufig genutzt als Suchen und Lesen. Es erfordert die anderen Funktionen als Basis.

**Independent Test**: Kann getestet werden durch `gmail send --to recipient@example.com --subject "Test" --body "Nachricht"` und Verifizierung in Gmail, dass die E-Mail gesendet wurde.

**Acceptance Scenarios**:

1. **Given** der Nutzer ist authentifiziert, **When** er `gmail send --to <empfänger> --subject <betreff> --body <nachricht>` ausführt, **Then** wird die E-Mail gesendet und eine Bestätigung angezeigt
2. **Given** der Nutzer möchte seine Gmail-Signatur verwenden, **When** er `gmail send ... --signature` ausführt, **Then** wird die in Gmail konfigurierte Signatur automatisch angehängt
3. **Given** der Nutzer möchte mehrere Empfänger angeben, **When** er `--to` und `--cc` und `--bcc` verwendet, **Then** werden alle Empfänger korrekt adressiert
4. **Given** der Nutzer möchte Dateien anhängen, **When** er `--attach <datei>` verwendet, **Then** wird die Datei als Anhang mitgesendet
5. **Given** der Nutzer möchte auf eine E-Mail antworten, **When** er `gmail reply <mail-id> --body <nachricht>` ausführt, **Then** wird die Antwort im korrekten Thread gesendet

---

### Edge Cases

- Was passiert, wenn die Netzwerkverbindung während einer Operation abbricht? → Fehlermeldung mit Hinweis auf Netzwerkproblem
- Wie verhält sich das System bei abgelaufenem OAuth-Token? → Automatische Token-Erneuerung via Refresh-Token
- Was passiert, wenn der Nutzer versucht, eine sehr große Datei (>25MB) anzuhängen? → Fehlermeldung vor Upload (Gmail-Limit)
- Wie werden E-Mails mit speziellen Zeichensätzen oder Encoding dargestellt? → UTF-8 Normalisierung, Fallback auf Raw-Darstellung
- Was passiert bei gleichzeitiger Nutzung durch mehrere Terminal-Sessions? → Unterstützt (Keyring ist thread-safe)
- Wie wird mit Rate-Limiting der Gmail API umgegangen? → Automatisches Exponential Backoff mit max. 3 Retries

## Requirements *(mandatory)*

### Functional Requirements

**Authentifizierung:**
- **FR-001**: System MUST OAuth 2.0 Authentifizierung mit Google implementieren
- **FR-002**: System MUST Access- und Refresh-Tokens im System Keyring speichern (macOS Keychain, Windows Credential Manager, Linux Secret Service via keyring library)
- **FR-003**: System MUST automatisch Token erneuern, wenn sie ablaufen
- **FR-004**: System MUST einen `auth login`, `auth logout` und `auth status` Befehl bereitstellen

**Suche:**
- **FR-005**: System MUST E-Mails nach Stichworten durchsuchen können
- **FR-006**: System MUST Filter für Absender, Empfänger, Betreff, Label, Datum und Anhänge unterstützen
- **FR-007**: System MUST Suchergebnisse paginiert anzeigen (Standard: 20 pro Seite, konfigurierbar via `--limit`)
- **FR-008**: System MUST für jede E-Mail ID, Absender, Betreff, Datum und Vorschau anzeigen

**Lesen:**
- **FR-009**: System MUST E-Mails anhand ihrer ID vollständig anzeigen können
- **FR-010**: System MUST HTML-Inhalte als lesbaren Text im Terminal formatieren
- **FR-011**: System MUST Anhänge einer E-Mail mit Name und Größe auflisten

**Attachments:**
- **FR-012**: System MUST einzelne Anhänge herunterladen können
- **FR-013**: System MUST alle Anhänge einer E-Mail auf einmal herunterladen können
- **FR-014**: System MUST einen Ziel-Pfad für Downloads akzeptieren

**Senden:**
- **FR-015**: System MUST E-Mails mit Empfänger, Betreff und Nachrichtentext senden können
- **FR-016**: System MUST CC und BCC Empfänger unterstützen
- **FR-017**: System MUST Dateianhänge beim Senden unterstützen
- **FR-018**: System MUST die in Gmail konfigurierte Signatur verwenden können
- **FR-019**: System MUST auf bestehende E-Mails antworten können (im selben Thread)

**Installation & UX:**
- **FR-020**: System MUST als uv-Tool installierbar sein
- **FR-021**: System MUST einen `--help` Befehl für jeden Unterbefehl bereitstellen
- **FR-022**: System MUST farbige, formatierte Ausgabe im Terminal unterstützen
- **FR-023**: System MUST aussagekräftige Fehlermeldungen bei Problemen anzeigen

### Key Entities

- **E-Mail**: Eine Nachricht mit Absender, Empfänger(n), Betreff, Inhalt, Datum, Labels und optionalen Anhängen
- **Attachment**: Eine an eine E-Mail angehängte Datei mit Name, Größe und MIME-Type
- **Credentials**: OAuth 2.0 Token-Paar (Access + Refresh Token) für die API-Authentifizierung
- **Signatur**: Die in Gmail vom Nutzer konfigurierte E-Mail-Signatur
- **Label**: Gmail-spezifische Kategorie/Ordner für E-Mails (Inbox, Sent, Spam, etc.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Nutzer können sich innerhalb von 2 Minuten authentifizieren (erster Login)
- **SC-002**: Suchergebnisse werden innerhalb von 3 Sekunden angezeigt (bei stabiler Internetverbindung)
- **SC-003**: Eine E-Mail kann innerhalb von 2 Sekunden vollständig geladen und angezeigt werden
- **SC-004**: Anhänge werden mit mindestens 1 MB/s heruntergeladen (bei ausreichender Bandbreite)
- **SC-005**: E-Mails können innerhalb von 5 Sekunden gesendet werden
- **SC-006**: Installation via uv gelingt in unter 30 Sekunden
- **SC-007**: 95% der typischen Entwickler-Workflows (Suchen, Lesen, Antworten) erfordern maximal 3 Befehle
- **SC-008**: Alle CLI-Befehle folgen dem bekannten Muster von gh CLI (verb-noun Struktur)
- **SC-009**: Die Hilfe-Texte ermöglichen Nutzern, alle Features ohne externe Dokumentation zu verstehen

## Clarifications

### Session 2025-12-01

- Q: Wie wird die OAuth Client ID bereitgestellt? → A: CLI enthält vorkonfigurierte credentials.json; Nutzer durchlaufen OAuth-Flow bei `gmail auth login`
- Q: Wo werden OAuth-Tokens gespeichert? → A: System Keyring (keyring library - macOS Keychain, Windows Credential Manager, Linux Secret Service)
- Q: Standard-Pagination Seitengröße? → A: 20 Ergebnisse pro Seite (konfigurierbar via --limit)
- Q: Was ist explizit out-of-scope? → A: Label-Management, Drafts, Kalender-Integration, Kontakte-Verwaltung
- Q: Wie wird Gmail API Rate-Limiting behandelt? → A: Automatisches Exponential Backoff mit max. 3 Retries

## Assumptions

- Nutzer haben Python 3.13+ installiert und uv verfügbar
- Nutzer haben einen Google Account mit Gmail
- OAuth credentials.json ist im CLI-Paket enthalten (vom Entwickler bereitgestellt)
- Terminal unterstützt UTF-8 und ANSI-Farbcodes
- Netzwerkzugang zu Google APIs ist verfügbar
- Gmail-Signaturen werden über die Gmail Settings API abgerufen
