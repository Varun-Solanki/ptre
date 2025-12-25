import React from 'react';
import styles from './SystemPage.module.css';

const SystemPage = () => {
    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1 className={styles.title}>System Architecture & Features</h1>
                <p className={styles.subtitle}>
                    A deep dive into the Probabilistic Trend & Risk Engine (PTRE).
                </p>
            </header>

            <section className={styles.section}>
                <h2>01. The Problem with Binary Signals</h2>
                <p>
                    Traditional technical analysis often forces a binary "Buy" or "Sell" choice, ignoring the inherent uncertainty.
                    PTRE treats trend direction as a continuous probability distribution, not a coin flip.
                </p>
            </section>

            <div className={styles.divider} />

            <section className={styles.section}>
                <h2>02. Model Ensemble</h2>
                <div className={styles.grid}>
                    <div className={styles.card}>
                        <h3>Trend Model (ML)</h3>
                        <p>
                            A non-linear classifier trained on price action features (volatility, slope, gaps).
                            It detects structural regime changes that simple moving averages miss.
                        </p>
                    </div>
                    <div className={styles.card}>
                        <h3>Momentum Model (Quantitative)</h3>
                        <p>
                            A classic robust momentum filter measuring velocity over a dynamic lookback window.
                            It confirms if the ML-detected trend has actual market participation backing it.
                        </p>
                    </div>
                </div>
            </section>

            <div className={styles.divider} />

            <section className={styles.section}>
                <h2>03. Soft-Gating & Calibration</h2>
                <p>
                    Raw model scores are rarely well-calibrated probabilities. PTRE applies a calibration layer (Isotonic Regression) to ensure that a predicted
                    confidence of 70% roughly corresponds to a 70% historical win rate.
                </p>
                <div className={styles.formula}>
                    Calibrated P(x) = Isotonic( Raw_Model_Output(x) )
                </div>
            </section>

            <div className={styles.divider} />

            <section className={styles.section}>
                <h2>04. Proprietary Neutral Zone Risk Map</h2>
                <p>
                    The engine uses a dynamic "Risk Map" to identify market states where the signal-to-noise ratio is too low to trade.
                    This overrides bullish/bearish signals into a forced Neutral state.
                </p>
                <div className={styles.formula}>
                     If Volatility > Regime_Threshold AND Momentum &lt; Conviction_Floor <br />
                    THEN Signal = Neutral (0)
                </div>
                <p>
                    This prevents the system from taking positions during "choppy" high-volatility sideways markets, effectively acting as a volatility shield.
                </p>
            </section>

            <div className={styles.divider} />

            <section className={styles.section}>
                <h2>05. Risk-Adjusted Labels</h2>
                <p>
                    The models are trained not on raw price changes, but on <strong>future risk-adjusted returns</strong> (forward Sharpe ratio).
                    See the <a href="/labels" className={styles.link}>Labels Page</a> for the exact formulas.
                </p>
            </section>
        </div>
    );
};

export default SystemPage;
