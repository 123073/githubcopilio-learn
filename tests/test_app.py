"""
Tests for Mergington High School Activities API
"""

import pytest
from src.app import app, activities


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that the response contains expected activities"""
        response = client.get("/activities")
        activities_data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities_data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_details in activities_data.items():
            for field in required_fields:
                assert field in activity_details, f"Activity {activity_name} missing field {field}"


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_new_participant_returns_200(self, client):
        """Test that signing up a new participant returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=uniquetest0@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=uniquetest1@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that signing up the same participant twice returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a nonexistent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "test@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Check new count
        response = client.get("/activities")
        new_count = len(response.json()[activity_name]["participants"])
        
        assert new_count == initial_count + 1
        assert email in response.json()[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_existing_participant_returns_200(self, client):
        """Test that unregistering an existing participant returns 200"""
        email = "existingstudent@mergington.edu"
        
        # First sign up
        client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
    
    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a success message"""
        email = "removetest@mergington.edu"
        
        # Sign up first
        client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        
        # Unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonparticipant_returns_400(self, client):
        """Test that unregistering a non-participant returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonparticipant@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a nonexistent activity returns 404"""
        response = client.delete(
            "/activities/NonexistentActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "removetest2@mergington.edu"
        activity_name = "Programming Class"
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Get count after signup
        response = client.get("/activities")
        after_signup = len(response.json()[activity_name]["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Check count after unregister
        response = client.get("/activities")
        after_unregister = len(response.json()[activity_name]["participants"])
        
        assert after_unregister == after_signup - 1
        assert email not in response.json()[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
