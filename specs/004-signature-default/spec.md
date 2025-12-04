# Feature Specification: Signature Default Behavior Change

**Feature Branch**: `004-signature-default`
**Created**: 2025-12-04
**Status**: Draft
**Input**: User description: "ich will den default von keiner signature auf eine signature umstellen und das flag ändern aber es rückwärtskomptibel machen"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Default Signature Inclusion (Priority: P1)

As a user, I want my Gmail signature to be automatically appended to all sent emails and replies by default, so that I don't have to remember to add the `--signature` flag every time.

**Why this priority**: This is the core feature request - changing the default behavior to include signatures automatically, which matches standard email client behavior.

**Independent Test**: Can be fully tested by sending an email without any signature-related flags and verifying the signature is appended.

**Acceptance Scenarios**:

1. **Given** a user with a Gmail signature configured, **When** they send an email without specifying any signature flag, **Then** their Gmail signature is automatically appended to the email.
2. **Given** a user with a Gmail signature configured, **When** they reply to an email without specifying any signature flag, **Then** their Gmail signature is automatically appended to the reply.
3. **Given** a user without a Gmail signature configured, **When** they send an email, **Then** the email is sent normally without any signature (no error).

---

### User Story 2 - Opt-Out with No-Signature Flag (Priority: P1)

As a user, I want to be able to explicitly exclude my signature from an email when needed, using a `--no-signature` flag.

**Why this priority**: This provides backwards compatibility and user control. Users who previously sent emails without signatures need a way to continue doing so.

**Independent Test**: Can be fully tested by sending an email with `--no-signature` flag and verifying no signature is appended.

**Acceptance Scenarios**:

1. **Given** a user with a Gmail signature configured, **When** they send an email with `--no-signature` flag, **Then** the email is sent without a signature.
2. **Given** a user with a Gmail signature configured, **When** they reply to an email with `--no-signature` flag, **Then** the reply is sent without a signature.

---

### User Story 3 - Backwards Compatibility with Old Flag (Priority: P2)

As a user who has existing scripts or workflows using `--signature`, I want the old flag to still work (even though it's now the default behavior), so my existing automation doesn't break.

**Why this priority**: Essential for backwards compatibility but lower priority since the flag becomes essentially a no-op (the default behavior).

**Independent Test**: Can be fully tested by sending an email with the legacy `--signature` flag and verifying the signature is appended (same as default).

**Acceptance Scenarios**:

1. **Given** a user with existing scripts using `--signature` flag, **When** they run their existing command, **Then** the email is sent with signature (behaves as before, now same as default).
2. **Given** a user with existing scripts using `--sig` shorthand, **When** they run their existing command, **Then** the email is sent with signature.

---

### Edge Cases

- What happens when user has no Gmail signature configured? → Email sends normally without any signature, no error.
- What happens when both `--signature` and `--no-signature` are specified? → `--no-signature` takes precedence (explicit opt-out wins).
- What happens in plain text mode with signature? → Signature is converted to plain text and appended (existing behavior preserved).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST append the user's Gmail signature to emails by default when no signature-related flags are specified.
- **FR-002**: System MUST provide a `--no-signature` (or `--no-sig`) flag to explicitly exclude the signature from an email.
- **FR-003**: System MUST continue to accept the existing `--signature` (or `--sig`) flag for backwards compatibility, though it now has no effect (signature is default).
- **FR-004**: System MUST apply the new default behavior to both `send` and `reply` commands.
- **FR-005**: When both `--signature` and `--no-signature` are specified, `--no-signature` MUST take precedence.
- **FR-006**: System MUST handle the case where user has no Gmail signature configured gracefully (send email without signature, no error).
- **FR-007**: System MUST update help text and documentation to reflect the new default behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All existing commands using `--signature` flag continue to work identically (100% backwards compatibility for explicit flag usage).
- **SC-002**: Users can send emails without signature using `--no-signature` flag.
- **SC-003**: Default behavior (no flags) now includes signature automatically.
- **SC-004**: Help text accurately describes the new default behavior and available flags.

## Assumptions

- Users generally want their signature included in emails (standard email client behavior).
- The existing signature fetching and appending logic (`get_signature`, HTML/plain text handling) works correctly and doesn't need modification.
- The `--signature`/`--sig` flag will become a no-op but remains for backwards compatibility with existing scripts.
- No deprecation warning is needed for `--signature` flag as it's not harmful, just redundant.
