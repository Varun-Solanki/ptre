import React from 'react';
import { ChevronDown } from 'lucide-react';
import styles from './TickerSelector.module.css';

const TICKERS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'UNH', 'XOM'];

const TickerSelector = ({ selectedTicker, onChange }) => {
    return (
        <div className={styles.container}>
            <label className={styles.label} htmlFor="ticker-select">Instrument</label>
            <div className={styles.selectWrapper}>
                <select
                    id="ticker-select"
                    className={styles.select}
                    value={selectedTicker}
                    onChange={(e) => onChange(e.target.value)}
                >
                    {TICKERS.map((ticker) => (
                        <option key={ticker} value={ticker}>
                            {ticker}
                        </option>
                    ))}
                </select>
                <ChevronDown className={styles.icon} size={20} />
            </div>
        </div>
    );
};

export default TickerSelector;
