import React, { useState } from 'react';
import { fetchBacktest } from '../api/client';
import TickerSelector from '../components/TickerSelector';
import EquityChart from '../components/EquityChart';
import styles from './BacktestPage.module.css';
import { Info, TrendingUp, Activity, AlertTriangle, DollarSign } from 'lucide-react';
import clsx from 'clsx';

const BacktestPage = () => {
    const [selectedTicker, setSelectedTicker] = useState('AAPL');
    const [startDate, setStartDate] = useState('2020-01-01');
    const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleRunBacktest = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await fetchBacktest(selectedTicker, startDate, endDate);
            setData(result);
        } catch (err) {
            setError(err.message || 'Failed to run backtest.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.pageContainer}>
            <header className={styles.header}>
                <h1 className={styles.headerTitle}>Strategy Backtester</h1>
                <p className={styles.headerSubtitle}>
                    Simulate historical performance of the Trend + Momentum strategy.
                </p>
            </header>

            <div className={styles.controlsParams}>
                <TickerSelector
                    selectedTicker={selectedTicker}
                    onChange={setSelectedTicker}
                />

                <div className={styles.inputGroup}>
                    <label className={styles.inputLabel}>Start Date</label>
                    <input
                        type="date"
                        className={styles.dateInput}
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                    />
                </div>

                <div className={styles.inputGroup}>
                    <label className={styles.inputLabel}>End Date</label>
                    <input
                        type="date"
                        className={styles.dateInput}
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                    />
                </div>

                <button
                    className={styles.runButton}
                    onClick={handleRunBacktest}
                    disabled={loading}
                >
                    {loading ? 'Running...' : 'Run Backtest'}
                </button>
            </div>

            {error && <div className={styles.errorBanner}>{error}</div>}

            {loading && (
                <div className={styles.loadingState}>
                    <div className={styles.spinner}></div>
                    <span>Processing historical data...</span>
                </div>
            )}

            {!loading && data && (
                <>
                    <div className={styles.metricsGrid}>
                        <MetricCard
                            label="CAGR"
                            value={`${data.metrics['CAGR_%']}%`}
                            icon={TrendingUp}
                            isPositive={data.metrics['CAGR_%'] > 0}
                        />
                        <MetricCard
                            label="Sharpe Ratio"
                            value={data.metrics.Sharpe}
                            icon={Activity}
                            isPositive={data.metrics.Sharpe > 1}
                        />
                        <MetricCard
                            label="Max Drawdown"
                            value={`${data.metrics['Max_Drawdown_%']}%`}
                            icon={AlertTriangle}
                            isPositive={false} // Drawdown is always "risk"
                        />
                        <MetricCard
                            label="Total Return"
                            value={`${data.metrics['total_return_%']}%`}
                            icon={DollarSign}
                            isPositive={data.metrics['total_return_%'] > 0}
                        />
                        <MetricCard
                            label="Total Trades"
                            value={data.metrics.num_trades}
                            icon={Info}
                        />
                    </div>

                    <div className={styles.equitySection}>
                        <EquityChart data={data.equity_curve} />
                    </div>

                    <div className={styles.explanationSection}>
                        <h3 className={styles.explanationTitle}>Metric Definitions & Calculations</h3>
                        <div className={styles.explanationGrid}>
                            <div className={styles.explanationItem}>
                                <h4>CAGR</h4>
                                <p>Compound Annual Growth Rate represents the mean annual growth rate of the investment.</p>
                                <pre className={styles.codeBlock}>
                                    {`cagr = (equity.iloc[-1]) ** (252 / len(df)) - 1`}
                                </pre>
                            </div>
                            <div className={styles.explanationItem}>
                                <h4>Sharpe Ratio</h4>
                                <p>A measure of risk-adjusted return. Higher values indicate better returns for the same unit of risk.</p>
                                <pre className={styles.codeBlock}>
                                    {`std = strategy_returns.std()
sharpe = np.sqrt(252) * strategy_returns.mean() / std`}
                                </pre>
                            </div>
                            <div className={styles.explanationItem}>
                                <h4>Max Drawdown</h4>
                                <p>The maximum observed loss from a peak to a trough of the portfolio, before a new peak is attained.</p>
                                <pre className={styles.codeBlock}>
                                    {`equity = df["Equity"]
max_dd = ((equity.cummax() - equity) / equity.cummax()).max()`}
                                </pre>
                            </div>
                            <div className={styles.explanationItem}>
                                <h4>Total Return</h4>
                                <p>The absolute percentage change in equity over the entire backtest period.</p>
                                <pre className={styles.codeBlock}>
                                    {`total_return = equity.iloc[-1] - 1`}
                                </pre>
                            </div>
                            <div className={styles.explanationItem}>
                                <h4>Trade Count</h4>
                                <p>The total number of completed round-trip trades executed during the period.</p>
                                <pre className={styles.codeBlock}>
                                    {`num_trades = int(df["Trade"].sum() / 2)`}
                                </pre>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

const MetricCard = ({ label, value, icon: Icon, isPositive }) => {
    return (
        <div className={styles.metricCard}>
            <div className={styles.metricLabel}>
                {Icon && <Icon size={16} />}
                {label}
            </div>
            <div className={clsx(
                styles.metricValue,
                isPositive === true && styles.positive,
                isPositive === false && styles.negative
            )}>
                {value}
            </div>
        </div>
    );
};

export default BacktestPage;
