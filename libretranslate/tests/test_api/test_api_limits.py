import json


def test_api_char_limit(client_factory):
    client = client_factory("--char-limit", 5)

    response = client.post("/translate", data={
        "q": "This text is too long",
        "source": "en",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert "exceeds text limit" in response_json["error"]
    assert response.status_code == 400


def test_api_char_limit_ok(client_factory):
    client = client_factory("--char-limit", 100)

    response = client.post("/translate", data={
        "q": "Short",
        "source": "en",
        "target": "es"
    })

    assert response.status_code == 200


def test_api_batch_limit(client_factory):
    client = client_factory("--batch-limit", 1)

    response = client.post("/translate", json={
        "q": ["Hello", "World"],
        "source": "en",
        "target": "es"
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert "exceeds text limit" in response_json["error"]
    assert response.status_code == 400


def test_api_alternatives_limit(client_factory):
    client = client_factory("--alternatives-limit", 1)

    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es",
        "alternatives": 3
    })

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: alternatives parameter must be <= 1"
    assert response.status_code == 400


def test_api_req_limit_slowdown(client_factory):
    client = client_factory("--req-limit", 1)

    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })
    assert response.status_code == 200

    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })
    response_json = json.loads(response.data)
    assert response.status_code == 429
    assert "Slowdown" in response_json["error"]


def test_api_flood_banned_client(client_factory):
    from libretranslate import flood

    client = client_factory("--req-flood-threshold", 2)

    # Simulate prior rate limit offences from this client (test client
    # requests originate from 127.0.0.1)
    flood.report("127.0.0.1")
    flood.report("127.0.0.1")

    response = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })
    response_json = json.loads(response.data)
    assert response.status_code == 403
    assert response_json["error"] == "Too many request limits violations"
