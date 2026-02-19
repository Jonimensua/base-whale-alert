import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

GAS_THRESHOLD = 1000000

deployer_count = {}

def enviar_telegram(texto):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    requests.post(url, data=data)

def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    r = requests.post(BASE_RPC, json=payload)
    return r.json()["result"]

def get_latest_block():
    return int(rpc_call("eth_blockNumber", []), 16)

def get_block(num):
    return rpc_call("eth_getBlockByNumber", [hex(num), True])

def main():
    print("Contract monitor running")
    ultimo = get_latest_block()

    while True:
        try:
            time.sleep(10)
            actual = get_latest_block()

            if actual > ultimo:
                bloque = get_block(actual)

                for tx in bloque["transactions"]:
                    if tx["to"] is None:

                        gas = int(tx["gas"], 16)
                        value = int(tx["value"], 16) / (10**18)

                        if gas >= GAS_THRESHOLD or value > 0:

                            creator = tx["from"]

                            if creator not in deployer_count:
                                deployer_count[creator] =
