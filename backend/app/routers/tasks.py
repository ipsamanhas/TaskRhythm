"""
Tasks CRUD routes.

Handles creation, reading, updating, and deletion of academic tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from pathlib import Path
from typing import Optional

from ..database import get_db
from ..models import Task
from ..schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

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
async def tasks_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Task management page.
    
    Shows form to add new tasks and list of existing tasks.
    """
    user_id = request.session.get("user_id")
    
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get user's tasks
    tasks = db.query(Task).filter(
        Task.user_id == user_id
    ).order_by(
        Task.is_completed,
        Task.deadline,
        Task.created_at.desc()
    ).all()
    
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks,
            "levels": ["high", "medium", "low"]
        }
    )


@router.get("/list", response_model=list[TaskResponse])
async def list_tasks(
    request: Request,
    include_completed: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all tasks for the authenticated user.
    
    By default, excludes completed tasks.
    """
    user_id = require_auth(request)
    
    query = db.query(Task).filter(Task.user_id == user_id)
    
    if not include_completed:
        query = query.filter(Task.is_completed == False)
    
    tasks = query.order_by(
        Task.is_completed,
        Task.deadline,
        Task.created_at.desc()
    ).all()
    
    return tasks


@router.post("/create")
async def create_task(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    effort_level: str = Form(...),
    estimated_duration: Optional[int] = Form(None),
    deadline: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the authenticated user.
    """
    user_id = require_auth(request)
    
    try:
        # Parse deadline if provided
        deadline_date = None
        if deadline and deadline.strip():
            deadline_date = date.fromisoformat(deadline)
        
        # Create task
        task = Task(
            user_id=user_id,
            title=title,
            description=description if description else None,
            effort_level=effort_level,
            estimated_duration=estimated_duration if estimated_duration else None,
            deadline=deadline_date
        )
        
        db.add(task)
        db.commit()
        
        return RedirectResponse(url="/tasks", status_code=status.HTTP_303_SEE_OTHER)
        
    except ValueError as e:
        return RedirectResponse(
            url="/tasks?error=Invalid date format",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        return RedirectResponse(
            url="/tasks?error=Failed to create task",
            status_code=status.HTTP_303_SEE_OTHER
        )


@router.post("/{task_id}/complete")
async def toggle_task_completion(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Toggle task completion status.
    
    Only the owner can modify their tasks.
    """
    user_id = require_auth(request)
    
    # Get task and verify ownership
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        return RedirectResponse(
            url="/tasks?error=Task not found",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Toggle completion status
    task.is_completed = not task.is_completed
    db.commit()
    
    return RedirectResponse(url="/tasks", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{task_id}/delete")
async def delete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Delete a task.
    
    Only the owner can delete their tasks.
    """
    user_id = require_auth(request)
    
    # Get task and verify ownership
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        return RedirectResponse(
            url="/tasks?error=Task not found",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Delete task
    db.delete(task)
    db.commit()
    
    return RedirectResponse(url="/tasks", status_code=status.HTTP_303_SEE_OTHER)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update a task.
    
    Only the owner can update their tasks.
    """
    user_id = require_auth(request)
    
    # Get task and verify ownership
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields if provided
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

