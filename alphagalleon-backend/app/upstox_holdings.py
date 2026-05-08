import os
from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
import httpx
from app.convex_service import ConvexService
from app.auth import decode_token

router = APIRouter()
convex_service = ConvexService()

@router.post("/holdings/sync")
async def sync_upstox_holdings(authorization: Optional[str] = Header(None)):
    """
    Fetch the user's live long term holdings from Upstox.
    Requires AlphaGalleon Bearer auth to identify the user.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
        
    try:
        token = authorization.replace("Bearer ", "")
        token_data = decode_token(token)
        
        if not token_data or not token_data.user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
        user_id = token_data.user_id
        
        # Pull user from Convex to get their Upstox Access Token
        user_record = convex_service.get_user_by_id(user_id)
        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")
            
        upstox_token = user_record.get("upstox_access_token")
        if not upstox_token:
            raise HTTPException(status_code=403, detail="Upstox account not linked")
            
        # Hit the Upstox API
        holdings_url = "https://api.upstox.com/v2/portfolio/long-term-holdings"
        headers = {
            "accept": "application/json",
            "Api-Version": "2.0",
            "Authorization": f"Bearer {upstox_token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(holdings_url, headers=headers)
            
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Upstox token expired. Please re-link your broker.")
                
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch holdings: {response.text}")
                
            holdings_data = response.json()
            raw_holdings = holdings_data.get("data", [])
            
            # Sync to Convex immediately
            convex_service.sync_upstox_portfolio(user_id, raw_holdings)
            
            # Log Activity
            convex_service.log_activity(
                action="VAULT_SYNC",
                details="User synced live Upstox holdings",
                user_id=user_id
            )
            
            return holdings_data
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Holdings sync error: {str(e)}")
