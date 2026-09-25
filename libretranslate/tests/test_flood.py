from types import SimpleNamespace

import pytest

from libretranslate import flood, storage


@pytest.fixture()
def mem_storage():
    return storage.setup("memory://")


@pytest.fixture()
def flood_active(mem_storage):
    flood.setup(SimpleNamespace(req_flood_threshold=2))
    yield
    flood.active = False
    flood.threshold = -1


def test_inactive_by_default(mem_storage):
    flood.report("1.2.3.4")
    assert not flood.is_banned("1.2.3.4")


def test_report_and_ban(flood_active):
    flood.report("1.2.3.4")
    assert flood.has_violation("1.2.3.4")
    assert not flood.is_banned("1.2.3.4")

    flood.report("1.2.3.4")
    assert flood.is_banned("1.2.3.4")


def test_violations_are_per_ip(flood_active):
    flood.report("1.2.3.4")
    assert not flood.has_violation("5.6.7.8")


def test_decrease(flood_active):
    flood.report("1.2.3.4")
    flood.report("1.2.3.4")
    flood.decrease("1.2.3.4")
    assert not flood.is_banned("1.2.3.4")

    flood.decrease("1.2.3.4")
    assert not flood.has_violation("1.2.3.4")


def test_decrease_does_not_go_negative(flood_active):
    flood.decrease("1.2.3.4")
    assert not flood.has_violation("1.2.3.4")


def test_forgive_banned_reduces_offences(flood_active):
    flood.report("1.2.3.4")
    flood.report("1.2.3.4")
    assert flood.is_banned("1.2.3.4")

    flood.forgive_banned()
    assert not flood.is_banned("1.2.3.4")


def test_forgive_banned_removes_cleared_ips(flood_active, mem_storage):
    flood.report("1.2.3.4")
    flood.decrease("1.2.3.4")

    flood.forgive_banned()
    assert mem_storage.get_all_hash_int("banned") == {}


def test_fingerprint_mismatch(flood_active):
    assert flood.fingerprint_mismatch("1.2.3.4", "fp1") is False
    assert flood.fingerprint_mismatch("1.2.3.4", "fp1") is False
    assert flood.fingerprint_mismatch("1.2.3.4", "fp2") is True


def test_fingerprint_mismatch_empty(flood_active):
    assert flood.fingerprint_mismatch("1.2.3.4", "") is True
    assert flood.fingerprint_mismatch("1.2.3.4", None) is True
