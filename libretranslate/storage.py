import redis

storage = None
def get_storage():
    return storage

class Storage:
    def exists(self, key):
        raise Exception("not implemented")

    def set_bool(self, key, value):
        raise Exception("not implemented")
    def get_bool(self, key):
        raise Exception("not implemented")

    def set_int(self, key, value):
        raise Exception("not implemented")
    def get_int(self, key):
        raise Exception("not implemented")

    def set_str(self, key, value):
        raise Exception("not implemented")
    def get_str(self, key):
        raise Exception("not implemented")

    def set_hash_int(self, ns, key, value):
        raise Exception("not implemented")
    def get_hash_int(self, ns, key):
        raise Exception("not implemented")
    def inc_hash_int(self, ns, key):
        raise Exception("not implemented")
    def dec_hash_int(self, ns, key):
        raise Exception("not implemented")

    def get_hash_keys(self, ns):
        raise Exception("not implemented")
    def del_hash(self, ns, key):
        raise Exception("not implemented")

class MemoryStorage(Storage):
    def __init__(self):
        self.store = {}

    def exists(self, key):
        return key in self.store

    def set_bool(self, key, value):
        self.store[key] = bool(value)

    def get_bool(self, key):
        return bool(self.store[key])

    def set_int(self, key, value):
        self.store[key] = int(value)

    def get_int(self, key):
        return int(self.store.get(key, 0))

    def set_str(self, key, value):
        self.store[key] = value

    def get_str(self, key):
        return str(self.store.get(key, ""))

    def set_hash_int(self, ns, key, value):
        if ns not in self.store:
            self.store[ns] = {}
        self.store[ns][key] = int(value)

    def get_hash_int(self, ns, key):
        d = self.store.get(ns, {})
        return int(d.get(key, 0))

    def inc_hash_int(self, ns, key):
        if ns not in self.store:
            self.store[ns] = {}

        if key not in self.store[ns]:
            self.store[ns][key] = 0
        else:
            self.store[ns][key] += 1

    def dec_hash_int(self, ns, key):
        if ns not in self.store:
            self.store[ns] = {}

        if key not in self.store[ns]:
            self.store[ns][key] = 0
        else:
            self.store[ns][key] -= 1

    def get_all_hash_int(self, ns):
        if ns in self.store:
            return [{str(k): int(v)} for k,v in self.store[ns].items()]
        else:
            return []

    def del_hash(self, ns, key):
        del self.store[ns][key]


class RedisStorage(Storage):
    def __init__(self, redis_uri):
        self.conn = redis.from_url(redis_uri)
        self.conn.ping()

    def exists(self, key):
        return bool(self.conn.exists(key))

    def set_bool(self, key, value):
        self.conn.set(key, "1" if value else "0")

    def get_bool(self, key):
        return bool(self.conn.get(key))

    def set_int(self, key, value):
        self.conn.set(key, str(value))

    def get_int(self, key):
        v = self.conn.get(key)
        if v is None:
            return 0
        else:
            return v

    def set_str(self, key, value):
        self.conn.set(key, value)

    def get_str(self, key):
        v = self.conn.get(key)
        if v is None:
            return ""
        else:
            return v.decode('utf-8')

    def get_hash_int(self, ns, key):
        v = self.conn.hget(ns, key)
        if v is None:
            return 0
        else:
            return int(v)

    def set_hash_int(self, ns, key, value):
        self.conn.hset(ns, key, value)

    def inc_hash_int(self, ns, key):
        return int(self.conn.hincrby(ns, key))

    def dec_hash_int(self, ns, key):
        return int(self.conn.hincrby(ns, key, -1))

    def get_all_hash_int(self, ns):
        return {k.decode("utf-8"): int(v) for k,v in self.conn.hgetall(ns).items()}

    def del_hash(self, ns, key):
        self.conn.hdel(ns, key)

def setup(storage_uri):
    global storage
    if storage_uri.startswith("memory://"):
        storage = MemoryStorage()
    elif storage_uri.startswith("redis://"):
        storage = RedisStorage(storage_uri)
    else:
        raise Exception("Invalid storage URI: " + storage_uri)

    return storage