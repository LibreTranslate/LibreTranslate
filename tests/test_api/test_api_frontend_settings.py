def test_api_get_frontend_settings(client):
    response = client.get("/frontend/settings")

    assert response.status_code == 200
