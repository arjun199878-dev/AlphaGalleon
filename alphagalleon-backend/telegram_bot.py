import os
import sys
import logging
import asyncio
from typing import List, Optional

# --- Add backend modules to path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from app.brain import Brain
from app.doctor import Doctor, PortfolioItem
from app.architect import Architect, UserDNA
from app.scout import Scout
from app.schemas import FundamentalData, Ticker

# --- Config ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Use a separate token if needed, or reuse current bot

if not TELEGRAM_TOKEN:
    # Fallback to hardcoded token from openclaw.json if env is missing
    # But for security, better to rely on env.
    # I'll ask user for token if this fails.
    print("Error: TELEGRAM_BOT_TOKEN not set.")
    sys.exit(1)

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Agent Instances ---
scout = Scout()
brain = Brain()
doctor = Doctor()
architect = Architect()

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚓️ AlphaGalleon War Room Active.\n\n"
        "Commands:\n"
        "/price <ticker> - Live Quote (Scout)\n"
        "/memo <ticker> - Investment Memo (Brain)\n"
        "/portfolio <age> <risk> <capital> - Wealth Plan (Architect)\n"
        "/diagnose <ticker1:alloc, ticker2:alloc...> - Portfolio Check (Doctor)"
    )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price <ticker> (e.g., /price RELIANCE)")
        return
    
    ticker = context.args[0].upper()
    await update.message.reply_text(f"📡 Scout tracking {ticker}...")
    
    try:
        # Heuristic mapping for common tickers if needed
        symbol = ticker
        if "NSE_EQ" not in symbol and "|" not in symbol:
             # Basic mapping attempts or direct try
             if ticker == "RELIANCE": symbol = "NSE_EQ|INE002A01018"
             elif ticker == "TCS": symbol = "NSE_EQ|INE467B01029"
             elif ticker == "INFY": symbol = "NSE_EQ|INE009A01021"
             elif ticker == "HDFCBANK": symbol = "NSE_EQ|INE040A01034"
        
        quote = scout.get_quote(symbol)
        if quote:
            ltp = quote.get('last_price')
            await update.message.reply_text(f"📈 {ticker}: ₹{ltp}")
        else:
            await update.message.reply_text(f"❌ Scout lost track of {ticker}. Check symbol.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Scout Error: {str(e)}")

async def get_memo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /memo <ticker> (e.g., /memo RELIANCE)")
        return

    ticker = context.args[0].upper()
    await update.message.reply_text(f"🧠 Brain analyzing {ticker}...")
    
    try:
        # 1. Get Live Data
        symbol = ticker
        # (Reuse mapping logic - ideally abstract this)
        if ticker == "RELIANCE": symbol = "NSE_EQ|INE002A01018"
        elif ticker == "TCS": symbol = "NSE_EQ|INE467B01029"
        
        quote = scout.get_quote(symbol)
        price = quote.get('last_price', 0.0) if quote else 0.0
        
        # 2. Mock Fundamentals (until we have Screener API)
        # We use a placeholder for now to test the pipeline
        fund_data = FundamentalData(
            ticker=Ticker(symbol=ticker, name=ticker, sector="Unknown", current_price=price, market_cap=0.0, pe_ratio=25.0),
            revenue_growth_3y=12.0, profit_growth_3y=15.0, debt_to_equity=0.5, roe=18.0, promoter_holding=50.0,
            recent_news_summary="Stable outlook."
        )
        
        # 3. Generate Memo
        memo = brain.generate_memo(fund_data)
        
        response = (
            f"📄 *MEMO: {memo.ticker_symbol}*\n"
            f"Verdict: *{memo.recommendation.upper()}* (Conf: {memo.confidence_score}%)\n"
            f"Valuation: {memo.valuation_verdict}\n\n"
            f"🐂 *Bull Case:*\n" + "\n".join([f"- {p}" for p in memo.bull_case]) + "\n\n"
            f"🐻 *Bear Case:*\n" + "\n".join([f"- {p}" for p in memo.bear_case])
        )
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Brain Freeze: {str(e)}")

async def get_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /portfolio 28 aggressive 500000
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /portfolio <age> <risk> <capital>")
        return
        
    try:
        age = int(context.args[0])
        risk = context.args[1]
        capital = float(context.args[2])
        
        await update.message.reply_text(f"🏗️ Architect building plan for {age}y {risk} investor...")
        
        user = UserDNA(
            age=age, risk_appetite=risk, capital_amount=capital, 
            investment_horizon="10 years", goals="Wealth Creation"
        )
        
        plan = architect.construct_portfolio(user)
        
        response = (
            f"🏗️ *PLAN: {plan.strategy_name}*\n"
            f"CAGR: {plan.expected_cagr} | Drawdown: {plan.max_drawdown}\n\n"
        )
        for alloc in plan.allocations:
            response += f"*{alloc.asset_class} ({alloc.percentage}%)*: {', '.join(alloc.suggested_instruments)}\n"
            
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Architect Error: {str(e)}")

# --- Main ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('price', get_price))
    application.add_handler(CommandHandler('memo', get_memo))
    application.add_handler(CommandHandler('portfolio', get_portfolio))
    
    print("🤖 AlphaGalleon Telegram Interface Running...")
    application.run_polling()
