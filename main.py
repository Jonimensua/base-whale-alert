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


# Test manual
if __name__ == "__main__":
    publish_to_x("Testing Base automation final.")
