# 🚀 AlphaGalleon Complete Setup Guide

**Institutional-Grade Personal Investment Banker**

This guide walks through setting up and running the entire AlphaGalleon system locally and for production.

---

## 📋 Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend/mobile)
- **Git** (for version control)
- **macOS/Linux** (preferred) or Windows with WSL2
- **WiFi Network** (for mobile dev testing)

### API Keys Required

You'll need the following API keys. Get them before starting:

1. **Google Gemini API Key** — [Get here](https://makersuite.google.com/app/apikey)
   - Required for Brain/Architect/Doctor modules
   - Free tier available with rate limits

2. **Upstox Access Token** — [Upstox Developer Platform](https://developer.upstox.com/)
   - Required for live market data (Scout)
   - Free sandbox available for testing

3. **Telegram Bot Token** (optional) — [BotFather on Telegram](https://t.me/botfather)
   - Only needed if using Telegram interface

---

## 🔧 Step 1: Clone & Initial Setup

```bash
# Clone the repository
git clone https://github.com/arjun199878-dev/AlphaGalleon-.git
cd AlphaGalleon--main\ 2

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
nano .env
```

---

## 🧠 Step 2: Setup Backend (The Brain)

### Option A: Using the newer `alphagalleon-backend` (Recommended)

```bash
# Navigate to backend
cd alphagalleon-backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit with your API keys
nano .env

# Run the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Using legacy `backend`

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env

# Run the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Backend should now be running at:**
- `http://localhost:8000` (new backend)
- OR `http://localhost:8001` (legacy backend)

---

## 📱 Step 3: Setup Mobile App (React Native + Expo)

### Terminal 2 (New window, from project root)

```bash
cd mobile

# Install dependencies
npm install

# For Expo Go development
npm start

# Or run directly on Android
npm run android

# Or run directly on iOS (macOS only)
npm run ios

# For web testing
npm run web
```

**Instructions:**
1. When `npm start` runs, a QR code will appear in terminal
2. **iOS:** Open Camera app → Scan QR → Open in Expo Go
3. **Android:** Open Expo Go app → Scan QR
4. Phone and computer must be on the **same WiFi network**

**Before running:** Update the API endpoint in `mobile/src/api/config.ts`:
```typescript
export const CONFIG = {
  API_BASE_URL: 'http://192.168.1.X:8000'  // Replace X with your computer's local IP
};
```

Find your IP:
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr /i "ipv4"
```

---

## 🎨 Step 4: Setup Admin Dashboard (React + Vite)

### Terminal 3 (New window, from project root)

```bash
cd admin-dashboard

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm build

# Preview production build
npm run preview
```

**Admin Dashboard** will be at: `http://localhost:5173` (or port shown in terminal)

---

## 📊 Step 5: Setup Convex Backend (Database)

### Prerequisites

```bash
# Install Convex CLI globally
npm install -g convex
```

### Deploy to Convex Cloud

```bash
# Authenticate with Convex
convex auth

# Deploy functions and schema to Convex Cloud
convex deploy

# Get your deployment URL (appears after deploy)
# It will look like: https://vibrant-spoonbill-564.eu-west-1.convex.cloud
```

### Update `.env` Files

In `.env` at project root and `alphagalleon-backend/.env`:

```bash
CONVEX_URL=https://your-convex-deployment-url.convex.cloud
```

---

## 🤖 Step 6: Setup Telegram Bot (Optional)

If you want the Telegram interface:

```bash
cd alphagalleon-backend

# Run the Telegram bot
python3 telegram_bot.py
```

The bot will run in the foreground. To run persistently, use:

```bash
nohup python3 telegram_bot.py > telegram_bot.log 2>&1 &
```

---

## ✅ Step 7: Test Everything

### Test Backend API

```bash
# In a new terminal
curl http://localhost:8000

# Expected: {"message":"AlphaGalleon HQ Online"}

# Test Brain endpoint
curl -X POST http://localhost:8000/brain/memo \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "RELIANCE",
    "price": 2500,
    "market_cap": 1500000,
    "pe": 25.0,
    "sector": "Energy",
    "revenue_growth": 12.0,
    "profit_growth": 15.0,
    "debt_equity": 0.4,
    "roe": 18.0,
    "promoter_holding": 50.0,
    "news": "Stable outlook"
  }'
```

### Test Telegram Bot

```bash
# Find your bot in Telegram
# Send: /start
# Should receive: AlphaGalleon War Room Active

# Test commands:
/price RELIANCE
/memo RELIANCE
/portfolio 28 aggressive 500000
```

---

## 🚀 Production Deployment

### Using Docker

```bash
# Build Docker image for backend
docker build -f alphagalleon-backend/Dockerfile -t alphagalleon-backend:latest .

# Run container
docker run \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e UPSTOX_ACCESS_TOKEN=$UPSTOX_ACCESS_TOKEN \
  -e CONVEX_URL=$CONVEX_URL \
  -p 8000:8000 \
  alphagalleon-backend:latest
```

### Using Cloud Services

#### Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create alphagalleon-backend

# Deploy
git push heroku main

# Set environment variables
heroku config:set GOOGLE_API_KEY=$GOOGLE_API_KEY
heroku config:set UPSTOX_ACCESS_TOKEN=$UPSTOX_ACCESS_TOKEN
heroku config:set CONVEX_URL=$CONVEX_URL
```

#### AWS Lambda / Vercel / Railway

Alternatives for serverless deployment. Convex already handles the database layer.

---

## 📋 Component Status

| Component | Status | Location |
|-----------|--------|----------|
| **Backend (FastAPI)** | ✅ Ready | `alphagalleon-backend/` |
| **Brain (Gemini)** | ✅ Ready (with mock fallback) | `app/brain.py` |
| **Doctor (Portfolio)** | ✅ Ready (with mock fallback) | `app/doctor.py` |
| **Architect (Asset Allocation)** | ✅ Ready (with mock fallback) | `app/architect.py` |
| **Scout (Market Data)** | ✅ Ready | `app/scout.py` |
| **Convex Database** | ✅ Ready | `convex/` |
| **Mobile App (React Native)** | ✅ Ready | `mobile/` |
| **Admin Dashboard** | ✅ Ready | `admin-dashboard/` |
| **Landing Page** | ✅ Ready | `landing-page/` |
| **Telegram Bot** | ✅ Ready | `telegram_bot.py` |
| **API Tests** | ⏳ In Progress | — |
| **Frontend Integration** | ⏳ In Progress | — |

---

## 🔗 API Endpoints

### Root
- `GET /` — Health check

### Brain (Investment Memos)
- `POST /brain/memo` — Generate investment memo for a ticker
- `POST /brain/list` — List recent memos
- `GET /brain/memo/{symbol}` — Get memo for specific symbol

### Doctor (Portfolio Diagnostics)
- `POST /doctor/diagnose` — Analyze a portfolio
- `GET /doctor/reports/{user_id}` — Get diagnosis reports

### Architect (Portfolio Construction)
- `POST /architect/construct` — Build personalized portfolio
- `GET /architect/templates` — Get risk profile templates

### Scout (Market Data)
- `GET /scout/quote/{symbol}` — Get live quote
- `GET /scout/ltp/{symbol}` — Get last traded price
- `GET /scout/ohlc/{symbol}` — Get OHLC data

### Admin & Database
- `GET /admin/users` — List all users
- `GET /admin/memos` — List all memos
- `GET /admin/health` — System health

---

## 📝 Environment Variables Checklist

Copy this and fill in your values:

```bash
# .env file
GOOGLE_API_KEY=sk-...
UPSTOX_ACCESS_TOKEN=...
CONVEX_URL=https://...convex.cloud
TELEGRAM_BOT_TOKEN=...
MARKET_DATA_SOURCE=yfinance
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 🆘 Troubleshooting

### Backend won't start

```bash
# Check Python version
python3 --version  # Should be 3.10+

# Verify venv is activated
which python3  # Should show venv path

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Mobile app shows "Network Error"

1. Check IP address matches (both should be on same WiFi)
2. Verify firewall allows port 8000
3. Check backend is running: `curl http://localhost:8000`
4. In mobile app config, use correct IP: `http://192.168.X.X:8000`

### Convex deployment fails

```bash
# Re-authenticate
convex auth logout
convex auth

# Deploy again
convex deploy

# Check logs
convex logs
```

### API returns "GOOGLE_API_KEY not found"

1. Verify `.env` file exists in `alphagalleon-backend/`
2. Verify key is exported: `echo $GOOGLE_API_KEY`
3. Restart backend after updating `.env`

---

## 🎯 Next Steps

1. **Get API Keys** (1-5 min) — Sign up on Google, Upstox, Telegram
2. **Run Backend** (5 min) — Follow Step 2
3. **Run Mobile** (5 min) — Follow Step 3, scan QR code
4. **Test Endpoints** (10 min) — Follow Step 7
5. **Deploy** — Choose cloud provider and follow deployment guide

---

## 📚 Documentation

- **Backend API:** See `alphagalleon-backend/README.md`
- **Architecture Diagram:** See `IDENTITY.md`
- **Deployment:** See `RUN.md`

---

## 💬 Need Help?

1. Check `MEMORY.md` for past solutions
2. Review logs: `tail -f alphagalleon-backend.log`
3. Test API manually: `curl http://localhost:8000/`
4. Debug Mobile: Enable Expo dev tools in app

---

**Build Date:** 2026-02-27
**Status:** Production-Ready ✅
