import requests
import os
import time

POST_INTERVAL_SECONDS = 60  # test, luego lo subimos a 21600

TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY")
SOCIAL_SET_ID = 287271  # tu social set

def post_to_typefully(text):
    if not TYPEFULLY_API_KEY:
        print("ERROR: TYPEFULLY_API_KEY not set.")
        return

    try:
        url = "https://api.typefully.com/v1/drafts/"
        headers = {
            "X-API-KEY": TYPEFULLY_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "content": text,
            "social_set_ids": [SOCIAL_SET_ID],
            "auto_post": True
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print("Typefully response:", response.status_code)
        print("Response body:", response.text)

    except Exception as e:
        print("Error posting:", e)


def run_engine():
    print("Publishing test post...")

    test_post = """Base structural momentum building.

Liquidity expanding.
Volume rising.
Smart capital positioning early.

Monitoring closely.
"""

    post_to_typefully(test_post)


def main():
    print("🚀 Base Intelligence Engine iniciado...")

    while True:
        try:
            run_engine()
            time.sleep(POST_INTERVAL_SECONDS)
        except Exception as e:
            print("Loop error:", e)
            time.sleep(30)


if __name__ == "__main__":
    main()
