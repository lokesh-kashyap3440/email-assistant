# Email Assistant

AI-powered email assistant for your terminal — summarizes, categorizes, extracts action items, and suggests replies. Uses the **OpenCode server API** as the LLM backend.

## Quick Start

```bash
# 1. Start OpenCode server (the LLM backend)
opencode serve

# 2a. Setup with Composio (recommended if you already use Composio)
email-assistant setup --composio

# 2b. Or setup with Gmail API directly
email-assistant setup --creds path/to/credentials.json

# 3. Analyze your inbox
email-assistant inbox
```

## Commands

| Command | Description |
|---------|-------------|
| `inbox` | Fetch + AI-analyze your inbox (summary, category, urgency, action items, reply drafts) |
| `summarize` | Quick listing of recent emails (no AI) |
| `config` | Change settings (host, port, password, backend) |
| `setup` | One-time auth |

## Backends

Two email backends are supported:

| Backend | Setup | Pros |
|---------|-------|------|
| `composio` | Already connected? Just `email-assistant setup --composio` | No Google Cloud project needed |
| `gmail_api` | `email-assistant setup --creds credentials.json` | No third-party dependency |

Switch between them:
```bash
email-assistant config --backend composio
email-assistant config --backend gmail_api
```

## Options

```bash
email-assistant inbox --count 5          # Last 5 emails
email-assistant inbox --unread           # Unread only
email-assistant config --host 10.0.0.5 --port 4096   # Remote OpenCode server
email-assistant config --backend composio            # Switch to Composio
```

## Architecture

```
Gmail (Composio SDK / Google API) → fetcher.py
    → processor.py (via OpenCode server API)
        → CLI output (rich panels with colors + urgency icons)
```
