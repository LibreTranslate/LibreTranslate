import pytest

from libretranslate.suggestions import Database


@pytest.fixture()
def db(tmp_path):
    return Database(str(tmp_path / "suggestions.db"))


def test_add_suggestion(db):
    assert db.add("Hello", "Hola", "en", "es") is True

    row = db.c.execute(
        "SELECT q, s, source, target FROM suggestions"
    ).fetchone()
    assert row == ("Hello", "Hola", "en", "es")


def test_add_multiple_suggestions(db):
    db.add("Hello", "Hola", "en", "es")
    db.add("Goodbye", "Adiós", "en", "es")

    count = db.c.execute("SELECT COUNT(*) FROM suggestions").fetchone()[0]
    assert count == 2


def test_legacy_db_migration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "suggestions.db").write_bytes(b"")
    (tmp_path / "db").mkdir()

    Database()

    assert not (tmp_path / "suggestions.db").exists()
    assert (tmp_path / "db" / "suggestions.db").exists()
