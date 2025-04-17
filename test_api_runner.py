import requests
import json

with open("test_api.json") as f:
    data = json.load(f)

base_url = "http://127.0.0.1:8000"

for call in data:
    endpoint = call["endpoint"]
    body = call["body"]
    
    url = f"{base_url}{endpoint.split(' ')[1]}"
    method = endpoint.split(' ')[0]

    response = requests.request(method, url, json=body)
    
    print(f"{method} {url}")
    print("Status Code:", response.status_code)
    try:
        print("Risposta:", response.json())
    except:
        print("Risposta:", response.text)
    print("-" * 50)
