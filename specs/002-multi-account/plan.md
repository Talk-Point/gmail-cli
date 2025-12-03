# Implementation Plan: Multi-Account Support

**Branch**: `002-multi-account` | **Date**: 2025-12-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-multi-account/spec.md`

## Summary

Enable Gmail CLI to manage and use multiple Gmail accounts. Users can authenticate multiple accounts, set a default, and select which account to use via `--account` flag or `GMAIL_ACCOUNT` environment variable. The implementation follows "Approach A: Simple Parameterization" from the technical study, threading account context through all service and CLI layers while maintaining full backward compatibility.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: typer (CLI), google-api-python-client (Gmail API), keyring (credential storage), rich (terminal output)
**Storage**: System keyring via `keyring` library (account-specific keys)
**Testing**: pytest with pytest-mock
**Target Platform**: macOS, Linux, Windows (any platform supporting system keyring)
**Project Type**: Single CLI application
**Performance Goals**: Account switch <3 seconds (SC-002)
**Constraints**: Backward compatibility with single-account workflows (SC-003)
**Scale/Scope**: Unlimited accounts (no enforced limit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Modern Python Stack | PASS | Uses Python 3.13+, uv, ruff, type hints throughout |
| II. CLI-First Design | PASS | Follows `gmail <verb> [options]` pattern; adds `--account`/`-a` flag and `--json` already supported |
| III. Test-Driven Development | PASS | Existing pytest structure; new tests required for multi-account |
| IV. Secure Credential Handling | PASS | Uses system keyring; per-account credential isolation |
| V. Simplicity Over Features | PASS | Minimal approach (Approach A from study); no over-engineering |

**All gates pass.** Proceeding with implementation planning.

## Project Structure

### Documentation (this feature)

```text
specs/002-multi-account/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contracts)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/gmail_cli/
├── __init__.py
├── __main__.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py          # MODIFY: set-default, enhanced status/logout
│   ├── search.py        # MODIFY: add --account parameter
│   ├── read.py          # MODIFY: add --account parameter
│   ├── send.py          # MODIFY: add --account parameter
│   └── attachment.py    # MODIFY: add --account parameter
├── models/
│   ├── __init__.py
│   ├── credentials.py
│   ├── email.py
│   ├── search.py
│   └── attachment.py
├── services/
│   ├── __init__.py
│   ├── auth.py          # MODIFY: account parameter, resolve_account()
│   ├── credentials.py   # MODIFY: multi-account keyring functions
│   └── gmail.py         # MODIFY: account parameter on all API calls
└── utils/
    ├── __init__.py
    ├── html.py
    └── output.py

tests/
├── conftest.py          # MODIFY: multi-account fixtures
├── unit/
│   ├── test_credentials.py    # MODIFY: multi-account tests
│   ├── test_auth_service.py   # MODIFY: account parameter tests
│   └── test_gmail_service.py  # MODIFY: account parameter tests
└── integration/
    ├── test_auth.py     # MODIFY: multi-account flow tests
    ├── test_search.py   # MODIFY: --account flag tests
    ├── test_read.py     # MODIFY: --account flag tests
    └── test_send.py     # MODIFY: --account flag tests
```

**Structure Decision**: Single project structure maintained. Changes are extensions to existing modules, not new structural components.

## Complexity Tracking

> No violations - all changes align with constitution principles.

| Aspect | Justification |
|--------|---------------|
| Approach A (Simple Parameterization) | Minimal complexity while meeting all requirements |
| No new modules | All changes in existing service/CLI layers |
| No new dependencies | Existing keyring library supports multi-key storage |
