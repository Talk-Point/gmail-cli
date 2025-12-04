# Gmail CLI

A powerful command-line interface for Gmail, inspired by GitHub's `gh` CLI. Manage your emails directly from the terminal with intuitive commands.

## Features

- **Multi-Account Support** - Authenticate and manage multiple Gmail accounts
- **Authentication** - Secure OAuth 2.0 login with credentials stored in your system's keyring
- **Search** - Find emails with powerful filters (sender, recipient, date, labels, attachments)
- **Read** - View full email content with automatic HTML-to-text conversion
- **Send** - Compose and send emails with attachments and Markdown formatting
- **Reply** - Reply to emails (single or reply-all) within the same thread
- **Markdown Support** - Email bodies are automatically converted from Markdown to HTML
- **Attachments** - List and download email attachments
- **JSON Output** - Machine-readable output for scripting and automation

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- A Google Cloud project with Gmail API enabled

### Install from GitHub

```bash
# Install directly from GitHub
uv tool install git+https://github.com/Talk-Point/gmail-cli.git

# Update to latest version
uv tool upgrade gmail-cli
```

### Install from source

```bash
git clone https://github.com/Talk-Point/gmail-cli.git
cd gmail-cli
uv tool install .
```

### Run without installing

```bash
# Run directly from GitHub
uvx --from git+https://github.com/Talk-Point/gmail-cli.git gmail --help

# Or clone and run locally
git clone https://github.com/Talk-Point/gmail-cli.git
cd gmail-cli
uv run gmail --help
```

### Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API** for your project
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Select **Desktop app** as application type
6. Download the credentials and save as `credentials.json` in your working directory

## Quick Start

Download the secret, `credential.json` in current directory. Delete after `$ gmail auth login`

```bash
# 1. Authenticate with Gmail
gmail auth login

# 2. Search for emails
gmail search "from:newsletter@example.com"

# 3. Read an email
gmail read 18c1234abcd5678

# 4. Send an email
gmail send --to recipient@example.com --subject "Hello" --body "Hi there!"
```

## Commands

### Authentication

```bash
# Login via OAuth (opens browser)
gmail auth login

# Add another account
gmail auth login

# Add account and set as default
gmail auth login --set-default

# Check authentication status (shows all accounts)
gmail auth status

# Set default account
gmail auth set-default work@company.com

# Logout default account
gmail auth logout

# Logout specific account
gmail auth logout --account work@company.com

# Logout all accounts
gmail auth logout --all
```

### Account Management

```bash
# List all configured accounts (default marked with *)
gmail accounts list
```

### Multi-Account Usage

All commands support the `--account` option to specify which account to use:

```bash
# Search in specific account
gmail search "invoice" --account work@company.com

# Read email from specific account
gmail read 18c1234abcd5678 --account personal@gmail.com

# Send from specific account
gmail send --to recipient@example.com --subject "Hello" --body "Hi!" --account work@company.com
```

You can also set the default account via environment variable:

```bash
# Set default account via environment variable
export GMAIL_ACCOUNT=work@company.com
gmail search "test"  # Uses work@company.com

# --account flag always takes precedence
gmail search "test" --account personal@gmail.com  # Uses personal@gmail.com
```

**Account Resolution Priority:**
1. `--account` flag (highest priority)
2. `GMAIL_ACCOUNT` environment variable
3. Configured default account
4. First authenticated account

### Search Emails

```bash
# Basic search
gmail search "invoice"

# Search with filters
gmail search --from sender@example.com
gmail search --to recipient@example.com
gmail search --subject "meeting"
gmail search --label INBOX
gmail search --label STARRED
gmail search --after 2025-01-01 --before 2025-12-31
gmail search --has-attachment

# Combine filters
gmail search "project" --from boss@company.com --has-attachment

# Pagination
gmail search "reports" --limit 50
gmail search "reports" --page <token>  # Use token from previous results
```

**Search Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--from` | `-f` | Filter by sender |
| `--to` | `-t` | Filter by recipient |
| `--subject` | `-s` | Filter by subject |
| `--label` | `-l` | Filter by label (INBOX, SENT, STARRED, etc.) |
| `--after` | | Emails after date (YYYY-MM-DD) |
| `--before` | | Emails before date (YYYY-MM-DD) |
| `--has-attachment` | `-a` | Only emails with attachments |
| `--limit` | `-n` | Max results (default: 20) |
| `--page` | | Pagination token |
| `--account` | `-A` | Use specific account |

### Read Emails

```bash
# Read email by ID
gmail read 18c1234abcd5678

# Show raw content without HTML conversion
gmail read 18c1234abcd5678 --raw

