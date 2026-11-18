"""Local settings and diagnostic history. No network or telemetry."""
import json
import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def data_directory():
    root = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
    return Path(os.environ.get("CORESENSE_DATA_DIR", os.environ.get("FIXAI_DATA_DIR", root / "user_data")))


class LocalStore:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory is not None else data_directory()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.database = self.directory / "history.sqlite3"
        with closing(sqlite3.connect(self.database, isolation_level=None)) as db:
            db.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, updated TEXT NOT NULL, question TEXT NOT NULL, payload TEXT NOT NULL)")

    def settings(self):
        defaults = {"theme": "dark", "animations": True}
        try:
            value = json.loads((self.directory / "settings.json").read_text(encoding="utf-8"))
            if value.get("theme") in {"dark", "light", "system"}:
                defaults["theme"] = value["theme"]
            if isinstance(value.get("animations"), bool):
                defaults["animations"] = value["animations"]
        except (OSError, ValueError, AttributeError):
            pass
        return defaults

    def save_settings(self, settings):
        path = self.directory / "settings.json"
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(path)

    def save_session(self, session):
        payload = session.to_dict()
        with closing(sqlite3.connect(self.database, isolation_level=None)) as db:
            db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET updated=excluded.updated, question=excluded.question, payload=excluded.payload",
                       (session.id, datetime.now(timezone.utc).isoformat(), session.question,
                        json.dumps(payload, ensure_ascii=False)))

    def list_sessions(self, query=""):
        # Treat wildcard characters as literal user text.
        query = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        with closing(sqlite3.connect(self.database, isolation_level=None)) as db:
            return db.execute("SELECT id, updated, question FROM sessions WHERE question LIKE ? ESCAPE '\\' ORDER BY updated DESC", (f"%{query}%",)).fetchall()

    def load_session(self, session_id):
        with closing(sqlite3.connect(self.database, isolation_level=None)) as db:
            row = db.execute("SELECT payload FROM sessions WHERE id=?", (session_id,)).fetchone()
        return json.loads(row[0]) if row else None
