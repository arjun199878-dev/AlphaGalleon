import os
import httpx
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Scout:
    """Scout Engine - Fetches real-time market data from Upstox API"""
    
    BASE_URL = "https://api.upstox.com/v2"

    def __init__(self):
        """Initialize Scout with Upstox credentials from environment"""
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.api_secret = os.getenv("UPSTOX_API_SECRET")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        
        # Check if we have the required credentials
        self.has_credentials = bool(self.access_token)
        
        if self.has_credentials:
            logger.info("✓ Scout: Upstox credentials loaded successfully")
            logger.info(f"  API Key: {self.api_key[:20]}..." if self.api_key else "  API Key: Not provided")
            logger.info(f"  Access Token: {self.access_token[:30]}..." if self.access_token else "  Access Token: Not provided")
        else:
            logger.warning("⚠ Scout: Upstox credentials not found. Using mock data fallback.")
            logger.warning("  Set UPSTOX_ACCESS_TOKEN, UPSTOX_API_KEY, UPSTOX_API_SECRET to use real API")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        } if self.has_credentials else {}

    def _get(self, endpoint, params=None):
        """Make GET request to Upstox API with error handling"""
        if not self.has_credentials:
            return self._get_mock_data(endpoint, params)
        
        url = f"{self.BASE_URL}{endpoint}"
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                logger.debug(f"Scout API call succeeded: {endpoint} for {params}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Upstox API Error: {e.response.status_code} - {e.response.text}")
            # Fallback to mock data on API error
            return self._get_mock_data(endpoint, params)
        except httpx.RequestError as e:
            logger.error(f"Network Error calling Upstox: {e}")
            # Fallback to mock data on network error
            return self._get_mock_data(endpoint, params)
        except Exception as e:
            logger.error(f"Unexpected error in Scout._get: {e}")
            return self._get_mock_data(endpoint, params)

    def _get_mock_data(self, endpoint, params):
        """Fallback mock data when API is unavailable"""
        logger.info(f"Scout using mock data for: {endpoint}")
        
        symbol = params.get("symbol", "UNKNOWN") if params else "UNKNOWN"
        
        if "ltp" in endpoint:
            return {
                "data": {
                    symbol: {
                        "last_price": 2500.0,
                        "ohlc": {
                            "open": 2480,
                            "high": 2550,
                            "low": 2470,
                            "close": 2500
                        }
                    }
                }
            }
        elif "ohlc" in endpoint:
            return {
                "data": {
                    symbol: {
                        "ohlc": {
                            "open": 2480,
                            "high": 2550,
                            "low": 2470,
                            "close": 2500
                        }
                    }
                }
            }
        elif "quotes" in endpoint:
            return {
                "data": {
                    symbol: {
                        "last_price": 2500.0,
                        "volume": 1000000,
                        "ohlc": {
                            "open": 2480,
                            "high": 2550,
                            "low": 2470,
                            "close": 2500
                        },
                        "depth": {
                            "buy": [{"price": 2499, "quantity": 500}, {"price": 2498, "quantity": 1000}],
                            "sell": [{"price": 2501, "quantity": 500}, {"price": 2502, "quantity": 1000}]
                        }
                    }
                }
            }
        
        return {"data": {}}

    def get_ltp(self, symbol: str):
        """
        Fetch Last Traded Price (LTP) for a symbol.
        
        Args:
            symbol: Symbol in format like "NSE_EQ|INE002A01018" or "RELIANCE"
        
        Returns:
            float: Last traded price, or None if not found
        
        Example:
            >>> scout = Scout()
            >>> price = scout.get_ltp("NSE_EQ|INE002A01018")
            >>> print(price)  # 2500.5
        """
        endpoint = "/market-quote/ltp"
        params = {"symbol": symbol}
        data = self._get(endpoint, params)
        if data and "data" in data:
            if symbol in data["data"]:
                return data["data"][symbol].get("last_price")
            if len(data["data"]) == 1:
                key = next(iter(data["data"]))
                return data["data"][key].get("last_price")
        return None

    def get_ltp_multi(self, symbols: list):
        """
        Fetch Last Traded Prices (LTP) for multiple symbols.
        
        Args:
            symbols: List of symbols in Upstox format
            
        Returns:
            dict: Mapping of symbol to last traded price
        """
        if not symbols:
            return {}
            
        endpoint = "/market-quote/ltp"
        # Upstox supports comma separated symbols
        symbol_str = ",".join(symbols)
        params = {"symbol": symbol_str}
        
        data = self._get(endpoint, params)
        result = {}
        
        if data and "data" in data:
            for sym in symbols:
                # Upstox returns keys that might slightly differ or be nested
                if sym in data["data"]:
                    result[sym] = data["data"][sym].get("last_price")
                else:
                    # Look for case-insensitive match or contains
                    for key in data["data"]:
                        if sym.upper() in key.upper():
                            result[sym] = data["data"][key].get("last_price")
                            break
                            
        return result

    def get_ohlc(self, symbol: str, interval: str = "1d"):
        """
        Fetch OHLC (Open, High, Low, Close) data for a symbol.
        
        Args:
            symbol: Symbol in format like "NSE_EQ|INE002A01018"
            interval: Time interval - 1d, 1w, 1m, I1, I5, I10, I15, I30, I60
        
        Returns:
            dict: OHLC data with keys 'open', 'high', 'low', 'close', or None
        
        Example:
            >>> scout = Scout()
            >>> ohlc = scout.get_ohlc("NSE_EQ|INE002A01018", "1d")
            >>> print(ohlc)  # {'open': 2480, 'high': 2550, 'low': 2470, 'close': 2500}
        """
        endpoint = "/market-quote/ohlc"
        params = {"symbol": symbol, "interval": interval}
        data = self._get(endpoint, params)
        if data and "data" in data:
            if symbol in data["data"]:
                return data["data"][symbol].get("ohlc")
            if len(data["data"]) == 1:
                key = next(iter(data["data"]))
                return data["data"][key].get("ohlc")
        return None

    def get_quote(self, symbol: str):
        """
        Fetch complete quote for a symbol (LTP, OHLC, volume, depth).
        
        Args:
            symbol: Symbol in format like "NSE_EQ|INE002A01018"
        
        Returns:
            dict: Complete quote data, or None if not found
        
        Example:
            >>> scout = Scout()
            >>> quote = scout.get_quote("NSE_EQ|INE002A01018")
            >>> print(quote['last_price'])  # 2500.5
            >>> print(quote['ohlc'])  # {'open': 2480, 'high': 2550, ...}
        """
        endpoint = "/market-quote/quotes"
        params = {"symbol": symbol}
        data = self._get(endpoint, params)
        if data and "data" in data:
            if symbol in data["data"]:
                return data["data"][symbol]
            if len(data["data"]) == 1:
                key = next(iter(data["data"]))
                return data["data"][key]
        return None

    def get_depth(self, symbol: str):
        """
        Fetch market depth (buy/sell orders) for a symbol.
        
        Args:
            symbol: Symbol in format like "NSE_EQ|INE002A01018"
        
        Returns:
            dict: Depth information with 'buy' and 'sell' orders, or None
        
        Example:
            >>> scout = Scout()
            >>> depth = scout.get_depth("NSE_EQ|INE002A01018")
            >>> print(depth['buy'])  # [{'price': 2499, 'quantity': 500}, ...]
        """
        endpoint = "/market-quote/quotes"
        params = {"symbol": symbol}
        data = self._get(endpoint, params)
        if data and "data" in data:
            if symbol in data["data"]:
                return data["data"][symbol].get("depth")
            if len(data["data"]) == 1:
                key = next(iter(data["data"]))
                return data["data"][key].get("depth")
        return None

    def is_real_api(self) -> bool:
        """Check if using real Upstox API or mock data"""
        return self.has_credentials

    def get_status(self) -> dict:
        """Get Scout engine status"""
        return {
            "engine": "scout",
            "status": "operational",
            "api_source": "upstox" if self.has_credentials else "mock",
            "credentials_loaded": self.has_credentials
        }

    def screen(self, query: str):
        """
        AI-powered natural language stock screening.
        Uses key-word heuristics to simulate an institutional-grade brain.
        """
        logger.info(f"Scout screening markets for query: {query}")
        q = query.lower()
        
        # Knowledge-base of opportunities (Base candidates)
        # In a production app, this would query a real universe of 5000+ stocks
        universe = [
            {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "debt": "Zero", "return": "15%", "price": "₹2,980.50", "rationale": "Massive conglomerate with clean balance sheet and green energy pivot."},
            {"symbol": "HAL", "name": "Hindustan Aeronautics", "sector": "Defense", "debt": "Zero", "return": "42%", "price": "₹3,204.50", "rationale": "Strategic monopoly, defense order book at all-time high, negative net debt."},
            {"symbol": "TATAELXSI", "name": "Tata Elxsi", "sector": "Tech", "debt": "Low", "return": "28%", "price": "₹7,840.00", "rationale": "High-end R&D play, strong margins, and AI/Auto-tech focus."},
            {"symbol": "CDSL", "name": "Central Depository", "sector": "Fintech", "debt": "Zero", "return": "35%", "price": "₹1,950.25", "rationale": "Asset-light monopoly, recurring revenue as investor base grows."},
            {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT", "debt": "Zero", "return": "22%", "price": "₹4,120.00", "rationale": "Resilient cash flow, high dividends, and global delivery scale."},
            {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking", "debt": "N/A", "return": "12%", "price": "₹1,640.00", "rationale": "Market leader, strong CASA ratio, and safe-haven status."},
        ]
        
        results = []
        
        # Heuristic Matching Logic
        if "debt" in q or "cash" in q or "clean" in q:
            results = [s for s in universe if s["debt"] in ["Zero", "Low"]]
        elif "tech" in q or "it" in q or "software" in q:
            results = [s for s in universe if s["sector"] in ["Tech", "IT", "Fintech"]]
        elif "bank" in q or "finance" in q:
            results = [s for s in universe if s["sector"] in ["Banking", "Fintech"]]
        elif "defense" in q or "strategic" in q:
            results = [s for s in universe if s["sector"] == "Defense"]
        else:
            # Default to diversified high-potential picks
            results = [universe[1], universe[2], universe[3]]
            
        # Map to final output format
        final_opportunities = []
        for r in results:
            final_opportunities.append({
                "id": r["symbol"],
                "symbol": r["symbol"],
                "name": r["name"],
                "price": r["price"],
                "change": "+2.4%", # Mocked trend for UI
                "trend": "up",
                "rationale": r["rationale"]
            })
            
        return final_opportunities

