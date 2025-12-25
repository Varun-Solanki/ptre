import React from 'react';
import styles from './FeaturesPage.module.css';

const FEATURES = [
    {
        category: "Returns (8)", items: [
            { name: "ret_1d", formula: "(Pₜ − Pₜ₋₁) / Pₜ₋₁", purpose: "Immediate price direction" },
            { name: "ret_3d", formula: "(Pₜ − Pₜ₋₃) / Pₜ₋₃", purpose: "Short-term trend" },
            { name: "ret_5d", formula: "(Pₜ − Pₜ₋₅) / Pₜ₋₅", purpose: "Medium-short momentum" },
            { name: "ret_10d", formula: "(Pₜ − Pₜ₋₁₀) / Pₜ₋₁₀", purpose: "Horizon-aligned momentum" },
            { name: "log_ret_1d", formula: "ln(Pₜ / Pₜ₋₁)", purpose: "Scale-stable daily return" },
            { name: "log_ret_5d", formula: "ln(Pₜ / Pₜ₋₅)", purpose: "Smoothed return magnitude" },
            { name: "cum_ret_5d", formula: "∏(1 + ret_1d) − 1 (5d)", purpose: "Compounded short-term return" },
            { name: "cum_ret_10d", formula: "∏(1 + ret_1d) − 1 (10d)", purpose: "Compounded horizon return" },
        ]
    },
    {
        category: "Volatility (7)", items: [
            { name: "vol_5d", formula: "Std(ret_1d) over 5d", purpose: "Short-term risk" },
            { name: "vol_10d", formula: "Std(ret_1d) over 10d", purpose: "Risk normalization base" },
            { name: "vol_20d", formula: "Std(ret_1d) over 20d", purpose: "Medium-term risk regime" },
            { name: "vol_ratio_5_20", formula: "vol_5d / vol_20d", purpose: "Volatility expansion/contraction" },
            { name: "vol_ratio_10_20", formula: "vol_10d / vol_20d", purpose: "Risk regime comparison" },
            { name: "hl_vol_5d", formula: "Mean((High−Low)/Close) 5d", purpose: "Intraday range volatility" },
            { name: "hl_vol_10d", formula: "Mean((High−Low)/Close) 10d", purpose: "Short-term price dispersion" },
        ]
    },
    {
        category: "Momentum (8)", items: [
            { name: "rsi_14", formula: "RSI over 14 periods", purpose: "Overbought / oversold signal" },
            { name: "rsi_divergence", formula: "Z(price) − Z(RSI)", purpose: "Detect hidden momentum shifts" },
            { name: "dmi_spread", formula: "(+DI − −DI) / (+DI + −DI)", purpose: "Directional dominance" },
            { name: "roc_5d", formula: "(Pₜ − Pₜ₋₅) / Pₜ₋₅", purpose: "Acceleration signal" },
            { name: "roc_10d", formula: "(Pₜ − Pₜ₋₁₀) / Pₜ₋₁₀", purpose: "Horizon-aligned ROC" },
            { name: "mom_slope_5d", formula: "Mean(ret_1d) over 5d", purpose: "Short-term trend strength" },
            { name: "mom_slope_10d", formula: "Mean(ret_1d) over 10d", purpose: "Medium-term trend strength" },
        ]
    },
    {
        category: "Trend Context (7)", items: [
            { name: "dist_sma_20", formula: "(Pₜ − SMA₂₀) / SMA₂₀", purpose: "Position relative to trend" },
            { name: "dist_sma_50", formula: "(Pₜ − SMA₅₀) / SMA₅₀", purpose: "Long-term trend bias" },
            { name: "trend_alignment", formula: "SMA Alignment Score", purpose: "Multi-timeframe trend agreement" },
            { name: "dist_ema_20", formula: "(Pₜ − EMA₂₀) / EMA₂₀", purpose: "Adaptive trend distance" },
            { name: "dist_ema_50", formula: "(Pₜ − EMA₅₀) / EMA₅₀", purpose: "Medium-term adaptive trend" },
            { name: "price_range_pos_20", formula: "(P − Low₂₀)/(High₂₀ − Low₂₀)", purpose: "Position inside recent range" },
        ]
    },
    {
        category: "Volume (6)", items: [
            { name: "volume_zscore", formula: "(Vol − Mean₂₀) / Std₂₀", purpose: "Abnormal volume detection" },
            { name: "volume_change", formula: "Delta(Volume) 1d/5d", purpose: "Sudden volume change" },
            { name: "volume_price_corr", formula: "Corr(Vol, Price) 10d", purpose: "Volume-price confirmation" },
            { name: "vol_weighted_mom", formula: "Σ(Ret×Vol)/ΣVol", purpose: "High-conviction momentum" },
            { name: "ad_momentum", formula: "ROC of A/D Line", purpose: "Institutional pressure signal" },
            { name: "volume_surprise", formula: "Vol / EMA₂₀(Vol)", purpose: "Unusual participation detection" },
        ]
    },
    {
        category: "Volatility Estimators (3)", items: [
            { name: "parkinson_vol", formula: "Range-based Vol", purpose: "Efficient range-based volatility" },
            { name: "garman_klass_vol", formula: "OHLC-based Vol", purpose: "OHLC-based volatility estimator" },
            { name: "atr_percentile", formula: "Rank of ATR₂₀", purpose: "Volatility regime detection" },
        ]
    },
    {
        category: "Engineered Structure (2)", items: [
            { name: "lr_slope_conf", formula: "Slope(LogP) × R²", purpose: "Trend direction + reliability" },
            { name: "obv_divergence", formula: "Slope(OBV) − Slope(P)", purpose: "Volume–price divergence" },
        ]
    }
];

const FeaturesPage = () => {
    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1 className={styles.title}>Feature Definitions (Phase 3)</h1>
                <p className={styles.subtitle}>
                    Total Features: 40 | Horizon Alignment: 10 Days | Leakage-Safe
                </p>
            </header>

            <div className={styles.grid}>
                {FEATURES.map((cat, idx) => (
                    <div key={idx} className={styles.categoryCard}>
                        <h3 className={styles.categoryTitle}>{cat.category}</h3>
                        <div className={styles.featureList}>
                            {cat.items.map((feat, fIdx) => (
                                <div key={fIdx} className={styles.featureRow}>
                                    <div className={styles.featureName}>{feat.name}</div>
                                    <div className={styles.featureFormula}>{feat.formula}</div>
                                    <div className={styles.featurePurpose}>{feat.purpose}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FeaturesPage;
