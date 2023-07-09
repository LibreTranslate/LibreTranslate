import sys

import pytest

from libretranslate.app import create_app
from libretranslate.default_values import DEFAULT_ARGUMENTS
from libretranslate.main import get_args


@pytest.fixture()
def app():
    sys.argv = ['']
    DEFAULT_ARGUMENTS['LOAD_ONLY'] = "en,es"
    app = create_app(get_args())

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
