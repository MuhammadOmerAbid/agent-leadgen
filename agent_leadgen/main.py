"""agent-leadgen CLI

Usage:
  python agent_leadgen/main.py campaign create --type client --name "US Startups June"
  python agent_leadgen/main.py campaign list
  python agent_leadgen/main.py leads pull --campaign "US Startups June"
  python agent_leadgen/main.py leads import --file professors.csv --campaign "UK Professors"
  python agent_leadgen/main.py enrich --campaign "US Startups June"
  python agent_leadgen/main.py send --campaign "US Startups June" [--dry-run]
"""
import sys
import csv
from agent_leadgen.db import init_db, create_campaign, get_campaign, get_leads, list_campaigns, save_lead
from agent_leadgen.apollo import pull_leads
from agent_leadgen.enricher import enrich_lead
from agent_leadgen.drafter import draft_email
from agent_leadgen.sender import send_approved
from shared.approval import send_for_approval
import asyncio


def _get_arg(args: list[str], flag: str) -> str | None:
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return None


def cmd_campaign(args: list[str]) -> None:
    if not args:
        print("Subcommand: create | list")
        return
    sub = args[0]
    if sub == "create":
        name = _get_arg(args, "--name")
        ctype = _get_arg(args, "--type") or "client"
        if not name:
            print("--name required")
            return
        cid = create_campaign(name, ctype)
        print(f"Campaign created: '{name}' (id={cid}, type={ctype})")
    elif sub == "list":
        for c in list_campaigns():
            print(f"[{c['id']}] {c['name']} ({c['type']})")


def cmd_leads(args: list[str]) -> None:
    sub = args[0] if args else ""
    if sub == "pull":
        name = _get_arg(args, "--campaign")
        campaign = get_campaign(name)
        if not campaign:
            print(f"Campaign '{name}' not found.")
            return
        titles = ["CTO", "Founder", "Tech Lead", "VP Engineering"]
        count = pull_leads(campaign["id"], titles, ["1,10", "11,50"])
        print(f"Pulled {count} leads into '{name}'.")
    elif sub == "import":
        filepath = _get_arg(args, "--file")
        name = _get_arg(args, "--campaign")
        campaign = get_campaign(name)
        if not campaign or not filepath:
            print("--file and --campaign required")
            return
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                save_lead(
                    campaign_id=campaign["id"],
                    first_name=row.get("first_name", ""),
                    last_name=row.get("last_name", ""),
                    email=row.get("email", ""),
                    title=row.get("title", ""),
                    company=row.get("company", ""),
                )
                count += 1
        print(f"Imported {count} leads into '{name}'.")


def cmd_enrich(args: list[str]) -> None:
    name = _get_arg(args, "--campaign")
    campaign = get_campaign(name)
    if not campaign:
        print(f"Campaign '{name}' not found.")
        return
    leads = get_leads(campaign["id"])
    for lead in leads:
        enrich_lead(lead)
        email_id = draft_email(lead)
        msg = (
            f"*New Draft* — {lead['first_name']} {lead['last_name']}, {lead['title']} @ {lead['company']}\n"
            f"Email id: {email_id}"
        )
        asyncio.run(send_for_approval(msg, str(email_id)))
    print(f"Enriched and drafted {len(leads)} leads. Check Telegram for approval.")


def cmd_send(args: list[str]) -> None:
    dry_run = "--dry-run" in args
    sent = send_approved(dry_run=dry_run)
    label = "[DRY RUN] " if dry_run else ""
    print(f"{label}Sent {sent} emails.")


if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    cmd = argv[0]
    rest = argv[1:]
    init_db()
    if cmd == "campaign":
        cmd_campaign(rest)
    elif cmd == "leads":
        cmd_leads(rest)
    elif cmd == "enrich":
        cmd_enrich(rest)
    elif cmd == "send":
        cmd_send(rest)
    else:
        print(__doc__)
        sys.exit(1)
