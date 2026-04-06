import sys
import os
import requests

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

try:
    from app.scout import Scout
except ImportError:
    # Fallback if run from inside app/ or similar
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))
    from scout import Scout

def main():
    try:
        scout = Scout()
        print("Scout initialized successfully.")
        
        # Test symbol: RELIANCE (NSE EQ)
        # Correct format for Upstox V2 is often: 'NSE_EQ|INE002A01018'
        # Let's try to find the instrument key if possible, or use the known one for Reliance
        instrument_key = "NSE_EQ|INE002A01018" 
        
        print(f"\n1. Fetching Full Market Quote for {instrument_key}...")
        # We use a direct requests call first to debug if the class wrapper fails
        url = "https://api.upstox.com/v2/market-quote/quotes"
        headers = {
            "Authorization": f"Bearer {os.getenv('UPSTOX_ACCESS_TOKEN')}",
            "Accept": "application/json"
        }
        params = {"symbol": instrument_key}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Connection Successful!")
            if "data" in data and instrument_key in data["data"]:
                quote = data["data"][instrument_key]
                print(f"   Name: {instrument_key}")
                print(f"   LTP: ₹{quote['last_price']}")
                print(f"   OHLC: {quote['ohlc']}")
                print(f"   Depth (Best Bid): {quote['depth']['buy'][0] if 'depth' in quote and 'buy' in quote['depth'] and quote['depth']['buy'] else 'N/A'}")
            else:
                print(f"⚠️ Data fetched but symbol key mismatch. Raw keys: {list(data.get('data', {}).keys())}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Script Error: {e}")

if __name__ == "__main__":
    main()
