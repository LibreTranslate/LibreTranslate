import json

import libretranslate.app as app_module
from libretranslate.suggestions import Database as SuggestionsDatabase


def test_api_suggest(client_factory, tmp_path, monkeypatch):
    db_path = str(tmp_path / "suggestions.db")
    monkeypatch.setattr(
        app_module, "SuggestionsDatabase", lambda: SuggestionsDatabase(db_path)
    )

    client = client_factory("--suggestions")

    response = client.post("/suggest", data={
        "q": "Hello",
        "s": "Hola",
        "source": "en",
        "target": "es"
    })

    assert response.status_code == 200
    assert json.loads(response.data) == {"success": True}

    row = SuggestionsDatabase(db_path).c.execute(
        "SELECT q, s, source, target FROM suggestions"
    ).fetchone()
    assert row == ("Hello", "Hola", "en", "es")


def test_api_suggest_json(client_factory, tmp_path, monkeypatch):
    db_path = str(tmp_path / "suggestions.db")
    monkeypatch.setattr(
        app_module, "SuggestionsDatabase", lambda: SuggestionsDatabase(db_path)
    )

    client = client_factory("--suggestions")

    response = client.post("/suggest", json={
        "q": "Hello",
        "s": "Hola",
        "source": "en",
        "target": "es"
    })

    assert response.status_code == 200
    assert json.loads(response.data) == {"success": True}


def test_api_suggest_missing_parameter(client_factory, tmp_path, monkeypatch):
    db_path = str(tmp_path / "suggestions.db")
    monkeypatch.setattr(
        app_module, "SuggestionsDatabase", lambda: SuggestionsDatabase(db_path)
    )

    client = client_factory("--suggestions")

    response = client.post("/suggest", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing s parameter"
    assert response.status_code == 400


def test_api_suggest_disabled(client):
    response = client.post("/suggest", data={
        "q": "Hello",
        "s": "Hola",
        "source": "en",
        "target": "es"
    })

    assert response.status_code == 403
