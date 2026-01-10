from pathlib import Path
import pandas as pd
import numpy as np

from src.config.tickers import TICKERS

PROCESSED_DIR = Path("data/processed")
FEATURE_DIR = Path("data/processed/features")
FEATURE_DIR.mkdir(parents=True, exist_ok=True)


def build_features(df: pd.DataFrame, shift: bool = True) -> pd.DataFrame:
    # -------------------------------
    # Normalize column names
    # -------------------------------
    df = df.copy()
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    # Required columns
    for col in ["open", "high", "low", "close", "adj_close", "volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    features = pd.DataFrame(index=df.index)
    
    # Helpers
    close = df["adj_close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]
    open_p = df["open"]

    # =============================
    # A. CORE PRICE
    # =============================
    features["Price"] = close

    # =============================
    # B. RETURNS (1-8)
    # =============================
    features["ret_1d"] = close.pct_change(1)
    features["ret_3d"] = close.pct_change(3)
    features["ret_5d"] = close.pct_change(5)
    features["ret_10d"] = close.pct_change(10)

    features["log_ret_1d"] = np.log(close).diff(1)
    features["log_ret_5d"] = np.log(close).diff(5)

    features["cum_ret_5d"] = (1 + features["ret_1d"]).rolling(5).apply(np.prod, raw=True) - 1
    features["cum_ret_10d"] = (1 + features["ret_1d"]).rolling(10).apply(np.prod, raw=True) - 1

    # =============================
    # C. VOLATILITY (9-15)
    # =============================
    features["vol_5d"] = features["ret_1d"].rolling(5).std()
    features["vol_10d"] = features["ret_1d"].rolling(10).std()
    features["vol_20d"] = features["ret_1d"].rolling(20).std()

    features["vol_ratio_5_20"] = features["vol_5d"] / (features["vol_20d"] + 1e-9)
    features["vol_ratio_10_20"] = features["vol_10d"] / (features["vol_20d"] + 1e-9)

    hl_range = (high - low) / close
    features["hl_vol_5d"] = hl_range.rolling(5).mean()
    features["hl_vol_10d"] = hl_range.rolling(10).mean()

    # =============================
    # D. MOMENTUM (16-22)
    # =============================
    # 16. RSI 14
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    features["rsi_14"] = 100 - (100 / (1 + rs))

    # 17. RSI Divergence: Z(price 14d) - Z(rsi 14d)
    # Using 20d window for Z-score normalization as per standard practice in this pipeline
    def zscore(s, window=20):
        return (s - s.rolling(window).mean()) / (s.rolling(window).std() + 1e-9)
    
    features["rsi_divergence"] = zscore(close.diff(14)) - zscore(features["rsi_14"].diff(14))
    
    # Missing feature: rsi_trend
    # Inferred as Z-score of RSI change (trend of RSI)
    features["rsi_trend"] = zscore(features["rsi_14"].diff(14))

    # 18. DMI Spread
    # Wilder's Smoothing usually, but simple rolling is used here for consistency/speed
    up = high.diff()
    down = -low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0)
    minus_dm = np.where((down > up) & (down > 0), down, 0)
    
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    
    # Smooth over 14 days
    plus_di = pd.Series(plus_dm, index=df.index).rolling(14).sum() / tr.rolling(14).sum()
    minus_di = pd.Series(minus_dm, index=df.index).rolling(14).sum() / tr.rolling(14).sum()
    
    features["dmi_spread"] = (plus_di - minus_di) / (plus_di + minus_di + 1e-9)

    # 19-20 ROC
    features["roc_5d"] = features["ret_5d"] # Same math
    features["roc_10d"] = features["ret_10d"]

    # 21-22 Momentum Slope (Avg Daily Return)
    features["mom_slope_5d"] = features["ret_1d"].rolling(5).mean()
    features["mom_slope_10d"] = features["ret_1d"].rolling(10).mean()

    # =============================
    # E. TREND CONTEXT (23-28)
    # =============================
    sma5 = close.rolling(5).mean()
    sma10 = close.rolling(10).mean()
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()

    features["dist_sma_20"] = (close - sma20) / sma20
    features["dist_sma_50"] = (close - sma50) / sma50

    # 25. Trend Alignment
    # (SMA5>SMA10) + (SMA10>SMA20) + (SMA20>SMA50) + (P>SMA50)
    # Normalized to 0-1 range (sum / 4)
    alignment = (
        (sma5 > sma10).astype(int) +
        (sma10 > sma20).astype(int) +
        (sma20 > sma50).astype(int) +
        (close > sma50).astype(int)
    )
    features["trend_alignment"] = alignment / 4.0

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    features["dist_ema_20"] = (close - ema20) / ema20
    features["dist_ema_50"] = (close - ema50) / ema50

    # 28. Price Range Position
    roll_low = low.rolling(20).min()
    roll_high = high.rolling(20).max()
    features["price_range_pos_20"] = (close - roll_low) / (roll_high - roll_low + 1e-9)

    # =============================
    # F. VOLUME (29-35)
    # =============================
    vol_mean = volume.rolling(20).mean()
    vol_std = volume.rolling(20).std()

    features["volume_zscore"] = (volume - vol_mean) / (vol_std + 1e-9)
    features["volume_change_1d"] = volume.pct_change()
    features["volume_change_5d"] = volume.pct_change(5)
    
    # 32. Volume Price Corr
    features["volume_price_corr_10d"] = volume.rolling(10).corr(close)

    # 33. Vol Weighted Momentum
    # Sum(Ret * Vol) / Sum(Vol)
    vw_ret = features["ret_1d"] * volume
    features["vol_weighted_momentum"] = vw_ret.rolling(20).sum() / (volume.rolling(20).sum() + 1e-9)

    # 34. AD Momentum (ROC of A/D Line)
    mf_mult = ((close - low) - (high - close)) / (high - low + 1e-9)
    mf_vol = mf_mult * volume
    ad_line = mf_vol.cumsum()
    features["ad_momentum_14d"] = ad_line.pct_change(14) # Approximation of ROC

    # 35. Volume Surprise
    features["volume_surprise"] = volume / (volume.ewm(span=20).mean() + 1e-9)

    # =============================
    # G. VOLATILITY ESTIMATORS (36-38)
    # =============================
    # 36. Parkinson
    const_park = 1.0 / (4.0 * np.log(2.0))
    features["parkinson_vol"] = np.sqrt(const_park * np.log(high / low)**2).rolling(20).mean()

    # 37. Garman-Klass
    # 0.5 * ln(H/L)^2 - (2ln2 - 1) * ln(C/O)^2
    log_hl = np.log(high / low)
    log_co = np.log(close / open_p)
    gk = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2
    features["garman_klass_vol"] = gk.rolling(20).mean() # smoothed

    # 38. ATR Percentile
    atr20 = tr.rolling(20).mean()
    features["atr_percentile"] = atr20.rank(pct=True)

    # =============================
    # H. ENGINEERED STRUCTURE (39-40)
    # =============================
    # 39. LR Slope Confidence
    # Vectorized Slope: Cov(x,y)/Var(x). For fixed x (time), Var(x) is constant.
    # We want slope of log(price).
    # Cov(y, t) over window 20.
    # This is heavy to do exactly right with rolling apply. We use a proxy.
    # Proxy: Linear Regression Slope ~ (SMA5 - SMA20) / 15 * Scaling? No.
    # Correlation * StdY / StdX.
    # Let's use corr(log_price, time) * (std(log_price)/std(time))
    y = np.log(close)
    # time t is just index 0..N.
    # std(t) for window W is sqrt((W^2 - 1)/12) -> constant.
    window = 20
    std_t = np.sqrt((window**2 - 1) / 12)
    
    # We need correlation of y with static [0..19]. 
    # Use workaround: construct a feature 't' and roll corr.
    # Actually, simpler: Slope ~ (Price - Price_20d_ago) / 20 is the SECANT.
    # We want REGRESSION slope.
    # Let's try to be somewhat accurate:
    # slope = r * sy / sx.
    # r = y.rolling(20).corr(pd.Series(np.arange(len(df)), index=df.index)) 
    # ^ This works if index is monotonic.
    
    t_idx = pd.Series(np.arange(len(df)), index=df.index)
    r = y.rolling(window).corr(t_idx)
    sy = y.rolling(window).std()
    slope = r * (sy / std_t)
    
    features["lr_slope_conf_20"] = slope * (r**2) # Slope * R2

    # 40. OBV Divergence
    # Slope(OBV, 10d) - Slope(Price, 10d)
    # Use simple secant slope for speed: (X_t - X_t-10)/10. 
    # Or reuse the efficient slope calc above?
    # Let's use secant for robustness/simplicity as 'Divergence' is often visual.
    # But features.txt said "Slope(OBV10)".
    # Let's use (Ma5 - Ma10) proxy?
    # Let's use normalized change: (Val - Val_lag) / Val_lag / lag?
    # Let's use simple zscored differences.
    # Actually, let's stick to the Z-score logic used in RSI Divergence.
    # Z(OBV change) - Z(Price change).
    
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    
    # Slope proxy: linear change over 10 days normalized
    obv_slope = obv.diff(10) 
    price_slope = close.diff(10)
    
    features["obv_divergence"] = zscore(obv_slope, 10) - zscore(price_slope, 10)

    # =============================
    # Leakage protection
    # =============================
    features = features.replace([np.inf, -np.inf], np.nan)

    if shift:
        features = features.shift(1)

    return features
