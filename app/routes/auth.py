# app/routes/auth.py

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError
from typing import cast

# Import your database session dependency, User model, and security functions
from app.database.database import get_db
from app.database.models.user import User
from app.auth import security

# Create an APIRouter instance
router = APIRouter()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


# Dependency to get the current user from the token in the cookie
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependency function to get the current user from the JWT token
    stored in the request's cookies.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        detail="Could not validate credentials",
        headers={"Location": "/login"},  # Redirect to login page
    )

    # 1. Get the token from the cookies
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    # 2. Decode the token and extract username
    try:
        payload = security.decode_access_token(token)
        username: str = cast(str, payload.get("sub"))
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 3. Find the user in the database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

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


# --- Auth Actions ---

@router.post("/login")
async def login_for_access_token(
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
        return RedirectResponse(
            url="/login?error=invalid", status_code=status.HTTP_303_SEE_OTHER
        )

    # Create the JWT access token
    access_token = security.create_access_token(data={"sub": user.username})

    # Create a redirect response to the protected dashboard
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    # Set the token in an HttpOnly cookie for security
    response.set_cookie(
        key="access_token",
        value=access_token,  # store raw token instead of "Bearer <token>"
        httponly=True,       # prevents JavaScript access
        samesite="lax",      # use "strict" if you want tighter CSRF protection
        secure=False         # change to True in production (HTTPS only)
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
    return RedirectResponse(url="/login?success=1", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
async def logout():
    """
    Logs the user out by clearing the access token cookie.
    """
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False  # set to True in production
    )
    return response

