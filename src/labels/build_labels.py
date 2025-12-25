from pathlib import Path
import pandas as pd
import numpy as np

from src.config.tickers import TICKERS
from src.config.settings import PREDICTION_HORIZON


PROCESSED_DIR = Path("data/processed")
FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/labels")
LABEL_DIR.mkdir(parents=True, exist_ok=True)


def build_labels(df: pd.DataFrame) -> pd.DataFrame:
    labels = pd.DataFrame(index=df.index)

    # Future return (forward-looking)
    future_ret = df["adj_close"].shift(-PREDICTION_HORIZON) / df["adj_close"] - 1

    # Risk-adjusted return
    risk_adj_ret = future_ret / (df["vol_10d"] + 1e-6)

    labels["risk_adj_ret"] = risk_adj_ret

    # Label assignment
    labels["label"] = 0
    labels.loc[risk_adj_ret >= 0.75, "label"] = 1
    labels.loc[risk_adj_ret <= -0.75, "label"] = -1

    return labels


def main():
    print("Building labels...\n")

    for ticker in TICKERS:
        print(f"Processing {ticker}...")

        # Load clean price data (for future returns)
        price_df = pd.read_csv(
            PROCESSED_DIR / f"{ticker}_clean.csv",
            index_col=0,
            parse_dates=True
        )

        # Load feature data (for volatility)
        feature_df = pd.read_csv(
            FEATURE_DIR / f"{ticker}_features.csv",
            index_col=0,
            parse_dates=True
        )

        # Align indices (safety)
        df = price_df.join(feature_df[["vol_10d"]], how="inner")

        labels = build_labels(df)
        labels = labels.dropna()

        out_path = LABEL_DIR / f"{ticker}_labels.csv"
        labels.to_csv(out_path)

        print(f"Saved → {out_path}")
        print(labels["label"].value_counts(normalize=True), "\n")

    print("Labeling completed.")



if __name__ == "__main__":
    main()
