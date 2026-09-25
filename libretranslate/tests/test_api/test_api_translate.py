import json


def test_api_translate(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert "translatedText" in response_json
    assert response.status_code == 200


def test_api_translate_batch(client):

    response = client.post("/translate", json={
        "q": ["Hello", "World"],
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert "translatedText" in response_json
    assert isinstance(response_json["translatedText"], list)
    assert len(response_json["translatedText"]) == 2
    assert response.status_code == 200


def test_api_translate_unsupported_language(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "zz",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "zz is not supported"
    assert response.status_code == 400


def test_api_translate_missing_parameter(client):
    response = client.post("/translate", data={
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing q parameter"
    assert response.status_code == 400


def test_api_translate_missing_source(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing source parameter"
    assert response.status_code == 400


def test_api_translate_missing_target(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing target parameter"
    assert response.status_code == 400


def test_api_translate_unsupported_format(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "format": "xml"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "xml format is not supported"
    assert response.status_code == 400


def test_api_translate_invalid_alternatives(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "alternatives": "abc"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: alternatives parameter is not a number"
    assert response.status_code == 400


def test_api_translate_alternatives(client):
    response = client.post("/translate", json={
        "q": "Hello world, this is a test",
        "source": "en",
        "target": "es",
        "alternatives": 3
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert "alternatives" in response_json
    assert isinstance(response_json["alternatives"], list)


def test_api_translate_auto_detect_source(client):
    response = client.post("/translate", data={
        "q": "This is a sentence written in English for testing purposes",
        "source": "auto",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert response_json["detectedLanguage"]["language"] == "en"
    assert response_json["detectedLanguage"]["confidence"] > 0


def test_api_translate_html_format(client):
    response = client.post("/translate", data={
        "q": "<p>Hello</p>",
        "source": "en",
        "target": "es",
        "format": "html"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "<p>" in response_json["translatedText"]
    assert "</p>" in response_json["translatedText"]


def test_api_translate_non_translatable_returns_source(client):
    response = client.post("/translate", data={
        "q": "😀",
        "source": "en",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert response_json["translatedText"] == "😀"


def test_api_translate_empty_batch(client):
    response = client.post("/translate", json={
        "q": [],
        "source": "en",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing q parameter"
    assert response.status_code == 400


def test_api_translate_spanish_to_english(client):
    response = client.post("/translate", data={
        "q": "Hola mundo",
        "source": "es",
        "target": "en"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert response_json["translatedText"] != "Hola mundo"


def test_api_translate_error_returns_json_500(client, monkeypatch):
    import libretranslate.app as app_module

    def broken(*a, **kw):
        raise RuntimeError("translation failed")

    monkeypatch.setattr(app_module, "improve_translation_formatting", broken)

    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 500
    assert "error" in response_json


def test_api_translate_invalid_json_body(client):
    response = client.post("/translate", json=["not", "a", "dict"])

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid JSON format"
    assert response.status_code == 400


def test_api_translate_batch_html(client):
    response = client.post("/translate", json={
        "q": ["<p>Hello</p>", "<p>World</p>"],
        "source": "en",
        "target": "es",
        "format": "html"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert isinstance(response_json["translatedText"], list)
    assert "<p>" in response_json["translatedText"][0]


def test_api_translate_batch_non_translatable(client):
    response = client.post("/translate", json={
        "q": ["😀", "😁"],
        "source": "en",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert response_json["translatedText"] == ["😀", "😁"]


def test_api_translate_batch_alternatives(client):
    response = client.post("/translate", json={
        "q": ["Hello", "World"],
        "source": "en",
        "target": "es",
        "alternatives": 2
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "alternatives" in response_json
    assert isinstance(response_json["alternatives"], list)
    assert len(response_json["alternatives"]) == 2


def test_api_translate_batch_auto_detect(client):
    response = client.post("/translate", json={
        "q": ["Hello there", "Good morning"],
        "source": "auto",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert len(response_json["detectedLanguage"]) == 2
    assert all(
        d["language"] == "en" for d in response_json["detectedLanguage"]
    )


def test_api_translate_unsupported_source_language(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "zz",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "zz is not supported"
    assert response.status_code == 400


def test_api_translate_uses_cache(client_factory):
    from libretranslate import storage as storage_module

    client = client_factory("--translation-cache", "all")

    first = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })
    assert first.status_code == 200

    mem_store = storage_module.get_storage().store
    assert any(k.startswith("tcache_") for k in mem_store)

    second = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })
    assert second.status_code == 200
    assert json.loads(second.data)["translatedText"] == json.loads(first.data)["translatedText"]
