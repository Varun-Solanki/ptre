from pathlib import Path
from matplotlib import ticker
import pandas as pd
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix

from src.config.tickers import TICKERS

# -----------------------------
# Paths
# -----------------------------
FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/momentum_labels")

# -----------------------------
# Momentum feature set (FAST ONLY)
# -----------------------------
MOMENTUM_FEATURES = [
    "ret_1d",
    "ret_3d",
    "ret_5d",
    "roc_5d",
    "mom_slope_5d",

    "vol_ratio_5_20",
    "hl_vol_5d",

    "vol_weighted_momentum",
    "volume_zscore",
    "volume_surprise",

    "rsi_14"
]


# -----------------------------
# Data loading & alignment
# -----------------------------
def load_data(ticker: str) -> pd.DataFrame:
    X = pd.read_csv(
        FEATURE_DIR / f"{ticker}_features.csv",
        index_col=0,
        parse_dates=True
    )

    y = pd.read_csv(
        LABEL_DIR / f"{ticker}_momentum_labels.csv",
        index_col=0,
        parse_dates=True
    )["momentum_label"]

    # Select momentum features only
    X = X[MOMENTUM_FEATURES]

    # Force clean datetime indices
    X.index = pd.to_datetime(X.index, errors="coerce")
    y.index = pd.to_datetime(y.index, errors="coerce")

    # Drop invalid rows created by coercion
    X = X[~X.index.isna()]
    y = y[~y.index.isna()]

    # Sort (important for time split)
    X = X.sort_index()
    y = y.sort_index()

    # Align
    df = X.join(y.rename("label"), how="inner")


    print(f"{ticker} raw feature rows:", len(X))
    print(f"{ticker} raw label rows:", len(y))
    print(f"{ticker} common index rows:", len(df))


    print(f"{ticker} rows before dropna:", len(df))
    df = df.dropna()
    print(f"{ticker} rows after dropna:", len(df))


    return df


# -----------------------------
# Time-based split
# -----------------------------
def time_split(df: pd.DataFrame, train_ratio=0.7):
    split_idx = int(len(df) * train_ratio)

    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]

    X_train = train.drop(columns="label")
    y_train = train["label"]

    X_test = test.drop(columns="label")
    y_test = test["label"]

    return X_train, y_train, X_test, y_test


# -----------------------------
# Main training loop
# -----------------------------
def main():
    print("\n=== TRAINING MOMENTUM MODEL (7-day horizon) ===\n")

    for ticker in TICKERS:
        print(f"\n===== {ticker} =====")

        df = load_data(ticker)

        if len(df) < 250:
            print("Not enough data, skipping.")
            continue

        X_train, y_train, X_test, y_test = time_split(df)

        model = HistGradientBoostingClassifier(
            max_depth=5,
            learning_rate=0.05,
            max_iter=300,
            random_state=42
        )

        model.fit(X_train, y_train)

        preds = model.predict(X_test)

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, preds))

        print("\nClassification Report:")
        print(classification_report(y_test, preds, digits=3))

        pos_rate = (preds == 1).mean()
        print(f"Predicted +1 rate: {pos_rate:.2%}")

    print("\nMomentum model training completed.")


if __name__ == "__main__":
    main()
