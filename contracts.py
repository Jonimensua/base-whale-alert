import requests
import time
import os

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
    print("📦 Contract Monitor iniciado")
    ultimo_bloque = get_latest_block()

    while True:
        try:
            time.sleep(10)
            bloque_actual = get_latest_block()

            if bloque_actual > ultimo_bloque:
                block_data = get_block(bloque_actual)

                for tx in block_data["transactions"]:
                    if tx["to"] is None:
                        mensaje = (
                            "🆕 NUEVO CONTRATO DESPLEGADO EN BASE\n\n"
                            f"📤 Creator: {tx['from']}\n"
                            f"🔗 Tx Hash:\n{tx['hash']}\n\n"
                            "#Base #NewContract #OnChain"
                        )

                        print(mensaje)
                        enviar_telegram(mensaje)

                ultimo_bloque = bloque_actual

        except Exception as e:
            print("Error en contract monitor:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
