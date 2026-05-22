import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the main FastAPI app
from app.main import app
from app.auth import hash_password

client = TestClient(app)

@patch("app.main.convex_service")
def test_login_success(mock_convex):
    """Verify that a user with correct credentials gets a JWT token."""
    mock_convex.get_user_by_email.return_value = {
        "_id": "test_user_123",
        "name": "Test User",
        "email": "test@example.com",
        "password_hash": hash_password("password123")
    }

    payload = {
        "email": "test@example.com",
        "password": "password123"
    }

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["user"]["email"] == "test@example.com"

@patch("app.main.convex_service")
def test_signup_success(mock_convex):
    """Verify that a user with new credentials gets a JWT token."""
    mock_convex.get_user_by_email.return_value = None
    mock_convex.create_user.return_value = {
        "_id": "test_user_123",
        "name": "New User",
        "email": "new@example.com",
        "password_hash": hash_password("password123"),
        "riskProfile": "aggressive"
    }

    payload = {
        "name": "New User",
        "email": "new@example.com",
        "password": "password123",
        "riskProfile": "aggressive"
    }

    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["user"]["email"] == "new@example.com"
