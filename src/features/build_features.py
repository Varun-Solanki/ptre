# """
# PTRE - Feature Engineering

# Builds leakage-safe features from cleaned OHLCV data.
# All features are shifted by 1 day to avoid lookahead bias.
# """

# from pathlib import Path
# import pandas as pd
# import numpy as np

# from src.config.tickers import TICKERS
# from src.config.settings import PREDICTION_HORIZON


# PROCESSED_DIR = Path("data/processed")
# FEATURE_DIR = Path("data/processed/features")
# FEATURE_DIR.mkdir(parents=True, exist_ok=True)


# def build_features(df: pd.DataFrame) -> pd.DataFrame:
#     features = pd.DataFrame(index=df.index)

#     # -----------------------------
#     # A. RETURNS
#     # -----------------------------
#     features["ret_1d"] = df["adj_close"].pct_change(1)
#     features["ret_3d"] = df["adj_close"].pct_change(3)
#     features["ret_5d"] = df["adj_close"].pct_change(5)
#     features["ret_10d"] = df["adj_close"].pct_change(10)

#     # Log returns
#     features["log_ret_1d"] = np.log(df["adj_close"]).diff(1)
#     features["log_ret_5d"] = np.log(df["adj_close"]).diff(5)

#     # Rolling cumulative return
#     features["cum_ret_5d"] = (1 + features["ret_1d"]).rolling(5).apply(np.prod, raw=True) - 1
#     features["cum_ret_10d"] = (1 + features["ret_1d"]).rolling(10).apply(np.prod, raw=True) - 1


#     # -----------------------------
#     # B. VOLATILITY
#     # -----------------------------
#     features["vol_5d"] = features["ret_1d"].rolling(5).std()
#     features["vol_10d"] = features["ret_1d"].rolling(10).std()
#     features["vol_20d"] = features["ret_1d"].rolling(20).std()

#     # Volatility ratios
#     features["vol_ratio_5_20"] = features["vol_5d"] / features["vol_20d"]
#     features["vol_ratio_10_20"] = features["vol_10d"] / features["vol_20d"]

#     # High-Low range volatility
#     hl_range = (df["high"] - df["low"]) / df["adj_close"]
#     features["hl_vol_5d"] = hl_range.rolling(5).mean()
#     features["hl_vol_10d"] = hl_range.rolling(10).mean()



#     # -----------------------------
#     # C. MOMENTUM
#     # -----------------------------
#     delta = df["adj_close"].diff()
#     gain = delta.clip(lower=0)
#     loss = -delta.clip(upper=0)

#     avg_gain = gain.rolling(14).mean()
#     avg_loss = loss.rolling(14).mean()
#     rs = avg_gain / avg_loss
#     features["rsi_14"] = 100 - (100 / (1 + rs))

#     # RSI divergence (engineered)
#     price_ret_14 = df["adj_close"].pct_change(14)
#     rsi_change_14 = features["rsi_14"].diff(14)

#     features["rsi_divergence"] = (
#         (price_ret_14 - price_ret_14.rolling(50).mean()) /
#         price_ret_14.rolling(50).std() + 1e-6
#         -
#         (rsi_change_14 - rsi_change_14.rolling(50).mean()) /
#         rsi_change_14.rolling(50).std()
#     )

#     # DMI spread (directional dominance) -> (engineered)
#     high = df["high"]
#     low = df["low"]
#     close = df["close"]

#     up_move = high.diff()
#     down_move = low.shift() - low

#     plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
#     minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

#     plus_dm = pd.Series(plus_dm, index=df.index)
#     minus_dm = pd.Series(minus_dm, index=df.index)

#     tr = pd.concat([
#         high - low,
#         (high - close.shift()).abs(),
#         (low - close.shift()).abs()
#     ], axis=1).max(axis=1)

#     atr_14 = tr.rolling(14).mean()

#     plus_di = 100 * (plus_dm.rolling(14).mean() / atr_14)
#     minus_di = 100 * (minus_dm.rolling(14).mean() / atr_14)

#     features["dmi_spread"] = (plus_di - minus_di) / (plus_di + minus_di)
#     features = features.replace([np.inf, -np.inf], np.nan)


#     # Rate of Change
#     features["roc_5d"] = df["adj_close"].pct_change(5)
#     features["roc_10d"] = df["adj_close"].pct_change(10)

#     # Momentum slope (trend strength)
#     features["mom_slope_5d"] = features["ret_1d"].rolling(5).mean()
#     features["mom_slope_10d"] = features["ret_1d"].rolling(10).mean()

#     # -----------------------------
#     # D. TREND CONTEXT
#     # -----------------------------
#     sma_20 = df["adj_close"].rolling(20).mean()
#     sma_50 = df["adj_close"].rolling(50).mean()

