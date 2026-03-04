import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PUBLISHER_URL = os.getenv("PUBLISHER_URL")

MIN_GAS_DEPLOY = 3000000
MIN_ETH_VALUE = 0.5
MIN_LIQUIDITY = 2
COOLDOWN_SECONDS = 600

tracked_contracts = {}
last_alert_time = 0


def enviar_telegram(texto):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        r = requests.post(url, data=data)
        print("Telegram:", r.text)
    except Exception as e:
        print("Telegram error:", e)


def publicar_en_x(texto):

    if not PUBLISHER_URL:
        print("Publisher no configurado")
        return

    try:

        r = requests.post(
            PUBLISHER_URL + "/post",
            json={"content": texto}
        )

        print("Publisher status:", r.status_code)

    except Exception as e:

        print("Publisher error:", e)


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


def run_contract_monitor():

    global last_alert_time

    print("🔥 Base Intelligence Engine iniciado")

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

                block_data = get_block(bloque_actual)

                if not block_data:
                    continue

                for tx in block_data["transactions"]:

                    # NUEVO CONTRATO
                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        valor_eth = int(tx["value"], 16) / (10**18)

                        if gas_used < MIN_GAS_DEPLOY and valor_eth < MIN_ETH_VALUE:
                            continue

                        now = time.time()

                        if now - last_alert_time < COOLDOWN_SECONDS:
                            continue

                        last_alert_time = now

                        contract_hash = tx["hash"]

                        tracked_contracts[contract_hash] = bloque_actual

                        mensaje = (
                            "🚀 BASE NETWORK — NEW SMART CONTRACT\n\n"
                            f"Gas Used: {gas_used}\n"
                            f"ETH Value: {valor_eth:.4f}\n\n"
                            f"Tx:\n{contract_hash}\n\n"
                            "---\n"
                            "On-Chain Intelligence"
                        )

                        print(mensaje)

                        enviar_telegram(mensaje)
                        publicar_en_x(mensaje)

                    # DETECCION DE LIQUIDEZ

                    for contract, start_block in list(tracked_contracts.items()):

                        if bloque_actual - start_block <= 50:

                            value = int(tx["value"], 16) / (10**18)

                            if value >= MIN_LIQUIDITY and tx["to"] == contract:

                                alerta = (
                                    "💰 BASE NETWORK — LIQUIDITY DETECTED\n\n"
                                    f"Liquidity Added: {value:.4f} ETH\n"
                                    f"Contract Tx:\n{contract}\n\n"
                                    "---\n"
                                    "On-Chain Intelligence"
                                )

                                print(alerta)

                                enviar_telegram(alerta)
                                publicar_en_x(alerta)

                                del tracked_contracts[contract]

                        else:
                            del tracked_contracts[contract]

                ultimo_bloque = bloque_actual

        except Exception as e:

            print("Loop error:", e)
            time.sleep(5)


if __name__ == "__main__":

    run_contract_monitor()
