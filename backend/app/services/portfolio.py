from typing import List, Dict, Any
from app.services.gemini import gemini_service
import json

class PortfolioService:
    """
    The Architect.
    Constructs optimized investment portfolios based on capital, risk, and goals.
    """

    async def generate_portfolio(self, capital: float, risk_profile: str, time_horizon: str) -> Dict[str, Any]:
        # 1. Construct the Prompt Context
        context = f"""
        ACT AS: AlphaGalleon Portfolio Architect (Institutional Grade).
        
        CLIENT PROFILE:
        - Capital: ₹{capital:,.2f}
        - Risk Tolerance: {risk_profile} (Low/Medium/High)
        - Time Horizon: {time_horizon}
        
        TASK:
        Design an optimal investment portfolio allocation for the Indian Market (NSE).
        Focus on asset allocation (Equity, Debt, Gold, Cash) and specific stock/sector recommendations.
        
        REQUIRED OUTPUT FORMAT (JSON):
        {{
            "strategy_name": "Name of the strategy (e.g., 'Aggressive Growth', 'Balanced Shield')",
            "allocation": {{
                "Equity": "percentage (e.g., '70%')",
                "Debt": "percentage",
                "Gold": "percentage",
                "Cash": "percentage"
            }},
            "rationale": "Brief explanation of why this mix suits the profile.",
            "recommended_sectors": ["Sector 1", "Sector 2", "Sector 3"],
            "top_picks": [
                {{ "symbol": "TATASTEEL", "reason": "Infrastructure growth play" }},
                {{ "symbol": "INFY", "reason": "Defensive IT play" }},
                {{ "symbol": "HDFCBANK", "reason": "Banking leader" }}
            ]
        }}
        
        Do not use markdown formatting in the JSON output. Return pure JSON.
        """

        # 2. Invoke The Brain
        print(f"Architecting portfolio for {risk_profile} profile...")
        response_text = await gemini_service.generate_content(context)

        # 3. Parse and Return
        try:
            # Clean up potential markdown code blocks from LLM
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            portfolio = json.loads(cleaned_text)
            
            return {
                "profile": {
                    "capital": capital,
                    "risk": risk_profile,
                    "horizon": time_horizon
                },
                "portfolio": portfolio
            }
        except json.JSONDecodeError:
            return {
                "error": "Failed to architect portfolio",
                "raw_response": response_text
            }

portfolio_service = PortfolioService()
