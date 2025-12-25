"""
PTRE - Data Cleaning Script

Cleans raw OHLCV data:
- Standardizes column names
- Ensures datetime index
- Handles missing values
- Saves cleaned data to processed directory
"""

from pathlib import Path
import pandas as pd

from src.config.tickers import TICKERS


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


COLUMN_MAP = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
}


def clean_stock(ticker: str):
    # Load raw data
    df = pd.read_csv(
        RAW_DIR / f"{ticker}.csv",
        index_col=0,
        parse_dates=True
    )

    # Sort index just in case
    df = df.sort_index()

    # Rename columns
    df = df.rename(columns=COLUMN_MAP)

    # Keep only required columns
    df = df[list(COLUMN_MAP.values())]

    # -----------------------------
    # Convert columns to numeric (CRITICAL)
    # -----------------------------
    for col in ["open", "high", "low", "close", "adj_close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle missing values
    price_cols = ["open", "high", "low", "close", "adj_close"]
    df[price_cols] = df[price_cols].ffill()

    df["volume"] = df["volume"].fillna(0)

    # Drop rows that are still missing (very rare edge case)
    df = df.dropna()

    return df


def main():
    print("Starting data cleaning...\n")

    for ticker in TICKERS:
        print(f"Cleaning {ticker}...")

        df_clean = clean_stock(ticker)

        output_path = PROCESSED_DIR / f"{ticker}_clean.csv"
        df_clean.to_csv(output_path)

        print(f"Saved → {output_path}")
        print(f"Rows: {len(df_clean)}\n")

    print("Data cleaning completed.")


if __name__ == "__main__":
    main()
