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
