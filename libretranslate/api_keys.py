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
            PRIMARY KEY("api_key")
        );"""
        )

    def lookup(self, api_key):
        req_limit = self.cache.get(api_key)
        if req_limit is None:
            # DB Lookup
            stmt = self.c.execute(
                "SELECT req_limit FROM api_keys WHERE api_key = ?", (api_key,)
            )
            row = stmt.fetchone()
            if row is not None:
                self.cache[api_key] = row[0]
                req_limit = row[0]
            else:
                self.cache[api_key] = False
                req_limit = False

        if isinstance(req_limit, bool):
            req_limit = None

        return req_limit

    def add(self, req_limit, api_key="auto"):
        if api_key == "auto":
            api_key = str(uuid.uuid4())

        self.remove(api_key)
        self.c.execute(
            "INSERT INTO api_keys (api_key, req_limit) VALUES (?, ?)",
            (api_key, req_limit),
        )
        self.c.commit()
        return (api_key, req_limit)

    def remove(self, api_key):
        self.c.execute("DELETE FROM api_keys WHERE api_key = ?", (api_key,))
        self.c.commit()
        return api_key

    def all(self):
        row = self.c.execute("SELECT api_key, req_limit FROM api_keys")
        return row.fetchall()


class RemoteDatabase:
    def __init__(self, url, max_cache_len=1000, max_cache_age=600):
        self.url = url
        self.cache = ExpiringDict(max_len=max_cache_len, max_age_seconds=max_cache_age)

    def lookup(self, api_key):
        req_limit = self.cache.get(api_key)
        if req_limit is None:
            try:
                r = requests.post(self.url, data={'api_key': api_key}, timeout=60)
                res = r.json()
            except Exception as e:
                print("Cannot authenticate API key: " + str(e))
                return None

            req_limit = res.get('req_limit', None) if res.get('error', None) is None else None
            self.cache[api_key] = req_limit

        return req_limit
