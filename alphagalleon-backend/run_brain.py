import argparse
import asyncio
import os
from dotenv import load_dotenv
from app.brain import Brain
from app.schemas import FundamentalData, Ticker

# Load env
load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="AlphaGalleon Brain CLI")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol (e.g., RELIANCE)")
    parser.add_argument("--price", type=float, default=2500.0)
    parser.add_argument("--sector", type=str, default="Conglomerate")
    parser.add_argument("--market_cap", type=float, default=1500000.0)
    parser.add_argument("--pe", type=float, default=25.0)
    parser.add_argument("--rev_growth", type=float, default=12.5)
    parser.add_argument("--prof_growth", type=float, default=15.0)
    parser.add_argument("--debt_equity", type=float, default=0.4)
    parser.add_argument("--roe", type=float, default=18.0)
    parser.add_argument("--promoter", type=float, default=50.0)
    parser.add_argument("--news", type=str, default="No major negative news. Stable outlook.")

    args = parser.parse_args()

    print(f"\n🧠 AlphaGalleon Brain initializing for {args.ticker}...")
    
    # Check for API Key
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ Error: GOOGLE_API_KEY not found in environment.")
        print("Please create a .env file with GOOGLE_API_KEY=your_key_here")
        return

    brain = Brain()

    # Construct Data
    ticker_data = Ticker(
        symbol=args.ticker,
        name=args.ticker,
        sector=args.sector,
        current_price=args.price,
        market_cap=args.market_cap,
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

    print("⏳ Generating Investment Memo (Gemini 1.5 Flash)...")
    try:
        memo = brain.generate_memo(fund_data)
        
        print("\n" + "="*50)
        print(f"📄 INVESTMENT MEMO: {memo.ticker_symbol}")
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
