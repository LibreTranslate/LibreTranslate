import sys

import pytest

from libretranslate.app import create_app
from libretranslate.main import get_args


@pytest.fixture()
def app():
    sys.argv = ['', '--load-only', 'en,es']
    app = create_app(get_args())

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
