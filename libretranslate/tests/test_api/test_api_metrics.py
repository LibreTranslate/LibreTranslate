def test_api_metrics_disabled_by_default(client):
    response = client.get("/metrics")

    assert response.status_code == 404


# Only one metrics-enabled app can exist per process: the Prometheus
# Summary/Gauge timeseries are registered on a global registry and creating a
# second app raises "Duplicated timeseries".
def test_api_metrics_auth_token(client_factory):
    client = client_factory("--metrics", "--metrics-auth-token", "test-token")

    response = client.get("/metrics")
    assert response.status_code == 401

    response = client.get("/metrics", headers={
        "Authorization": "Bearer wrong-token"
    })
    assert response.status_code == 401

    response = client.get("/metrics", headers={
        "Authorization": "Bearer test-token"
    })
    assert response.status_code == 200
    assert "libretranslate" in response.get_data(as_text=True)

    # Requests through access_check-decorated endpoints are measured
    translate = client.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "es"
    })
    assert translate.status_code == 200

    response = client.get("/metrics", headers={
        "Authorization": "Bearer test-token"
    })
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "libretranslate_http_request_duration_seconds" in body
    assert "libretranslate_http_requests_in_flight" in body
