import base64
import random
from types import SimpleNamespace

import pytest

from libretranslate import secret, storage


@pytest.fixture()
def mem_storage():
    return storage.setup("memory://")


@pytest.fixture()
def secrets(mem_storage):
    secret.setup(SimpleNamespace(require_api_key_secret=True))
    return mem_storage


def test_to_base():
    assert secret.to_base(0, 4) == 0
    assert secret.to_base(5, 4) == 11
    assert secret.to_base(255, 7) == 513
    assert secret.to_base(-5, 4) == -11


def test_generate_secret():
    s = secret.generate_secret()
    assert len(s) == 7
    assert s.isalnum()
    assert s.upper() == s


def test_setup_populates_secrets(secrets):
    assert secrets.get_str("secret_0") != ""
    assert secrets.get_str("secret_1") != ""
    assert secrets.get_str("secret_bogus") != ""


def test_setup_disabled_leaves_storage_empty(mem_storage):
    secret.setup(SimpleNamespace(require_api_key_secret=False))
    assert not mem_storage.exists("secret_0")
    assert not mem_storage.exists("secret_1")


def test_rotate_secrets(secrets):
    old_1 = secrets.get_str("secret_1")

    secret.rotate_secrets()

    assert secrets.get_str("secret_0") == old_1
    assert secrets.get_str("secret_1") != old_1


def test_secret_match(secrets):
    assert secret.secret_match(secrets.get_str("secret_0"))
    assert secret.secret_match(secrets.get_str("secret_1"))
    assert not secret.secret_match("not-a-secret")
    assert not secret.secret_match(None)


def test_secret_match_after_rotation(secrets):
    previous = secrets.get_str("secret_1")
    secret.rotate_secrets()
    # The rotated-out secret remains valid
    assert secret.secret_match(previous)


def test_secret_bogus_match(secrets, monkeypatch):
    monkeypatch.setattr(random, "randint", lambda *a: 0)
    assert secret.secret_bogus_match(secrets.get_str("secret_bogus"))
    assert not secret.secret_bogus_match("wrong")


def test_get_current_secret_b64(secrets):
    expected = secrets.get_str("secret_1")
    decoded = base64.b64decode(secret.get_current_secret_b64()).decode("utf-8")
    assert decoded == expected


def test_get_current_secret_js(secrets):
    assert "String.fromCharCode" in secret.get_current_secret_js()


def test_obfuscate_returns_js():
    code = secret.obfuscate("abc")
    assert "String.fromCharCode" in code
    assert "parseInt" in code


def test_obfuscate_is_cached():
    assert secret.obfuscate("same") == secret.obfuscate("same")


def test_get_bogus_secret(secrets):
    assert secret.get_bogus_secret() == secrets.get_str("secret_bogus")


def test_get_emoji():
    assert isinstance(secret.get_emoji(), str)
    assert len(secret.get_emoji()) > 0
