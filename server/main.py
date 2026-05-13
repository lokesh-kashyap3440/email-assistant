import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any
import traceback

from email_assistant.fetcher import GmailAPIFetcher, Email
from email_assistant.processor import EmailProcessor
from email_assistant.provider import OpenCodeAPI
from email_assistant.config import get_settings, save_settings
from email_assistant.gmail_auth import authenticate, get_service

app = FastAPI(title="Email Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend), html=True), name="frontend")


class AnalyzeRequest(BaseModel):
    emails: list[dict[str, Any]]


class ConfigUpdate(BaseModel):
    config: dict[str, Any]


class AuthSetup(BaseModel):
    creds_path: str = ""


def _email_to_dict(e: Email) -> dict:
    return {
        "id": e.id,
        "subject": e.subject,
        "sender": e.sender,
        "timestamp": e.timestamp,
        "body_preview": e.body_preview,
        "labels": e.labels,
        "is_unread": e.is_unread,
        "is_important": e.is_important,
    }


def _email_from_dict(d: dict) -> Email:
    return Email(
        id=d.get("id", ""),
        thread_id=d.get("thread_id", ""),
        subject=d.get("subject", "(no subject)"),
        sender=d.get("sender", ""),
        recipient=d.get("recipient", ""),
        timestamp=d.get("timestamp", ""),
        labels=d.get("labels", []),
        body_preview=d.get("body_preview", ""),
        body_text=d.get("body_text", ""),
        display_url=d.get("display_url", ""),
    )


@app.get("/api/health")
def health():
    try:
        llm = OpenCodeAPI()
        ok = llm.check()
    except Exception:
        ok = False
    return {"status": "ok", "opencode": ok}


@app.get("/api/emails")
def list_emails(count: int = Query(10, ge=1, le=100), unread: bool = Query(False)):
    try:
        fetcher = GmailAPIFetcher()
        query = "is:unread" if unread else ""
        emails = fetcher.fetch(max_results=count, query=query)
        return {"emails": [_email_to_dict(e) for e in emails]}
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        emails = [_email_from_dict(d) for d in req.emails]
        processor = EmailProcessor()
        results = processor.process(emails)
        return {"results": results}
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.get("/api/config")
def config_get():
    try:
        s = get_settings()
        safe = {k: v for k, v in s.items() if "password" not in k.lower() and "token" not in k.lower() and "key" not in k.lower() and "secret" not in k.lower()}
        return {"config": safe}
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.post("/api/config")
def config_update(req: ConfigUpdate):
    try:
        current = get_settings()
        current.update(req.config)
        save_settings(current)
        safe = {k: v for k, v in current.items() if "password" not in k.lower() and "token" not in k.lower() and "key" not in k.lower() and "secret" not in k.lower()}
        return {"config": safe}
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.get("/api/auth/status")
def auth_status():
    try:
        svc = get_service()
        return {"authenticated": svc is not None}
    except Exception:
        return {"authenticated": False}


@app.post("/api/auth/setup")
def auth_setup(req: AuthSetup):
    try:
        ok = authenticate(req.creds_path or None)
        return {"success": ok}
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.get("/api/inbox")
def inbox(count: int = Query(10, ge=1, le=100), unread: bool = Query(False)):
    try:
        fetcher = GmailAPIFetcher()
        query = "is:unread" if unread else ""
        emails = fetcher.fetch(max_results=count, query=query)

        processor = EmailProcessor()
        analysis = processor.process(emails)

        analysis_by_id = {a.get("id", ""): a for a in analysis}

        combined = []
        for e in emails:
            item = _email_to_dict(e)
            a = analysis_by_id.get(e.id, {})
            item["analysis"] = a
            combined.append(item)

        return {"emails": combined}
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())
