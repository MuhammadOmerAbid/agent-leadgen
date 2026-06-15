import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_init_db(tmp_path, monkeypatch):
    import agent_leadgen.db as db_mod
    test_db = str(tmp_path / "leadgen.db")
    monkeypatch.setattr(db_mod, "DB_PATH", test_db)
    db_mod.init_db()
    conn = sqlite3.connect(test_db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    assert {"campaigns", "leads", "emails", "approvals", "sent", "replies"}.issubset(tables)


def test_create_campaign_and_lead(tmp_path, monkeypatch):
    import agent_leadgen.db as db_mod
    test_db = str(tmp_path / "leadgen.db")
    monkeypatch.setattr(db_mod, "DB_PATH", test_db)
    db_mod.init_db()
    cid = db_mod.create_campaign("Test Campaign", "client")
    assert cid is not None
    lid = db_mod.save_lead(cid, "John", "Smith", "john@acme.com", "CTO", "Acme Inc")
    leads = db_mod.get_leads(cid)
    assert len(leads) == 1
    assert leads[0]["email"] == "john@acme.com"
