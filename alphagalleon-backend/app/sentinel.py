import logging
from app.scout import Scout

logger = logging.getLogger(__name__)

class Sentinel:
    """Sentinel Risk Engine - Monitors market for drawdowns and portfolio risks"""
    
    def __init__(self, scout_engine: Scout, convex_service=None):
        self.scout = scout_engine
        self.convex_service = convex_service

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
            
            # 2. Portfolio Concentration Alert
            if self.convex_service:
                holdings = self.convex_service.get_holdings(user_id)
                if holdings:
                    # simplistic check for high concentration in single stock
                    total_value = sum((h.get('quantity', 0) * h.get('avgBuyPrice', 0)) for h in holdings)
                    if total_value > 0:
                        for h in holdings:
                            val = h.get('quantity', 0) * h.get('avgBuyPrice', 0)
                            if (val / total_value) > 0.4:
                                alerts.append({
                                    "id": f"concentration_{h.get('symbol')}",
                                    "type": "WARNING",
                                    "title": "Concentration Risk",
                                    "description": f"Your portfolio is heavily weighted (>40%) in {h.get('symbol')}. Diversification suggested.",
                                    "icon": "PieChart"
                                })
            else:
                alerts.append({
                    "id": "concentration_risk",
                    "type": "WARNING",
                    "title": "Portfolio Concentration",
                    "description": "Ensure your portfolio is well diversified. Connect Convex to analyze.",
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
