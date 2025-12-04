# Contributing to Gmail CLI

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
- **[pymdown-extensions](https://facelessuser.github.io/pymdown-extensions/)** - GFM extensions
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Ruff](https://docs.astral.sh/ruff/)** - Linting and formatting

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_gmail_service.py -v

# Run with coverage
uv run pytest --cov=gmail_cli
```

### Test Structure

- **Unit tests** (`tests/unit/`) - Test individual functions and classes
- **Integration tests** (`tests/integration/`) - Test CLI commands end-to-end

All tests use mocks for Gmail API calls - no real credentials needed.

### Writing Tests

```python
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

### Testing Send/Reply Commands

Since signature is enabled by default, **all tests must mock `get_signature`**:

```python
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

## API Rate Limiting

The Gmail API has quota limits. The CLI handles this with:
- Exponential backoff (1s, 2s, 4s delays)
- Max 3 retries per request
- Graceful error handling

See `_execute_with_retry()` in `src/gmail_cli/services/gmail.py`.

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`uv run pytest`)
5. Ensure code is formatted (`uv run ruff format src/ tests/`)
6. Commit your changes
7. Push to the branch
8. Open a Pull Request
