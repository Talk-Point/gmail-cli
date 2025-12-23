# Gmail CLI

A command-line interface for Gmail, inspired by GitHub's `gh` CLI. Manage your emails directly from the terminal.

```bash
# Search, read, send - all from your terminal
gmail search "from:boss@company.com"
gmail read 18c1234abcd5678
gmail send --to colleague@company.com --subject "Update" --body "**Done!**"
```

## Why Gmail CLI?

- **Fast** - No browser needed, work directly in your terminal
- **Scriptable** - JSON output for automation and pipelines
- **Secure** - OAuth 2.0 authentication, credentials stored in your system keyring
- **Familiar** - Syntax inspired by `gh` CLI

---

## Installation

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Install

```bash
uv tool install git+https://github.com/Talk-Point/gmail-cli.git
```

### Update

```bash
uv tool upgrade gmail-cli
```

---

## Setup

### 1. Create Google Cloud Credentials

Before using Gmail CLI, you need OAuth credentials from Google:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Gmail API**: APIs & Services → Library → Search "Gmail API" → Enable
4. Create OAuth credentials: APIs & Services → Credentials → Create Credentials → OAuth client ID
5. Select **Desktop app** as application type
6. Download the JSON file and save as `credentials.json`

### 2. Authenticate

```bash
# Place credentials.json in current directory, then:
gmail auth login

# This opens your browser for Google OAuth consent
# After login, you can delete credentials.json - tokens are stored securely
```

### 3. Verify

```bash
gmail auth status
# ✓ Authenticated as: your.email@gmail.com
```

---

## Quick Start

```bash
# Search your inbox
gmail search "is:unread"

# Read an email (use ID from search results)
gmail read 18c1234abcd5678

# Send an email (Markdown supported, signature auto-included)
gmail send --to recipient@example.com --subject "Hello" --body "Hi there!"

# Reply to an email
gmail reply 18c1234abcd5678 --body "Thanks for your message!"
```

---

## Commands

### Search

Find emails with Gmail's powerful search syntax.

```bash
gmail search "invoice"                        # Free text search
gmail search --from boss@company.com          # By sender
gmail search --subject "meeting"              # By subject
gmail search --label STARRED                  # By label
gmail search --after 2025-01-01               # By date
gmail search --has-attachment                 # With attachments
gmail search "project" --from boss@company.com --has-attachment  # Combined
```

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

### Read

View email content with automatic HTML-to-text conversion.

```bash
gmail read 18c1234abcd5678           # Read email by ID
gmail read 18c1234abcd5678 --raw     # Show raw content
```

### Send

Compose and send emails. **Markdown is converted to HTML automatically.**

```bash
gmail send --to recipient@example.com --subject "Hello" --body "Hi there!"
```

**Features:**
- Markdown formatting (bold, tables, code blocks, etc.)
- Signature auto-included (use `--no-signature` to exclude)
- Multiple recipients, CC, BCC
- File attachments

```bash
# Markdown formatting
gmail send --to dev@company.com --subject "Status" \
    --body "## Done\n- [x] Feature A\n- [ ] Feature B"

# Multiple recipients with CC
gmail send --to a@x.com --to b@x.com --cc manager@x.com \
    --subject "Update" --body "See below..."

# With attachment
gmail send --to client@x.com --subject "Report" \
    --body "Please find attached" --attach report.pdf

# Body from file
gmail send --to team@x.com --subject "Notes" --body-file meeting-notes.md

# Without signature
gmail send --to quick@x.com --subject "FYI" --body "Quick note" --no-signature

# Plain text (no Markdown conversion)
gmail send --to x@x.com --subject "Code" --body "Use **asterisks**" --plain
```

| Option | Short | Description |
|--------|-------|-------------|
| `--to` | `-t` | Recipient (required, repeatable) |
| `--subject` | `-s` | Subject (required) |
| `--body` | `-b` | Body text |
| `--body-file` | `-f` | Read body from file |
| `--cc` | | CC recipient (repeatable) |
| `--bcc` | | BCC recipient (repeatable) |
| `--attach` | `-a` | File attachment (repeatable) |
| `--signature/--no-signature` | `--sig/--no-sig` | Include signature (default: yes) |
| `--plain` | | Disable Markdown conversion |

### Reply

Reply to emails. Same features as send (Markdown, signature, attachments).

```bash
gmail reply 18c1234abcd5678 --body "Thanks!"
gmail reply 18c1234abcd5678 --all --body "Thanks everyone!"  # Reply all
gmail reply 18c1234abcd5678 --body "See attached" --attach file.pdf
```

| Option | Short | Description |
|--------|-------|-------------|
| `--body` | `-b` | Reply text |
| `--body-file` | `-f` | Read body from file |
| `--all` | `-a` | Reply to all recipients |
| `--attach` | | File attachment (repeatable) |
| `--cc` | | Additional CC (repeatable) |
| `--signature/--no-signature` | `--sig/--no-sig` | Include signature (default: yes) |
| `--plain` | | Disable Markdown conversion |

