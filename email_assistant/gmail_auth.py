import json
import os
from pathlib import Path

from email_assistant.config import CONFIG_DIR, get_settings, save_settings

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]


def get_service():
    token_file = CONFIG_DIR / "gmail_token.json"
    creds_file = CONFIG_DIR / "credentials.json"

    if not token_file.exists():
        return None

    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        token_file.write_text(creds.to_json())

    if not creds or not creds.valid:
        return None

    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=creds)


def authenticate(creds_path: str | None = None) -> bool:
    creds_file = Path(creds_path) if creds_path else CONFIG_DIR / "credentials.json"

    if not creds_file.exists():
        print(f"credentials.json not found at {creds_file}")
        print("Download it from https://console.cloud.google.com/apis/credentials")
        return False

    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
    creds = flow.run_local_server(port=0)

    token_file = CONFIG_DIR / "gmail_token.json"
    token_file.write_text(creds.to_json())
    print(f"Authenticated! Token saved to {token_file}")
    return True
