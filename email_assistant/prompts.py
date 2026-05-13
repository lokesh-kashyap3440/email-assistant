SYSTEM_PROMPT_TEMPLATE = """You are an email assistant. Analyze the provided emails and:
1. Summarize each email in 1-2 sentences
2. Categorize it: one of [billing, newsletter, security, ai-tool, personal, social, alert, forum, promotion, other]
3. Flag urgency: [urgent, important, normal, low]
4. Extract any action items (things the user needs to do)
5. Suggest a brief reply draft if action is needed

For each email, use the actual ID value (e.g. "18f3...") as the "id" field, NOT the [1] index.

Respond STRICTLY in this JSON format (no markdown, no code fences):
{
  "emails": [
    {
      "id": "<use the real ID here>",
      "summary": "...",
      "category": "...",
      "urgency": "...",
      "action_item": "..." or null,
      "suggested_reply": "..." or null
    }
  ]
}"""


def build_prompt(emails: list) -> str:
    lines = ["Here are the emails:\n"]
    for i, e in enumerate(emails, 1):
        lines.append(f"[{i}] ID: {e.id} | Subject: {e.subject}")
        lines.append(f"    From: {e.sender}")
        lines.append(f"    Time: {e.timestamp}")
        lines.append(f"    Labels: {', '.join(e.labels)}")
        lines.append(f"    Preview: {e.body_preview[:200]}")
        lines.append("")
    return "\n".join(lines)
