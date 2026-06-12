import os
import sqlite3
from shared.db import execute, fetchall, fetchone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leadgen.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                title TEXT,
                company TEXT,
                enrichment TEXT,
                email_verified INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                subject TEXT,
                body TEXT,
                status TEXT DEFAULT 'draft',
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER UNIQUE,
                status TEXT DEFAULT 'pending',
                updated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                sent_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                body TEXT,
                draft_reply TEXT,
                received_at TEXT DEFAULT (datetime('now'))
            );
        """)


def create_campaign(name: str, campaign_type: str) -> int:
    execute(DB_PATH, "INSERT OR IGNORE INTO campaigns (name, type) VALUES (?, ?)", (name, campaign_type))
    row = fetchone(DB_PATH, "SELECT id FROM campaigns WHERE name = ?", (name,))
    return row["id"]


def get_campaign(name: str) -> dict | None:
    return fetchone(DB_PATH, "SELECT * FROM campaigns WHERE name = ?", (name,))


def save_lead(campaign_id: int, first_name: str, last_name: str, email: str, title: str, company: str) -> int:
    execute(DB_PATH,
        "INSERT INTO leads (campaign_id, first_name, last_name, email, title, company) VALUES (?,?,?,?,?,?)",
        (campaign_id, first_name, last_name, email, title, company))
    row = fetchone(DB_PATH, "SELECT last_insert_rowid() AS id")
    return row["id"]


def get_leads(campaign_id: int) -> list[dict]:
    return fetchall(DB_PATH, "SELECT * FROM leads WHERE campaign_id = ?", (campaign_id,))


def save_email(lead_id: int, subject: str, body: str) -> int:
    execute(DB_PATH, "INSERT INTO emails (lead_id, subject, body) VALUES (?,?,?)", (lead_id, subject, body))
    row = fetchone(DB_PATH, "SELECT last_insert_rowid() AS id")
    return row["id"]


def get_approved_emails() -> list[dict]:
    return fetchall(DB_PATH,
        "SELECT e.*, a.status FROM emails e JOIN approvals a ON e.id = a.email_id WHERE a.status = 'approved'")


def list_campaigns() -> list[dict]:
    return fetchall(DB_PATH, "SELECT * FROM campaigns ORDER BY id DESC")
