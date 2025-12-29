"""
SQLAlchemy database models for TaskRhythm.

Models represent the core entities: Users, EnergyWindows, and Tasks.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Time, Date
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """
    User account model.
    
    Stores authentication credentials and relationships to energy windows and tasks.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    energy_windows = relationship("EnergyWindow", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class EnergyWindow(Base):
    """
    Energy window model.
    
    Represents a time block during the day with an associated energy level.
    Users define these to match their natural rhythms.
    """
    __tablename__ = "energy_windows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    day_of_week = Column(String(10), nullable=False)  # Monday-Sunday
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    energy_level = Column(String(10), nullable=False)  # high, medium, low
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="energy_windows")
    tasks = relationship("Task", back_populates="assigned_window")

    def __repr__(self):
        return f"<EnergyWindow(id={self.id}, day={self.day_of_week}, energy={self.energy_level})>"


class Task(Base):
    """
    Task model.
    
    Represents an academic task with effort level and optional deadline.
    Tasks are assigned to energy windows by the scheduling algorithm.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    effort_level = Column(String(10), nullable=False)  # high, medium, low
    estimated_duration = Column(Integer, nullable=True)  # Duration in minutes
    deadline = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    assigned_window_id = Column(Integer, ForeignKey("energy_windows.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tasks")
    assigned_window = relationship("EnergyWindow", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', effort={self.effort_level})>"

