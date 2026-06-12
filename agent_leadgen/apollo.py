import requests
from shared.config import APOLLO_API_KEY
from agent_leadgen.db import save_lead

APOLLO_URL = "https://api.apollo.io/v1/mixed_people/search"


def pull_leads(campaign_id: int, titles: list[str], company_size: list[str], limit: int = 25) -> int:
    if not APOLLO_API_KEY:
        raise RuntimeError("APOLLO_API_KEY not set")
    payload = {
        "api_key": APOLLO_API_KEY,
        "person_titles": titles,
        "organization_num_employees_ranges": company_size,
        "page": 1,
        "per_page": limit,
    }
    resp = requests.post(APOLLO_URL, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    count = 0
    for person in data.get("people", []):
        email = (person.get("email") or "").strip()
        if not email:
            continue
        save_lead(
            campaign_id=campaign_id,
            first_name=person.get("first_name", ""),
            last_name=person.get("last_name", ""),
            email=email,
            title=person.get("title", ""),
            company=(person.get("organization") or {}).get("name", ""),
        )
        count += 1
    return count
