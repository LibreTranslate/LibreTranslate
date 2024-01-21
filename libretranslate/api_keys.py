import os
import sqlite3
import uuid

import requests
from expiringdict import ExpiringDict

from libretranslate.default_values import DEFAULT_ARGUMENTS as DEFARGS

DEFAULT_DB_PATH = DEFARGS['API_KEYS_DB_PATH']


class Database:
    def __init__(self, db_path=DEFAULT_DB_PATH, max_cache_len=1000, max_cache_age=30):
        # Legacy check - this can be removed at some point in the near future
        if os.path.isfile("api_keys.db") and not os.path.isfile("db/api_keys.db"):
            print("Migrating {} to {}".format("api_keys.db", "db/api_keys.db"))
            try:
                os.rename("api_keys.db", "db/api_keys.db")
            except Exception as e:
                print(str(e))

        db_dir = os.path.dirname(db_path)
        if db_dir != '' and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self.db_path = db_path
        self.cache = ExpiringDict(max_len=max_cache_len, max_age_seconds=max_cache_age)

        # Make sure to do data synchronization on writes!
        self.c = sqlite3.connect(db_path, check_same_thread=False)
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS api_keys (
            "api_key"	TEXT NOT NULL,
            "req_limit"	INTEGER NOT NULL,
            "char_limit" INTEGER DEFAULT NULL,
            PRIMARY KEY("api_key")
        );"""
        )

        # Schema/upgrade checks
        schema = self.c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='api_keys';").fetchone()[0]
        if '"char_limit" INTEGER DEFAULT NULL' not in schema:
            self.c.execute('ALTER TABLE api_keys ADD COLUMN "char_limit" INTEGER DEFAULT NULL;')

    def lookup(self, api_key):
        val = self.cache.get(api_key)
        if val is None:
            # DB Lookup
            stmt = self.c.execute(
                "SELECT req_limit, char_limit FROM api_keys WHERE api_key = ?", (api_key,)
            )
            row = stmt.fetchone()
            if row is not None:
                self.cache[api_key] = row
                val = row
            else:
                self.cache[api_key] = False
                val = False

        if isinstance(val, bool):
            val = None

        return val

    def add(self, req_limit, api_key="auto", char_limit=None):
        if api_key == "auto":
            api_key = str(uuid.uuid4())
        if char_limit == 0:
            char_limit = None

        self.remove(api_key)
        self.c.execute(
            "INSERT INTO api_keys (api_key, req_limit, char_limit) VALUES (?, ?, ?)",
            (api_key, req_limit, char_limit),
        )
        self.c.commit()
        return (api_key, req_limit, char_limit)

    def remove(self, api_key):
        self.c.execute("DELETE FROM api_keys WHERE api_key = ?", (api_key,))
        self.c.commit()
        return api_key

    def all(self):
        row = self.c.execute("SELECT api_key, req_limit, char_limit FROM api_keys")
        return row.fetchall()


class RemoteDatabase:
    def __init__(self, url, max_cache_len=1000, max_cache_age=600):
        self.url = url
        self.cache = ExpiringDict(max_len=max_cache_len, max_age_seconds=max_cache_age)

    def lookup(self, api_key):
        val = self.cache.get(api_key)
        if val is None:
            try:
                r = requests.post(self.url, data={'api_key': api_key}, timeout=60)
                res = r.json()
            except Exception as e:
                print("Cannot authenticate API key: " + str(e))
                return None

            if res.get('error') is not None:
                return None

            req_limit = res.get('req_limit', None)
            char_limit = res.get('char_limit', None)

            self.cache[api_key] = (req_limit, char_limit)

        return val
