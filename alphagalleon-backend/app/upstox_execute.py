import os
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import httpx
from app.convex_service import ConvexService
from app.auth import decode_token

router = APIRouter()
convex_service = ConvexService()

class BasketItem(BaseModel):
    symbol: str
    quantity: int
    price: float  # Limit price
    transaction_type: str = "BUY"  # BUY or SELL

class ExecuteBasketRequest(BaseModel):
    basket: List[BasketItem]

@router.post("/execute-basket")
async def execute_basket(request: ExecuteBasketRequest, authorization: Optional[str] = Header(None)):
    """
    Given a basket of stocks, loops through and places limit orders
    on the user's linked Upstox account.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
        
    try:
        # Validate User Auth
        token = authorization.replace("Bearer ", "")
        token_data = decode_token(token)
        
        if not token_data or not token_data.user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
        user_id = token_data.user_id
        
        # Pull user from Convex to get Upstox Access Token
        user_record = convex_service.get_user_by_id(user_id)
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")
            
        upstox_token = user_record.get("upstox_access_token")
        if not upstox_token:
            raise HTTPException(status_code=403, detail="Upstox account not linked")

        order_url = "https://api.upstox.com/v2/order/place"
        headers = {
            "accept": "application/json",
            "Api-Version": "2.0",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {upstox_token}"
        }
        
        results = []
        has_errors = False
        
        async with httpx.AsyncClient() as client:
            for item in request.basket:
                # Upstox Order Payload
                payload = {
                    "quantity": item.quantity,
                    "product": "D", # Delivery
                    "validity": "DAY",
                    "price": item.price,
                    "tag": "alphagalleon_architect",
                    "instrument_token": item.symbol, # Needs to be 'NSE_EQ|INE123...'
                    "order_type": "LIMIT",
                    "transaction_type": item.transaction_type.upper(),
                    "disclosed_quantity": 0,
                    "trigger_price": 0,
                    "is_amo": False
                }
                
                response = await client.post(order_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    order_data = response.json()
                    results.append({
                        "symbol": item.symbol,
                        "status": "success",
                        "order_id": order_data.get("data", {}).get("order_id")
                    })
                else:
                    has_errors = True
                    results.append({
                        "symbol": item.symbol,
                        "status": "error",
                        "error_message": response.text
                    })
        
        # Log Activity
        log_detail = f"Executed basket with {len(request.basket)} orders. Errors: {has_errors}"
        convex_service.log_activity(
            action="BASKET_EXECUTION",
            details=log_detail,
            user_id=user_id
        )
        
        return {
            "execution_status": "completed_with_errors" if has_errors else "success",
            "details": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Basket execution failed: {str(e)}")
