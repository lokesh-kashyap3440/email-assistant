import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "email-assistant"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "gmail_token.json"
CREDS_FILE = CONFIG_DIR / "credentials.json"

DEFAULTS = {
    "opencode_host": "127.0.0.1",
    "opencode_port": 4096,
    "opencode_password": "",
    "backend": "gmail_api",
}


def get_settings() -> dict:
    s = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        s.update(json.loads(CONFIG_FILE.read_text()))
    return s


def save_settings(s: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(s, indent=2))
