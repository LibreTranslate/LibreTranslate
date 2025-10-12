def test_api_get_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_api_health_must_fail_bad_request_type(client):
    response = client.post("/health")

    assert response.status_code == 405
