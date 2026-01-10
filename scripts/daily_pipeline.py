from scripts.update_features import main as update_features
from scripts.retrain_models import main as retrain_models

if __name__ == "__main__":
    print("\n===== PTRE DAILY UPDATE & TRAIN PIPELINE START=====\n")

    # print("Step 1: Updating Features")
    update_features()

    # print("\nStep 2: Retraining Models")
    retrain_models()

    print("\n===== PTRE MODELS UPDATED SUCCESSFULLY =====\n")