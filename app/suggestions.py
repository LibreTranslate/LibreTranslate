import sqlite3
import uuid

from expiringdict import ExpiringDict

DEFAULT_DB_PATH = "suggestions.db"


class Database:
    def __init__(self, db_path=DEFAULT_DB_PATH, max_cache_len=1000, max_cache_age=30):
        self.db_path = db_path
        self.cache = ExpiringDict(max_len=max_cache_len, max_age_seconds=max_cache_age)

        # Make sure to do data synchronization on writes!
        self.c = sqlite3.connect(db_path, check_same_thread=False)
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS suggestions (
            "q"	TEXT NOT NULL,
            "s"	TEXT NOT NULL,
            "source"	TEXT NOT NULL,
            "target"	TEXT NOT NULL
        );"""
        )

    def add(self, q, s, source, target):
        self.c.execute(
            "INSERT INTO suggestions (q, s, source, target) VALUES (?, ?, ?, ?)",
            (q, s, source, target),
        )
        self.c.commit()
        return True
