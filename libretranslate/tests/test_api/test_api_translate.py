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


def test_api_translate_emoji_does_not_cut_off_text(client):
    # Regression for https://github.com/LibreTranslate/LibreTranslate/issues/439
    response = client.post("/translate", data={
        "q": "Hello. 😆 How are you?",
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    translated = response_json["translatedText"]
    assert "😆" in translated
    after_emoji = translated.split("😆", 1)[1]
    assert len(after_emoji.strip()) > 5


def test_api_translate_emoji_only(client):
    response = client.post("/translate", data={
        "q": "🌷🌷🌷",
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert response_json["translatedText"] == "🌷🌷🌷"


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
