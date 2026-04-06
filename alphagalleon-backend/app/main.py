from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
import uvicorn
import os
from dotenv import load_dotenv

# Import our internal modules
from app.schemas import Ticker, FundamentalData, InvestmentMemo
from app.brain import Brain
from app.doctor import Doctor
from app.doctor_schema import PortfolioItem, PortfolioDiagnosis
from app.architect import Architect
from app.architect_schema import UserDNA, ModelPortfolio
from app.scout import Scout
from app.sentinel import Sentinel
from app.backtester import Backtester
from app.convex_service import ConvexService
from app.upstox_auth import router as upstox_auth_router
from app.upstox_holdings import router as upstox_holdings_router
from app.upstox_execute import router as upstox_execute_router
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    get_token_expiry_seconds
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AlphaGalleon API",
    version="1.0.0",
    description="Institutional-Grade Personal Investment Banker"
)

# Add CORS middleware to allow frontend/mobile requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Main Routers ──────────────────────────────
app.include_router(upstox_auth_router, prefix="/api/v1/upstox", tags=["Upstox Auth"])
app.include_router(upstox_holdings_router, prefix="/api/v1/upstox", tags=["Upstox Sync"])
app.include_router(upstox_execute_router, prefix="/api/v1/upstox", tags=["Upstox Execute"])

# ─── Initialize Engines ───────────────────────────────────
brain_engine = Brain()
doctor_engine = Doctor()
architect_engine = Architect()
scout_engine = Scout()
sentinel_engine = Sentinel(scout_engine)
backtest_engine = Backtester(scout_engine)
convex_service = ConvexService()

# ─── Request/Response Models ──────────────────────────────

# Authentication Models
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    riskProfile: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: str
    riskProfile: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: UserResponse
    expiresIn: int

class MemoRequest(BaseModel):
    ticker: str
    price: float
    market_cap: float
    pe: float
    sector: str
    revenue_growth: float
    profit_growth: float
    debt_equity: float
    roe: float
    promoter_holding: float
    news: str

class DoctorRequest(BaseModel):
    portfolio: List[dict]  # [{"ticker": "RELIANCE", "allocation": 30, "buy_price": 2500, "current_price": 2600}]
    risk_appetite: str = "moderate"

class ArchitectRequest(BaseModel):
    age: int
    risk_appetite: str
    capital_amount: float
    investment_horizon: str
    goals: str = "Wealth Creation"

class QuoteResponse(BaseModel):
    symbol: str
    ltp: float
    ohlc: Optional[Dict[str, Any]] = None
    depth: Optional[Dict[str, Any]] = None

# ─── Health & Root Endpoints ──────────────────────────────

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "AlphaGalleon HQ Online 🚀", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "services": {
            "brain": "operational",
            "doctor": "operational",
            "architect": "operational",
            "scout": "operational",
            "convex": "operational"
        }
    }

# ─── Authentication Endpoints ─────────────────────────────

