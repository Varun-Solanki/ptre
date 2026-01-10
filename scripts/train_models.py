import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV

from src.config.tickers import TICKERS
from src.models.generate_final_signal import (
    FEATURE_DIR,
    TREND_MODEL_DIR,
    MOM_MODEL_DIR
)


def train_trend_model(df):
    """
    Trend target:
      +1 bullish
       0 neutral
      -1 bearish
    """

    # label: future 10-day return
    fwd = df["ret_10d"].shift(-10)

    y = np.where(fwd > 0.01, 1,
        np.where(fwd < -0.01, -1, 0)
    )

    X = df.drop(columns=["Date", "date"], errors="ignore").copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = HistGradientBoostingClassifier(max_depth=6, learning_rate=0.08)

    model.fit(X_train, y_train)

    # probability calibration
    calibrated = CalibratedClassifierCV(model, cv=3)
    calibrated.fit(X_train, y_train)

    return calibrated


def train_momentum_model(df):
    """
    Momentum target:
       +1 short-term up
       -1 short-term down
    """

    fwd = df["ret_5d"].shift(-5)

    y = np.where(fwd > 0.005, 1, -1)

    X = df.drop(columns=["Date", "date"], errors="ignore").copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.1)

    model.fit(X_train, y_train)

    calibrated = CalibratedClassifierCV(model, cv=3)
    calibrated.fit(X_train, y_train)

    return calibrated


def process_ticker(ticker):

    ticker = ticker.upper()
    print(f"\n📈 Training: {ticker}")

    feature_file = FEATURE_DIR / f"{ticker}_features.csv"

    if not feature_file.exists():
        print("   ⚠ Feature file missing—run update_features first")
        return

    df = pd.read_csv(feature_file)

    if len(df) < 500:
        print("   ⚠ Too little data, skipping")
        return

    # ==========================
    # Train Trend
    # ==========================
    trend_model = train_trend_model(df)
    TREND_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(trend_model, TREND_MODEL_DIR / f"{ticker}_trend.pkl")
    print("   ✔ Trend model saved")

    # ==========================
    # Train Momentum
    # ==========================
    mom_model = train_momentum_model(df)
    MOM_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(mom_model, MOM_MODEL_DIR / f"{ticker}_momentum.pkl")
    print("   ✔ Momentum model saved")


def main():

    print("\n===== PTRE MODEL RETRAIN PIPELINE =====")

    for t in TICKERS:
        try:
            process_ticker(t)
        except Exception as e:
            print(f"   ❌ {t}: {e}")

    print("\n===== DONE =====")


if __name__ == "__main__":
    main()
