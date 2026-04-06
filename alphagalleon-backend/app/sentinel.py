import logging
from app.scout import Scout

logger = logging.getLogger(__name__)

class Sentinel:
    """Sentinel Risk Engine - Monitors market for drawdowns and portfolio risks"""
    
    def __init__(self, scout_engine: Scout):
        self.scout = scout_engine

    def get_alerts(self, user_id: str):
        """
        Scan for active risk alerts.
        In production, this would use real-time streaming and historical data.
        """
        alerts = []
        
        try:
            # 1. Check Global Market Drawdown (Nifty 50)
            nifty = self.scout.get_ltp("NSE_INDEX|Nifty 50")
            if nifty:
                # Assuming yesterday's close was ~26200 for mock calculation
                prev_close = 26200 
                drawdown = ((nifty - prev_close) / prev_close) * 100
                
                if drawdown <= -1.5:
                    alerts.append({
                        "id": "global_drawdown",
                        "type": "CRITICAL",
                        "title": "Global Market Drawdown",
                        "description": f"Nifty 50 has dropped {abs(drawdown):.2f}% in a single session. Consider defensive hedging.",
                        "icon": "ShieldAlert"
                    })
            
            # 2. Portfolio Concentration Alert (Simulated logic)
            # This would normally query Convex for the user's portfolio
            alerts.append({
                "id": "concentration_risk",
                "type": "WARNING",
                "title": "Sector Concentration",
                "description": "Your portfolio is >60% weighted in Tech. Diversification suggested.",
                "icon": "PieChart"
            })
            
            # 3. Sentinel Proactive Insight
            alerts.append({
                "id": "galleon_insight",
                "type": "INFO",
                "title": "Sentinel Watch: Defense",
                "description": "Increased volume detected in Defense stocks (HAL, BEL). Sentiment is Bullish.",
                "icon": "Zap"
            })

        except Exception as e:
            logger.error(f"Sentinel error: {str(e)}")
            
        return alerts
