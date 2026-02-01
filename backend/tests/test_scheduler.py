"""
Unit tests for the TaskRhythm scheduling algorithm.

Tests core scheduling logic, capacity management, and effort-energy mapping.
"""

import pytest
from datetime import time, date, timedelta

from app.scheduler import (
    calculate_window_duration,
    get_available_window_capacity,
    get_effort_priority_order,
    get_day_name,
    find_best_window,
    schedule_tasks,
)
from app.models import EnergyWindow, Task


class TestCalculateWindowDuration:
    """Tests for window duration calculation."""
    
    def test_normal_window(self, db_session, test_user):
        """Test duration calculation for a normal time window."""
        window = EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(9, 0),
            time_end=time(11, 0),
            energy_level="high"
        )
        duration = calculate_window_duration(window)
        assert duration == 120  # 2 hours = 120 minutes
    
    def test_window_crossing_midnight(self, db_session, test_user):
        """Test duration calculation for a window that crosses midnight."""
        window = EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(23, 0),
            time_end=time(1, 0),
            energy_level="low"
        )
        duration = calculate_window_duration(window)
        assert duration == 120  # 2 hours = 120 minutes
    
    def test_short_window(self, db_session, test_user):
        """Test duration calculation for a short window."""
        window = EnergyWindow(
            user_id=test_user.id,
            day_of_week="Tuesday",
            time_start=time(14, 0),
            time_end=time(14, 30),
            energy_level="medium"
        )
        duration = calculate_window_duration(window)
        assert duration == 30  # 30 minutes


class TestGetAvailableWindowCapacity:
    """Tests for window capacity calculation."""
    
    def test_empty_window(self, db_session, test_user):
        """Test capacity for a window with no assigned tasks."""
        window = EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(9, 0),
            time_end=time(11, 0),
            energy_level="high"
        )
        db_session.add(window)
        db_session.commit()
        db_session.refresh(window)
        
        capacity = get_available_window_capacity(window, db_session)
        assert capacity == 120  # Full 2-hour window available
    
    def test_partially_filled_window(self, db_session, test_user):
        """Test capacity for a window with some assigned tasks."""
        window = EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(9, 0),
            time_end=time(11, 0),
            energy_level="high"
        )
        db_session.add(window)
        db_session.commit()
        db_session.refresh(window)
        
        # Add a task that takes 60 minutes
        task = Task(
            user_id=test_user.id,
            title="Test task",
            effort_level="high",
            estimated_duration=60,
            assigned_window_id=window.id
        )
        db_session.add(task)
        db_session.commit()
        
        capacity = get_available_window_capacity(window, db_session)
        assert capacity == 60  # 120 - 60 = 60 minutes remaining
    
    def test_completed_tasks_dont_reduce_capacity(self, db_session, test_user):
        """Test that completed tasks don't reduce available capacity."""
        window = EnergyWindow(
            user_id=test_user.id,
            day_of_week="Monday",
            time_start=time(9, 0),
            time_end=time(11, 0),
            energy_level="high"
        )
        db_session.add(window)
        db_session.commit()
        db_session.refresh(window)
        
        # Add a completed task
        task = Task(
            user_id=test_user.id,
            title="Completed task",
            effort_level="high",
            estimated_duration=60,
            assigned_window_id=window.id,
            is_completed=True
        )
        db_session.add(task)
        db_session.commit()
        
        capacity = get_available_window_capacity(window, db_session)
        assert capacity == 120  # Full capacity since task is completed


class TestGetEffortPriorityOrder:
    """Tests for effort-energy priority mapping."""
    
    def test_high_effort_priority(self):
        """High effort tasks should prefer high energy windows."""
        priority = get_effort_priority_order("high")
        assert priority == ["high", "medium"]
        assert priority[0] == "high"  # Prefer high energy first
    
    def test_medium_effort_priority(self):
        """Medium effort tasks should be flexible."""
        priority = get_effort_priority_order("medium")
        assert priority == ["medium", "high", "low"]
        assert priority[0] == "medium"  # Prefer medium energy first
    
    def test_low_effort_priority(self):
        """Low effort tasks should prefer low energy to save high energy."""
        priority = get_effort_priority_order("low")
        assert priority == ["low", "medium", "high"]
        assert priority[0] == "low"  # Prefer low energy first


