# Research: Signature Default Behavior Change

**Feature**: 004-signature-default
**Date**: 2025-12-04

## Research Summary

This feature has minimal technical unknowns. The implementation leverages existing typer CLI patterns and the established signature handling code.

## Decision 1: Typer Boolean Flag Pattern

**Decision**: Use typer's built-in `--flag/--no-flag` pattern for boolean options

**Rationale**:
- Typer natively supports `--option/--no-option` syntax
- Provides clean help text generation
- Widely recognized CLI convention (similar to git, npm, etc.)
- Single parameter handles both positive and negative cases

**Alternatives considered**:
- Separate `--signature` and `--no-signature` parameters: More complex, requires conflict handling
- Environment variable override: Over-engineered for this use case

**Implementation**:
```python
signature: Annotated[
    bool,
    typer.Option(
        "--signature/--no-signature",
        "--sig/--no-sig",
        help="Include Gmail signature (default: enabled)."
    ),
] = True
```

## Decision 2: Backwards Compatibility Strategy

**Decision**: The `--signature` flag continues to work but becomes a no-op (default behavior)

**Rationale**:
- Existing scripts using `--signature` will not break
- Users don't need to update their workflows
- No deprecation warnings needed (flag still valid, just redundant)

**Alternatives considered**:
- Remove `--signature` flag: Would break existing scripts
- Show deprecation warning: Unnecessary noise for a harmless flag

## Decision 3: Flag Precedence

**Decision**: When both flags are somehow specified, `--no-signature` wins (explicit opt-out)

**Rationale**:
- Explicit opt-out should take precedence over default
- Follows principle of least surprise
- With typer's `--flag/--no-flag` pattern, the last flag wins naturally

**Implementation**: Typer handles this automatically - the last occurrence determines the value.

## No Further Research Needed

The existing codebase already has:
- `get_signature()` function working correctly
- HTML and plain text signature handling
- Signature appending logic in both send and reply commands

No external research or API investigation required.
