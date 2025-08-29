# app/auth/security.py

from datetime import datetime, timedelta
from typing import Optional, cast

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# It's better to import the User model and settings directly
from app.core.config import settings
from app.database.models.user import User

# --- Configuration ---
# Use the values from your settings file
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# --- Password Hashing ---
# Create a single CryptContext instance for password operations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


# --- JWT Token Handling ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use the expiration time from settings
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes the JWT token to get the payload.
    This function is now present for your `get_current_user` dependency.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # In case of any decoding error, re-raise it to be handled by the dependency
        raise


# --- User Authentication ---

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticates a user by checking username and password.
    This function is now present for your login route.

    Args:
        db (Session): The database session.
        username (str): The username to authenticate.
        password (str): The plain text password.

    Returns:
        Optional[User]: The User object if authentication is successful, otherwise None.
    """
    # 1. Find the user by their username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None  # User not found
    
    # 2. Verify the provided password against the stored hash
    # We use `cast` to inform the type checker that user.hashed_password is a `str`,
    # not a `Column` object. This resolves a common linter false positive.
    if not verify_password(password, cast(str, user.hashed_password)):
        return None  # Incorrect password
        
    # 3. Return the user object if both checks pass
    return user

