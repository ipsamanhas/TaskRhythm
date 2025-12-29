"""
Authentication routes for login, logout, and registration.

Handles user authentication using session-based cookies.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import create_user, authenticate_user, get_current_user
from ..schemas import UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Creates a new user with hashed password and automatically logs them in.
    """
    try:
        # Validate password length
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Create user
        user_data = UserCreate(username=username, email=email, password=password)
        user = create_user(db, user_data)
        
        # Automatically log in the new user
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        
        # Redirect to dashboard
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        
    except HTTPException as e:
        # Return to registration page with error
        return RedirectResponse(
            url=f"/register?error={e.detail}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/register?error=Registration failed. Please try again.",
            status_code=status.HTTP_303_SEE_OTHER
        )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Log in an existing user.
    
    Authenticates credentials and creates a session.
    """
    # Authenticate user
    user = authenticate_user(db, username, password)
    
    if not user:
        # Return to login page with error
        return RedirectResponse(
            url="/?error=Invalid username or password",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    # Redirect to dashboard
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
@router.get("/logout")
async def logout(request: Request):
    """
    Log out the current user.
    
    Clears the session and redirects to home page.
    """
    # Clear session
    request.session.clear()
    
    # Redirect to home page
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/me", response_model=UserResponse)
async def get_me(request: Request, db: Session = Depends(get_db)):
    """
    Get current authenticated user information.
    
    Returns user data if authenticated, otherwise raises 401 error.
    """
    user_id = request.session.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = get_current_user(db, user_id)
    
    if not user:
        # Clear invalid session
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

