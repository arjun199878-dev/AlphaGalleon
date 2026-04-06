# 🚀 AlphaGalleon Developer Quick Reference

Handy commands and patterns for building the app.

---

## ⚡ Quick Commands

### Start Backend
```bash
cd alphagalleon-backend
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Mobile App (Expo)
```bash
cd mobile
npm start
# Scan QR code with phone Expo Go app
```

### Start Admin Dashboard
```bash
cd admin-dashboard
npm run dev
# Opens on http://localhost:5173
```

### Deploy Everything with Docker
```bash
docker-compose up -d
# Backend runs on http://localhost:8000
```

### Run Telegram Bot
```bash
cd alphagalleon-backend
python3 telegram_bot.py
```

---

## 📡 API Endpoints Cheat Sheet

### Health Check
```bash
curl http://localhost:8000/health
```

### Brain (Investment Analysis)
```bash
# Generate memo for ticker
curl -X POST http://localhost:8000/api/v1/brain/memo \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "RELIANCE",
    "price": 2500,
    "market_cap": 1500000,
    "pe": 25,
    "sector": "Energy",
    "revenue_growth": 12,
    "profit_growth": 15,
    "debt_equity": 0.4,
    "roe": 18,
    "promoter_holding": 50,
    "news": "Stable"
  }'

# List recent memos
curl http://localhost:8000/api/v1/brain/memos

# Get memo for specific symbol
curl http://localhost:8000/api/v1/brain/memo/RELIANCE
```

### Doctor (Portfolio Diagnostics)
```bash
curl -X POST http://localhost:8000/api/v1/doctor/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [
      {"ticker": "RELIANCE", "allocation": 30, "buy_price": 2500, "current_price": 2600},
      {"ticker": "TCS", "allocation": 40, "buy_price": 3500, "current_price": 3600}
    ],
    "risk_appetite": "moderate"
  }'
```

### Architect (Portfolio Construction)
```bash
curl -X POST http://localhost:8000/api/v1/architect/construct \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "risk_appetite": "aggressive",
    "capital_amount": 500000,
    "investment_horizon": "10 years",
    "goals": "Wealth Creation"
  }'

# Get templates
curl http://localhost:8000/api/v1/architect/templates
```

### Scout (Market Data)
```bash
# Get live quote
curl http://localhost:8000/api/v1/scout/quote/RELIANCE

# Get LTP
curl http://localhost:8000/api/v1/scout/ltp/RELIANCE

# Get OHLC data
curl http://localhost:8000/api/v1/scout/ohlc/RELIANCE?interval=1d
```

### Admin
```bash
# List users
curl http://localhost:8000/api/v1/admin/users

# Get activity log
curl http://localhost:8000/api/v1/admin/activity?limit=100
```

---

## 🔧 Common Development Patterns

### Frontend API Call (React/React Native)

```typescript
// src/api/client.ts
const API_BASE = 'http://192.168.1.5:8000';  // Update your IP

export const generateMemo = async (tickerData) => {
  const response = await fetch(`${API_BASE}/api/v1/brain/memo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tickerData)
  });
  
  if (!response.ok) throw new Error('API Error');
  return await response.json();
};

export const diagnosePortfolio = async (portfolio) => {
  const response = await fetch(`${API_BASE}/api/v1/doctor/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(portfolio)
  });
  
  if (!response.ok) throw new Error('API Error');
  return await response.json();
};

export const getQuote = async (symbol) => {
  const response = await fetch(`${API_BASE}/api/v1/scout/quote/${symbol}`);
  
  if (!response.ok) throw new Error('Quote not found');
  return await response.json();
};
```

### In a Screen Component

```typescript
import { generateMemo } from '../api/client';

