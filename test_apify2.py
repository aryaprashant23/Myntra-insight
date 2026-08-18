import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))
token = os.environ.get("APIFY_API_TOKEN")

response = requests.get(f'https://api.apify.com/v2/store/actors?search=app%20store', headers={'Authorization': f'Bearer {token}'})
if response.status_code == 200:
    data = response.json()
    actors = data.get('data', {}).get('items', [])
    for actor in actors[:5]:
        print(f"ID: {actor['username']}/{actor['name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
