import os
import time
import requests
from web3 import Web3

BASE_RPC = os.getenv("BASE_RPC")
PUBLISHER_URL = os.getenv("PUBLISHER_URL")

w3 = Web3(Web3.HTTPProvider(BASE_RPC))

print("🚀 Base Contract Monitor iniciado")
print("Connected to Base. Current block:", w3.eth.block_number)

last_block = w3.eth.block_number


def send_to_publisher(content):
    try:

        # límite para Typefully
        content = content[:260]

        res = requests.post(
            f"{PUBLISHER_URL}/post",
            json={"content": content},
            timeout=30
        )

        print("Publisher status:", res.status_code)
        print("Publisher body:", res.text)

    except Exception as e:
        print("Publisher error:", e)


while True:
    try:

        latest_block = w3.eth.block_number

        if latest_block > last_block:

            for block_number in range(last_block + 1, latest_block + 1):

                print("Checking block:", block_number)

                block = w3.eth.get_block(block_number, full_transactions=True)

                for tx in block.transactions:

                    # contrato nuevo
                    if tx.to is None:

                        receipt = w3.eth.get_transaction_receipt(tx.hash)

                        gas_used = receipt.gasUsed

                        # filtro para evitar contratos basura
                        if gas_used < 1000000:
                            continue

                        eth_value = w3.from_wei(tx.value, "ether")

                        tx_hash = tx.hash.hex()

                        post = f"""
🚨 BASE CONTRACT DEPLOYED

Gas: {gas_used}
ETH: {eth_value}

Tx:
{tx_hash}

#Base #OnChain

/community/1991809112070557893
"""

                        print("Publishing alert")

                        send_to_publisher(post)

        last_block = latest_block

        time.sleep(10)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
