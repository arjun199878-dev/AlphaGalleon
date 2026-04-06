import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
        
        # Test symbol: RELIANCE (using ISIN format if known, or generic example)
        # Using a valid symbol format for Upstox V2 is crucial.
        # Often it is 'NSE_EQ|INE002A01018' for Reliance.
        symbol = "NSE_EQ|INE002A01018" 
        
        print(f"\nFetching LTP for {symbol}...")
        ltp = scout.get_ltp(symbol)
        print(f"LTP: {ltp}")

        print(f"\nFetching Quote for {symbol}...")
        quote = scout.get_quote(symbol)
        print(f"Quote: {quote}")

        print(f"\nFetching OHLC for {symbol} (1d)...")
        ohlc = scout.get_ohlc(symbol, "1d")
        print(f"OHLC: {ohlc}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
