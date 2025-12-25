import React from 'react';
import clsx from 'clsx';
import { ArrowUpRight, ArrowDownRight, AlertTriangle, Minus } from 'lucide-react';
import styles from './ModelCard.module.css';

const ModelCard = ({ title, direction, confidence, horizon, agreement }) => {
    const isBullish = direction === 'Bullish';
    const isBearish = direction === 'Bearish';
    const isNeutral = direction === 'Neutral';

    // Badge content logic
    const AgreementBadge = () => (
        <span className={clsx(styles.badge, styles.badgeSuccess)}>
            Agreement
        </span>
    );

    const ConflictBadge = () => (
        <span className={clsx(styles.badge, styles.badgeWarning)}>
            <AlertTriangle size={12} style={{ marginRight: 4 }} /> Conflict
        </span>
    );

    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <h3 className={styles.title}>{title}</h3>
                {agreement !== undefined && (
                    <div title={agreement ? "Trend and Momentum models agree in direction." : "Models disagree; confidence penalty applied."}>
                        {agreement ? <AgreementBadge /> : <ConflictBadge />}
                    </div>
                )}
            </div>

            <div className={styles.content}>
                <div className={styles.directionRow}>
                    <span className={clsx(styles.direction, {
                        [styles.textBullish]: isBullish,
                        [styles.textBearish]: isBearish,
                        [styles.textNeutral]: isNeutral,
                    })}>
                        {direction}
                    </span>
                    {isBullish && <ArrowUpRight className={styles.textBullish} />}
                    {isBearish && <ArrowDownRight className={styles.textBearish} />}
                    {isNeutral && <Minus className={styles.textNeutral} />}
                </div>

                <div className={styles.metric}>
                    <span className={styles.label}>Confidence</span>
                    <span className={styles.value}>{(confidence * 100).toFixed(0)}%</span>
                </div>

                {horizon && (
                    <div className={styles.metric}>
                        <span className={styles.label}>Horizon</span>
                        <span className={styles.value}>{horizon} Days</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ModelCard;
