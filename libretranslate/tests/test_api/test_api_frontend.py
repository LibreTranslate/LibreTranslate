import json


def test_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"LibreTranslate" in response.data


def test_index_disabled_web_ui(client_factory):
    client = client_factory("--disable-web-ui")

    assert client.get("/").status_code == 404


def test_appjs(client):
    response = client.get("/js/app.js")

    assert response.status_code == 200
    assert "application/javascript" in response.content_type


def test_appjs_disabled_web_ui(client_factory):
    client = client_factory("--disable-web-ui")

    assert client.get("/js/app.js").status_code == 404


def test_appjs_secret_headers(client_factory):
    client = client_factory("--require-api-key-secret")

    response = client.get("/js/app.js")

    assert response.status_code == 200
    assert "no-store" in response.headers["Cache-Control"]


def test_appjs_serves_secret_to_browser(client_factory):
    client = client_factory("--require-api-key-secret")

    # The index route sets the 'r' cookie marking browser clients
    client.get("/")
    response = client.get("/js/app.js", headers={"User-Agent": "test-agent"})

    assert response.status_code == 200
    assert b"String.fromCharCode" in response.data


def test_index_custom_title(client_factory):
    client = client_factory("--frontend-title", "My Custom Title")

    response = client.get("/")

    assert response.status_code == 200
    assert b"My Custom Title" in response.data


def test_index_lang_param_sets_cookie(client):
    response = client.get("/?lang=es")

    assert response.status_code == 200
    assert "preferred_lang=es" in response.headers.get("Set-Cookie", "")


def test_cors_headers(client):
    response = client.get("/health")

    assert response.headers.get("Access-Control-Allow-Origin") == "*"
    assert response.headers.get("Access-Control-Allow-Methods") == "GET, POST"


def test_frontend_settings_content(client):
    response = client.get("/frontend/settings")

    settings = json.loads(response.data)

    assert response.status_code == 200
    assert settings["apiKeys"] is False
    assert settings["keyRequired"] is False
    assert settings["suggestions"] is False
    assert settings["filesTranslation"] is True
    assert ".txt" in settings["supportedFilesFormat"]
    assert settings["language"]["source"]["code"] == "auto"


def test_frontend_settings_char_limit(client_factory):
    client = client_factory("--char-limit", 42)

    settings = json.loads(client.get("/frontend/settings").data)

    assert settings["charLimit"] == 42


def test_frontend_settings_suggestions(client_factory):
    client = client_factory("--suggestions")

    settings = json.loads(client.get("/frontend/settings").data)

    assert settings["suggestions"] is True


def test_frontend_settings_files_disabled(client_factory):
    client = client_factory("--disable-files-translation")

    settings = json.loads(client.get("/frontend/settings").data)

    assert settings["filesTranslation"] is False
    assert settings["supportedFilesFormat"] == []


def test_frontend_settings_key_required(client_factory, tmp_path):
    client = client_factory(
        "--api-keys", "--api-keys-db-path", str(tmp_path / "api_keys.db"),
        "--require-api-key-origin", "^https://allowed"
    )

    settings = json.loads(client.get("/frontend/settings").data)

    assert settings["apiKeys"] is True
    assert settings["keyRequired"] is True


def test_frontend_settings_target_language(client_factory):
    client = client_factory("--frontend-language-target", "es")

    settings = json.loads(client.get("/frontend/settings").data)

    assert settings["language"]["target"]["code"] == "es"


def test_frontend_settings_source_language(client_factory):
    client = client_factory("--frontend-language-source", "es")

    settings = json.loads(client.get("/frontend/settings").data)

    assert settings["language"]["source"]["code"] == "es"


def test_frontend_settings_source_fallback(client_factory):
    client = client_factory("--frontend-language-source", "zz")

    settings = json.loads(client.get("/frontend/settings").data)

    # Falls back to the first installed language
    assert settings["language"]["source"]["code"] == "en"


def test_index_locale_override_header(client):
    response = client.get("/", headers={"X-Override-Accept-Language": "es"})

    assert response.status_code == 200


def test_index_preferred_lang_cookie(client):
    client.set_cookie("preferred_lang", "es")
    response = client.get("/")

    assert response.status_code == 200


def test_powercycle_exits(client_factory, monkeypatch):
    import pytest

    monkeypatch.setenv("LT_POWERCYCLE", "1")

    with pytest.raises(SystemExit):
        client_factory()
