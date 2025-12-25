from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from src.config.tickers import TICKERS

#ABSOLUTE PROJECT ROOT (CRITICAL FIX)
BASE_DIR = Path(__file__).resolve().parents[2]

FEATURE_DIR = BASE_DIR / "data" / "processed" / "features"
TREND_MODEL_DIR = BASE_DIR / "src" / "models" / "trend"
MOM_MODEL_DIR = BASE_DIR / "src" / "models" / "momentum"

# -----------------------------
# Soft-gating constants (LOCKED)
# -----------------------------
BASE_WEIGHT = 0.7
MOM_WEIGHT = 0.3
DISAGREE_PENALTY = 0.15

MIN_CONF = 0.35
MAX_CONF = 0.85


def load_latest_features(ticker):
    df = pd.read_csv(
        FEATURE_DIR / f"{ticker}_features.csv",
        index_col=0
    )
    return df.iloc[[-1]]  # latest row only


def generate_signal(ticker):

    # print("FEATURE DIR:", FEATURE_DIR)
    # print("TREND MODEL PATH:", TREND_MODEL_DIR / f"{ticker}_trend.pkl")
    # print("MOM MODEL PATH:", MOM_MODEL_DIR / f"{ticker}_momentum.pkl")
    ticker = ticker.upper()

    if ticker not in TICKERS:
        raise FileNotFoundError(f"Ticker {ticker} not supported.")
    
    feature_path = FEATURE_DIR / f"{ticker}_features.csv"
    trend_path = TREND_MODEL_DIR / f"{ticker}_trend.pkl"
    mom_path = MOM_MODEL_DIR / f"{ticker}_momentum.pkl"

    if not feature_path.exists():
        raise FileNotFoundError(f"Missing features for {ticker}")

    if not trend_path.exists():
        raise FileNotFoundError(f"Missing trend model for {ticker}")

    if not mom_path.exists():
        raise FileNotFoundError(f"Missing momentum model for {ticker}")
    
    X = load_latest_features(ticker)


    # -----------------------------
    # Load models
    # -----------------------------
    trend_model = joblib.load(TREND_MODEL_DIR / f"{ticker}_trend.pkl")
    mom_model = joblib.load(MOM_MODEL_DIR / f"{ticker}_momentum.pkl")

    # -----------------------------
    # TREND inference
    # -----------------------------
    trend_probs = trend_model.predict_proba(X)[0]
    trend_idx = np.argmax(trend_probs)
    trend_conf = trend_probs[trend_idx]

    trend_classes = trend_model.classes_
    trend_dir = trend_classes[trend_idx]  # -1, 0, +1

    # -----------------------------
    # MOMENTUM inference
    # -----------------------------
    mom_probs = mom_model.predict_proba(X)[0]
    mom_idx = np.argmax(mom_probs)
    mom_conf = mom_probs[mom_idx]

    mom_classes = mom_model.classes_
    mom_dir = mom_classes[mom_idx]  # -1, +1

    # -----------------------------
    # Soft gating
    # -----------------------------
    raw_conf = (
        BASE_WEIGHT * trend_conf +
        MOM_WEIGHT * mom_conf
    )

    if trend_dir != 0 and mom_dir != trend_dir:
        final_conf = raw_conf - DISAGREE_PENALTY
        agreement = False
    else:
        final_conf = raw_conf
        agreement = True

    final_conf = float(np.clip(final_conf, MIN_CONF, MAX_CONF))

    # -----------------------------
    # Final signal
    # -----------------------------
    if trend_dir == 1:
        signal = "Bullish"
    elif trend_dir == -1:
        signal = "Bearish"
    else:
        signal = "Neutral"

    return {
    "ticker": ticker,
    "signal": signal,
    "confidence": round(final_conf * 100, 2),
    "components": {
        "trend": {
            "direction": int(trend_dir),
            "confidence": round(float(trend_conf), 3)
        },
        "momentum": {
            "direction": int(mom_dir),
            "confidence": round(float(mom_conf), 3),
            "agreement": agreement
        }
    }
}



def main():
    print("\n=== FINAL PTRE SIGNALS ===\n")

    for ticker in TICKERS:
        try:
            output = generate_signal(ticker)
            print(output)
        except Exception as e:
            print(f"{ticker}: ERROR → {e}")


if __name__ == "__main__":
    main()
