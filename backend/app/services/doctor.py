from typing import List, Dict, Any
from app.services.market_data import market_data_service
from app.services.gemini import gemini_service
import json
import asyncio

class DoctorService:
    """
    The Doctor.
    Diagnoses existing portfolios for health, risk, and optimization.
    """

    async def diagnose_portfolio(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 1. Fetch Live Data for All Holdings
        print(f"Diagnosing portfolio with {len(holdings)} holdings...")
        
        portfolio_data = []
        total_value = 0.0

        for holding in holdings:
            symbol = holding['symbol']
            qty = holding.get('quantity', 1) # Default to 1 if not specified
            
            price_data = market_data_service.get_stock_price(symbol)
            fundamental_data = market_data_service.get_company_ratios(symbol)
            
            if price_data:
                current_price = float(price_data.get('lastPrice', 0.0) or 0.0)
                value = current_price * qty
                total_value += value
                
                # Enrich holding data
                holding_analysis = {
                    "symbol": symbol,
                    "qty": qty,
                    "current_price": current_price,
                    "current_value": value,
                    "fundamentals": fundamental_data
                }
                portfolio_data.append(holding_analysis)
            else:
                portfolio_data.append({"symbol": symbol, "error": "Data unavailable"})

        # 2. Construct the Prompt Context
        context = f"""
        ACT AS: AlphaGalleon Portfolio Doctor (Ruthless, Institutional Grade).
        
        PORTFOLIO SNAPSHOT:
        Total Value: ₹{total_value:,.2f}
        
        HOLDINGS:
        {json.dumps(portfolio_data, indent=2, default=str)}
        
        TASK:
        Diagnose this portfolio. Look for:
        1. Over-concentration (single stock > 10-15%).
        2. Sector bias (too much IT? Banks?).
        3. Fundamental risks (High P/E, Debt).
        4. "Junk" stocks (poor fundamentals).
        
        REQUIRED OUTPUT FORMAT (JSON):
        {{
            "health_score": "Score out of 100 (e.g., 75)",
            "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
            "diagnosis_summary": "One paragraph overview.",
            "critical_warnings": ["Warning 1", "Warning 2"],
            "sector_analysis": "Comment on diversification.",
            "prescriptions": [
                {{ "action": "SELL/REDUCE", "symbol": "XYZ", "reason": "Reason" }},
                {{ "action": "HOLD/ACCUMULATE", "symbol": "ABC", "reason": "Reason" }}
            ]
        }}
        
        Do not use markdown formatting in the JSON output. Return pure JSON.
        """

        # 3. Invoke The Brain
        print("Consulting The Doctor...")
        response_text = await gemini_service.generate_content(context)

        # 4. Parse and Return
        try:
            # Clean up potential markdown code blocks from LLM
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            if cleaned_text.startswith("json"): # Common Gemini quirk
                cleaned_text = cleaned_text[4:].strip()
                
            diagnosis = json.loads(cleaned_text)
            
            return {
                "portfolio_summary": {
                    "total_value": total_value,
                    "holdings_count": len(portfolio_data)
                },
                "diagnosis": diagnosis
            }
        except json.JSONDecodeError:
            return {
                "error": "The Doctor is confused (JSON Parse Error)",
                "raw_response": response_text
            }

doctor_service = DoctorService()
