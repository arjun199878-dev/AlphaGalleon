from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Enums ---

class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"

class InvestmentHorizon(str, Enum):
    SHORT_TERM = "short_term" # < 1 year
    MEDIUM_TERM = "medium_term" # 1-3 years
    LONG_TERM = "long_term" # > 3 years

class Sentiment(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class Recommendation(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    AVOID = "avoid"

# --- Core Models ---

class Ticker(BaseModel):
    symbol: str
    name: str
    sector: str
    current_price: float
    market_cap: float
    pe_ratio: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.now)

class FundamentalData(BaseModel):
    """Raw financial data for The Brain to digest."""
    ticker: Ticker
    revenue_growth_3y: Optional[float] = None
    profit_growth_3y: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    promoter_holding: Optional[float] = None
    recent_news_summary: Optional[str] = None

# --- User DNA (Personalization) ---

class UserProfile(BaseModel):
    user_id: str
    name: str
    risk_profile: RiskProfile
    capital_available: float
    investment_horizon: InvestmentHorizon
    preferred_sectors: List[str] = []
    avoid_sectors: List[str] = []

# --- The Brain Output (Investment Memo) ---

class InvestmentMemo(BaseModel):
    ticker_symbol: str
    generated_at: datetime = Field(default_factory=datetime.now)
    recommendation: Recommendation
    confidence_score: int = Field(..., ge=0, le=100, description="0-100 confidence level")
    
    thesis_summary: str = Field(..., description="One paragraph executive summary")
    
    bull_case: List[str] = Field(..., description="Key reasons to buy")
    bear_case: List[str] = Field(..., description="Key risks/reasons to sell")
    
    catalysts: List[str] = Field(..., description="Upcoming events that could move the stock")
    
    valuation_verdict: str = Field(..., description="Is it cheap, fair, or expensive?")
    
    sources: List[str] = []

# --- The Intelligence Output (Portfolio) ---

class PortfolioAllocation(BaseModel):
    ticker_symbol: str
    allocation_percentage: float
    rationale: str

class PortfolioConstruction(BaseModel):
    user_id: str
    total_capital: float
    allocations: List[PortfolioAllocation]
    strategy_name: str
    expected_return_cagr: Optional[float] = None
    max_drawdown_risk: Optional[float] = None
