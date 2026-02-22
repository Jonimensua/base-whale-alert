    print("Contract + Liquidity Monitor iniciado")
    ultimo_bloque = get_latest_block()

    while True:
        try:
            time.sleep(10)
            bloque_actual = get_latest_block()

            if bloque_actual > ultimo_bloque:

                # Revisar nuevos bloques
                block_data = get_block(bloque_actual)

                for tx in block_data["transactions"]:

                    # 1️⃣ Detectar nuevo contrato
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

                    # 2️⃣ Detectar liquidez en contratos rastreados
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
            print("Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
