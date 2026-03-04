import os
import time
import requests
from web3 import Web3
from datetime import datetime, timezone

# ==============================
# ENV
# ==============================

BASE_RPC = os.environ["BASE_RPC"]
PUBLISHER_URL = os.environ["PUBLISHER_URL"]

# ==============================
# CONNECTION
# ==============================

web3 = Web3(Web3.HTTPProvider(BASE_RPC))

if not web3.is_connected():
    raise Exception("RPC connection failed")

print("🧠 Base Intelligence Engine iniciado")
print("Connected to Base. Block:", web3.eth.block_number)

# ==============================
# CONFIG
# ==============================

ANALYSIS_INTERVAL = 1800  # 30 min
BASE_WHALE_THRESHOLD = 20  # ETH base threshold

last_checked_block = web3.eth.block_number
last_analysis_time = time.time()

tx_counter_30m = 0
eth_moved_30m = 0
largest_tx_30m = 0

# ==============================
# PUBLISH
# ==============================

def publish(message):
    try:
        r = requests.post(
            f"{PUBLISHER_URL}/post",
            json={"content": message},
            timeout=15
        )
        print("Publisher:", r.status_code)
    except Exception as e:
        print("Publish error:", e)

# ==============================
# WHALE DETECTION
# ==============================

def dynamic_whale_threshold():
    if tx_counter_30m > 3000:
        return 50
    elif tx_counter_30m > 1500:
        return 30
    else:
        return BASE_WHALE_THRESHOLD

def check_block(block_number):
    global tx_counter_30m, eth_moved_30m, largest_tx_30m

    block = web3.eth.get_block(block_number, full_transactions=True)
    tx_count = len(block.transactions)
    tx_counter_30m += tx_count

    for tx in block.transactions:
        eth_value = web3.from_wei(tx.value, "ether")
        eth_moved_30m += float(eth_value)

        if eth_value > largest_tx_30m:
            largest_tx_30m = float(eth_value)

        if eth_value >= dynamic_whale_threshold():
            message = f"""
🐋 Whale movement detected on Base

{eth_value:.2f} ETH moved
Block: {block_number}

Liquidity is rotating.

#Base #Whale
"""
            publish(message)

# ==============================
# PERIODIC PULSE
# ==============================

def activity_label(tx_count):
    if tx_count > 3000:
        return "🔥 High"
    elif tx_count > 1500:
        return "📈 Moderate"
    else:
        return "🧊 Low"

def periodic_update():
    global tx_counter_30m, eth_moved_30m, largest_tx_30m

    label = activity_label(tx_counter_30m)

    message = f"""
📊 Base Network Pulse

Last 30m:
• Transactions: {tx_counter_30m}
• ETH moved: {eth_moved_30m:.2f}
• Largest tx: {largest_tx_30m:.2f} ETH

Activity level: {label}

Time: {datetime.now(timezone.utc).strftime('%H:%M UTC')}

#Base
"""

    publish(message)

    # reset counters
    tx_counter_30m = 0
    eth_moved_30m = 0
    largest_tx_30m = 0

# ==============================
# MAIN LOOP
# ==============================

while True:
    try:
        current_block = web3.eth.block_number

        if current_block > last_checked_block:
            for b in range(last_checked_block + 1, current_block + 1):
                check_block(b)
            last_checked_block = current_block

        if time.time() - last_analysis_time > ANALYSIS_INTERVAL:
            periodic_update()
            last_analysis_time = time.time()

        time.sleep(10)

    except Exception as e:
        print("Main loop error:", e)
        time.sleep(15)
