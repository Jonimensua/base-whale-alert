import requests
import os
import time
import random

DEX_URL = "https://api.dexscreener.com/latest/dex/search/?q=base"
POST_INTERVAL_SECONDS = 21600  # 6 horas

MIN_LIQUIDITY = 150000
MIN_VOLUME = 300000
MIN_PRICE_CHANGE = 12

TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY")


def get_base_pairs():
    try:
        response = requests.get(DEX_URL)
        data = response.json()
        return data.get("pairs", [])
    except Exception as e:
        print("Error fetching pairs:", e)
        return []


def filter_pairs(pairs):
    opportunities = []

    for pair in pairs:
        try:
            liquidity = float(pair.get("liquidity", {}).get("usd", 0))
            volume = float(pair.get("volume", {}).get("h24", 0))
            price_change = float(pair.get("priceChange", {}).get("h24", 0))

            if liquidity > MIN_LIQUIDITY and volume > MIN_VOLUME and abs(price_change) > MIN_PRICE_CHANGE:
                opportunities.append(pair)

        except Exception:
            continue

    return opportunities


def generate_post(pair):
    name = pair["baseToken"]["name"]
    volume = float(pair["volume"]["h24"])
    liquidity = float(pair["liquidity"]["usd"])
    change = float(pair["priceChange"]["h24"])

    return f"""{name} showing expansion on Base.

24h Volume: ${int(volume):,}
Liquidity: ${int(liquidity):,}
Price change: {change:.2f}%

Momentum building.
Watching closely.
"""


def post_to_typefully(text):
    try:
        url = "https://api.typefully.com/v1/drafts/"
        headers = {
            "X-API-KEY": TYPEFULLY_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "content": text,
            "auto_post": True
        }

        response = requests.post(url, json=payload, headers=headers)
        print("Typefully response:", response.status_code, response.text)

    except Exception as e:
        print("Error posting:", e)


def run_engine():
    pairs = get_base_pairs()
    filtered = filter_pairs(pairs)

    if not filtered:
        print("No opportunities found.")
        return

    selected = random.choice(filtered)
    post = generate_post(selected)

    print("Posting:\n", post)
    post_to_typefully(post)


def main():
    print("🚀 Base Intelligence Engine iniciado...")

    while True:
        try:
            run_engine()
            time.sleep(POST_INTERVAL_SECONDS)
        except Exception as e:
            print("Loop error:", e)
            time.sleep(60)


if __name__ == "__main__":
    main()
