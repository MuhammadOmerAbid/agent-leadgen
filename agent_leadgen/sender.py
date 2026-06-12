import requests
from shared.config import INSTANTLY_API_KEY, SMARTLEAD_API_KEY, SENDING_DOMAIN, DAILY_SEND_CAP
from shared.db import execute
from agent_leadgen.db import DB_PATH, get_approved_emails


def _send_via_instantly(to_email: str, subject: str, body: str) -> bool:
    if not INSTANTLY_API_KEY:
        return False
    payload = {
        "api_key": INSTANTLY_API_KEY,
        "from_email": f"outreach@{SENDING_DOMAIN}",
        "to": to_email,
        "subject": subject,
        "body": body,
    }
    resp = requests.post("https://api.instantly.ai/api/v1/email/send", json=payload, timeout=15)
    return resp.status_code == 200


def send_approved(dry_run: bool = False) -> int:
    emails = get_approved_emails()
    sent_count = 0
    for email in emails:
        if sent_count >= DAILY_SEND_CAP:
            print(f"Daily cap ({DAILY_SEND_CAP}) reached — stopping.")
            break
        if dry_run:
            print(f"[DRY RUN] Would send to lead_id={email['lead_id']}: {email['subject']}")
            sent_count += 1
            continue
        ok = _send_via_instantly("placeholder@example.com", email["subject"], email["body"])
        if ok:
            execute(DB_PATH, "INSERT INTO sent (email_id) VALUES (?)", (email["id"],))
            execute(DB_PATH, "UPDATE approvals SET status = 'sent' WHERE email_id = ?", (email["id"],))
            sent_count += 1
    return sent_count
