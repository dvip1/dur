# app/auth/security.py

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings

# --- Password Hashing ---

# 1. Create a PasswordContext instance for bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


# --- JSON Web Token (JWT) Management ---

def create_access_token(data: dict) -> str:
    """Creates a new access token."""
    to_encode = data.copy()
    
    # 1. Calculate expiration time for the access token
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # 2. Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Creates a new refresh token."""
    to_encode = data.copy()
    
    # 1. Calculate expiration time for the refresh token (longer duration)
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    # 2. Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> str | None:
    """
    Decodes a JWT token and extracts the username.

    :param token: The JWT token string to decode.
    :return: The username (subject) if decoding is successful, otherwise None.
    """
    try:
        # 1. Decode the token using the secret key and algorithm
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 2. Extract the username from the 'sub' (subject) claim
        username: str | None = payload.get("sub")
        if username is None:
            return None # Subject claim missing
        return username
    except JWTError:
        # Token is invalid (e.g., signature verification failed, expired token)
        return None