# gmail-cli Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-01

## Active Technologies
- Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (credential storage), rich (terminal output) (002-multi-account)
- System keyring via `keyring` library (account-specific keys) (002-multi-account)
- Python 3.13+ + yper (CLI framework), google-api-python-client (Gmail API) (004-signature-default)
- N/A (no data model changes) (004-signature-default)

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
- 004-signature-default: Added Python 3.13+ + yper (CLI framework), google-api-python-client (Gmail API)
- 002-multi-account: Added Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (credential storage), rich (terminal output)

- 001-gmail-cli: Added Python 3.13+ + yper (CLI), google-api-python-client (Gmail API), keyring (Credential Storage), rich (Terminal Output)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
