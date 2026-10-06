import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["indexed_schemes"] >= 4
    assert data["total_chunks"] >= 16

def test_list_schemes_endpoint(client):
    response = client.get("/api/schemes")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) >= 4
    scheme_ids = [s["scheme_id"] for s in schemes]
    assert "pm-kisan" in scheme_ids
    assert "ayushman-bharat" in scheme_ids

def test_retrieve_api_endpoint(client):
    payload = {
        "query": "PM-KISAN eligibility for small farmers",
        "top_k": 3,
        "debug": True
    }
    response = client.post("/api/retrieve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert top["scheme_id"] == "pm-kisan"
    assert top["official_url"] == "https://pmkisan.gov.in"
    assert data["debug_info"] is not None
    assert "pm-kisan" in [r["scheme_id"] for r in data["debug_info"]["final_top_k"]]
