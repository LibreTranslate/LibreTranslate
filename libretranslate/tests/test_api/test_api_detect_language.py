import json


def test_api_detect_language(client):
    response = client.post("/detect", data={
        "q": "Hello"
    })
    response_json = json.loads(response.data)

    assert "confidence" in response_json[0] and "language" in response_json[0]
    assert len(response_json) >= 1
    assert response.status_code == 200


def test_api_detect_language_must_fail_without_parameters(client):
    response = client.post("/detect")
    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response.status_code == 400


def test_api_detect_language_must_fail_bad_request_type(client):
    response = client.get("/detect")

    assert response.status_code == 405
