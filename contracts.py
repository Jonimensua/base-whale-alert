import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

GAS_THRESHOLD = 1000000

deployer_count = {}

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": mensaje
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Error enviando a Telegram:", e)

def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    response = requests.post(BASE_RPC, json=payload, timeout=10)
    return response.json()["result"]

def get_latest_block():
    return int(rpc_call("eth_blockNumber", []), 16)

def get_block(block_number):
    return rpc_call("eth_getBlockByNumber", [hex(block_number), True])

def main():
    print("Contract Monitor iniciado")
    ultimo_bloque = get_latest_block()

    while True:
        try:
            time.sleep(10)
            bloque_actual = get_latest_block()

            if bloque_actual > ultimo_bloque:
                block_data = get_block(bloque_actual)

                for tx in block_data["transactions"]:

                    if tx["to"] is None:

                        gas_used = int(tx["gas"], 16)
                        valor_eth = int(tx["value"], 16) / (10**18)

                        if gas_used >= GAS_THRESHOLD or valor_eth > 0:

                            creator = tx["from"]

                            # Contador de deploys
                            if creator not in deployer_count:
                                deployer_count[creator] = 1
                            else:
                                deployer_count[creator] += 1

                            # Alerta por deploy repetido
                            if deployer_count[creator] >= 2:
                                alerta_repetida = (
                                    "REPEATED CONTRACT DEPLOYER\n\n"
                                    "Creator: " + creator + "\n"
                                    "Deployments detected: " + str(deployer_count[creator]) + "\n\n"
                                    "#Base #SmartMoney #OnChain"
                                )

                                print(alerta_repetida)
                                enviar_telegram(alerta_repetida)

                            # Mensaje normal
                            mensaje = (
                                "SMART CONTRACT DEPLOYED\n\n"
                                "Gas: " + str(gas_used) + "\n"
                                "Value: " + str(round(valor_eth, 4)) + " ETH\n"
