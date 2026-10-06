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

def test_eligibility_api_endpoint_single(client):
    payload = {
        "scheme_id": "pm-kisan",
        "profile": {
            "age": 28,
            "occupation": "farmer",
            "state": "Maharashtra"
        }
    }
    response = client.post("/api/eligibility", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    eval_res = data[0]
    assert eval_res["scheme_id"] == "pm-kisan"
    assert eval_res["status"] == "ELIGIBLE"
    assert eval_res["official_url"] == "https://pmkisan.gov.in"

def test_eligibility_api_endpoint_missing_info(client):
    payload = {
        "scheme_id": "sanjay-gandhi-niradhar",
        "profile": {
            "state": "Maharashtra"
            # Missing income and age
        }
    }
    response = client.post("/api/eligibility", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    eval_res = data[0]
    assert eval_res["scheme_id"] == "sanjay-gandhi-niradhar"
    assert eval_res["status"] == "INFORMATION_MISSING"
    assert "annual_income" in eval_res["missing_fields"]
    assert "age" in eval_res["missing_fields"]

def test_chat_api_endpoint_clarification(client):
    payload = {
        "message": "Find schemes for me"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["needs_clarification"] is True
    assert len(data["response"]) > 0
    assert "session_state" in data

def test_chat_api_endpoint_full_flow(client):
    payload = {
        "message": "I am a 25 years old farmer from Maharashtra with income 2 lakh. Tell me what schemes I can apply for."
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["needs_clarification"] is False
    assert len(data["recommendations"]) > 0
    assert "PM-KISAN" in data["response"]
    assert len(data["source_urls"]) > 0
    assert "https://pmkisan.gov.in" in data["source_urls"]


