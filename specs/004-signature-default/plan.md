# Implementation Plan: Signature Default Behavior Change

**Branch**: `004-signature-default` | **Date**: 2025-12-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-signature-default/spec.md`

## Summary

Change the default signature behavior from opt-in (`--signature` flag required) to opt-out (`--no-signature` flag to exclude). This matches standard email client behavior where signatures are included by default. The implementation maintains backwards compatibility by keeping the `--signature` flag (now a no-op) and adding a new `--no-signature` flag.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: typer (CLI framework), google-api-python-client (Gmail API)
**Storage**: N/A (no data model changes)
**Testing**: pytest with typer.testing.CliRunner
**Target Platform**: macOS, Linux, Windows (cross-platform CLI)
**Project Type**: Single CLI project
**Performance Goals**: N/A (no performance-sensitive changes)
**Constraints**: Must maintain 100% backwards compatibility with existing `--signature` flag usage
**Scale/Scope**: Changes limited to `send.py` CLI module and corresponding tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modern Python Stack | ✅ PASS | Python 3.13+, type hints, uv/ruff tooling |
| II. CLI-First Design | ✅ PASS | Follows `gmail <verb> [options]` pattern, backwards compatible |
| III. Test-Driven Development | ✅ PASS | Tests will be written for new flag behavior |
| IV. Secure Credential Handling | ✅ PASS | No credential changes |
| V. Simplicity Over Features | ✅ PASS | Minimal change - only flag default modification |

**Gate Status**: ✅ PASS - No violations

## Project Structure

### Documentation (this feature)

```text
specs/004-signature-default/
├── plan.md              # This file
├── research.md          # Phase 0 output (minimal - no unknowns)
├── tasks.md             # Phase 2 output (/speckit.tasks command)
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
src/gmail_cli/
├── cli/
│   └── send.py          # PRIMARY CHANGE: send_command and reply_command signature handling
├── services/
│   └── gmail.py         # get_signature function (no changes needed)
└── utils/
    └── markdown.py      # Markdown processing (no changes needed)

tests/
├── integration/
│   └── test_send.py     # UPDATE: Tests for new default behavior
└── unit/
    └── test_compose.py  # Existing compose tests (no changes needed)
```

**Structure Decision**: Single project structure. Changes are localized to `send.py` CLI module and its integration tests.

## Complexity Tracking

> No violations - table not needed

## Implementation Approach

### Flag Behavior Matrix

| Flags Specified | Current Behavior | New Behavior |
|-----------------|------------------|--------------|
| (none) | No signature | **Signature included** |
| `--signature` | Signature included | Signature included (no-op) |
| `--no-signature` | N/A (flag doesn't exist) | **No signature** |
| `--signature --no-signature` | N/A | **No signature** (opt-out wins) |

### Code Change Strategy

The change is straightforward:

1. **Invert the boolean logic**:
   - Current: `if signature:` → append signature
   - New: `if not no_signature:` → append signature (default True)

2. **Keep old flag for compatibility**:
   - `--signature` becomes a no-op (explicitly included in help for backwards compatibility)
   - Both flags coexist; `--no-signature` takes precedence

3. **Typer flag configuration**:
   ```python
   # New approach using typer's flag/no-flag pattern
   signature: bool = typer.Option(
       True,  # Default is now True (signature included)
       "--signature/--no-signature",
       "--sig/--no-sig",
       help="Include/exclude Gmail signature (default: include)."
   )
   ```

### Files to Modify

1. **`src/gmail_cli/cli/send.py`**:
   - `send_command()`: Change signature parameter default and logic
   - `reply_command()`: Change signature parameter default and logic
   - Update docstrings and help text

2. **`tests/integration/test_send.py`**:
   - Update existing `test_send_with_signature` test
   - Add `test_send_default_includes_signature`
   - Add `test_send_no_signature_excludes_signature`
   - Add `test_reply_default_includes_signature`
   - Add `test_reply_no_signature_excludes_signature`

3. **`README.md`**:
   - Update Send Emails section to reflect new default
   - Update options table with `--no-signature` flag
