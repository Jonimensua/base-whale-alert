import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PUBLISHER_URL = os.getenv("PUBLISHER_URL")

# FILTRO SIMPLE (solo esto cambia)
MIN_GAS = 3000000
MIN_ETH = 0.5

tracked_contracts = {}

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


def publicar(texto):

    if not PUBLISHER_URL:
        return

    try:

        requests.post(
            PUBLISHER_URL + "/post",
            json={"content": texto}
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

        r = requests.post(BASE_RPC, json=payload)

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

    print("Base Contract Monitor iniciado")

    ultimo_bloque = get_latest_block()

    while True:

        try:

            time.sleep(10)

            bloque_actual = get_latest_block()

            if bloque_actual > ultimo_bloque:

                block = get_block(bloque_actual)

                if not block:
                    continue

                for tx in block["transactions"]:

                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        valor_eth = int(tx["value"], 16) / (10**18)

                        # FILTRO (esto evita ruido)
                        if gas_used < MIN_GAS and valor_eth < MIN_ETH:
                            continue

                        contract_hash = tx["hash"]

                        tracked_contracts[contract_hash] = bloque_actual

                        mensaje = (
                            "BASE NETWORK — NEW SMART CONTRACT\n\n"
                            f"Gas Used: {gas_used}\n"
                            f"ETH Value: {valor_eth:.4f}\n"
                            f"Tx:\n{contract_hash}"
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
