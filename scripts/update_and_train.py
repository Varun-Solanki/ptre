"""
PTRE Daily Pipeline Runner

This script will later:
1) update price history
2) rebuild features
3) retrain models

Right now it only prints structure to verify execution.
"""
import sys
from pathlib import Path
import yfinance as yf
import pandas as pd
from pathlib import Path

RAW_PRICE_DIR = Path("data/raw/prices")
RAW_PRICE_DIR.mkdir(parents=True, exist_ok=True)


def update_price_history(ticker, new_prices: pd.DataFrame):
    """
    Appends only new dates to stored price history CSV.
    Creates the file if missing.
    """

    path = RAW_PRICE_DIR / f"{ticker}_prices.csv"

    if path.exists():
        existing = pd.read_csv(path, parse_dates=["Date"])
        merged = pd.concat([existing, new_prices], ignore_index=True)

        # drop duplicate dates
        merged = merged.drop_duplicates(subset=["Date"]).sort_values("Date")
    else:
        merged = new_prices

    merged.to_csv(path, index=False)

    print(f" Saved {len(merged)} rows for {ticker}")


def fetch_latest_prices(ticker, lookback_days=30):
    """
    Download recent prices only (not whole history)
    """
    df = yf.download(
        ticker,
        period=f"{lookback_days}d",
        interval="1d",
        progress=False
    )

    if df.empty:
        print(f"⚠ No new price data for {ticker}")
        return None

    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index.name = "Date"
    df.reset_index(inplace=True)

    return df


# add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


from src.config.tickers import TICKERS


def run_daily_pipeline():
    print("\n===== PTRE DAILY PIPELINE START =====\n")

    for t in TICKERS:
        print(f"\n Updating {t}")

        prices = fetch_latest_prices(t)

        if prices is None:
            continue

        # print(prices.tail(2))   # TEMP sanity check
        update_price_history(t, prices)
    print("\n===== PTRE PIPELINE SKELETON OK =====\n")


if __name__ == "__main__":
    run_daily_pipeline()
