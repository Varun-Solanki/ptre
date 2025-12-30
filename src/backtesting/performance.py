def pretty_print(results: dict):
    print("\n===== PTRE BACKTEST RESULTS =====\n")
    for k, v in results.items():
        print(f"{k:18} : {v}")
