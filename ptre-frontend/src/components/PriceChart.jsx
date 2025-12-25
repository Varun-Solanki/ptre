import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';
import styles from './PriceChart.module.css';

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className={styles.tooltip}>
                <p className={styles.tooltipDate}>{label}</p>
                <p className={styles.tooltipPrice}>
                    ${payload[0].value.toFixed(2)}
                </p>
            </div>
        );
    }
    return null;
};

const PriceChart = ({ data }) => {
    // Default to '1Y' (Max / Everything provided) as per user request
    const [range, setRange] = useState('1Y');

    // Filter data based on selected range
    const chartData = React.useMemo(() => {
        const prices = data?.prices || [];
        if (prices.length === 0) return [];

        // If '1Y', we show EVERYTHING the backend gave us.
        // This satisfies "takes whatever is given".
        if (range === '1Y') return prices;

        // For other ranges, we calculate the cutoff.
        const lastDate = new Date(prices[prices.length - 1].date);
        const cutoffDate = new Date(lastDate);

        if (range === '1M') {
            cutoffDate.setMonth(lastDate.getMonth() - 1);
        } else if (range === '3M') {
            cutoffDate.setMonth(lastDate.getMonth() - 3);
        } else if (range === '6M') {
            cutoffDate.setMonth(lastDate.getMonth() - 6);
        }

        return prices.filter(p => new Date(p.date) >= cutoffDate);
    }, [data, range]);

    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <h3 className={styles.title}>Price History</h3>
                <div className={styles.controls}>
                    {['1M', '3M', '6M', '1Y'].map((r) => (
                        <button
                            key={r}
                            className={clsx(styles.rangeButton, { [styles.activeRange]: range === r })}
                            onClick={() => setRange(r)}
                        >
                            {r}
                        </button>
                    ))}
                </div>
            </div>

            <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                        data={chartData}
                        margin={{ top: 10, right: 0, left: 0, bottom: 0 }}
                    >
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1F2933" />
                        <XAxis
                            dataKey="date"
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                            minTickGap={30}
                        />
                        <YAxis
                            domain={['auto', 'auto']}
                            orientation="right"
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={(val) => `$${val}`}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Area
                            type="monotone"
                            dataKey="close"
                            stroke="#3B82F6"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorPrice)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default PriceChart;