class TestGetDayName:
    """Tests for day name conversion."""
    
    def test_monday(self):
        """Test Monday date conversion."""
        # January 6, 2025 is a Monday
        test_date = date(2025, 1, 6)
        assert get_day_name(test_date) == "Monday"
    
    def test_friday(self):
        """Test Friday date conversion."""
        # January 10, 2025 is a Friday
        test_date = date(2025, 1, 10)
        assert get_day_name(test_date) == "Friday"
    
    def test_sunday(self):
        """Test Sunday date conversion."""
        # January 12, 2025 is a Sunday
        test_date = date(2025, 1, 12)
        assert get_day_name(test_date) == "Sunday"


class TestFindBestWindow:
    """Tests for finding the best window for a task."""
    
    def test_high_effort_gets_high_energy(self, db_session, test_user, sample_energy_windows):
        """High effort task should be assigned to high energy window."""
        task = Task(
            user_id=test_user.id,
            title="High effort task",
            effort_level="high",
            estimated_duration=60
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        best_window = find_best_window(task, sample_energy_windows, db_session)
        assert best_window is not None
        assert best_window.energy_level == "high"
    
    def test_low_effort_gets_low_energy(self, db_session, test_user, sample_energy_windows):
        """Low effort task should be assigned to low energy window."""
        task = Task(
            user_id=test_user.id,
            title="Low effort task",
            effort_level="low",
            estimated_duration=30
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        best_window = find_best_window(task, sample_energy_windows, db_session)
        assert best_window is not None
        assert best_window.energy_level == "low"
    
    def test_no_window_when_insufficient_capacity(self, db_session, test_user, sample_energy_windows):
        """Task should not be assigned if no window has sufficient capacity."""
        # Create a task that's too long for any window
        task = Task(
            user_id=test_user.id,
            title="Very long task",
            effort_level="high",
            estimated_duration=300  # 5 hours, longer than any window
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        best_window = find_best_window(task, sample_energy_windows, db_session)
        assert best_window is None


class TestGenerateSchedule:
    """Tests for the full schedule generation."""
    
    def test_schedule_generation_with_tasks_and_windows(
        self, db_session, test_user, sample_energy_windows, sample_tasks
    ):
        """Test that schedule generation assigns tasks to appropriate windows."""
        result = schedule_tasks(test_user.id, db_session)
        
        assert "assigned_count" in result
        assert "unassigned_count" in result
        assert result["assigned_count"] >= 0
        assert result["unassigned_count"] >= 0
        
        # Check that some tasks were scheduled
        scheduled_tasks = db_session.query(Task).filter(
            Task.user_id == test_user.id,
            Task.assigned_window_id.isnot(None)
        ).all()
        
        assert len(scheduled_tasks) > 0
    
    def test_schedule_generation_with_no_windows(self, db_session, test_user, sample_tasks):
        """Test schedule generation when user has no energy windows."""
        result = schedule_tasks(test_user.id, db_session)
        
        assert result["assigned_count"] == 0
        assert result["unassigned_count"] == len(sample_tasks)
    
    def test_schedule_generation_with_no_tasks(self, db_session, test_user, sample_energy_windows):
        """Test schedule generation when user has no tasks."""
        result = schedule_tasks(test_user.id, db_session)
        
        assert result["assigned_count"] == 0
        assert result["unassigned_count"] == 0
    
    def test_schedule_respects_effort_energy_mapping(
        self, db_session, test_user, sample_energy_windows, sample_tasks
    ):
        """Test that scheduled tasks respect effort-energy mapping."""
        schedule_tasks(test_user.id, db_session)
        
        # Check high effort task got high or medium energy window
        high_task = db_session.query(Task).filter(
            Task.user_id == test_user.id,
            Task.effort_level == "high"
        ).first()
        
        if high_task.assigned_window_id:
            window = db_session.query(EnergyWindow).filter(
                EnergyWindow.id == high_task.assigned_window_id
            ).first()
            assert window.energy_level in ["high", "medium"]