export const MemoScreen = () => {
  const [memo, setMemo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateMemo = async (tickerData) => {
    setLoading(true);
    try {
      const result = await generateMemo(tickerData);
      setMemo(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      {/* Form inputs */}
      {/* Display memo result */}
      {loading && <Text>Loading...</Text>}
      {error && <Text>Error: {error}</Text>}
      {memo && (
        <View>
          <Text>Recommendation: {memo.recommendation}</Text>
          <Text>Confidence: {memo.confidence_score}%</Text>
          {/* More memo details */}
        </View>
      )}
    </View>
  );
};
```

---

## 🗄️ Database Patterns (Convex)

### Create User
```typescript
// In convex/functions.ts or wherever you call
const userId = await client.mutation('users:create', {
  name: 'John Doe',
  email: 'john@example.com',
  riskProfile: 'moderate'
});
```

### Store Memo
```typescript
const memoId = await client.mutation('memos:store', {
  symbol: 'RELIANCE',
  verdict: 'BUY',
  confidence: 82,
  summary: 'Strong fundamentals...',
  reasoning: 'BULLS: ...\nBEARS: ...',
  priceAtGeneration: 2500
});
```

### Query Memos
```typescript
const recentMemos = await client.query('memos:listRecent', {
  limit: 50
});

const relianceMemos = await client.query('memos:listBySymbol', {
  symbol: 'RELIANCE'
});
```

---

## 🔐 Environment Variables

### .env Template
```bash
# Required
GOOGLE_API_KEY=sk-...
UPSTOX_ACCESS_TOKEN=...
CONVEX_URL=https://...convex.cloud

# Optional
TELEGRAM_BOT_TOKEN=...
MARKET_DATA_SOURCE=yfinance
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 🐛 Debugging Tips

### Check if Port is Available
```bash
lsof -i :8000
# Kill if needed:
kill -9 <PID>
```

### View Server Logs
```bash
# Terminal output logs
tail -f app.log

# Or run with explicit logging
python3 -m uvicorn app.main:app --reload --log-level debug
```

### Test API with curl
```bash
# Simple GET
curl http://localhost:8000/health

# POST with JSON
curl -X POST http://localhost:8000/api/v1/brain/memo \
  -H "Content-Type: application/json" \
  -d '{"ticker":"RELIANCE",...}'

# Show response headers
curl -i http://localhost:8000/health

# Verbose output
curl -v http://localhost:8000/health
```

### Check Python Syntax
```bash
python3 -m py_compile path/to/file.py
# No output = OK
```

### View Installed Packages
```bash
pip list
pip show google-generativeai
```

---

## 📱 Mobile Setup Tips

### Update API Base URL
```typescript
// mobile/src/api/config.ts
export const CONFIG = {
  API_BASE_URL: 'http://192.168.1.100:8000'  // Update your IP
};
```

### Find Your Computer's IP
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr /i "ipv4"
```

### Ensure Phone & Computer are on Same WiFi
- Both connected to same WiFi network
- Firewall allows port 8000
- Backend server running: `uvicorn app.main:app --reload`

---

## 🚀 Docker Commands

### Build Image
```bash
docker build -f alphagalleon-backend/Dockerfile -t alphagalleon:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e UPSTOX_ACCESS_TOKEN=$UPSTOX_ACCESS_TOKEN \
  -e CONVEX_URL=$CONVEX_URL \
  alphagalleon:latest
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all
docker-compose down

# View logs
docker-compose logs -f backend

# Rebuild
docker-compose up -d --build
```

---

## 🧪 Testing

### Test Brain Module (Python)
```python
from app.brain import Brain
from app.schemas import Ticker, FundamentalData

brain = Brain()
ticker = Ticker(symbol="RELIANCE", name="RELIANCE", sector="Energy", 
                current_price=2500, market_cap=1500000, pe_ratio=25)
fund_data = FundamentalData(ticker=ticker, revenue_growth_3y=12, 
                            profit_growth_3y=15, ...)
memo = brain.generate_memo(fund_data)
print(memo.recommendation)  # Should be BUY/SELL/HOLD
```

### Test Doctor Module (Python)
```python
from app.doctor import Doctor
from app.doctor_schema import PortfolioItem

doctor = Doctor()
portfolio = [
    PortfolioItem(ticker="RELIANCE", allocation_percent=30, 
                  avg_buy_price=2500, current_price=2600)
]
diagnosis = doctor.diagnose_portfolio(portfolio, risk_appetite="moderate")
print(diagnosis.overall_health_score)  # Should be 0-100
```

---

## 📚 Key Files to Know

```
alphagalleon-backend/
├── app/
│   ├── main.py              ← All API endpoints defined here
│   ├── brain.py             ← Investment analysis
│   ├── doctor.py            ← Portfolio diagnosis
│   ├── architect.py         ← Portfolio construction
│   ├── scout.py             ← Market data
│   ├── convex_service.py    ← Database operations
│   └── schemas.py           ← Pydantic models
├── telegram_bot.py          ← Telegram interface
├── requirements.txt         ← Python dependencies
├── Dockerfile               ← Container config
└── .env.example             ← Environment template

mobile/
├── src/
│   ├── api/
│   │   ├── config.ts        ← Update API_BASE_URL here
│   │   └── client.ts        ← API call functions
│   ├── screens/             ← UI components to wire
│   └── navigation/          ← Screen navigation
└── package.json             ← Node dependencies

admin-dashboard/
├── src/
│   ├── pages/               ← Dashboard pages
│   ├── components/          ← Reusable components
│   └── App.tsx              ← Main app
└── package.json             ← Dependencies
```

---

## ⚠️ Common Mistakes

1. **Wrong IP in mobile config** — Update `API_BASE_URL` to your computer's IP
2. **Port 8000 already in use** — Kill process: `lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9`
3. **API key missing** — Ensure .env file exists and is filled
4. **Phone can't reach backend** — Check firewall, ensure same WiFi
5. **Frontend not wired** — API exists, but screens don't call it yet

---

## 📞 Getting Help

1. **Backend won't start?** Check: `python3 -m py_compile alphagalleon-backend/app/main.py`
2. **Can't connect from phone?** Check: `ifconfig` to get IP, ensure firewall allows 8000
3. **API returns error?** Check: Server logs, verify .env file
4. **Convex connection fails?** Check: `CONVEX_URL` in .env matches deployment

---

**Last Updated:** Feb 27, 2026
**Maintained by:** AlphaGalleon Dev Team
