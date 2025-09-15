# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

from app.database.database import SessionLocal
from app.auth import security as auth_security
from app.crud import user as crud_user
from app.schemas.token import TokenData
from app.database.models.user import User
from app.core.config import settings

# --- Dependency 1: Database Session ---

def get_db():
    """
    Dependency function to get a database session.
    Yields a session for use in a request, then ensures it's closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dependency 2: Authentication ---

# 1. Define the OAuth2 scheme.
# tokenUrl points to the endpoint where the client gets the token.
# This must match the path to your login endpoint: prefix + login_route = "/api/auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Decodes the access token to get the current user.
    This function acts as a dependency to protect routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decode the token using the security utility function.
    username = auth_security.decode_token(token)
    if username is None:
        raise credentials_exception

    # 2. Retrieve the user from the database using the CRUD function.
    user = crud_user.get_user_by_username(db, username=username)
    if user is None:
        # User not found in database (e.g., deleted after token was issued)
        raise credentials_exception
    
    # 3. Return the authenticated user object.
    return user