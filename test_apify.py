import requests
import json

response = requests.get('https://api.apify.com/v2/actor-store/actors?search=app%20store')
if response.status_code == 200:
    data = response.json()
    actors = data.get('data', {}).get('items', [])
    for actor in actors[:5]:
        print(f"ID: {actor['username']}/{actor['name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
