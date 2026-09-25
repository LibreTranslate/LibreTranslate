from types import SimpleNamespace

import pytest

from libretranslate import flood, scheduler, secret, storage


@pytest.fixture()
def mem_storage():
    return storage.setup("memory://")


def _args(**overrides):
    base = {
        "secondary": False,
        "req_flood_threshold": -1,
        "api_keys": False,
        "require_api_key_secret": False,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_setup_registers_flood_job(mem_storage, monkeypatch):
    monkeypatch.setattr(scheduler, "scheduler", None)
    scheduler.setup(_args(req_flood_threshold=5))

    job_funcs = [j.func for j in scheduler.scheduler.get_jobs()]
    assert flood.forgive_banned in job_funcs


def test_setup_registers_secret_rotation_job(mem_storage, monkeypatch):
    monkeypatch.setattr(scheduler, "scheduler", None)
    scheduler.setup(_args(api_keys=True, require_api_key_secret=True))

    job_funcs = [j.func for j in scheduler.scheduler.get_jobs()]
    assert secret.rotate_secrets in job_funcs


def test_setup_no_jobs_without_features(mem_storage, monkeypatch):
    monkeypatch.setattr(scheduler, "scheduler", None)
    scheduler.setup(_args())

    assert scheduler.scheduler.get_jobs() == []


def test_setup_secondary_registers_no_jobs(mem_storage, monkeypatch):
    monkeypatch.setattr(scheduler, "scheduler", None)
    scheduler.setup(_args(
        secondary=True,
        req_flood_threshold=5,
        api_keys=True,
        require_api_key_secret=True,
    ))

    assert scheduler.scheduler.get_jobs() == []
