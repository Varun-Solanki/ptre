# This file will show that What are the global assumptions of PTRE
# i.e HOW WE ANALYZE
# What will go here

# Examples:
# Historical start date
# Prediction horizon (10 days)
# Thresholds for bullish / bearish
# Confidence cutoffs
# Risk caps
# These are policy decisions, not code logic.

"""
Global configuration settings for PTRE.
These values define the core assumptions of the system.
Changing them changes the behavior of the entire pipeline.
"""

# =====================
# Data settings
# =====================

START_DATE = "2015-01-01"
END_DATE = None  # None means "up to today"


# =====================
# Prediction settings
# =====================

# Prediction horizon in trading days
PREDICTION_HORIZON = 10


# =====================
# Label thresholds
# =====================

# Directional thresholds for 10-day forward return
BULLISH_THRESHOLD = 0.02    # +2%
BEARISH_THRESHOLD = -0.02   # -2%


# =====================
# Confidence & risk settings
# =====================

# Below this confidence → Neutral / no action
CONFIDENCE_DEADBAND_LOW = 0.45
CONFIDENCE_DEADBAND_HIGH = 0.55

# Hard cap on exposure (used later in risk engine)
MAX_EXPOSURE = 0.20   # 20% of capital