# Read from specific account
gmail read 18c1234abcd5678 --account work@company.com
```

### Send Emails

Email bodies support **Markdown formatting** by default. Your Markdown is automatically converted to HTML with GitHub-Flavored Markdown support (bold, italic, tables, code blocks, task lists, etc.).

Your **Gmail signature is included by default** - use `--no-signature` to exclude it.

```bash
# Basic send (Markdown + signature enabled by default)
gmail send --to recipient@example.com --subject "Hello" --body "Message content"

# With Markdown formatting
gmail send --to recipient@example.com --subject "Update" \
    --body "## Status Report\n\n**Progress:** 80% complete\n\n- [x] Task 1\n- [ ] Task 2"

# Send without signature
gmail send --to recipient@example.com --subject "Quick note" --body "Hi!" --no-signature

# Send as plain text (disable Markdown)
gmail send --to recipient@example.com --subject "Hello" --body "**not bold**" --plain

# Multiple recipients
gmail send --to a@example.com --to b@example.com --subject "Team Update" --body "..."

# With CC and BCC
gmail send --to main@example.com --cc copy@example.com --bcc hidden@example.com \
    --subject "Report" --body "See attached"

# Body from file (Markdown also supported)
gmail send --to recipient@example.com --subject "Report" --body-file report.md

# With attachments
gmail send --to recipient@example.com --subject "Documents" \
    --body "Please find attached" --attach document.pdf --attach image.png
```

**Send Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--to` | `-t` | Recipient (required, repeatable) |
| `--subject` | `-s` | Email subject (required) |
| `--body` | `-b` | Email body text |
| `--body-file` | `-f` | Read body from file |
| `--cc` | | CC recipient (repeatable) |
| `--bcc` | | BCC recipient (repeatable) |
| `--attach` | `-a` | File to attach (repeatable) |
| `--signature/--no-signature` | `--sig/--no-sig` | Include/exclude Gmail signature (default: enabled) |
| `--plain` | | Disable Markdown, send as plain text |
| `--account` | `-A` | Use specific account |

### Reply to Emails

Replies also support Markdown formatting by default, and your **Gmail signature is included by default**.

```bash
# Reply to sender (signature included by default)
gmail reply 18c1234abcd5678 --body "Thanks for your message!"

# Reply to all recipients
gmail reply 18c1234abcd5678 --all --body "Thanks everyone!"

# Reply with attachment
gmail reply 18c1234abcd5678 --body "Here's the file" --attach document.pdf

# Reply body from file
gmail reply 18c1234abcd5678 --body-file response.txt

# Reply without signature
gmail reply 18c1234abcd5678 --body "Quick reply" --no-signature

# Reply as plain text (no Markdown)
gmail reply 18c1234abcd5678 --body "**literal asterisks**" --plain
```

**Reply Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--body` | `-b` | Reply body text |
| `--body-file` | `-f` | Read body from file |
| `--all` | `-a` | Reply to all recipients |
| `--attach` | | File to attach (repeatable) |
| `--signature/--no-signature` | `--sig/--no-sig` | Include/exclude Gmail signature (default: enabled) |
| `--plain` | | Disable Markdown, send as plain text |
| `--account` | `-A` | Use specific account |

### Markdown Support

Email bodies are processed as **GitHub-Flavored Markdown** by default. Supported formatting:

| Feature | Syntax | Example |
|---------|--------|---------|
| Bold | `**text**` | **bold** |
| Italic | `*text*` | *italic* |
| Strikethrough | `~~text~~` | ~~deleted~~ |
| Headers | `# H1` to `###### H6` | Headings |
| Code (inline) | `` `code` `` | `inline code` |
| Code blocks | ` ```python ... ``` ` | Syntax highlighted |
| Tables | `\| A \| B \|` | Formatted tables |
| Task lists | `- [x] Done` | Checkboxes |
| Blockquotes | `> quote` | Quoted text |
| Lists | `- item` or `1. item` | Bulleted/numbered |
| Links | `[text](url)` | Clickable links |
| Images | `![alt](url)` | Embedded images |

The HTML output uses **inline CSS** for maximum email client compatibility (Gmail, Outlook, Apple Mail).

Use `--plain` to disable Markdown processing and send literal text.

### Manage Attachments

```bash
# List attachments for an email
gmail attachment list 18c1234abcd5678

# Download specific attachment
gmail attachment download 18c1234abcd5678 document.pdf

# Download to specific location
gmail attachment download 18c1234abcd5678 document.pdf --output ~/Downloads/doc.pdf

# Download all attachments
gmail attachment download 18c1234abcd5678 --all

# From specific account
gmail attachment list 18c1234abcd5678 --account work@company.com
```

### Global Options

```bash
# Show version
gmail --version

# JSON output (for scripting)
gmail --json search "test"
gmail --json read 18c1234abcd5678

# Help
gmail --help
gmail search --help
```

## JSON Output

