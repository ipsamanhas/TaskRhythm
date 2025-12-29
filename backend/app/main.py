"""
TaskRhythm - Main FastAPI application

A human-centered productivity web application that schedules academic tasks
based on natural energy levels instead of rigid time blocks.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import secrets

from .database import init_db
from .routers import auth, energy, tasks, schedule

# Initialize FastAPI app
app = FastAPI(
    title="TaskRhythm",
    description="A human-centered productivity app for students",
    version="0.1.0"
)

# Add session middleware for authentication
# Generate a secret key for production: secrets.token_urlsafe(32)
SECRET_KEY = secrets.token_urlsafe(32)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Setup static files and templates
BASE_DIR = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(energy.router, prefix="/energy", tags=["Energy Windows"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()
    print("✓ Database initialized")
    print("✓ TaskRhythm is ready")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Landing page - shows login form or redirects to dashboard if authenticated.
    """
    user_id = request.session.get("user_id")
    if user_id:
        # User is already logged in, show dashboard link
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "logged_in": True}
        )
    # User not logged in, show login form
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "logged_in": False}
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Main dashboard page - requires authentication.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        # Redirect to login if not authenticated
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "logged_in": False, "error": "Please log in to continue"}
        )
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user_id": user_id}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "TaskRhythm"}

