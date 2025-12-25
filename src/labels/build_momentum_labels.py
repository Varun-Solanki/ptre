"""
PTRE – Momentum Labels (7-Day Horizon)

Binary momentum labels:
+1 → positive 7-day return
-1 → negative 7-day return
"""

from pathlib import Path
import pandas as pd
import numpy as np

from src.config.tickers import TICKERS

PROCESSED_DIR = Path("data/processed")
LABEL_DIR = Path("data/processed/momentum_labels")
LABEL_DIR.mkdir(parents=True, exist_ok=True)

HORIZON = 7


def build_momentum_labels(df: pd.DataFrame) -> pd.Series:
    price = df["adj_close"]

    future_return = price.shift(-HORIZON) / price - 1

    labels = np.where(
        future_return > 0, 1,
        np.where(future_return < 0, -1, np.nan)
    )

    labels = pd.Series(labels, index=df.index, name="momentum_label")

    # Drop NaNs caused by horizon shift or zero returns
    labels = labels.dropna()

    return labels


def main():
    print("Building momentum labels (7-day horizon)...\n")

    for ticker in TICKERS:
        print(f"Processing {ticker}...")

        df = pd.read_csv(
            PROCESSED_DIR / f"{ticker}_clean.csv",
            index_col=0,
            parse_dates=True
        )

        labels = build_momentum_labels(df)

        out_path = LABEL_DIR / f"{ticker}_momentum_labels.csv"
        labels.to_csv(out_path)

        print(f"Saved → {out_path}")
        print(labels.value_counts(normalize=True).rename("proportion"), "\n")

    print("Momentum labeling completed.")


if __name__ == "__main__":
    main()