All commands support `--json` for machine-readable output:

```bash
# Search results as JSON
gmail --json search "invoice" | jq '.emails[].subject'

# Email details as JSON
gmail --json read 18c1234abcd5678 | jq '.body_text'

# Attachment list as JSON
gmail --json attachment list 18c1234abcd5678 | jq '.attachments[].filename'
```

Example JSON output for search:

```json
{
  "emails": [
    {
      "id": "18c1234abcd5678",
      "thread_id": "18c1234abcd5678",
      "subject": "Invoice #1234",
      "sender": "billing@example.com",
      "date": "2025-12-01T10:30:00+00:00",
      "snippet": "Please find attached...",
      "is_read": true,
      "labels": ["INBOX", "IMPORTANT"]
    }
  ],
  "total_estimate": 42,
  "next_page_token": "token123",
  "query": "invoice"
}
```

## Configuration

### Credentials Storage

OAuth tokens are securely stored in your system's native keyring:
- **macOS**: Keychain
- **Windows**: Credential Manager
- **Linux**: Secret Service (GNOME Keyring, KWallet)

Each account's credentials are stored separately, allowing multiple Gmail accounts to be authenticated simultaneously.

### OAuth Scopes

The CLI requests the following Gmail API scopes:
- `gmail.readonly` - Read emails and metadata
- `gmail.send` - Send emails
- `gmail.settings.basic` - Access basic settings

---

# Developer Documentation

## Project Structure

```
gmail-cli/
├── src/gmail_cli/
│   ├── __init__.py          # Version string
│   ├── __main__.py          # Entry point
│   ├── cli/
│   │   ├── main.py          # Typer app, global options
│   │   ├── accounts.py      # Account management commands
│   │   ├── auth.py          # Auth commands + @require_auth decorator
│   │   ├── search.py        # Search command
│   │   ├── read.py          # Read command
│   │   ├── send.py          # Send + Reply commands
│   │   └── attachment.py    # Attachment commands
│   ├── services/
│   │   ├── auth.py          # OAuth flow, token management
│   │   ├── credentials.py   # Keyring storage
│   │   └── gmail.py         # Gmail API wrapper
│   ├── models/
│   │   ├── email.py         # Email dataclass
│   │   ├── attachment.py    # Attachment dataclass
│   │   ├── credentials.py   # Credentials model
│   │   └── search.py        # SearchResult model
│   └── utils/
│       ├── output.py        # Rich formatting, JSON output
│       ├── html.py          # HTML-to-text conversion
│       └── markdown.py      # Markdown-to-HTML conversion
├── tests/
│   ├── conftest.py          # Pytest fixtures, Gmail API mocks
│   ├── unit/                # Unit tests
│   └── integration/         # CLI integration tests
├── pyproject.toml           # Project config, dependencies
└── credentials.json         # OAuth client credentials (not in git!)
```

## Tech Stack

