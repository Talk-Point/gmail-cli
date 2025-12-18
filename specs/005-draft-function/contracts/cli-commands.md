# CLI Commands Contract: Draft-Funktion

**Feature**: 005-draft-function
**Date**: 2025-12-17

## Modified Commands

### gmail send --draft

**Synopsis**:
```bash
gmail send --to EMAIL [--to EMAIL...] --subject TEXT (--body TEXT | --body-file PATH) [OPTIONS] --draft
```

**New Option**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--draft` | flag | false | Save as draft instead of sending |

**Behavior Change**:
- Without `--draft`: Email is sent (unchanged)
- With `--draft`: Email is saved as draft

**Output (Human)**:
```
Draft created!
  Draft ID: r1234567890
```

**Output (JSON)**:
```json
{
    "status": "draft_created",
    "draft_id": "r1234567890",
    "message_id": "msg123",
    "thread_id": null
}
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Draft successfully created |
| 1 | Error (authentication, API error) |

---

### gmail reply --draft

**Synopsis**:
```bash
gmail reply MESSAGE_ID (--body TEXT | --body-file PATH) [OPTIONS] --draft
```

**New Option**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--draft` | flag | false | Save reply as draft instead of sending |

**Behavior Change**:
- Without `--draft`: Reply is sent (unchanged)
- With `--draft`: Reply is saved as draft in original thread

**Output (Human)**:
```
Reply draft created!
  Draft ID: r1234567890
  Thread ID: thread123
```

**Output (JSON)**:
```json
{
    "status": "draft_created",
    "draft_id": "r1234567890",
    "message_id": "msg123",
    "thread_id": "thread123"
}
```

---

## New Commands

### gmail draft list

**Synopsis**:
```bash
gmail draft list [--json] [--account EMAIL] [--limit N]
```

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | false | JSON output |
| `--account, -A` | string | default | Select account |
| `--limit, -n` | int | 20 | Maximum number of results |

**Output (Human)**:
```
Drafts (3):
  r1234567890  recipient@example.com     Subject line here
  r0987654321  another@example.com       Another subject
  r1111111111  third@example.com         Third email draft
```

**Output (No Drafts)**:
```
No drafts found.
```

**Output (JSON)**:
```json
{
    "drafts": [
        {
            "id": "r1234567890",
            "to": "recipient@example.com",
            "subject": "Subject line here",
            "snippet": "Preview text..."
        }
    ],
    "count": 3
}
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success (even with empty list) |
| 1 | Error |

---

### gmail draft show

**Synopsis**:
```bash
gmail draft show DRAFT_ID [--json] [--account EMAIL]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| DRAFT_ID | string | Yes | Draft ID |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | false | JSON output |
| `--account, -A` | string | default | Select account |

**Output (Human)**:
```
Draft: r1234567890

To:      recipient@example.com
Cc:      cc@example.com
Subject: Subject line here
Thread:  thread123

This is the email body content.
It can span multiple lines.

Attachments:
  - document.pdf (1.2 MB)
```

**Output (JSON)**:
```json
{
    "id": "r1234567890",
    "message_id": "msg123",
    "thread_id": null,
    "to": ["recipient@example.com"],
    "cc": ["cc@example.com"],
    "subject": "Subject line here",
    "body": "This is the email body content.\nIt can span multiple lines.",
    "attachments": [
        {
            "filename": "document.pdf",
            "size": 1258291,
            "mime_type": "application/pdf"
        }
    ]
}
```

**Error (Not Found)**:
```
Draft 'r1234567890' not found
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Draft not found or error |

---

### gmail draft send

**Synopsis**:
```bash
gmail draft send DRAFT_ID [--account EMAIL]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| DRAFT_ID | string | Yes | ID of draft to send |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--account, -A` | string | default | Select account |

**Output (Human)**:
```
Draft sent!
  Message ID: msg456
  Thread ID:  thread123
```

**Output (JSON)**:
```json
{
    "status": "sent",
    "message_id": "msg456",
    "thread_id": "thread123"
}
```

**Error (Not Found)**:
```
Draft 'r1234567890' not found
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Draft not found, invalid message, or error |

---

### gmail draft delete

**Synopsis**:
```bash
gmail draft delete DRAFT_ID [--account EMAIL]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| DRAFT_ID | string | Yes | ID of draft to delete |

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--account, -A` | string | default | Select account |

**Output (Human)**:
```
Draft deleted.
```

**Output (JSON)**:
```json
{
    "status": "deleted",
    "draft_id": "r1234567890"
}
```

**Error (Not Found)**:
```
Draft 'r1234567890' not found
```

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Draft not found or error |

---

## Help Text

### gmail draft --help

```
Usage: gmail draft [OPTIONS] COMMAND [ARGS]...

  Manage email drafts.

Commands:
  list    List all drafts.
  show    Show draft details.
  send    Send a draft.
  delete  Delete a draft.

Options:
  --help  Show this message and exit.
```
