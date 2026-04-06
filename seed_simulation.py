from convex import ConvexClient

# Your Convex URL
client = ConvexClient("https://vibrant-spoonbill-564.eu-west-1.convex.cloud")

def seed_simulation():
    print("⚓️ Seeding Simulated Reliance Portfolio...")
    
    # 1. Ensure a test user exists
    user_id = client.mutation("users:create", {
        "name": "Arjun Tr",
        "email": "arjun@alphagalleon.ai",
        "riskProfile": "moderate"
    })
    print(f"✅ User ID: {user_id}")

    # 2. Create a simulated portfolio
    portfolio_id = client.mutation("portfolios:create", {
        "userId": user_id,
        "name": "Strategy Alpha (Simulated)",
        "capital": 500000,
        "riskProfile": "moderate",
        "timeHorizon": "Long Term"
    })
    print(f"✅ Portfolio ID: {portfolio_id}")

    # 3. Add Reliance Holding
    client.mutation("holdings:add", {
        "portfolioId": portfolio_id,
        "userId": user_id,
        "symbol": "RELIANCE",
        "quantity": 50,
        "avgBuyPrice": 2950,
        "allocation": 29.5
    })
    print("✅ Reliance Simulation Injected.")

    # 4. Generate a Simulated Memo for Reliance
    client.mutation("memos:store", {
        "userId": user_id,
        "symbol": "RELIANCE",
        "verdict": "BUY",
        "confidence": 85,
        "summary": "Reliance showing strong consolidation at current levels with positive momentum in O2C and Retail segments.",
        "reasoning": "Technical indicators suggest an RSI bounce from 40. Fundamental growth in Jio Financial and green energy pivot provides long-term valuation support.",
        "priceAtGeneration": 2980.50
    })
    print("✅ Simulated Brain Memo stored.")

if __name__ == "__main__":
    seed_simulation()
