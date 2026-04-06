import httpx
import os
from typing import Dict, List

class UpstoxService:
    def __init__(self):
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.base_url = "https://api.upstox.com/v2"

    async def get_indices(self) -> Dict:
        """
        Fetch LIVE NIFTY 50 and SENSEX data from Upstox API.
        """
        if not self.access_token:
            print("WARNING: No Access Token. Returning Mock Data.")
            return self._get_mock_indices()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        # Instrument keys for Nifty 50 and SENSEX (Note: These keys might vary, using standard format)
        # Upstox Symbol Format: NSE_INDEX|Nifty 50, BSE_INDEX|SENSEX
        params = {
            "instrument_key": "NSE_INDEX|Nifty 50,BSE_INDEX|SENSEX"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/market-quote/quotes",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    
                    nifty_data = data.get("NSE_INDEX:Nifty 50", {})
                    sensex_data = data.get("BSE_INDEX:SENSEX", {})
                    
                    # Safe extraction (APIs can change)
                    def format_index(idx_data):
                        if not idx_data: return {"value": "0.00", "change": "0.00%"}
                        last_price = idx_data.get("last_price", 0)
                        close_price = idx_data.get("ohlc", {}).get("close", last_price)
                        change = ((last_price - close_price) / close_price) * 100 if close_price else 0
                        
                        return {
                            "value": f"{last_price:,.2f}",
                            "change_percent": f"{change:+.2f}%",
                            "trend": "up" if change > 0 else "down"
                        }

                    return {
                        "nifty": format_index(nifty_data),
                        "sensex": format_index(sensex_data),
                        "gold": {"value": "65,200.00", "change_percent": "+0.4%", "trend": "flat"} # Gold API key pending
                    }
                else:
                    print(f"Upstox API Error: {response.status_code} - {response.text}")
                    return self._get_mock_indices()
                    
        except Exception as e:
            print(f"Upstox Connection Failed: {str(e)}")
            return self._get_mock_indices()

    def _get_mock_indices(self):
        return {
            "nifty": { "value": "22,419.40 (MOCK)", "change_percent": "+1.2%", "trend": "up" },
            "sensex": { "value": "73,876.15 (MOCK)", "change_percent": "+0.8%", "trend": "up" },
            "gold": { "value": "65,200.00", "change_percent": "+0.4%", "trend": "flat" }
        }
