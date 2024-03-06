import requests

response = requests.post(
    url='http://[::1]:5000/translate',
    headers={'Content-Type': 'application/json'},
    json={
         'q': 'Hello World!',
         'source': 'en',
         'target': 'en'
    },
    timeout=60
)
# if server unavailable then requests with raise exception and healthcheck will fail
