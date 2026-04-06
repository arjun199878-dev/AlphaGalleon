from fastapi import APIRouter, HTTPException
from app.services.gemini import gemini_service
from app.services.analysis import analysis_service
from app.services.portfolio import portfolio_service
from app.services.doctor import doctor_service
from app.services.backtest import backtest_service
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

class MemoRequest(BaseModel):
    symbol: str

class PortfolioRequest(BaseModel):
    capital: float
    risk_profile: str
    time_horizon: str

class DiagnosisRequest(BaseModel):
    holdings: List[Dict[str, Any]] # e.g. [{"symbol": "TATASTEEL", "quantity": 100}]

class BacktestRequest(BaseModel):
    holdings: List[Dict[str, Any]] # e.g. [{"symbol": "RELIANCE", "allocation": 0.5}]
    duration_years: int = 1

@router.post("/generate")
async def generate_text(request: PromptRequest):
    """
    Direct interface to The Brain (Gemini 2.5 Flash).
    """
    response = await gemini_service.generate_content(request.prompt)
    return {"response": response}

@router.post("/memo")
async def generate_memo(request: MemoRequest):
    """
    Generates a full Investment Memo (Data + Analysis).
    """
    result = await analysis_service.generate_investment_memo(request.symbol)
    if "error" in result and "market_data" not in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/portfolio")
async def generate_portfolio(request: PortfolioRequest):
    """
    Architects an investment portfolio.
    """
    result = await portfolio_service.generate_portfolio(request.capital, request.risk_profile, request.time_horizon)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/diagnose")
async def diagnose_portfolio(request: DiagnosisRequest):
    """
    Analyses an existing portfolio for risks.
    """
    result = await doctor_service.diagnose_portfolio(request.holdings)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/backtest")
async def run_backtest(request: BacktestRequest):
    """
    Time Travel: Backtests a portfolio against historical data.
    """
    result = await backtest_service.run_backtest(request.holdings, request.duration_years)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/stats")
async def get_brain_stats():
    """
    Returns system stats for the Admin Dashboard.
    """
    # In a real app, fetch these from DB or monitoring service
    return [
        {"label": "Brain Uptime", "value": "42h 12m", "trend": "up"},
        {"label": "Requests / Hr", "value": "1,245", "trend": "up"},
        {"label": "Active Sessions", "value": "8", "trend": "down"}
    ]
