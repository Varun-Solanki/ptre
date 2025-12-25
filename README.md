# PTRE: Predictive Trend & Risk Engine

**An Institutional-Grade Quantitative Trading Dashboard.**

![Main Dashboard](assets/readme-img-1.png)
*(Top: Dynamic Price History, Trend & Momentum Models, Signal Agreement Badges)*

![Dashboard Metrics](assets/readme-img-2.png)
*(Bottom: Technical Indicators, Explainability Engine, and Risk Analysis)*

---

## Overview

**PTRE** is a specialized financial analytics platform designed to detect high-probability market regimes. Unlike standard technical analysis tools, PTRE uses a **Dual-Model Ensemble** approach (Trend + Momentum) with a strict volatility-gating mechanism to generate signals with calibrated probabilities.

It answers three critical questions for any asset:
1.  **What is the Regime?** (Bullish / Bearish / Neutral)
2.  **How confident are we?** (Calibrated Probability %)
3.  **Is it safe to trade?** (Volatility Risk Score)

---

## Key Features

### Dual-Model Architecture
*   **Trend Model**: Using **Histogram-Based Gradient Boosting**, this model analyzes ~40 non-linear features (price action, gaps, volatility estimators) to determine the macro direction.
*   **Momentum Model**: A fast-twitch verification layer focusing on 11 velocity and volume-based features to confirm or reject the trend.

### Risk-First Design
*   **Ensemble Soft-Gating**: Signals require agreement. If models disagree (e.g., Bullish Trend vs Bearish Momentum), the system applies a **Confidence Penalty** and flags the signal as "Conflict".
*   **Neutral Zone Risk Map**: Automatically detects high-volatility "chop" zones where directional signals are unreliable.

### Institutional UI
*   **Dynamic Time-frame Filtering**: Client-side analysis of 1M, 3M, 6M, and 1Y data windows.
*   **Explainability Engine**: A dedicated panel that translates complex model probabilities into plain English (e.g., *"Trend confirms Bullish, but Volatility is High"*).
*   **Real-time Indicators**: Live calculation of RSI, SMA, EMA, MACD, and ATR.

---

## Technology Stack

### Frontend
*   **React** (Vite)
*   **CSS Modules** (Dark Theme Design System)
*   **Recharts** (Responsive Visualization)
*   **Lucide React** (Iconography)

### Backend
*   **Python** (FastAPI)
*   **Pandas & NumPy** (Vectorized Feature Engineering)
*   **Scikit-Learn** (HistGradientBoostingClassifier, Isotonic Regression)
*   **Joblib** (Model Persistence)

---

## Getting Started

### Prerequisites
*   Node.js (v16+)
*   Python (3.9+)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/ptre.git
    cd ptre
    ```

2.  **Backend Setup**
    ```bash
    # Create virtual environment
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run the Signal API
    uvicorn src.api.main:app --reload
    ```

3.  **Frontend Setup**
    ```bash
    cd ptre-frontend
    npm install
    npm run dev
    ```

4.  **Access**
    Open `http://localhost:5173` in your browser.

---

## Model Performance
*   **Target Accuracy**: >53% Directional Accuracy (Alpha threshold)
*   **Calibration**: Probabilities are harmonized using Isotonic Regression, ensuring that a "70% Confidence" score historically correlates with a 70% win rate.

---

*Private Research Project. Not Financial Advice.*
