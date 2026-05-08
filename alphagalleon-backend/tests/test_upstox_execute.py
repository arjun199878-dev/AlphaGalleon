import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the main FastAPI app
from app.main import app

client = TestClient(app)

def test_missing_auth_header():
    """Verify that omitting the authorization header throws a 401."""
    payload = {
        "basket": [{"symbol": "RELIANCE", "quantity": 10, "price": 2500.0, "transaction_type": "BUY"}],
        "sandbox": True
    }
    
    response = client.post("/api/v1/upstox/execute-basket", json=payload)
    assert response.status_code == 401
    assert "Missing authorization header" in response.json()["detail"]


@patch("app.upstox_execute.decode_token")
@patch("app.upstox_execute.convex_service")
def test_user_not_linked_to_broker(mock_convex, mock_decode):
    """Verify that a valid user without an Upstox access token gets a 403 Forbidden."""
    
    # Mock Auth
    mock_token_data = MagicMock()
    mock_token_data.user_id = "test_user_123"
    mock_decode.return_value = mock_token_data
    
    # Mock Convex to return a user WITHOUT 'upstox_access_token'
    mock_convex.get_user_by_id.return_value = {"_id": "test_user_123", "name": "Test User"}
    
    payload = {
        "basket": [{"symbol": "RELIANCE", "quantity": 10, "price": 2500.0}],
        "sandbox": True
    }
    
    response = client.post(
        "/api/v1/upstox/execute-basket", 
        json=payload, 
        headers={"Authorization": "Bearer VALID_MOCK_TOKEN"}
    )
    
    assert response.status_code == 403
    assert "Upstox account not linked" in response.json()["detail"]


@patch("app.upstox_execute.decode_token")
@patch("app.upstox_execute.convex_service")
def test_sandbox_execution(mock_convex, mock_decode):
    """Verify that a valid user with a linked broker receives PAPER-UUIDs completely bypassing httpx."""
    
    # Mock Auth
    mock_token_data = MagicMock()
    mock_token_data.user_id = "test_user_123"
    mock_decode.return_value = mock_token_data
    
    # Mock Convex to return a user WITH 'upstox_access_token'
    mock_convex.get_user_by_id.return_value = {
        "_id": "test_user_123", 
        "name": "Test User",
        "upstox_access_token": "live_upstox_token_xx_yy"
    }
    
    payload = {
        "basket": [{"symbol": "NSE_EQ|INE123", "quantity": 2, "price": 100.0}],
        "sandbox": True
    }
    
    response = client.post(
        "/api/v1/upstox/execute-basket", 
        json=payload, 
        headers={"Authorization": "Bearer VALID_MOCK_TOKEN"}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["execution_status"] == "success"
    assert data["sandbox_mode"] is True
    
    # Verify the UUID was mocked correctly
    assert len(data["details"]) == 1
    assert data["details"][0]["order_id"].startswith("PAPER-")
    
    # Verify telemetry was logged
    mock_convex.log_activity.assert_called_once()
