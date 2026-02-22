import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

GAS_THRESHOLD = 1000000
TRACK_BLOCKS = 50

tracked_contracts = {}


def enviar_telegram(texto):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERROR: TELEGRAM_TOKEN or CHAT_ID not set")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        response = requests.post(url, data=data)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram send error:", e)


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
        print("RPC Error:", e)
        return None


def get_latest_block():
    result = rpc_call("eth_blockNumber", [])
    if result:
        return int(result, 16)
    return None


def get_block(num):
    return rpc_call("eth_getBlockByNumber", [hex(num), True])


def main():
    print("Contract + Liquidity Monitor iniciado")

    ultimo_bloque = get_latest_block()
    if not ultimo_bloque:
        print("Error getting initial block")
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

                    # Detectar contrato nuevo
                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        valor_eth = int(tx["value"], 16) / (10**18)

                        if gas_used >= GAS_THRESHOLD or valor_eth > 0:

                            contract_hash = tx["hash"]
                            tracked_contracts[contract_hash] = bloque_actual

                            mensaje = (
                                "BASE NETWORK — NEW SMART CONTRACT\n\n"
                                f"Gas Used: {gas_used}\n"
                                f"ETH Value: {valor_eth:.4f}\n"
                                f"Tx Hash:\n{contract_hash}\n\n"
                                "---\n"
                                "On-Chain Intelligence"
                            )

                            print(mensaje)
                            enviar_telegram(mensaje)

                    # Detectar liquidez en contratos rastreados
                    for contract, start_block in list(tracked_contracts.items()):

                        if bloque_actual - start_block <= TRACK_BLOCKS:

                            value = int(tx["value"], 16) / (10**18)

                            if value > 0 and tx["to"] == contract:

                                alerta = (
                                    "BASE NETWORK — LIQUIDITY DETECTED\n\n"
                                    f"Contract Tx: {contract}\n"
                                    f"Liquidity Added: {value:.4f} ETH\n"
                                    f"Block: {bloque_actual}\n\n"
                                    "---\n"
                                    "On-Chain Intelligence"
                                )

                                print(alerta)
                                enviar_telegram(alerta)

                                del tracked_contracts[contract]

                        else:
                            del tracked_contracts[contract]

                ultimo_bloque = bloque_actual

        except Exception as e:
            print("Main loop error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
