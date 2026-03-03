import requests
import time
import os
from openai import OpenAI

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SLEEP_TIME = 8


def enviar_telegram(texto):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram error:", e)


def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    try:
        r = requests.post(BASE_RPC, json=payload, timeout=10)
        return r.json().get("result")
    except Exception as e:
        print("RPC error:", e)
        return None


def get_latest_block():
    result = rpc_call("eth_blockNumber", [])
    if result:
        return int(result, 16)
    return None


def get_block(num):
    return rpc_call("eth_getBlockByNumber", [hex(num), True])


def get_tx_count(address):
    result = rpc_call("eth_getTransactionCount", [address, "latest"])
    if result:
        return int(result, 16)
    return 0


def get_balance(address):
    result = rpc_call("eth_getBalance", [address, "latest"])
    if result:
        return int(result, 16) / (10**18)
    return 0


def generate_analysis(gas_used, eth_value, tx_count, balance):

    prompt = f"""
    Analyze this Base network smart contract deployment:

    Gas Used: {gas_used}
    ETH Sent: {eth_value}
    Wallet Tx Count: {tx_count}
    Wallet Balance: {balance} ETH

    Determine if this looks like:
    - A serious project launch
    - A coordinated deployment
    - Or low-quality noise

    Be concise and professional.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert crypto on-chain analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def run_contract_monitor():

    print("🔥 Base Intelligence Engine + AI iniciado")

    ultimo_bloque = get_latest_block()
    if not ultimo_bloque:
        return

    while True:
        try:
            time.sleep(SLEEP_TIME)

            bloque_actual = get_latest_block()
            if not bloque_actual:
                continue

            if bloque_actual > ultimo_bloque:

                block_data = get_block(bloque_actual)
                if not block_data:
                    continue

                for tx in block_data["transactions"]:

                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        eth_value = int(tx["value"], 16) / (10**18)
                        deployer = tx["from"]
                        tx_hash = tx["hash"]

                        # Filtro equilibrado
                        if gas_used > 3000000 and eth_value > 0.2:

                            tx_count = get_tx_count(deployer)
                            balance = get_balance(deployer)

                            if tx_count > 300 and balance > 3:

                                analysis = generate_analysis(
                                    gas_used,
                                    eth_value,
                                    tx_count,
                                    balance
                                )

                                mensaje = (
                                    "🚨 HIGH-CONVICTION DEPLOY\n\n"
                                    f"Deployer: {deployer}\n"
                                    f"Gas Used: {gas_used}\n"
                                    f"ETH Value: {eth_value:.4f}\n"
                                    f"Tx Count: {tx_count}\n"
                                    f"Balance: {balance:.4f} ETH\n\n"
                                    "🧠 AI Insight:\n"
                                    f"{analysis}\n\n"
                                    f"Tx Hash:\n{tx_hash}\n\n"
                                    "---\n"
                                    "Base Intelligence Engine"
                                )

                                enviar_telegram(mensaje)

                ultimo_bloque = bloque_actual

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)


if __name__ == "__main__":
    run_contract_monitor()
