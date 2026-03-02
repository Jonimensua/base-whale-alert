import requests
import os
import time
import random

# ==============================
# CONFIGURACIÓN
# ==============================

DEX_URL = "https://api.dexscreener.com/latest/dex/search/?q=base"

# MODO TEST (cambiar luego a 21600)
POST_INTERVAL_SECONDS = 60  

MIN_LIQUIDITY = 50000
MIN_VOLUME = 80000
MIN_PRICE_CHANGE = 4

TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY")

# ==============================
# FUNCIONES
# ==============================

def get_base_pairs():
    try:
        response = requests.get(DEX_URL, timeout=10)
        response.raise_for_status()
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

            if (
                liquidity > MIN_LIQUIDITY
                and volume > MIN_VOLUME
                and abs(price_change) > MIN_PRICE_CHANGE
            ):
                opportunities.append(pair)

        except Exception:
            continue

    return opportunities


def generate_post(pair):
    name = pair.get("baseToken", {}).get("name", "Unknown")
    volume = float(pair.get("volume", {}).get("h24", 0))
    liquidity = float(pair.get("liquidity", {}).get("usd", 0))
    change = float(pair.get("priceChange", {}).get("h24", 0))

    return f"""{name} gaining momentum on Base.

24h Volume: ${int(volume):,}
Liquidity: ${int(liquidity):,}
Price change: {change:.2f}%

Early expansion phase.
Watching closely.
"""


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
            "auto_post": True
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print("Typefully response:", response.status_code, response.text)

    except Exception as e:
        print("Error posting:", e)


def run_engine():
    print("Checking opportunities...")

    pairs = get_base_pairs()
    if not pairs:
        print("No pairs returned from API.")
        return

    filtered = filter_pairs(pairs)

    if not filtered:
        print("No opportunities found.")
        return

    selected = random.choice(filtered)
    post = generate_post(selected)

    print("Posting:\n", post)
    post_to_typefully(post)


# ==============================
# LOOP PRINCIPAL
# ==============================

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
