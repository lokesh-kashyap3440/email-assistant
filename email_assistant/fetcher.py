from dataclasses import dataclass, field
from datetime import datetime
from email_assistant.config import get_settings


@dataclass
class Email:
    id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    timestamp: str
    labels: list[str] = field(default_factory=list)
    body_preview: str = ""
    body_text: str = ""
    display_url: str = ""

    @property
    def datetime(self) -> datetime | None:
        try:
            if self.timestamp.isdigit():
                return datetime.fromtimestamp(int(self.timestamp) / 1000)
            return datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except Exception:
            return None

    @property
    def is_unread(self) -> bool:
        return "UNREAD" in self.labels

    @property
    def is_important(self) -> bool:
        return "IMPORTANT" in self.labels

    @property
    def category(self) -> str:
        for c in ("CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_UPDATES", "CATEGORY_FORUMS", "CATEGORY_PERSONAL"):
            if c in self.labels:
                return c.removeprefix("CATEGORY_").lower()
        return "inbox"


def create_fetcher():
    s = get_settings()
    backend = s.get("backend", "gmail_api")

    if backend == "composio":
        return ComposioFetcher()
    return GmailAPIFetcher()


class GmailAPIFetcher:
    def __init__(self, service=None):
        self.service = service
        if not service:
            from email_assistant.gmail_auth import get_service
            self.service = get_service()

    def fetch(self, max_results: int = 10, query: str = "") -> list[Email]:
        if not self.service:
            raise RuntimeError(
                "Gmail API not authenticated.\n"
                "  Run: email-assistant setup --creds path/to/credentials.json"
            )
        return self._fetch_api(max_results, query)

    def _fetch_api(self, max_results: int, query: str) -> list[Email]:
        messages = []
        page_token = None
        while len(messages) < max_results:
            resp = self.service.users().messages().list(
                userId="me", q=query, maxResults=min(500, max_results),
                pageToken=page_token,
            ).execute()
            messages.extend(resp.get("messages", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        emails = []
        for msg in messages[:max_results]:
            detail = self.service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            ).execute()
            headers = {h["name"].lower(): h["value"] for h in detail.get("payload", {}).get("headers", [])}
            emails.append(Email(
                id=detail["id"],
                thread_id=detail["threadId"],
                subject=headers.get("subject", "(no subject)"),
                sender=headers.get("from", ""),
                recipient=headers.get("to", ""),
                timestamp=detail.get("internalDate", ""),
                labels=detail.get("labelIds", []),
                body_preview=detail.get("snippet", ""),
                display_url=f"https://mail.google.com/mail/u/0/#inbox/{detail['id']}",
            ))
        return emails


class ComposioFetcher:
    def __init__(self):
        pass

    def fetch(self, max_results: int = 10, query: str = "") -> list[Email]:
        from email_assistant import composio_api as ca
        if not ca.is_available():
            raise RuntimeError(
                "Composio API key not set.\n"
                "  Set it: email-assistant config --composio-key YOUR_KEY\n"
                "  Or switch: email-assistant config --backend gmail_api"
            )
        return ca.fetch_emails(max_results=max_results)
