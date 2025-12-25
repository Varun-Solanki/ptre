import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowRight } from 'lucide-react';
import styles from './LandingPage.module.css';

const LandingPage = () => {
    return (
        <div className={styles.container}>
            <div className={styles.hero}>
                <div className={styles.logoContainer}>
                    <Activity size={64} className={styles.logoIcon} />
                </div>

                <h1 className={styles.title}>PTRE</h1>
                <h2 className={styles.subtitle}>Probabilistic Trend & Risk Engine for Equities</h2>

                <p className={styles.description}>
                    Advanced quantitative signal generation using soft-gated ML trend models and momentum analytics.
                    <br />
                    Confidence-weighted directional outputs for professional risk management.
                </p>

                <Link to="/dashboard" className={styles.ctaButton}>
                    Launch Terminal <ArrowRight size={20} />
                </Link>
            </div>

            <div className={styles.features}>
                <div className={styles.featureCard}>
                    <h3>Multi-Factor Models</h3>
                    <p>Combines classical momentum with machine learning trend detection.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>Calibrated Probability</h3>
                    <p>Raw model outputs are calibrated to real-world probabilities, ensuring 60% confidence means 60% accuracy.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>Neutral Zone Risk Map</h3>
                    <p>Proprietary risk mapping identifies "dead zones" where volatility eats returns, forcing a Neutral stance.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>Momentum Labels</h3>
                    <p>Training targets derive from future risk-adjusted returns (Sharpe-like), not just raw price direction.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>Decade-Scale Training</h3>
                    <p>Models are trained on 10+ years of high-resolution historical market data to capture robust patterns.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>Institutional Grade</h3>
                    <p>Designed with the same rigorous risk-first architecture and volatility gating used by quantitative hedge funds.</p>
                </div>
            </div>
        </div>
    );
};

export default LandingPage;
