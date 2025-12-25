from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss

from src.config.tickers import TICKERS

# -----------------------------
# Paths
# -----------------------------
FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/momentum_labels")

# -----------------------------
# Momentum features (same as training)
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
        index_col=0
    )

    y = pd.read_csv(
        LABEL_DIR / f"{ticker}_momentum_labels.csv",
        index_col=0
    )["momentum_label"]

    # Force clean datetime index
    X.index = pd.to_datetime(X.index, errors="coerce")
    y.index = pd.to_datetime(y.index, errors="coerce")

    X = X[~X.index.isna()]
    y = y[~y.index.isna()]

    X = X.sort_index()
    y = y.sort_index()

    X = X[MOMENTUM_FEATURES]

    df = X.join(y.rename("label"), how="inner")
    df = df.dropna()

    return df


# -----------------------------
# Main calibration loop
# -----------------------------
def main():
    print("\n=== CALIBRATING MOMENTUM MODEL PROBABILITIES ===\n")

    for ticker in TICKERS:
        print(f"\n=== Calibration test: {ticker} ===")

        df = load_data(ticker)

        if len(df) < 500:
            print("Not enough data, skipping.")
            continue

        # -----------------------------
        # Time-based split
        # -----------------------------
        n = len(df)
        train_end = int(n * 0.6)
        calib_end = int(n * 0.8)

        train = df.iloc[:train_end]
        calib = df.iloc[train_end:calib_end]
        test = df.iloc[calib_end:]

        X_train = train.drop(columns="label")
        y_train = train["label"]

        X_calib = calib.drop(columns="label")
        y_calib = calib["label"]

        X_test = test.drop(columns="label")
        y_test = test["label"]

        # -----------------------------
        # Base momentum model
        # -----------------------------
        base_model = HistGradientBoostingClassifier(
            max_depth=5,
            learning_rate=0.05,
            max_iter=300,
            random_state=42
        )

        base_model.fit(X_train, y_train)

        # -----------------------------
        # Uncalibrated probabilities
        # -----------------------------
        uncal_probs = base_model.predict_proba(X_test)[:, 1]
        y_true = (y_test == 1).astype(int)

        brier_before = brier_score_loss(y_true, uncal_probs)

        # -----------------------------
        # Calibration (Isotonic)
        # -----------------------------
        calibrated_model = CalibratedClassifierCV(
            estimator=HistGradientBoostingClassifier(
                max_depth=5,
                learning_rate=0.05,
                max_iter=300,
                random_state=42
            ),
            method="isotonic",
            cv=3
        )

        calibrated_model.fit(
            pd.concat([X_train, X_calib]),
            pd.concat([y_train, y_calib])
        )

        
        cal_probs = calibrated_model.predict_proba(X_test)[:, 1]
        brier_after = brier_score_loss(y_true, cal_probs)

        # -----------------------------
        # Results
        # -----------------------------
        print(f"Brier score before calibration: {brier_before:.4f}")
        print(f"Brier score after  calibration: {brier_after:.4f}")

    print("\nMomentum probability calibration completed.")


if __name__ == "__main__":
    main()
