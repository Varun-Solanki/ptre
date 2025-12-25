import React from 'react';
import styles from './LabelsPage.module.css';

const LabelsPage = () => {
    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1 className={styles.title}>Label Definition (Phase 4)</h1>
                <p className={styles.subtitle}>
                    Understanding how PTRE defines "truth" for model training.
                </p>
            </header>

            <section className={styles.section}>
                <h2>Core Concept</h2>
                <p>
                    In PTRE, labels represent the <strong>future directional trend</strong>, not a precise price prediction.
                    They answer the question: <em>"Given today's market structure, what was the risk-adjusted directional outcome over the next 10 trading days?"</em>
                </p>
            </section>

            <div className={styles.divider} />

            <section className={styles.section}>
                <h2>Formula 1: Future Return (Direction)</h2>
                <div className={styles.formulaBox}>
                    <code>r(t,10) = ( P(t+10) − P(t) ) / P(t)</code>
                </div>
                <p>
                    Where <code>P(t)</code> is the price today and <code>P(t+10)</code> is the price 10 trading days in the future.
                    This measures strict direction but ignores volatility.
                </p>
            </section>

            <section className={styles.section}>
                <h2>Formula 2: Risk Normalization (Context)</h2>
                <div className={styles.formulaBox}>
                    <code>z(t) = r(t,10) / σ(t)</code>
                </div>
                <p>
                    Where <code>σ(t)</code> is the 10-day historical volatility. This normalizes the return, ensuring that high-volatility moves aren't over-rewarded and stable trends aren't penalized.
                </p>
            </section>

            <div className={styles.divider} />

            <section className={styles.section}>
                <h2>Final Label Logic</h2>
                <p>Labels are assigned using symmetric thresholds on the risk-adjusted return <code>z(t)</code>:</p>
                <div className={styles.tableContainer}>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Condition</th>
                                <th>Label</th>
                                <th>Meaning</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className={styles.rowBullish}>
                                <td>z(t) ≥ +0.75</td>
                                <td>+1 (Bullish)</td>
                                <td>Strong upside trend relative to risk</td>
                            </tr>
                            <tr className={styles.rowBearish}>
                                <td>z(t) ≤ −0.75</td>
                                <td>−1 (Bearish)</td>
                                <td>Strong downside trend relative to risk</td>
                            </tr>
                            <tr className={styles.rowNeutral}>
                                <td>Otherwise</td>
                                <td>0 (Neutral)</td>
                                <td>Noise, chop, or insignificant movement</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    );
};

export default LabelsPage;
