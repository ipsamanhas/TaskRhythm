"""
Database configuration and session management for TaskRhythm.

Uses SQLite for MVP simplicity with SQLAlchemy ORM.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database file path - store in project root
DATABASE_DIR = Path(__file__).parent.parent.parent
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/taskrhythm.db"

# Create engine with check_same_thread=False for SQLite
# This allows FastAPI to use the database from different threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query debugging
)

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    
    Yields database session and ensures it's closed after use.
    Use with FastAPI's Depends() for automatic session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    
    Call this on application startup to ensure tables exist.
    Safe to call multiple times - only creates missing tables.
    """
    Base.metadata.create_all(bind=engine)

