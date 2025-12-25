# src/models/predict_with_confidence.py
import os
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count())

from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from src.config.tickers import TICKERS

FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/labels")


def load_data(ticker):
    X = pd.read_csv(FEATURE_DIR / f"{ticker}_features.csv", index_col=0)
    y = pd.read_csv(LABEL_DIR / f"{ticker}_labels.csv", index_col=0)["label"]

    X.index = pd.to_datetime(X.index, errors="coerce")
    y.index = pd.to_datetime(y.index, errors="coerce")

    X = X[~X.index.isna()]
    y = y[~y.index.isna()]

    common_idx = X.index.intersection(y.index)
    df = X.loc[common_idx].copy()
    df["label"] = y.loc[common_idx]

    return df


def main(conf_threshold=0.65):
    for ticker in TICKERS:
        print(f"\n===== {ticker} =====")

        df = load_data(ticker)
        split = int(len(df) * 0.7)

        train = df.iloc[:split]
        test = df.iloc[split:]

        X_train = train.drop(columns="label")
        y_train = train["label"]

        X_test = test.drop(columns="label")
        y_test = test["label"]

        model = HistGradientBoostingClassifier(
            max_depth=6,
            learning_rate=0.05,
            max_iter=300,
            random_state=42
        )

        model.fit(X_train, y_train)

        probs = model.predict_proba(X_test)
        preds = model.predict(X_test)

        confidence = probs.max(axis=1)

        result = pd.DataFrame({
            "true_label": y_test.values,
            "pred_label": preds,
            "confidence": confidence
        }, index=y_test.index)

        # Phase 7.1 — Trend regime filter
        confident = result[result["confidence"] >= conf_threshold]

        trend_mask = (
            X_test.loc[confident.index, "trend_alignment"].abs() >= 0.5
        )
        confident = confident.loc[trend_mask]


        # Phase 7.2 — Volatility regime filter
        vol_mask = (
            X_test.loc[confident.index, "atr_percentile"].between(0.2, 0.8)
        )
        confident = confident.loc[vol_mask]


        # Directional-only evaluation
        directional = confident[confident["pred_label"] != 0]

        # drop neutral true outcomes
        directional = directional[directional["true_label"] != 0]

        if len(directional) == 0:
            print("No directional predictions at this threshold.")
            continue

        dir_acc = (
            np.sign(directional["true_label"]) ==
            np.sign(directional["pred_label"])
        ).mean()

        coverage = len(directional) / len(result)

        # print(f"Coverage (directional): {coverage:.2%}")


        print(f"Confidence threshold: {conf_threshold}")
        print(f"Trend filter: trend_alignment >= 0.5")
        print(f"Directional Coverage: {coverage:.2%}")
        print(f"Directional accuracy: {dir_acc:.2%}")
        # print(f"Accuracy (confident only): {dir_acc:.2%}")


if __name__ == "__main__":
    main()