### Attachments

List and download email attachments.

```bash
gmail attachment list 18c1234abcd5678                    # List attachments
gmail attachment download 18c1234abcd5678 report.pdf    # Download one
gmail attachment download 18c1234abcd5678 --all         # Download all
gmail attachment download 18c1234abcd5678 doc.pdf --output ~/Downloads/doc.pdf
gmail attachment download 18c1234abcd5678 doc.pdf --output ~/Downloads/  # Saves as ~/Downloads/doc.pdf
```

---

## Features

### Markdown Support

Email bodies are processed as **GitHub-Flavored Markdown**:

| Syntax | Result |
|--------|--------|
| `**bold**` | **bold** |
| `*italic*` | *italic* |
| `~~strike~~` | ~~strikethrough~~ |
| `` `code` `` | `inline code` |
| `# Heading` | Headers (H1-H6) |
| `- item` | Bullet list |
| `1. item` | Numbered list |
| `- [x] task` | Checkboxes |
| `> quote` | Blockquote |
| `[text](url)` | Links |
| ` ``` code ``` ` | Code blocks |
| `\| table \|` | Tables |

Use `--plain` to send literal text without Markdown processing.

### Signature

Your Gmail signature is **automatically included** in all outgoing emails.

```bash
gmail send ... --body "Message"           # Signature included (default)
gmail send ... --body "Message" --no-sig  # No signature
```

The signature is fetched from your Gmail account settings. If no signature is configured in Gmail, nothing is added.

> **Note:** Changed in v0.5.0 - signatures are now included by default. Use `--no-signature` to exclude.

### Multi-Account Support

Use multiple Gmail accounts with the `--account` flag:

```bash
gmail auth login                                    # Add account
gmail auth login --set-default                      # Add and set as default
gmail accounts list                                 # List all accounts

gmail search "test" --account work@company.com     # Use specific account
gmail send --to x@x.com ... --account personal@gmail.com
```

Set default via environment variable:

```bash
export GMAIL_ACCOUNT=work@company.com
gmail search "test"  # Uses work@company.com
```

**Priority:** `--account` flag > `GMAIL_ACCOUNT` env > configured default > first account

### JSON Output

All commands support `--json` for scripting:

```bash
gmail --json search "invoice" | jq '.emails[].subject'
gmail --json read 18c1234abcd5678 | jq '.body_text'
gmail --json attachment list 18c1234abcd5678 | jq '.attachments[].filename'
```

Example output:

```json
{
  "emails": [
    {
      "id": "18c1234abcd5678",
      "subject": "Invoice #1234",
      "sender": "billing@example.com",
      "date": "2025-12-01T10:30:00+00:00",
      "snippet": "Please find attached..."
    }
  ],
  "total_estimate": 42,
  "next_page_token": "token123"
}
```

---

## Authentication

### How It Works

1. Gmail CLI uses **OAuth 2.0** - your password is never stored
2. On first login, your browser opens for Google consent
3. Tokens are stored in your system's **secure keyring**:
   - macOS: Keychain
   - Windows: Credential Manager
   - Linux: Secret Service (GNOME Keyring, KWallet)

### Managing Auth

```bash
gmail auth login              # Add account (opens browser)
gmail auth status             # Check authentication
gmail auth set-default x@x.com  # Change default account
gmail auth logout             # Logout default account
gmail auth logout --all       # Logout all accounts
gmail auth token              # Export credentials (for server deployment)
```

### Server Deployment

For headless servers without a browser, export credentials locally and transfer them:

```bash
# On local machine: export credentials
gmail auth token > credentials_export.json

# Transfer to server (use secure method)
scp credentials_export.json server:/path/to/

# On server: credentials can be imported via environment or file
# (See CONTRIBUTING.md for import details)
```

**Security Warning:** The exported JSON contains sensitive OAuth tokens. Handle with care and delete after transfer.

### Required Permissions

Gmail CLI requests these scopes:
- `gmail.readonly` - Read emails
- `gmail.send` - Send emails
- `gmail.settings.basic` - Read signature settings

---

## Troubleshooting

### "Not authenticated"

```bash
gmail auth login  # Re-authenticate
```

### "credentials.json not found"

Download OAuth credentials from Google Cloud Console (see [Setup](#setup)).

### "Rate limit exceeded"

Gmail API has quotas. The CLI automatically retries with exponential backoff. Wait a moment and try again.

### Token expired

Tokens auto-refresh. If issues persist:

```bash
gmail auth logout
gmail auth login
```

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and architecture documentation.

```bash
git clone https://github.com/Talk-Point/gmail-cli.git
cd gmail-cli
uv pip install -e ".[dev]"
uv run pytest
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
