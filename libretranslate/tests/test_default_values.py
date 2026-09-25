from libretranslate.default_values import _get_value


def test_env_int_override(monkeypatch):
    monkeypatch.setenv("LT_REQ_LIMIT", "5")
    assert _get_value("REQ_LIMIT", -1, "int") == 5


def test_env_int_invalid_falls_back(monkeypatch):
    monkeypatch.setenv("LT_REQ_LIMIT", "abc")
    assert _get_value("REQ_LIMIT", -1, "int") == -1


def test_env_bool_override(monkeypatch):
    for value in ["TRUE", "True", "true", "1"]:
        monkeypatch.setenv("LT_DEBUG", value)
        assert _get_value("DEBUG", False, "bool") is True

    for value in ["FALSE", "False", "false", "0"]:
        monkeypatch.setenv("LT_DEBUG", value)
        assert _get_value("DEBUG", True, "bool") is False


def test_env_bool_unrecognized_falls_back(monkeypatch):
    monkeypatch.setenv("LT_DEBUG", "yes")
    assert _get_value("DEBUG", False, "bool") is False
    assert _get_value("DEBUG", True, "bool") is True


def test_env_str_override(monkeypatch):
    monkeypatch.setenv("LT_HOST", "0.0.0.0")
    assert _get_value("HOST", "127.0.0.1", "str") == "0.0.0.0"


def test_no_env_uses_default(monkeypatch):
    monkeypatch.delenv("LT_REQ_LIMIT", raising=False)
    assert _get_value("REQ_LIMIT", -1, "int") == -1


def test_unknown_type_returns_default():
    assert _get_value("LOAD_ONLY", None, "unknown") is None
