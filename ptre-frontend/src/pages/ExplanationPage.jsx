import React from 'react';
import styles from './ExplanationPage.module.css';

const ExplanationPage = () => {
    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1 className={styles.title}>System Internals & Architecture</h1>
                <p className={styles.subtitle}>
                    A technical deep-dive into how PTRE generates signals.
                </p>
            </header>

            {/* 1. Visual Architecture Flow */}
            <section className={styles.section}>
                <h2>1. Data Pipeline Architecture</h2>
                <div className={styles.pipeline}>
                    {/* Step 1: Source */}
                    <div className={styles.stage}>
                        <div className={styles.node}>Market Data (OHLCV)</div>
                        <div className={styles.arrow}>↓</div>
                        <div className={styles.label}>Feature Engineering</div>
                    </div>

                    {/* Step 2: Models (Parallel) */}
                    <div className={styles.stageRow}>
                        <div className={styles.branch}>
                            <div className={styles.node}>
                                <strong>Trend Model</strong>
                                <span className={styles.detail}>~40 Features</span>
                                <span className={styles.tag}>HistGradBoost</span>
                            </div>
                        </div>
                        <div className={styles.branch}>
                            <div className={styles.node}>
                                <strong>Momentum Model</strong>
                                <span className={styles.detail}>11 Features</span>
                                <span className={styles.tag}>HistGradBoost</span>
                            </div>
                        </div>
                    </div>

                    {/* Step 3: Gating */}
                    <div className={styles.connector}>
                        <div className={styles.arrow}>↓</div>
                        <div className={styles.arrow}>↓</div>
                    </div>

                    <div className={styles.stage}>
                        <div className={styles.nodeBox}>
                            <strong>Soft Gating & Ensemble</strong>
                            <p>0.7 × Trend + 0.3 × Mom</p>
                            <p className={styles.penalty}>Disagreement Penalty (-15%)</p>
                        </div>
                        <div className={styles.arrow}>↓</div>
                    </div>

                    {/* Step 4: Risk Map */}
                    <div className={styles.stage}>
                        <div className={styles.nodeBox}>
                            <strong>Neutral Zone Risk Map</strong>
                            <p>Volatility Injection (API Level)</p>
                        </div>
                        <div className={styles.arrow}>↓</div>
                    </div>

                    {/* Step 5: Output */}
                    <div className={styles.stage}>
                        <div className={styles.finalNode}>Final Signal & Confidence</div>
                    </div>
                </div>
            </section>

            <div className={styles.divider} />

            {/* 2. Model Details */}
            <div className={styles.grid}>
                <div className={styles.card}>
                    <h3>2a. Trend Model</h3>
                    <p>
                        <strong>Algorithm:</strong> Histogram Gradient Boosting Classifier (sklearn).<br />
                        <strong>Features:</strong> Uses approximately 40 engineered features including volatility estimators, gap analysis, and price action derivatives.<br />
                        <strong>Logic:</strong> Trained to detect non-linear regime changes. It outputs a 3-class probability: Bullish (+1), Neutral (0), or Bearish (-1).
                    </p>
                </div>

                <div className={styles.card}>
                    <h3>2b. Momentum Model</h3>
                    <p>
                        <strong>Algorithm:</strong> Histogram Gradient Boosting Classifier.<br />
                        <strong>Features:</strong> 11 High-Impact Features:<br />
                        <code>ret_1d, ret_3d, ret_5d, roc_5d, mom_slope_5d, vol_ratio, hl_vol, vol_weighted_mom, vol_zscore, vol_surprise, rsi_14</code>.<br />
                        <strong>Logic:</strong> A "Fast" verification layer. Checks if the trend is supported by velocity and volume.
                    </p>
                </div>
            </div>

            <div className={styles.divider} />

            {/* 3. Performance Metrics & Calibration (Detailed Linear View) */}
            <section className={styles.section}>
                <h2>3. Performance Metrics & Calibration</h2>

                <div className={styles.detailBlock}>
                    <h3>Directional Accuracy</h3>
                    <p>
                        Directional Accuracy represents the straightforward "hit rate" of the model: <em>How often does the model correctly predict the sign (positive or negative) of the future return?</em>
                    </p>
                    <p>
                        In academic financial machine learning, a consistent directional accuracy above <strong>52-54%</strong> is considered statistically significant ("Alpha"). PTRE aims for this baseline to ensure the statistical edge of the casino, rather than trying to predict the exact price magnitude, which is notoriously noisy.
                    </p>
                </div>

                <div className={styles.detailBlock}>
                    <h3>Precision vs. Noise</h3>
                    <p>
                        While accuracy measures overall correctness, <strong>Precision</strong> is more critical for a trading system. It answers: <em>"When the model actually triggers a signal, how likely is it to be correct?"</em>
                    </p>
                    <p>
                        A model can have 50% accuracy but high precision if it stays "Neutral" during choppy markets and only bets when certainty is high. PTRE optimizes for Precision over Recall—meaning we prefer to miss a trade (stay Neutral) rather than take a losing trade.
                    </p>
                </div>

                <div className={styles.detailBlock}>
                    <h3>Probability Calibration (Isotonic Regression)</h3>
                    <p>
                        Most machine learning models output a raw score (e.g., 0.85) that is not a true probability. It just means the model is "very sure" relative to other samples.
                    </p>
                    <p>
                        <strong>The Solution:</strong> We apply a secondary layer called <em>Isotonic Regression</em> (or Sigmoid calibration). This maps the raw scores to historical win rates.
                    </p>
                    <p>
                        <strong>Why it matters:</strong> If the PTRE dashboard shows <strong>70% Confidence</strong>, it mathematically means that in the past, when the model saw this exact setup, the price moved in the predicted direction <strong>70% of the time</strong>. This allows traders to use the <em>Kelly Criterion</em> for position sizing—betting larger when the calibrated probability is higher.
                    </p>
                </div>
            </section>

            <div className={styles.divider} />

            {/* 4. Risk Score */}
            <section className={styles.section}>
                <h2>4. Risk Score & Volatility</h2>
                <p>
                    <strong>Risk Score Calculation:</strong> In the current implementation, the "Risk Score" displayed on the dashboard is directly derived from the <strong>Final Confidence</strong> of the model ensemble (0-100). Lower confidence implies higher uncertainty risk.
                </p>
                <div className={styles.riskDefs}>
                    <h3>Volatility Regimes (6-Month Calculation):</h3>
                    <ul>
                        <li><span className={styles.low}>Low Risk</span>: &lt; 20% annualized volatility. Safe for aggressive sizing.</li>
                        <li><span className={styles.mod}>Moderate Risk</span>: 20% - 35%. Normal market conditions.</li>
                        <li><span className={styles.high}>High Risk</span>: &gt; 35%. Choppy/Crash conditions. Signal reliability decreases.</li>
                    </ul>
                </div>
                <p>
                    <strong>Necessity:</strong> This volatility overlay acts as a final sanity check. Even if the model is confident, high volatility (e.g., during earnings or a crash) warns the user that the "path" to the target will be turbulent.
                </p>
            </section>

            <div className={styles.divider} />

            {/* 5. Algorithm Deep Dive */}
            <section className={styles.section}>
                <h2>5. Algorithm Deep Dive: HistGradBoost</h2>

                <div className={styles.detailBlock}>
                    <h3>What is Histogram-Based Gradient Boosting?</h3>
                    <p>
                        <strong>HistGradBoost</strong> is a modern, high-performance implementation of Gradient Boosting Trees (similar to LightGBM). Unlike traditional Random Forests that split data based on exact values, HistGradBoost places continuous values into discrete bins (histograms).
                    </p>
                </div>

                <div className={styles.detailBlock}>
                    <h3>Why we chose it over Deep Learning (LSTM/Transformers):</h3>
                    <p>
                        For <strong>Tabular Financial Data</strong>, tree-based ensembles consistently outperform deep learning models in low-signal-to-noise environments. Deep learning (LSTMs) often overfits the noise in price data. HistGradBoost is robust, requires less tuning, and handles the chaotic nature of markets better.
                    </p>
                </div>

                <div className={styles.detailBlock}>
                    <h3>Critical Characteristic: Native NaN Handling</h3>
                    <p>
                        <strong>Real-world data is messy.</strong> In finance, indicators like "200-day Moving Average" are undefined (NaN) for the first 200 days of a stock's life.
                    </p>
                    <p>
                        Most models crash on NaNs or require clumsy "imputation" (filling with zeros/averages), which introduces bias. HistGradBoost has <strong>Native Support for Missing Values</strong>—it learns the optimal direction to send "missing" data points during the tree split, treating "lack of data" as a signal in itself. This is crucial for robust backtesting.
                    </p>
                </div>
            </section>
        </div>
    );
};

export default ExplanationPage;
