# gmail-cli Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-01

## Active Technologies
- Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (credential storage), rich (terminal output) (002-multi-account)
- System keyring via `keyring` library (account-specific keys) (002-multi-account)
- Python 3.13+ + yper (CLI framework), google-api-python-client (Gmail API) (004-signature-default)
- N/A (no data model changes) (004-signature-default)
- Python 3.11+ (kompatibel mit 3.11, 3.12, 3.13, 3.14) + typer (CLI), google-api-python-client (Gmail API), rich (Output), keyring (Credentials) (005-draft-function)
- Gmail API (Drafts werden in Gmail gespeichert, nicht lokal) (005-draft-function)
- Python 3.13+ (wie in Constitution definiert) + typer (CLI), google-api-python-client (Gmail API), python-dateutil (Zeit-Parsing) (006-email-schedule)
- Gmail Drafts (API), keine lokale Persistenz (006-email-schedule)

- Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (Credential Storage), rich (Terminal Output) (001-gmail-cli)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13+: Follow standard conventions

## Recent Changes
- 006-email-schedule: Added Python 3.13+ (wie in Constitution definiert) + typer (CLI), google-api-python-client (Gmail API), python-dateutil (Zeit-Parsing)
- 005-draft-function: Added Python 3.11+ (kompatibel mit 3.11, 3.12, 3.13, 3.14) + typer (CLI), google-api-python-client (Gmail API), rich (Output), keyring (Credentials)
- 004-signature-default: Added Python 3.13+ + yper (CLI framework), google-api-python-client (Gmail API)


<!-- MANUAL ADDITIONS START -->

## Release Process

1. **Version bump** - Update version in both files:
   - `src/gmail_cli/__init__.py` → `__version__ = "X.Y.Z"`
   - `pyproject.toml` → `version = "X.Y.Z"`

2. **Commit & Push** to develop:
   ```bash
   git add src/gmail_cli/__init__.py pyproject.toml
   git commit -m "chore: Bump version to X.Y.Z"
   git push
   ```

3. **Create PR** from develop → master:
   ```bash
   gh pr create --base master --head develop --title "Release vX.Y.Z"
   ```

4. **Merge PR** after CI passes

5. **Create GitHub Release** with tag:
   ```bash
   gh release create vX.Y.Z --target master --title "vX.Y.Z" --notes "Release notes here"
   ```

<!-- MANUAL ADDITIONS END -->
