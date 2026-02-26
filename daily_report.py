import requests
import time
import os
from datetime import datetime, timezone

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

WHALE_THRESHOLD = 1
GAS_THRESHOLD = 1000000


def enviar_telegram(texto):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram variables not set")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": texto}
    requests.post(url, data=data)


def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    r = requests.post(BASE_RPC, json=payload)
    return r
