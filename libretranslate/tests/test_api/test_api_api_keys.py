import json

from libretranslate.api_keys import Database


def _translate(client, headers=None, **kwargs):
    return client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        **kwargs
    }, headers=headers or {})


def test_api_key_required_for_programmatic_access(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-origin", "^https://allowed\\.example\\.com$"
    )

    response = _translate(client)

    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json["error"] == "Please contact the server operator to get an API key"


def test_api_key_not_required_from_allowed_origin(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-origin", "^https://allowed\\.example\\.com$"
    )

    response = _translate(client, headers={"Origin": "https://allowed.example.com"})

    assert response.status_code == 200


def test_api_invalid_key_is_rejected(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path
    )

    response = _translate(client, api_key="bogus-key")

    response_json = json.loads(response.data)
    assert response.status_code == 403
    assert response_json["error"] == "Invalid API key"


def test_api_valid_key_is_accepted(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path).add(req_limit=100, api_key="valid-key")

    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path
    )

    response = _translate(client, api_key="valid-key")

    assert response.status_code == 200
