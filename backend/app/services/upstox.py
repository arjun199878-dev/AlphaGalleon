import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class UpstoxService:
    def __init__(self):
        self.base_url = "https://api.upstox.com/v2"
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    async def get_holdings(self):
        """
        Fetch real-time holdings from Upstox account.
        """
        url = f"{self.base_url}/portfolio/long-term-holdings"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                return {"error": f"Failed to fetch holdings: {response.text}", "status_code": response.status_code}

    async def get_positions(self):
        """
        Fetch real-time positions (intraday/unsettled) from Upstox account.
        """
        url = f"{self.base_url}/portfolio/short-term-positions"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                return {"error": f"Failed to fetch positions: {response.text}"}

    async def get_market_quote(self, symbols: list):
        """
        Fetch live market quotes for a list of symbols (NSE/BSE).
        Example symbols: ["NSE_EQ|INE062A01020", "NSE_EQ|INE467B01029"]
        """
        symbol_string = ",".join(symbols)
        url = f"{self.base_url}/market-quote/quotes?instrument_key={symbol_string}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                return {"error": f"Failed to fetch quotes: {response.text}"}

upstox_service = UpstoxService()
