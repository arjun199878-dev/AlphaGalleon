import httpx
import asyncio

async def test_backend():
    base_url = "http://localhost:8001"
    
    print("\n--- 1. Testing Market Pulse (Upstox Live) ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/market/pulse")
            print(f"Status: {resp.status_code}")
            print(f"Data: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- 2. Testing AI Doctor (Gemini) ---")
    try:
        portfolio = {
            "holdings": [
                {"stock": "Adani Power", "percent": 40},
                {"stock": "Adani Green", "percent": 30},
                {"stock": "Infosys", "percent": 30}
            ]
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{base_url}/ai/doctor", json=portfolio, timeout=30.0)
            print(f"Status: {resp.status_code}")
            print(f"Diagnosis: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- 3. Testing AI Architect (Gemini) ---")
    try:
        params = {"capital": 500000, "risk": "High", "horizon": "5 Years"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{base_url}/ai/architect?capital=500000&risk=High&horizon=5%20Years", timeout=30.0)
            print(f"Status: {resp.status_code}")
            print(f"Strategy: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend())
