from app.celery_app import celery_app
from app.brain import Brain
from app.architect import Architect
from app.schemas import FundamentalData
from app.architect_schema import UserDNA
import asyncio
import nest_asyncio

# Required to run asyncio event loops inside Celery synchronous workers
nest_asyncio.apply()

# Initialize AI Engines
brain_engine = Brain()
architect_engine = Architect()

@celery_app.task(bind=True, name="generate_memo_task")
def generate_memo_task(self, fundamental_data_dict: dict):
    """
    Background task to generate an investment memo.
    """
    try:
        data = FundamentalData(**fundamental_data_dict)
        result = brain_engine.generate_memo(data)

        # Store in Convex so it is persisted
        from app.main import convex_service
        convex_service.store_memo({
            "symbol": result.ticker_symbol,
            "verdict": result.recommendation.upper(),
            "confidence": result.confidence_score,
            "summary": result.thesis_summary,
            "reasoning": f"BULLS: {', '.join(result.bull_case)}\nBEARS: {', '.join(result.bear_case)}\nVALUATION: {result.valuation_verdict}",
            "priceAtGeneration": data.ticker.current_price if getattr(data, "ticker", None) else 0.0
        })

        return result.dict()
    except Exception as e:
        self.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
        raise e

@celery_app.task(bind=True, name="construct_portfolio_task")
def construct_portfolio_task(self, user_dna_dict: dict):
    """
    Background task to construct a model portfolio.
    """
    try:
        dna = UserDNA(**user_dna_dict)
        result = architect_engine.construct_portfolio(dna)

        from app.main import convex_service
        convex_service.log_activity(
            action="CONSTRUCT_PORTFOLIO",
            details=f"Constructed portfolio for {dna.risk_appetite} profile with capital {dna.capital_amount}"
        )

        return result.dict()
    except Exception as e:
        self.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
        raise e
