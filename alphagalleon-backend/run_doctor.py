import argparse
import asyncio
import os
from dotenv import load_dotenv
from app.doctor import Doctor
from app.doctor_schema import PortfolioItem

# Load env
load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="AlphaGalleon Doctor CLI")
    parser.add_argument("--portfolio", type=str, required=True, help="List of ticker:allocation pairs (e.g., 'RELIANCE:30:2500,TCS:40:3500,ITC:30:400')")
    parser.add_argument("--risk", type=str, default="moderate", help="Risk appetite (conservative|moderate|aggressive)")

    args = parser.parse_args()

    print(f"\n🩺 AlphaGalleon Doctor initializing for risk profile: {args.risk}...")
    
    # Check for API Key
    if "GOOGLE_API_KEY" not in os.environ:
        print("❌ Error: GOOGLE_API_KEY not found in environment.")
        return

    doctor = Doctor()

    # Parse Portfolio Input
    items = []
    try:
        raw_items = args.portfolio.split(",")
        for item in raw_items:
            parts = item.split(":")
            ticker = parts[0].strip()
            alloc = float(parts[1].strip())
            buy_price = float(parts[2].strip()) if len(parts) > 2 else 0.0
            
            # Mock current price (in real app, we fetch live)
            current_price = buy_price * 1.05 # Assume 5% gain for mock
            
            items.append(PortfolioItem(ticker=ticker, allocation_percent=alloc, avg_buy_price=buy_price, current_price=current_price))
    except Exception as e:
        print(f"❌ Error parsing portfolio string: {e}")
        return

    print(f"📊 Analyzing {len(items)} holdings...")
    try:
        diagnosis = doctor.diagnose_portfolio(items, risk_appetite=args.risk)
        
        print("\n" + "="*50)
        print(f"🩺 PORTFOLIO DIAGNOSIS")
        print("="*50)
        print(f"HEALTH SCORE: {diagnosis.overall_health_score}/100")
        print(f"RISK LEVEL: {diagnosis.risk_level.upper()}")
        print("-" * 50)
        print(f"VERDICT: {diagnosis.diversification_verdict}")
        print("-" * 50)
        print("🚩 RED FLAGS:")
        for flag in diagnosis.red_flags:
            print(f"  • {flag}")
        print("-" * 50)
        print("✅ GREEN FLAGS:")
        for flag in diagnosis.green_flags:
            print(f"  • {flag}")
        print("-" * 50)
        print("🛠️ ACTIONABLE FIXES:")
        for fix in diagnosis.actionable_fixes:
            print(f"  • {fix}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
