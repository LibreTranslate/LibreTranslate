import sys
import json
import pytest
from libretranslate.app import create_app
from libretranslate.main import get_args


@pytest.fixture()
def app_with_pb():
    sys.argv = ['', '--load-only', 'en,pb']
    app = create_app(get_args())
    yield app


@pytest.fixture()
def client_with_pb(app_with_pb):
    return app_with_pb.test_client()


@pytest.fixture()
def app_with_pt():
    sys.argv = ['', '--load-only', 'en,pt']
    app = create_app(get_args())
    yield app


@pytest.fixture()
def client_with_pt(app_with_pt):
    return app_with_pt.test_client()


@pytest.fixture()
def app_with_zh():
    sys.argv = ['', '--load-only', 'en,zh']
    app = create_app(get_args())
    yield app


@pytest.fixture()
def client_with_zh(app_with_zh):
    return app_with_zh.test_client()


@pytest.fixture()
def app_with_zt():
    sys.argv = ['', '--load-only', 'en,zt']
    app = create_app(get_args())
    yield app


@pytest.fixture()
def client_with_zt(app_with_zt):
    return app_with_zt.test_client()


def test_auto_detect_fallback_pt_to_pb(client_with_pb):
    response = client_with_pb.post("/translate", data={
        "q": "Olá mundo",
        "source": "auto",
        "target": "en",
        "format": "text"
    })
    
    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert "translatedText" in response_json
    assert len(response_json["translatedText"]) > 0


def test_auto_detect_fallback_pb_to_pt(client_with_pt):
    response = client_with_pt.post("/translate", data={
        "q": "Olá mundo",
        "source": "auto",
        "target": "en",
        "format": "text"
    })
    
    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert "translatedText" in response_json
    assert len(response_json["translatedText"]) > 0


def test_explicit_language_no_fallback(client_with_pb):
    response = client_with_pb.post("/translate", data={
        "q": "Hello",
        "source": "en",
        "target": "pt",
        "format": "text"
    })
    
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in response_json


def test_auto_detect_fallback_zt_to_zh(client_with_zh):
    response = client_with_zh.post("/translate", data={
        "q": "你好世界",
        "source": "auto",
        "target": "en",
        "format": "text"
    })
    
    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert "translatedText" in response_json
    assert len(response_json["translatedText"]) > 0


def test_auto_detect_fallback_zh_to_zt(client_with_zt):
    response = client_with_zt.post("/translate", data={
        "q": "你好世界",
        "source": "auto",
        "target": "en",
        "format": "text"
    })
    
    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert "translatedText" in response_json
    assert len(response_json["translatedText"]) > 0

