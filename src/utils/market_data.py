import yfinance as yf
from datetime import datetime

def load_price_series(ticker: str, period: str = "6M"):
    """
    Returns list of {date, close} dicts for frontend charts
    """

    ticker = ticker.upper()

    # Map frontend periods to yfinance periods
    PERIOD_MAP = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y"
    }

    yf_period = PERIOD_MAP.get(period, "6mo")

    df = yf.download(
        ticker,
        period=yf_period,
        interval="1d",
        progress=False
    )

    if df.empty:
        raise FileNotFoundError(f"No price data for {ticker}")

    prices = []
    for idx, row in df.iterrows():
        prices.append({
            "date": idx.strftime("%Y-%m-%d"),
            "close": round(float(row["Close"]), 2)
        })

    return prices

import numpy as np

def calculate_volatility(prices):
    """
    prices: list of {date, close}
    returns annualized volatility
    """

    if len(prices) < 20:
        return None

    closes = np.array([p["close"] for p in prices])
    log_returns = np.diff(np.log(closes))

    daily_vol = np.std(log_returns)
    annual_vol = daily_vol * np.sqrt(252)

    return round(float(annual_vol), 4)

