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


def test_api_translate_with_json_glossary(client):
    response = client.post("/translate", json={
        "q": "Hello world",
        "source": "en",
        "target": "es",
        "format": "text",
        "glossary": {"world": "universo"}
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert "universo" in response_json["translatedText"].lower()


def test_api_translate_with_form_glossary(client):
    response = client.post("/translate", data={
        "q": "Hello world",
        "source": "en",
        "target": "es",
        "format": "text",
        "glossary": json.dumps({"world": "universo"})
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert "universo" in response_json["translatedText"].lower()


def test_api_translate_batch_with_glossary(client):
    response = client.post("/translate", json={
        "q": ["Hello world", "A beautiful world"],
        "source": "en",
        "target": "es",
        "format": "text",
        "glossary": {"world": "universo"}
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert isinstance(response_json["translatedText"], list)
    assert len(response_json["translatedText"]) == 2
    for t in response_json["translatedText"]:
        assert "universo" in t.lower()


def test_api_translate_glossary_with_alternatives(client):
    response = client.post("/translate", json={
        "q": "Hello world",
        "source": "en",
        "target": "es",
        "format": "text",
        "alternatives": 2,
        "glossary": {"world": "universo"}
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert "universo" in response_json["translatedText"].lower()
    if "alternatives" in response_json:
        for alt in response_json["alternatives"]:
            assert "ltph" not in alt.lower()
            assert "ltglossary" not in alt.lower()
        assert any("universo" in alt.lower() for alt in response_json["alternatives"])


def test_api_translate_glossary_html_format(client):
    response = client.post("/translate", json={
        "q": "<p>Hello <b>world</b></p>",
        "source": "en",
        "target": "es",
        "format": "html",
        "glossary": {"world": "universo"}
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedText" in response_json
    assert "<p>" in response_json["translatedText"]
    assert "<b>" in response_json["translatedText"]
    assert "universo" in response_json["translatedText"].lower()


def test_api_translate_server_glossary_and_override(client):
    import os
    import tempfile
    from libretranslate import glossary

    with tempfile.TemporaryDirectory() as temp_dir:
        en_es_file = os.path.join(temp_dir, "en_es.json")
        with open(en_es_file, "w", encoding="utf-8") as f:
            json.dump({"device": "aparato"}, f)

        glossary.setup(temp_dir)
        try:
            # 1. Without request glossary -> server-side glossary applies
            res1 = client.post("/translate", json={
                "q": "The device is ready",
                "source": "en",
                "target": "es",
                "format": "text",
            })
            res1_json = json.loads(res1.data)
            assert res1.status_code == 200
            assert "aparato" in res1_json["translatedText"].lower()

            # 2. With request glossary -> request-level overrides server glossary
            res2 = client.post("/translate", json={
                "q": "The device is ready",
                "source": "en",
                "target": "es",
                "format": "text",
                "glossary": {"device": "dispositivo"}
            })
            res2_json = json.loads(res2.data)
            assert res2.status_code == 200
            assert "dispositivo" in res2_json["translatedText"].lower()
        finally:
            glossary.setup(None)


def test_api_translate_glossary_validation_errors(client):
    # Malformed JSON
    res = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": "{not_valid_json"
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)

    # Non-dict JSON
    res = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": ["item1", "item2"]
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)

    # Non-string values
    res = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": {"key": 123}
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)

    # Empty key
    res = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": {"": "value"}
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)

    # Empty value
    res = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": {"key": ""}
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)

    # Oversized glossary (>200 items)
    large_gloss = {f"k{i}": f"v{i}" for i in range(201)}
    res = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": large_gloss
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)

    # Oversized term (>200 chars)
    res = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "glossary": {"a" * 201: "val"}
    })
    assert res.status_code == 400
    assert "error" in json.loads(res.data)
