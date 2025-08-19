import sqlite3
from datetime import datetime


class SQLiteStorage:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                type TEXT,
                details TEXT
            )
        """)
        self.conn.commit()

    def log_event(self, event_type: str, details: dict):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO activity (time, type, details) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), event_type, str(details))
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
