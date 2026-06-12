import json
from shared.llm import ask
from agent_leadgen.db import save_email, execute, DB_PATH

_SYSTEM = """You are a cold email copywriter. Write a short, personalized cold email (100-150 words).
Subject line should be specific, not generic. Body should reference the personalization context.
End with a soft CTA (30-min call or reply). Always include an unsubscribe line at the bottom.
Return JSON: {\"subject\": \"...\", \"body\": \"...\"}"""


def draft_email(lead: dict, sender_name: str = "Omer", sender_role: str = "Full-Stack Developer") -> int:
    enrichment = lead.get("enrichment") or f"They work as {lead['title']} at {lead['company']}."
    prompt = (
        f"Sender: {sender_name} ({sender_role})\n"
        f"Lead: {lead['first_name']} {lead['last_name']}, {lead['title']} @ {lead['company']}\n"
        f"Context: {enrichment}"
    )
    raw = ask(system=_SYSTEM, user=prompt, max_tokens=400)
    try:
        data = json.loads(raw)
        subject = data.get("subject", "Quick question")
        body = data.get("body", raw)
    except Exception:
        subject, body = "Quick question", raw
    email_id = save_email(lead["id"], subject, body)
    return email_id
