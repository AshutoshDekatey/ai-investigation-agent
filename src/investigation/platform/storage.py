"""Durable report storage; PostgreSQL production-local, SQLite explicit dev mode."""
import json
import sqlite3
from pathlib import Path

class Reports:
    def __init__(self, dsn=None, path=".cache/reports.sqlite"):
        self.pg = bool(dsn)
        if self.pg:
            import psycopg
            self.db = psycopg.connect(dsn, autocommit=True)
        else:
            Path(path).parent.mkdir(parents=True,exist_ok=True)
            self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS investigations (id TEXT PRIMARY KEY, report TEXT NOT NULL)")
        self.db.commit()

    def save(self, report):
        marker = "%s" if self.pg else "?"
        self.db.execute(f"INSERT INTO investigations VALUES ({marker},{marker}) ON CONFLICT(id) DO UPDATE SET report=excluded.report", (report["investigation_id"],json.dumps(report)))
        self.db.commit()

    def get(self, investigation_id):
        marker = "%s" if self.pg else "?"
        row = self.db.execute(f"SELECT report FROM investigations WHERE id={marker}",(investigation_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def close(self):
        self.db.close()
