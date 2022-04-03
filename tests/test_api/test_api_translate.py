import json


def test_api_detect_language(client):
    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "format": "text"
    })

    response_json = json.loads(response.data)

    assert "translatedText" in response_json
    assert response.status_code == 200

