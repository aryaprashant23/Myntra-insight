import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv('backend/.env')

try:
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    models = client.models.list()
    print("\n--- AVAILABLE GROQ MODELS FOR YOUR API KEY ---")
    for m in models.data:
        print(f"- {m.id}")
    print("----------------------------------------------\n")
except Exception as e:
    print(f"Failed to fetch models: {e}")
