"""Security tests for the /metrics endpoint.

Verifies that:
1. /metrics returns 401 when no --metrics-auth-token is configured (deny by default)
2. /metrics returns 401 with an invalid bearer token
3. /metrics returns 200 with a valid bearer token
4. Prometheus output does not contain api_key or request_ip labels
"""
import sys

import pytest

from libretranslate.app import create_app
from libretranslate.main import get_args


@pytest.fixture()
def metrics_app():
    sys.argv = ['', '--load-only', 'en,es', '--metrics', '--metrics-auth-token', 'test-secret-token']
    app = create_app(get_args())
    yield app


@pytest.fixture()
def metrics_client(metrics_app):
    return metrics_app.test_client()


@pytest.fixture()
def metrics_app_no_token():
    sys.argv = ['', '--load-only', 'en,es', '--metrics']
    app = create_app(get_args())
    yield app


@pytest.fixture()
def metrics_client_no_token(metrics_app_no_token):
    return metrics_app_no_token.test_client()


def test_metrics_denied_without_auth_token_configured(metrics_client_no_token):
    """ /metrics must return 401 when no --metrics-auth-token is set (deny by default) """
    response = metrics_client_no_token.get("/metrics")
    assert response.status_code == 401


def test_metrics_unauthorized_with_invalid_bearer(metrics_client):
    """ /metrics must return 401 with an invalid bearer token """
    response = metrics_client.get(
        "/metrics",
        headers={"Authorization": "Bearer wrong-token"}
    )
    assert response.status_code == 401


def test_metrics_unauthorized_without_bearer(metrics_client):
    """ /metrics must return 401 when no Authorization header is provided """
    response = metrics_client.get("/metrics")
    assert response.status_code == 401


def test_metrics_authorized_with_valid_bearer(metrics_client):
    """ /metrics must return 200 with a valid bearer token """
    response = metrics_client.get(
        "/metrics",
        headers={"Authorization": "Bearer test-secret-token"}
    )
    assert response.status_code == 200


def test_metrics_output_has_no_api_key_label(metrics_client):
    """ Prometheus output must not contain api_key labels """
    response = metrics_client.get(
        "/metrics",
        headers={"Authorization": "Bearer test-secret-token"}
    )
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "api_key=" not in body, "metrics output must not contain api_key labels"


def test_metrics_output_has_no_request_ip_label(metrics_client):
    """ Prometheus output must not contain request_ip labels """
    response = metrics_client.get(
        "/metrics",
        headers={"Authorization": "Bearer test-secret-token"}
    )
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "request_ip=" not in body, "metrics output must not contain request_ip labels"
