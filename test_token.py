import requests
import re
import json
import urllib.parse

url = "https://apps.apple.com/in/app/myntra/id412812508"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
match = re.search(r'name="web-experience-app/config/environment" content="([^"]+)"', response.text)
if match:
    encoded = match.group(1)
    decoded = urllib.parse.unquote(encoded)
    data = json.loads(decoded)
    token = data.get("MEDIA_API", {}).get("token")
    print(f"Found token: {token[:20]}...")
else:
    print("Token not found.")