#     features["dist_sma_20"] = (df["adj_close"] - sma_20) / sma_20
#     features["dist_sma_50"] = (df["adj_close"] - sma_50) / sma_50

#     # Multi-timeframe trend alignment score (engineered)
#     sma_5 = df["adj_close"].rolling(5).mean()
#     sma_10 = df["adj_close"].rolling(10).mean()

#     trend_score = (
#         (sma_5 > sma_10).astype(int) +
#         (sma_10 > sma_20).astype(int) +
#         (sma_20 > sma_50).astype(int) +
#         (df["adj_close"] > sma_50).astype(int)
#     )

#     # Normalize to [-1, +1]
#     features["trend_alignment"] = (trend_score - 2) / 2


#     # EMA distances
#     ema_20 = df["adj_close"].ewm(span=20, adjust=False).mean()
#     ema_50 = df["adj_close"].ewm(span=50, adjust=False).mean()

#     features["dist_ema_20"] = (df["adj_close"] - ema_20) / ema_20
#     features["dist_ema_50"] = (df["adj_close"] - ema_50) / ema_50

#     # Price position in recent range
#     rolling_low_20 = df["adj_close"].rolling(20).min()
#     rolling_high_20 = df["adj_close"].rolling(20).max()

#     features["price_range_pos_20"] = (
#         (df["adj_close"] - rolling_low_20) /
#         (rolling_high_20 - rolling_low_20)
#     )


#     # -----------------------------
#     # E. VOLUME
#     # -----------------------------
#     vol_mean_20 = df["volume"].rolling(20).mean()
#     vol_std_20 = df["volume"].rolling(20).std()
#     features["volume_zscore"] = (df["volume"] - vol_mean_20) / vol_std_20

#     # Volume trend
#     features["volume_change_1d"] = df["volume"].pct_change(1)
#     features["volume_change_5d"] = df["volume"].pct_change(5)

#     # Volume relative to price movement
#     features["volume_price_corr_10d"] = (
#         df["volume"].rolling(10).corr(df["adj_close"])
#     )


#     # -----------------------------
#     # F. CUSTOM / REGIME
#     # -----------------------------
#     # features["ret_vol_ratio"] = features["ret_5d"] / features["vol_10d"]

#     # -----------------------------
#     # F. ENGINEERED FEATURES
#     # -----------------------------

#     # Volume-weighted momentum
#     features["vol_weighted_momentum"] = (
#         (features["ret_1d"] * df["volume"])
#         .rolling(20).sum()
#         /
#         df["volume"].rolling(20).sum()
#     )

#     # Accumulation / Distribution momentum
#     money_flow_mult = (
#         ((df["close"] - df["low"]) - (df["high"] - df["close"])) /
#         (df["high"] - df["low"])
#     ).replace([np.inf, -np.inf], 0)

#     ad_line = (money_flow_mult * df["volume"]).cumsum()
#     features["ad_momentum_14d"] = ad_line.pct_change(14)

#     # Volume surprise
#     features["volume_surprise"] = (
#         df["volume"] /
#         df["volume"].ewm(span=20, adjust=False).mean()
#     )

#     # Parkinson volatility
#     features["parkinson_vol"] = np.sqrt(
#         (1 / (4 * np.log(2))) *
#         (np.log(df["high"] / df["low"]) ** 2)
#     )

#     # Garman-Klass volatility
#     features["garman_klass_vol"] = (
#         0.5 * (np.log(df["high"] / df["low"]) ** 2)
#         -
#         (2 * np.log(2) - 1) *
#         (np.log(df["close"] / df["open"]) ** 2)
#     )

#     # ATR percentile
#     tr = pd.concat([
#         df["high"] - df["low"],
#         (df["high"] - df["close"].shift()).abs(),
#         (df["low"] - df["close"].shift()).abs()
#     ], axis=1).max(axis=1)

#     atr_20 = tr.rolling(20).mean()
#     features["atr_percentile"] = atr_20.rank(pct=True)

#     # Linear regression slope confidence (slope × R²)
#     log_price = np.log(df["adj_close"])

#     def slope_confidence(series):
#         x = np.arange(len(series))
#         if series.isna().any():
#             return np.nan
#         coef = np.polyfit(x, series, 1)
#         slope = coef[0]
#         fitted = np.polyval(coef, x)
#         ss_res = np.sum((series - fitted) ** 2)
#         ss_tot = np.sum((series - series.mean()) ** 2)
#         r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
#         return slope * r2

#     features["lr_slope_conf_20"] = (
#         log_price.rolling(20).apply(slope_confidence, raw=False)
#     )

#     # OBV trend divergence
#     obv = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()

