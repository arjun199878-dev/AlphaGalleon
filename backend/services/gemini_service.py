import google.generativeai as genai
import os
import json

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            print("WARNING: GEMINI_API_KEY not set. AI Features will mock data.")
            self.model = None

    async def diagnose_portfolio(self, portfolio: dict):
        """Analyze portfolio risks (The Doctor)"""
        if not self.model:
            return {"score": 84, "alert": "Gemini API Key Missing"}

        prompt = f"""
        Act as an institutional risk manager. Analyze this portfolio:
        {json.dumps(portfolio)}
        
        Output JSON only:
        {{
            "health_score": (0-100),
            "critical_risk": "One sentence summary of biggest risk",
            "sector_exposure": {{ "Financials": "30%", ... }},
            "recommendation": "One actionable fix"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return {"error": str(e)}

    async def create_strategy(self, capital: float, risk: str, horizon: str):
        """Generate investment strategy (The Architect)"""
        if not self.model:
            return {"strategy": "High-Conviction Growth (Mock)", "cagr": "18-22%"}

        prompt = f"""
        Act as an investment banker. Create a portfolio for:
        Capital: ₹{capital}
        Risk: {risk}
        Horizon: {horizon}
        
        Output JSON only:
        {{
            "strategy_name": "Name (e.g., Aggressive Alpha)",
            "target_cagr": "XX-XX%",
            "allocation": [
                {{ "asset": "Small Cap Fund", "percent": "40%", "reason": "High alpha" }},
                ...
            ]
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return {"error": str(e)}
