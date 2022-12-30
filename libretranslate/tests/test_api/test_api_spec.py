def test_api_get_spec(client):
    response = client.get("/spec")

    assert response.status_code == 200


def test_api_get_spec_must_fail_bad_request_type(client):
    response = client.post("/spec")

    assert response.status_code == 405
