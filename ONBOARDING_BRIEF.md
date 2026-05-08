# AlphaGalleon: Project Master Brief (Partner & Developer Onboarding)

Welcome to **AlphaGalleon**. Whether you are a new human partner, a senior engineer, or an incoming AI agent, this document is your complete brain-dump of the project. 

AlphaGalleon is not a chatbot; it is a fully autonomous, AI-driven institutional wealth manager. It bridges the critical gap in modern FinTech: it doesn't just give financial advice, it physically executes that advice on the open stock market while mathematically protecting the user's capital.

---

## 📊 1. Project Completion Status

As of right now, **MVP Version 1.0 is 100% Complete**.

**Technical Completion (100%):**
* **Frontend Mobile App:** 100% (Auth, UI, Navigation, Expo EAS build configs).
* **Backend Intelligence API:** 100% (FastAPI routing, AI prompts, PyTest coverage).
* **Broker Integration:** 100% (Upstox OAuth, Live Holdings Sync, Limit Order Execution).
* **Database & Infrastructure:** 100% (Convex serverless state, Dockerfiles, Render.yaml).

**Non-Technical / Business Completion (Phase 1 Ready):**
* **Product-Market Fit Blueprint:** Defined. Targeting retail investors who want algorithmic edge without learning how to code Quant strategies.
* **Compliance / Legal:** 0% (Pending). *Crucial Note for Partners:* Because the AI generates direct financial recommendations and places limit orders, launching this publicly requires strict navigation of SEBI (India) or SEC (US) Registered Investment Advisor (RIA) regulations. Currently, the app utilizes a "Sandbox / Paper Trading" mode to bypass this legal hurdle during beta testing.
* **Go-To-Market / Marketing:** 0%. The tech is ready to scale; the business pipeline needs to be built.

---

## 🛠️ 2. The Complete Technology Stack

Every piece of technology was chosen for speed, scalability, and serverless edge-execution.

* **Frontend Framework:** `React Native` (built via `Expo`). Allows us to write TypeScript once and compile native `.apk` (Android) and `.ipa` (iOS) files.
* **Backend Framework:** `Python` & `FastAPI`. Python is mandatory for quantitative finance and AI data parsing. FastAPI ensures asynchronous, high-speed HTTP routing.
* **Database & State:** `Convex`. A serverless backend platform. We use it to store user profiles, encrypt OAuth tokens, store live portfolio holdings, and run background serverless `Crons` (scheduled jobs).
* **AI / Large Language Model:** `Google Gemini API`. Chosen for its massive context window and rapid inference speed.
* **Brokerage API:** `Upstox API V2`. Upstox provides reliable OAuth linkage, live portfolio fetching, and limit-order execution.
* **Market Data Fallback:** `Yahoo Finance (yfinance)`. Used by the backend to fetch historical OHLC (Open, High, Low, Close) candles if Upstox limits are hit.
* **Testing Infrastructure:** `PyTest` & `PyTest-Asyncio`. Used to mathematically verify the app's output without risking real money.
* **Deployment:** `Docker` & `Render.yaml` (Backend containerization), `EAS` (Expo Application Services for cloud mobile builds).

---

## ⚙️ 3. The AlphaGalleon Pipeline (How It Actually Works)

The entire application is a continuous, self-feeding loop. Here is the exact sequence of events, broken down individually:

### Step 1: `Fetch Data (Scout)`
* **What it is:** The `scout.py` module.
* **How it works:** AI models (like Gemini) do not know what the stock market is doing today; their training data is old. The Scout is the sensory organ. Whenever the app needs to make a decision, the Scout reaches out to Upstox or Yahoo Finance to pull the **Last Traded Price (LTP)** or historical charts. It feeds pure, hard numbers into the system so the AI is never blind.

### Step 2: `Analyze (Doctor / Brain)`
* **What it is:** The `run_doctor.py` and `run_brain.py` modules.
* **How it works:** When a user links their Upstox account, their live holdings are synced to our Convex database. The "Doctor" module pulls this data and hands it to the "Brain" (Gemini LLM). The Brain has strict system prompts forcing it to act as a Chief Risk Officer. It analyzes the user's current money, identifies massive risks (e.g., "You have 90% of your net worth in banking stocks"), and generates a strict JSON diagnostic report suggesting what to sell or hold.

### Step 3: `Generate Strategy (Architect)`
* **What it is:** The `run_architect.py` module.
* **How it works:** The user tells the app: *"I have ₹100,000. Build me an aggressive tech portfolio."* The Architect asks the Brain to pick the best 5 stocks. The Architect then asks the Scout for the exact price of those 5 stocks right now. It does the math to figure out exactly how many shares the user can afford, and packages this into a "Basket" of limit orders.

### Step 4: `Verify Math (Backtester)`
* **What it is:** The `backtester.py` module.
* **How it works:** We cannot trust AI with real money blindly. Before the Architect's basket is shown to the user, the Backtester time-travels. It asks the Scout for 1-year historical data on the chosen stocks. It calculates the **CAGR (Compound Annual Growth Rate)** and the **Maximum Drawdown** (the worst possible loss). If the numbers are safe, it approves the basket.

### Step 5: `Execute Capital (Upstox)`
* **What it is:** The `upstox_execute.py` module.
* **How it works:** The user sees the verified basket on their phone and clicks "Execute". The backend intercepts their encrypted Upstox token and fires real `POST` HTTP requests to the Upstox Exchange, placing live Buy/Sell limit orders. 
* *Note:* If the user clicks "Paper Trade" instead, the system triggers `sandbox=True`, bypassing Upstox and faking the trade internally so users can test strategies for free.

### Step 6: `Monitor Continuously (Sentinel)`
* **What it is:** The `sentinel.py` and Convex Crons module.
* **How it works:** AlphaGalleon never sleeps. We built a serverless Cron job in Convex that fires every single day at market close. It triggers the Python backend to loop through every single user's portfolio. The Sentinel asks the Scout: *"Did any of these stocks crash today?"* If a risk threshold is breached, the Sentinel bypasses the mobile app entirely and fires an urgent **Push Notification** directly to the user's phone lock-screen advising them to open the app and restructure.

---

### 🚀 Next Steps for a New Partner
1. **Read the Code:** Start by reviewing `alphagalleon-backend/app/main.py` to see the FastAPI routes, then trace them down to the individual agents.
2. **Setup Local Dev:** Run `npm start` in the `/mobile` folder, and `uvicorn app.main:app` in the `/alphagalleon-backend` folder.
3. **Plan Phase 2:** MVP 1.0 is done. Phase 2 should focus on legal compliance, adding more brokerages (Zerodha/Groww), and building a subscription paywall.
