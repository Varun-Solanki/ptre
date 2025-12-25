from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

from src.config.tickers import TICKERS

# ------------------------
# PATHS
# ------------------------
FEATURE_DIR = Path("data/processed/features")
TREND_LABEL_DIR = Path("data/processed/labels")
MOM_LABEL_DIR = Path("data/processed/momentum_labels")

TREND_MODEL_DIR = Path("src/models/trend")
MOM_MODEL_DIR = Path("src/models/momentum")

TREND_MODEL_DIR.mkdir(parents=True, exist_ok=True)
MOM_MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------
# HELPERS
# ------------------------

def load_and_align(feature_path, label_path, label_col):
    X = pd.read_csv(feature_path, index_col=0)
    y = pd.read_csv(label_path, index_col=0)

    # print("\n[DEBUG] Loaded:")
    # print("Features rows:", len(X))
    # print("Labels rows:", len(y))
    # print("Feature index dtype:", X.index.dtype)
    # print("Label index dtype:", y.index.dtype)

    # FORCE datetime (CRITICAL)
    X.index = pd.to_datetime(X.index, errors="coerce")
    y.index = pd.to_datetime(y.index, errors="coerce")

    common_idx = X.index.intersection(y.index)
    print("Common index rows:", len(common_idx))

    df = X.loc[common_idx].copy()
    df[label_col] = y.loc[common_idx][label_col]

    print("Rows before dropna:", len(df))

    df = df.dropna()

    print("Rows after dropna:", len(df))

    df = df.sort_index()

    return df


def train_and_calibrate(X_train, y_train, X_calib, y_calib):
    base_model = HistGradientBoostingClassifier(
        max_depth=6,
        learning_rate=0.05,
        max_iter=300,
        random_state=42
    )

    # 1️ Train base model
    base_model.fit(X_train, y_train)

    # 2️ Calibrate using a proper CV object
    calibrated = CalibratedClassifierCV(
        estimator=base_model,
        method="isotonic",
        cv=3   # <-- THIS replaces "prefit"
    )

    # IMPORTANT: fit on CALIBRATION data
    calibrated.fit(X_calib, y_calib)

    return calibrated



# ------------------------
# MAIN
# ------------------------
def main():
    print("\n=== SAVING FINAL CALIBRATED MODELS ===\n")

    for ticker in TICKERS:
        print(f"\n===== {ticker} =====")

        # ==============================
        # TREND MODEL
        # ==============================
        trend_df = load_and_align(
            FEATURE_DIR / f"{ticker}_features.csv",
            TREND_LABEL_DIR / f"{ticker}_labels.csv",
            "label"
        )

        n = len(trend_df)

        train_end = int(n * 0.7)
        calib_end = int(n * 0.85)

        train = trend_df.iloc[:train_end]
        calib = trend_df.iloc[train_end:calib_end]

        if len(train) == 0 or len(calib) == 0:
            print("Not enough data after split, skipping.")
            continue

        trend_model = train_and_calibrate(
            train.drop(columns="label"),
            train["label"],
            calib.drop(columns="label"),
            calib["label"]
        )

        trend_path = TREND_MODEL_DIR / f"{ticker}_trend.pkl"
        joblib.dump(trend_model, trend_path)

        print(f"✔ Trend model saved → {trend_path}")

        # ==============================
        # MOMENTUM MODEL
        # ==============================
        mom_df = load_and_align(
            FEATURE_DIR / f"{ticker}_features.csv",
            MOM_LABEL_DIR / f"{ticker}_momentum_labels.csv",
            "momentum_label"
        )

        n = len(mom_df)

        train_end = int(n * 0.7)
        calib_end = int(n * 0.85)

        train = mom_df.iloc[:train_end]
        calib = mom_df.iloc[train_end:calib_end]

        if len(train) == 0 or len(calib) == 0:
            print("Not enough data after split, skipping.")
            continue

        mom_model = train_and_calibrate(
            train.drop(columns="momentum_label"),
            train["momentum_label"],
            calib.drop(columns="momentum_label"),
            calib["momentum_label"]
        )

        mom_path = MOM_MODEL_DIR / f"{ticker}_momentum.pkl"
        joblib.dump(mom_model, mom_path)

        print(f"✔ Momentum model saved → {mom_path}")

    print("\n=== ALL MODELS SAVED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
