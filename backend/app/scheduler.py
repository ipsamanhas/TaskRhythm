"""
Core scheduling algorithm for TaskRhythm.

Deterministic task scheduling based on effort-energy mapping.
Uses compassionate, non-judgmental logic to assign tasks.
"""

from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from .models import Task, EnergyWindow


def calculate_window_duration(window: EnergyWindow) -> int:
    """
    Calculate duration of an energy window in minutes.
    
    Args:
        window: EnergyWindow object
        
    Returns:
        Duration in minutes
    """
    # Convert time objects to datetime for calculation
    start = datetime.combine(date.today(), window.time_start)
    end = datetime.combine(date.today(), window.time_end)
    
    # Handle windows that cross midnight
    if end <= start:
        end += timedelta(days=1)
    
    duration = (end - start).total_seconds() / 60
    return int(duration)


def get_available_window_capacity(window: EnergyWindow, db: Session) -> int:
    """
    Get remaining capacity (in minutes) for an energy window.
    
    Calculates how much time is still available after accounting
    for already assigned tasks.
    
    Args:
        window: EnergyWindow object
        db: Database session
        
    Returns:
        Remaining capacity in minutes
    """
    total_duration = calculate_window_duration(window)
    
    # Get all tasks assigned to this window
    assigned_tasks = db.query(Task).filter(
        Task.assigned_window_id == window.id,
        Task.is_completed == False
    ).all()
    
    # Sum up duration of assigned tasks
    used_duration = sum(
        task.estimated_duration for task in assigned_tasks 
        if task.estimated_duration
    )
    
    return max(0, total_duration - used_duration)


def get_effort_priority_order(effort_level: str) -> List[str]:
    """
    Get priority order for energy levels based on task effort.
    
    High-effort tasks prefer high-energy windows, but can use medium.
    Medium-effort tasks prefer medium-energy, can use high or low.
    Low-effort tasks can use any window (prefer low to save high energy).
    
    Args:
        effort_level: Task effort level (high, medium, low)
        
    Returns:
        Ordered list of acceptable energy levels
    """
    priority_map = {
        "high": ["high", "medium"],  # High effort needs good energy
        "medium": ["medium", "high", "low"],  # Medium is flexible
        "low": ["low", "medium", "high"]  # Low effort can fit anywhere
    }
    return priority_map.get(effort_level, ["medium", "high", "low"])


def get_day_name(target_date: date) -> str:
    """
    Get day of week name from date.
    
    Args:
        target_date: Date object
        
    Returns:
        Day name (e.g., "Monday")
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[target_date.weekday()]


def find_best_window(
    task: Task,
    windows: List[EnergyWindow],
    db: Session,
    current_date: date = None
) -> Optional[EnergyWindow]:
    """
    Find the best energy window for a task.
    
    Considers effort-energy mapping, deadline constraints, and capacity.
    Uses graceful degradation if perfect match isn't available.
    
    Args:
        task: Task to schedule
        windows: Available energy windows
        db: Database session
        current_date: Reference date (defaults to today)
        
    Returns:
        Best matching EnergyWindow or None if no suitable window found
    """
    if current_date is None:
        current_date = date.today()
    
    # Get effort priority order
    energy_priorities = get_effort_priority_order(task.effort_level)
    
    # If task has deadline, filter windows before deadline
    candidate_windows = []
    
    if task.deadline:
        # Calculate days until deadline
        days_until_deadline = (task.deadline - current_date).days
        
        # Only consider windows in the next week (or until deadline)
        for window in windows:
            # For MVP, we'll consider windows in the current week
            # In production, we'd want more sophisticated date handling
            if days_until_deadline >= 0:
                candidate_windows.append(window)
    else:
        # No deadline constraint, consider all windows
        candidate_windows = windows
    
    # Try to find window matching energy priorities
    for energy_level in energy_priorities:
        matching_windows = [
            w for w in candidate_windows 
            if w.energy_level == energy_level
        ]
        
        for window in matching_windows:
            # Check if window has enough capacity
            capacity = get_available_window_capacity(window, db)
            task_duration = task.estimated_duration or 60  # Default 60 min if not specified
            
            if capacity >= task_duration:
                return window
    
    # No perfect match found - return None for graceful handling
    return None


def schedule_tasks(user_id: int, db: Session) -> Dict[str, any]:
    """
    Main scheduling algorithm.
    
    Assigns unscheduled tasks to appropriate energy windows using
    deterministic effort-energy mapping with compassionate messaging.
    
    Args:
        user_id: User ID to schedule tasks for
        db: Database session
        
    Returns:
        Dictionary with scheduling results and human-centered message
    """
    # Get all unscheduled, incomplete tasks
    unscheduled_tasks = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_completed == False,
        Task.assigned_window_id == None
    ).order_by(
        Task.deadline.asc().nullslast(),  # Deadline tasks first
        Task.effort_level.desc(),  # High effort next
        Task.created_at.asc()  # Oldest first
    ).all()
    
    # Get all energy windows for user
    windows = db.query(EnergyWindow).filter(
        EnergyWindow.user_id == user_id
    ).all()
    
    # Track results
    assigned_count = 0
    unassigned_tasks = []
    
    # If no windows defined, provide helpful message
    if not windows:
        return {
            "success": True,
            "assigned_count": 0,
            "unassigned_count": len(unscheduled_tasks),
            "message": "To get started, define your energy windows to match your natural rhythm.",
            "unassigned_tasks": unscheduled_tasks
        }
    
    # If no tasks, provide encouraging message
    if not unscheduled_tasks:
        return {
            "success": True,
            "assigned_count": 0,
            "unassigned_count": 0,
            "message": "Your schedule is clear. Add tasks when you're ready.",
            "unassigned_tasks": []
        }
    
    # Attempt to schedule each task
    for task in unscheduled_tasks:
        best_window = find_best_window(task, windows, db)
        
        if best_window:
            # Assign task to window
            task.assigned_window_id = best_window.id
            assigned_count += 1
        else:
            # Could not find suitable window
            unassigned_tasks.append(task)
    
    # Commit all assignments
    db.commit()
    
    # Generate compassionate message
    if assigned_count == 0 and unassigned_tasks:
        message = "These tasks are waiting for an energy window that fits. Consider adding more windows or adjusting task durations."
    elif assigned_count > 0 and unassigned_tasks:
        message = f"Scheduled {assigned_count} task(s). Some tasks need more window space or flexibility."
    elif assigned_count > 0 and not unassigned_tasks:
        message = f"Great! All {assigned_count} task(s) are scheduled to match your energy."
    else:
        message = "Your schedule is ready."
    
    return {
        "success": True,
        "assigned_count": assigned_count,
        "unassigned_count": len(unassigned_tasks),
        "message": message,
        "unassigned_tasks": unassigned_tasks
    }


def clear_schedule(user_id: int, db: Session) -> None:
    """
    Clear all task assignments for a user.
    
    Resets assigned_window_id to None for all user's tasks.
    Useful for re-scheduling from scratch.
    
    Args:
        user_id: User ID to clear schedule for
        db: Database session
    """
    db.query(Task).filter(
        Task.user_id == user_id
    ).update({"assigned_window_id": None})
    
    db.commit()

