import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

from src.models.generate_final_signal import generate_signal


class Backtester:

    def __init__(self, ticker, start="2018-01-01", end=None, cost=0.001):
        self.ticker = ticker
        self.start = start
        self.end = end or datetime.today().strftime("%Y-%m-%d")

        self.cost = cost  # 0.1% per trade (slippage + brokerage)

        self.data = None
        self.signals = None
        self.trades = []
        self.equity_curve = None

    def load_data(self):
        df = yf.download(self.ticker, start=self.start, end=self.end)

        if df.empty:
            raise ValueError("No price data loaded")

        df = df[["Open", "Close"]]
        df["Return"] = df["Close"].pct_change()

        self.data = df

    def generate_signals(self):
        """
        Calls YOUR PTRE signal engine daily
        """

        signals = []

        for date in self.data.index:
            try:
                result = generate_signal(self.ticker)
                sig = result["signal"]
            except Exception:
                sig = "Neutral"

            if sig == "Bullish":
                signals.append(1)
            elif sig == "Bearish":
                signals.append(-1)
            else:
                signals.append(0)

        self.data["Signal"] = signals

    def run_backtest(self):
        """
        Executes trades based on signal shifting by 1 day
        """

        self.data["Position"] = self.data["Signal"].shift(1).fillna(0)

        # Strategy returns
        self.data["Strategy"] = self.data["Position"] * self.data["Return"]

        # Transaction costs: if position changes -> pay cost
        self.data["Trade"] = self.data["Position"].diff().abs()
        self.data["Strategy"] -= self.data["Trade"] * self.cost

        # Equity curve
        self.data["Equity"] = (1 + self.data["Strategy"]).cumprod()

    def results(self):
        df = self.data.copy()

        total_return = df["Equity"].iloc[-1] - 1
        cagr = (df["Equity"].iloc[-1]) ** (252 / len(df)) - 1
        sharpe = np.sqrt(252) * df["Strategy"].mean() / df["Strategy"].std()

        max_dd = ((df["Equity"].cummax() - df["Equity"]) / df["Equity"].cummax()).max()

        return {
            "ticker": self.ticker,
            "period": f"{self.start} → {self.end}",
            "total_return_%": round(total_return * 100, 2),
            "CAGR_%": round(cagr * 100, 2),
            "Sharpe": round(sharpe, 2),
            "Max_Drawdown_%": round(max_dd * 100, 2),
            "num_trades": int(df["Trade"].sum() / 2)
        }