@app.post("/api/v1/auth/login", response_model=AuthResponse, tags=["Auth"])
def login(request: LoginRequest):
    """
    User login endpoint. Returns JWT token for authenticated requests.
    """
    try:
        # Get user from database
        user = convex_service.get_user_by_email(request.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(request.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        token = create_access_token({"sub": request.email, "user_id": str(user.get("_id", ""))})
        
        # Log activity
        convex_service.log_activity(
            user_id=str(user.get("_id", "")),
            action="USER_LOGIN",
            details=f"User {request.email} logged in"
        )
        
        return AuthResponse(
            token=token,
            user=UserResponse(
                _id=str(user.get("_id", "")),
                name=user.get("name", ""),
                email=user.get("email", ""),
                riskProfile=user.get("riskProfile")
            ),
            expiresIn=get_token_expiry_seconds()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.post("/api/v1/auth/signup", response_model=AuthResponse, tags=["Auth"])
def signup(request: SignupRequest):
    """
    User signup endpoint. Creates a new user account and returns JWT token.
    """
    try:
        # Check if user already exists
        existing_user = convex_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Hash password
        password_hash = hash_password(request.password)
        
        # Create user in database
        user = convex_service.create_user(
            name=request.name,
            email=request.email,
            password_hash=password_hash,
            riskProfile=request.riskProfile
        )
        
        # Create access token
        token = create_access_token({"sub": request.email, "user_id": str(user.get("_id", ""))})
        
        # Log activity
        convex_service.log_activity(
            user_id=str(user.get("_id", "")),
            action="USER_SIGNUP",
            details=f"New user {request.email} signed up"
        )
        
        return AuthResponse(
            token=token,
            user=UserResponse(
                _id=str(user.get("_id", "")),
                name=user.get("name", ""),
                email=user.get("email", ""),
                riskProfile=user.get("riskProfile")
            ),
            expiresIn=get_token_expiry_seconds()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

@app.get("/api/v1/auth/verify", tags=["Auth"])
def verify_token(authorization: Optional[str] = Header(None)):
    """
    Verify JWT token validity.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.replace("Bearer ", "")
        token_data = decode_token(token)
        
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {"valid": True, "email": token_data.sub, "user_id": token_data.user_id}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

# ─── Brain Endpoints (Investment Analysis) ────────────────

@app.post("/api/v1/brain/memo", response_model=InvestmentMemo, tags=["Brain"])
def create_memo(request: MemoRequest):
    """
    Generate an Investment Memo using The Brain (Gemini 2.5 Flash).
    
    Returns:
    - recommendation: BUY | SELL | HOLD | AVOID
    - confidence_score: 0-100
    - thesis_summary: Executive summary
    - bull_case: Reasons to buy
    - bear_case: Risks to watch
    - catalysts: Upcoming events
    - valuation_verdict: Cheap | Fair | Expensive
    """
    try:
        ticker_obj = Ticker(
            symbol=request.ticker,
            name=request.ticker,
            sector=request.sector,
            current_price=request.price,
            market_cap=request.market_cap,
            pe_ratio=request.pe
        )
        
        fund_data = FundamentalData(
            ticker=ticker_obj,
            revenue_growth_3y=request.revenue_growth,
            profit_growth_3y=request.profit_growth,
            debt_to_equity=request.debt_equity,
            roe=request.roe,
            promoter_holding=request.promoter_holding,
            recent_news_summary=request.news
        )
        
        memo = brain_engine.generate_memo(fund_data)
        
        # Store in Convex
        convex_service.store_memo({
            "symbol": memo.ticker_symbol,
            "verdict": memo.recommendation.upper(),
            "confidence": memo.confidence_score,
            "summary": memo.thesis_summary,
            "reasoning": f"BULLS: {', '.join(memo.bull_case)}\nBEARS: {', '.join(memo.bear_case)}\nVALUATION: {memo.valuation_verdict}",
            "priceAtGeneration": request.price
        })
        
        convex_service.log_activity(
            action="GENERATE_MEMO",
            details=f"Generated memo for {memo.ticker_symbol} with {memo.recommendation.upper()} verdict."
        )

        return memo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain error: {str(e)}")

@app.get("/api/v1/brain/memos", tags=["Brain"])
def list_memos(limit: int = Query(50, ge=1, le=500)):
    """Get recent investment memos."""
    try:
        return convex_service.list_memos(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing memos: {str(e)}")

@app.get("/api/v1/brain/memo/{symbol}", tags=["Brain"])
def get_memo_by_symbol(symbol: str):
    """Get memo for a specific symbol."""
    try:
        return convex_service.get_memo_by_symbol(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching memo: {str(e)}")

# ─── Doctor Endpoints (Portfolio Diagnostics) ─────────────

@app.post("/api/v1/doctor/diagnose", response_model=PortfolioDiagnosis, tags=["Doctor"])
def diagnose_portfolio(request: DoctorRequest):
    """
    Analyze and diagnose a portfolio.
    
    Returns:
    - overall_health_score: 0-100
    - risk_level: low | moderate | high | extreme
    - red_flags: Critical risks
    - green_flags: Strengths
    - actionable_fixes: What to do
    """
    try:
        portfolio_items = [
            PortfolioItem(
                ticker=item["ticker"],
                allocation_percent=item["allocation"],
                avg_buy_price=item["buy_price"],
                current_price=item["current_price"]
            )
            for item in request.portfolio
        ]
        
        diagnosis = doctor_engine.diagnose_portfolio(portfolio_items, risk_appetite=request.risk_appetite)
        
        convex_service.log_activity(
            action="DIAGNOSE_PORTFOLIO",
            details=f"Diagnosed portfolio with {diagnosis.overall_health_score}/100 health."
        )
        
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doctor error: {str(e)}")

# ─── Architect Endpoints (Portfolio Construction) ────────

@app.post("/api/v1/architect/construct", response_model=ModelPortfolio, tags=["Architect"])
def construct_portfolio(request: ArchitectRequest):
    """
    Build a personalized model portfolio.
    
    Returns:
    - strategy_name: Name of the strategy
    - allocations: Asset allocation breakdown
    - expected_cagr: Expected compound annual growth rate
    - max_drawdown: Expected maximum drawdown risk
    """
    try:
        user_dna = UserDNA(
            age=request.age,
            risk_appetite=request.risk_appetite,
            capital_amount=request.capital_amount,
            investment_horizon=request.investment_horizon,
            goals=request.goals
        )
        
        portfolio = architect_engine.construct_portfolio(user_dna)
        
        convex_service.log_activity(
            action="CONSTRUCT_PORTFOLIO",
            details=f"Constructed {portfolio.strategy_name} portfolio for {request.age}y {request.risk_appetite} investor."
        )
        
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Architect error: {str(e)}")

@app.get("/api/v1/architect/templates", tags=["Architect"])
def get_portfolio_templates():
    """Get pre-built portfolio templates by risk profile."""
    return {
        "templates": [
            {
                "name": "Conservative Anchor",
                "risk": "conservative",
                "description": "Capital preservation with modest growth"
            },
            {
                "name": "Balanced Builder",
                "risk": "moderate",
                "description": "Balanced growth and stability"
            },
            {
                "name": "Aggressive Growth",
                "risk": "aggressive",
                "description": "Maximum growth for long horizons"
            }
        ]
    }

# ─── Scout Endpoints (Market Data) ────────────────────────

@app.get("/api/v1/scout/quote/{symbol}", response_model=QuoteResponse, tags=["Scout"])
def get_quote(symbol: str):
    """
    Fetch live market quote for a symbol.
    
    Symbol format: NSE_EQ|INE002A01018 (for Reliance)
    """
    try:
        # Map common ticker names to Upstox symbols
        symbol_map = {
            "RELIANCE": "NSE_EQ|INE002A01018",
            "TCS": "NSE_EQ|INE467B01029",
            "INFY": "NSE_EQ|INE009A01021",
            "HDFCBANK": "NSE_EQ|INE040A01034",
        }
        
        upstox_symbol = symbol_map.get(symbol.upper(), symbol)
        
        quote = scout_engine.get_quote(upstox_symbol)
        if not quote:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found or token invalid")
        
        return QuoteResponse(
            symbol=symbol,
            ltp=quote.get('last_price', 0),
            ohlc=quote.get('ohlc', {}),
            depth=quote.get('depth', {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scout error: {str(e)}")

@app.get("/api/v1/scout/ltp/{symbol}", tags=["Scout"])
def get_ltp(symbol: str):
    """Get Last Traded Price (LTP) for a symbol."""
    try:
        symbol_map = {
            "RELIANCE": "NSE_EQ|INE002A01018",
            "TCS": "NSE_EQ|INE467B01029",
            "INFY": "NSE_EQ|INE009A01021",
            "HDFCBANK": "NSE_EQ|INE040A01034",
            "NIFTY50": "NSE_INDEX|Nifty 50"
        }
        upstox_symbol = symbol_map.get(symbol.upper(), symbol)
        ltp = scout_engine.get_ltp(upstox_symbol)
        
        if ltp is None:
            raise HTTPException(status_code=404, detail=f"Cannot fetch LTP for {symbol}")
        
        return {"symbol": symbol, "ltp": ltp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scout error: {str(e)}")

@app.post("/api/v1/scout/ltp-multi", tags=["Scout"])
def get_ltp_multi(request: dict):
    """
    Get Last Traded Prices for multiple symbols.
    Expects: {"symbols": ["RELIANCE", "TCS", ...]}
    """
    try:
        symbols = request.get("symbols", [])
        symbol_map = {
            "RELIANCE": "NSE_EQ|INE002A01018",
            "TCS": "NSE_EQ|INE467B01029",
            "INFY": "NSE_EQ|INE009A01021",
            "HDFCBANK": "NSE_EQ|INE040A01034",
            "NIFTY50": "NSE_INDEX|Nifty 50"
        }
        
        upstox_symbols = [symbol_map.get(s.upper(), s) for s in symbols]
        prices = scout_engine.get_ltp_multi(upstox_symbols)
        
        # Map back to original requested symbols for convenience
        result = {}
        for original, upstox in zip(symbols, upstox_symbols):
            result[original] = prices.get(upstox, 2500.0) # Fallback to mock
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scout error: {str(e)}")

@app.post("/api/v1/scout/screen", tags=["Scout"])
def screen_markets(request: dict):
    """
    AI-powered natural language market scanner.
    Expects: {"query": "Cash-rich tech stocks"}
    """
    try:
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
            
        opportunities = scout_engine.screen(query)
        return {"query": query, "opportunities": opportunities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scout engine error: {str(e)}")

@app.get("/api/v1/sentinel/alerts", tags=["Sentinel"])
def get_sentinel_alerts(userId: str = Query(...)):
    """
    Fetch active risk alerts for the user.
    """
    try:
        alerts = sentinel_engine.get_alerts(userId)
        return {"userId": userId, "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentinel error: {str(e)}")

@app.post("/api/v1/backtest", tags=["TimeTravel"])
def run_backtest(request: dict):
    """
    Run historical performance simulation for a basket.
    Expects: {"assets": [...], "period": "1y"}
    """
    try:
        results = backtest_engine.simulate(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtester error: {str(e)}")

@app.get("/api/v1/scout/ohlc/{symbol}", tags=["Scout"])
def get_ohlc(symbol: str, interval: str = Query("1d")):
    """
    Get OHLC (Open, High, Low, Close) data.
    
    Intervals: 1d, 1w, 1m, I1, I5, I10, I15, I30, I60
    """
    try:
        symbol_map = {
            "RELIANCE": "NSE_EQ|INE002A01018",
            "TCS": "NSE_EQ|INE467B01029",
            "INFY": "NSE_EQ|INE009A01021",
            "HDFCBANK": "NSE_EQ|INE040A01034",
        }
        upstox_symbol = symbol_map.get(symbol.upper(), symbol)
        ohlc = scout_engine.get_ohlc(upstox_symbol, interval)
        
        if ohlc is None:
            raise HTTPException(status_code=404, detail=f"Cannot fetch OHLC for {symbol}")
        
        return {"symbol": symbol, "interval": interval, "ohlc": ohlc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scout error: {str(e)}")

# ─── Admin Endpoints ───────────────────────────────────────

@app.get("/api/v1/admin/users", tags=["Admin"])
def list_users():
    """List all registered users."""
    try:
        return convex_service.list_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")

@app.get("/api/v1/admin/activity", tags=["Admin"])
def get_activity_log(limit: int = Query(100, ge=1, le=1000)):
    """Get activity log for audit trail."""
    try:
        return convex_service.get_activity_log(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activity: {str(e)}")

# ─── Error Handlers ────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "error": str(exc),
        "status_code": 500
    }

# ─── Main ──────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 8000))
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, reload=True)
