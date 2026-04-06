import argparse
import asyncio
import os
from dotenv import load_dotenv
from app.architect import Architect
from app.architect_schema import UserDNA

# Load env
load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="AlphaGalleon Architect CLI")
    parser.add_argument("--age", type=int, required=True, help="User's age")
    parser.add_argument("--risk", type=str, required=True, help="Risk appetite (conservative|moderate|aggressive)")
    parser.add_argument("--capital", type=float, required=True, help="Capital amount in INR")
    parser.add_argument("--horizon", type=str, required=True, help="Investment horizon (e.g., '10 years')")
    parser.add_argument("--goals", type=str, default="Wealth Creation", help="Investment goals")

    args = parser.parse_args()

    print(f"\n🏗️ AlphaGalleon Architect initializing for {args.age}y {args.risk} investor...")
    
    # Check for API Key
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ Error: GOOGLE_API_KEY not found in environment.")
        return

    architect = Architect()

    # Construct Data
    user_dna = UserDNA(
        age=args.age,
        risk_appetite=args.risk,
        capital_amount=args.capital,
        investment_horizon=args.horizon,
        goals=args.goals
    )

    print(f"⏳ Constructing personalized portfolio for ₹{args.capital:,.0f}...")
    try:
        portfolio = architect.construct_portfolio(user_dna)
        
        print("\n" + "="*50)
        print(f"🏗️ MODEL PORTFOLIO: {portfolio.strategy_name.upper()}")
        print("="*50)
        print(f"STRATEGY: {portfolio.description}")
        print(f"EXPECTED CAGR: {portfolio.expected_cagr} | MAX DRAWDOWN: {portfolio.max_drawdown}")
        print(f"REBALANCE: {portfolio.rebalance_frequency}")
        print("-" * 50)
        
        total_alloc = 0
        for alloc in portfolio.allocations:
            print(f"{alloc.asset_class} - {alloc.sub_category}: {alloc.percentage}%")
            print(f"   💡 Rationale: {alloc.rationale}")
            print(f"   🎯 Instruments: {', '.join(alloc.suggested_instruments)}")
            print("-" * 30)
            total_alloc += alloc.percentage
        
        print(f"TOTAL ALLOCATION: {total_alloc}%")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
