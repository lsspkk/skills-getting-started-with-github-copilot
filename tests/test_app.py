import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    # Use a test activity and email
    activity = "Chess Club"
    email = "testuser@mergington.edu"

    # Ensure user is not already signed up
    client.post(f"/activities/{activity}/unregister?email={email}")

    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]

    # Duplicate signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400

    # Unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert f"Unregistered {email}" in response.json()["message"]

    # Unregister again should fail
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404

def test_unregister_activity_not_found():
    response = client.post("/activities/Nonexistent/unregister?email=someone@mergington.edu")
    assert response.status_code == 404

def test_signup_activity_full():
    """Test that signup fails when activity is at max capacity"""
    activity = "Mathletes"  # max_participants: 10
    
    # Get current activity state
    activities_response = client.get("/activities")
    activity_data = activities_response.json()[activity]
    max_participants = activity_data["max_participants"]
    
    # Clean up - unregister all test users first
    for i in range(max_participants + 5):
        email = f"fulltest{i}@mergington.edu"
        client.post(f"/activities/{activity}/unregister?email={email}")
    
    # Fill up the activity to max capacity
    test_emails = []
    for i in range(max_participants):
        email = f"fulltest{i}@mergington.edu"
        test_emails.append(email)
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Try to sign up one more student when activity is full
    overflow_email = f"fulltest{max_participants}@mergington.edu"
    response = client.post(f"/activities/{activity}/signup?email={overflow_email}")
    
    # Should return 400 status code
    assert response.status_code == 400
    # Should have an appropriate error message
    assert "full" in response.json()["detail"].lower()
    
    # Cleanup - unregister all test users
    for email in test_emails:
        client.post(f"/activities/{activity}/unregister?email={email}")
