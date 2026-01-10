import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path

from src.config.tickers import TICKERS
from src.features.build_features import build_features

FEATURE_DIR = Path("data/processed/features")


def update_features_for_ticker(ticker: str):

    ticker = ticker.upper()
    feature_file = FEATURE_DIR / f"{ticker}_features.csv"

    print(f"\n🔄 Updating features for {ticker}")

    # -----------------------------
    # Load existing features if present
    # -----------------------------
    existing = None
    last_date = None

    if feature_file.exists():
        existing = pd.read_csv(feature_file)

        # Case 1 — Date column exists
        if "Date" in existing.columns:
            existing["Date"] = pd.to_datetime(existing["Date"], errors="coerce")
            last_date = existing["Date"].max()

        # Case 2 — already indexed
        else:
            existing.index = pd.to_datetime(existing.index, errors="coerce")
            last_date = existing.index.max()

        print(f"   Last feature date: {last_date.date() if pd.notna(last_date) else 'UNKNOWN'}")

    # -----------------------------
    # Decide start date for fetching prices
    # -----------------------------
    if last_date is None or pd.isna(last_date):
        start = "2015-01-01"
    else:
        start = last_date.strftime("%Y-%m-%d")

    from datetime import timedelta

    # -----------------------------
    # Download only missing price data
    # -----------------------------
    df = yf.download(
        ticker,
        start=start,
        end=(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        interval="1d",
        progress=False
    )

    if df.empty:
        print("   No new price data. Skipping.")
        return

    # -----------------------------
    # FIX: flatten MultiIndex columns from Yahoo
    # -----------------------------
    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

    # Ensure adjusted close exists
    if "adj_close" not in df.columns:
        if "close" in df.columns:
            df["adj_close"] = df["close"]
        else:
            raise ValueError("No close or adj_close price available for feature building")

    # -----------------------------
    # FIX: Restore Date index for build_features
    # -----------------------------
    # 'date' column should exist from reset_index() earlier, lowercased
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    else:
        # fallback if somehow date is missing or named differently
        # check for 'index' if reset didn't rename it? 
        # But we did df.columns = [str(c).lower()...]
        # Let's hope 'date' is there.
        pass

    # -----------------------------
    # Build features using YOUR pipeline
    # -----------------------------
    new_features = build_features(df, shift=True)

    # normalize Date column
    if "Date" in new_features.columns:
        new_features["Date"] = pd.to_datetime(new_features["Date"])
    else:
        new_features = new_features.reset_index().rename(columns={"index": "Date"})

    # -----------------------------
    # Merge with existing features
    # -----------------------------
    if existing is not None:
        combined = pd.concat([existing, new_features], axis=0)
        combined = combined.drop_duplicates(subset=["Date"]).sort_values("Date")
    else:
        combined = new_features

    # -----------------------------
    # Save
    # -----------------------------
    FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(feature_file, index=False)

    print(f"   ✔ Saved {len(combined)} total rows")


def main():
    print("\n===== PTRE FEATURE UPDATE PIPELINE =====")

    for t in TICKERS:
        try:
            update_features_for_ticker(t)
        except Exception as e:
            print(f"   ❌ {t}: {e}")

    print("\n===== DONE =====")


if __name__ == "__main__":
    main()
