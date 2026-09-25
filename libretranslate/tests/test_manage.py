import sys

import pytest

from libretranslate.api_keys import Database
from libretranslate.manage import manage


def _run_manage(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["ltmanage"] + [str(a) for a in argv])
    manage()


def test_keys_missing_db_exits(tmp_path, monkeypatch, capsys):
    db_path = str(tmp_path / "nonexistent.db")

    with pytest.raises(SystemExit):
        _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path)

    assert "No such database" in capsys.readouterr().out


def test_keys_list_empty(tmp_path, monkeypatch, capsys):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path)

    _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path)

    assert "There are no API keys" in capsys.readouterr().out


def test_keys_add_and_list(tmp_path, monkeypatch, capsys):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path)

    _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path,
                "add", "100", "--key", "mykey")
    assert "mykey" in capsys.readouterr().out

    _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path)
    out = capsys.readouterr().out
    assert "mykey: 100" in out


def test_keys_add_auto_generates_key(tmp_path, monkeypatch, capsys):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path)

    _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path, "add", "50")

    generated = capsys.readouterr().out.strip()
    assert len(generated) == 36  # uuid4
    assert Database(db_path).lookup(generated) == (50, None)


def test_keys_remove(tmp_path, monkeypatch, capsys):
    db_path = str(tmp_path / "api_keys.db")
    db = Database(db_path)
    db.add(10, "mykey")

    _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path,
                "remove", "mykey")

    assert "mykey" in capsys.readouterr().out
    assert db.lookup("mykey") is None


def test_keys_add_with_char_limit(tmp_path, monkeypatch, capsys):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path)

    _run_manage(monkeypatch, "keys", "--api-keys-db-path", db_path,
                "add", "100", "--key", "k", "--char-limit", "500")

    capsys.readouterr()
    assert Database(db_path).lookup("k") == (100, 500)


def test_no_command_exits(monkeypatch):
    with pytest.raises(SystemExit):
        _run_manage(monkeypatch)
