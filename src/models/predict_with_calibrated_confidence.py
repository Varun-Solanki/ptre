from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

from src.config.tickers import TICKERS

FEATURE_DIR = Path("data/processed/features")
LABEL_DIR = Path("data/processed/labels")

def load_data(ticker):
    X = pd.read_csv(FEATURE_DIR / f"{ticker}_features.csv", index_col=0)
    y = pd.read_csv(LABEL_DIR / f"{ticker}_labels.csv", index_col=0)["label"]

    idx = X.index.intersection(y.index)
    df = X.loc[idx].copy()
    df["label"] = y.loc[idx]

    return df.dropna()


def split_data(df):
    n = len(df)
    train_end = int(n * 0.5)
    calib_end = int(n * 0.7)

    train_df = df.iloc[:train_end]
    calib_df = df.iloc[train_end:calib_end]
    test_df  = df.iloc[calib_end:]

    return train_df, calib_df, test_df


def evaluate(ticker, conf_threshold=0.65, trend_threshold=0.5):
    print(f"\n===== {ticker} =====")

    df = load_data(ticker)

    # Optional trend filter (Phase 7)
    df = df[df["trend_alignment"] >= trend_threshold]

    train_df, calib_df, test_df = split_data(df)

    base_model = HistGradientBoostingClassifier(
        max_depth=6,
        learning_rate=0.05,
        max_iter=300,
        random_state=42
    )

    base_model.fit(
        train_df.drop(columns="label"),
        train_df["label"]
    )

    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=None
    )

    calibrated_model.fit(
        calib_df.drop(columns="label"),
        calib_df["label"]
    )

    probs = calibrated_model.predict_proba(
        test_df.drop(columns="label")
    )

    preds = probs.argmax(axis=1)
    confidence = probs.max(axis=1)

    result = pd.DataFrame({
        "true": test_df["label"].values,
        "pred": preds,
        "conf": confidence
    }, index=test_df.index)

    confident = result[result["conf"] >= conf_threshold]

    directional = confident[
        (confident["pred"] != 0) &
        (confident["true"] != 0)
    ]

    if len(directional) == 0:
        print("No confident directional samples.")
        return

    dir_acc = (
        np.sign(directional["pred"]) ==
        np.sign(directional["true"])
    ).mean()

    coverage = len(directional) / len(result)

    print(f"Confidence threshold: {conf_threshold}")
    print(f"Directional coverage: {coverage:.2%}")
    print(f"Directional accuracy: {dir_acc:.2%}")

def main():
    for ticker in TICKERS:
        evaluate(ticker)

if __name__ == "__main__":
    main()