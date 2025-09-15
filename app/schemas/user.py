# app/schemas/user.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

# --- User Base Schema ---
# Contains common fields shared across different user-related schemas.
# Avoids code duplication.
class UserBase(BaseModel):
    username: str

# --- User Create Schema ---
# Used when creating a new user via the /register endpoint.
# Inherits from UserBase and adds the password field.
class UserCreate(UserBase):
    password: str

# --- User Public Schema ---
# This is the model that will be returned to the client.
# It includes fields from the database model but explicitly excludes sensitive data.
class UserPublic(UserBase):
    id: int
    created_at: datetime

    # ConfigDict tells Pydantic to read data even if it's not a dict,
    # but an ORM model (like our SQLAlchemy User model).
    model_config = ConfigDict(from_attributes=True)