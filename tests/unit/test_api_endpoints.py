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

def test_auth_register_with_profile_and_login(client):
    import uuid
    uid = uuid.uuid4().hex[:8]
    test_user = f"citizen_{uid}"
    reg_payload = {
        "username": test_user,
        "full_name": "Rajesh Patil",
        "password": "Password123",
        "email": f"{test_user}@example.com",
        "age": 32,
        "occupation": "farmer",
        "state": "Maharashtra",
        "annual_income": 180000.0
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["username"] == test_user
    assert reg_data["full_name"] == "Rajesh Patil"
    assert reg_data["session_id"] is not None
    assert reg_data["profile"]["age"] == 32
    assert reg_data["profile"]["occupation"] == "farmer"

    sid = reg_data["session_id"]

    # Verify /api/auth/me returns profile
    me_resp = client.get(f"/api/auth/me?session_id={sid}")
    assert me_resp.status_code == 200
    assert me_resp.json()["profile"]["state"] == "Maharashtra"

    # Verify /api/profile/{session_id}
    prof_resp = client.get(f"/api/profile/{sid}")
    assert prof_resp.status_code == 200
    assert prof_resp.json()["occupation"] == "farmer"

    # Verify update profile
    update_resp = client.put(f"/api/profile/{sid}", json={
        "age": 33,
        "occupation": "farmer",
        "state": "Maharashtra",
        "annual_income": 200000.0
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["age"] == 33

    # Verify chat session persistence
    chat_resp = client.post("/api/chat", json={
        "message": "Which loan subsidies can I get for drip irrigation?",
        "session_id": sid
    })
    assert chat_resp.status_code == 200

    # Verify conversation history stored
    conv_resp = client.get(f"/api/conversations/{sid}")
    assert conv_resp.status_code == 200
    history = conv_resp.json()
    assert len(history) >= 2
    assert history[0]["role"] == "user"
    assert "drip irrigation" in history[0]["content"]
    assert history[1]["role"] == "assistant"

    # Verify clear history
    clear_resp = client.delete(f"/api/conversations/{sid}")
    assert clear_resp.status_code == 200
    cleared_history = client.get(f"/api/conversations/{sid}").json()
    assert len(cleared_history) == 0


def test_guest_chat_and_sync_flow(client):
    """Verify that guest users can chat without login, and later sync their messages into an account."""
    import uuid
    guest_sid = f"guest-{uuid.uuid4().hex[:12]}"

    # 1. Guest chat turns without an account
    resp1 = client.post("/api/chat", json={
        "message": "I am a 25 year old student in Maharashtra looking for education loans.",
        "session_id": guest_sid
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "response" in data1
    assert data1["profile"]["age"] == 25
    assert data1["profile"]["state"] == "Maharashtra"

    # Guest history endpoints should return empty gracefully
    guest_hist = client.get(f"/api/conversations/{guest_sid}").json()
    assert guest_hist == []

    guest_prof = client.get(f"/api/profile/{guest_sid}").json()
    assert guest_prof == {}

    guest_clear = client.delete(f"/api/conversations/{guest_sid}").json()
    assert guest_clear["status"] == "cleared"

    # 2. Citizen decides to register/login to store chat details
    uid = uuid.uuid4().hex[:8]
    test_user = f"student_{uid}"
    reg_resp = client.post("/api/auth/register", json={
        "username": test_user,
        "full_name": "Aarav Sharma",
        "password": "Password123",
        "email": f"{test_user}@example.com",
        "age": 25,
        "occupation": "student",
        "state": "Maharashtra"
    })
    assert reg_resp.status_code == 200
    user_sid = reg_resp.json()["session_id"]

    # 3. Sync guest conversation into the registered user account
    sync_resp = client.post("/api/conversations/sync", json={
        "session_id": user_sid,
        "messages": [
            {"role": "user", "content": "I am a 25 year old student in Maharashtra looking for education loans."},
            {"role": "assistant", "content": data1["response"]}
        ]
    })
    assert sync_resp.status_code == 200
    assert sync_resp.json()["status"] == "synced"
    assert sync_resp.json()["count"] == 2

    # 4. Verify conversation is now saved in user account
    saved_hist = client.get(f"/api/conversations/{user_sid}").json()
    assert len(saved_hist) == 2
    assert saved_hist[0]["role"] == "user"
    assert "student in Maharashtra" in saved_hist[0]["content"]
    assert saved_hist[1]["role"] == "assistant"



