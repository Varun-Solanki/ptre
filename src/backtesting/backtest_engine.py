import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import joblib

from src.models.generate_final_signal import (
    TREND_MODEL_DIR,
    MOM_MODEL_DIR
)
from src.features.build_features import build_features


class Backtester:

    def __init__(self, ticker, start="2018-01-01", end=None, cost=0.001):
        self.ticker = ticker
        self.start = start
        self.end = end or datetime.today().strftime("%Y-%m-%d")

        self.cost = cost  # slippage + brokerage

        self.data = None
        self.raw_data = None  # Store raw OHLCV for feature computation

        # load models once
        self.trend_model = joblib.load(TREND_MODEL_DIR / f"{ticker}_trend.pkl")
        self.mom_model = joblib.load(MOM_MODEL_DIR / f"{ticker}_momentum.pkl")

    # ============================
    # load price data
    # ============================
    def load_data(self):
        df = yf.download(self.ticker, start=self.start, end=self.end)

        if df.empty:
            raise ValueError("No price data loaded")

        # Store raw data for feature computation
        self.raw_data = df.copy()
        
        # Clean column names for raw data (handle MultiIndex from yfinance)
        if isinstance(self.raw_data.columns, pd.MultiIndex):
            self.raw_data.columns = [c[0] for c in self.raw_data.columns]
        self.raw_data.columns = [str(c).lower().replace(" ", "_") for c in self.raw_data.columns]
        
        # Add adj_close if not present
        if "adj_close" not in self.raw_data.columns:
            self.raw_data["adj_close"] = self.raw_data["close"]

        # Prepare price data for backtest
        df = df[["Open", "Close"]]
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df["Return"] = df["Close"].pct_change()

        df.index = pd.to_datetime(df.index).tz_localize(None)

        self.data = df

    # ============================
    # generate historical signals (ON-THE-FLY FEATURES)
    # ============================
    def generate_signals(self):
        
        # Build features dynamically from downloaded price data
        df_feat = build_features(self.raw_data, shift=True)
        
        # Set index properly
        df_feat.index = pd.to_datetime(df_feat.index).tz_localize(None)
        
        # Drop rows with NaN from rolling windows
        df_feat = df_feat.dropna()

        # -------------------------------
        # align with price data
        # -------------------------------
        self.data.index = pd.to_datetime(self.data.index).tz_localize(None)

        df_feat = df_feat.loc[self.data.index.intersection(df_feat.index)]

        print(f"Price rows   : {len(self.data)}")
        print(f"Feature rows : {len(df_feat)}")
        print(f"Overlap rows : {len(df_feat)}")

        if len(df_feat) == 0:
            raise ValueError("No aligned feature rows after feature computation.")

        # Select only numeric features
        X = df_feat.select_dtypes(include=[np.number])
        
        # Enforce training feature schema (models expect specific columns)
        trend_features = list(self.trend_model.feature_names_in_)
        mom_features = list(self.mom_model.feature_names_in_)
        
        X_trend = X[trend_features]
        X_mom = X[mom_features]

        # ---- model inference ----
        trend_probs = self.trend_model.predict_proba(X_trend)
        mom_probs = self.mom_model.predict_proba(X_mom)

        trend_dir = self.trend_model.classes_[trend_probs.argmax(axis=1)]
        mom_dir = self.mom_model.classes_[mom_probs.argmax(axis=1)]

        trend_conf = trend_probs.max(axis=1)
        mom_conf = mom_probs.max(axis=1)

        raw_conf = 0.7 * trend_conf + 0.3 * mom_conf

        disagree = (trend_dir != 0) & (trend_dir != mom_dir)

        final_conf = raw_conf - 0.15 * disagree
        final_conf = np.clip(final_conf, 0.35, 0.85)

        numeric_signal = []
        for t in trend_dir:
            if t == 1:
                numeric_signal.append(1)
            elif t == -1:
                numeric_signal.append(-1)
            else:
                numeric_signal.append(0)

        self.data["Signal"] = 0
        self.data.loc[df_feat.index, "Signal"] = numeric_signal
        self.data.loc[df_feat.index, "Confidence"] = final_conf

    # ============================
    # run backtest
    # ============================
    def run_backtest(self):

        self.data["Position"] = self.data["Signal"].shift(1).fillna(0)

        self.data["Strategy"] = self.data["Position"] * self.data["Return"]

        self.data["Trade"] = self.data["Position"].diff().abs()
        self.data["Strategy"] -= self.data["Trade"] * self.cost

        self.data["Equity"] = (1 + self.data["Strategy"]).cumprod()

    # ============================
    # performance metrics
    # ============================
    def results(self):
        df = self.data.copy()

        total_return = df["Equity"].iloc[-1] - 1
        cagr = (df["Equity"].iloc[-1]) ** (252 / len(df)) - 1

        std = df["Strategy"].std()
        sharpe = 0 if std == 0 or np.isnan(std) else np.sqrt(252) * df["Strategy"].mean() / std

        equity = df["Equity"].replace(0, np.nan)
        max_dd = ((equity.cummax() - equity) / equity.cummax()).max()

        return {
            "ticker": self.ticker,
            "period": f"{self.start} → {self.end}",
            "total_return_%": round(total_return * 100, 2),
            "CAGR_%": round(cagr * 100, 2),
            "Sharpe": round(sharpe, 2),
            "Max_Drawdown_%": round(max_dd * 100, 2),
            "num_trades": int(df["Trade"].sum() / 2)
        }
