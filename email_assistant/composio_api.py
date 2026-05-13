import os
from email_assistant.fetcher import Email
from email_assistant.config import get_settings


def is_available() -> bool:
    return bool(get_settings().get("composio_key") or os.environ.get("COMPOSIO_API_KEY"))


def fetch_emails(max_results: int = 10) -> list[Email]:
    raise RuntimeError(
        "Composio backend not yet supported with this tool.\n"
        "Switch to Gmail API: email-assistant config --backend gmail_api\n"
        "Then run: email-assistant setup --creds path/to/credentials.json"
    )
