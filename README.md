# Agent 2 — Lead Gen + Enrichment Engine

Finds prospects (clients or professors), enriches their profiles, drafts personalized cold emails, gets your Telegram approval, then sends via Instantly/Smartlead. Tracks replies and drafts suggested responses.

**Part of:** [AI Outreach System](../ai-outreach-system/)

---

## What It Does

1. You define a campaign (Clients or Professors) and your target profile (ICP)
2. Leads are pulled — Apollo API for clients; CSV/manual import for professors
3. Each lead is verified (email validation) and enriched (recent activity, papers, etc.)
4. Claude drafts a personalized first email + follow-up sequence referencing something specific about each person
5. Drafts go to you for approval (batch approve via Telegram or a simple review table)
6. Approved sequences are sent via Instantly or Smartlead API — from warmed, separate sending domains only
7. Replies are tracked; when one arrives, Claude drafts a suggested reply for your approval

**No email is ever sent without your explicit approval.**

---

## Two Campaign Types

### Campaign A — Client Outreach
- Target: startup founders, CTOs, tech leads who need web development
- Source: Apollo API (search by industry, company size, title, location)
- Personalization: recent company news, product launches, funding rounds

### Campaign B — Professor Outreach
- Target: foreign university professors for academic collaboration / research
- Source: CSV import from faculty pages or Google Scholar exports
- Personalization: references their most recent published paper or research area

---

## Setup

```bash
# Inside ai-outreach-system/
pip install -r requirements.txt
cp .env.example .env
# Fill in all keys in .env
```

---

## Usage

```bash
# Create a new campaign
python agent_leadgen/main.py campaign create --type client --name "US Startups June"

# Pull leads (Apollo for clients)
python agent_leadgen/main.py leads pull --campaign "US Startups June"

# Import professors from CSV
python agent_leadgen/main.py leads import --file professors.csv --campaign "UK Professors"

# Enrich and draft emails (sends to Telegram for approval)
python agent_leadgen/main.py enrich --campaign "US Startups June"

# View pending approvals (web table)
python agent_leadgen/main.py review

# Send approved sequences
python agent_leadgen/main.py send --campaign "US Startups June"
```

---

## Email Safety (Enforced in Code)

| Rule | Default |
|------|---------|
| Sending domain | Separate domain only — never your main domain |
| Warm-up | Must be completed before any send (assumed done in Instantly/Smartlead) |
| Daily send cap per inbox | 30 emails max |
| Email verification | Required — bounces blocked before send |
| Unsubscribe link | Included in every email automatically |
| Human approval gate | Required before every send — no exceptions |

---

## Environment Variables Needed

```
ANTHROPIC_API_KEY=         # https://console.anthropic.com
TELEGRAM_BOT_TOKEN=        # Create bot via @BotFather on Telegram
TELEGRAM_CHAT_ID=          # Your personal Telegram chat ID
APOLLO_API_KEY=            # https://developer.apollo.io
INSTANTLY_API_KEY=         # https://app.instantly.ai  (or use Smartlead)
SMARTLEAD_API_KEY=         # https://app.smartlead.ai  (alternative to Instantly)
SENDING_DOMAIN=            # Your separate cold-email domain (NOT your main domain)
DAILY_SEND_CAP=30          # Max emails per inbox per day
```

---

## Database

SQLite file: `data/leadgen.db`

Tables:
- `campaigns` — campaign definitions and settings
- `leads` — all prospects with enrichment data
- `emails` — drafted email sequences per lead
- `approvals` — approval status per email
- `sent` — send history with timestamps
- `replies` — incoming replies and AI-drafted responses

---

## Approval Flow (Telegram)

```
📧 New batch ready for approval — "US Startups June"
5 emails drafted

Lead 1: John Smith, CTO @ Acme Inc
Subject: Your recent product launch + a quick idea

"Hi John, saw that Acme just launched..."
[Full email in message]

[✅ Approve] [✏️ Edit] [🚫 Skip]
```

---

## Schedule

- Lead pull: configurable (e.g. weekly)
- Send: configurable (e.g. weekdays 9 AM–12 PM, respecting daily cap)
- Reply check: every 2 hours during business hours

Configurable in `agent_leadgen/config/schedule.py`.

---

## Safety

- Official APIs only — no scraping of Apollo, LinkedIn, or professor sites
- Separate sending domains enforced — code checks and blocks sends from main domain
- Per-inbox daily cap enforced — code stops sending when cap is reached
- Unsubscribe handling — opt-outs are logged and respected automatically
- Every single outbound action requires your approval first
