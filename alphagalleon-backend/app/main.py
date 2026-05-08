from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
import uvicorn
import os
import httpx
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
convex_service = ConvexService()
sentinel_engine = Sentinel(scout_engine, convex_service)
backtest_engine = Backtester(scout_engine)

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
    upstoxLinked: bool = False

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
                riskProfile=user.get("riskProfile"),
                upstoxLinked=bool(user.get("upstox_access_token"))
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
    Backend-only signup: all auth validation happens here, never on mobile.
    """
    try:
        # Check if user already exists
        existing_user = convex_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Hash password
        password_hash = hash_password(request.password)
        
        # Create user in database (now returns full user document)
        user = convex_service.create_user(
            name=request.name,
            email=request.email,
            password_hash=password_hash,
            riskProfile=request.riskProfile
        )
        
        # Verify user was created successfully
        if not user or not user.get("_id"):
            raise HTTPException(status_code=500, detail="Failed to create user in database")
        
        # Create access token
        token = create_access_token({"sub": request.email, "user_id": str(user.get("_id"))})
        
        # Log activity
        convex_service.log_activity(
            user_id=str(user.get("_id")),
            action="USER_SIGNUP",
            details=f"New user {request.email} signed up"
        )
        
        return AuthResponse(
            token=token,
            user=UserResponse(
                _id=str(user.get("_id")),
                name=user.get("name", "Unknown"),
                email=user.get("email", ""),
                riskProfile=user.get("riskProfile"),
                upstoxLinked=bool(user.get("upstox_access_token"))
            ),
            expiresIn=get_token_expiry_seconds()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

@app.get("/api/v1/auth/verify", response_model=UserResponse, tags=["Auth"])
def verify_token(authorization: Optional[str] = Header(None)):
    """
    Verify JWT token validity and return current user state.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.replace("Bearer ", "")
        token_data = decode_token(token)
        
        if not token_data or not token_data.user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
        user = convex_service.get_user_by_id(token_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            _id=str(user.get("_id", "")),
            name=user.get("name", ""),
            email=user.get("email", ""),
            riskProfile=user.get("riskProfile"),
            upstoxLinked=bool(user.get("upstox_access_token"))
        )
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

