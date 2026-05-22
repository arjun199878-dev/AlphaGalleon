from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.convex_service import ConvexService
from app.auth import decode_token
from app.upstox_broker import UpstoxBroker
from app.zerodha_broker import ZerodhaBroker

router = APIRouter()
convex_service = ConvexService()

# In a real app we'd load these dynamically based on user config.
# For now, default to Upstox unless otherwise specified.
brokers = {
    "upstox": UpstoxBroker(),
    "zerodha": ZerodhaBroker(),
}

class BasketItem(BaseModel):
    symbol: str
    quantity: int
    price: float
    transaction_type: str = "BUY"

class ExecuteBasketRequest(BaseModel):
    basket: List[BasketItem]
    sandbox: bool = False
    broker_id: str = "upstox"

@router.post("/execute-basket")
async def execute_basket(request: ExecuteBasketRequest, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        token = authorization.replace("Bearer ", "")
        token_data = decode_token(token)

        if not token_data or not token_data.user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user_id = token_data.user_id

        # Pull user from Convex
        user_record = convex_service.get_user_by_id(user_id)
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")

        # Determine which broker to use
        broker_id = request.broker_id
        if broker_id not in brokers:
            raise HTTPException(status_code=400, detail=f"Unsupported broker: {broker_id}")

        broker = brokers[broker_id]

        # Get appropriate token from user record
        broker_token = user_record.get(f"{broker_id}_access_token")
        if not broker_token:
            raise HTTPException(status_code=403, detail=f"{broker_id.capitalize()} account not linked")

        # Convert Pydantic models to dicts for the broker abstraction
        basket_dicts = [item.dict() for item in request.basket]

        result = await broker.execute_basket(user_id, broker_token, basket_dicts, request.sandbox)

        # Log Activity
        log_detail = f"Executed basket on {broker_id} with {len(request.basket)} orders. Status: {result['execution_status']}"
        convex_service.log_activity(
            action=f"BASKET_EXECUTION_{broker_id.upper()}",
            details=log_detail,
            user_id=user_id
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Basket execution failed: {str(e)}")

@router.post("/holdings/sync")
async def sync_holdings(broker_id: str = "upstox", authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        token = authorization.replace("Bearer ", "")
        token_data = decode_token(token)

        if not token_data or not token_data.user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user_id = token_data.user_id

        user_record = convex_service.get_user_by_id(user_id)
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")

        if broker_id not in brokers:
            raise HTTPException(status_code=400, detail=f"Unsupported broker: {broker_id}")

        broker = brokers[broker_id]
        broker_token = user_record.get(f"{broker_id}_access_token")

        if not broker_token:
            raise HTTPException(status_code=403, detail=f"{broker_id.capitalize()} account not linked")

        try:
            raw_holdings = await broker.get_holdings(user_id, broker_token)
        except Exception as e:
            if "Token Expired" in str(e):
                raise HTTPException(status_code=401, detail=f"{broker_id.capitalize()} token expired. Please re-link your broker.")
            raise HTTPException(status_code=400, detail=f"Failed to fetch holdings: {str(e)}")

        # Sync to Convex immediately (Assume Convex service handles formatting)
        convex_service.sync_portfolio(user_id, raw_holdings) # TODO: rename sync_upstox_portfolio to generic sync_portfolio

        convex_service.log_activity(
            action=f"VAULT_SYNC_{broker_id.upper()}",
            details=f"User synced live {broker_id.capitalize()} holdings",
            user_id=user_id
        )

        return {"status": "success", "data": raw_holdings}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Holdings sync error: {str(e)}")