#     price_slope_10 = (
#         df["adj_close"]
#         .rolling(10)
#         .apply(lambda x: np.polyfit(np.arange(len(x)), x, 1)[0], raw=False)
#     )

#     obv_slope_10 = (
#         obv
#         .rolling(10)
#         .apply(lambda x: np.polyfit(np.arange(len(x)), x, 1)[0], raw=False)
#     )

#     features["obv_divergence"] = obv_slope_10 - price_slope_10




#     # -----------------------------
#     # LEAKAGE PROTECTION
#     # -----------------------------
#     features = features.shift(1)

#     return features


# def main():
#     print("Building features...\n")

#     for ticker in TICKERS:
#         print(f"Processing {ticker}...")

#         df = pd.read_csv(
#             PROCESSED_DIR / f"{ticker}_clean.csv",
#             index_col=0,
#             parse_dates=True
#         )

#         features = build_features(df)
#         features = features.dropna()

#         out_path = FEATURE_DIR / f"{ticker}_features.csv"
#         features.to_csv(out_path)

#         print(f"Saved → {out_path}")
#         print(f"Feature shape: {features.shape}\n")

#     print("Feature engineering completed.")


# if __name__ == "__main__":
#     main()

"""
PTRE - Feature Engineering

Builds leakage-safe features from cleaned OHLCV data.
All features are shifted by 1 day to avoid lookahead bias.
"""

from pathlib import Path
import pandas as pd
import numpy as np

from src.config.tickers import TICKERS
from src.config.settings import PREDICTION_HORIZON


