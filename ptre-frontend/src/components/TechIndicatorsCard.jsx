import React, { useMemo } from 'react';
import clsx from 'clsx';
import { calculateSMA, calculateEMA, calculateRSI, calculateMACD, calculateATR } from '../utils/indicators';
import styles from './TechIndicatorsCard.module.css';

const TechIndicatorsCard = ({ prices }) => {
    // We'll use the last available price point for the summary
    const indicators = useMemo(() => {
        if (!prices || prices.length === 0) return null;

        const sma20 = calculateSMA(prices, 20);
        const sma50 = calculateSMA(prices, 50);
        const ema20 = calculateEMA(prices, 20);
        const rsi14 = calculateRSI(prices, 14);
        const macd = calculateMACD(prices);
        const atr14 = calculateATR(prices, 14);

        // Get latest values (handling potential nulls)
        const lastIndex = prices.length - 1;

        const lastPrice = prices[lastIndex].close;
        const lastSMA20 = sma20[lastIndex]?.value;
        const lastSMA50 = sma50[lastIndex]?.value;
        const lastEMA20 = ema20[lastIndex]?.value;
        const lastRSI = rsi14[lastIndex]?.value;
        const lastMACD = macd[lastIndex]; // object {macd, signal, histogram}
        const lastATR = atr14[lastIndex]?.value;

        return { lastPrice, lastSMA20, lastSMA50, lastEMA20, lastRSI, lastMACD, lastATR };
    }, [prices]);

    if (!indicators) return null;

    const { lastPrice, lastSMA20, lastSMA50, lastEMA20, lastRSI, lastMACD, lastATR } = indicators;

    const getRSIColor = (val) => {
        if (val > 70) return styles.bearish; // Overbought
        if (val < 30) return styles.bullish; // Oversold
        return styles.neutral;
    }

    // MACD Color: Bullish if Histogram > 0
    const getMACDColor = (hist) => hist > 0 ? styles.bullish : styles.bearish;

    return (
        <div className={styles.card}>
            <h3 className={styles.title}>Technical Indicators (Live)</h3>

            <div className={styles.grid}>
                <div className={styles.item}>
                    <span className={styles.label}>RSI (14)</span>
                    <span className={clsx(styles.value, getRSIColor(lastRSI))}>
                        {lastRSI ? lastRSI.toFixed(2) : 'N/A'}
                    </span>
                </div>
                <div className={styles.item}>
                    <span className={styles.label}>SMA (20)</span>
                    <span className={styles.value}>
                        ${lastSMA20 ? lastSMA20.toFixed(2) : 'N/A'}
                    </span>
                </div>

                <div className={styles.item}>
                    <span className={styles.label}>MACD (12,26,9)</span>
                    <span className={clsx(styles.value, getMACDColor(lastMACD?.histogram))}>
                        {lastMACD?.histogram ? lastMACD.histogram.toFixed(2) : 'N/A'}
                    </span>
                </div>
                <div className={styles.item}>
                    <span className={styles.label}>EMA (20)</span>
                    <span className={styles.value}>
                        ${lastEMA20 ? lastEMA20.toFixed(2) : 'N/A'}
                    </span>
                </div>

                <div className={styles.item}>
                    <span className={styles.label}>ATR (14)</span>
                    <span className={styles.value}>
                        {lastATR ? lastATR.toFixed(2) : 'N/A'}
                    </span>
                </div>
                <div className={styles.item}>
                    <span className={styles.label}>SMA (50)</span>
                    <span className={styles.value}>
                        ${lastSMA50 ? lastSMA50.toFixed(2) : 'N/A'}
                    </span>
                </div>
            </div>

            <div className={styles.context}>
                <p>Price stands {lastPrice > lastSMA50 ? 'above' : 'below'} the 50-day average, suggesting {lastPrice > lastSMA50 ? 'macro uptrend' : 'macro downtrend'}.</p>
            </div>
        </div>
    );
};

export default TechIndicatorsCard;
