# app/routes/auth/base.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import dependencies as deps
from app.crud import user as crud_user
from app.schemas import user as user_schema
from app.schemas import token as token_schema
from app.auth import security as auth_security
from app.core.routes import Routes # Your route configuration class

router = APIRouter(
    prefix=Routes.Auth.root,
    tags=["Authentication"]
)

# --- Registration Endpoint ---
@router.post(
    Routes.Auth.register,
    response_model=user_schema.UserPublic,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_in: user_schema.UserCreate, 
    db: Session = Depends(deps.get_db)
):
    """
    Create a new user account.
    - Checks if username already exists.
    - Hashes password before storing.
    """
    # 1. Check if user already exists
    existing_user = crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # 2. Create new user
    user = crud_user.create_user(db=db, user=user_in)
    return user

# --- Login Endpoint ---
@router.post(Routes.Auth.login, response_model=token_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(deps.get_db)
):
    """
    Authenticate user and return access and refresh tokens.
    """
    # 1. Authenticate user
    user = crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not auth_security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Create tokens
    token_data = {"sub": user.username}
    access_token = auth_security.create_access_token(data=token_data)
    refresh_token = auth_security.create_refresh_token(data=token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

# --- Get Current User Endpoint ("Me") ---
@router.get(Routes.Auth.me, response_model=user_schema.UserPublic)
def read_users_me(current_user: user_schema.UserPublic = Depends(deps.get_current_user)):
    """
    Fetch details for the currently authenticated user.
    The get_current_user dependency handles all authentication logic.
    """
    return current_user

# --- Refresh Token Endpoint ---
@router.post(Routes.Auth.refresh, response_model=token_schema.Token)
def refresh_access_token(
    current_user: user_schema.UserPublic = Depends(deps.get_current_user),
):
    """
    Generate a new access token using a valid refresh token.
    The client should send the refresh token as the bearer token for this request.
    """
    # Note: For enhanced security, you could add logic here to ensure
    # that only a refresh token (not an access token) can use this endpoint.
    # For simplicity, we re-use get_current_user, assuming a valid refresh token was sent.

    new_access_token = auth_security.create_access_token(data={"sub": current_user.username})
    
    # Re-return a full token object, potentially with a new refresh token or keeping the old one.
    # Here we issue a new access token and keep the existing refresh token logic simple.
    # A full-featured implementation might rotate refresh tokens as well.
    return {
        "access_token": new_access_token,
        "refresh_token": "", # Client should ideally re-use existing refresh token until it expires
        "token_type": "bearer",
    }