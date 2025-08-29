# app/routes/auth.py

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError
from typing import  cast

# Import your database session dependency, User model, and security functions
from app.database.database import get_db

from app.database.models.user import User
from app.auth import security

# Create an APIRouter instance
# This helps in organizing your routes. You'll include this router in your main app.
router = APIRouter()

# Setup Jinja2 templates
# Make sure the directory path is correct based on your project structure.
templates = Jinja2Templates(directory="app/templates")


# Dependency to get the current user from the token in the cookie
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependency function to get the current user from the JWT token
    stored in the request's cookies.

    Args:
        request (Request): The incoming request object.
        db (Session): The database session.

    Raises:
        HTTPException: If the token is missing, invalid, or the user is not found.

    Returns:
        User: The authenticated user object from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        detail="Could not validate credentials",
        headers={"Location": "/login"}, # Redirect to login page
    )
    
    # 1. Get the token from the cookies
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    # The token in the cookie is expected to be in the format "Bearer <token>"
    try:
        token_value = token.split(" ")[1]
        payload = security.decode_access_token(token_value)
        username: str = cast(str,payload.get("sub"))
        if username is None:
            raise credentials_exception
    except (JWTError, IndexError):
        # This catches errors from splitting, decoding, or if 'sub' is missing
        raise credentials_exception
    
    # 2. Find the user in the database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # 3. Return the user object
    return user


# --- HTML Page Routes ---

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serves the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serves the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: User = Depends(get_current_user)):
    """
    Serves a protected dashboard page.
    The `get_current_user` dependency ensures only logged-in users can access it.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})


# --- Authentication Logic Routes ---

@router.post("/login")
async def login_for_access_token(
    response: RedirectResponse,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Handles the login form submission. Verifies credentials and sets a
    secure, HttpOnly cookie with the JWT access token.
    """
    # Authenticate the user
    user = security.authenticate_user(db, username, password)
    if not user:
        # If authentication fails, redirect back to the login page with an error
        # In a real app, you might use query params to show an error message
        return RedirectResponse(url="/login?error=1", status_code=status.HTTP_303_SEE_OTHER)

    # Create the JWT access token
    access_token = security.create_access_token(data={"sub": user.username})

    # Create a redirect response to the protected dashboard
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    # Set the token in an HttpOnly cookie for security
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True, # Prevents JavaScript from accessing the cookie
        samesite='lax', # Can be 'strict' or 'lax'
        secure=False # Set to True in production with HTTPS
    )
    return response


@router.post("/register")
async def register_new_user(
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Handles the registration form submission. Creates a new user in the database.
    """
    # Check if the user already exists
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        # You should handle this more gracefully on the frontend
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Hash the password and create the new user
    hashed_password = security.get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Redirect to the login page after successful registration
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
async def logout():
    """
    Logs the user out by clearing the access token cookie.
    """
    # Redirect to the login page
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    # Delete the cookie
    response.delete_cookie(key="access_token")
    return response

