<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0 (Initial ratification)
Modified principles: N/A (initial creation)
Added sections:
  - Core Principles (5 principles)
  - Technology Stack
  - Development Workflow
  - Governance
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (no changes needed - generic placeholders)
  - .specify/templates/spec-template.md ✅ (no changes needed - generic template)
  - .specify/templates/tasks-template.md ✅ (no changes needed - generic template)
Follow-up TODOs: None
-->

# Gmail CLI Constitution

## Core Principles

### I. Modern Python Stack

All code MUST use Python 3.13+ with type hints throughout. The project uses uv as the sole
package manager and build tool. Dependencies MUST be from the Astral ecosystem where available
(ruff for linting/formatting, uv for package management). No legacy tools (pip, setuptools,
poetry) are permitted in the development workflow.

**Rationale**: Astral tools provide superior performance and developer experience. Type hints
enable better IDE support and catch errors at development time.

### II. CLI-First Design

The application is a command-line tool following established CLI patterns (similar to gh, gcloud).
All functionality MUST be accessible via well-documented CLI commands. Commands follow the
pattern `gmail <verb> [options]` with consistent flag naming. Human-readable output is default;
JSON output MUST be available via `--json` flag for scripting.

**Rationale**: Developers expect consistent CLI interfaces. Machine-readable output enables
integration into scripts and automation workflows.

### III. Test-Driven Development

Tests MUST be written using pytest. New functionality requires tests before implementation
(red-green-refactor). Coverage targets: unit tests for all business logic, integration tests
for Gmail API interactions using mocks. Tests MUST pass before merging to main branch.

**Rationale**: TDD ensures code correctness and prevents regressions. Mocked API tests enable
reliable CI without requiring live Gmail credentials.

### IV. Secure Credential Handling

OAuth 2.0 tokens MUST be stored securely using system keyring or encrypted file storage.
Credentials MUST never be logged, committed, or exposed in error messages. Token refresh
MUST happen automatically and transparently to the user.

**Rationale**: Users trust the tool with access to their email. Security failures would
compromise sensitive communications.

### V. Simplicity Over Features

Start with minimal viable functionality. Avoid premature abstraction. Every feature addition
MUST justify its complexity. Prefer standard library solutions over additional dependencies
when equivalent. YAGNI (You Aren't Gonna Need It) applies to all design decisions.

**Rationale**: A focused CLI tool is more maintainable and easier to understand than a
feature-bloated application.

## Technology Stack

**Required versions and tools**:
- Python 3.13+ (required)
- uv for package management and virtual environment
- ruff for linting and formatting
- pytest for testing
- click or typer for CLI framework (to be decided in planning phase)

**Dependency policy**:
- Prefer Astral ecosystem packages
- Minimize external dependencies
- All dependencies MUST be specified in pyproject.toml with version constraints
- Security updates MUST be applied promptly

## Development Workflow

**Code quality gates**:
1. All code MUST pass `ruff check` with zero errors
2. All code MUST pass `ruff format --check`
3. All tests MUST pass via `pytest`
4. Type hints MUST be present on all public functions

**Branching strategy**:
- Feature branches from `develop`
- PRs require passing CI checks
- Main branch protected; releases tagged with semantic versions

**Commit conventions**:
- Conventional commits format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore

## Governance

This constitution defines non-negotiable standards for the Gmail CLI project. All code reviews
MUST verify compliance with these principles. Amendments require:

1. Written proposal with rationale
2. Update to this document with version increment
3. Migration plan for any breaking changes

Complexity beyond these standards MUST be justified in writing and approved before implementation.

**Version**: 1.0.0 | **Ratified**: 2025-12-01 | **Last Amended**: 2025-12-01
