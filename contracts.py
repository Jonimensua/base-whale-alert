import os
import time
import requests
from web3 import Web3

BASE_RPC = os.getenv("BASE_RPC")
PUBLISHER_URL = os.getenv("PUBLISHER_URL")

w3 = Web3(Web3.HTTPProvider(BASE_RPC))

print("🚀 Base Intelligence Engine iniciado")
print("Connected to Base:", w3.eth.block_number)

last_block = w3.eth.block_number

tracked_contracts = {}


def send_to_publisher(content):

    try:

        content = content[:260]

        res = requests.post(
            f"{PUBLISHER_URL}/post",
            json={"content": content},
            timeout=30
        )

        print("Publisher status:", res.status_code)

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

                    # detectar contrato nuevo
                    if tx.to is None:

                        receipt = w3.eth.get_transaction_receipt(tx.hash)

                        gas_used = receipt.gasUsed

                        if gas_used < 400000:
                            continue

                        contract = receipt.contractAddress

                        tracked_contracts[contract] = block_number

                        print("New contract tracked:", contract)

                    # detectar liquidez
                    if tx.to in tracked_contracts:

                        eth_value = w3.from_wei(tx.value, "ether")

                        if eth_value > 0.1:

                            tx_hash = tx.hash.hex()

                            post = f"""
🚨 NEW BASE TOKEN

Liquidity: {eth_value} ETH

Tx:
{tx_hash}

#Base #Memecoin

/community/1991809112070557893
"""

                            print("Publishing alert")

                            send_to_publisher(post)

                            del tracked_contracts[tx.to]

        last_block = latest_block

        time.sleep(10)

    except Exception as e:

        print("Loop error:", e)

        time.sleep(10)
