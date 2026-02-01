"""
Schedule routes for task assignment and viewing.

Handles schedule generation and display.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from collections import defaultdict

from ..database import get_db
from ..models import Task, EnergyWindow
from ..scheduler import schedule_tasks, clear_schedule

router = APIRouter()
logger = logging.getLogger(__name__)

# Setup templates
BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def require_auth(request: Request) -> int:
    """
    Dependency to require authentication.
    
    Returns user_id if authenticated, otherwise raises HTTPException.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_id


@router.get("/", response_class=HTMLResponse)
@router.get("/view", response_class=HTMLResponse)
async def schedule_view(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Schedule view page.
    
    Shows tasks organized by energy windows with compassionate messaging.
    """
    user_id = request.session.get("user_id")
    
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get all energy windows
    windows = db.query(EnergyWindow).filter(
        EnergyWindow.user_id == user_id
    ).order_by(
        EnergyWindow.day_of_week,
        EnergyWindow.time_start
    ).all()
    
    # Get assigned tasks
    assigned_tasks = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_completed == False,
        Task.assigned_window_id != None
    ).all()
    
    # Get unassigned tasks
    unassigned_tasks = db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_completed == False,
        Task.assigned_window_id == None
    ).all()
    
    # Organize tasks by window
    tasks_by_window = defaultdict(list)
    for task in assigned_tasks:
        tasks_by_window[task.assigned_window_id].append(task)
    
    # Generate compassionate message
    if not windows:
        message = "Define your energy windows to get started with scheduling."
        message_type = "info"
    elif not assigned_tasks and not unassigned_tasks:
        message = "Your schedule is clear. Add tasks when you're ready."
        message_type = "success"
    elif unassigned_tasks and not assigned_tasks:
        message = "These tasks are waiting to be scheduled. Click 'Generate Schedule' to assign them."
        message_type = "info"
    elif assigned_tasks and not unassigned_tasks:
        message = f"All set! {len(assigned_tasks)} task(s) are scheduled to match your energy."
        message_type = "success"
    else:
        message = f"{len(assigned_tasks)} task(s) scheduled. {len(unassigned_tasks)} task(s) still need a window."
        message_type = "warning"
    
    return templates.TemplateResponse(
        "schedule.html",
        {
            "request": request,
            "windows": windows,
            "tasks_by_window": dict(tasks_by_window),
            "unassigned_tasks": unassigned_tasks,
            "message": message,
            "message_type": message_type
        }
    )


@router.post("/generate")
async def generate_schedule(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Generate schedule by running the scheduling algorithm.
    
    Assigns unscheduled tasks to appropriate energy windows.
    """
    user_id = require_auth(request)
    
    try:
        # Run scheduling algorithm
        result = schedule_tasks(user_id, db)
        
        logger.info(
            f"Schedule generated for user {user_id}: "
            f"{result['assigned_count']} scheduled, {result['unassigned_count']} unscheduled"
        )
        
        json_data = {
            "success": result["success"],
            "scheduled_count": result["assigned_count"],
            "unscheduled_count": result["unassigned_count"],
            "message": result["message"]
        }
        # Browser form expects redirect; API/tests expect JSON
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(
                url=f"/schedule?success={result['message']}",
                status_code=status.HTTP_303_SEE_OTHER
            )
        return JSONResponse(content=json_data)
        
    except Exception as e:
        logger.exception(f"Failed to generate schedule for user {user_id}")
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(
                url="/schedule?error=Failed to generate schedule",
                status_code=status.HTTP_303_SEE_OTHER
            )
        return JSONResponse(
            content={"error": "Failed to generate schedule"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/clear")
async def clear_user_schedule(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Clear all task assignments.
    
    Removes all task-to-window assignments to start fresh.
    """
    user_id = require_auth(request)
    
    try:
        # Clear schedule
        clear_schedule(user_id, db)
        
        logger.info(f"Schedule cleared for user {user_id}")
        
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(
                url="/schedule?success=Schedule cleared. Tasks are ready to be rescheduled.",
                status_code=status.HTTP_303_SEE_OTHER
            )
        return JSONResponse(content={"message": "Schedule cleared successfully"})
        
    except Exception as e:
        logger.exception(f"Failed to clear schedule for user {user_id}")
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(
                url="/schedule?error=Failed to clear schedule",
                status_code=status.HTTP_303_SEE_OTHER
            )
        return JSONResponse(
            content={"error": "Failed to clear schedule"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

