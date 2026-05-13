"""
Tests for the Mergington High School Activities API
Using the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide TestClient for API testing"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset activities to a clean state before each test.
    This ensures test isolation by resetting the in-memory database.
    """
    # Store the original state
    original_activities = deepcopy(activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(deepcopy(original_activities))


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_success(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: No setup needed, activities are pre-populated
        - Act: Make GET request to /activities
        - Assert: Verify status code is 200
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Activities are pre-populated in the database
        - Act: Make GET request to /activities
        - Assert: Verify all activities are returned
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data) == 9  # Verify we get all activities
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: No setup needed
        - Act: Make GET request and parse response
        - Assert: Verify response structure has required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Get an empty activity (Basketball Club has no participants)
        - Act: Sign up a new student
        - Assert: Verify status is 200 and student is added
        """
        # Arrange
        activity_name = "Basketball Club"
        email = "new.student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert f"Signed up {email}" in response.json()["message"]
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email_fails(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Attempt to sign up same email twice
        - Act: First signup succeeds, second signup attempts
        - Assert: Second signup fails with 400 status
        """
        # Arrange
        activity_name = "Basketball Club"
        email = "student@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Second signup (duplicate)
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_invalid_activity_fails(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Prepare invalid activity name
        - Act: Attempt signup for non-existent activity
        - Assert: Verify 404 response
        """
        # Arrange
        invalid_activity = "Non-Existent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Track initial participant count
        - Act: Sign up a student
        - Assert: Verify participant list grows by 1
        """
        # Arrange
        activity_name = "Soccer Team"
        initial_count = len(activities[activity_name]["participants"])
        email = "player@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Student is already registered in Chess Club
        - Act: Unregister the student
        - Assert: Verify status is 200 and student is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Pre-registered in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert f"Unregistered {email}" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_not_registered_email_fails(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Prepare email not registered for activity
        - Act: Attempt to unregister non-registered email
        - Assert: Verify 400 status
        """
        # Arrange
        activity_name = "Chess Club"
        email = "not.registered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_invalid_activity_fails(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Prepare invalid activity name
        - Act: Attempt unregister from non-existent activity
        - Assert: Verify 404 response
        """
        # Arrange
        invalid_activity = "Phantom Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_removes_participant_from_list(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Track initial participant count
        - Act: Unregister a student
        - Assert: Verify participant list shrinks by 1
        """
        # Arrange
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])
        email = "michael@mergington.edu"  # Pre-registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count - 1


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints"""
    
    def test_signup_then_unregister_flow(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Prepare activity and email
        - Act: Sign up, verify in list, then unregister
        - Assert: Verify participant added then removed
        """
        # Arrange
        activity_name = "Art Club"
        email = "artist@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Signup
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert - Unregister
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """
        AAA Pattern:
        - Arrange: Prepare multiple unique emails
        - Act: Sign up multiple students to same activity
        - Assert: Verify all students in participant list
        """
        # Arrange
        activity_name = "Drama Club"
        emails = [
            "actor1@mergington.edu",
            "actor2@mergington.edu",
            "actor3@mergington.edu"
        ]
        
        # Act - Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        for email in emails:
            assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3
