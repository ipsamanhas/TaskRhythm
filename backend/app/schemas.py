"""
Pydantic schemas for request/response validation.

These schemas ensure data validation and provide clear API contracts.
"""

from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


# ============= User Schemas =============

class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @validator('username')
    def username_alphanumeric(cls, v):
        """Ensure username contains only alphanumeric characters and underscores."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


# ============= Energy Window Schemas =============

class EnergyWindowCreate(BaseModel):
    """Schema for creating an energy window."""
    day_of_week: str = Field(..., pattern="^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$")
    time_start: time
    time_end: time
    energy_level: str = Field(..., pattern="^(high|medium|low)$")

    @validator('time_end')
    def end_after_start(cls, v, values):
        """Ensure end time is after start time."""
        if 'time_start' in values and v <= values['time_start']:
            raise ValueError('End time must be after start time')
        return v


class EnergyWindowUpdate(BaseModel):
    """Schema for updating an energy window."""
    day_of_week: Optional[str] = Field(None, pattern="^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$")
    time_start: Optional[time] = None
    time_end: Optional[time] = None
    energy_level: Optional[str] = Field(None, pattern="^(high|medium|low)$")


class EnergyWindowResponse(BaseModel):
    """Schema for energy window in responses."""
    id: int
    user_id: int
    day_of_week: str
    time_start: time
    time_end: time
    energy_level: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Task Schemas =============

class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    effort_level: str = Field(..., pattern="^(high|medium|low)$")
    estimated_duration: Optional[int] = Field(None, gt=0, description="Duration in minutes")
    deadline: Optional[date] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    effort_level: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    estimated_duration: Optional[int] = Field(None, gt=0, description="Duration in minutes")
    deadline: Optional[date] = None
    is_completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task in responses."""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    effort_level: str
    estimated_duration: Optional[int]
    deadline: Optional[date]
    is_completed: bool
    assigned_window_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Schedule Schemas =============

class ScheduleResponse(BaseModel):
    """Schema for schedule view response."""
    message: str
    assigned_tasks: list[TaskResponse]
    unassigned_tasks: list[TaskResponse]

