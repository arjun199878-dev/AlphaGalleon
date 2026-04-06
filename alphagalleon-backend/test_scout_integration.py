#!/usr/bin/env python3
"""
Test Scout Integration with Real Upstox API
Tests the Scout engine with provided credentials
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.scout import Scout
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_scout_initialization():
    """Test Scout engine initializes with credentials"""
    print("=" * 60)
    print("TEST 1: Scout Initialization")
    print("=" * 60)
    
    scout = Scout()
    status = scout.get_status()
    
    print(f"✓ Scout Engine Status:")
    print(f"  - Engine: {status['engine']}")
    print(f"  - Status: {status['status']}")
    print(f"  - API Source: {status['api_source']}")
    print(f"  - Credentials Loaded: {status['credentials_loaded']}")
    
    if status['credentials_loaded']:
        print("\n✓ Using REAL Upstox API")
    else:
        print("\n⚠ Using mock fallback data (credentials not found)")
    
    return scout

def test_get_ltp(scout, symbol="NSE_EQ|INE002A01018"):
    """Test fetching Last Traded Price"""
    print("\n" + "=" * 60)
    print(f"TEST 2: Fetch LTP for {symbol}")
    print("=" * 60)
    
    try:
        ltp = scout.get_ltp(symbol)
        if ltp:
            print(f"✓ Last Traded Price: ₹{ltp}")
            return True
        else:
            print(f"⚠ Could not fetch LTP for {symbol}")
            return False
    except Exception as e:
        print(f"✗ Error fetching LTP: {e}")
        return False

def test_get_ohlc(scout, symbol="NSE_EQ|INE002A01018"):
    """Test fetching OHLC data"""
    print("\n" + "=" * 60)
    print(f"TEST 3: Fetch OHLC for {symbol}")
    print("=" * 60)
    
    try:
        ohlc = scout.get_ohlc(symbol, interval="1d")
        if ohlc:
            print(f"✓ OHLC Data (1D):")
            print(f"  - Open: ₹{ohlc.get('open')}")
            print(f"  - High: ₹{ohlc.get('high')}")
            print(f"  - Low: ₹{ohlc.get('low')}")
            print(f"  - Close: ₹{ohlc.get('close')}")
            return True
        else:
            print(f"⚠ Could not fetch OHLC for {symbol}")
            return False
    except Exception as e:
        print(f"✗ Error fetching OHLC: {e}")
        return False

def test_get_quote(scout, symbol="NSE_EQ|INE002A01018"):
    """Test fetching complete quote"""
    print("\n" + "=" * 60)
    print(f"TEST 4: Fetch Quote for {symbol}")
    print("=" * 60)
    
    try:
        quote = scout.get_quote(symbol)
        if quote:
            print(f"✓ Quote Data:")
            print(f"  - Last Price: ₹{quote.get('last_price')}")
            if 'ohlc' in quote:
                print(f"  - Close: ₹{quote['ohlc'].get('close')}")
            if 'volume' in quote:
                print(f"  - Volume: {quote.get('volume'):,}")
            return True
        else:
            print(f"⚠ Could not fetch quote for {symbol}")
            return False
    except Exception as e:
        print(f"✗ Error fetching quote: {e}")
        return False

def test_get_depth(scout, symbol="NSE_EQ|INE002A01018"):
    """Test fetching market depth"""
    print("\n" + "=" * 60)
    print(f"TEST 5: Fetch Depth for {symbol}")
    print("=" * 60)
    
    try:
        depth = scout.get_depth(symbol)
        if depth:
            print(f"✓ Market Depth:")
            buy_orders = depth.get('buy', [])
            sell_orders = depth.get('sell', [])
            print(f"  - Buy Orders: {len(buy_orders)}")
            if buy_orders:
                print(f"    Best Bid: ₹{buy_orders[0].get('price')} x {buy_orders[0].get('quantity')}")
            print(f"  - Sell Orders: {len(sell_orders)}")
            if sell_orders:
                print(f"    Best Ask: ₹{sell_orders[0].get('price')} x {sell_orders[0].get('quantity')}")
            return True
        else:
            print(f"⚠ Could not fetch depth for {symbol}")
            return False
    except Exception as e:
        print(f"✗ Error fetching depth: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🚀 SCOUT ENGINE INTEGRATION TEST\n")
    
    # Test 1: Initialization
    scout = test_scout_initialization()
    
    if not scout.is_real_api():
        print("\n⚠️ WARNING: Using mock data. Please check:")
        print("   1. Is .env file present in alphagalleon-backend/?")
        print("   2. Does it contain UPSTOX_ACCESS_TOKEN?")
        print("   3. Is the token fresh (not expired)?")
    else:
        print("\n✓ Real API credentials loaded. Running API tests...\n")
    
    # Run tests
    results = {
        "LTP": test_get_ltp(scout),
        "OHLC": test_get_ohlc(scout),
        "Quote": test_get_quote(scout),
        "Depth": test_get_depth(scout),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "=" * 60)
    if passed == total:
        print("✓ All tests passed! Scout is ready for production.")
    elif passed > 0:
        print("⚠ Some tests passed. Scout is using mock fallback for failed tests.")
    else:
        print("✗ All tests failed. Check Scout configuration and Upstox API status.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
