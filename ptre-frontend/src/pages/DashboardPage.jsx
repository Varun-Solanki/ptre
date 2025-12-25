import React, { useState, useEffect } from 'react';
import { fetchSignal } from '../api/client';
import TickerSelector from '../components/TickerSelector';
import SignalCard from '../components/SignalCard';
import ModelCard from '../components/ModelCard';
import RiskCard from '../components/RiskCard';
import PriceChart from '../components/PriceChart';
import TechIndicatorsCard from '../components/TechIndicatorsCard';
import ExplainabilityCard from '../components/ExplainabilityCard';
import styles from './DashboardPage.module.css';

const DashboardPage = () => {
    const [selectedTicker, setSelectedTicker] = useState('AAPL');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError(null);
            try {
                const result = await fetchSignal(selectedTicker);
                setData(result);
            } catch (err) {
                setError('Failed to fetch data for the selected ticker. Please try again.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        if (selectedTicker) {
            loadData();
        }
    }, [selectedTicker]);

    return (
        <div className={styles.dashboard}>
            <header className={styles.controlsHeader}>
                <TickerSelector
                    selectedTicker={selectedTicker}
                    onChange={setSelectedTicker}
                />
                <div className={styles.lastUpdated}>
                    {data && `Last Updated: ${new Date(data.timestamp).toLocaleString()}`}
                </div>
            </header>

            {error && (
                <div className={styles.errorBanner}>{error}</div>
            )}

            {loading && (
                <div className={styles.loadingState}>
                    <div className={styles.spinner}></div>
                    <span>Analyzing market signals...</span>
                </div>
            )}

            {!loading && data && (
                <>
                    {/* Top Row: Chart + Core Signals */}
                    <div className={styles.grid}>
                        {/* Main Chart Area */}
                        <div className={styles.chartSection}>
                            <PriceChart data={data.price_chart} />
                        </div>

                        {/* Right Sidebar: Models & Signal */}
                        <div className={styles.cardsSection}>
                            {/* Models (Top) */}
                            <div className={styles.modelsGrid}>
                                <ModelCard
                                    title="Trend Model"
                                    direction={data.trend.direction}
                                    confidence={data.trend.confidence}
                                />

                                <ModelCard
                                    title="Momentum Model"
                                    direction={data.momentum.direction}
                                    confidence={data.momentum.confidence}
                                    horizon={data.momentum.horizon_days}
                                    agreement={data.agreement}
                                />
                            </div>

                            {/* Signal (Middle) */}
                            <SignalCard
                                signal={data.final_signal}
                                confidence={data.final_confidence}
                            />
                        </div>
                    </div>

                    {/* Bottom Row: Indicators (Left) & Risk + Explain (Right) */}
                    <div className={styles.bottomRow}>
                        <TechIndicatorsCard prices={data.price_chart.prices} />

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
                            <ExplainabilityCard data={data} />
                            <RiskCard
                                volatility={data.risk.volatility}
                                volatilityValue={data.risk.volatility_value}
                                riskScore={data.risk.risk_score}
                            />
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardPage;
