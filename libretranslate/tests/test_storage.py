import pytest

from libretranslate.storage import MemoryStorage


@pytest.fixture()
def storage():
    return MemoryStorage()


def test_bool_roundtrip(storage):
    storage.set_bool("k", True)
    assert storage.get_bool("k") is True

    storage.set_bool("k", False)
    assert storage.get_bool("k") is False


def test_int_roundtrip(storage):
    storage.set_int("k", 42)
    assert storage.get_int("k") == 42


def test_int_missing_defaults_to_zero(storage):
    assert storage.get_int("missing") == 0


def test_str_roundtrip(storage):
    storage.set_str("k", "value")
    assert storage.get_str("k") == "value"


def test_str_missing_defaults_to_empty(storage):
    assert storage.get_str("missing") == ""


def test_str_expired_returns_empty(storage):
    storage.set_str("k", "value", ex=0)
    assert storage.get_str("k") == ""
    assert not storage.exists("k")


def test_hash_int_roundtrip(storage):
    storage.set_hash_int("ns", "k", 5)
    assert storage.get_hash_int("ns", "k") == 5


def test_hash_int_missing_defaults_to_zero(storage):
    assert storage.get_hash_int("ns", "missing") == 0


def test_inc_hash_int(storage):
    assert storage.inc_hash_int("ns", "k") == 1
    assert storage.inc_hash_int("ns", "k") == 2
    assert storage.get_hash_int("ns", "k") == 2


def test_dec_hash_int(storage):
    storage.set_hash_int("ns", "k", 3)
    assert storage.dec_hash_int("ns", "k") == 2
    assert storage.get_hash_int("ns", "k") == 2


def test_get_all_hash_int(storage):
    storage.set_hash_int("ns", "a", 1)
    storage.set_hash_int("ns", "b", 2)

    assert storage.get_all_hash_int("ns") == {"a": 1, "b": 2}


def test_get_all_hash_int_missing(storage):
    assert storage.get_all_hash_int("ns") == {}


def test_del_hash(storage):
    storage.set_hash_int("ns", "k", 1)
    storage.del_hash("ns", "k")
    assert storage.get_hash_int("ns", "k") == 0
