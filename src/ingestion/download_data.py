"""
PTRE - Data Ingestion Script

Downloads historical daily OHLCV data for the configured
US stock universe using Yahoo Finance.

Raw data is saved as CSV and must NEVER be modified.
"""

from pathlib import Path
import yfinance as yf

from src.config.tickers import TICKERS
from src.config.settings import START_DATE, END_DATE


# =====================
# Paths
# =====================

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# =====================
# Functions
# =====================

def download_stock_data(ticker: str):
    """
    Download historical data for a single stock.
    """
    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        progress=False
    )
    return df


def save_to_csv(df, ticker: str):
    """
    Save dataframe to CSV in raw data directory.
    """
    file_path = RAW_DATA_DIR / f"{ticker}.csv"
    df.to_csv(file_path)
    print(f"Saved {ticker} → {file_path}")


# =====================
# Main execution
# =====================

def main():
    print("Starting data download...\n")

    for ticker in TICKERS:
        print(f"Downloading {ticker}...")
        df = download_stock_data(ticker)

        if df.empty:
            print(f"⚠️  Warning: No data returned for {ticker}\n")
            continue

        save_to_csv(df, ticker)
        print()

    print("Data download completed.")


if __name__ == "__main__":
    main()
