from typing import List
from pydantic import BaseModel, Field

# --- Doctor Models ---

class PortfolioItem(BaseModel):
    ticker: str
    allocation_percent: float
    avg_buy_price: float
    current_price: float

class PortfolioDiagnosis(BaseModel):
    overall_health_score: int = Field(..., ge=0, le=100)
    risk_level: str
    
    diversification_verdict: str
    sector_exposure: List[str]
    
    red_flags: List[str] = Field(..., description="Critical risks like overexposure or bad stocks")
    green_flags: List[str] = Field(..., description="Good diversification or quality picks")
    
    actionable_fixes: List[str] = Field(..., description="What should the user change immediately?")
    
    projected_performance: str = Field(..., description="Bull/Bear outlook for this specific mix")