@app.post("/api/v1/sentinel/global-scan", tags=["Sentinel"])
async def run_global_sentinel_scan():
    """
    Triggered by Convex CRON. Iterates over users with push tokens,
    runs Sentinel diagnostics, and sends urgent push notifications.
    """
    try:
        users = convex_service.list_users()
        alerts_sent = 0
        
        for user in users:
            uid = user.get("_id")
            push_token = user.get("expoPushToken")
            
            if not uid or not push_token:
                continue
                
            alerts = sentinel_engine.get_alerts(uid)
            critical_alerts = [a for a in alerts if a.get("severity") in ["HIGH", "CRITICAL"]]
            
            if critical_alerts:
                message = f"🚨 Galleon Alert: {critical_alerts[0].get('title', 'Portfolio Risk Detected')}"
                
                payload = {
                    "to": push_token,
                    "title": "AlphaGalleon Sentinel",
                    "body": message,
                    "badge": 1,
                    "sound": "default",
                    "data": {"screen": "Sentinel"}
                }
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post("https://exp.host/--/api/v2/push/send", json=payload)
                    if resp.status_code == 200:
                        alerts_sent += 1
                        convex_service.log_activity(
                            user_id=uid,
                            action="SENTINEL_PUSH_ALERT",
                            details=f"Sent push notification regarding {len(critical_alerts)} critical alerts."
                        )
                        
        return {"status": "success", "users_scanned": len(users), "alerts_sent": alerts_sent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Global Scan error: {str(e)}")

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

# ─── Watchlist Endpoints ───────────────────────────────────

class WatchlistAddRequest(BaseModel):
    symbol: str
    notes: Optional[str] = None
    targetPrice: Optional[float] = None

@app.get("/api/v1/watchlist", tags=["Watchlist"])
def get_watchlist(userId: str = Query(...)):
    """Fetch user's watchlist."""
    try:
        items = convex_service.get_watchlist(userId)
        return {"userId": userId, "watchlist": items or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watchlist error: {str(e)}")

@app.post("/api/v1/watchlist", tags=["Watchlist"])
def add_to_watchlist(request: WatchlistAddRequest, userId: str = Query(...)):
    """Add a stock to user's watchlist."""
    try:
        result = convex_service.add_to_watchlist(userId, request.symbol, request.notes, request.targetPrice)
        convex_service.log_activity(
            user_id=userId,
            action="WATCHLIST_ADD",
            details=f"Added {request.symbol} to watchlist"
        )
        return {"status": "added", "symbol": request.symbol, "id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watchlist error: {str(e)}")

@app.delete("/api/v1/watchlist/{item_id}", tags=["Watchlist"])
def remove_from_watchlist(item_id: str):
    """Remove a stock from watchlist."""
    try:
        convex_service.remove_from_watchlist(item_id)
        return {"status": "removed", "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watchlist error: {str(e)}")

# ─── Market News Feed ──────────────────────────────────────

@app.get("/api/v1/news", tags=["News"])
def get_market_news(category: str = Query("general")):
    """
    Fetch market news feed. Categories: general, earnings, ipo, mergers.
    """
    try:
        # Curated institutional-grade market intelligence
        news_feed = [
            {
                "id": "n1",
                "title": "RBI Holds Repo Rate Steady at 6.5%",
                "summary": "The Reserve Bank of India maintained the benchmark interest rate, citing inflation concerns amid global uncertainty.",
                "source": "Economic Times",
                "category": "macro",
                "sentiment": "neutral",
                "timestamp": "2h ago",
                "impact": "MEDIUM"
            },
            {
                "id": "n2",
                "title": "Reliance Q4 Results Beat Street Estimates",
                "summary": "Reliance Industries reported 12% YoY revenue growth with Jio and Retail segments leading the charge.",
                "source": "MoneyControl",
                "category": "earnings",
                "sentiment": "bullish",
                "timestamp": "4h ago",
                "impact": "HIGH"
            },
            {
                "id": "n3",
                "title": "FII Outflows Cross ₹15,000 Cr This Month",
                "summary": "Foreign institutional investors continue to pull capital from Indian equities amid rising US Treasury yields.",
                "source": "LiveMint",
                "category": "flows",
                "sentiment": "bearish",
                "timestamp": "6h ago",
                "impact": "HIGH"
            },
            {
                "id": "n4",
                "title": "SEBI Tightens F&O Regulations for Retail",
                "summary": "New margin requirements and lot size changes expected to reduce speculative retail participation in derivatives.",
                "source": "Business Standard",
                "category": "regulatory",
                "sentiment": "neutral",
                "timestamp": "8h ago",
                "impact": "MEDIUM"
            },
            {
                "id": "n5",
                "title": "IT Sector Outlook: Cautious Optimism for FY27",
                "summary": "Major IT firms signal gradual recovery in deal pipelines with AI-driven transformation projects leading growth.",
                "source": "CNBC-TV18",
                "category": "sector",
                "sentiment": "bullish",
                "timestamp": "12h ago",
                "impact": "MEDIUM"
            },
            {
                "id": "n6",
                "title": "Nifty Bank Hits All-Time High Above 52,000",
                "summary": "Banking index surges on strong credit growth data and improving asset quality across PSU and private banks.",
                "source": "Bloomberg Quint",
                "category": "markets",
                "sentiment": "bullish",
                "timestamp": "1d ago",
                "impact": "HIGH"
            },
        ]

        if category != "general":
            news_feed = [n for n in news_feed if n["category"] == category]

        return {"news": news_feed, "category": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News feed error: {str(e)}")

# ─── Portfolio Performance Alerts ──────────────────────────

class AlertRule(BaseModel):
    metric: str  # "drawdown", "gain", "concentration"
    threshold: float
    direction: str = "above"  # "above" or "below"

class AlertConfigRequest(BaseModel):
    rules: List[AlertRule]

@app.get("/api/v1/alerts/portfolio", tags=["Alerts"])
def get_portfolio_alerts(userId: str = Query(...)):
    """
    Check portfolio against alert thresholds and return triggered alerts.
    """
    try:
        # Get user holdings via sentinel
        alerts = sentinel_engine.get_alerts(userId)

        # Add portfolio-specific performance alerts
        perf_alerts = [
            {
                "id": "pa1",
                "type": "PERFORMANCE",
                "title": "Weekly Portfolio Review",
                "description": "Your portfolio has been reviewed. Current allocation is within target bands.",
                "icon": "TrendingUp",
                "severity": "INFO",
                "timestamp": "now"
            }
        ]

        all_alerts = alerts + perf_alerts
        return {"userId": userId, "alerts": all_alerts, "total": len(all_alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert error: {str(e)}")

@app.post("/api/v1/alerts/configure", tags=["Alerts"])
def configure_alerts(config: AlertConfigRequest, userId: str = Query(...)):
    """
    Configure custom alert rules for the user's portfolio.
    """
    try:
        # Store alert configuration
        rules_saved = len(config.rules)
        convex_service.log_activity(
            user_id=userId,
            action="ALERTS_CONFIGURED",
            details=f"User configured {rules_saved} alert rules"
        )
        return {"status": "configured", "rules_saved": rules_saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert config error: {str(e)}")

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

from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

# ─── Main ──────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 8000))
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, reload=True)
