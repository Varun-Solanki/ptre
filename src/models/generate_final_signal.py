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


from datetime import datetime, timedelta
import yfinance as yf
from src.features.build_features import build_features

# ... (existing imports)

def get_inference_features(ticker):
    """
    Fetches LIVE data and generates features WITHOUT shifting.
    This ensures we use Today's Close to predict Tomorrow's Move.
    """
    # 1. Fetch enough history for rolling windows (100 days is safe)
    end_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    df = yf.download(
        ticker,
        period="6mo", # ample buffer
        interval="1d",
        progress=False
    )

    if df.empty:
        raise ValueError(f"No live data found for {ticker}")

    # 2. Clean
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]

    # 3. Build features (SHIFT=FALSE for inference!)
    features = build_features(df, shift=False)

    # 4. Return last row (Today)
    return features.iloc[[-1]]


def generate_signal(ticker):

    ticker = ticker.upper()

    if ticker not in TICKERS:
        raise FileNotFoundError(f"Ticker {ticker} not supported.")

    # feature_path = FEATURE_DIR / f"{ticker}_features.csv" # DEPRECATED
    trend_path = TREND_MODEL_DIR / f"{ticker}_trend.pkl"
    mom_path = MOM_MODEL_DIR / f"{ticker}_momentum.pkl"

    if not trend_path.exists():
        raise FileNotFoundError(f"Missing trend model for {ticker}")
    if not mom_path.exists():
        raise FileNotFoundError(f"Missing momentum model for {ticker}")

    # -----------------------------
    # Load latest features (LIVE)
    # -----------------------------
    # df = pd.read_csv(feature_path)  <-- OLD LAGGY WAY
    # ...
    # X = df.iloc[[-1]] 
    
    try:
        X = get_inference_features(ticker)
    except Exception as e:
        raise ValueError(f"Feature generation failed: {e}")
        
    # Ensure numeric
    X = X.select_dtypes(include=[np.number])


    # -----------------------------
    # Load models
    # -----------------------------
    trend_model = joblib.load(trend_path)
    mom_model = joblib.load(mom_path)

    # -----------------------------
    # Enforce training feature schema
    # -----------------------------
    trend_features = list(trend_model.feature_names_in_)
    mom_features = list(mom_model.feature_names_in_)

    X_trend = X[trend_features]
    X_mom = X[mom_features]

    # -----------------------------
    # TREND inference
    # -----------------------------
    trend_probs = trend_model.predict_proba(X_trend)[0]
    trend_idx = np.argmax(trend_probs)
    trend_conf = trend_probs[trend_idx]
    trend_dir = trend_model.classes_[trend_idx]

    # -----------------------------
    # MOMENTUM inference
    # -----------------------------
    mom_probs = mom_model.predict_proba(X_mom)[0]
    mom_idx = np.argmax(mom_probs)
    mom_conf = mom_probs[mom_idx]
    mom_dir = mom_model.classes_[mom_idx]

    # -----------------------------
    # Soft gating
    # -----------------------------
    raw_conf = BASE_WEIGHT * trend_conf + MOM_WEIGHT * mom_conf

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
