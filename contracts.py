import os
import time
import requests
from web3 import Web3
from datetime import datetime

# ==============================
# ENVIRONMENT VARIABLES
# ==============================

BASE_RPC = os.getenv("BASE_RPC")
PUBLISHER_URL = os.getenv("PUBLISHER_URL")

if not BASE_RPC:
    raise ValueError("BASE_RPC not found in environment variables")

if not PUBLISHER_URL:
    raise ValueError("PUBLISHER_URL not found in environment variables")

print("BASE_RPC loaded:", BASE_RPC[:30], "...")
print("Publisher URL:", PUBLISHER_URL)

# ==============================
# WEB3 CONNECTION
# ==============================

web3 = Web3(Web3.HTTPProvider(BASE_RPC))

if not web3.is_connected():
    raise ConnectionError("Failed to connect to BASE RPC")

print("Connected to Base. Current block:", web3.eth.block_number)

# ==============================
# CONFIG
# ==============================

ANALYSIS_INTERVAL = 1800  # 30 minutes
WHALE_THRESHOLD_ETH = 50  # Adjust as needed

last_analysis_time = 0
last_checked_block = web3.eth.block_number

# ==============================
# PUBLISH FUNCTION
# ==============================

def publish_to_x(content):
    try:
        response = requests.post(
            f"{PUBLISHER_URL}/post",
            json={"content": content},
            timeout=20
        )

        print("Publisher status:", response.status_code)
        print("Publisher body:", response.text)

    except Exception as e:
        print("Publish error:", str(e))


# ==============================
# WHALE DETECTION
# ==============================

def check_block_for_whales(block_number):
    block = web3.eth.get_block(block_number, full_transactions=True)

    for tx in block.transactions:
        eth_value = web3.from_wei(tx.value, "ether")

        if eth_value >= WHALE_THRESHOLD_ETH:
            message = f"""
🐋 Whale Alert on Base

Block: {block_number}
Value: {eth_value:.2f} ETH
Tx: https://basescan.org/tx/{tx.hash.hex()}

#Base #WhaleAlert
"""
            publish_to_x(message)


# ==============================
# PERIODIC ANALYSIS
# ==============================

def periodic_analysis():
    latest_block = web3.eth.block_number
    block = web3.eth.get_block(latest_block)

    tx_count = len(block.transactions)

    message = f"""
📊 Base Network Update

Block: {latest_block}
Transactions in block: {tx_count}
Time: {datetime.utcnow().strftime('%H:%M UTC')}

#Base #Onchain
"""
    publish_to_x(message)


# ==============================
# MAIN LOOP
# ==============================

print("🔥 Base Intelligence Engine iniciado")

while True:
    try:
        current_block = web3.eth.block_number

        # Check new blocks for whales
        if current_block > last_checked_block:
            for block_num in range(last_checked_block + 1, current_block + 1):
                print("Checking block:", block_num)
                check_block_for_whales(block_num)

            last_checked_block = current_block

        # Periodic analysis
        current_time = time.time()
        if current_time - last_analysis_time > ANALYSIS_INTERVAL:
            print("Running periodic analysis...")
            periodic_analysis()
            last_analysis_time = current_time

        time.sleep(10)

    except Exception as e:
        print("Main loop error:", str(e))
        time.sleep(15)
