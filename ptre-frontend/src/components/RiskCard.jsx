import React from 'react';
import clsx from 'clsx';
import { ShieldAlert } from 'lucide-react';
import styles from './RiskCard.module.css';

const RiskCard = ({ volatility, volatilityValue, riskScore }) => {
    const isHigh = volatility === 'High';
    const isModerate = volatility === 'Moderate';
    const isLow = volatility === 'Low';

    return (
        <div className={styles.card}>
            <h3 className={styles.title}>Risk Analysis</h3>

            <div className={styles.content}>
                <div className={styles.volatilitySection}>
                    <ShieldAlert
                        className={clsx(styles.icon, {
                            [styles.iconHigh]: isHigh,
                            [styles.iconModerate]: isModerate,
                            [styles.iconLow]: isLow,
                        })}
                        size={24}
                    />
                    <div>
                        <div className={styles.label}>Volatility</div>
                        <div className={clsx(styles.value, {
                            [styles.textHigh]: isHigh,
                            [styles.textModerate]: isModerate,
                            [styles.textLow]: isLow,
                        })}>
                            {volatility} ({(volatilityValue * 100).toFixed(1)}%)
                        </div>
                    </div>
                </div>

                <div className={styles.divider} />

                <div className={styles.riskScoreSection}>
                    <div className={styles.label}>Risk Score</div>
                    <div className={styles.riskValue}>{riskScore}/100</div>
                </div>
            </div>
        </div>
    );
};

export default RiskCard;
