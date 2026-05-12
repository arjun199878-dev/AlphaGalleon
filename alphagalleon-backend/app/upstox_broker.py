import uuid
import httpx
from typing import List, Dict, Any
from app.broker_base import BaseBroker

class UpstoxBroker(BaseBroker):
    """
    Upstox implementation of the Broker API abstraction.
    """

    @property
    def broker_id(self) -> str:
        return "upstox"

    async def get_holdings(self, user_id: str, access_token: str) -> List[Dict[str, Any]]:
        holdings_url = "https://api.upstox.com/v2/portfolio/long-term-holdings"
        headers = {
            "accept": "application/json",
            "Api-Version": "2.0",
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(holdings_url, headers=headers)

            if response.status_code == 401:
                raise Exception("Token Expired")

            if response.status_code != 200:
                raise Exception(f"Failed to fetch holdings: {response.text}")

            holdings_data = response.json()
            return holdings_data.get("data", [])

    async def execute_basket(self, user_id: str, access_token: str, basket: List[Dict[str, Any]], sandbox: bool = False) -> Dict[str, Any]:
        results = []
        has_errors = False

        if sandbox:
            for item in basket:
                results.append({
                    "symbol": item["symbol"],
                    "status": "success",
                    "order_id": f"PAPER-{str(uuid.uuid4())[:8].upper()}",
                    "message": "Paper trade executed successfully"
                })
            return {
                "execution_status": "success",
                "details": results,
                "sandbox_mode": True
            }

        order_url = "https://api.upstox.com/v2/order/place"
        headers = {
            "accept": "application/json",
            "Api-Version": "2.0",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            for item in basket:
                payload = {
                    "quantity": item["quantity"],
                    "product": "D", # Delivery
                    "validity": "DAY",
                    "price": item["price"],
                    "tag": "alphagalleon_architect",
                    "instrument_token": item["symbol"], # Needs to be 'NSE_EQ|INE123...'
                    "order_type": "LIMIT",
                    "transaction_type": item["transaction_type"].upper(),
                    "disclosed_quantity": 0,
                    "trigger_price": 0,
                    "is_amo": False
                }

                response = await client.post(order_url, json=payload, headers=headers)

                if response.status_code == 200:
                    order_data = response.json()
                    results.append({
                        "symbol": item["symbol"],
                        "status": "success",
                        "order_id": order_data.get("data", {}).get("order_id")
                    })
                else:
                    has_errors = True
                    results.append({
                        "symbol": item["symbol"],
                        "status": "error",
                        "error_message": response.text
                    })

        return {
            "execution_status": "completed_with_errors" if has_errors else "success",
            "details": results
        }
