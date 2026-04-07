# AlphaGalleon: Architecture & Project State Documentation

**Date:** April 2026
**Status:** Phase 9 (Hardening, Deployment Prep, & Feature Completion)

---

## 1. Project Overview
**AlphaGalleon** is an institutional-grade, sentient personal investment engine designed for retail investors. It acts as a comprehensive "AI Hedge Fund Manager in your pocket." Rather than just showing charts, it dynamically analyzes portfolios, builds investment memos, suggests rebalancing, and ultimately executes trades.

The platform is designed with a premium, sleek aesthetic ("vibrant dark mode, glassmorphism") to ensure the retail user feels they are using a multi-million-dollar institutional terminal.

---

## 2. Tech Stack & Infrastructure
*   **Mobile Client (Frontend):** React Native (Expo CLI), TypeScript, Lucide Icons, Custom Theming Hook.
*   **Backend Server:** Python 3.11, FastAPI, Pydantic (Type validation).
*   **Database (Serverless):** Convex (Real-time sync, schema-enforced NoSQL).
*   **Containerization:** Docker, Docker Compose.
*   **CI/CD Pipeline:** GitHub Actions (for automated type-checking and Docker build verification).
*   **Version Control:** Git & GitHub.
*   **AI Engine:** Google Gemini Pro (`google-generativeai`).
*   **Brokerage API:** Upstox API (OAuth & Trading).

---

## 3. Core AI Modules ("The Hub")
AlphaGalleon is powered by 5 distinct AI personalities/engines:

1.  **The Brain (Investment Memos):** Generates high-confidence buy/sell theses based on fundamental and macro data using Google Gemini.
2.  **The Doctor (Risk Diagnosis):** Algorithmically scans existing portfolios for concentration risk, sector overlap, and drawdown threats. Returns a 0-100 "Health Score" with severity-graded alerts.
3.  **The Architect (Portfolio Construction):** Suggests optimized allocation strategies (e.g., finding the efficient frontier) based on user risk profiles (Conservative, Moderate, Aggressive).
4.  **The Scout (Dynamic Screener):** Natural language stock screener (e.g., "Find me undervalued Indian EV stocks with low debt").
5.  **The Sentinel (Real-time Watcher):** Curated institutional-grade market news feed and real-time portfolio performance alerts (e.g., "Target gain hit", "Excessive drawdown").

---

## 4. Completed Features & Integrations (What Has Been Done)

✅ **Database Architecture (Convex)**
*   Fully defined `schema.ts` supporting `users`, `portfolios`, `holdings`, `watchlist`, `memos`, `diagnoses`, `backtests`, and `activityLog`.
*   Realtime queries and mutations active.

✅ **Backend Server (FastAPI)**
*   Robust REST API architecture structured in `app/main.py`.
*   Pydantic V2 models built for strict type safety and request validation. `Field(alias="_id")` configured to ensure seamless translation between Convex IDs and Python logic.
*   Integrated Convex Python SDK (`convex_service.py`) to manage backend-to-database communication.

✅ **Mobile App (React Native)**
*   Custom iOS-style Bottom Tab Navigation (`Deck`, `Vault`, `Hub`, `Network`, `System`).
*   Dedicated screens built for all 5 core AI modules.
*   New feature screens built: `WatchlistScreen` (CRUD operations for prospective stocks), `NewsScreen` (Market Pulse with category filtering), and `PortfolioAlertsScreen` (Custom drawdown/gain triggers).
*   API Client (`src/api/index.ts`) completely wired to FastAPI endpoints handling async requests seamlessly.

✅ **External Integrations**
*   **Google Gemini API:** Fully connected to `scout.py` and `brain.py` to process dynamic user queries and generate JSON-formatted fundamental analysis.
*   **Upstox Brokerage API:** OAuth login endpoints built in the backend. Infrastructure laid out to handle access tokens and execute trades on the Indian stock market.

✅ **DevOps, Security, & Version Control**
*   **Version Control:** Git repository initialized and pushed to GitHub. `.gitignore` set up to exclude sensitive data.
*   **Secrets Management:** Environment variables strictly segregated using `.env` (excluded from git) and `.env.example` templates.
*   **Dockerization:** `Dockerfile` built to containerize FastAPI. `docker-compose.yml` set up to run the service autonomously.
*   **CI/CD:** GitHub Actions workflow (`.github/workflows/ci.yml`) built to test dependency resolution and build cache on every push to the `main` branch.

---

## 5. Pending & Up Next (What Has To Be Done)

⏳ **1. End-to-End System Testing ("Live Fire")**
*   Spin up the local backend (`uvicorn`) and local mobile app (Expo) simultaneously.
*   Test real-world API requests between the phone and the computer via local IP binding.

⏳ **2. Upstox API Trading Verification**
*   Ensure the Upstox OAuth redirect URL correctly issues an active auth token.
*   Execute a "test trade" via the backend to verify the app can actually buy/sell securities for the user.

⏳ **3. Market Data Connection**
*   Wire real-time market data (LTP - Last Traded Price) to the app. Currently, mock values are used in `HomeScreen.tsx` (e.g., Nifty 50 at 25,807). This needs to be replaced with Upstox or Yahoo Finance Live quotes API.

⏳ **4. Production Deployment**
*   Deploy the customized Docker image to a cloud VPS (e.g., AWS EC2, DigitalOcean, or Render).
*   Set up Nginx as a reverse proxy with SSL (HTTPS) to ensure API communication from the mobile phone to the server is fully encrypted.
*   Transition Convex database from the "Development" environment to the "Production" environment.

---

### End of Documentation
*This document serves as the master source of truth. Any AI agent or developer jumping onto this project should review this file before writing code to understand the architecture, completed scope, and existing pipelines.*
