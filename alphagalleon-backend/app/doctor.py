import json
import google.generativeai as genai
from typing import List
from app.doctor_schema import PortfolioItem, PortfolioDiagnosis
import os

class Doctor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
             genai.configure(api_key=api_key)
             self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
             print("Warning: GOOGLE_API_KEY not found. Doctor will run in mock mode if needed.")
             self.model = None

    def diagnose_portfolio(self, portfolio: List[PortfolioItem], risk_appetite: str = "moderate") -> PortfolioDiagnosis:
        # If no model available, return a simple deterministic diagnosis so tools can function offline
        if not self.model:
            # Basic heuristics
            overall: int = 70
            risk = risk_appetite.lower()
            diversification = "Reasonable diversification" if len(portfolio) > 2 else "Concentrated holdings"
            sector_exposure = []
            red = []
            green = []
            fixes = []
            for item in portfolio:
                # collect pseudo sector exposures from ticker naming heuristics (not perfect)
                if ":" in item.ticker:
                    sector_exposure.append(item.ticker.split(":")[0])
                else:
                    sector_exposure.append("General")
                if item.allocation_percent > 40:
                    red.append(f"High allocation to {item.ticker} ({item.allocation_percent}%)")
                    overall -= 10
                    fixes.append(f"Reduce exposure to {item.ticker} to balance risk")
                else:
                    green.append(f"Moderate allocation to {item.ticker}")

            return PortfolioDiagnosis(
                overall_health_score=max(0, min(100, overall)),
                risk_level=("high" if risk == "aggressive" else "moderate" if risk == "moderate" else "low"),
                diversification_verdict=diversification,
                sector_exposure=list(set(sector_exposure)),
                red_flags=red or ["No critical red flags detected"],
                green_flags=green or ["No significant green flags detected"],
                actionable_fixes=fixes or ["Consider rebalancing to reduce concentration"],
                projected_performance="Neutral"
            )
        
        # Format the portfolio for the prompt
        portfolio_str = "\n".join([
            f"- {item.ticker}: {item.allocation_percent}% (Buy: {item.avg_buy_price}, Current: {item.current_price})"
            for item in portfolio
        ])

        prompt = f"""
        You are AlphaGalleon's 'Doctor' - an expert portfolio manager who ruthlessly analyzes retail portfolios.
        
        Analyze this portfolio for a '{risk_appetite}' investor.
        Identify concentration risks, sector overlap, bad stocks, and missed opportunities.
        
        Portfolio:
        {portfolio_str}
        
        Output strictly in JSON format matching this schema:
        {{
            "overall_health_score": 0-100,
            "risk_level": "low" | "moderate" | "high" | "extreme",
            "diversification_verdict": "...",
            "sector_exposure": ["sector 1", "sector 2"],
            "red_flags": ["bad stock 1", "overexposed to sector X"],
            "green_flags": ["good stock 1", "balanced allocation"],
            "actionable_fixes": ["sell X", "buy Y", "reduce Z"],
            "projected_performance": "..."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            raw_json = response.text
            parsed = json.loads(raw_json)
            
            return PortfolioDiagnosis(**parsed)
        except Exception as e:
            print(f"Error diagnosing portfolio: {e}")
            raise e
