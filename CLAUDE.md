# gmail-cli Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-01

## Active Technologies
- Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (credential storage), rich (terminal output) (002-multi-account)
- System keyring via `keyring` library (account-specific keys) (002-multi-account)
- Python 3.13+ + yper (CLI framework), google-api-python-client (Gmail API) (004-signature-default)
- N/A (no data model changes) (004-signature-default)
- Python 3.11+ (kompatibel mit 3.11, 3.12, 3.13, 3.14) + typer (CLI), google-api-python-client (Gmail API), rich (Output), keyring (Credentials) (005-draft-function)
- Gmail API (Drafts werden in Gmail gespeichert, nicht lokal) (005-draft-function)

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
- 005-draft-function: Added Python 3.11+ (kompatibel mit 3.11, 3.12, 3.13, 3.14) + typer (CLI), google-api-python-client (Gmail API), rich (Output), keyring (Credentials)
- 004-signature-default: Added Python 3.13+ + yper (CLI framework), google-api-python-client (Gmail API)
- 002-multi-account: Added Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (credential storage), rich (terminal output)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
