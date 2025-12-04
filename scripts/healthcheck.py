import requests
import os

port = os.environ.get('LT_PORT', '5000')
response = requests.get(
    url=f'http://localhost:{port}/health',
    headers={'Content-Type': 'application/json'},
    json={},
    timeout=60
)
response.raise_for_status() # if server unavailable then requests with raise exception and healthcheck will fail
