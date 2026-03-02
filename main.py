import requests
import os
import time
import random

# ==============================
# CONFIGURACIÓN
# ==============================

DEX_URL = "https://api.dexscreener.com/latest/dex/search/?q=base"
POST_INTERVAL_SECONDS = 21600  # 6 horas
MIN_LIQUIDITY = 150000
MIN_VOLUME = 300000
MIN_PRICE_CHANGE = 12

TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY")


# ==============================
# FUNCIONES
# ==============================

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

            if (
                liquidity
