from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseBroker(ABC):
    """
    Abstract base class defining the contract for all broker integrations (Upstox, Zerodha, etc).
    """

    @property
    @abstractmethod
    def broker_id(self) -> str:
        """Return the unique identifier for the broker (e.g., 'upstox', 'zerodha')."""
        pass

    @abstractmethod
    async def get_holdings(self, user_id: str, access_token: str) -> List[Dict[str, Any]]:
        """
        Fetch current portfolio holdings from the broker.
        Should return a standard list of dictionaries containing symbol, quantity, average_price, etc.
        """
        pass

    @abstractmethod
    async def execute_basket(self, user_id: str, access_token: str, basket: List[Dict[str, Any]], sandbox: bool = False) -> Dict[str, Any]:
        """
        Execute a basket of limit orders.
        'basket' format: [{"symbol": "RELIANCE", "quantity": 10, "price": 2500.0, "transaction_type": "BUY"}]
        Returns a dictionary with execution status and details.
        """
        pass
