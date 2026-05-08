import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import urllib.parse
from app.convex_service import ConvexService
from app.auth import decode_token

router = APIRouter()
convex_service = ConvexService()

UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
# The redirect URL MUST match the one registered in Upstox Developer Console
UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/api/v1/upstox/callback")

@router.get("/login")
async def upstox_login(request: Request, user_id: str):
    """
    Redirects the user to the Upstox OAuth login page.
    Pass user_id in query params so it can be passed via 'state'
    """
    if not UPSTOX_API_KEY or not UPSTOX_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Upstox OAuth credentials not configured")
        
    auth_url = "https://api.upstox.com/v2/login/authorization/dialog"
    params = {
        "response_type": "code",
        "client_id": UPSTOX_API_KEY,
        "redirect_uri": UPSTOX_REDIRECT_URI,
        "state": user_id
    }
    redirect_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=redirect_url)


@router.get("/callback")
async def upstox_callback(code: str, state: str):
    """
    Callback endpoint where Upstox sends the authorization code.
    'state' contains the original user_id from the login request.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    if not state:
        raise HTTPException(status_code=400, detail="State missing (user_id required)")

    user_id = state
    
    # Swap code for access token
    token_url = "https://api.upstox.com/v2/login/authorization/token"
    data = {
        "code": code,
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "redirect_uri": UPSTOX_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {
        "accept": "application/json",
        "Api-Version": "2.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to fetch token: {response.text}")
            
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token missing in response")
            
        # Store in Convex
        success = convex_service.update_upstox_token(user_id, access_token)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save token to DB")
            
        # Log Activity
        convex_service.log_activity(
            action="UPSTOX_LINKED",
            details="User successfully linked Upstox account",
            user_id=user_id
        )
            
        # Return success redirect (deep link to mobile app)
        # Ideally this redirects to galleon://upstox/success or similar
        return {"status": "success", "message": "Upstox account linked successfully. You may close this window."}
