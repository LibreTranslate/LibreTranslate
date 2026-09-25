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


@pytest.fixture()
def client_factory():
    def _factory(*extra_args):
        sys.argv = ['', '--load-only', 'en,es'] + [str(a) for a in extra_args]
        return create_app(get_args()).test_client()

    return _factory
