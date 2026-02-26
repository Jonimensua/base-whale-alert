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
    return r.json()["result"]


def get_latest_block():
    return int(rpc_call("eth_blockNumber", []), 16)


def get_block(num):
    return rpc_call("eth_getBlockByNumber", [hex(num), True])


def generate_interpretation(contract_count, liquidity_count, largest_tx):

    interpretation = []

    if contract_count > 5:
        interpretation.append("High deployment activity suggests active builder momentum.")
    else:
        interpretation.append("Deployment activity remains moderate.")

    if liquidity_count > 2:
        interpretation.append("Multiple contracts received early liquidity.")
    elif liquidity_count > 0:
        interpretation.append("Selective liquidity observed.")
    else:
        interpretation.append("No significant early liquidity detected.")

    if largest_tx > 3:
        interpretation.append("Notable whale movement detected.")
    else:
        interpretation.append("Whale activity remains within normal range.")

    return " ".join(interpretation)


def run_report():

    latest = get_latest_block()
    start_block = latest - 400  # ~12h approx

    contract_count = 0
    liquidity_count = 0
    largest_tx = 0

    tracked_contracts = {}

    for block_number in range(start_block, latest + 1):
        block = get_block(block_number)

        for tx in block["transactions"]:
            value = int(tx["value"], 16) / (10**18)

            if value >= WHALE_THRESHOLD:
                if value > largest_tx:
                    largest_tx = value

            if tx["to"] is None:
                gas = int(tx["gas"], 16)
                if gas >= GAS_THRESHOLD:
                    contract_count += 1
                    tracked_contracts[tx["hash"]] = block_number

            for contract_hash in list(tracked_contracts.keys()):
                if tx["to"] == contract_hash and value > 0:
                    liquidity_count += 1
                    del tracked_contracts[contract_hash]

    interpretation = generate_interpretation(contract_count, liquidity_count, largest_tx)

    telegram_message = (
        "BASE NETWORK — 12H ACTIVITY REPORT\n\n"
        f"• High-gas deployments: {contract_count}\n"
        f"• Liquidity events detected: {liquidity_count}\n"
        f"• Largest whale: {round(largest_tx,4)} ETH\n\n"
        "Interpretation:\n\n"
        f"{interpretation}\n\n"
        "—\n"
        "Automated On-Chain Intelligence"
    )

    farcaster_ready = (
        f"Base 12H snapshot:\n\n"
        f"{contract_count} high-gas deployments.\n"
        f"{liquidity_count} contracts received liquidity.\n"
        f"Largest whale: {round(largest_tx,4)} ETH.\n\n"
        "Builder momentum remains active."
    )

    print("TELEGRAM VERSION:\n", telegram_message)
    print("\nFARCASTER VERSION:\n", farcaster_ready)

    enviar_telegram(telegram_message)


if __name__ == "__main__":
    print("12H Report Service Started")

    while True:
        run_report()
        time.sleep(43200)  # 12 hours
