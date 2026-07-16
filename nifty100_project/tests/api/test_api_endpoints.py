import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    """Validates the health check endpoint (Gate AC-11)."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_sectors_endpoint():
    """Validates the sectors list slice."""
    response = client.get("/api/v1/sectors")
    assert response.status_code == 200
    assert "sectors" in response.json()