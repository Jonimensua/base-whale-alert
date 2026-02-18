import requests
import time

# ================= CONFIGURACIÓN =================

BASE_RPC = "https://mainnet.base.org"

TELEGRAM_TOKEN = "8544264445:AAG78xl8HIp5sTyv_ZZESTqdPQQ0qcmG3Tk"
CHAT_ID = "-1003841254712"

ETH_THRESHOLD = 1  # Cambia solo esto si quieres otro filtro

# =================================================

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
    print("🚀 Base Whale Alert iniciado...")
    ultimo_bloque = get_latest_block()
    print("Bloque actual:", ultimo_bloque)

    while True:
        try:
            time.sleep(10)
            bloque_actual = get_latest_block()

            if bloque_actual > ultimo_bloque:
                block_data = get_block(bloque_actual)

                for tx in block_data["transactions"]:
                    valor_eth = int(tx["value"], 16) / (10**18)

                    if valor_eth >= ETH_THRESHOLD:
                        mensaje = (
                            "🚨 BASE WHALE ALERT 🚨\n\n"
                            f"💰 Valor: {valor_eth:.4f} ETH\n"
                            f"📤 From: {tx['from']}\n"
                            f"📥 To: {tx['to']}\n\n"
                            f"🔗 Tx Hash:\n{tx['hash']}\n\n"
                            "#Base #Whale #OnChain"
                        )

                        print(mensaje)
                        enviar_telegram(mensaje)

                ultimo_bloque = bloque_actual

        except Exception as e:
            print("Error en el loop principal:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
