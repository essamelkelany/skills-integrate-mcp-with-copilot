from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_members_list_returns_profiles():
    response = client.get("/members")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(member["email"] == "michael@mergington.edu" for member in data)


def test_create_member_and_assign_activity():
    payload = {
        "name": "Ava Johnson",
        "email": "ava.johnson@mergington.edu",
        "grade": "10",
        "status": "active",
    }

    create_response = client.post("/members", json=payload)
    assert create_response.status_code == 201
    created_member = create_response.json()
    assert created_member["email"] == payload["email"]
    assert created_member["activities"] == []

    signup_response = client.post(
        "/activities/Chess Club/signup?email=ava.johnson@mergington.edu"
    )
    assert signup_response.status_code == 200

    member_response = client.get("/members/ava.johnson@mergington.edu")
    assert member_response.status_code == 200
    member = member_response.json()
    assert "Chess Club" in member["activities"]
