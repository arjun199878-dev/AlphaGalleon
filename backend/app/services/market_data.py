import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

class MarketDataService:
    """
    Core data connector for AlphaGalleon.
    Connects to NSE and Screener data sources.
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.nse_base_url = "https://www.nseindia.com"
        self.screener_base_url = "https://www.screener.in/company"
        
        # Initialize cookies for NSE
        self._refresh_nse_cookies()

    def _refresh_nse_cookies(self):
        try:
            self.session.get(self.nse_base_url, timeout=10)
        except Exception as e:
            print(f"Error refreshing NSE cookies: {e}")

    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetches real-time price data from NSE for a given symbol.
        """
        try:
            url = f"{self.nse_base_url}/api/quote-equity?symbol={symbol}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 401:
                self._refresh_nse_cookies()
                response = self.session.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                price_info = data.get("priceInfo", {})
                metadata = data.get("metadata", {})
                
                return {
                    "symbol": symbol,
                    "lastPrice": price_info.get("lastPrice"),
                    "change": price_info.get("change"),
                    "pChange": price_info.get("pChange"),
                    "companyName": metadata.get("companyName"),
                    "lastUpdateTime": metadata.get("lastUpdateTime")
                }
            return None
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_company_ratios(self, symbol: str) -> Optional[Dict[str, str]]:
        """
        Fetches fundamental ratios from Screener.in for a given symbol.
        """
        try:
            # Screener.in uses simple symbol for URL e.g. /company/RELIANCE/consolidated/
            url = f"https://www.screener.in/company/{symbol}/consolidated/"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 404:
                url = f"https://www.screener.in/company/{symbol}/"
                response = self.session.get(url, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                ratios = {}
                
                # Screener puts top ratios in a specific UL > LI structure
                ratio_list = soup.find('ul', {'id': 'top-ratios'})
                if ratio_list:
                    for item in ratio_list.find_all('li', recursive=False):
                        name_span = item.find('span', {'class': 'name'})
                        value_span = item.find('span', {'class': 'number'})
                        if name_span and value_span:
                            ratios[name_span.text.strip()] = value_span.text.strip()
                
                return ratios
            return None
        except Exception as e:
            print(f"Error scraping Screener for {symbol}: {e}")
            return None

market_data_service = MarketDataService()
