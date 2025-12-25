import os
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count())


from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix

from src.config.tickers import TICKERS

FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/labels")


def load_data(ticker):
    X = pd.read_csv(
        FEATURE_DIR / f"{ticker}_features.csv",
        index_col=0
    )

    y = pd.read_csv(
        LABEL_DIR / f"{ticker}_labels.csv",
        index_col=0
    )["label"]

    # SAFE datetime conversion (handles "Date" bug)
    X.index = pd.to_datetime(X.index, errors="coerce")
    y.index = pd.to_datetime(y.index, errors="coerce")

    # Drop bad index rows (NaT)
    X = X[~X.index.isna()]
    y = y[~y.index.isna()]

    # Ensure sorted
    X = X.sort_index()
    y = y.sort_index()

    # Align explicitly
    common_idx = X.index.intersection(y.index)
    df = X.loc[common_idx].copy()
    df["label"] = y.loc[common_idx]

    return df


def time_split(df, train_ratio=0.7):
    split_idx = int(len(df) * train_ratio)

    train = df.iloc[:split_idx]
    val = df.iloc[split_idx:]

    X_train = train.drop(columns=["label"])
    y_train = train["label"]

    X_val = val.drop(columns=["label"])
    y_val = val["label"]

    return X_train, y_train, X_val, y_val



def main():
    for ticker in TICKERS:
        print(f"\n===== {ticker} =====")

        df = load_data(ticker)
        print("Data shape after alignment:", df.shape)

        X_train, y_train, X_val, y_val = time_split(df)

        model = HistGradientBoostingClassifier(
            max_depth=6,
            learning_rate=0.05,
            max_iter=300,
            random_state=42
        )

        model.fit(X_train, y_train)

        preds = model.predict(X_val)

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_val, preds))

        print("\nClassification Report:")
        print(classification_report(y_val, preds, digits=3))


if __name__ == "__main__":
    main()
