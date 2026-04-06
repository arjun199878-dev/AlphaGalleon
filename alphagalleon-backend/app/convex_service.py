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
        memo_data is a dict matching the 'memos:store' mutation args.
        """
        if not self.client:
            print("❌ Convex client not available. Memo not stored.")
            return None
            
        try:
            memo_id = self.client.mutation("memos:store", memo_data)
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
            return self.client.query("memos:listRecent", {"limit": limit})
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
            return self.client.query("memos:listBySymbol", {"symbol": symbol})
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
            
            user_result = self.client.mutation("users:create", user_data)
            print(f"✅ User created: {user_result}")
            return user_result
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

    def update_upstox_token(self, user_id: str, token: str):
        """
        Update Upstox access token for a user.
        """
        if not self.client:
            return False
            
        try:
            self.client.mutation("users:updateUpstoxToken", {
                "id": user_id,
                "upstox_access_token": token
            })
            print(f"✅ Upstox token updated for user: {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating Upstox token: {e}")
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
