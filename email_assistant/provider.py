import httpx, json, re
from email_assistant.config import get_settings
from email_assistant.prompts import SYSTEM_PROMPT_TEMPLATE


class OpenCodeAPI:
    def __init__(self):
        s = get_settings()
        self.base_url = f"http://{s.get('opencode_host', '127.0.0.1')}:{s.get('opencode_port', 4096)}"
        password = s.get("opencode_password", "")
        self._headers = {"Content-Type": "application/json"}
        if password:
            import base64
            token = base64.b64encode(f"opencode:{password}".encode()).decode()
            self._headers["Authorization"] = f"Basic {token}"

    def _post(self, path: str, body: dict) -> dict:
        with httpx.Client(base_url=self.base_url, headers=self._headers, timeout=300) as c:
            r = c.post(path, json=body)
            r.raise_for_status()
            return r.json()

    def _get(self, path: str) -> dict:
        with httpx.Client(base_url=self.base_url, headers=self._headers, timeout=10) as c:
            r = c.get(path)
            r.raise_for_status()
            return r.json()

    def check(self) -> bool:
        try:
            return self._get("/global/health").get("healthy", False)
        except Exception:
            return False

    def analyze(self, emails_text: str) -> list[dict]:
        session = self._post("/session", {"title": "email-assistant"})
        sid = session["id"]

        body = {
            "parts": [{"type": "text", "text": emails_text}],
            "system": SYSTEM_PROMPT_TEMPLATE,
        }
        result = self._post(f"/session/{sid}/message", body)

        raw = ""
        for p in result.get("parts", []):
            if p.get("type") == "text":
                raw += p.get("text", "")
            elif p.get("type") == "tool_use":
                try:
                    raw += json.dumps(p.get("input", {}))
                except Exception:
                    pass

        error = result.get("info", {}).get("error", {})
        if error:
            raise RuntimeError(f"LLM error: {error.get('name', '')} - {error.get('data', {}).get('message', str(error))}")

        return self._parse_json(raw)

    def _parse_json(self, text: str) -> list[dict]:
        text = text.strip()
        if not text:
            return []

        code_block = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if code_block:
            text = code_block.group(1).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                data = json.loads(text[start:end])
            except (ValueError, json.JSONDecodeError):
                raise RuntimeError(f"Failed to parse LLM response as JSON:\n{text[:1000]}")

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("emails", "results", "items", "data"):
                if key in data:
                    return data[key]
        raise RuntimeError(f"Unexpected JSON structure from LLM:\n{json.dumps(data)[:500]}")
