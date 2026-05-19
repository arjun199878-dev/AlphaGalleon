import os
import sys
from convex import ConvexClient
from dotenv import load_dotenv

# Add parent dir to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class ConvexService:
    def __init__(self):
        self.url = os.getenv("CONVEX_URL")
        if not self.url:
            # Fallback to a demo URL for testing (will fail if not set properly)
            self.url = "https://vibrant-spoonbill-564.eu-west-1.convex.cloud"
        
        try:
            self.client = ConvexClient(self.url)
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Convex client: {e}")
            self.client = None

    def store_memo(self, memo_data):
        """
        Stores an investment memo in Convex.
        memo_data is a dict matching the 'memos:create' mutation args.
        """
        if not self.client:
            print("❌ Convex client not available. Memo not stored.")
            return None
            
        try:
            memo_id = self.client.mutation("memos:create", memo_data)
            print(f"✅ Memo stored in Convex: {memo_id}")
            return memo_id
        except Exception as e:
            print(f"❌ Error storing memo in Convex: {e}")
            return None

    def log_activity(self, action, details=None, user_id=None):
        """
        Logs activity to Convex activityLog.
        """
        if not self.client:
            print("❌ Convex client not available. Activity not logged.")
            return
            
        try:
            self.client.mutation("activity:log", {
                "action": action,
                "details": details,
                "userId": user_id
            })
        except Exception as e:
            print(f"❌ Error logging activity to Convex: {e}")

    def list_memos(self, limit=50):
        """
        List recent investment memos.
        """
        if not self.client:
            return []
            
        try:
            return self.client.query("memos:list", {"limit": limit})
        except Exception as e:
            print(f"❌ Error listing memos: {e}")
            return []

    def get_memo_by_symbol(self, symbol):
        """
        Get memos for a specific symbol.
        """
        if not self.client:
            return []
            
        try:
            return self.client.query("memos:getBySymbol", {"symbol": symbol})
        except Exception as e:
            print(f"❌ Error fetching memo for {symbol}: {e}")
            return []

    def list_users(self):
        """
        List all registered users.
        """
        if not self.client:
            return []
            
        try:
            return self.client.query("users:list", {})
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []

    def get_user_by_email(self, email):
        """
        Get user by email.
        """
        if not self.client:
            return None
            
        try:
            return self.client.query("users:getByEmail", {"email": email})
        except Exception as e:
            print(f"❌ Error fetching user: {e}")
            return None

    def get_user_by_id(self, user_id):
        """
        Get user by Convex ID.
        """
        if not self.client:
            return None
            
        try:
            return self.client.query("users:get", {"id": user_id})
        except Exception as e:
            print(f"❌ Error fetching user by ID: {e}")
            return None

    def create_user(self, name, email, password_hash=None, riskProfile=None):
        """
        Create a new user with optional password hashing for auth.
        Returns the full user document (not just ID).
        """
        if not self.client:
            return None
            
        try:
            user_data = {
                "name": name,
                "email": email,
                "riskProfile": riskProfile or "moderate"
            }
            if password_hash:
                user_data["password_hash"] = password_hash
            
            # Create user (returns ID)
            user_id = self.client.mutation("users:create", user_data)
            print(f"✅ User created with ID: {user_id}")
            
            # Fetch and return full user document
            user = self.client.query("users:getByEmail", {"email": email})
            print(f"✅ User document retrieved: {user}")
            return user
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None

    def get_activity_log(self, limit=100, user_id=None):
        """
        Get activity log (optionally filtered by user).
        """
        if not self.client:
            return []
            
        try:
            if user_id:
                return self.client.query("activity:listByUser", {"userId": user_id})
            else:
                # For global activity, we'd need a convex query defined
                return self.client.query("activity:listRecent", {"limit": limit})
        except Exception as e:
            print(f"❌ Error fetching activity: {e}")
            return []

    def update_broker_token(self, user_id: str, broker_id: str, token: str):
        """
        Update a generic broker access token for a user.
        """
        if not self.client:
            return False
            
        try:
            self.client.mutation("users:updateBrokerToken", {
                "id": user_id,
                "broker_id": broker_id,
                "access_token": token
            })
            print(f"✅ {broker_id.capitalize()} token updated for user: {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating {broker_id.capitalize()} token: {e}")
            return False


    def update_preferred_broker(self, user_id: str, broker_id: str):
        """
        Update a user's preferred broker.
        """
        if not self.client:
            return False

        try:
            self.client.mutation("users:updatePreferredBroker", {
                "id": user_id,
                "broker_id": broker_id
            })
            print(f"✅ Preferred broker updated to {broker_id} for user: {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating preferred broker: {e}")
            return False

    # ─── Portfolio / Holdings Operations ────────────────────────────

    def sync_portfolio(self, user_id: str, holdings_data: list):
        """Sync live Upstox holdings to a dedicated Convex portfolio."""
        if not self.client:
            return None
        try:
            formatted_holdings = []
            for h in holdings_data:
                # Upstox V2 returns 'trading_symbol', 'quantity', 'average_price'
                formatted_holdings.append({
                    "symbol": h.get("trading_symbol", "UNKNOWN"),
                    "quantity": int(h.get("quantity", 0)),
                    "avgBuyPrice": float(h.get("average_price", 0.0))
                })
            
            portfolio_id = self.client.mutation("holdings:sync", {
                "userId": user_id,
                "holdings": formatted_holdings
            })
            print(f"✅ Upstox portfolio synced for user {user_id}")
            return portfolio_id
        except Exception as e:
            print(f"❌ Error syncing Upstox portfolio: {e}")
            return None

    def get_holdings(self, user_id: str):
        """Get user's portfolio holdings."""
        if not self.client:
            return []
        try:
            return self.client.query("holdings:listByUser", {"userId": user_id})
        except Exception as e:
            print(f"❌ Error fetching holdings: {e}")
            return []

    # ─── Watchlist Operations ──────────────────────────────

    def get_watchlist(self, user_id: str):
        """Get user's watchlist items."""
        if not self.client:
            return []
        try:
            return self.client.query("watchlist:listByUser", {"userId": user_id})
        except Exception as e:
            print(f"❌ Error fetching watchlist: {e}")
            return []

    def add_to_watchlist(self, user_id: str, symbol: str, notes: str = None, target_price: float = None):
        """Add a stock to user's watchlist."""
        if not self.client:
            return None
        try:
            data = {"userId": user_id, "symbol": symbol}
            if notes:
                data["notes"] = notes
            if target_price:
                data["targetPrice"] = target_price
            return self.client.mutation("watchlist:add", data)
        except Exception as e:
            print(f"❌ Error adding to watchlist: {e}")
            return None

    def remove_from_watchlist(self, item_id: str):
        """Remove a stock from watchlist."""
        if not self.client:
            return False
        try:
            self.client.mutation("watchlist:remove", {"id": item_id})
            return True
        except Exception as e:
            print(f"❌ Error removing from watchlist: {e}")
            return False

# If run directly, test the connection
if __name__ == "__main__":
    service = ConvexService()
    print(f"Connected to Convex at: {service.url}")
    
    # Test basic operations
    print("\n--- Testing Convex Operations ---")
    
    # List users
    users = service.list_users()
    print(f"Users: {len(users)} found")
    
    # List recent memos
    memos = service.list_memos(limit=5)
    print(f"Recent memos: {len(memos)} found")
    
    # Test creating a user
    user_id = service.create_user("Test User", "test@example.com", "moderate")
    print(f"Created user: {user_id}")
