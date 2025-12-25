/**
 * Calculates Simple Moving Average (SMA)
 * @param {Array<number>} prices - Array of prices
 * @param {number} period - Window size
 * @returns {Array<{value: number, time: string} | null>}
 */
export const calculateSMA = (data, period) => {
    if (!data || data.length < period) return [];

    let result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push({ date: data[i].date, value: null });
            continue;
        }

        const slice = data.slice(i - period + 1, i + 1);
        const sum = slice.reduce((a, b) => a + b.close, 0);
        result.push({ date: data[i].date, value: sum / period });
    }
    return result;
};

/**
 * Calculates Exponential Moving Average (EMA)
 * @param {Array<number>} prices 
 * @param {number} period 
 * @returns {Array<{value: number, time: string} | null>}
 */
export const calculateEMA = (data, period) => {
    if (!data || data.length === 0) return [];

    const k = 2 / (period + 1);
    let result = [];
    let ema = data[0].close; // Start with first price as seed

    result.push({ date: data[0].date, value: ema });

    for (let i = 1; i < data.length; i++) {
        ema = (data[i].close * k) + (ema * (1 - k));
        result.push({ date: data[i].date, value: ema });
    }
    return result;
};

/**
 * Calculates Relative Strength Index (RSI)
 * @param {Array<number>} prices 
 * @param {number} period (default 14)
 * @returns {Array<{value: number, time: string} | null>}
 */
export const calculateRSI = (data, period = 14) => {
    if (!data || data.length < period + 1) return [];

    let result = [];
    let gains = [];
    let losses = [];

    // First RSI calculation needs previous period averages
    for (let i = 1; i < data.length; i++) {
        const change = data[i].close - data[i - 1].close;
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
    }

    let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
    let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;

    // Fill initial nulls
    for (let i = 0; i < period; i++) {
        result.push({ date: data[i].date, value: null });
    }

    // First valid point
    let rs = avgGain / avgLoss;
    let rsi = 100 - (100 / (1 + rs));
    result.push({ date: data[period].date, value: rsi });

    // Subsequent points using smoothed averages
    for (let i = period + 1; i < data.length; i++) {
        const change = data[i].close - data[i - 1].close;
        const gain = change > 0 ? change : 0;
        const loss = change < 0 ? Math.abs(change) : 0;

        avgGain = ((avgGain * (period - 1)) + gain) / period;
        avgLoss = ((avgLoss * (period - 1)) + loss) / period;

        rs = avgGain / avgLoss;
        rsi = 100 - (100 / (1 + rs));
        result.push({ date: data[i].date, value: rsi });
    }

    return result;
};

/**
 * Calculates MACD (12, 26, 9)
 * @param {Array<number>} data 
 * @returns {Array<{macd: number, signal: number, histogram: number, time: string} | null>}
 */
export const calculateMACD = (data) => {
    if (!data || data.length < 26) return [];

    const ema12 = calculateEMA(data, 12);
    const ema26 = calculateEMA(data, 26);

    let macdLine = [];

    // Align lengths - MACD starts when slow EMA starts
    for (let i = 0; i < data.length; i++) {
        if (ema12[i].value !== null && ema26[i].value !== null) {
            macdLine.push({ date: data[i].date, value: ema12[i].value - ema26[i].value });
        } else {
            macdLine.push({ date: data[i].date, value: null });
        }
    }

    // Signal line is EMA(9) of MACD line
    // We need to extract just values for EMA calc, but our EMA function expects objects
    // So we'll repurpose the list structure
    const signalLineData = macdLine.map(d => ({ date: d.date, close: d.value || 0 }));
    // ^ Note: This is a hacky simplification for `calculateEMA` which expects {close}. 
    // But since `calculateEMA` handles nulls by taking first valid as seed, we need to be careful.
    // Better strategy: Calculate Signal manually on the valid MACD slice to avoid 0-padding bias.

    // Simple correct approach for Signal Line:
    // 1. Get valid MACD values
    const validMacd = macdLine.filter(m => m.value !== null);
    if (validMacd.length === 0) return [];

    const signalEma = calculateEMA(validMacd.map(m => ({ date: m.date, close: m.value })), 9);

    // Map back to original timeline
    let result = [];
    let signalIdx = 0;

    for (let i = 0; i < data.length; i++) {
        const mVal = macdLine[i].value;
        let sVal = null;

        // Find matching signal value by date if available
        if (mVal !== null) {
            const matchingSig = signalEma.find(s => s.date === data[i].date);
            if (matchingSig) sVal = matchingSig.value;
        }

        result.push({
            date: data[i].date,
            macd: mVal,
            signal: sVal,
            histogram: (mVal !== null && sVal !== null) ? mVal - sVal : null
        });
    }

    return result;
};

/**
 * Calculates Average True Range (ATR)
 * @param {Array<number>} data 
 * @param {number} period (default 14)
 */
export const calculateATR = (data, period = 14) => {
    if (!data || data.length < period + 1) return [];

    let tr = [];
    // TR calculation: max(high-low, abs(high-prevClose), abs(low-prevClose))

    // First value is high-low
    tr.push({ date: data[0].date, value: data[0].high - data[0].low });

    for (let i = 1; i < data.length; i++) {
        const hl = data[i].high - data[i].low;
        const hpc = Math.abs(data[i].high - data[i - 1].close);
        const lpc = Math.abs(data[i].low - data[i - 1].close);
        tr.push({ date: data[i].date, value: Math.max(hl, hpc, lpc) });
    }

    // ATR is RMA (Running Moving Average) or Wilder's Smoothing of TR
    // Wilder's: ATR = ((Prev ATR * (n-1)) + Current TR) / n
    // Initial ATR is simple average of first n TRs

    let result = [];
    // Nulls for initial period
    for (let i = 0; i < period; i++) result.push({ date: data[i].date, value: null });

    // First ATR
    const firstATR = tr.slice(0, period).reduce((a, b) => a + b.value, 0) / period;
    result.push({ date: data[period].date, value: firstATR });

    let prevATR = firstATR;
    for (let i = period + 1; i < data.length; i++) {
        const currentTR = tr[i].value;
        const currentATR = ((prevATR * (period - 1)) + currentTR) / period;
        result.push({ date: data[i].date, value: currentATR });
        prevATR = currentATR;
    }

    return result;
};
