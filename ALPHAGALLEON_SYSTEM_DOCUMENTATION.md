# AlphaGalleon System Documentation

**AlphaGalleon** is an autonomous, AI-driven institutional wealth management platform. It bridges the gap between passive algorithmic analysis and active market execution. By connecting directly to user brokerage accounts (like Upstox) and utilizing advanced Large Language Models (Google Gemini), AlphaGalleon evaluates, constructs, and executes financial portfolios in real-time.

This document serves as the absolute source of truth regarding how the engine works, what each autonomous "Agent" is responsible for, and how the internal pipeline routes real capital safely.

---

## 1. The Core Architecture

The platform operates across three main technological pillars:
1. **The Client Interface (React Native / Web):** The consumer-facing mobile application built on Expo, alongside a web-based Admin Dashboard. This is the UI where users connect their brokerages and view their "Vault".
2. **The Intelligence Backend (Python / FastAPI):** A high-performance Python server that houses the LLM orchestration logic, the math verification engines, and the API pipelines to the Upstox exchange.
3. **The State Manager (Convex):** A serverless, real-time database that securely stores OAuth tokens, live holdings, cron-job scheduling, and push-notification device tokens.

---

## 2. The AI Agents & Engine Modules

AlphaGalleon relies on highly specialized Python scripts, often referred to as "Agents." Each agent has a very strict mandate.

### 🧠 The Brain (`run_brain.py` / `run_brain_live.py`)
**What it is:** The central cognitive orchestrator.
**What it does:** The Brain is the wrapper around the Google Gemini Large Language Model (LLM). On its own, an LLM is dangerous in finance because it hallucinates math. The Brain enforces strict system prompts and output schemas (JSON). It is responsible for taking raw data provided by other modules, applying quantitative reasoning, and returning structured financial insights. It essentially acts as the "Chief Investment Officer."

### 📡 The Fetcher / Scout (`scout.py`)
**What it is:** The sensory organ of the platform. The Brain is completely blind without the Scout.
**What it does:** The Scout is responsible for reaching out to the actual internet to get real financial data. It connects to Yahoo Finance (yfinance) and Upstox API V2. Whenever another module needs to know the Last Traded Price (LTP), the daily open/close, or the 1-year historical OHLC (Open, High, Low, Close) candles of a specific ticker (e.g., `RELIANCE` or `NIFTY50`), the Scout fetches it. It strictly returns clean, hard numbers back to the internal system.

### 🏗️ The Architect (`run_architect.py`)
**What it is:** The Portfolio Constructor.
**What it does:** When a user opens the mobile app and says, *"Build me an aggressive tech-heavy portfolio with ₹50,000"*, the Architect takes over. 
1. It queries the Brain to select the best 5-10 stocks for that specific prompt.
2. It queries the Scout to get the exact real-time prices of those stocks.
3. It performs the mathematics to figure out exactly how many shares the user can afford given their capital constraints.
4. It outputs a complete, ready-to-execute "Basket" containing tickers, quantities, and limit prices.

### 🩺 The Doctor (`run_doctor.py`)
**What it is:** The Diagnostic Engine.
**What it does:** The Doctor evaluates the user's *existing* money. It looks into the Convex database at the user's "Vault" (their currently held stocks). It analyzes the sector allocation (e.g., "You are 80% exposed to banking"), calculates risk metrics, and uses the Brain to generate a health score. It then suggests precise rebalancing actions (e.g., "Sell 10 shares of HDFC to buy IT stocks").

### 🛡️ The Sentinel (`sentinel.py`)
**What it is:** The Automated Risk Watchdog.
**What it does:** This is the retention loop of the app. Powered by Convex Native Crons, the Sentinel is automatically triggered every day at market close (e.g., 10:30 AM UTC / 4:00 PM IST). 
1. It loops through every single user in the database.
2. It pulls their live portfolio.
3. It asks the Scout if any of those stocks crashed significantly today.
4. If a critical risk threshold is crossed, it bypasses the app entirely and blasts a Push Notification directly to the user's phone lock screen using the Expo Push API.

### ⏱️ The Backtester (`backtester.py`)
**What it is:** The Time-Travel Engine.
**What it does:** Before a user buys a basket suggested by the Architect, they need proof it works. The Backtester takes the proposed basket, asks the Scout for historical pricing data (1-year/5-year), and runs mathematical simulations. It calculates the **CAGR (Compound Annual Growth Rate)** and the **Maximum Drawdown** (the biggest loss the portfolio would have suffered). This provides mathematical safety checks before execution.

---

## 3. The Live Execution Engine (Broker Integration)

AlphaGalleon doesn't just give advice; it executes trades. It uses Upstox as the primary broker.

1. **The Handshake (`upstox_auth.py`):** When a user clicks "Link Broker", the app opens a secure webview to Upstox. Once the user logs in, Upstox returns an OAuth token. The backend intercepts this token and encrypts it safely into the user's Convex database profile.
2. **Live Sync (`upstox_holdings.py`):** Once linked, the user can click "Sync Broker" in the Vault. The backend reaches into Upstox, downloads their massive array of currently held positions, wipes their old AlphaGalleon portfolio, and replaces it with the exact, live data. This is how the AI knows exactly what the user owns.
3. **The Trigger (`upstox_execute.py`):** When a user approves an Architect Basket, this script loops through the basket items and fires real API POST requests to the Upstox `/v2/order/place` endpoint, placing limit orders on the open market.
4. **The Sandbox (Paper Trading):** Built directly into `upstox_execute.py`, if the user selects "Paper Trade", the backend intercepts the order *before* it hits Upstox. It fakes a successful order and returns `PAPER-UUID` trackers, allowing users to test the AI's strategies without risking real capital.

---

## 4. Testing & Safety Protocol

To ensure the AI doesn't hallucinate math that bankrupts users, the entire financial calculation layer is wrapped in a **PyTest Automation Suite** (`tests/test_backtester.py` & `tests/test_upstox_execute.py`). 
* It mathematically verifies that multi-asset blending returns exact weighted averages.
* It proves that unauthorized API hits (missing headers) return 401s.
* It proves that users without an Upstox Token are blocked with a 403 error before an order executes.

---

## Conclusion
AlphaGalleon is a fully enclosed loop:
`Fetch Data (Scout)` ➔ `Analyze (Doctor/Brain)` ➔ `Generate Strategy (Architect)` ➔ `Verify Math (Backtester)` ➔ `Execute Capital (Upstox)` ➔ `Monitor Continuously (Sentinel)`. 

Every module acts independently but feeds into the single goal of autonomous wealth compounding.
