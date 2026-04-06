from typing import Dict, Any, Optional
from app.services.market_data import market_data_service
from app.services.gemini import gemini_service
import json

class AnalysisService:
    """
    The Intelligence Layer.
    Orchestrates data fetching and Gemini analysis to generate Investment Memos.
    """
    
    async def generate_investment_memo(self, symbol: str) -> Dict[str, Any]:
        # 1. Gather Intelligence (Parallelize if possible, sequential for now)
        print(f"Gathering intel for {symbol}...")
        price_data = market_data_service.get_stock_price(symbol)
        fundamental_data = market_data_service.get_company_ratios(symbol)
        
        if not price_data:
            return {"error": f"Could not fetch market data for {symbol}"}
            
        # 2. Construct the Prompt Context
        context = f"""
        ANALYZE THIS STOCK: {symbol}
        
        MARKET DATA:
        - Price: ₹{price_data.get('lastPrice')}
        - Day Change: {price_data.get('change')} ({price_data.get('pChange')}%)
        - Company: {price_data.get('companyName')}
        
        FUNDAMENTALS (Screener.in):
        {json.dumps(fundamental_data, indent=2) if fundamental_data else "Data unavailable"}
        
        TASK:
        Act as AlphaGalleon, an institutional-grade investment banker. 
        Generate a concise INVESTMENT MEMO.
        
        REQUIRED OUTPUT FORMAT (JSON):
        {{
            "verdict": "BUY" | "SELL" | "HOLD",
            "risk_rating": "LOW" | "MEDIUM" | "HIGH",
            "time_horizon": "SHORT_TERM" | "LONG_TERM",
            "summary": "One sentence punchline.",
            "bull_case": ["point 1", "point 2"],
            "bear_case": ["point 1", "point 2"],
            "key_metrics_analysis": "Brief comment on valuation (P/E, etc)."
        }}
        
        Do not use markdown formatting in the JSON output. Return pure JSON.
        """
        
        # 3. Invoke The Brain
        print(f"Synthesizing memo for {symbol}...")
        response_text = await gemini_service.generate_content(context)
        
        # 4. Parse and Return
        try:
            # Clean up potential markdown code blocks from LLM
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            memo = json.loads(cleaned_text)
            
            # Enrich with source data for UI to display alongside
            return {
                "symbol": symbol,
                "market_data": price_data,
                "fundamentals": fundamental_data,
                "memo": memo
            }
        except json.JSONDecodeError:
            return {
                "symbol": symbol,
                "error": "Failed to parse Brain response",
                "raw_response": response_text
            }

analysis_service = AnalysisService()
