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


def test_api_get_api_key_link_in_error(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-origin", "^https://allowed",
        "--get-api-key-link", "https://keys.example.com"
    )

    response = _translate(client)

    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json["error"] == "Visit https://keys.example.com to get an API key"


def test_api_under_attack_requires_key(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path).add(req_limit=100, api_key="valid-key")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path, "--under-attack"
    )

    assert _translate(client).status_code == 400
    assert _translate(client, api_key="valid-key").status_code == 200


def test_api_secret_grants_access(client_factory, tmp_path):
    from libretranslate import secret

    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-secret"
    )

    # No key and no secret -> rejected
    assert _translate(client).status_code == 400

    # The rotating server secret acts as a key substitute
    response = _translate(client, secret=secret.get_current_secret())
    assert response.status_code == 200


def test_api_fingerprint_mismatch_requires_key(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-fingerprint"
    )

    # First request establishes the fingerprint for this IP
    response = _translate(client, headers={"User-Agent": "agent-a"})
    assert response.status_code == 200

    # A different fingerprint from the same IP looks like a script
    response = _translate(client, headers={"User-Agent": "agent-b"})
    assert response.status_code == 400

    # The original fingerprint still works
    response = _translate(client, headers={"User-Agent": "agent-a"})
    assert response.status_code == 200


def test_api_need_key_reports_flood_violation(client_factory, tmp_path):
    from libretranslate import storage as storage_module

    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-origin", "^https://allowed",
        "--req-flood-threshold", "10"
    )

    assert _translate(client).status_code == 400
    assert _translate(client).status_code == 400

    violations = storage_module.get_storage().get_hash_int("banned", "127.0.0.1")
    assert violations == 2


def test_api_secret_via_json_body(client_factory, tmp_path):
    from libretranslate import secret

    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-secret"
    )

    response = client.post("/translate", json={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "secret": secret.get_current_secret()
    })
    assert response.status_code == 200


def test_api_bogus_secret_returns_emoji(client_factory, tmp_path, monkeypatch):
    import random

    from libretranslate import secret

    db_path = str(tmp_path / "api_keys.db")
    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path,
        "--require-api-key-secret"
    )

    monkeypatch.setattr(random, "randint", lambda *a: 0)
    response = _translate(client, secret=secret.get_bogus_secret())

    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert response_json["translatedText"] == secret.get_emoji()


def test_api_key_char_limit_override(client_factory, tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    Database(db_path).add(req_limit=100, api_key="limited-key", char_limit=3)

    client = client_factory(
        "--api-keys", "--api-keys-db-path", db_path
    )

    response = _translate(client, api_key="limited-key")

    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert "exceeds text limit" in response_json["error"]
