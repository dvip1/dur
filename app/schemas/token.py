# app/schemas/token.py

from pydantic import BaseModel

# --- Token Schema ---
# Represents the JSON response sent back to the client upon successful login.
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# --- Token Data Schema ---
# Represents the data stored inside the JWT payload (the "sub" claim).
# We'll use this when decoding the token to identify the user.
class TokenData(BaseModel):
    username: str | None = None