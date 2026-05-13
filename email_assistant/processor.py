from email_assistant.provider import OpenCodeAPI
from email_assistant.prompts import build_prompt
from email_assistant.fetcher import Email


class EmailProcessor:
    def __init__(self):
        self.llm = OpenCodeAPI()

    def process(self, emails: list[Email]) -> list[dict]:
        if not emails:
            return []
        prompt = build_prompt(emails)
        results = self.llm.analyze(prompt)
        if not results:
            return [{"id": e.id, "summary": "(no analysis)", "category": "other", "urgency": "normal"} for e in emails]
        return results
