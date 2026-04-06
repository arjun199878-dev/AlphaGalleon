from fastapi import APIRouter, HTTPException
from app.services.market_data import market_data_service
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter()

class StockPriceResponse(BaseModel):
    symbol: str
    lastPrice: Optional[float]
    change: Optional[float]
    pChange: Optional[float]
    companyName: Optional[str]
    lastUpdateTime: Optional[str]

class CompanyRatiosResponse(BaseModel):
    symbol: str
    ratios: Dict[str, str]

@router.get("/price/{symbol}", response_model=Optional[StockPriceResponse])
async def get_stock_price(symbol: str):
    """
    Fetches real-time price data from NSE for a given symbol.
    """
    data = market_data_service.get_stock_price(symbol)
    if not data:
        raise HTTPException(status_code=404, detail=f"Data for {symbol} not found or NSE service unavailable.")
    return data

@router.get("/fundamentals/{symbol}", response_model=Optional[CompanyRatiosResponse])
async def get_fundamentals(symbol: str):
    """
    Fetches fundamental ratios from Screener.in for a given symbol.
    """
    ratios = market_data_service.get_company_ratios(symbol)
    if not ratios:
        raise HTTPException(status_code=404, detail=f"Fundamentals for {symbol} not found.")
    return {"symbol": symbol, "ratios": ratios}
