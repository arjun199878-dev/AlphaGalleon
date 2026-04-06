import httpx
import asyncio
import os

async def check_api():
    base_url = "http://localhost:8001"
    report = []
    
    # 1. Server Health
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/")
            if resp.status_code != 200:
                report.append("❌ Backend Server is not responding correctly.")
    except Exception:
        report.append("❌ Backend Server is OFFLINE.")

    # 2. Upstox Token
    if not report: # Only check if server is up
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{base_url}/market/pulse")
                if resp.status_code != 200:
                    report.append("❌ TOKEN_EXPIRED: Upstox Access Token has EXPIRED.")
                else:
                    data = resp.json()
                    # Check if it returned mock data due to API error
                    if "MOCK" in str(data):
                        report.append("❌ TOKEN_EXPIRED: Upstox API is returning MOCK data.")
        except Exception:
            report.append("❌ Error connecting to Upstox service.")

    return "\\n".join(report) if report else "OK"

if __name__ == "__main__":
    status = asyncio.run(check_api())
    print(status)
