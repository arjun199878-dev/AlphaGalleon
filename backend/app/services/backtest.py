from typing import List, Dict, Any
from app.services.market_data import market_data_service
from app.services.gemini import gemini_service
import json
import asyncio
import datetime
import pandas as pd
import numpy as np
import yfinance as yf

class BacktestService:
    """
    The Time Machine.
    Simulates portfolio performance against historical market data.
    """

    async def run_backtest(self, holdings: List[Dict[str, Any]], duration_years: int = 1) -> Dict[str, Any]:
        """
        Runs a buy-and-hold backtest.
        holdings: [{"symbol": "RELIANCE", "allocation": 0.5}, {"symbol": "INFY", "allocation": 0.5}]
        """
        print(f"Initiating Time Travel sequence for {duration_years} years...")
        
        end_date = datetime.date.today()
        # Add buffer for weekends/holidays
        start_date = end_date - datetime.timedelta(days=int(duration_years * 365.25) + 30)
        
        # Prepare tickers (append .NS for NSE)
        tickers = [h['symbol'] + ".NS" for h in holdings]
        # Normalize allocations to sum to 1.0
        total_alloc = sum(h.get('allocation', 0) for h in holdings)
        if total_alloc == 0:
            # Equal weight fallback
            weights = np.ones(len(tickers)) / len(tickers)
        else:
            weights = np.array([h.get('allocation', 0) / total_alloc for h in holdings])
        
        try:
            # Fetch Data with auto_adjust=True (Splits/Dividends)
            # progress=False hides the progress bar
            df = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
            
            if df.empty:
                return {"error": "No historical data found. Symbols might be incorrect."}

            # Handle Single vs Multi Ticker response structure
            if len(tickers) == 1:
                # yfinance returns Series if single ticker, or DataFrame with OHLCV columns
                if isinstance(df, pd.DataFrame):
                    if 'Close' in df.columns:
                        adj_close = df['Close']
                    else:
                        adj_close = df.iloc[:, 0] # Assume first col is close-like if not named
                else:
                    adj_close = df
            else:
                # Multi-ticker: DataFrame with MultiIndex or Columns
                # Usually Level 0 is 'Close', Level 1 is Ticker
                try:
                    adj_close = df['Close']
                except KeyError:
                    # Fallback if structure is flat (older yfinance versions sometimes)
                    adj_close = df

            # Ensure data is numeric and handle missing values
            adj_close = adj_close.ffill().dropna()

            # Calculate Daily Returns
            daily_returns = adj_close.pct_change().dropna()

            # Calculate Portfolio Daily Returns
            if len(tickers) == 1:
                portfolio_daily_ret = daily_returns
            else:
                # Dot product of Daily Returns Matrix * Weights Vector
                # Align columns with weights
                portfolio_daily_ret = daily_returns.dot(weights)

            # Calculate Equity Curve (Cumulative Return)
            # Start at 100,000 (Initial Capital Base)
            initial_capital = 100000
            cumulative_ret = (1 + portfolio_daily_ret).cumprod()
            
            # Create Equity Curve Series
            equity_curve = initial_capital * cumulative_ret
            
            # Prepend start point (Day 0)
            start_val = pd.Series([initial_capital], index=[daily_returns.index[0] - datetime.timedelta(days=1)])
            equity_curve = pd.concat([start_val, equity_curve])

            # Metrics Calculation
            final_value = equity_curve.iloc[-1]
            total_return_pct = ((final_value - initial_capital) / initial_capital) * 100
            
            # CAGR
            total_days = (equity_curve.index[-1] - equity_curve.index[0]).days
            years = total_days / 365.25
            if years > 0 and final_value > 0:
                cagr = ((final_value / initial_capital) ** (1 / years)) - 1
            else:
                cagr = 0
            
            # Max Drawdown
            rolling_max = equity_curve.cummax()
            drawdown = (equity_curve - rolling_max) / rolling_max
            max_drawdown = drawdown.min()

            # Chart Data (Downsample for UI Performance)
            # Aim for ~20-30 points
            if len(equity_curve) > 30:
                step = len(equity_curve) // 30
                chart_points = equity_curve.iloc[::step]
                # Ensure last point is included
                if chart_points.index[-1] != equity_curve.index[-1]:
                    chart_points = pd.concat([chart_points, equity_curve.iloc[[-1]]])
            else:
                chart_points = equity_curve

            # Format Dates for Chart Labels (e.g., "Jan 23")
            labels = [d.strftime('%b %y') for d in chart_points.index]
            data_points = [round(x, 0) for x in chart_points.values.tolist()]

            return {
                "metrics": {
                    "initial_investment": initial_capital,
                    "final_value": round(float(final_value), 2),
                    "total_return_pct": round(float(total_return_pct), 2),
                    "cagr_pct": round(float(cagr * 100), 2),
                    "max_drawdown_pct": round(float(max_drawdown * 100), 2),
                    "duration_days": total_days
                },
                "chart": {
                    "labels": labels,
                    "data": data_points
                }
            }

        except Exception as e:
            print(f"Backtest failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

backtest_service = BacktestService()
