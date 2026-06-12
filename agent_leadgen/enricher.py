import json
from shared.llm import ask
from shared.db import execute
from agent_leadgen.db import DB_PATH

_SYSTEM = """You are a lead researcher. Given a person's name, title, and company, write 2-3 sentences
of personalization context for a cold email: reference something specific about their role, company, or industry.
Return only the personalization text, nothing else."""


def enrich_lead(lead: dict) -> str:
    prompt = (
        f"Name: {lead['first_name']} {lead['last_name']}\n"
        f"Title: {lead['title']}\n"
        f"Company: {lead['company']}"
    )
    context = ask(system=_SYSTEM, user=prompt, max_tokens=150)
    execute(DB_PATH, "UPDATE leads SET enrichment = ? WHERE id = ?", (context, lead["id"]))
    return context
