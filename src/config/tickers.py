#This files will show that Which stocks does PTRE operate on

# i.e WHAT WE ANALYZE


"""
Stock universe configuration for PTRE.

We start with a small, liquid, large-cap US equity universe
to ensure clean data and stable behavior.

This list can be expanded later, but should remain fixed
during experiments for reproducibility.
"""

TICKERS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "NVDA",   # NVIDIA
    "AMZN",   # Amazon
    "META",   # Meta Platforms
    "GOOGL",  # Alphabet
    "TSLA",   # Tesla
    "JPM",    # JPMorgan Chase
    "UNH",    # UnitedHealth Group
    "XOM"     # Exxon Mobil
]
