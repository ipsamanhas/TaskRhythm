"""
Energy windows CRUD routes.

Handles creation, reading, updating, and deletion of energy windows.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import time
from pathlib import Path

from ..database import get_db
from ..models import EnergyWindow
from ..schemas import EnergyWindowCreate, EnergyWindowUpdate, EnergyWindowResponse

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
async def energy_windows_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Energy windows configuration page.
    
    Shows form to add new windows and list of existing windows.
    """
    user_id = request.session.get("user_id")
    
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get user's energy windows
    windows = db.query(EnergyWindow).filter(
        EnergyWindow.user_id == user_id
    ).order_by(
        EnergyWindow.day_of_week,
        EnergyWindow.time_start
    ).all()
    
    return templates.TemplateResponse(
        "energy_windows.html",
        {
            "request": request,
            "windows": windows,
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "levels": ["high", "medium", "low"]
        }
    )


@router.get("/windows", response_model=list[EnergyWindowResponse])
async def list_energy_windows(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get all energy windows for the authenticated user.
    """
    user_id = require_auth(request)
    
    windows = db.query(EnergyWindow).filter(
        EnergyWindow.user_id == user_id
    ).order_by(
        EnergyWindow.day_of_week,
        EnergyWindow.time_start
    ).all()
    
    return windows


@router.post("/windows")
async def create_energy_window(
    request: Request,
    day_of_week: str = Form(...),
    time_start: str = Form(...),
    time_end: str = Form(...),
    energy_level: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create a new energy window for the authenticated user.
    """
    user_id = require_auth(request)
    
    try:
        # Parse time strings (format: "HH:MM")
        start_time = time.fromisoformat(time_start)
        end_time = time.fromisoformat(time_end)
        
        # Validate that end time is after start time
        if end_time <= start_time:
            return RedirectResponse(
                url="/energy?error=End time must be after start time",
                status_code=status.HTTP_303_SEE_OTHER
            )
        
        # Create window
        window = EnergyWindow(
            user_id=user_id,
            day_of_week=day_of_week,
            time_start=start_time,
            time_end=end_time,
            energy_level=energy_level
        )
        
        db.add(window)
        db.commit()
        
        return RedirectResponse(url="/energy", status_code=status.HTTP_303_SEE_OTHER)
        
    except ValueError as e:
        return RedirectResponse(
            url="/energy?error=Invalid time format",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        return RedirectResponse(
            url="/energy?error=Failed to create energy window",
            status_code=status.HTTP_303_SEE_OTHER
        )


@router.post("/windows/{window_id}/delete")
async def delete_energy_window(
    window_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Delete an energy window.
    
    Only the owner can delete their energy windows.
    """
    user_id = require_auth(request)
    
    # Get window and verify ownership
    window = db.query(EnergyWindow).filter(
        EnergyWindow.id == window_id,
        EnergyWindow.user_id == user_id
    ).first()
    
    if not window:
        return RedirectResponse(
            url="/energy?error=Energy window not found",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Delete window
    db.delete(window)
    db.commit()
    
    return RedirectResponse(url="/energy", status_code=status.HTTP_303_SEE_OTHER)


@router.put("/windows/{window_id}", response_model=EnergyWindowResponse)
async def update_energy_window(
    window_id: int,
    window_data: EnergyWindowUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update an energy window.
    
    Only the owner can update their energy windows.
    """
    user_id = require_auth(request)
    
    # Get window and verify ownership
    window = db.query(EnergyWindow).filter(
        EnergyWindow.id == window_id,
        EnergyWindow.user_id == user_id
    ).first()
    
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy window not found"
        )
    
    # Update fields if provided
    update_data = window_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(window, field, value)
    
    db.commit()
    db.refresh(window)
    
    return window

