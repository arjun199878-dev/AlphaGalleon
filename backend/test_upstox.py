import asyncio
from app.services.upstox import upstox_service

async def test_upstox():
    print("⚓️ Testing Upstox Connection...")
    
    print("\n--- Holdings (Long Term) ---")
    holdings = await upstox_service.get_holdings()
    if isinstance(holdings, list):
        print(f"✅ Found {len(holdings)} holdings.")
        for item in holdings[:3]:
            print(f"- {item['tradingsymbol']}: {item['quantity']} units")
    else:
        print(f"❌ Error: {holdings.get('error')}")

    print("\n--- Positions (Short Term/Live) ---")
    positions = await upstox_service.get_positions()
    if isinstance(positions, list):
        print(f"✅ Found {len(positions)} positions.")
        for item in positions[:3]:
            print(f"- {item['tradingsymbol']}: {item['quantity']} units")
    else:
        print(f"❌ Error: {positions.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_upstox())
