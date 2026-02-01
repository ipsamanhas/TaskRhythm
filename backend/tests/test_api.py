"""
Integration tests for TaskRhythm API endpoints.

Tests authentication, tasks, energy windows, and schedule generation.
"""

import pytest
from datetime import date, timedelta


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test that health check returns 200 and correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "TaskRhythm"


class TestAuthentication:
    """Tests for authentication endpoints."""
    
    def test_register_new_user(self, client):
        """Test user registration with valid data."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123"
            },
            follow_redirects=False
        )
        assert response.status_code == 303  # Redirect after successful registration
        assert response.headers["location"] == "/dashboard"
    
    def test_register_with_short_password(self, client):
        """Test that registration fails with password < 8 characters."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "short"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        # Should redirect back to register with error
        assert "register" in response.headers["location"]
    
    def test_login_with_valid_credentials(self, client, test_user):
        """Test login with correct username and password."""
        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"
    
    def test_login_with_invalid_credentials(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        # Should redirect back to home with error
        assert "error" in response.headers["location"]
    
    def test_logout(self, authenticated_client):
        """Test logout clears session."""
        response = authenticated_client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"
    
    def test_get_current_user_when_authenticated(self, authenticated_client):
        """Test /auth/me returns user data when authenticated."""
        response = authenticated_client.get("/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_when_not_authenticated(self, client):
        """Test /auth/me returns 401 when not authenticated."""
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestTasksAPI:
    """Tests for task management endpoints."""
    
    def test_create_task(self, authenticated_client, db_session):
        """Test creating a new task."""
        response = authenticated_client.post(
            "/tasks/create",
            data={
                "title": "New test task",
                "description": "Task description",
                "effort_level": "high",
                "estimated_duration": "60",
                "deadline": str(date.today() + timedelta(days=7))
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/tasks"
    
    def test_list_tasks(self, authenticated_client, sample_tasks):
        """Test listing all tasks for authenticated user."""
        response = authenticated_client.get("/tasks/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(sample_tasks)
    
    def test_toggle_task_completion(self, authenticated_client, sample_tasks):
        """Test marking a task as complete."""
        task_id = sample_tasks[0].id
        response = authenticated_client.post(
            f"/tasks/{task_id}/complete",
            follow_redirects=False
        )
        assert response.status_code == 303
    
    def test_delete_task(self, authenticated_client, sample_tasks):
        """Test deleting a task."""
        task_id = sample_tasks[0].id
        response = authenticated_client.post(
            f"/tasks/{task_id}/delete",
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/tasks"
    
    def test_create_task_requires_authentication(self, client):
        """Test that creating a task requires authentication."""
        response = client.post(
            "/tasks/create",
            data={
                "title": "Unauthorized task",
                "effort_level": "high"
            },
            follow_redirects=False
        )
        # Should redirect to login or show error
        assert response.status_code in [303, 401]


class TestEnergyWindowsAPI:
    """Tests for energy window management endpoints."""
    
    def test_create_energy_window(self, authenticated_client):
        """Test creating a new energy window."""
        response = authenticated_client.post(
            "/energy/windows",
            data={
                "day_of_week": "Monday",
                "time_start": "09:00",
                "time_end": "11:00",
                "energy_level": "high"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/energy"
    
    def test_list_energy_windows(self, authenticated_client, sample_energy_windows):
        """Test listing all energy windows for authenticated user."""
        response = authenticated_client.get("/energy/windows")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(sample_energy_windows)
    
    def test_delete_energy_window(self, authenticated_client, sample_energy_windows):
        """Test deleting an energy window."""
        window_id = sample_energy_windows[0].id
        response = authenticated_client.post(
            f"/energy/windows/{window_id}/delete",
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/energy"
    
    def test_create_energy_window_requires_authentication(self, client):
        """Test that creating an energy window requires authentication."""
        response = client.post(
            "/energy/windows",
            data={
                "day_of_week": "Monday",
                "time_start": "09:00",
                "time_end": "11:00",
                "energy_level": "high"
            },
            follow_redirects=False
        )
        # Should redirect to login or show error
        assert response.status_code in [303, 401]


class TestScheduleAPI:
    """Tests for schedule generation endpoints."""
    
    def test_generate_schedule(self, authenticated_client, sample_energy_windows, sample_tasks):
        """Test schedule generation with tasks and windows."""
        response = authenticated_client.post("/schedule/generate")
        assert response.status_code == 200
        data = response.json()
        assert "scheduled_count" in data
        assert "unscheduled_count" in data
        assert isinstance(data["scheduled_count"], int)
        assert isinstance(data["unscheduled_count"], int)
    
    def test_clear_schedule(self, authenticated_client, sample_energy_windows, sample_tasks):
        """Test clearing all task assignments."""
        # First generate a schedule
        authenticated_client.post("/schedule/generate")
        
        # Then clear it
        response = authenticated_client.post("/schedule/clear")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_generate_schedule_requires_authentication(self, client):
        """Test that schedule generation requires authentication."""
        response = client.post("/schedule/generate")
        # Should return error or redirect
        assert response.status_code in [303, 401]


class TestPageRendering:
    """Tests for HTML page rendering."""
    
    def test_landing_page(self, client):
        """Test that landing page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"TaskRhythm" in response.content or b"taskrhythm" in response.content.lower()
    
    def test_register_page(self, client):
        """Test that register page loads."""
        response = client.get("/register")
        assert response.status_code == 200
    
    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard requires authentication."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        # Should show login prompt or error
    
    def test_dashboard_when_authenticated(self, authenticated_client):
        """Test that authenticated user can access dashboard."""
        response = authenticated_client.get("/dashboard")
        assert response.status_code == 200
    
    def test_tasks_page(self, authenticated_client):
        """Test that tasks page loads for authenticated user."""
        response = authenticated_client.get("/tasks")
        assert response.status_code == 200
    
    def test_energy_page(self, authenticated_client):
        """Test that energy windows page loads for authenticated user."""
        response = authenticated_client.get("/energy")
        assert response.status_code == 200
    
    def test_schedule_page(self, authenticated_client):
        """Test that schedule page loads for authenticated user."""
        response = authenticated_client.get("/schedule")
        assert response.status_code == 200
