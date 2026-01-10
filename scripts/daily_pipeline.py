"""
PTRE Daily Pipeline

This script orchestrates the nightly update cycle:
1. Fetch latest market data
2. Update feature history files
3. Retrain Trend & Momentum models
4. Push changes to GitHub (for deployment auto-redeploy)

For deployment on Render:
- Create a Cron Job with command: python -m scripts.daily_pipeline
- Schedule: 0 23 * * 1-5 (Mon-Fri at 11 PM UTC)
- Set environment variable GIT_PUSH_ENABLED=true
- Set environment variable GITHUB_TOKEN=<your_personal_access_token>
"""

import os
import subprocess
from datetime import datetime

from scripts.update_features import main as update_features
from scripts.retrain_models import main as retrain_models


def git_push_changes():
    """
    Commits and pushes updated model files to GitHub.
    Only runs if GIT_PUSH_ENABLED environment variable is set to 'true'.
    Requires GITHUB_TOKEN for authentication on Render.
    """
    if os.environ.get("GIT_PUSH_ENABLED", "").lower() != "true":
        print("\n⏭  Git push disabled (GIT_PUSH_ENABLED not set). Skipping.")
        return

    print("\nPushing updated models to GitHub...")

    try:
        # Configure git user (required in CI/CD environments)
        subprocess.run(["git", "config", "user.email", "pipeline@ptre.ai"], check=True)
        subprocess.run(["git", "config", "user.name", "PTRE Pipeline"], check=True)

        # Stage all changed files (models, features)
        subprocess.run(["git", "add", "."], check=True)

        # Commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Auto: Daily model update ({timestamp})"
        
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        
        if result.returncode != 0:  # There are staged changes
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push"], check=True)
            print("   ✔ Changes pushed successfully!")
        else:
            print("   ℹ No changes to commit. Models are up to date.")

    except subprocess.CalledProcessError as e:
        print(f"    Git push failed: {e}")
        # Don't raise - let the pipeline complete even if push fails


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  PTRE DAILY UPDATE & TRAIN PIPELINE")
    print("=" * 50 + "\n")

    # Step 1: Update feature history
    print("Step 1: Updating Features...")
    update_features()

    # Step 2: Retrain models
    print("\n Step 2: Retraining Models...")
    retrain_models()

    # Step 3: Push to GitHub (for deployment auto-redeploy)
    git_push_changes()

    print("\n" + "=" * 50)
    print("PTRE DAILY PIPELINE COMPLETE")
    print("=" * 50 + "\n")