- **Python 3.13+** with type hints throughout
- **[Typer](https://typer.tiangolo.com/)** - CLI framework with Rich integration
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting, tables, panels
- **[google-api-python-client](https://github.com/googleapis/google-api-python-client)** - Gmail API
- **[google-auth-oauthlib](https://google-auth-oauthlib.readthedocs.io/)** - OAuth 2.0 flow
- **[keyring](https://keyring.readthedocs.io/)** - Secure credential storage
- **[html2text](https://github.com/Alir3z4/html2text)** - HTML-to-text conversion
- **[markdown](https://python-markdown.github.io/)** - Markdown to HTML conversion
- **[pymdown-extensions](https://facelessuser.github.io/pymdown-extensions/)** - GFM extensions (strikethrough, task lists)
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Ruff](https://docs.astral.sh/ruff/)** - Linting and formatting

## Development Setup

```bash
# Clone repository
git clone https://github.com/Talk-Point/gmail-cli.git
cd gmail-cli

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run CLI
uv run gmail --help
```

## Testing

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/unit/test_gmail_service.py -v

# Run with coverage
uv run python -m pytest tests/ --cov=gmail_cli
```

### Test Structure

Tests are organized by type:

- **Unit tests** (`tests/unit/`) - Test individual functions and classes
- **Integration tests** (`tests/integration/`) - Test CLI commands end-to-end

All tests use mocks for Gmail API calls - no real credentials needed.

### Writing Tests

```python
# Example: Testing a CLI command
from unittest.mock import patch
from typer.testing import CliRunner
from gmail_cli.cli.main import app

runner = CliRunner()

def test_search_requires_auth():
    with patch("gmail_cli.cli.auth.is_authenticated") as mock_auth:
        mock_auth.return_value = False
        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code == 1
```

## Code Quality

```bash
# Lint check
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check src/ tests/ --fix

# Format code
uv run ruff format src/ tests/

# Check formatting
uv run ruff format --check src/ tests/
```

### Ruff Configuration

See `pyproject.toml` for full config. Key rules enabled:
- `E`, `W` - pycodestyle
- `F` - Pyflakes
- `I` - isort (import sorting)
- `B` - flake8-bugbear
- `UP` - pyupgrade (modern Python syntax)

## Architecture

### Authentication Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   User      │────▶│ gmail auth   │────▶│  Browser    │
│             │     │   login      │     │  OAuth      │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   Keyring    │◀────│  Google     │
                    │   Storage    │     │  Token      │
                    └──────────────┘     └─────────────┘
```

### Request Flow

```
CLI Command
    │
    ▼
@require_auth decorator  ──▶  Check credentials
    │
    ▼
Gmail Service (gmail.py)
    │
    ▼
_execute_with_retry()  ──▶  Exponential backoff for rate limits
    │
    ▼
Google API Client
    │
    ▼
Gmail API
```

### Adding New Commands

1. Create command in `src/gmail_cli/cli/yourcommand.py`:

```python
from typing import Annotated
import typer
from gmail_cli.cli.auth import require_auth

@require_auth
def your_command(
    arg: Annotated[str, typer.Argument(help="Description")],
) -> None:
    """Command docstring shown in --help."""
    # Implementation
    pass
```

2. Register in `src/gmail_cli/cli/main.py`:

```python
from gmail_cli.cli.yourcommand import your_command

app.command("yourcommand")(your_command)
```

3. Write tests in `tests/integration/test_yourcommand.py`

## Signature Handling

The signature is **enabled by default** for `send` and `reply` commands. This has important implications for testing.

### Signature Flag Behavior

```python
# In src/gmail_cli/cli/send.py
signature: Annotated[
    bool,
    typer.Option(
        "--signature/--no-signature",
        "--sig/--no-sig",
        help="Include Gmail signature (default: enabled).",
    ),
] = True,  # Default is True (signature enabled)
```

- `gmail send ...` → Signature included (default)
- `gmail send ... --signature` → Signature included (explicit, same as default)
- `gmail send ... --no-signature` → Signature excluded

### Testing with Signatures

Since signature is enabled by default, **all tests that call `send` or `reply` must mock `get_signature`** to avoid unexpected behavior:

```python
from unittest.mock import patch
from typer.testing import CliRunner
from gmail_cli.cli.main import app

runner = CliRunner()

def test_send_email():
    with (
        patch("gmail_cli.cli.auth.is_authenticated") as mock_auth,
        patch("gmail_cli.cli.send.send_email") as mock_send,
        patch("gmail_cli.cli.send.compose_email") as mock_compose,
        patch("gmail_cli.cli.send.get_signature") as mock_sig,  # Required!
    ):
        mock_auth.return_value = True
        mock_sig.return_value = None  # No signature configured
        mock_compose.return_value = {"raw": "test"}
        mock_send.return_value = {"id": "123", "threadId": "456"}

        result = runner.invoke(app, ["send", "--to", "x@x.com", "--subject", "Test", "--body", "Hi"])
        assert result.exit_code == 0
```

**Important:** If you don't mock `get_signature`, the test will attempt to fetch a real signature from the Gmail API, which may fail or cause unexpected test behavior.

### Testing Signature-Specific Behavior

```python
# Test that signature is included by default
def test_send_default_includes_signature():
    with (
        patch("gmail_cli.cli.send.get_signature") as mock_sig,
        # ... other mocks
    ):
        mock_sig.return_value = '<div class="signature">My Sig</div>'

        result = runner.invoke(app, ["send", "--to", "x@x.com", "--subject", "Test", "--body", "Hi"])

        mock_sig.assert_called_once()  # Signature was fetched
        # Check html_body contains signature
        call_kwargs = mock_compose.call_args[1]
        assert "signature" in call_kwargs["html_body"].lower()

# Test that --no-signature excludes signature
def test_send_no_signature_excludes():
    with (
        patch("gmail_cli.cli.send.get_signature") as mock_sig,
        # ... other mocks
    ):
        result = runner.invoke(app, ["send", "--to", "x@x.com", "--subject", "Test", "--body", "Hi", "--no-signature"])

        mock_sig.assert_not_called()  # Signature was NOT fetched
```

## API Rate Limiting

The Gmail API has quota limits. The CLI handles this with:
- Exponential backoff (1s, 2s, 4s delays)
- Max 3 retries per request
- Graceful error handling

See `_execute_with_retry()` in `src/gmail_cli/services/gmail.py`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`uv run python -m pytest tests/`)
5. Ensure code is formatted (`uv run ruff format src/ tests/`)
6. Commit your changes
7. Push to the branch
8. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Made with Python and caffeine.
