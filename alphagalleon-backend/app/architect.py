import json
import google.generativeai as genai
from typing import List
from .architect_schema import UserDNA, ModelPortfolio
import os

class Architect:
    def __init__(self):
        if "GOOGLE_API_KEY" in os.environ:
             genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
             self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
             print("Warning: GOOGLE_API_KEY not found. Architect will run in mock mode if needed.")
             self.model = None

    def construct_portfolio(self, user: UserDNA) -> ModelPortfolio:
        # Allow local/mock construction when model is not configured
        if not self.model:
            # Simple rule-based allocation depending on risk appetite
            risk = user.risk_appetite.lower()
            if risk == "aggressive":
                allocations = [
                    {"asset_class": "Equity", "sub_category": "Large Cap", "percentage": 70.0, "rationale": "High growth focus", "suggested_instruments": ["Nifty 50 ETF", "Select Growth Stocks"]},
                    {"asset_class": "Debt", "sub_category": "Corporate Bond", "percentage": 20.0, "rationale": "Stability", "suggested_instruments": ["Short Term Corp Bond Fund"]},
                    {"asset_class": "Cash", "sub_category": "Liquid", "percentage": 10.0, "rationale": "Dry powder", "suggested_instruments": ["Liquid ETF"]}
                ]
            elif risk == "conservative":
                allocations = [
                    {"asset_class": "Debt", "sub_category": "G-Sec", "percentage": 60.0, "rationale": "Capital preservation", "suggested_instruments": ["Gilt Fund"]},
                    {"asset_class": "Equity", "sub_category": "Large Cap", "percentage": 25.0, "rationale": "Selective equity exposure", "suggested_instruments": ["Nifty 50 ETF"]},
                    {"asset_class": "Cash", "sub_category": "Liquid", "percentage": 15.0, "rationale": "Liquidity", "suggested_instruments": ["Liquid ETF"]}
                ]
            else:
                allocations = [
                    {"asset_class": "Equity", "sub_category": "Large Cap", "percentage": 50.0, "rationale": "Balanced growth", "suggested_instruments": ["Nifty 50 ETF"]},
                    {"asset_class": "Equity", "sub_category": "Mid Cap", "percentage": 20.0, "rationale": "Growth tilt", "suggested_instruments": ["Midcap Fund"]},
                    {"asset_class": "Debt", "sub_category": "Corporate Bond", "percentage": 20.0, "rationale": "Stability", "suggested_instruments": ["Short Term Corp Bond Fund"]},
                    {"asset_class": "Cash", "sub_category": "Liquid", "percentage": 10.0, "rationale": "Liquidity", "suggested_instruments": ["Liquid ETF"]}
                ]

            return ModelPortfolio(
                strategy_name=("Aggressive Growth" if risk == "aggressive" else "Conservative Anchor" if risk == "conservative" else "Balanced Builder"),
                description="Auto-generated mock portfolio (no GOOGLE_API_KEY).",
                allocations=allocations,
                expected_cagr="8-12%",
                max_drawdown="10-20%",
                rebalance_frequency="Annually"
            )
        
        prompt = f"""
        You are AlphaGalleon's 'Architect' - an expert wealth manager who builds personalized, institutional-grade portfolios.
        
        Design a Model Portfolio for this user:
        - Age: {user.age}
        - Risk Appetite: {user.risk_appetite.upper()}
        - Capital: ₹{user.capital_amount:,.2f}
        - Investment Horizon: {user.investment_horizon}
        - Goals: {user.goals}
        
        Provide a detailed asset allocation strategy.
        Focus on Indian markets (NSE/BSE). Recommend specific instrument categories (e.g., Nifty 50 ETF, Corporate Bond Fund) but you can also name specific high-quality stocks if appropriate for the risk level.
        
        Output strictly in JSON format matching this schema:
        {{
            "strategy_name": "Name of the strategy (e.g., 'Aggressive Growth Builder')",
            "description": "One sentence description",
            "allocations": [
                {{
                    "asset_class": "Equity" | "Debt" | "Gold" | "Cash",
                    "sub_category": "Large Cap" | "Mid Cap" | "Small Cap" | "G-Sec" | "Liquid",
                    "percentage": 25.5,
                    "rationale": "Why this allocation?",
                    "suggested_instruments": ["HDFC Nifty 50 ETF", "SBI Bluechip Fund"]
                }}
            ],
            "expected_cagr": "12-14%",
            "max_drawdown": "15-20%",
            "rebalance_frequency": "Quarterly" | "Annually"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            raw_json = response.text
            parsed = json.loads(raw_json)
            
            return ModelPortfolio(**parsed)
        except Exception as e:
            print(f"Error constructing portfolio: {e}")
            raise e