PROCESSED_DIR = Path("data/processed")
FEATURE_DIR = Path("data/processed/features")
FEATURE_DIR.mkdir(parents=True, exist_ok=True)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)

    # =============================
    # A. RETURNS
    # =============================
    features["ret_1d"] = df["adj_close"].pct_change(1)
    features["ret_3d"] = df["adj_close"].pct_change(3)
    features["ret_5d"] = df["adj_close"].pct_change(5)
    features["ret_10d"] = df["adj_close"].pct_change(10)

    features["log_ret_1d"] = np.log(df["adj_close"]).diff(1)
    features["log_ret_5d"] = np.log(df["adj_close"]).diff(5)

    features["cum_ret_5d"] = (1 + features["ret_1d"]).rolling(5).apply(np.prod, raw=True) - 1
    features["cum_ret_10d"] = (1 + features["ret_1d"]).rolling(10).apply(np.prod, raw=True) - 1

    # =============================
    # B. VOLATILITY
    # =============================
    features["vol_5d"] = features["ret_1d"].rolling(5).std()
    features["vol_10d"] = features["ret_1d"].rolling(10).std()
    features["vol_20d"] = features["ret_1d"].rolling(20).std()

    features["vol_ratio_5_20"] = features["vol_5d"] / (features["vol_20d"] + 1e-6)
    features["vol_ratio_10_20"] = features["vol_10d"] / (features["vol_20d"] + 1e-6)

    hl_range = (df["high"] - df["low"]) / df["adj_close"]
    features["hl_vol_5d"] = hl_range.rolling(5).mean()
    features["hl_vol_10d"] = hl_range.rolling(10).mean()

    # =============================
    # C. MOMENTUM
    # =============================
    delta = df["adj_close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    features["rsi_14"] = 100 - (100 / (1 + rs))

    # RSI divergence (normalized & stable)
    price_ret_14 = df["adj_close"].pct_change(14)
    rsi_change_14 = features["rsi_14"].diff(14)

    features["rsi_divergence"] = (
        (price_ret_14 - price_ret_14.rolling(50).mean()) /
        (price_ret_14.rolling(50).std() + 1e-6)
        -
        (rsi_change_14 - rsi_change_14.rolling(50).mean()) /
        (rsi_change_14.rolling(50).std() + 1e-6)
    )

    # Correct DMI spread
    high = df["high"]
    low = df["low"]
    close = df["close"]

    up_move = high.diff()
    down_move = low.shift() - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    plus_dm = pd.Series(plus_dm, index=df.index)
    minus_dm = pd.Series(minus_dm, index=df.index)

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr_14 = tr.rolling(14).mean()

    plus_di = 100 * (plus_dm.rolling(14).mean() / atr_14)
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr_14)

    features["dmi_spread"] = (plus_di - minus_di) / (plus_di + minus_di + 1e-6)

    features["roc_5d"] = df["adj_close"].pct_change(5)
    features["roc_10d"] = df["adj_close"].pct_change(10)

    features["mom_slope_5d"] = features["ret_1d"].rolling(5).mean()
    features["mom_slope_10d"] = features["ret_1d"].rolling(10).mean()

    # =============================
    # D. TREND CONTEXT
    # =============================
    sma_5 = df["adj_close"].rolling(5).mean()
    sma_10 = df["adj_close"].rolling(10).mean()
    sma_20 = df["adj_close"].rolling(20).mean()
    sma_50 = df["adj_close"].rolling(50).mean()

    features["dist_sma_20"] = (df["adj_close"] - sma_20) / sma_20
    features["dist_sma_50"] = (df["adj_close"] - sma_50) / sma_50

    trend_score = (
        (sma_5 > sma_10).astype(int) +
        (sma_10 > sma_20).astype(int) +
        (sma_20 > sma_50).astype(int) +
        (df["adj_close"] > sma_50).astype(int)
    )

    features["trend_alignment"] = (trend_score - 2) / 2

    ema_20 = df["adj_close"].ewm(span=20, adjust=False).mean()
    ema_50 = df["adj_close"].ewm(span=50, adjust=False).mean()

    features["dist_ema_20"] = (df["adj_close"] - ema_20) / ema_20
    features["dist_ema_50"] = (df["adj_close"] - ema_50) / ema_50

    rolling_low_20 = df["adj_close"].rolling(20).min()
    rolling_high_20 = df["adj_close"].rolling(20).max()

    features["price_range_pos_20"] = (
        (df["adj_close"] - rolling_low_20) /
        (rolling_high_20 - rolling_low_20)
    )

    # =============================
    # E. VOLUME
    # =============================
    vol_mean_20 = df["volume"].rolling(20).mean()
    vol_std_20 = df["volume"].rolling(20).std()

    features["volume_zscore"] = (df["volume"] - vol_mean_20) / vol_std_20
    features["volume_change_1d"] = df["volume"].pct_change(1)
    features["volume_change_5d"] = df["volume"].pct_change(5)
    features["volume_price_corr_10d"] = df["volume"].rolling(10).corr(df["adj_close"])

    # =============================
    # F. ENGINEERED FEATURES
    # =============================
    features["vol_weighted_momentum"] = (
        (features["ret_1d"] * df["volume"]).rolling(20).sum() /
        df["volume"].rolling(20).sum()
    )

    money_flow_mult = (
        ((df["close"] - df["low"]) - (df["high"] - df["close"])) /
        (df["high"] - df["low"])
    ).replace([np.inf, -np.inf], 0)

    ad_line = (money_flow_mult * df["volume"]).cumsum()
    features["ad_momentum_14d"] = ad_line.pct_change(14)

    features["volume_surprise"] = df["volume"] / df["volume"].ewm(span=20, adjust=False).mean()

    features["parkinson_vol"] = np.sqrt(
        (1 / (4 * np.log(2))) * (np.log(df["high"] / df["low"]) ** 2)
    )

    features["garman_klass_vol"] = (
        0.5 * (np.log(df["high"] / df["low"]) ** 2)
        -
        (2 * np.log(2) - 1) * (np.log(df["close"] / df["open"]) ** 2)
    )

    atr_20 = tr.rolling(20).mean()
    features["atr_percentile"] = atr_20.rank(pct=True)

    log_price = np.log(df["adj_close"])

    def slope_confidence(series):
        x = np.arange(len(series))
        if series.isna().any():
            return np.nan
        coef = np.polyfit(x, series, 1)
        slope = coef[0]
        fitted = np.polyval(coef, x)
        ss_res = np.sum((series - fitted) ** 2)
        ss_tot = np.sum((series - series.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
        return slope * r2

    features["lr_slope_conf_20"] = log_price.rolling(20).apply(slope_confidence, raw=False)

    obv = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()

    price_slope_10 = df["adj_close"].rolling(10).apply(
        lambda x: np.polyfit(np.arange(len(x)), x, 1)[0], raw=False
    )

    obv_slope_10 = obv.rolling(10).apply(
        lambda x: np.polyfit(np.arange(len(x)), x, 1)[0], raw=False
    )

    features["obv_divergence"] = obv_slope_10 - price_slope_10

    # =============================
    # LEAKAGE PROTECTION
    # =============================
    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.shift(1)

    return features


def main():
    print("Building features...\n")

    for ticker in TICKERS:
        print(f"Processing {ticker}...")

        df = pd.read_csv(
            PROCESSED_DIR / f"{ticker}_clean.csv",
            index_col=0,
            parse_dates=True
        )

        features = build_features(df)
        features = features.dropna()

        out_path = FEATURE_DIR / f"{ticker}_features.csv"
        features.to_csv(out_path)

        print(f"Saved → {out_path}")
        print(f"Feature shape: {features.shape}\n")

    print("Feature engineering completed.")


if __name__ == "__main__":
    main()
