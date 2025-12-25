from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

from src.config.tickers import TICKERS

FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/labels")

def load_data(ticker):
    X = pd.read_csv(FEATURE_DIR / f"{ticker}_features.csv", index_col=0)
    y = pd.read_csv(LABEL_DIR / f"{ticker}_labels.csv", index_col=0)["label"]

    common_idx = X.index.intersection(y.index)
    df = X.loc[common_idx].copy()
    df["label"] = y.loc[common_idx]

    return df.dropna()

def split_data(df):
    n = len(df)
    train_end = int(n * 0.5)
    calib_end = int(n * 0.7)

    train_df = df.iloc[:train_end]
    calib_df = df.iloc[train_end:calib_end]
    test_df  = df.iloc[calib_end:]

    return train_df, calib_df, test_df

def expected_calibration_error(probs, y_true, n_bins=10):
    confidences = probs.max(axis=1)
    predictions = probs.argmax(axis=1)

    correct = (predictions == y_true.values)

    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        mask = (confidences > bins[i]) & (confidences <= bins[i+1])
        if mask.sum() == 0:
            continue
        acc = correct[mask].mean()
        conf = confidences[mask].mean()
        ece += np.abs(acc - conf) * mask.mean()

    return ece

def main():
    ticker = "AAPL"  # start with one

    print(f"\n=== Calibration test: {ticker} ===")

    df = load_data(ticker)
    train_df, calib_df, test_df = split_data(df)

    base_model = HistGradientBoostingClassifier(
        max_depth=6,
        learning_rate=0.05,
        max_iter=300,
        random_state=42
    )

    base_model.fit(
        train_df.drop(columns="label"),
        train_df["label"]
    )

    raw_probs = base_model.predict_proba(
        test_df.drop(columns="label")
    )

    calibrated_model = CalibratedClassifierCV(
    estimator=base_model,
    method="sigmoid",
    cv=None
    )


    calibrated_model.fit(
        calib_df.drop(columns="label"),
        calib_df["label"]
    )

    calib_probs = calibrated_model.predict_proba(
        test_df.drop(columns="label")
    )

    ece_raw = expected_calibration_error(raw_probs, test_df["label"])
    ece_cal = expected_calibration_error(calib_probs, test_df["label"])

    print(f"ECE before calibration: {ece_raw:.4f}")
    print(f"ECE after  calibration: {ece_cal:.4f}")

if __name__ == "__main__":
    main()
