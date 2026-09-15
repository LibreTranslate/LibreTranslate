import os
import sys

import pytest

from libretranslate.app import create_app, get_upload_dir
from libretranslate.main import get_args


@pytest.fixture()
def under_attack_app(tmp_path):
    db_path = str(tmp_path / "api_keys.db")
    sys.argv = [
        '', '--load-only', 'en,es',
        '--api-keys', '--api-keys-db-path', db_path,
        '--under-attack',
    ]
    app = create_app(get_args())
    yield app


@pytest.fixture()
def under_attack_client(under_attack_app):
    return under_attack_app.test_client()


def test_detect_requires_api_key_under_attack(under_attack_client):
    response = under_attack_client.post("/detect", data={"q": "Hello"})

    assert response.status_code == 400


def test_download_file_must_also_require_api_key_under_attack(under_attack_client):
    filename = "regression-test-under-attack.txt"
    filepath = os.path.join(get_upload_dir(), filename)
    with open(filepath, "w") as f:
        f.write("should not be reachable without a key")

    try:
        response = under_attack_client.get(f"/download_file/{filename}")

        assert response.status_code == 400
    finally:
        os.remove(filepath)
