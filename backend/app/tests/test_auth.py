"""Authentication endpoint tests."""

from fastapi import status
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    """Test successful user registration."""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


def test_register_duplicate_email(client: TestClient):
    """Test registration with existing email returns 409."""
    client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "username": "user1",
        "password": "TestPass123!",
    })
    response = client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "username": "user2",
        "password": "TestPass123!",
    })
    assert response.status_code == status.HTTP_409_CONFLICT


def test_login_success(client: TestClient):
    """Test successful login."""
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "TestPass123!",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "TestPass123!",
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data["tokens"]


def test_login_invalid_credentials(client: TestClient):
    """Test login with wrong password returns 401."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "WrongPass123!",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

