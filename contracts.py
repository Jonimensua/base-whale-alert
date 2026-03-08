import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PUBLISHER_URL = os.getenv("PUBLISHER_URL")

# FILTROS
MIN_GAS = 1200000
MIN_ETH = 0

# TIEMPO MINIMO ENTRE POSTS
POST_DELAY = 180

last_post = 0


def enviar_telegram(texto):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass


def publicar(texto):

    if not PUBLISHER_URL:
        return

    try:
        requests.post(
            PUBLISHER_URL + "/post",
            json={"content": texto},
            timeout=10
        )
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
        return r.json()["result"]
    except:
        return None


def get_latest_block():

    result = rpc_call("eth_blockNumber", [])

    if result:
        return int(result, 16)

    return None


def get_block(num):

    return rpc_call("eth_getBlockByNumber", [hex(num), True])


def run_contract_monitor():

    global last_post

    print("🚀 Base Contract Monitor iniciado")

    ultimo_bloque = get_latest_block()

    if not ultimo_bloque:
        print("Error obteniendo bloque inicial")
        return

    while True:

        try:

            time.sleep(10)

            bloque_actual = get_latest_block()

            if not bloque_actual:
                continue

            if bloque_actual > ultimo_bloque:

                block = get_block(bloque_actual)

                if not block:
                    continue

                for tx in block["transactions"]:

                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        eth_value = int(tx["value"], 16) / (10**18)

                        # FILTRO GAS
                        if gas_used < MIN_GAS:
                            continue

                        # FILTRO ETH
                        if eth_value < MIN_ETH:
                            continue

                        now = time.time()

                        # RATE LIMIT
                        if now - last_post < POST_DELAY:
                            continue

                        last_post = now

                        contract_hash = tx["hash"]

                        # MENSAJE PARA X (menos de 280 chars)
                        mensaje = (
                            f"🚨 New contract deployed on Base\n\n"
                            f"Gas: {gas_used}\n"
                            f"Value: {eth_value:.3f} ETH\n\n"
                            f"https://basescan.org/tx/{contract_hash}"
                        )

                        print(mensaje)

                        enviar_telegram(mensaje)

                        publicar(mensaje)

                ultimo_bloque = bloque_actual

        except Exception as e:

            print("Error:", e)

            time.sleep(5)


if __name__ == "__main__":

    run_contract_monitor()
