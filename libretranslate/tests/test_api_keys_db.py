import uuid

import pytest
import requests

from libretranslate.api_keys import Database, RemoteDatabase


@pytest.fixture()
def db(tmp_path):
    return Database(str(tmp_path / "api_keys.db"))


def test_add_generates_uuid_key(db):
    api_key, req_limit, char_limit = db.add(req_limit=120)

    uuid.UUID(api_key)
    assert req_limit == 120
    assert char_limit is None


def test_add_custom_key(db):
    api_key, _, _ = db.add(req_limit=60, api_key="my-key")
    assert api_key == "my-key"


def test_lookup(db):
    db.add(req_limit=120, api_key="k", char_limit=500)
    assert db.lookup("k") == (120, 500)


def test_lookup_missing_returns_none(db):
    assert db.lookup("missing") is None


def test_char_limit_zero_is_normalized_to_none(db):
    db.add(req_limit=10, api_key="k", char_limit=0)
    assert db.lookup("k") == (10, None)


def test_add_replaces_existing_key(db):
    db.add(req_limit=10, api_key="k")
    db.add(req_limit=99, api_key="k", char_limit=7)
    assert db.lookup("k") == (99, 7)


def test_remove(db):
    db.add(req_limit=10, api_key="k")
    db.remove("k")
    assert db.lookup("k") is None


def test_remove_missing_key_does_not_raise(db):
    db.remove("missing")


def test_all(db):
    db.add(req_limit=10, api_key="a")
    db.add(req_limit=20, api_key="b", char_limit=5)

    assert sorted(db.all()) == [("a", 10, None), ("b", 20, 5)]


def test_lookup_uses_cache(db):
    db.add(req_limit=10, api_key="k")
    assert db.lookup("k") == (10, None)

    db.c.execute("DELETE FROM api_keys WHERE api_key = 'k'")
    db.c.commit()

    assert db.lookup("k") == (10, None)


def test_lookup_cache_expires(tmp_path):
    db = Database(str(tmp_path / "api_keys.db"), max_cache_age=0)
    db.add(req_limit=10, api_key="k")
    db.lookup("k")

    db.c.execute("UPDATE api_keys SET req_limit = 42 WHERE api_key = 'k'")
    db.c.commit()

    assert db.lookup("k") == (42, None)


def _mock_remote(monkeypatch, payload):
    class FakeResponse:
        def json(self):
            return payload

    monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse())


def test_remote_lookup(monkeypatch):
    _mock_remote(monkeypatch, {"req_limit": 50, "char_limit": 1000})

    db = RemoteDatabase("https://example.com/keys")
    assert db.lookup("k") == (50, 1000)


def test_remote_lookup_error_response(monkeypatch):
    _mock_remote(monkeypatch, {"error": "invalid key"})

    db = RemoteDatabase("https://example.com/keys")
    assert db.lookup("k") is None


def test_remote_lookup_request_failure(monkeypatch):
    def fail(*a, **kw):
        raise requests.ConnectionError("unreachable")

    monkeypatch.setattr(requests, "post", fail)

    db = RemoteDatabase("https://example.com/keys")
    assert db.lookup("k") is None


def test_remote_lookup_uses_cache(monkeypatch):
    calls = []

    class FakeResponse:
        def json(self):
            return {"req_limit": 50, "char_limit": None}

    def post(*a, **kw):
        calls.append(1)
        return FakeResponse()

    monkeypatch.setattr(requests, "post", post)

    db = RemoteDatabase("https://example.com/keys")
    assert db.lookup("k") == (50, None)
    assert db.lookup("k") == (50, None)
    assert len(calls) == 1
