import os
import requests
from dotenv import load_dotenv

load_dotenv("alphagalleon-backend/.env")

TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
BASE_URL = "https://api.upstox.com/v2"

# 1. Fetch Instruments for NSE EQ to find RELIANCE key
# This is usually a large CSV download. Let's try to query quotes directly with the correct key format if known.
# Common Upstox V2 instrument key format for Reliance NSE EQ: "NSE_EQ|INE002A01018"
# But the previous test returned 'NSE_EQ:RELIANCE' as a key in the response. That's unusual for V2 quotes endpoint which usually returns instrument_key.
# Let's try with 'NSE_EQ|INE002A01018' and see if we can parse the response correctly.

def test_quote():
    url = f"{BASE_URL}/market-quote/quotes"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }
    # Trying the ISIN based instrument key first
    instrument_key = "NSE_EQ|INE002A01018"
    params = {"symbol": instrument_key}
    
    print(f"Fetching Quote for {instrument_key}...")
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # print(data) # Start by printing raw if structure is unknown
            
            # The structure is usually {"status": "success", "data": { "NSE_EQ:RELIANCE": { ... } }}
            # Wait, the previous output said: "Raw keys: ['NSE_EQ:RELIANCE']"
            # So the API *accepts* "NSE_EQ|INE002A01018" but returns data keyed by "NSE_EQ:RELIANCE".
            
            if "data" in data:
                # Get the first key in data dictionary
                first_key = next(iter(data["data"]))
                quote = data["data"][first_key]
                
                print(f"\n✅ SUCCESS: {first_key}")
                print(f"   LTP: ₹{quote.get('last_price', 'N/A')}")
                print(f"   Open: {quote.get('ohlc', {}).get('open', 'N/A')}")
                print(f"   High: {quote.get('ohlc', {}).get('high', 'N/A')}")
                print(f"   Low: {quote.get('ohlc', {}).get('low', 'N/A')}")
                print(f"   Close: {quote.get('ohlc', {}).get('close', 'N/A')}")
            else:
                print("❌ 'data' field missing in response.")
        else:
             print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_quote()
