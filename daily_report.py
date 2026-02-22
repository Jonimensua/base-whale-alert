def run_daily_report():
    print("Running daily report...")

    latest = get_latest_block()
    start_block = latest - 300

    whale_count = 0
    contract_count = 0
    largest_tx = 0

    for block_number in range(start_block, latest + 1):
        block = get_block(block_number)

        for tx in block["transactions"]:
            value = int(tx["value"], 16) / (10**18)

            if value >= WHALE_THRESHOLD:
                whale_count += 1
                if value > largest_tx:
                    largest_tx = value

            if tx["to"] is None:
                gas = int(tx["gas"], 16)
                if gas >= GAS_THRESHOLD:
                    contract_count += 1

    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    message = (
        "BASE NETWORK — TOP ACTIVITY (24H)\n\n"
        f"🔥 Largest Whale: {round(largest_tx,4)} ETH\n"
        f"🚀 High Gas Deployments: {contract_count}\n"
        f"💧 Whale Transactions: {whale_count}\n\n"
        "Base remains active.\n\n"
        "—\n"
        "Automated On-Chain Intelligence"
    )

    print(message)
    enviar_telegram(message)
    from datetime import datetime, timedelta, timezone
    def wait_until_midnight_utc():
        while True:
            now = datetime.now(timezone.utc)
            tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_until_midnight = (tomorrow - now).total_seconds()
            time.sleep(seconds_until_midnight)
            run_daily_report()
            if __name__ == "__main__":
                print("Daily Report Service Started (UTC schedule)")
                wait_until_midnight_utc()
