from fastapi import APIRouter, HTTPException
from src.backtesting.backtest_engine import Backtester
from datetime import datetime

router = APIRouter(prefix="/api/backtest")

@router.get("/{ticker}")
def run_backtest_endpoint(ticker: str, start_date: str = "2020-01-01", end_date: str = None):
    try:
        # Validate dates if needed, but Backtester handles basic strings.
        # Ensure ticker is uppercase
        ticker = ticker.upper()

        backtester = Backtester(ticker, start=start_date, end=end_date)
        backtester.load_data()
        backtester.generate_signals()
        backtester.run_backtest()
        
        results = backtester.results()
        
        # Extract equity curve for plotting
        # backtester.data is a DataFrame with "Equity" column
        df = backtester.data
        equity_curve = []
        if "Equity" in df.columns:
            # Drop NaNs which might appear before first signal
            valid_df = df[df["Equity"].notna()]
            equity_curve = [
                {"date": str(date).split(" ")[0], "equity": float(val)}
                for date, val in zip(valid_df.index, valid_df["Equity"])
            ]
            
        return {
            "metrics": results,
            "equity_curve": equity_curve
        }

    except ValueError as e:
        # Often raised by Backtester if no data or no aligned features
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
