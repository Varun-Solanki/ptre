import React from 'react';
import clsx from 'clsx';
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';
import styles from './SignalCard.module.css';

const SignalCard = ({ signal, confidence }) => {
    const isBullish = signal === 'Bullish';
    const isBearish = signal === 'Bearish';
    const isNeutral = signal === 'Neutral';

    return (
        <div className={styles.card}>
            <h3 className={styles.title}>Final Signal</h3>

            <div className={styles.signalContainer}>
                {isBullish && <TrendingUp className={styles.iconBullish} size={32} />}
                {isBearish && <TrendingDown className={styles.iconBearish} size={32} />}
                {isNeutral && <Minus className={styles.iconNeutral} size={32} />}

                <span className={clsx(styles.signalText, {
                    [styles.bullish]: isBullish,
                    [styles.bearish]: isBearish,
                    [styles.neutral]: isNeutral,
                })}>
                    {signal}
                </span>
            </div>

            <div className={styles.confidenceSection}>
                <div className={styles.confidenceLabel}>
                    <div className={styles.labelWithIcon}>
                        <span>Confidence</span>
                        <div className={styles.tooltipContainer} title={`PTRE confidence is calibrated. A value of ${confidence.toFixed(0)}% historically corresponds to approximately ${confidence.toFixed(0)}% directional accuracy.`}>
                            <Info size={14} className={styles.infoIcon} />
                        </div>
                    </div>
                    <span>{confidence.toFixed(1)}%</span>
                </div>
                <div className={styles.progressBarBackground}>
                    <div
                        className={clsx(styles.progressBarFill, {
                            [styles.fillBullish]: isBullish,
                            [styles.fillBearish]: isBearish,
                            [styles.fillNeutral]: isNeutral,
                        })}
                        style={{ width: `${confidence}%` }}
                    />
                </div>
            </div>
        </div>
    );
};

export default SignalCard;
