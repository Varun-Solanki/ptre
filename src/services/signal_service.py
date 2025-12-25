from datetime import datetime
from src.models.generate_final_signal import generate_signal as model_generate_signal
from src.utils.market_data import load_price_series, calculate_volatility


def generate_signal(ticker: str):
    ticker = ticker.upper()

    # 1️ Call ML layer
    result = model_generate_signal(ticker)

    # 2️ Load prices
    try:
        prices = load_price_series(ticker, period="1Y")
    except FileNotFoundError:
        prices = []

    # 3️ Volatility (API-level risk)
    vol = calculate_volatility(prices)

    if vol is None:
        vol_label = "Unknown"
    elif vol < 0.20:
        vol_label = "Low"
    elif vol < 0.35:
        vol_label = "Moderate"
    else:
        vol_label = "High"

    # 4️ Final API response
    return {
        "ticker": ticker,
        "timestamp": datetime.utcnow().isoformat(),

        "final_signal": result["signal"],
        "final_confidence": result["confidence"],

        "agreement": result["components"]["momentum"]["agreement"],

        "trend": {
            "direction": "Bullish"
            if result["components"]["trend"]["direction"] == 1
            else "Bearish",
            "confidence": result["components"]["trend"]["confidence"]
        },

        "momentum": {
            "direction": "Bullish"
            if result["components"]["momentum"]["direction"] == 1
            else "Bearish",
            "confidence": result["components"]["momentum"]["confidence"],
            "horizon_days": 7
        },

        "risk": {
            "volatility": vol_label,
            "volatility_value": vol,
            "risk_score": int(result["confidence"])
        },

        "price_chart": {
            "period": "1Y",
            "prices": prices
        }
    }
