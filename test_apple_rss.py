import urllib.request
import json
import logging

logging.basicConfig(level=logging.INFO)

APP_ID = "412812508"
RSS_URL = f"https://itunes.apple.com/in/rss/customerreviews/page=1/id={APP_ID}/sortby=mostrecent/json"

req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    entries = data.get('feed', {}).get('entry', [])
    print(f"Number of entries: {len(entries)}")
    if len(entries) > 1:
        print("Keys in the second entry (usually a review):")
        print(list(entries[1].keys()))
        print("Sample of the second entry:")
        print(json.dumps(entries[1], indent=2))
except Exception as e:
    print(f"Error: {e}")
