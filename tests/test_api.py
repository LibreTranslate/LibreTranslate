import pytest
import sys
import json
from app.app import create_app
from app.main import get_args

@pytest.fixture()
def app():
    sys.argv=['']
    app = create_app(get_args())

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()

def test_api_get_languages(client):
    response = client.get("/languages")
    response_json = json.loads(response.data)

    assert "code" in response_json[0] and "name" in response_json[0]
    assert len(response_json) >= 1
    assert response.status_code == 200
