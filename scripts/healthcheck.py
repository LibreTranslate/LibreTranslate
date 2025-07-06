import requests
import os

port = os.environ.get('LT_PORT', '5000')
response = requests.post(
    url=f'http://localhost:{port}/translate',
    headers={'Content-Type': 'application/json'},
    json={
         'q': 'Hello World!',
         'source': 'en',
         'target': 'en'
    },
    timeout=60
)
response.raise_for_status() # if server unavailable then requests with raise exception and healthcheck will fail
