import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path to import the main app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

def test_scan_endpoint():
    response = client.get("/scan")
    assert response.status_code == 200
    data = response.json()
    assert "bullish" in data
    assert "bearish" in data
    assert isinstance(data["bullish"], list)
    assert isinstance(data["bearish"], list)

if __name__ == "__main__":
    pytest.main()
