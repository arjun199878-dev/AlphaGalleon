import argparse
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.brain import Brain
from app.schemas import FundamentalData, Ticker
from app.scout import Scout

# Load env
load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="AlphaGalleon Brain CLI (Live)")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol (e.g., RELIANCE or NSE_EQ|INE002A01018)")
    
    # Optional overrides for missing data
    parser.add_argument("--sector", type=str, default="Unknown", help="Sector override")
    parser.add_argument("--pe", type=float, default=25.0, help="P/E override")
    parser.add_argument("--rev_growth", type=float, default=10.0, help="Rev growth override")
    parser.add_argument("--prof_growth", type=float, default=12.0, help="Profit growth override")
    parser.add_argument("--debt_equity", type=float, default=0.5, help="Debt/Equity override")
    parser.add_argument("--roe", type=float, default=15.0, help="ROE override")
    parser.add_argument("--promoter", type=float, default=50.0, help="Promoter holding override")
    parser.add_argument("--news", type=str, default="No major negative news. Stable outlook.", help="News summary override")

    args = parser.parse_args()

    print(f"\n🧠 AlphaGalleon Brain initializing for {args.ticker}...")
    
    # Check for API Key
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ Error: GOOGLE_API_KEY not found in environment.")
        return

    # Initialize Scout
    print("📡 Contacting Scout for live market data...")
    scout = Scout()
    
    # Handle Ticker Format
    # If user provides just 'RELIANCE', we need to map or guess the instrument key.
    # Ideally we'd have a mapping db. For now, we assume user might pass 'NSE_EQ|INE...' or just rely on manual mapping for testing.
    # Let's try to infer common ones or just take raw input.
    symbol = args.ticker
    if "|" not in symbol and "NSE_EQ" not in symbol:
        # Simple heuristic mapping for demo
        if symbol.upper() == "RELIANCE":
            symbol = "NSE_EQ|INE002A01018"
        elif symbol.upper() == "TCS":
            symbol = "NSE_EQ|INE467B01029"
        elif symbol.upper() == "INFY":
            symbol = "NSE_EQ|INE009A01021"
        elif symbol.upper() == "HDFCBANK":
            symbol = "NSE_EQ|INE040A01034"
        else:
            print(f"⚠️ Warning: Symbol '{symbol}' might not be a valid Upstox instrument key. Using as-is.")

    try:
        quote = scout.get_quote(symbol)
        if not quote:
            print(f"❌ Scout failed to fetch quote for {symbol}. Check symbol or token.")
            return

        ltp = quote.get('last_price', 0.0)
        ohlc = quote.get('ohlc', {})
        open_price = ohlc.get('open', 0.0)
        high_price = ohlc.get('high', 0.0)
        low_price = ohlc.get('low', 0.0)
        close_price = ohlc.get('close', 0.0)
        
        print(f"✅ Live Data Acquired: LTP ₹{ltp} (O: {open_price} H: {high_price} L: {low_price})")
        
        # We don't have Market Cap in Upstox Quote API (usually needs fundamental API).
        # We will mock Market Cap based on Price * Shares (assumed) or just use a placeholder
        # For demo purposes, we will estimate or use the passed default if 0.
        market_cap = ltp * 1000000 # Mock shares count

    except Exception as e:
        print(f"❌ Scout error: {e}")
        return

    brain = Brain()

    # Construct Data with LIVE Price
    ticker_data = Ticker(
        symbol=args.ticker, # User friendly name
        name=args.ticker,
        sector=args.sector,
        current_price=ltp, # LIVE PRICE
        market_cap=market_cap,
        pe_ratio=args.pe
    )

    fund_data = FundamentalData(
        ticker=ticker_data,
        revenue_growth_3y=args.rev_growth,
        profit_growth_3y=args.prof_growth,
        debt_to_equity=args.debt_equity,
        roe=args.roe,
        promoter_holding=args.promoter,
        recent_news_summary=args.news
    )

    print("⏳ Generating Investment Memo (Gemini 2.5 Flash)...")
    try:
        memo = brain.generate_memo(fund_data)
        
        print("\n" + "="*50)
        print(f"📄 INVESTMENT MEMO: {memo.ticker_symbol} @ ₹{ltp}")
        print("="*50)
        print(f"VERDICT: {memo.recommendation.upper()} (Confidence: {memo.confidence_score}/100)")
        print(f"VALUATION: {memo.valuation_verdict}")
        print("-" * 50)
        print(f"THESIS: {memo.thesis_summary}")
        print("-" * 50)
        print("🟢 BULL CASE:")
        for point in memo.bull_case:
            print(f"  • {point}")
        print("-" * 50)
        print("🔴 BEAR CASE:")
        for point in memo.bear_case:
            print(f"  • {point}")
        print("-" * 50)
        print("⚠️ CATALYSTS:")
        for point in memo.catalysts:
            print(f"  • {point}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
