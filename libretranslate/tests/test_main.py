import sys

from werkzeug.middleware.dispatcher import DispatcherMiddleware

from libretranslate.main import get_args, main


def test_get_args_load_only_split(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["libretranslate", "--load-only", "en,es,fr"])
    args = get_args()
    assert args.load_only == ["en", "es", "fr"]


def test_get_args_url_prefix_normalized(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["libretranslate", "--url-prefix", "lt"])
    args = get_args()
    assert args.url_prefix == "/lt"


def test_get_args_url_prefix_already_normalized(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["libretranslate", "--url-prefix", "/lt"])
    args = get_args()
    assert args.url_prefix == "/lt"


def test_main_wsgi_returns_app(monkeypatch):
    # wsgi.py signals WSGI mode via argv[0], not a parsed flag
    monkeypatch.setattr(sys, "argv", ["--wsgi", "--load-only", "en,es"])
    app = main()
    assert isinstance(app, DispatcherMiddleware)
