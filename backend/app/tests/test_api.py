"""Integration tests for API endpoints."""

from fastapi import status
from fastapi.testclient import TestClient


def test_trends_endpoint(client: TestClient):
    """Test trends list endpoint."""
    response = client.get("/api/v1/trends")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_trend_sources_endpoint(client: TestClient):
    """Test trend sources endpoint."""
    response = client.get("/api/v1/trends/sources")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_billing_plans_endpoint(client: TestClient):
    """Test billing plans endpoint."""
    response = client.get("/api/v1/billing/plans")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_video_creation_requires_auth(client: TestClient):
    """Test video creation requires authentication."""
    response = client.post("/api/v1/videos", json={
        "channel_id": 1,
        "script_id": 1,
        "title": "Test Video",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_workflow_list(client: TestClient):
    """Test workflow listing."""
    response = client.get("/api/v1/workflows")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data


def test_notifications_endpoint(client: TestClient):
    """Test notifications require auth."""
    response = client.get("/api/v1/notifications")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_admin_stats_requires_admin(client: TestClient):
    """Test admin stats require admin role."""
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

