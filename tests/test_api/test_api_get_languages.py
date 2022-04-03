import json


def test_api_get_languages(client):
    response = client.get("/languages")
    response_json = json.loads(response.data)

    assert "code" in response_json[0] and "name" in response_json[0]
    assert len(response_json) >= 1
    assert response.status_code == 200


def test_api_get_languages_must_fail_bad_request_type(client):
    response = client.post("/languages")

    assert response.status_code == 405
