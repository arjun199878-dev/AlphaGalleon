from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.upstox_service import UpstoxService
from services.gemini_service import GeminiService
import os
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="AlphaGalleon API", description="AI-First Investment Banking Backend")

# CORS for Mobile/Web Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
upstox = UpstoxService()
gemini = GeminiService()

@app.get("/")
def health_check():
    return {"status": "online", "system": "AlphaGalleon Neural Core"}

@app.get("/market/pulse")
async def get_market_pulse():
    """Fetch live NIFTY/SENSEX data from Upstox"""
    try:
        return await upstox.get_indices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/doctor")
async def analyze_portfolio(portfolio_data: dict):
    """Send portfolio to Gemini for diagnosis"""
    try:
        diagnosis = await gemini.diagnose_portfolio(portfolio_data)
        return {"diagnosis": diagnosis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/architect")
async def generate_strategy(capital: float, risk: str, horizon: str):
    """Generate investment strategy via Gemini"""
    try:
        strategy = await gemini.create_strategy(capital, risk, horizon)
        return {"strategy": strategy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
