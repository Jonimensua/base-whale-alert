import requests
import os

PUBLISHER_URL = os.getenv("PUBLISHER_URL")

def publish_to_x(content):
    response = requests.post(
        f"{PUBLISHER_URL}/post",
        json={"content": content}
    )

    print("Publisher status:", response.status_code)
    print("Publisher body:", response.text)
payload = {
    "content": "Testing Base automation final.",
    "social_set_ids": [SOCIAL_SET_ID],
    "auto_post": True
}

response = requests.post(url, json=payload, headers=headers)

print("Status:", response.status_code)
print("Body:", response.text)

