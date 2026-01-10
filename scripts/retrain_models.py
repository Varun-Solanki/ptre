import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

from src.config.tickers import TICKERS
from src.models.generate_final_signal import TREND_MODEL_DIR, MOM_MODEL_DIR, FEATURE_DIR


def retrain_for_ticker(ticker: str):

    print(f"\nRetraining models for {ticker}")

    df = pd.read_csv(FEATURE_DIR / f"{ticker}_features.csv")

    df = df.dropna()

    X = df.drop(columns=["target_trend", "target_momentum", "Date"], errors="ignore")

    y_trend = df["target_trend"]
    y_mom = df["target_momentum"]

    # === Trend Model ===
    trend_base = HistGradientBoostingClassifier(max_depth=6)

    trend_model = CalibratedClassifierCV(trend_base, cv=3)
    trend_model.fit(X, y_trend)

    joblib.dump(trend_model, TREND_MODEL_DIR / f"{ticker}_trend.pkl")

    # === Momentum Model ===
    mom_base = HistGradientBoostingClassifier(max_depth=5)

    mom_model = CalibratedClassifierCV(mom_base, cv=3)
    mom_model.fit(X, y_mom)

    joblib.dump(mom_model, MOM_MODEL_DIR / f"{ticker}_momentum.pkl")

    print("   ✔ retrained & saved")


def main():
    for t in TICKERS:
        try:
            retrain_for_ticker(t)
        except Exception as e:
            print(f"   ❌ {t}: {e}")


if __name__ == "__main__":
    main()
