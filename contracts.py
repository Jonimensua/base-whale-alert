import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PUBLISHER_URL = os.getenv("PUBLISHER_URL")

# filtro contratos basura
GAS_THRESHOLD = 1200000

# evitar duplicados
seen_contracts = set()


def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    try:
        r = requests.post(BASE_RPC, json=payload, timeout=10)
        return r.json()["result"]
    except:
        return None


def get_latest_block():
    block = rpc_call("eth_blockNumber", [])
    return int(block, 16)


def get_block(block_number):
    return rpc_call("eth_getBlockByNumber", [hex(block_number), True])


def send_telegram(message):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload, timeout=10)
    except:
        print("Telegram error")


def publish_to_typefully(message):

    if not PUBLISHER_URL:
        print("Publisher not configured")
        return

    try:

        print("Publishing alert")

        r = requests.post(
            PUBLISHER_URL,
            json={"content": message},
            timeout=20
        )

        print("Publisher status:", r.status_code)

    except Exception as e:
        print("Publisher error:", e)


def format_message(tx_hash, gas_used, value):

    value_eth = value / 10**18

    message = (
        "🚨 BASE CONTRACT DEPLOYED\n"
        f"Gas: {gas_used}\n"
        f"ETH: {value_eth:.4f}\n"
        f"https://basescan.org/tx/{tx_hash}\n"
        "#Base #OnChain"
    )

    return message


def monitor():

    print("Base contract monitor started")

    last_block = get_latest_block()

    while True:

        try:

            current_block = get_latest_block()

            if current_block > last_block:

                block = get_block(current_block)

                if not block:
                    time.sleep(2)
                    continue

                for tx in block["transactions"]:

                    if tx["to"] is None:

                        tx_hash = tx["hash"]

                        if tx_hash in seen_contracts:
                            continue

                        gas_used = int(tx["gas"], 16)
                        value = int(tx["value"], 16)

                        if gas_used < GAS_THRESHOLD:
                            continue

                        seen_contracts.add(tx_hash)

                        message = format_message(tx_hash, gas_used, value)

                        print(message)

                        send_telegram(message)

                        publish_to_typefully(message)

                last_block = current_block

            time.sleep(2)

        except Exception as e:

            print("Monitor error:", e)
            time.sleep(5)


if __name__ == "__main__":
    monitor()
