"""
Pytest configuration and shared fixtures for TaskRhythm tests.

Provides test database, FastAPI test client, and authentication fixtures.
"""

# Patch bcrypt to truncate passwords to 72 bytes before passlib/bcrypt backend
# detection runs (passlib's internal detect_wrap_bug can pass long strings).
import bcrypt as _bcrypt_mod

_original_hashpw = _bcrypt_mod.hashpw

def _truncating_hashpw(secret: bytes, salt: bytes) -> bytes:
    if len(secret) > 72:
        secret = secret[:72]
    return _original_hashpw(secret, salt)

_bcrypt_mod.hashpw = _truncating_hashpw

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, EnergyWindow, Task
from app.auth import hash_password

# Test database setup - use in-memory SQLite
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    
    Creates all tables, yields the session, then drops all tables.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI test client with test database dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """
    Create a test user in the database.
    
    Returns:
        User object with username='testuser', email='test@example.com'
    """
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Test client with an authenticated session.
    
    Logs in the test_user and returns the client with session cookies.
    """
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword123"},
        follow_redirects=False
    )
    assert response.status_code == 303, f"Expected 303 redirect after login, got {response.status_code}"
    return client


@pytest.fixture
def sample_energy_windows(db_session, test_user):
    """
    Create sample energy windows for testing.
    
    Returns:
        List of EnergyWindow objects (high, medium, low energy on Monday)
    """
    from datetime import time
    
    windows = [
        EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(9, 0),
            time_end=time(11, 0),
            energy_level="high"
        ),
        EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(14, 0),
            time_end=time(16, 0),
            energy_level="medium"
        ),
        EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(20, 0),
            time_end=time(21, 0),
            energy_level="low"
        ),
    ]
    
    for window in windows:
        db_session.add(window)
    db_session.commit()
    
    for window in windows:
        db_session.refresh(window)
    
    return windows


@pytest.fixture
def sample_tasks(db_session, test_user):
    """
    Create sample tasks for testing.
    
    Returns:
        List of Task objects with varying effort levels
    """
    from datetime import date, timedelta
    
    tasks = [
        Task(
            user_id=test_user.id,
            title="High effort task",
            effort_level="high",
            estimated_duration=60,
            deadline=date.today() + timedelta(days=3)
        ),
        Task(
            user_id=test_user.id,
            title="Medium effort task",
            effort_level="medium",
            estimated_duration=45,
            deadline=date.today() + timedelta(days=5)
        ),
        Task(
            user_id=test_user.id,
            title="Low effort task",
            effort_level="low",
            estimated_duration=30,
            deadline=date.today() + timedelta(days=7)
        ),
    ]
    
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    
    for task in tasks:
        db_session.refresh(task)
    
    return tasks
