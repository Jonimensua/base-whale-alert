import requests
import os

TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY")
SOCIAL_SET_ID = 287271

print("Loaded key:", TYPEFULLY_API_KEY)

url = "https://api.typefully.com/v1/drafts"

headers = {
    "X-API-KEY": TYPEFULLY_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "content": "Testing Base automation final.",
    "social_set_ids": [SOCIAL_SET_ID],
    "auto_post": True
}

response = requests.post(url, json=payload, headers=headers)

print("Status:", response.status_code)
print("Body:", response.text)
