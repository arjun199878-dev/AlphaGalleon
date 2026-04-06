from typing import List
from pydantic import BaseModel, Field

# --- Architect Models ---

class UserDNA(BaseModel):
    age: int
    investment_horizon: str # "short_term", "medium_term", "long_term"
    risk_appetite: str # "conservative", "moderate", "aggressive"
    capital_amount: float
    goals: str # e.g., "Retirement", "Buy a House", "Wealth Creation"

class Allocation(BaseModel):
    asset_class: str # Equity, Debt, Gold, Cash
    sub_category: str # Large Cap, Mid Cap, Small Cap, Corporate Bond...
    percentage: float
    rationale: str
    suggested_instruments: List[str] # Specific ETFs or Stocks

class ModelPortfolio(BaseModel):
    strategy_name: str
    description: str
    allocations: List[Allocation]
    expected_cagr: str
    max_drawdown: str
    rebalance_frequency: str
