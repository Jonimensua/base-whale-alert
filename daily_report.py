import requests
import time
import os
from datetime import datetime, timedelta, timezone

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

WHALE_THRESHOLD = 1
GAS_THRESHOLD = 1000000


def enviar_telegram(texto):
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


def run_daily_report():
    print("Running daily report...")

    latest = get_latest_block()
    start_block = latest - 300

    whale_count = 0
    contract_count = 0
    largest_tx = 0

    for block_number in range(start_block, latest + 1):
        block = get_block(block_number)

        for tx in block["transactions"]:
            value = int(tx["value"], 16) / (10**18)

            if value >= WHALE_THRESHOLD:
                whale_count += 1
                if value > largest_tx:
                    largest_tx = value

            if tx["to"] is None:
                gas = int(tx["gas"], 16)
                if gas >= GAS_THRESHOLD:
                    contract_count += 1

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    message = (
        "BASE NETWORK — TOP ACTIVITY (24H)\n\n"
        f"🔥 Largest Whale: {round(largest_tx,4)} ETH\n"
        f"🚀 High Gas Deployments: {contract_count}\n"
        f"💧 Whale Transactions: {whale_count}\n\n"
        "Base remains active.\n\n"
        "—\n"
        "Automated On-Chain Intelligence"
    )

    print(message)
    enviar_telegram(message)


def wait_until_midnight_utc():
    while True:
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        seconds_until_midnight = (tomorrow - now).total_seconds()
        time.sleep(seconds_until_midnight)
        run_daily_report()


if __name__ == "__main__":
    print("Daily Report Service Started (UTC schedule)")
    wait_until_midnight_utc()
