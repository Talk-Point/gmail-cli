# Quickstart: Draft Function

**Feature**: 005-draft-function
**Date**: 2025-12-17

## Prerequisites

- gmail-cli installed and authenticated (`gmail auth login`)
- Gmail account with API access enabled

## Quick Start

### 1. Save Email as Draft

```bash
# New email as draft
gmail send \
  --to recipient@example.com \
  --subject "Meeting tomorrow" \
  --body "Hello, can we call tomorrow?" \
  --draft

# Output:
# Draft created!
#   Draft ID: r1234567890
```

### 2. Save Reply as Draft

```bash
# Reply to an email as draft
gmail reply msg123456 \
  --body "Thanks for the info, I'll get back to you!" \
  --draft

# Output:
# Reply draft created!
#   Draft ID: r0987654321
#   Thread ID: thread789
```

### 3. List All Drafts

```bash
gmail draft list

# Output:
# Drafts (2):
#   r1234567890  recipient@example.com  Meeting tomorrow
#   r0987654321  sender@example.com      Re: Your request
```

### 4. Show Draft

```bash
gmail draft show r1234567890

# Output:
# Draft: r1234567890
#
# To:      recipient@example.com
# Subject: Meeting tomorrow
#
# Hello, can we call tomorrow?
```

### 5. Send Draft

```bash
gmail draft send r1234567890

# Output:
# Draft sent!
#   Message ID: msg789
#   Thread ID:  thread456
```

### 6. Delete Draft

```bash
gmail draft delete r0987654321

# Output:
# Draft deleted.
```

## JSON Output for Scripting

```bash
# All drafts as JSON
gmail draft list --json

# Draft details as JSON
gmail draft show r1234567890 --json
```

## Multi-Account Support

```bash
# Draft for specific account
gmail send --to user@example.com --subject "Test" --body "Content" \
  --draft --account work@company.com

# List drafts of specific account
gmail draft list --account work@company.com
```

## Typical Workflows

### Create draft → review → send

```bash
# 1. Create draft
gmail send -t user@example.com -s "Important" -b "Content..." --draft
# → Draft ID: r123

# 2. Review in browser (Gmail Drafts)
# ... or ...
gmail draft show r123

# 3. Send when satisfied
gmail draft send r123
```

### Batch drafts with script

```bash
#!/bin/bash
# Create multiple drafts
for email in user1@example.com user2@example.com user3@example.com; do
  gmail send \
    --to "$email" \
    --subject "Newsletter" \
    --body-file newsletter.md \
    --draft
done

# Show all created drafts
gmail draft list --json | jq '.drafts[].id'
```

## Error Handling

```bash
# Non-existent draft
gmail draft show invalid_id
# Draft 'invalid_id' not found

# Not authenticated
gmail draft list
# Error: Not authenticated. Run 'gmail auth login' first.
```
