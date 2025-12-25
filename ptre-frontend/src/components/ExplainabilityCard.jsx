import React, { useMemo } from 'react';
import { BrainCircuit } from 'lucide-react';
import styles from './ExplainabilityCard.module.css';

const ExplainabilityCard = ({ data }) => {
    // Logic to generate the explanation text
    const explanation = useMemo(() => {
        if (!data) return '';

        const { trend, momentum, risk, agreement, final_signal, final_confidence } = data;
        const trendDir = trend.direction === 'Bullish' ? 'Bullish' : 'Bearish';
        const momDir = momentum.direction === 'Bullish' ? 'Bullish' : 'Bearish';

        const lines = [];

        // Line 1: Trend
        lines.push(`Trend model indicates ${trendDir} regime (${trend.confidence.toFixed(2)} confidence).`);

        // Line 2: Momentum
        if (agreement) {
            lines.push(`Momentum confirms ${momDir === 'Bullish' ? 'upward' : 'downward'} pressure (${momentum.confidence.toFixed(2)} confidence).`);
        } else {
            lines.push(`Momentum ${momDir} vs Trend ${trendDir} indicates regime conflict.`);
        }

        // Line 3: Risk/Penalty
        if (!agreement) {
            lines.push(`Confidence reduced by disagreement penalty.`);
        }
        lines.push(`Volatility classified as ${risk.volatility}; ${risk.volatility === 'Low' ? 'safe for sizing' : risk.volatility === 'High' ? 'neutral drift risk elevated' : 'standard sizing'}.`);

        // Line 4: Final
        lines.push(`Models are in ${agreement ? 'Agreement' : 'Conflict'}. Ensemble probability = ${final_confidence.toFixed(0)}% ${final_signal}.`);

        return lines.join('\n');
    }, [data]);

    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <BrainCircuit size={18} className={styles.title} />
                <h3 className={styles.title}>Why this decision?</h3>
            </div>
            <div className={styles.content}>
                {explanation}
            </div>
        </div>
    );
};

export default ExplainabilityCard;
