import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Configuración inteligente
GAS_THRESHOLD = 1500000
MIN_SCORE = 70
SLEEP_TIME = 8


def enviar_telegram(texto):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        requests.post(url, data=data)
    except:
        pass


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
    except:
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


def score_deployer(deployer, gas_used, eth_value):
    score = 0

    tx_count = get_tx_count(deployer)
    balance = get_balance(deployer)

    # Gas alto
    if gas_used > 3000000:
        score += 20

    # ETH enviado en el deploy
    if eth_value > 0:
        score += 20

    # Wallet activa
    if tx_count > 50:
        score += 20

    # Wallet con balance relevante
    if balance > 1:
        score += 20

    # Wallet muy activa
    if tx_count > 200:
        score += 20

    return score, tx_count, balance


def run_contract_monitor():

    print("Advanced On-Chain Intelligence Engine iniciado")

    ultimo_bloque = get_latest_block()
    if not ultimo_bloque:
        print("No se pudo obtener bloque inicial")
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

                    # Detectar contrato nuevo
                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        eth_value = int(tx["value"], 16) / (10**18)
                        deployer = tx["from"]
                        tx_hash = tx["hash"]

                        # Filtro inicial
                        if gas_used < GAS_THRESHOLD and eth_value == 0:
                            continue

                        score, tx_count, balance = score_deployer(deployer, gas_used, eth_value)

                        if score >= MIN_SCORE:

                            mensaje = (
                                "🚨 HIGH-POTENTIAL DEPLOY DETECTED\n\n"
                                f"Deployer: {deployer}\n"
                                f"Gas Used: {gas_used}\n"
                                f"ETH Value: {eth_value:.4f}\n"
                                f"Tx Count: {tx_count}\n"
                                f"Balance: {balance:.4f} ETH\n"
                                f"Score: {score}/100\n\n"
                                f"Tx Hash:\n{tx_hash}\n\n"
                                "---\n"
                                "On-Chain Intelligence Engine"
                            )

                            print(mensaje)
                            enviar_telegram(mensaje)

                ultimo_bloque = bloque_actual

        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)
            if __name__ == "__main__":
    run_contract_monitor()
