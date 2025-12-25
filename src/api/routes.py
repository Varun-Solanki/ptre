from fastapi import APIRouter, HTTPException
from src.services.signal_service import generate_signal
from src.config.tickers import TICKERS

router = APIRouter(prefix="/api")

@router.get("/signal/{ticker}")
def get_signal(ticker: str):
    try:
        return generate_signal(ticker.upper())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Ticker not supported")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickers")
def get_tickers():
    return {
        "tickers": TICKERS
        }
